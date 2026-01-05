"""
Dicey Dungeons Archipelago Client

This client acts as a bridge between the Archipelago server and Dicey Dungeons.
It receives item collection notifications from the server and communicates with
the game via a WebSocket proxy server.
"""

import asyncio
import time
import functools
import websockets
from copy import deepcopy
from typing import List, Any, Iterable, Optional, Dict

import Utils
from NetUtils import (decode, encode, JSONtoTextParser, JSONMessagePart, 
                      NetworkItem, NetworkPlayer)
from MultiServer import Endpoint
from CommonClient import (CommonContext, gui_enabled, ClientCommandProcessor, 
                          logger, get_base_parser)

DEBUG = True


class DiceyDungeonsJSONToTextParser(JSONtoTextParser):
    """Custom JSON to text parser for Dicey Dungeons in-game text"""
    def _handle_color(self, node: JSONMessagePart):
        return self._handle_text(node)  # No colors for the in-game text


class DiceyDungeonsCommandProcessor(ClientCommandProcessor):
    """Command processor for Dicey Dungeons specific commands"""
    
    def _cmd_dicey(self):
        """Check Dicey Dungeons connection state"""
        if isinstance(self.ctx, DiceyDungeonsContext):
            logger.info(f"Dicey Dungeons Status: {self.ctx.get_dicey_status()}")


class DiceyDungeonsContext(CommonContext):
    """
    Context for Dicey Dungeons Archipelago integration.
    Manages communication between the Archipelago server and the game.
    """
    
    command_processor = DiceyDungeonsCommandProcessor
    game = "Dicey Dungeons"

    def __init__(self, server_address: Optional[str], password: Optional[str]):
        super().__init__(server_address, password)
        
        # Game-specific proxy attributes
        self.proxy = None
        self.proxy_task = None
        self.gamejsontotext = DiceyDungeonsJSONToTextParser(self)
        self.autoreconnect_task = None
        self.endpoint: Optional[Endpoint] = None
        
        # Items handling - receive all items
        self.items_handling = 0b111
        
        # Server communication state
        self.room_info = None
        self.connected_msg = None
        self.game_connected = False
        self.awaiting_info = False
        
        # Inventory and message queues
        self.full_inventory: List[NetworkItem] = []
        self.server_msgs: List[Any] = []
        
        # Location checking
        self.checked_locations_ids: set[int] = set()

    def get_dicey_status(self) -> str:
        """Get current connection status"""
        if not self.is_proxy_connected():
            return "Not connected to Dicey Dungeons"
        
        game_status = "Connected to Dicey Dungeons"
        server_status = " and Archipelago Server" if self.is_connected() else " (disconnected from Archipelago)"
        return game_status + server_status

    async def server_auth(self, password_requested: bool = False):
        """Authenticate with the server"""
        if password_requested and not self.password:
            await super(DiceyDungeonsContext, self).server_auth(password_requested)

        await self.get_username()
        await self.send_connect()

    def is_proxy_connected(self) -> bool:
        """Check if the game is connected to the proxy"""
        return self.endpoint and self.endpoint.socket.open

    def is_connected(self) -> bool:
        """Check if connected to the Archipelago server"""
        return self.server and self.server.socket.open

    async def send_msgs_proxy(self, msgs: Iterable[dict]) -> bool:
        """Send messages to the connected game via proxy"""
        if not self.endpoint or not self.endpoint.socket.open:
            return False

        if DEBUG:
            logger.info(f"Outgoing message to game: {msgs}")

        await self.endpoint.socket.send(msgs)
        return True

    async def disconnect_proxy(self):
        """Disconnect from the game proxy"""
        if self.endpoint and not self.endpoint.socket.closed:
            await self.endpoint.socket.close()
        if self.proxy_task is not None:
            await self.proxy_task

    async def disconnect(self, allow_autoreconnect: bool = False):
        """Disconnect from server and game"""
        await super().disconnect(allow_autoreconnect)

    def update_items(self):
        """Send inventory update to the game"""
        if not self.is_connected():
            return

        self.server_msgs.append(encode([{
            "cmd": "ReceivedItems",
            "index": 0,
            "items": self.full_inventory
        }]))

    def on_print_json(self, args: dict):
        """Handle print JSON messages from the server"""
        text = self.gamejsontotext(deepcopy(args["data"]))
        msg = {
            "cmd": "PrintJSON",
            "data": [{"text": text}],
            "type": "Chat"
        }
        self.server_msgs.append(encode([msg]))

        if self.ui:
            self.ui.print_json(args["data"])
        else:
            text = self.jsontotextparser(args["data"])
            logger.info(text)

    def on_package(self, cmd: str, args: dict):
        """Handle packages received from the server"""
        
        if cmd == "Connected":
            json = args
            
            # Reduce data size - game doesn't need full player/slot info
            if "slot_info" in json.keys():
                json["slot_info"] = {}
            if "players" in json.keys():
                # Keep only current player info
                me: Optional[NetworkPlayer] = None
                for n in json["players"]:
                    if n.slot == json["slot"] and n.team == json["team"]:
                        me = n
                        break
                json["players"] = [me] if me else []
            
            if DEBUG:
                logger.info(f"Connected: {json}")
            
            self.connected_msg = encode([json])
            if self.awaiting_info:
                self.server_msgs.append(self.room_info)
                self.update_items()
                self.awaiting_info = False

        elif cmd == "RoomUpdate":
            # Don't send full player list to game
            json = args
            if "players" in json.keys():
                json["players"] = []
            self.server_msgs.append(encode(json))

        elif cmd == "ReceivedItems":
            # Update our inventory
            if args["index"] == 0:
                self.full_inventory.clear()

            for item in args["items"]:
                self.full_inventory.append(NetworkItem(*item))

            self.server_msgs.append(encode([args]))

        elif cmd == "RoomInfo":
            self.seed_name = args["seed_name"]
            self.room_info = encode([args])

        else:
            if cmd != "PrintJSON":
                self.server_msgs.append(encode([args]))

    def run_gui(self):
        """Initialize and run the GUI"""
        from kvui import GameManager

        class DiceyDungeonsManager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = "Archipelago Dicey Dungeons Client"

        self.ui = DiceyDungeonsManager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")


async def proxy(websocket, path: str = "/", ctx: DiceyDungeonsContext = None):
    """
    WebSocket proxy handler for game connections.
    Receives messages from the game and forwards them to the Archipelago server.
    """
    ctx.endpoint = Endpoint(websocket)
    try:
        await on_client_connected(ctx)

        if ctx.is_proxy_connected():
            async for data in websocket:
                if DEBUG:
                    logger.info(f"Incoming message from game: {data}")

                for msg in decode(data):
                    
                    if msg["cmd"] == "Connect":
                        # Game proxy is connecting - validate connection
                        if msg.get("game") != "Dicey Dungeons":
                            logger.info("Aborting proxy connection: game is not Dicey Dungeons")
                            await ctx.disconnect_proxy()
                            break

                        # Validate seed name if present
                        if ctx.seed_name:
                            seed_name = msg.get("seed_name", "")
                            if seed_name != "" and seed_name != ctx.seed_name:
                                logger.info("Aborting proxy connection: seed mismatch from save file")
                                logger.info(f"Expected: {ctx.seed_name}, got: {seed_name}")
                                error_msg = encode([{
                                    "cmd": "PrintJSON",
                                    "data": [{"text": "Connection aborted - save file to seed mismatch"}]
                                }])
                                await ctx.send_msgs_proxy(error_msg)
                                await ctx.disconnect_proxy()
                                break

                        # Validate player name if present
                        if ctx.auth:
                            name = msg.get("name", "")
                            if name != "" and name != ctx.auth:
                                logger.info("Aborting proxy connection: player name mismatch from save file")
                                logger.info(f"Expected: {ctx.auth}, got: {name}")
                                error_msg = encode([{
                                    "cmd": "PrintJSON",
                                    "data": [{"text": "Connection aborted - player name mismatch"}]
                                }])
                                await ctx.send_msgs_proxy(error_msg)
                                await ctx.disconnect_proxy()
                                break

                        # Send connection info if we're already connected to server
                        if ctx.connected_msg and ctx.is_connected():
                            await ctx.send_msgs_proxy(ctx.connected_msg)
                            ctx.update_items()
                        continue

                    if not ctx.is_proxy_connected():
                        break

                    # Forward game messages to the server
                    if msg["cmd"] == "LocationCheck":
                        # Game is checking a location
                        location_id = msg.get("location_id")
                        if location_id:
                            ctx.checked_locations_ids.add(location_id)
                            logger.info(f"Location checked: {location_id}")

                    await ctx.send_msgs([msg])

    except Exception as e:
        if not isinstance(e, websockets.WebSocketException):
            logger.exception(e)
    finally:
        await ctx.disconnect_proxy()


async def on_client_connected(ctx: DiceyDungeonsContext):
    """Handle initial game client connection"""
    if ctx.room_info and ctx.is_connected():
        await ctx.send_msgs_proxy(ctx.room_info)
    else:
        ctx.awaiting_info = True


async def proxy_loop(ctx: DiceyDungeonsContext):
    """
    Main proxy loop that forwards messages from the server to the game.
    Runs continuously while the client is active.
    """
    try:
        while not ctx.exit_event.is_set():
            if len(ctx.server_msgs) > 0:
                for msg in ctx.server_msgs:
                    await ctx.send_msgs_proxy(msg)
                ctx.server_msgs.clear()
            
            await asyncio.sleep(0.1)
    except Exception as e:
        logger.exception(e)
        logger.info("Aborting Dicey Dungeons Proxy Client due to errors")


def launch(*launch_args: str):
    """
    Launch the Dicey Dungeons Archipelago client.
    
    This sets up a local WebSocket proxy server that the game connects to,
    while also connecting to the Archipelago multiworld server.
    """
    async def main():
        parser = get_base_parser()
        args = parser.parse_args(launch_args)

        ctx = DiceyDungeonsContext(args.connect, args.password)
        logger.info("Starting Dicey Dungeons Archipelago proxy server on localhost:11312")
        
        # Start the local proxy server for game connections
        ctx.proxy = websockets.serve(
            functools.partial(proxy, ctx=ctx),
            host="localhost",
            port=11312,
            ping_timeout=999999,
            ping_interval=999999
        )
        ctx.proxy_task = asyncio.create_task(proxy_loop(ctx), name="ProxyLoop")

        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        await ctx.proxy
        await ctx.proxy_task
        await ctx.exit_event.wait()

    Utils.init_logging("DiceyDungeonsClient")

    import colorama
    colorama.just_fix_windows_console()
    asyncio.run(main())
    colorama.deinit()


if __name__ == "__main__":
    import sys
    launch(*sys.argv[1:])

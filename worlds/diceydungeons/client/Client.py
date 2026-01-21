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
from queue import Queue, Empty
import ast
import random

import worlds.diceydungeons.client.launch_and_capture as launcher
import worlds.diceydungeons.generator.generator as generator

import Utils
from NetUtils import (decode, encode, JSONtoTextParser, JSONMessagePart, 
                      NetworkItem, NetworkPlayer)
from MultiServer import Endpoint
from CommonClient import (CommonContext, gui_enabled, ClientCommandProcessor, 
                          logger, get_base_parser)

# Import item metadata for categorization
try:
    from worlds.diceydungeons.data.extracted_data import item_metadata
except ImportError:
    logger.warning("Could not import item_metadata from extracted_data")
    item_metadata = {}

DEBUG = True


class DiceyDungeonsJSONToTextParser(JSONtoTextParser):
    """Custom JSON to text parser for Dicey Dungeons in-game text"""
    def _handle_color(self, node: JSONMessagePart):
        return self._handle_text(node)  # No colors for the in-game text


class DiceyDungeonsCommandProcessor(ClientCommandProcessor):
    """Command processor for Dicey Dungeons specific commands"""
    
    def _cmd_dicey(self):
        #"""Check Dicey Dungeons connection state"""
        # if isinstance(self.ctx, DiceyDungeonsContext):
        #     logger.info(f"Dicey Dungeons Status: {self.ctx.get_dicey_status()}")
        """Launch Dicey Dungeons"""
        if isinstance(self.ctx, DiceyDungeonsContext):
            self.ctx.launch_game()
    
    def _cmd_generate(self):
        """Generate new layout for episodes"""
        if isinstance(self.ctx, DiceyDungeonsContext):
            self.ctx.generate_items()



class DiceyDungeonsContext(CommonContext):
    """
    Context for Dicey Dungeons Archipelago integration.
    Manages communication between the Archipelago server and the game.
    """
    
    command_processor = DiceyDungeonsCommandProcessor
    game = "Dicey Dungeons"

    #TODO: replace string with, some variable or something? Will also need to update generators so, maybe we get some path to install 
    # then go from there?
    game_path: str = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Dicey Dungeons\\diceydungeons.exe"

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
        
        # Game launcher queue for receiving messages
        self.game_message_queue: Optional[Queue] = None
    
    def generate_items(self):
        """Generate newly randomized items to find in episodes, based on collected items."""
        asyncio.create_task(self._generate_items_for_game())
    
    async def _generate_items_for_game(self):
        """Asynchronously update ap_data for game to read in generators."""
        logger.info("Generating new options for game!")
        # self.locations_info holds locations and items in those locations
        # is a dict of location_id --> NetworkItem
        # NetworkItem has .item (item id), .player (player id)
        # for loc_id, net_item in self.locations_info.items(): 
        #       Name for ap_data.csv: f"{self.item_names.lookup_in_slot(net_item.item, net_item.player)} [AP][{loc_id}]"
        # We will need to know all locations, which ones we've picked up already, and which game items we have access to.
        # all locations: self.locations_info, explained above
        # locations we've sent already (don't want to spawn those in): self.checked_locations
        # items we've received in multiworld: self.items_received
        # logger.info(f"all our location info: {self.locations_info}")
        # logger.info(f"all locations we've already checked: {self.checked_locations}")
        # logger.info(f"all items we've received: {self.items_received}")
        # These all work (once game has launched!), so next is figuring out how to use them to generate ap_data.csv...
        ap_item_names = dict([(loc_id, f"{self.item_names.lookup_in_slot(net_item.item, net_item.player)} [AP][{loc_id}]") for loc_id, net_item in self.locations_info.items()])
        items_received_str = [self.item_names.lookup_in_slot(net_item.item, net_item.player) for net_item in self.items_received]
        # Get unique items and shuffle order
        items_received_str = list(set(items_received_str))
        random.shuffle(items_received_str)
        # logger.info(ap_item_names)
        generator.DiceyDungeonsAPItemGenerator(ap_item_names, self.locations_info, self.checked_locations, items_received_str).generate()
        logger.info("Done generating new options for game?")

    
    def launch_game(self):
        """Launch the game and attach to the message queue."""
        logger.info(f"Launching game from: {self.game_path}")
        self.game_message_queue = launcher.launch(self.game_path)
        logger.info("Game launched, message queue attached.")
        asyncio.create_task(self._wait_locations_and_get_items())

    async def _wait_locations_and_get_items(self, timeout: float = 10.0):
        """Request location information from server and parse the response."""
        # Request item information for all our locations
        await self.send_msgs([{"cmd": "LocationScouts", "locations": list(self.server_locations)}])

        # Wait for LocationInfo response (sets locations_info dictionary)
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.locations_info:
                logger.info(f"Received location item mappings for {len(self.locations_info)} locations")
                self.get_items_by_location()
                return
            remaining = deadline - time.time()
            try:
                await asyncio.wait_for(self.watcher_event.wait(), remaining)
            except asyncio.TimeoutError:
                logger.warning(f"Timeout waiting for LocationInfo from server")
                return
            finally:
                try:
                    self.watcher_event.clear()
                except Exception:
                    pass
    
    def process_game_messages(self):
        """Process any pending messages from the game queue.
        
        Call this periodically from the main loop to handle incoming messages.
        """
        if not self.game_message_queue:
            return
        
        try:
            while True:
                if not self.game_message_queue:
                    break
                message = self.game_message_queue.get_nowait()
                self.handle_game_message(message)
        except Empty:
            pass
    
    def handle_game_message(self, message: dict):
        """Handle a message received from the game.
        
        Args:
            message: A dict with 'type' and 'data' keys.
                     type='game_message' for JSON parsed from [AP] prefix
                     type='process_exit' when the game closes
                     type='error' for launch errors
        """
        msg_type = message.get("type", "unknown")
        data = message.get("data")
        
        if msg_type == "game_message":
            logger.info(f"Game message received: {data}")
            # Schedule the async command handler so we don't create an un-awaited coroutine
            asyncio.create_task(self.handle_game_command(data))
            
        elif msg_type == "process_exit":
            logger.warning(f"Game process exited with code: {data}")
            self.game_message_queue = None
            
        elif msg_type == "error":
            logger.error(f"Game launcher error: {data}")
            self.game_message_queue = None
        """Get current connection status"""
        if not self.is_proxy_connected():
            return "Not connected to Dicey Dungeons"
        
        game_status = "Connected to Dicey Dungeons"
        server_status = " and Archipelago Server" if self.is_connected() else " (disconnected from Archipelago)"
        return game_status + server_status
    
    async def handle_game_command(self, data: dict):
        command = data.get("command")

        if command == "send_item":
            new_loc = ast.literal_eval(data.get("payload"))[0]
            logger.info(f"Location checked: {str(new_loc)}")
            self.locations_checked.add(new_loc)
            await self.send_msgs([{"cmd": 'LocationChecks', "locations": [new_loc]}]) 
        
        elif command == "reload_generator":
            logger.info(f"Reloading generator")
            #TODO: make it work
    
    def get_items_by_location(self):
        if not self.locations_info:
            logger.info(f"No location info, something went wrong")
        for loc_id, net_item in sorted(self.locations_info.items()):
            logger.info(f"{loc_id} | {net_item}")
            loc_name = self.location_names.lookup_in_game(loc_id, self.game)
            item_name = self.item_names.lookup_in_slot(net_item.item, net_item.player)
            logger.info(f"{loc_id}: {loc_name} -> {item_name} (player {net_item.player})")
            #NOTE: must save location ID of Dicey Dungeons with item name! uniqueness needed.
            #TODO: Use this info to make generator reload.
            # self.locations_info holds locations and items in those locations
            # is a dict of location_id --> NetworkItem
            # NetworkItem has .item (item id), .player (player id)
            # for loc_id, net_item in self.locations_info.items(): 
            #       Name for ap_data.csv: f"{self.item_names.lookup_in_slot(net_item.item, net_item.player)} [AP][{loc_id}]"


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

    def get_items_filtered(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get items for the player with optional filtering and categorization.
        
        This supports the pull-based item model where the game requests items
        instead of having them pushed automatically. Items are returned categorized
        by location type (chest, shop, heal, upgrade, trade) based on metadata.
        
        Args:
            filters: Optional dictionary of filters:
                - 'episode': Int (1-6) - filter by episode
                - 'location_type': Str or List[Str] - filter by location type(s)
                  (e.g., "chest", "shop", ["chest", "shop"])
                - 'role': Str or List[Str] - filter by role
                - 'item_type': Str or List[Str] - filter by item type
            
        Returns:
            Dictionary with:
            - 'cmd': "ReceivedItems"
            - 'total_items': Total items available
            - 'filters_applied': The filters that were used
            - Items grouped by location_type: 'chest_items', 'shop_items', etc.
              Each group is a list of [name, id, player_id, flags]
        """
        if filters is None:
            filters = {}
        
        # Normalize filter values to lists for easier processing
        normalized_filters = {}
        for key, value in filters.items():
            if isinstance(value, (list, tuple)):
                normalized_filters[key] = value
            else:
                normalized_filters[key] = [value] if value is not None else []
        
        # Categorize all items by location_type
        categorized_items: Dict[str, List] = {}
        
        for item in self.full_inventory:
            item_name = item[0]  # item is [name, id, player_id, flags]
            metadata = item_metadata.get(item_name, {})
            
            # Check if item matches all filters
            matches_filters = True
            
            # Filter by episode
            if 'episode' in normalized_filters and normalized_filters['episode']:
                if metadata.get('episode') not in normalized_filters['episode']:
                    matches_filters = False
            
            # Filter by location_type
            if 'location_type' in normalized_filters and normalized_filters['location_type']:
                if metadata.get('location_type') not in normalized_filters['location_type']:
                    matches_filters = False
            
            # Filter by role
            if 'role' in normalized_filters and normalized_filters['role']:
                if metadata.get('role') not in normalized_filters['role']:
                    matches_filters = False
            
            # Filter by item_type
            if 'item_type' in normalized_filters and normalized_filters['item_type']:
                if metadata.get('item_type') not in normalized_filters['item_type']:
                    matches_filters = False
            
            if matches_filters:
                location_type = metadata.get('location_type', 'unknown')
                category_key = f"{location_type}_items"
                
                if category_key not in categorized_items:
                    categorized_items[category_key] = []
                
                categorized_items[category_key].append(item)
        
        response = {
            "cmd": "ReceivedItems",
            "total_items": len(self.full_inventory),
            "total_matching": sum(len(items) for items in categorized_items.values()),
            "filters_applied": filters,
        }
        
        # Add categorized items to response
        response.update(categorized_items)
        
        return response

    def update_items(self):
        """
        DEPRECATED: This method is kept for backward compatibility.
        In the pull-based model, items are not automatically sent to the game.
        The game requests items via GetItems command instead.
        """
        # No longer auto-sends items; game pulls them via GetItems
        pass

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
        # if DEBUG:
        #     logger.info(f"cmd: {cmd} | args: {args}")
        
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
            # Update our inventory but don't push to game
            # Game will pull items via GetItems command
            if args["index"] == 0:
                self.full_inventory.clear()

            for item in args["items"]:
                self.full_inventory.append(NetworkItem(*item))
            
            logger.info(f"Items updated: now have {len(self.full_inventory)} total items available")

        elif cmd == "RoomInfo":
            self.seed_name = args["seed_name"]
            self.room_info = encode([args])
                    
        # Handle location item mappings from the server
        elif cmd == "LocationInfo":
            for item in [NetworkItem(*item) for item in args['locations']]:
                self.locations_info[item.location] = item
            self.watcher_event.set()

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
    
    Supports pull-based item model where game requests items via GetItems command.
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
                        continue

                    if not ctx.is_proxy_connected():
                        break

                    # Handle GetItems request (pull-based model with filtering)
                    if msg["cmd"] == "GetItems":
                        # Extract optional filters from the message
                        filters = msg.get("filters", {})
                        items_response = ctx.get_items_filtered(filters)
                        await ctx.send_msgs_proxy(encode([items_response]))
                        continue

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
    Also processes incoming messages from the game.
    """
    try:
        while not ctx.exit_event.is_set():
            if len(ctx.server_msgs) > 0:
                for msg in ctx.server_msgs:
                    await ctx.send_msgs_proxy(msg)
                ctx.server_msgs.clear()
            
            # Process any messages from the game
            ctx.process_game_messages()
            
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

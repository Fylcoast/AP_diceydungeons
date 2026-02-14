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
import os

from . import launch_and_capture as launcher
from ..generator import generator as generator
from .. import mod as patcher

import Utils
from NetUtils import (decode, encode, JSONtoTextParser, JSONMessagePart, ClientStatus,
                      NetworkItem, NetworkPlayer)
from MultiServer import Endpoint
from CommonClient import (CommonContext, gui_enabled, ClientCommandProcessor, 
                          logger, get_base_parser)

# Import item metadata for categorization
try:
    from ..data.game_data import item_metadata
except ImportError:
    logger.warning("Could not import item_metadata from extracted_data")
    item_metadata = {}

DEBUG = False


class DiceyDungeonsJSONToTextParser(JSONtoTextParser):
    """Custom JSON to text parser for Dicey Dungeons in-game text"""
    def _handle_color(self, node: JSONMessagePart):
        return self._handle_text(node)  # No colors for the in-game text


class DiceyDungeonsCommandProcessor(ClientCommandProcessor):
    """Command processor for Dicey Dungeons specific commands"""
    
    def _cmd_dicey(self) -> bool:
        """Launch Dicey Dungeons"""
        if isinstance(self.ctx, DiceyDungeonsContext):
            self.ctx.launch_game()
            return True
        return False
    
    def _cmd_generate(self) -> bool:
        """Generate new layout for episodes"""
        if isinstance(self.ctx, DiceyDungeonsContext):
            self.ctx.generate_items()
            return True
        return False
    
    def _cmd_install_location(self, installation_location: str) -> bool:
        """Define installation location for Dicey Dungeons"""
        if isinstance(self.ctx, DiceyDungeonsContext):
            self.ctx.game_path = installation_location
            logger.info(f"Game path set to: {installation_location}")
            return True
        return False
    
    def _cmd_patch(self) -> bool:
        """Patch your version of Dicey Dungeons to work with this multiworld!"""
        if isinstance(self.ctx, DiceyDungeonsContext):
            self.ctx.patch_game()




class DiceyDungeonsContext(CommonContext):
    """
    Context for Dicey Dungeons Archipelago integration.
    Manages communication between the Archipelago server and the game.
    """
    
    command_processor = DiceyDungeonsCommandProcessor
    game = "Dicey Dungeons"
    game_path: str = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Dicey Dungeons"
    slot_data: dict

    def __init__(self, server_address: Optional[str], password: Optional[str]):
        super().__init__(server_address, password)
        
        self.gamejsontotext = DiceyDungeonsJSONToTextParser(self)
        
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
    
    def patch_game(self):
        """Patch Dicey Dungeons"""
        asyncio.create_task(self._patch_game())
        

    async def _patch_game(self):
        """Asynchronously patch the game."""
        if not self.locations_info:
            if DEBUG:
                logger.info("Locations not retrieved from server yet. Grabbing those first!")
            await self._wait_locations_and_get_items()
        ap_items: list[tuple[str, str, int]] = [(f"{self.item_names.lookup_in_slot(net_item.item, net_item.player).replace(",", "[comma]")} [AP][{loc_id}]", self.player_names[net_item.player], net_item.flags) for loc_id, net_item in self.locations_info.items()]
        patcher.DiceyDungeonsClientModGenerator(self.game_path, ap_items).generate()
        logger.info("Patched Dicey Dungeons!")
    
    def generate_items(self):
        """Generate newly randomized items to find in episodes, based on collected items."""
        asyncio.create_task(self._generate_items_for_game())
    
    async def _generate_items_for_game(self):
        """Asynchronously update ap_data for game to read in generators."""
        if DEBUG:
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
        if DEBUG:
            logger.info(f"all our location info: {self.locations_info}")
            logger.info(f"all locations we've already checked: {self.checked_locations}")
            logger.info(f"all items we've received: {self.items_received}")
        ap_item_names_list: list[tuple[int, str]] = [(loc_id, f"{self.item_names.lookup_in_slot(net_item.item, net_item.player).replace(",", "[comma]")} [AP][{loc_id}]") for loc_id, net_item in self.locations_info.items()]
        # Filter out Completion items
        ap_item_names_list = [item for item in ap_item_names_list if "Completed" not in item[1]]
        ap_item_names = dict(ap_item_names_list)
        items_received_str = [self.item_names.lookup_in_slot(net_item.item, net_item.player) for net_item in self.items_received]
        # Get unique items and shuffle order
        items_received_str = list(set([item for item in items_received_str if item in item_metadata.keys()]))
        random.shuffle(items_received_str)
        # logger.info(ap_item_names)
        generator.DiceyDungeonsAPItemGenerator(self.game_path, 
                                               self.slot_data, 
                                               ap_item_names, 
                                               self.locations_info, 
                                               self.checked_locations.union(self.locations_checked), 
                                               items_received_str,
                                               self.get_level_ups_received()).generate()
        if DEBUG:
            logger.info("Game generators updated!")

    
    def launch_game(self):
        """Launch the game and attach to the message queue."""
        game_exe = os.path.join(self.game_path, "diceydungeons.exe")
        logger.info(f"Launching game from: {self.game_path}")
        self.game_message_queue = launcher.launch(game_exe)
        if DEBUG:
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
                if DEBUG:
                    logger.info(f"Received location item mappings for {len(self.locations_info)} locations")
                    self.get_items_by_location()
                self.generate_items()
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
            if DEBUG:
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
        
        game_status = "Connected to Dicey Dungeons" if self.game_message_queue else "Not running Dicey Dungeons"
        server_status = " and Archipelago Server" if self.is_connected() else " (disconnected from Archipelago)"
        return game_status + server_status
    
    async def handle_game_command(self, data: dict):
        command = data.get("command")

        if command == "send_item":
            new_loc = ast.literal_eval(data.get("payload"))[0]
            if DEBUG:
                logger.info(f"Location checked: {str(new_loc)}")
            self.locations_checked.add(new_loc)
            await self.send_msgs([{"cmd": 'LocationChecks', "locations": [new_loc]}]) 
        
        elif command == "reload_generator":
            self.generate_items()
    
    async def check_for_victory(self):
        if self.finished_game == False:
            items_received_str = [self.item_names.lookup_in_slot(net_item.item, net_item.player) for net_item in self.items_received]
            if "Episode 1 - Episode Completed" in items_received_str and \
                "Episode 2 - Episode Completed" in items_received_str and \
                "Episode 3 - Episode Completed" in items_received_str and \
                "Episode 4 - Episode Completed" in items_received_str and \
                "Episode 5 - Episode Completed" in items_received_str and \
                "Episode 6 - Episode Completed" in items_received_str:
                await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                self.finished_game = True

    
    def get_items_by_location(self):
        """Print items by location, for debug purposes"""
        if not self.locations_info:
            logger.info(f"No location info, something went wrong")
        for loc_id, net_item in sorted(self.locations_info.items()):
            logger.info(f"{loc_id} | {net_item}")
            loc_name = self.location_names.lookup_in_game(loc_id, self.game)
            item_name = self.item_names.lookup_in_slot(net_item.item, net_item.player)
            logger.info(f"{loc_id}: {loc_name} -> {item_name} (player {net_item.player})")
    
    def get_level_ups_received(self) -> dict[str, int]:
        items_received_str = [self.item_names.lookup_in_slot(net_item.item, net_item.player) for net_item in self.items_received]
        level_ups: dict[str, int] = {}
        for episode in range(1, 7):
            level_ups[f"Episode {episode}"] = items_received_str.count(f"Episode {episode} Progressive Level Up")
        
        return level_ups


    async def server_auth(self, password_requested: bool = False):
        """Authenticate with the server"""
        if password_requested and not self.password:
            await super(DiceyDungeonsContext, self).server_auth(password_requested)

        await self.get_username()
        await self.send_connect()


    def is_connected(self) -> bool:
        """Check if connected to the Archipelago server"""
        return self.server and self.server.socket.open


    async def disconnect(self, allow_autoreconnect: bool = False):
        """Disconnect from server and game"""
        await super().disconnect(allow_autoreconnect)


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

            self.slot_data = json["slot_data"]
            if DEBUG:
                logger.info(f"Received the following player Options: {self.slot_data}")

        elif cmd == "RoomUpdate":
            # Don't send full player list to game
            json = args
            if "players" in json.keys():
                json["players"] = []
            self.server_msgs.append(encode(json))

        elif cmd == "ReceivedItems":
            if args["index"] == 0:
                self.full_inventory.clear()

            for item in args["items"]:
                self.full_inventory.append(NetworkItem(*item))
            
            self.generate_items()
            
            if DEBUG:
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


async def main_game_loop(ctx: DiceyDungeonsContext):
    """
    Main game loop that handles core client tasks.
    Processes incoming messages from the game and checks for victory conditions.
    """
    try:
        while not ctx.exit_event.is_set():
            # Process any messages from the game
            ctx.process_game_messages()

            # Check for victory
            await ctx.check_for_victory()
            
            await asyncio.sleep(0.1)
    except Exception as e:
        logger.exception(e)
        logger.info("Error in Dicey Dungeons main game loop")


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
        logger.info("Starting Dicey Dungeons Archipelago Client")
        
        # Start the main game loop that processes game messages and checks for victory
        ctx.game_loop_task = asyncio.create_task(main_game_loop(ctx), name="GameLoop")

        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        await ctx.exit_event.wait()

    Utils.init_logging("DiceyDungeonsClient")

    import colorama
    colorama.just_fix_windows_console()
    asyncio.run(main())
    colorama.deinit()


if __name__ == "__main__":
    import sys
    launch(*sys.argv[1:])

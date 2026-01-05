"""
Example Game Integration Code for Dicey Dungeons

This is a reference implementation showing how a Dicey Dungeons mod would
integrate with the Archipelago client. This would typically be implemented
in the game's modding framework or as a mod script.

The client runs as a separate server, and the game connects to it to:
1. Report location checks (items collected, bosses defeated, etc.)
2. Receive items from other players
3. Communicate game state
"""

import asyncio
import json
from typing import Optional, Callable, Dict, List, Any


class DiceyDungeonsGameIntegration:
    """
    Handles communication between Dicey Dungeons and the Archipelago proxy.
    
    This would be instantiated once when the game loads and persists
    throughout the gameplay session.
    """
    
    def __init__(self, player_name: str, seed_name: str):
        """
        Initialize the game integration.
        
        Args:
            player_name: The player's name in Archipelago
            seed_name: The seed name to validate against the save file
        """
        self.player_name = player_name
        self.seed_name = seed_name
        self.websocket = None
        self.is_connected = False
        self.received_items: List[Dict[str, Any]] = []
        self.message_callbacks: Dict[str, List[Callable]] = {}
    
    async def connect(self, proxy_url: str = "ws://localhost:11312/") -> bool:
        """
        Connect to the Archipelago proxy server.
        
        Args:
            proxy_url: URL of the proxy server
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            import websockets
            
            self.websocket = await websockets.connect(proxy_url)
            
            # Send connection message
            connect_msg = {
                "cmd": "Connect",
                "game": "Dicey Dungeons",
                "name": self.player_name,
                "seed_name": self.seed_name
            }
            
            await self.websocket.send(json.dumps(connect_msg))
            self.is_connected = True
            
            # Start listening for messages
            asyncio.create_task(self._receive_messages())
            
            return True
            
        except Exception as e:
            print(f"Failed to connect to Archipelago proxy: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the proxy server."""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
    
    async def check_location(self, location_id: int) -> bool:
        """
        Report a location check to the Archipelago server.
        
        This should be called when the player collects an item, defeats
        a boss, completes a floor, or any other trackable event.
        
        Args:
            location_id: The ID of the location being checked
            
        Returns:
            True if message sent successfully
        """
        if not self.is_connected or not self.websocket:
            return False
        
        try:
            msg = {
                "cmd": "LocationCheck",
                "location_id": location_id
            }
            await self.websocket.send(json.dumps(msg))
            return True
        except Exception as e:
            print(f"Failed to send location check: {e}")
            return False
    
    async def _receive_messages(self):
        """
        Listen for messages from the proxy and dispatch them.
        This runs continuously while connected.
        """
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError:
                    print(f"Invalid JSON received: {message}")
        except Exception as e:
            print(f"Error receiving messages: {e}")
            self.is_connected = False
    
    async def _handle_message(self, data: Dict[str, Any]):
        """
        Process a message from the proxy.
        
        Args:
            data: The message data
        """
        cmd = data.get("cmd")
        
        if cmd == "ReceivedItems":
            # Items have been collected for this player
            items = data.get("items", [])
            self.received_items.extend(items)
            
            # Call registered callbacks
            await self._dispatch_callback("items_received", items)
            
            print(f"Received {len(items)} items!")
            for item in items:
                print(f"  - {item[0]} (ID: {item[1]})")
        
        elif cmd == "PrintJSON":
            # Chat message or notification
            text = data.get("data", [{}])[0].get("text", "")
            await self._dispatch_callback("print", text)
            print(f"[Server] {text}")
        
        elif cmd == "RoomUpdate":
            # Room state has changed
            await self._dispatch_callback("room_update", data)
        
        elif cmd == "Connected":
            # Acknowledged connection
            await self._dispatch_callback("connected", data)
            print("Successfully connected to Archipelago server!")
        
        else:
            # Unknown command
            await self._dispatch_callback("unknown", data)
    
    def register_callback(self, event: str, callback: Callable):
        """
        Register a callback for an event.
        
        Args:
            event: Event name ("items_received", "print", "room_update", "connected")
            callback: Async callable to invoke when event occurs
        """
        if event not in self.message_callbacks:
            self.message_callbacks[event] = []
        self.message_callbacks[event].append(callback)
    
    async def _dispatch_callback(self, event: str, data: Any):
        """Dispatch all callbacks for an event."""
        callbacks = self.message_callbacks.get(event, [])
        for callback in callbacks:
            try:
                await callback(data)
            except Exception as e:
                print(f"Error in {event} callback: {e}")


# Example usage in game code:
async def example_game_loop():
    """
    Example of how to use the integration in game code.
    """
    
    # Initialize the integration
    integration = DiceyDungeonsGameIntegration(
        player_name="PlayerName",
        seed_name="MySeedName"
    )
    
    # Register callbacks for events
    async def on_items_received(items: List):
        # Handle newly received items
        for item in items:
            print(f"Item received: {item[0]}")
            # Update game state here
    
    async def on_connected(data: Dict):
        print("Connected!")
    
    integration.register_callback("items_received", on_items_received)
    integration.register_callback("connected", on_connected)
    
    # Connect to the proxy
    if await integration.connect():
        print("Connected to Archipelago!")
        
        # Simulate game events
        await asyncio.sleep(2)
        
        # Player completes level, check location
        await integration.check_location(11101)
        print("Location 11101 checked!")
        
        await asyncio.sleep(2)
        
        # Player defeats a boss
        await integration.check_location(12101)
        print("Location 11201 checked!")
        
        await asyncio.sleep(5)
        await integration.disconnect()


if __name__ == "__main__":
    # This would normally be part of the game, not a standalone script
    asyncio.run(example_game_loop())

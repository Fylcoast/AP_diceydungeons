# Dicey Dungeons Archipelago Client

## Overview

This is the Archipelago client for Dicey Dungeons, serving as a bridge between the Archipelago multiworld server and the game. The client uses a WebSocket proxy architecture to communicate with the game while maintaining a connection to the Archipelago server.

## Architecture

### How It Works

The client uses a proxy pattern similar to the A Hat in Time client:

```
Dicey Dungeons Game
        ↓
    (WebSocket)
        ↓
DiceyDungeonsContext Proxy (localhost:11312)
        ↓
    (WebSocket)
        ↓
Archipelago Server
```

1. **Game ↔ Proxy**: The game connects to a local WebSocket server running on `localhost:11312`
2. **Proxy ↔ Server**: The proxy maintains a connection to the Archipelago multiworld server
3. **Message Forwarding**: Messages are forwarded between the game and server as needed

### Key Components

#### `DiceyDungeonsContext`
The main context class that extends `CommonContext`. It manages:
- Connection to the Archipelago server
- Local WebSocket proxy for game connections
- Item inventory management
- Location checking
- Message queuing between game and server

#### `proxy()` Function
The WebSocket handler that processes incoming messages from the game. It:
- Validates connections (game name, seed, player name)
- Processes game commands like `LocationCheck`
- Forwards messages to the Archipelago server
- Sends server responses back to the game

#### `proxy_loop()`
Runs continuously to forward queued server messages to the game at regular intervals.

## Usage

### Starting the Client

From the command line:

```bash
python worlds/diceydungeons/Client.py --connect <server_address> --password <password>
```

Or with a GUI (if enabled):

```bash
python worlds/diceydungeons/Client.py --connect <server_address>
```

### Game Integration

The Dicey Dungeons game needs to connect to the proxy server. It should:

1. **Connect to the proxy**:
   ```
   ws://localhost:11312/
   ```

2. **Send a Connect message**:
   ```json
   {
       "cmd": "Connect",
       "game": "Dicey Dungeons",
       "name": "<player_name>",
       "seed_name": "<seed_name>"
   }
   ```

3. **Send LocationCheck messages** when the player collects items/completes challenges:
   ```json
   {
       "cmd": "LocationCheck",
       "location_id": <location_id>
   }
   ```

4. **Receive messages** from the server:
   - `ReceivedItems`: List of items the player has collected
   - `RoomUpdate`: Updates about other players
   - `PrintJSON`: Chat/notification messages
   - And other standard Archipelago messages

## Message Format

### LocationCheck Message
Sent by the game when a location is checked:
```json
{
    "cmd": "LocationCheck",
    "location_id": 11101
}
```

### ReceivedItems Message
Sent by the server with collected items:
```json
{
    "cmd": "ReceivedItems",
    "index": 0,
    "items": [
        [<item_name>, <item_id>, <player_id>, <flags>],
        ...
    ]
}
```

## Configuration

### Ports
- **Game Proxy**: `localhost:11312` (configurable in launch function)

### Debug Mode
To enable debug logging, set `DEBUG = True` at the top of the Client.py file.

## Validation

The client validates:
1. **Game Name**: Ensures connecting client is for "Dicey Dungeons"
2. **Seed Name**: Validates saved game seed matches server seed
3. **Player Name**: Ensures player name matches between game and server

## Available Commands

In the CLI, use these commands:

- `/dicey` - Check current connection status
- `/received` - List all received items
- `/missing` - List missing location checks
- `/items` - List all item names
- `/locations` - List all location names
- `/ready` - Toggle ready status

## Extension Points

To add game-specific functionality:

1. **Add custom commands** in `DiceyDungeonsCommandProcessor`
2. **Handle additional messages** in `DiceyDungeonsContext.on_package()`
3. **Process game messages** in the `proxy()` function
4. **Customize text parsing** in `DiceyDungeonsJSONToTextParser`

## Status

This is an MVP (Minimum Viable Product) client that provides:
- ✅ Server connection management
- ✅ Game proxy communication
- ✅ Item inventory management
- ✅ Location checking support
- ✅ Message routing between game and server

Future enhancements may include:
- Game-specific UI overlays
- DeathLink integration
- Hints system integration
- Custom item handling for different character classes
- Save/load integration

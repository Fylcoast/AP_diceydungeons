# Dicey Dungeons Archipelago Client - Implementation Summary

## What Was Created

An MVP (Minimum Viable Product) Archipelago client for Dicey Dungeons consisting of:

### 1. **Client.py** - Main Client Implementation
The core client that bridges Archipelago server and the game.

**Key Classes:**
- `DiceyDungeonsContext`: Main context managing connections and state
- `DiceyDungeonsCommandProcessor`: CLI command handling
- `DiceyDungeonsJSONToTextParser`: JSON-to-text message parsing

**Key Functions:**
- `proxy()`: WebSocket handler for incoming game connections
- `proxy_loop()`: Forwards queued server messages to game
- `launch()`: Entry point that starts the client

**Features:**
- ✅ WebSocket proxy on `localhost:11312`
- ✅ Archipelago server connection management
- ✅ Item inventory tracking
- ✅ Location checking support
- ✅ Connection validation (game name, seed, player name)
- ✅ Message routing between game and server
- ✅ CLI with debug commands

### 2. **CLIENT_README.md** - Technical Documentation
Comprehensive guide covering:
- Architecture and how it works
- Component descriptions
- Message format examples
- Configuration options
- Extension points for customization

### 3. **GAME_INTEGRATION_EXAMPLE.py** - Example Implementation
Sample code showing how a game would integrate with the client:
- `DiceyDungeonsGameIntegration` class for game-side integration
- Methods for connecting, checking locations, receiving items
- Event callback system for handling server messages
- Example usage demonstrating the integration

### 4. **QUICK_START.md** - Quick Reference Guide
Get-up-and-running guide including:
- Setup instructions
- How to run the client
- Manual testing with WebSocket clients
- Python testing code
- Debugging tips
- Common issues and solutions
- Architecture overview

## How It Works

### The Proxy Pattern

```
┌─────────────────────┐
│  Dicey Dungeons     │
│      Game           │
└──────────┬──────────┘
           │ ws://localhost:11312
           │
    ┌──────▼────────────────────┐
    │  DiceyDungeonsContext      │
    │  Proxy Server              │
    └──────┬─────────────────────┘
           │ Archipelago Server
           │
    ┌──────▼────────────────────┐
    │  Archipelago Multiworld    │
    │      Server                │
    └────────────────────────────┘
```

### Communication Flow

1. **Game → Proxy**: Location checks, connection info
2. **Proxy → Server**: Forwards location checks, receives slot confirmation
3. **Server → Proxy**: Items received, room updates, chat messages
4. **Proxy → Game**: Inventory updates, notifications

### Validation

Connections are validated for:
- Correct game name: "Dicey Dungeons"
- Matching seed name (if saved game exists)
- Matching player name

## Starting the Client

```bash
python worlds/diceydungeons/Client.py --connect <server_address> --password <password>
```

The client will:
1. Connect to the Archipelago server
2. Prompt for a username
3. Start listening on `ws://localhost:11312/` for game connections
4. Display a CLI interface with commands like `/dicey`, `/received`, `/missing`

## Game Integration

The game needs to:

1. **Connect** to `ws://localhost:11312/`
2. **Send Connect message**:
   ```json
   {
       "cmd": "Connect",
       "game": "Dicey Dungeons",
       "name": "PlayerName",
       "seed_name": "SeedName"
   }
   ```
3. **Send LocationCheck messages** when events occur:
   ```json
   {
       "cmd": "LocationCheck",
       "location_id": 11101
   }
   ```
4. **Receive messages** from the server (items, notifications, etc.)

See `GAME_INTEGRATION_EXAMPLE.py` for complete implementation example.

## Location ID Reference

Location IDs follow this pattern:

**Level Completion Locations:**
- Format: `10<episode><level>`
- Example: `1012` = Episode 1, Level 2

**Physical Locations (Chests, Shops, etc.):**
- Format: `<episode><floor><type><count>`
- Episode: 1-6
- Floor: 1-6  
- Type: 1=Chest, 2=Shop, 3=Heals, 4=Upgrades, 5=Trades
- Example: `11101` = Episode 1, Floor 1, Chest 1
- Example: `12201` = Episode 1, Floor 2, Shop 1

Full reference in `locations.py`

## Key Features

### ✅ Implemented
- Server connection/disconnection
- Game proxy with WebSocket
- Connection validation
- Item inventory management
- Location checking
- Message routing
- CLI interface
- Debug mode

### 🚀 Future Enhancements
- DeathLink integration
- Hints system support
- Custom item handling for different character classes
- In-game UI overlay
- Save/load synchronization
- Multi-character support

## Testing

### Quick Manual Test
```bash
# Terminal 1: Start client
python worlds/diceydungeons/Client.py --connect localhost:38281

# Terminal 2: Test connection (using websocat or Python)
python GAME_INTEGRATION_EXAMPLE.py
```

### Expected Behavior
- Client connects to server ✓
- Game connects to proxy ✓
- Location checks are registered ✓
- Items are received from server ✓
- Messages are displayed ✓

## File Structure

```
worlds/diceydungeons/
├── Client.py                      # Main client implementation (MVP)
├── CLIENT_README.md               # Technical documentation
├── GAME_INTEGRATION_EXAMPLE.py    # Example game integration code
├── QUICK_START.md                 # Quick reference guide
├── world.py                       # World definition
├── items.py                       # Item definitions
├── locations.py                   # Location definitions
├── regions.py                     # Region definitions
├── rules.py                       # Logic rules
├── options.py                     # Game options
├── web_world.py                   # Web interface
└── __init__.py                    # Package init
```

## Design Decisions

1. **Proxy Architecture**: Chosen to allow the game to connect locally without needing direct network changes
2. **Message Queuing**: Server messages are queued and sent at intervals to prevent flooding
3. **Validation**: Strict validation prevents mismatched saves/players
4. **Location IDs**: Use standardized ID format matching the game structure
5. **Extensibility**: Clean class structure for adding game-specific features

## Next Steps

1. **Test the proxy**: Run the client and verify it starts successfully
2. **Integrate with game**: Modify game code to connect to `localhost:11312`
3. **Map locations**: Ensure game sends correct location IDs
4. **Handle items**: Implement logic to give items to the player
5. **Test end-to-end**: Connect to a real multiworld game
6. **Add features**: Implement DeathLink, hints, etc. as needed

## Documentation Files

- **CLIENT_README.md**: Full technical documentation and architecture
- **QUICK_START.md**: Setup, testing, and troubleshooting guide
- **GAME_INTEGRATION_EXAMPLE.py**: Example code with detailed comments

All documentation is in the `worlds/diceydungeons/` directory alongside the client code.

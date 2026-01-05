# Quick Start Guide: Dicey Dungeons Archipelago Client

## Setup

### Prerequisites
- Python 3.7+
- websockets library (should already be installed as part of Archipelago)
- A running Archipelago multiworld server

### 1. Start the Client

```bash
cd AP_diceydungeons
python worlds/diceydungeons/Client.py --connect <server_address> --password <password>
```

**Example:**
```bash
python worlds/diceydungeons/Client.py --connect archipelago.gg:38281 --password mypassword
```

**Without password (if server doesn't require one):**
```bash
python worlds/diceydungeons/Client.py --connect 192.168.1.100:38281
```

The client will:
1. Output the server address and wait for a username to be entered
2. Connect to the server
3. Start listening for game connections on `localhost:11312`

### 2. Connect Your Game

The game needs to connect to `ws://localhost:11312/` and send a Connect message.

See `GAME_INTEGRATION_EXAMPLE.py` for how to do this.

## Testing the Client

### Manual Testing with WebSocket Clients

You can test the proxy without the actual game using a WebSocket client like `websocat` or `wscat`.

**Test 1: Connection Validation**

```bash
# Using websocat (install: cargo install websocat)
websocat ws://localhost:11312/

# Send a connect message
{"cmd": "Connect", "game": "Dicey Dungeons", "name": "TestPlayer", "seed_name": "test_seed"}
```

Expected response: You should receive the server's Connected message with slot info.

**Test 2: Location Check**

```
# After connecting, send a location check
{"cmd": "LocationCheck", "location_id": 11101}
```

This should register the location check on the server.

### Using Python for Testing

```python
import asyncio
import json
import websockets

async def test_client():
    async with websockets.connect("ws://localhost:11312/") as ws:
        # Connect
        connect_msg = {
            "cmd": "Connect",
            "game": "Dicey Dungeons",
            "name": "TestPlayer",
            "seed_name": "test_seed"
        }
        await ws.send(json.dumps(connect_msg))
        
        # Receive connection response
        response = await ws.recv()
        print("Connected:", response)
        
        # Check a location
        location_check = {"cmd": "LocationCheck", "location_id": 11101}
        await ws.send(json.dumps(location_check))
        
        # Listen for a bit
        for _ in range(5):
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
                print("Received:", msg)
            except asyncio.TimeoutError:
                print("No message received")

asyncio.run(test_client())
```

## Debugging

### Enable Debug Mode

Edit `Client.py` and set:
```python
DEBUG = True
```

This will log all incoming and outgoing messages.

### Check Connection Status

In the client CLI, use:
```
/dicey
```

This shows:
- Game connection status
- Server connection status

### View Received Items

```
/received
```

Lists all items received from the server.

### View Missing Locations

```
/missing
```

Lists all locations that haven't been checked yet.

## Common Issues

### "Connection refused" on startup

**Problem**: Client can't connect to the Archipelago server.

**Solutions**:
1. Check that the server address is correct: `--connect <host:port>`
2. Verify the server is running
3. Check firewall settings
4. Use `--connect localhost:38281` if running locally

### Game can't connect to proxy

**Problem**: Game gets connection refused when trying to reach localhost:11312

**Solutions**:
1. Ensure client is running: `python Client.py ...`
2. Check that port 11312 is not in use: `netstat -an | findstr 11312` (Windows)
3. Try a different port by modifying the `websockets.serve()` call in `launch()`
4. Verify game is connecting to correct URL: `ws://localhost:11312/`

### Seed mismatch error

**Problem**: "Connection aborted - save file to seed mismatch"

**Solutions**:
1. Make sure the game is connecting with the correct seed name
2. Verify the seed name matches between game and server
3. Reset the save file with the correct seed

### Player name mismatch error

**Problem**: "Connection aborted - player name mismatch"

**Solutions**:
1. Check that game player name matches the connected player
2. Verify name is transmitted correctly in Connect message
3. Check for typos or case sensitivity

## Architecture Overview

```
┌─────────────────┐
│  Game Instance  │
└────────┬────────┘
         │ WebSocket (localhost:11312)
         │
┌────────▼────────────────────────────────────┐
│  DiceyDungeonsContext                       │
│  - Proxy handler                            │
│  - Message routing                          │
│  - Inventory management                     │
└────────┬────────────────────────────────────┘
         │ WebSocket
         │
┌────────▼──────────────────────────┐
│  Archipelago Multiworld Server     │
│  - Slot management                 │
│  - Item distribution               │
│  - Player coordination             │
└────────────────────────────────────┘
```

## Next Steps

1. **Implement game integration**: Use `GAME_INTEGRATION_EXAMPLE.py` as a template
2. **Map locations**: Update location IDs in your game code to match `worlds/diceydungeons/locations.py`
3. **Handle item delivery**: Implement logic to give players their received items
4. **Test with server**: Connect to an actual Archipelago multiworld game
5. **Add UI**: Implement in-game notifications for received items and location checks

## Files Overview

- **Client.py**: Main client implementation
- **CLIENT_README.md**: Detailed client documentation
- **GAME_INTEGRATION_EXAMPLE.py**: Example code for game integration
- **QUICK_START.md**: This file

## Support

For issues or questions:
1. Check `CLIENT_README.md` for detailed documentation
2. Review the A Hat in Time client (`worlds/ahit/Client.py`) for reference
3. Check Archipelago documentation: https://archipelago.gg/

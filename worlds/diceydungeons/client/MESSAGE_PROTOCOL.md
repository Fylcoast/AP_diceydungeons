# Dicey Dungeons Archipelago Client - Message Protocol

## Overview

This document describes the message protocol used between Dicey Dungeons and the Archipelago proxy client.

## Message Format

All messages are sent as JSON over WebSocket, with one message per line (newline-delimited JSON).

### Generic Message Structure

```json
{
    "cmd": "CommandName",
    "field1": "value1",
    "field2": 123,
    ...
}
```

## Messages from Game → Proxy → Server

### Connect
Sent when the game initially connects to the proxy.

```json
{
    "cmd": "Connect",
    "game": "Dicey Dungeons",
    "name": "PlayerName",
    "seed_name": "optional_seed_name",
    "version": "optional_version_info"
}
```

**Fields:**
- `game` (required): Must be "Dicey Dungeons"
- `name` (required): Player's name in the slot
- `seed_name` (optional): Seed name to validate against server
- `version` (optional): Client version for compatibility tracking

**Validation:**
- Game must be "Dicey Dungeons"
- Seed name must match server (if provided)
- Player name must match connected slot (if saved)

---

### LocationCheck
Sent when the player checks/completes a location.

```json
{
    "cmd": "LocationCheck",
    "location_id": 11101
}
```

**Fields:**
- `location_id` (required): Integer ID of the location being checked

**Location ID Reference:**
- **Level Locations**: `10<episode><level>` (e.g., 1012 = Episode 1 Level 2)
- **Chest Locations**: `<episode><floor>101<number>` (e.g., 11101 = Ep1 Floor1 Chest1)
- **Shop Locations**: `<episode><floor>201<number>` (e.g., 11201 = Ep1 Floor1 Shop1)
- **Heal Locations**: `<episode><floor>301<number>` (e.g., 11301 = Ep1 Floor1 Heal1)
- **Upgrade Locations**: `<episode><floor>401<number>` (e.g., 11401 = Ep1 Floor1 Upgrade1)
- **Trade Locations**: `<episode><floor>501<number>` (e.g., 11501 = Ep1 Floor1 Trade1)

**Examples:**
```json
{
    "cmd": "LocationCheck",
    "location_id": 1012
}
```
(Checks Episode 1 Level 2)

---

### StatusUpdate
Update player status (sent by CLI).

```json
{
    "cmd": "StatusUpdate",
    "status": 30
}
```

**Status Codes:**
- 10: Connected
- 20: Busy
- 30: Ready

---

### Bounce
Mirror/echo message back through server (used for DeathLink).

```json
{
    "cmd": "Bounce",
    "tags": ["DeathLink"],
    "data": {
        "source_player": 2,
        "cause": "Lava",
        "time": 1234567890.123
    }
}
```

---

## Messages from Server → Proxy → Game

### Connected
Sent by proxy when connection to server is established.

```json
{
    "cmd": "Connected",
    "team": 0,
    "slot": 2,
    "slot_info": {
        "2": {
            "name": "PlayerName",
            "game": "Dicey Dungeons",
            "type": 0
        }
    },
    "players": [
        {
            "team": 0,
            "slot": 2,
            "name": "PlayerName",
            "alias": "P1"
        }
    ],
    "seed_name": "Seed Name",
    "seed": 12345,
    "timestamp": 1704384000,
    "datapackage_checksums": {
        "Dicey Dungeons": "abc123def456..."
    },
    "datapackage_version": 1
}
```

**Important Fields:**
- `team`: Team number (usually 0)
- `slot`: Player slot number
- `seed_name`: Name of the current seed
- `players`: List of players in the game (reduced to only current player by proxy)
- `slot_info`: Information about all slots (empty dict sent by proxy to reduce data)

---

### ReceivedItems
Items received from the server for this player.

```json
{
    "cmd": "ReceivedItems",
    "index": 0,
    "items": [
        ["Warrior Weapon 1", 0, 2, 0],
        ["Warrior Weapon 2", 1, 1, 0],
        ["Dice Shard", 9999, 3, 0]
    ]
}
```

**Structure:**
- `index`: Starting index in the item list (usually 0 for sync)
- `items`: Array of `[name, id, player_id, flags]`
  - `name`: Item name
  - `id`: Item ID in the game's item list
  - `player_id`: Slot number of the source player
  - `flags`: Bitflags (usually 0, can indicate special item properties)

---

### RoomUpdate
Sent when room state changes (other players connecting, status changes, etc.).

```json
{
    "cmd": "RoomUpdate",
    "players": [
        {
            "team": 0,
            "slot": 1,
            "name": "OtherPlayer",
            "alias": "P2",
            "status": 20
        },
        {
            "team": 0,
            "slot": 2,
            "name": "PlayerName",
            "alias": "P1",
            "status": 30
        }
    ],
    "hint_points": 0,
    "checked_locations": [11101, 11102],
    "missing_locations": [11201, 11202, 11203]
}
```

**Note:** Proxy reduces this to empty player list to reduce bandwidth.

---

### PrintJSON
Chat or notification message from server.

```json
{
    "cmd": "PrintJSON",
    "data": [
        {"text": "PlayerName", "color": "magenta"},
        {"text": " received "},
        {"text": "Warrior Weapon 1", "color": "yellow", "player_slot": 1}
    ],
    "type": "Chat"
}
```

**Message Types:**
- "Chat": Regular chat message
- "ItemSend": Item sent notification
- "Hint": Hint response
- "Alert": Important notification

---

### RoomInfo
Initial room information (sent by proxy when game connects if already connected to server).

```json
{
    "cmd": "RoomInfo",
    "version": {
        "major": 0,
        "minor": 4,
        "build": 5,
        "class": "Version"
    },
    "seed_name": "Seed Name",
    "seed": 12345,
    "room_seed": 54321,
    "forfeit_mode": "auto",
    "remaining_mode": "goal",
    "remaining": 0,
    "hint_cost": 100,
    "location_check_points": 1
}
```

---

### InvalidPacket
Sent when an invalid packet is received.

```json
{
    "cmd": "InvalidPacket",
    "text": "Unable to parse your packet: invalid JSON"
}
```

---

### ConnectionRefused
Connection to server failed or was rejected.

```json
{
    "cmd": "ConnectionRefused",
    "errors": [
        "Seed mismatch",
        "Player name mismatch"
    ]
}
```

---

## Connection Validation

The proxy performs validation before forwarding connection to server:

### Valid Connect Example
```json
{
    "cmd": "Connect",
    "game": "Dicey Dungeons",
    "name": "ValidPlayerName",
    "seed_name": "ValidSeed"
}
```

### Invalid - Wrong Game
```json
{
    "cmd": "Connect",
    "game": "Some Other Game",
    "name": "PlayerName"
}
```
Result: Connection aborted, error message sent to game

### Invalid - Seed Mismatch
```json
{
    "cmd": "Connect",
    "game": "Dicey Dungeons",
    "name": "PlayerName",
    "seed_name": "WrongSeed"
}
```
Result: Connection aborted if game has a saved seed that differs

---

## Message Flow Example

### Typical Session

1. **Game Connects**
   ```
   Game → Proxy: {"cmd": "Connect", "game": "Dicey Dungeons", "name": "Player1"}
   Proxy → Server: Forward Connect
   ```

2. **Server Acknowledges**
   ```
   Server → Proxy: {"cmd": "Connected", "team": 0, "slot": 1, ...}
   Proxy → Game: {"cmd": "Connected", "team": 0, "slot": 1, ...} (reduced)
   ```

3. **Game Receives Initial Items**
   ```
   Server → Proxy: {"cmd": "ReceivedItems", "items": [[item1, id1, ...], ...]}
   Proxy → Game: {"cmd": "ReceivedItems", ...}
   ```

4. **Player Checks Location**
   ```
   Game → Proxy: {"cmd": "LocationCheck", "location_id": 11101}
   Proxy → Server: Forward LocationCheck
   ```

5. **Server Broadcasts Item**
   ```
   Server → Other Game: item from Player1's location
   Server → Proxy: {"cmd": "ReceivedItems", "items": [[new_item, id, ...]]}
   Proxy → Game: {"cmd": "ReceivedItems", ...}
   ```

---

## Best Practices

1. **Error Handling**: Game should handle all message types gracefully
2. **Validation**: Always validate location IDs before checking
3. **Retries**: Connection failures should retry with exponential backoff
4. **Logging**: Log message flow for debugging
5. **Timeouts**: Set reasonable timeouts for WebSocket operations
6. **Buffering**: Buffer outgoing location checks if connection is temporarily down
7. **Parsing**: Handle unknown message types gracefully (future compatibility)

---

## Implementation Checklist

- [ ] Parse Connect message from game
- [ ] Validate game name, seed, player name
- [ ] Send Connected message when server confirms
- [ ] Handle LocationCheck messages from game
- [ ] Forward LocationCheck to server
- [ ] Process ReceivedItems from server
- [ ] Display items to player
- [ ] Handle PrintJSON messages
- [ ] Graceful disconnection
- [ ] Reconnection logic
- [ ] Error message handling
- [ ] Debug logging

---

## Debug Commands

Enable debug mode in Client.py to see all messages:
```python
DEBUG = True
```

This will log all incoming and outgoing messages to the console.

# Dicey Dungeons Archipelago Client Documentation Index

## 📋 Quick Reference

**What is this?** A complete MVP (Minimum Viable Product) Archipelago client for Dicey Dungeons.

**Main file:** `Client.py`

**Runs on:** `localhost:11312` (configurable)

**Start with:** Read `QUICK_START.md` for setup instructions

---

## 📚 Documentation Files

### For Getting Started
1. **QUICK_START.md** ⭐ **START HERE**
   - How to run the client
   - Manual testing instructions
   - Troubleshooting guide
   - Common issues and solutions

2. **IMPLEMENTATION_SUMMARY.md**
   - What was created and why
   - Architecture overview
   - Features implemented
   - Next steps for development

### For Technical Details
3. **CLIENT_README.md**
   - Complete architecture documentation
   - Component descriptions
   - Configuration options
   - Extension points
   - Available commands

4. **MESSAGE_PROTOCOL.md**
   - Complete message format reference
   - All message types with examples
   - Location ID reference
   - Connection validation rules
   - Message flow examples

### For Game Integration
5. **GAME_INTEGRATION_EXAMPLE.py**
   - Complete example implementation
   - How to integrate with game code
   - Event callback system
   - Full working example

---

## 🎯 Quick Navigation

### "How do I start the client?"
→ See **QUICK_START.md** → "Setup" section

### "What messages does the game send?"
→ See **MESSAGE_PROTOCOL.md** → "Messages from Game" section

### "How does the architecture work?"
→ See **CLIENT_README.md** → "Architecture" section OR **IMPLEMENTATION_SUMMARY.md** → "How It Works"

### "What if I get an error?"
→ See **QUICK_START.md** → "Common Issues" section

### "How do I integrate this with my game?"
→ See **GAME_INTEGRATION_EXAMPLE.py** for complete example code

### "What location IDs should I use?"
→ See **MESSAGE_PROTOCOL.md** → "Location ID Reference"

---

## 🗂️ File Structure

```
worlds/diceydungeons/
├── Client.py                        ⭐ MAIN CLIENT
├── 
├── DOCUMENTATION:
├── ├── README_INDEX.md              (this file)
├── ├── QUICK_START.md               (setup & troubleshooting)
├── ├── IMPLEMENTATION_SUMMARY.md    (overview & architecture)
├── ├── CLIENT_README.md             (technical details)
├── └── MESSAGE_PROTOCOL.md          (message format reference)
├──
├── EXAMPLE CODE:
├── └── GAME_INTEGRATION_EXAMPLE.py  (game integration)
├──
├── WORLD CODE:
├── ├── world.py
├── ├── items.py
├── ├── locations.py
├── ├── regions.py
├── ├── rules.py
├── ├── options.py
├── ├── web_world.py
├── └── __init__.py
└── ...
```

---

## 🚀 Getting Started (TL;DR)

### Step 1: Run the Client
```bash
cd AP_diceydungeons
python worlds/diceydungeons/Client.py --connect <server_address> --password <password>
```

### Step 2: Connect Your Game
Game connects to: `ws://localhost:11312/`

Send Connect message:
```json
{
    "cmd": "Connect",
    "game": "Dicey Dungeons",
    "name": "PlayerName",
    "seed_name": "SeedName"
}
```

### Step 3: Report Location Checks
```json
{
    "cmd": "LocationCheck",
    "location_id": 11101
}
```

That's it! For more details, see **QUICK_START.md**

---

## 📖 Documentation by Topic

### Connection & Setup
- How to start: **QUICK_START.md** - "Setup"
- Configuration: **CLIENT_README.md** - "Configuration"
- Validation: **MESSAGE_PROTOCOL.md** - "Connection Validation"

### Messages & Protocol
- All messages: **MESSAGE_PROTOCOL.md**
- Game → Server: **MESSAGE_PROTOCOL.md** - "Messages from Game"
- Server → Game: **MESSAGE_PROTOCOL.md** - "Messages from Server"
- Examples: **MESSAGE_PROTOCOL.md** - "Message Flow Example"

### Architecture
- Overview: **IMPLEMENTATION_SUMMARY.md** - "How It Works"
- Technical: **CLIENT_README.md** - "Architecture"
- Diagram: **CLIENT_README.md** - "How It Works" section

### Game Integration
- Step-by-step: **GAME_INTEGRATION_EXAMPLE.py**
- Class reference: See docstrings in `GAME_INTEGRATION_EXAMPLE.py`
- Best practices: **MESSAGE_PROTOCOL.md** - "Best Practices"

### Testing & Debugging
- Testing guide: **QUICK_START.md** - "Testing the Client"
- Debugging: **QUICK_START.md** - "Debugging"
- Debug mode: **QUICK_START.md** - "Enable Debug Mode"

### Troubleshooting
- Common issues: **QUICK_START.md** - "Common Issues"
- Error messages: **QUICK_START.md** - "Common Issues"
- Debug output: **CLIENT_README.md** - "Status" command

---

## 🔧 Key Concepts

### The Proxy Pattern
```
Game ←→ Proxy Server ←→ Archipelago Server
      localhost:11312
```

The client acts as a proxy/bridge allowing the game to communicate with Archipelago without needing network configuration.

### Connection Flow
1. Game connects to proxy
2. Proxy validates connection
3. Proxy connects to server (if not already)
4. Messages are routed between game and server

### Location IDs
Standardized format: `<episode><floor><type><number>`
- Episode: 1-6
- Floor: 1-6
- Type: 1=Chest, 2=Shop, 3=Heals, 4=Upgrades, 5=Trades

Example: `11101` = Episode 1, Floor 1, Chest 1

Full reference: **MESSAGE_PROTOCOL.md**

---

## 💡 Common Tasks

### Task: Add a custom command
→ See **CLIENT_README.md** → "Extension Points"

### Task: Handle a new message type
→ Modify `DiceyDungeonsContext.on_package()` in **Client.py**

### Task: Change the proxy port
→ Edit `websockets.serve()` call in `launch()` function in **Client.py**

### Task: Add DeathLink support
→ See **CLIENT_README.md** → "Future enhancements"

### Task: Test without the actual game
→ **QUICK_START.md** → "Testing the Client"

### Task: Enable debug logging
→ **QUICK_START.md** → "Enable Debug Mode"

---

## ✅ Checklist for Integration

- [ ] Read **QUICK_START.md**
- [ ] Run the client successfully
- [ ] Understand the architecture from **CLIENT_README.md**
- [ ] Review message protocol in **MESSAGE_PROTOCOL.md**
- [ ] Study **GAME_INTEGRATION_EXAMPLE.py**
- [ ] Map your location IDs to standard format
- [ ] Implement game connection code
- [ ] Test with WebSocket client
- [ ] Test with actual server
- [ ] Handle item delivery in game
- [ ] Display notifications to player
- [ ] Add in-game debugging/status display

---

## 🎓 Learning Path

**Beginner (Just want to use it):**
1. Read QUICK_START.md
2. Run the client
3. Test with WebSocket client

**Intermediate (Want to integrate):**
1. Read QUICK_START.md
2. Read IMPLEMENTATION_SUMMARY.md
3. Study GAME_INTEGRATION_EXAMPLE.py
4. Read MESSAGE_PROTOCOL.md
5. Integrate with your game

**Advanced (Want to customize):**
1. Read all documentation
2. Study Client.py code
3. Understand the architecture deeply
4. Modify for specific needs
5. Add custom features

---

## 🔗 Related Resources

### Archipelago
- Main site: https://archipelago.gg/
- AP Docs: https://archipelago.gg/apworld/
- Client API: See CommonClient.py in this project

### Reference Implementations
- A Hat in Time: `worlds/ahit/Client.py`
- Other clients: Various `worlds/*/Client.py` files

### WebSocket
- Python websockets: https://websockets.readthedocs.io/
- JSON Format: Standard RFC 7159

---

## 📞 Support

### Can't find the answer?
1. Search this documentation (use Ctrl+F)
2. Check **CLIENT_README.md** for detailed info
3. Review **GAME_INTEGRATION_EXAMPLE.py** for patterns
4. Look at **MESSAGE_PROTOCOL.md** for message details
5. Check **QUICK_START.md** for common issues

### Still stuck?
1. Enable debug mode in Client.py
2. Check the client output/logs
3. Review the architecture in IMPLEMENTATION_SUMMARY.md
4. Compare your code with GAME_INTEGRATION_EXAMPLE.py

---

## 📝 Version Info

- **Client Version:** MVP (Minimum Viable Product)
- **Features:** Core functionality for item distribution and location checking
- **Status:** Ready for testing and integration

---

## 🎯 Next Steps

1. **For Quick Start:** Open `QUICK_START.md`
2. **For Integration:** Open `GAME_INTEGRATION_EXAMPLE.py`
3. **For Reference:** Open `MESSAGE_PROTOCOL.md`
4. **For Deep Dive:** Open `CLIENT_README.md`

---

**Happy integrating! 🚀**

# Dicey Dungeons Archipelago Client - Haxe Integration Guide

## Overview

The Archipelago client now uses a **pull-based model** for item distribution with **filtering and categorization**. Instead of the client pushing items to the game, the game actively requests items from the client and can filter them by episode, location type, role, or item type. Items are returned categorized by location type (chest, shop, heal, upgrade, trade).

## What Changed

### Old Model (Push-Based)
- Server sends items → Client stores them → Client automatically pushes to Game
- Game has no control over item delivery timing
- All items sent in one batch on connection

### New Model (Pull-Based with Filtering)
- Server sends items → Client stores them with metadata → Game requests items with optional filters
- Game can request all items or filter by episode, location type, role, or item type
- Items are organized by location_type in response (chest_items, shop_items, heal_items, upgrade_items, trade_items, etc.)
- Better synchronization and organization

## Quick Start with Haxe

### 1. Initialize the Integration

```haxe
var integration = new DiceyDungeonsGameIntegration("PlayerName", "SeedName");

integration.connect(
    "ws://localhost:11312/",
    function() {
        trace("Connected!");
    },
    function(error: String) {
        trace("Connection failed: " + error);
    }
);
```

### 2. Request Items When Needed

```haxe
// Get all items (no filters)
integration.getItems(
    null,  // no filters
    function(response: Dynamic) {
        // Items are categorized by type:
        // response.chest_items, response.shop_items, response.heal_items, etc.
        
        var chestItems: Array<ArchipelagoItem> = Reflect.field(response, "chest_items");
        for (item in chestItems) {
            applyItemToGame(item);
        }
    },
    function(error: String) {
        trace("Error: " + error);
    }
);
```

### 3. Request Items with Filters

```haxe
// Get items for a specific episode
var episodeFilter = {
    episode: 1
};

integration.getItems(
    episodeFilter,
    function(response: Dynamic) {
        // Handle Episode 1 items
        trace("Got " + response.total_matching + " items for Episode 1");
    },
    function(error: String) {
        trace("Error: " + error);
    }
);
```

### 4. Filter by Location Type

```haxe
// Get only shop items
var shopFilter = {
    location_type: "shop"
};

integration.getItems(
    shopFilter,
    function(response: Dynamic) {
        var shopItems: Array<ArchipelagoItem> = Reflect.field(response, "shop_items");
        for (item in shopItems) {
            addItemToShop(item);
        }
    },
    function(error: String) {
        trace("Error: " + error);
    }
);
```

### 5. Multiple Filters

```haxe
// Get chest items from Episode 2 only
var complexFilter = {
    episode: 2,
    location_type: "chest"
};

integration.getItems(
    complexFilter,
    function(response: Dynamic) {
        // Only Episode 2 chest items
        var chestItems: Array<ArchipelagoItem> = Reflect.field(response, "chest_items");
    },
    function(error: String) {
        trace("Error: " + error);
    }
);
```

### 6. Send Location Checks

```haxe
// When player collects an item, defeats a boss, etc.
integration.checkLocation(11101);  // Ep1 Floor1 Chest1
integration.checkLocation(12101);  // Boss check
```

### 5. Listen for Server Events

```haxe
// Chat messages from the server
integration.registerCallback("print", function(text: String) {
    showChatMessage(text);
});

// Room state updates
integration.registerCallback("room_update", function(data: Dynamic) {
    updateGameState(data);
});

// Items received response
integration.registerCallback("items_received", function(response: Dynamic) {
    // This fires when GetItems response arrives
    var totalItems = response.total_items;
    var totalMatching = response.total_matching;
});
```

## API Reference

### Class: `DiceyDungeonsGameIntegration`

#### Constructor
```haxe
new DiceyDungeonsGameIntegration(playerName: String, seedName: String)
```

#### Methods

##### `connect(proxyUrl: String, onSuccess: Void -> Void, onError: String -> Void)`
Connect to the Archipelago proxy server.

**Parameters:**
- `proxyUrl`: WebSocket URL (default: `ws://localhost:11312/`)
- `onSuccess`: Called when connection succeeds
- `onError`: Called if connection fails, receives error message

**Example:**
```haxe
integration.connect(
    "ws://localhost:11312/",
    function() { trace("Connected!"); },
    function(err) { trace("Failed: " + err); }
);
```

##### `disconnect()`
Disconnect from the proxy server.

```haxe
integration.disconnect();
```

##### `getItems(?filters: Dynamic, onItemsReceived: Dynamic -> Void, onError: String -> Void): Bool`
Request items from the client with optional filtering.

**Parameters:**
- `filters`: Optional filter object with any/all of:
  - `episode`: Int (1-6) - filter by episode
  - `location_type`: String or Array<String> - filter by location type(s)
    - Valid types: "chest", "shop", "heal", "upgrade", "trade", etc.
  - `role`: String or Array<String> - filter by character role
  - `item_type`: String or Array<String> - filter by item type
- `onItemsReceived`: Called when items arrive, receives response object with categorized items
- `onError`: Called if request fails

**Returns:** `true` if request was sent, `false` if not connected

**Response Structure:**
The response object has:
- `cmd`: "ReceivedItems"
- `total_items`: Total items available for this player
- `total_matching`: Items matching the filters
- `filters_applied`: The filters that were used
- `<type>_items`: Arrays grouped by location type (chest_items, shop_items, heal_items, upgrade_items, trade_items)

**Example:**
```haxe
// Get chest items only
integration.getItems(
    { location_type: "chest" },
    function(response) {
        var chestItems: Array<ArchipelagoItem> = Reflect.field(response, "chest_items");
        trace("Chest items: " + chestItems.length);
    },
    function(err) { trace("Error: " + err); }
);
```

##### `checkLocation(locationId: Int): Bool`
Report a location check to the Archipelago server.

**Parameters:**
- `locationId`: ID of the location being checked

**Returns:** `true` if message was sent, `false` if not connected

**Example:**
```haxe
if (integration.checkLocation(11101)) {
    trace("Location 11101 checked!");
}
```

##### `registerCallback(event: String, callback: Dynamic -> Void)`
Register a callback for server events.

**Parameters:**
- `event`: Event name ("items_received", "print", "room_update", "connected")
- `callback`: Function to call when event occurs

**Example:**
```haxe
integration.registerCallback("connected", function(data) {
    trace("Server connected!");
});
```

### Types

#### `ArchipelagoItem`
```haxe
typedef ArchipelagoItem = {
    name: String,      // Item name (e.g., "Warrior Weapon 1")
    id: Int,           // Item ID in the game
    player_id: Int,    // Slot number of the source player
    flags: Int         // Bitflags (usually 0)
}
```

## Filter Options

### Filter Structure
Filters are optional. Pass `null` or an empty object `{}` to get all items.

```haxe
var filters = {
    episode: 1,                      // Int: 1-6
    location_type: "chest",          // String or Array<String>
    role: "warrior",                 // String or Array<String>: "warrior", "thief", "witch", "jester", "inventor", "robot"
    item_type: "weapon"              // String or Array<String>
};
```

### Available Location Types
- `chest` - Chest items
- `shop` - Shop items
- `heal` - Healing items
- `upgrade` - Upgrade items
- `trade` - Trade items

### Available Roles
- `warrior`
- `thief`
- `witch`
- `jester`
- `inventor`
- `robot`

### Example Filters

Get all items:
```haxe
integration.getItems(null, onItemsReceived, onError);
```

Get Episode 1 items:
```haxe
integration.getItems({ episode: 1 }, onItemsReceived, onError);
```

Get chest and shop items:
```haxe
integration.getItems({ location_type: ["chest", "shop"] }, onItemsReceived, onError);
```

Get warrior items from Episode 2:
```haxe
integration.getItems({ role: "warrior", episode: 2 }, onItemsReceived, onError);
```

Get heal items for any episode:
```haxe
integration.getItems({ location_type: "heal" }, onItemsReceived, onError);
```

## Common Patterns

### Pattern 1: Load All Items on Game Start
```haxe
integration.getItems(
    null,
    function(response) {
        // Handle all items, organized by location type
        for (key in Reflect.fields(response)) {
            if (key.endsWith("_items")) {
                var items: Array<ArchipelagoItem> = Reflect.field(response, key);
                trace(key + ": " + items.length);
            }
        }
    },
    function(err) { showError(err); }
);
```

### Pattern 2: Populate Episode Content
```haxe
function populateEpisode(episodeNum: Int) {
    integration.getItems(
        { episode: episodeNum },
        function(response) {
            // Populate this episode with filtered items
            var chestItems: Array<ArchipelagoItem> = Reflect.field(response, "chest_items");
            var shopItems: Array<ArchipelagoItem> = Reflect.field(response, "shop_items");
            
            populateChests(chestItems);
            populateShops(shopItems);
        },
        function(err) { trace("Error: " + err); }
    );
}
```

### Pattern 3: Get Specific Location Type Items
```haxe
function getShopItems() {
    integration.getItems(
        { location_type: "shop" },
        function(response) {
            var shopItems: Array<ArchipelagoItem> = Reflect.field(response, "shop_items");
            updateShopUI(shopItems);
        },
        function(err) { trace("Error: " + err); }
    );
}
```

### Pattern 4: Full Resync
```haxe
function fullResync() {
    // Get all items again (useful for debugging or re-initialization)
    integration.getItems(
        null,
        function(response) {
            trace("Resynced: " + response.total_items + " items");
            // Process all items
        },
        function(err) { showError(err); }
    );
}
```

### Pattern 5: Multiple Category Filtering
```haxe
// Get all chest items from warrior role
var filter = {
    location_type: "chest",
    role: "warrior"
};

integration.getItems(
    filter,
    function(response) {
        var chestItems: Array<ArchipelagoItem> = Reflect.field(response, "chest_items");
        trace("Found " + chestItems.length + " warrior chest items");
    },
    function(err) { trace("Error: " + err); }
);
```

## Location ID Reference

Location IDs follow this format: `<episode><floor><type><number>`

**Type codes:**
- `10`: Level check (e.g., episode 1, level 2 = 1012)
- `01`: Chest (floor check) (e.g., Ep1 Floor1 Chest1 = 11101)
- `02`: Shop (e.g., Ep1 Floor1 Shop1 = 11201)
- `03`: Heal (e.g., Ep1 Floor1 Heal1 = 11301)
- `04`: Upgrade (e.g., Ep1 Floor1 Upgrade1 = 11401)
- `05`: Trade (e.g., Ep1 Floor1 Trade1 = 11501)

**Examples:**
- `1012` - Episode 1, Level 2
- `21105` - Episode 2, Floor 1, Upgrade 1
- `32203` - Episode 3, Floor 2, Heal 1

## Troubleshooting

### "Not connected to Archipelago"
**Problem:** Getting this error when trying to request items or check locations.

**Solution:** 
1. Make sure `connect()` has completed successfully
2. Check that the proxy server is running on `localhost:11312`
3. Verify your firewall isn't blocking the connection

### Items not appearing
**Problem:** Called `getItems()` but items don't show up in response.

**Solution:**
1. Check the `onError` callback for error messages
2. Verify location checks are being sent (check `checkLocation()` calls)
3. Make sure items are actually due to your player in the multiworld
4. Try requesting all items: `integration.getItems(null, ...)`
5. Check `response.total_items` vs `response.total_matching` to see if filters are working

### Connection drops unexpectedly
**Problem:** Was connected, then suddenly disconnected.

**Solution:**
1. Implement reconnection logic in your game
2. Check the client logs for error messages
3. Verify the proxy server is still running

### Callback not being called
**Problem:** Registered a callback but it's not firing.

**Solution:**
1. Check the event name spelling (case-sensitive)
2. For `items_received`, it fires when GetItems response arrives
3. Ensure the response completed without error
4. Check console/trace output for callback errors

### Filter not working
**Problem:** Filter values aren't reducing items in response.

**Solution:**
1. Check that filter names are spelled correctly (episode, location_type, role, item_type)
2. Verify filter values are valid (e.g., episode 1-6, location_type "chest"/"shop"/etc.)
3. Items in the metadata might not have all filter properties
4. Try requesting all items first: `getItems(null, ...)` to see what you have

## Integration Checklist

- [ ] Create `DiceyDungeonsGameIntegration` instance
- [ ] Call `connect()` on game startup
- [ ] Request initial items with `getItems(null, ...)`
- [ ] Process categorized items from response (chest_items, shop_items, etc.)
- [ ] Send location checks with `checkLocation()` when appropriate
- [ ] Handle item requests with appropriate filters (episode, location_type, etc.)
- [ ] Register callbacks for important events
- [ ] Handle disconnection/reconnection gracefully
- [ ] Show appropriate UI feedback to player
- [ ] Populate game content based on filtered items

## Item Metadata Integration

The Client pulls item metadata from `worlds/diceydungeons/data/extracted_data.py`. Each item has:
- `role`: Character class (warrior, thief, witch, jester, inventor, robot)
- `item_type`: Type of item (weapon, support, consumable, dice_upgrade, etc.)
- `episode`: Which episode this item appears in (1-6)
- `location_type`: Where this item is found (chest, shop, heal, upgrade, trade)

This allows the game to:
- Filter items by episode when populating specific chapters
- Organize items by location type for proper UI placement
- Filter by character role for role-specific content
- Categorize by item type for inventory systems

## Next Steps

See [HAXE_INTEGRATION_EXAMPLE.hx](HAXE_INTEGRATION_EXAMPLE.hx) for a complete working example including:
- Full connection flow
- Item request patterns with filtering
- Multiple categorization examples
- Event callback setup
- Error handling
- Game event simulation

/**
 * Dicey Dungeons Archipelago Client Integration - Haxe Example
 * 
 * This is a reference implementation showing how a Dicey Dungeons mod would
 * integrate with the Archipelago client using Haxe.
 * 
 * The client runs as a separate server, and the game connects to it to:
 * 1. Report location checks (items collected, bosses defeated, etc.)
 * 2. PULL items from the client when needed (pull-based model)
 * 3. Communicate game state
 */

package archipelago;

import sys.net.Socket;

#if js
import js.html.WebSocket;
#elseif sys
import websocket.WebSocket;
#end

typedef ArchipelagoItem = {
    name: String,
    id: Int,
    player_id: Int,
    flags: Int
}

typedef ItemsResponse = {
    cmd: String,
    total_items: Int,
    total_matching: Int,
    filters_applied: Dynamic,
    // Items are grouped by type as arrays like:
    // chest_items: Array<ArchipelagoItem>,
    // shop_items: Array<ArchipelagoItem>,
    // heal_items: Array<ArchipelagoItem>,
    // etc.
}

/**
 * Handles communication between Dicey Dungeons and the Archipelago proxy.
 * 
 * Uses a pull-based model where the game requests items from the client
 * instead of the client pushing items to the game.
 * 
 * This would be instantiated once when the game loads and persists
 * throughout the gameplay session.
 */
class DiceyDungeonsGameIntegration {
    
    public var playerName: String;
    public var seedName: String;
    public var isConnected: Bool = false;
    public var receivedItems: Array<ArchipelagoItem> = [];
    
    private var websocket: WebSocket;
    private var messageCallbacks: Map<String, Array<Dynamic -> Void>> = [];
    
    /**
     * Initialize the game integration.
     * 
     * @param playerName The player's name in Archipelago
     * @param seedName The seed name to validate against the save file
     */
    public function new(playerName: String, seedName: String) {
        this.playerName = playerName;
        this.seedName = seedName;
        this.messageCallbacks = new Map();
    }
    
    /**
     * Connect to the Archipelago proxy server.
     * 
     * @param proxyUrl URL of the proxy server (default ws://localhost:11312/)
     * @param onSuccess Callback when connection succeeds
     * @param onError Callback when connection fails, receives error message
     */
    public function connect(
        proxyUrl: String = "ws://localhost:11312/",
        onSuccess: Void -> Void,
        onError: String -> Void
    ): Void {
        
        try {
            #if js
            this.websocket = new WebSocket(proxyUrl);
            this.websocket.onopen = function() {
                sendConnectMessage(onSuccess, onError);
            };
            this.websocket.onerror = function(err) {
                onError("WebSocket error");
                this.isConnected = false;
            };
            this.websocket.onmessage = function(msg: Dynamic) {
                handleMessage(msg.data);
            };
            this.websocket.onclose = function() {
                this.isConnected = false;
            };
            #elseif sys
            this.websocket = new WebSocket(proxyUrl);
            this.isConnected = true;
            sendConnectMessage(onSuccess, onError);
            // Start async message receiving
            receiveMessagesAsync();
            #end
            
        } catch (e: Dynamic) {
            onError('Failed to connect to Archipelago proxy: ${Std.string(e)}');
        }
    }
    
    /**
     * Send the initial connection message to the proxy.
     */
    private function sendConnectMessage(onSuccess: Void -> Void, onError: String -> Void): Void {
        var connectMsg = {
            cmd: "Connect",
            game: "Dicey Dungeons",
            name: playerName,
            seed_name: seedName
        };
        
        try {
            sendMessage(connectMsg);
            this.isConnected = true;
            onSuccess();
        } catch (e: Dynamic) {
            onError('Failed to send connect message: ${Std.string(e)}');
            this.isConnected = false;
        }
    }
    
    /**
     * Disconnect from the proxy server.
     */
    public function disconnect(): Void {
        if (websocket != null) {
            websocket.close();
            isConnected = false;
        }
    }
    
    /**
     * Report a location check to the Archipelago server.
     * 
     * This should be called when the player collects an item, defeats
     * a boss, completes a floor, or any other trackable event.
     * 
     * @param locationId The ID of the location being checked
     * @return True if message sent successfully
     */
    public function checkLocation(locationId: Int): Bool {
        if (!isConnected || websocket == null) {
            return false;
        }
        
        try {
            var msg = {
                cmd: "LocationCheck",
                location_id: locationId
            };
            sendMessage(msg);
            return true;
        } catch (e: Dynamic) {
            trace('Failed to send location check: ${Std.string(e)}');
            return false;
        }
    }
    
    /**
     * Request items from the Archipelago client using the pull-based model.
     * 
     * Returns ALL items collected for this player, optionally filtered by
     * episode, location type, role, or item type. Items are categorized
     * into groups like chest_items, shop_items, heal_items, etc.
     * 
     * @param filters Optional filters (all optional):
     *   - episode: Int (1-6) - filter by episode
     *   - location_type: String or Array<String> - filter by location type
     *   - role: String or Array<String> - filter by character role
     *   - item_type: String or Array<String> - filter by item type
     * @param onItemsReceived Callback when items are received with categorized items
     * @param onError Callback when request fails
     * @return True if request sent successfully
     */
    public function getItems(
        ?filters: Dynamic,
        onItemsReceived: Dynamic -> Void,
        onError: String -> Void
    ): Bool {
        
        if (!isConnected || websocket == null) {
            onError("Not connected to Archipelago");
            return false;
        }
        
        try {
            var msg: Dynamic = {
                cmd: "GetItems"
            };
            
            if (filters != null) {
                msg.filters = filters;
            }
            
            // Register a one-time callback for this specific request
            var callbackKey = 'items_requested_${Date.now().getTime()}';
            registerCallback(callbackKey, function(response: Dynamic) {
                onItemsReceived(response);
                // Clean up the callback
                messageCallbacks.remove(callbackKey);
            });
            
            sendMessage(msg);
            return true;
            
        } catch (e: Dynamic) {
            onError('Failed to request items: ${Std.string(e)}');
            return false;
        }
    }
    
    /**
     * Process a message from the proxy.
     */
    private function processMessage(data: Dynamic): Void {
        var cmd: String = data.cmd;
        
        switch (cmd) {
            case "ReceivedItems":
                // Items response from a GetItems request (categorized by location type)
                var response: Dynamic = data;
                
                // Items are now categorized (chest_items, shop_items, heal_items, etc.)
                // Collect all items from categories into receivedItems
                for (key in Reflect.fields(response)) {
                    if (key.endsWith("_items") && Std.is(Reflect.field(response, key), Array)) {
                        var itemArray: Array<ArchipelagoItem> = Reflect.field(response, key);
                        receivedItems = receivedItems.concat(itemArray);
                    }
                }
                
                // Dispatch callback with the full response (includes categorized items)
                dispatchCallback("items_received", response);
                trace('Received items: total=${response.total_items}, matching=${response.total_matching}');
                
            case "PrintJSON":
                // Chat message or notification
                var text: String = data.data[0].text ?? "";
                dispatchCallback("print", text);
                trace('[Server] $text');
                
            case "RoomUpdate":
                // Room state has changed
                dispatchCallback("room_update", data);
                
            case "Connected":
                // Acknowledged connection
                dispatchCallback("connected", data);
                trace("Successfully connected to Archipelago server!");
                
            default:
                // Unknown command
                dispatchCallback("unknown", data);
        }
    }
    
    /**
     * Send a message to the proxy.
     */
    private function sendMessage(data: Dynamic): Void {
        var jsonStr = haxe.Json.stringify(data);
        #if js
        if (websocket.readyState == WebSocket.OPEN) {
            websocket.send(jsonStr);
        }
        #elseif sys
        if (websocket != null && !websocket.isClosed()) {
            websocket.send(jsonStr);
        }
        #end
    }
    
    /**
     * Receive messages asynchronously (for non-JS targets).
     */
    #if sys
    private function receiveMessagesAsync(): Void {
        // This would typically run in a background thread or async loop
        // Implementation depends on your game's threading model
        trace("Message receiving started (implementation depends on target platform)");
    }
    #end
    
    /**
     * Handle a message received from the proxy.
     */
    private function handleMessage(messageData: String): Void {
        try {
            var data: Dynamic = haxe.Json.parse(messageData);
            processMessage(data);
        } catch (e: Dynamic) {
            trace('Invalid JSON received: $messageData');
        }
    }
    
    /**
     * Register a callback for an event.
     * 
     * @param event Event name ("items_received", "print", "room_update", "connected", etc.)
     * @param callback Function to invoke when event occurs
     */
    public function registerCallback(event: String, callback: Dynamic -> Void): Void {
        if (!messageCallbacks.exists(event)) {
            messageCallbacks.set(event, []);
        }
        messageCallbacks.get(event).push(callback);
    }
    
    /**
     * Dispatch all callbacks for an event.
     */
    private function dispatchCallback(event: String, data: Dynamic): Void {
        if (messageCallbacks.exists(event)) {
            var callbacks = messageCallbacks.get(event);
            for (callback in callbacks) {
                try {
                    callback(data);
                } catch (e: Dynamic) {
                    trace('Error in $event callback: ${Std.string(e)}');
                }
            }
        }
    }
}


/**
 * Example usage of the integration in game code.
 */
class ExampleGameIntegration {
    
    public static function main(): Void {
        // Initialize the integration
        var integration = new DiceyDungeonsGameIntegration(
            "PlayerName",
            "MySeedName"
        );
        
        // Register callbacks for events
        integration.registerCallback("items_received", function(items: Array<ArchipelagoItem>) {
            for (item in items) {
                trace('Item received: ${item.name}');
                // Update game state here
            }
        });
        
        integration.registerCallback("connected", function(data: Dynamic) {
            trace("Connected to Archipelago!");
        });
        
        // Connect to the proxy
        integration.connect(
            "ws://localhost:11312/",
            function() {
                trace("Connected to Archipelago!");
                
                // Request all items for this player (no filters)
                integration.getItems(
                    null,  // no filters - get all items
                    function(response: Dynamic) {
                        trace('Got all items: total=${response.total_items}, matching=${response.total_matching}');
                        
                        // Items are organized by location type:
                        // response.chest_items, response.shop_items, response.heal_items, etc.
                        if (Reflect.hasField(response, "chest_items")) {
                            var chestItems: Array<ArchipelagoItem> = Reflect.field(response, "chest_items");
                            trace('  - Chest items: ${chestItems.length}');
                        }
                        if (Reflect.hasField(response, "shop_items")) {
                            var shopItems: Array<ArchipelagoItem> = Reflect.field(response, "shop_items");
                            trace('  - Shop items: ${shopItems.length}');
                        }
                        
                        // Now simulate some game events
                        simulateGameEvents(integration);
                    },
                    function(error: String) {
                        trace('Error getting items: $error');
                    }
                );
            },
            function(error: String) {
                trace('Connection error: $error');
            }
        );
    }
    
    /**
     * Simulate game events like location checks.
     */
    private static function simulateGameEvents(integration: DiceyDungeonsGameIntegration): Void {
        #if sys
        Sys.sleep(2);
        #end
        
        // Player completes level, check location
        integration.checkLocation(11101);
        trace("Location 11101 checked!");
        
        #if sys
        Sys.sleep(2);
        #end
        
        // Player defeats a boss
        integration.checkLocation(12101);
        trace("Location 12101 checked!");
        
        // Request items for a specific episode (Episode 1 only)
        var episodeFilter = {
            episode: 1
        };
        
        integration.getItems(
            episodeFilter,
            function(response: Dynamic) {
                trace('Got Episode 1 items: total=${response.total_items}, matching=${response.total_matching}');
                
                // Can also request by location type
                simulateLocationTypeRequest(integration);
            },
            function(error: String) {
                trace('Error getting episode items: $error');
            }
        );
    }
    
    /**
     * Example of requesting items by location type.
     */
    private static function simulateLocationTypeRequest(integration: DiceyDungeonsGameIntegration): Void {
        #if sys
        Sys.sleep(2);
        #end
        
        // Get only shop items
        var shopFilter = {
            location_type: "shop"
        };
        
        integration.getItems(
            shopFilter,
            function(response: Dynamic) {
                trace('Got shop items: total=${response.total_items}, matching=${response.total_matching}');
                
                if (Reflect.hasField(response, "shop_items")) {
                    var shopItems: Array<ArchipelagoItem> = Reflect.field(response, "shop_items");
                    for (item in shopItems) {
                        trace('  - ${item.name}');
                    }
                }
                
                #if sys
                Sys.sleep(2);
                #end
                integration.disconnect();
            },
            function(error: String) {
                trace('Error getting shop items: $error');
            }
        );
    }
}

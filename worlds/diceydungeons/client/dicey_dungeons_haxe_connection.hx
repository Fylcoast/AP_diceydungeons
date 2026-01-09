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
trace("attempting connection to client!");
var integration = new DiceyDungeonsGameIntegration(args[0], args[1]);
integration.connect(
    "ws://localhost:11312/",
    function() {
        trace("Connected!");
    },
    function(error: String) {
        trace("Connection failed: " + error);
    }
);

return integration;
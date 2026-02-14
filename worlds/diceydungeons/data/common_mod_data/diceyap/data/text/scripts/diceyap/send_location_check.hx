var hp = args[0];
var location_id = args[1];

if (hp > 0) {
    trace("[AP] {\"command\": \"send_item\", \"payload\": \"" + location_id + "\"}");
}
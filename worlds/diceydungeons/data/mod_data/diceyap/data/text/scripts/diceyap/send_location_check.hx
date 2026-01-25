var hp = args[0];
var location_id = args[1];
trace("AP hp: " + hp + " and location: " + location_id);
if (hp > 0) {
    trace("[AP] {\"command\": \"send_item\", \"payload\": \"" + location_id + "\"}");
}
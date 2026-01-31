// Loop through equipment and send any we picked up!
//trace("[AP] {\"command\": \"send_equipment_debug\", \"payload\": \"" + self.equipment + "\"}");
var equipment = self.equipment;
var items_to_remove = [];

for (item in equipment) {
  //trace("Item: " + item + ", isnull: " + (item == null));
  if (item == null) {
    continue;
  }
  var itemString = item.toString();
  //trace("Item length: " + itemString.length);
  //trace("Index of [AP]: " + itemString.indexOf("[AP]"));
  if (itemString.indexOf("[AP]") >= 0) {
    //trace("Attempting to send item: " + itemString);
    var location_id = itemString.split("[AP]")[1];
    trace("[AP] {\"command\": \"send_item\", \"payload\": \"" + location_id + "\"}");
    //self.equipment.remove(item);
    items_to_remove.push(item);
  }
}

for (item in items_to_remove) {
  self.equipment.remove(item);
}
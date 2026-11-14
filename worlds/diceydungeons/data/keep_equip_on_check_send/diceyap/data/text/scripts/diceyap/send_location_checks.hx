// Loop through equipment and send any we picked up!
//var equipment = self.equipment;
// Use getbackpackcontents instead of self.equipment so we can send from backpack! This may not correctly remove... but i mean...
var equipment = getbackpackcontents(true);

for (item in equipment) {
  if (item == null) {
    continue;
  }
  var itemString = item.toString();
  if (itemString.indexOf("[AP]") >= 0) {
    var location_id = itemString.split("[AP]")[1];
    trace("[AP] {\"command\": \"send_item\", \"payload\": \"" + location_id + "\"}");
  }
}

if (self.layout == self.layout.SPELLBOOK) {
  var spell_slot = 1;
  while (spell_slot < 7) {
    var item = Spellbook.spellname(spell_slot);
    if (item == null) {
      continue;
    }
    var itemString = item.toString();
    if (itemString.indexOf("[AP]") >= 0) {
      var location_id = itemString.split("[AP]")[1];
      trace("[AP] {\"command\": \"send_item\", \"payload\": \"" + location_id + "\"}");
    }
    spell_slot = spell_slot + 1;
  }
}
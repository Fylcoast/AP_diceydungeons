var generator = "warrior_two";
var episode = "2";

usestandardenemies(false);

level1enemies = level6enemies;

var items = [];
var gooditems = [];
var otherstuff = [];
var goodotherstuff = [];

//Boss:
items = runscript("diceyap/load_ap_items_by_category", [generator, episode, "chests", "1", "1"]);
gooditems = [];
otherstuff = [];
goodotherstuff = [];

var lastfloor = addfloor("boss");

// if (getfinalboss() == "Drake"){
//   items.push(vampireitem.pop());
// }

lastfloor
  .addenemies([], ["Frog [AP]"])
  .additems(items, gooditems)
  .setlocation('BOSS')
  .addotherstuff(otherstuff, goodotherstuff)
  .generate();
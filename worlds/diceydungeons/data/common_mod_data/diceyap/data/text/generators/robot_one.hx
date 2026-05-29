usestandardenemies();

var generator = "robot_one";
var episode = "1";
var items = [];
var gooditems = [];
var otherstuff = [];
var goodotherstuff = [];

//Floor 1:
items = [];
gooditems = runscript("diceyap/load_ap_items_by_category", [generator, episode, "chests", "1", "1"]);
otherstuff = [];
goodotherstuff = [];

addfloor("tiny")
  .additems(items, gooditems)
  .addotherstuff(otherstuff, goodotherstuff)
  .generate();
  
//Floor 2:

items = [];

gooditems = runscript("diceyap/load_ap_items_by_category", [generator, episode, "chests", "2", "1"]);
otherstuff = [health(), health()];
goodotherstuff = [
  shop(runscript("diceyap/load_ap_items_by_category", [generator, episode, "shops", "2", "1"]))
];

addfloor("normal")
  .additems(items, gooditems)
  .addotherstuff(otherstuff, goodotherstuff)
  .generate();
  
//Floor 3:

items = runscript("diceyap/load_ap_items_by_category", [generator, episode, "chests", "3", "1"]);
gooditems = [];

otherstuff = [
  health(), 
  health()
];
goodotherstuff = [
  shop(runscript("diceyap/load_ap_items_by_category", [generator, episode, "shops", "3", "1"])), 
  upgrade()
];

addfloor("normal")
  .additems(items, gooditems)
  .addotherstuff(otherstuff, goodotherstuff)
  .generate();
  
//Floor 4:
items = [];
gooditems = runscript("diceyap/load_ap_items_by_category", [generator, episode, "chests", "4", "1"]);

otherstuff = [health(), health()];
goodotherstuff = [
  trade(["any"],runscript("diceyap/load_ap_items_by_category", [generator, episode, "trades", "4", "1"]))
];

addfloor("normal")
  .additems(items, gooditems)
  .addotherstuff(otherstuff, goodotherstuff)
  .generate();
  
//Floor 5:
items = [];
gooditems = runscript("diceyap/load_ap_items_by_category", [generator, episode, "chests", "5", "1"]);

otherstuff = [health(), health()];
goodotherstuff = [
  shop(runscript("diceyap/load_ap_items_by_category", [generator, episode, "shops", "5", "1"])), 
  upgrade()
];

addfloor("big")
  .additems(items, gooditems)
  .addotherstuff(otherstuff, goodotherstuff)
  .generate();
  
//Floor 6:
items = [];
gooditems = [];
otherstuff = [];
goodotherstuff = [];

var lastfloor = addfloor("boss");

if (getfinalboss() == "Drake"){
  items.push("Wooden Stake");
}

lastfloor
  .additems(items, gooditems)
  .setlocation('BOSS')
  .addotherstuff(otherstuff, goodotherstuff)
  .generate();
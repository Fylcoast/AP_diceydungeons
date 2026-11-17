usestandardenemies();

var generator = "jester_one";
var episode = "1";
var items = [];
var gooditems = [];
var otherstuff = [];
var goodotherstuff = [];

//Floor 1:
addfloor("tiny")
  .additems(runscript("diceyap/load_ap_items_by_category", [generator, episode, "chests", "1", "1"]), [])
  .generate();
  
//Floor 2:
items = runscript("diceyap/load_ap_items_by_category", [generator, episode, "chests", "2", "1"]);
gooditems = [];
otherstuff = [
  health(), 
  health()
];
goodotherstuff = [
  shop(runscript("diceyap/load_ap_items_by_category", [generator, episode, "shops", "2", "1"])), //substituted elsewhere
  upgrade()
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
  shop(runscript("diceyap/load_ap_items_by_category", [generator, episode, "shops", "3", "1"]))
];

addfloor("normal")
  .additems(items, gooditems)
  .addotherstuff(otherstuff, goodotherstuff)
  .generate();

//Floor 4
items = [];
gooditems = runscript("diceyap/load_ap_items_by_category", [generator, episode, "chests", "4", "1"]); //substituted elsewhere

otherstuff = [
  health(), 
  upgrade()
];
goodotherstuff = [
  shop(runscript("diceyap/load_ap_items_by_category", [generator, episode, "shops", "4", "1"])),
  copyshop()
];

addfloor("big")
  .additems(items, gooditems)
  .addotherstuff(otherstuff, goodotherstuff)
  .generate();
  
//Floor 5
items = [];
gooditems = [];
otherstuff = [health(), health(), health()];
goodotherstuff = [rand([upgrade(), copyshop()])];

addfloor("normal")
  .additems(items, gooditems)
  .addotherstuff(otherstuff, goodotherstuff)
  .generate();

// Floor 6:			
items = [];
gooditems = [];
otherstuff = [];
goodotherstuff = [];

usestandardenemies(false);
var finalboss:String = level6enemies.pop();
if (finalboss == "Drake"){
  items.push("Wooden Stake,Wooden Stake");
}

addfloor("boss")
  .addenemies([], [finalboss])
  .setlocation('BOSS')
  .additems(items, gooditems)
  .addotherstuff(otherstuff, goodotherstuff)
  .generate();
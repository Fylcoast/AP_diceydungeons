/*
var thisgenerator = "warrior_normal";
var chests = [];
var shops = [];
var heals = [];
var upgrades = [];
var trades = [];
var itempools = [chests, shops, heals, upgrades, trades]; //Initialize lists like this for clarity
*/
/*NOTICE TO MODDERS:
  All you need to do to get your items in here is append the name of your mod to:
    diceydungeons/itempools/[this generator's name minus file extension]/scriptstorun.txt
  Then add a .hx script of the appropriate name to that directory that returns an array containing arrays of items
  you want to add to each of the generator's item pools. Use the vanilla script for this generator for reference -
  it's important you return the right amount of arrays!
  
  (If you want to replace the generator entirely, in case you have an extremely specific item pool in mind, you should
  get rid of declaring itempools and add items directly to the above lists (or replace pops from them with strings).
  Note however that other mods will no longer be able to add items here.)*/
/*
itempools = runscript("diceyap/load_ap_items", ["warrior_ap", 3]);

var chests = itempools[0];
var shops = itempools[1];
var heals = itempools[2];
var upgrades = itempools[3];
var trades = itempools[4];
*/


usestandardenemies();

var generator = "warrior_three";
var episode = "3";
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
otherstuff = [health()];
goodotherstuff = [shop(runscript("diceyap/load_ap_items_by_category", [generator, episode, "shops", "2", "1"]))];

addfloor("small")
  .additems(items, gooditems)
  .addotherstuff(otherstuff, goodotherstuff)
  .generate();

//Floor 3:
items = runscript("diceyap/load_ap_items_by_category", [generator, episode, "chests", "3", "1"]);
gooditems = [];

otherstuff = [health(), health()];

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

otherstuff = [health()];
goodotherstuff = [
  trade(["any"], ["Dice Shard"])
];

addfloor("normal")
  .additems(items, gooditems)
  .addotherstuff(otherstuff, goodotherstuff)
  .generate();
  
//Floor 5:
items = runscript("diceyap/load_ap_items_by_category", [generator, episode, "chests", "5", "1"]);
gooditems = [];

otherstuff = [health(), health()];
goodotherstuff = [
  upgrade(),
  shop(runscript("diceyap/load_ap_items_by_category", [generator, episode, "shops", "5", "1"]), runscript("diceyap/load_ap_items_by_category", [generator, episode, "shops", "5", "2"]))
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
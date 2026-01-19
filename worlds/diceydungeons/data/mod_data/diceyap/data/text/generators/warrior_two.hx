var thisgenerator = "warrior_normal";
var warriorshops = [];
var strangeshop = [];
var awesomelist = [];
var floor2gooditem = [];
var floor3item = [];
var floor5item = [];
var vampireitem = [];
var itempools = [warriorshops, strangeshop, awesomelist, floor2gooditem, floor3item, floor5item, vampireitem]; //Initialize lists like this for clarity

/*NOTICE TO MODDERS:
  All you need to do to get your items in here is append the name of your mod to:
    diceydungeons/itempools/[this generator's name minus file extension]/scriptstorun.txt
  Then add a .hx script of the appropriate name to that directory that returns an array containing arrays of items
  you want to add to each of the generator's item pools. Use the vanilla script for this generator for reference -
  it's important you return the right amount of arrays!
  
  (If you want to replace the generator entirely, in case you have an extremely specific item pool in mind, you should
  get rid of declaring itempools and add items directly to the above lists (or replace pops from them with strings).
  Note however that other mods will no longer be able to add items here.)*/
  
itempools = runscript("diceydungeons/flexible_generator",[thisgenerator,itempools]);

// Attempt AP connection.
runscript("diceyap/client_connect", ["Dicey", ""]);

var warriorshops = itempools[0];
var strangeshop = itempools[1];
var awesomelist = itempools[2];
var floor2gooditem = itempools[3];
var floor3item = itempools[4];
var floor5item = itempools[5];
var vampireitem = itempools[6];

usestandardenemies(false);

level1enemies = level6enemies;

var items = [];
var gooditems = [];
var otherstuff = [];
var goodotherstuff = [];

//Boss:
items = ["Kingdom Hearts Item 1"];
gooditems = [];
otherstuff = [];
goodotherstuff = [];

var lastfloor = addfloor("boss");

// if (getfinalboss() == "Drake"){
//   items.push(vampireitem.pop());
// }

lastfloor
  .addenemies([], ["Frog"])
  .additems(items, gooditems)
  .setlocation('BOSS')
  .addotherstuff(otherstuff, goodotherstuff)
  .generate();
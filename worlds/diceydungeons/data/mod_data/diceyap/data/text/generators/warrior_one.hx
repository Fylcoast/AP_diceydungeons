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

var warriorshops = itempools[0];
var strangeshop = itempools[1];
var awesomelist = itempools[2];
var floor2gooditem = itempools[3];
var floor3item = itempools[4];
var floor5item = itempools[5];
var vampireitem = itempools[6];



usestandardenemies();

var items = [];
var gooditems = [];
var otherstuff = [];
var goodotherstuff = [];

//Floor 1:
items = [];
gooditems = ["Kingdom Hearts Item 1"];
otherstuff = [];
goodotherstuff = [shop(["upgrade", "health"])];

addfloor("tiny")
  .additems(items, gooditems)
  .addotherstuff(otherstuff, goodotherstuff)
  .generate();

//Floor 2:
items = [];
gooditems = [floor2gooditem.pop()];
otherstuff = [health()];
goodotherstuff = [shop([warriorshops.pop(), warriorshops.pop(), warriorshops.pop()])];

addfloor("small")
  .additems(items, gooditems)
  .addotherstuff(otherstuff, goodotherstuff)
  .generate();

//Floor 3:
items = [];
items.push(floor3item.pop());
gooditems = [];

otherstuff = [health(), health()];

goodotherstuff = [
  shop([warriorshops.pop(), warriorshops.pop(), warriorshops.pop()]),
  upgrade()
];

addfloor("normal")
  .additems(items, gooditems)
  .addotherstuff(otherstuff, goodotherstuff)
  .generate();
  
//Floor 4:
items = [];
gooditems = [awesomelist.pop()];

otherstuff = [health()];
goodotherstuff = [
  trade(["any"], [awesomelist.pop()])
];

addfloor("normal")
  .additems(items, gooditems)
  .addotherstuff(otherstuff, goodotherstuff)
  .generate();
  
//Floor 5:
items = [];
items.push(floor5item.pop());
gooditems = [];

otherstuff = [health(), health()];
goodotherstuff = [
  upgrade(),
  shop(["upgrade", strangeshop.pop(), "health"], [4, 4, 4])
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
  items.push(vampireitem.pop());
}

lastfloor
  .additems(items, gooditems)
  .setlocation('BOSS')
  .addotherstuff(otherstuff, goodotherstuff)
  .generate();
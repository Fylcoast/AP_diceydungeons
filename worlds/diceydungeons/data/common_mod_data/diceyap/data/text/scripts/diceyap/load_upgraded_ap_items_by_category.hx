// Incoming argument holds the item parameters we want.
var gen = args[0];
var episode = args[1];
var list = args[2];
var floor = args[3];
var iter = args[4]; // number of the thing that is on the floor

// AP data saved in columns name, generator, list 
var apdata = loaddata("diceyap/ap_data");

var res = [];

//trace("Intended args: " + args);

for (item in apdata) {
  if (item.generator == gen && item.episode == episode && item.list == list && (!floor || !item.floor || item.floor == floor) && (!iter || !item.iter || item.iter == iter)) {
    res.push(item.name+"+");
  }
}

return res;
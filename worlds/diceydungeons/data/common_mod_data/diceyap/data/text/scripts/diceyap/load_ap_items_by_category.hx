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
    //trace("Adding item!: " + item.name + " at " + args);
    var itemString = item.name;
    // STRAP IN. HARDCODING ALERT.
    if (itemString == "Battle Axe[APcomma]Nudge") {
      itemString = "Battle Axe,Nudge";
    }
    if (itemString == "Bumpblade[APcomma]Spatula") {
      itemString = "Bumpblade,Spatula";
    }
    if (itemString == "Chocolate Cookie[APcomma]Spatula") {
      itemString = "Chocolate Cookie,Spatula";
    }
    if (itemString == "Claw[APcomma]Claw") {
      itemString = "Claw,Claw";
    }
    if (itemString == "Hammer[APcomma]Bump") {
      itemString = "Hammer,Bump";
    }
    if (itemString == "Short Sword[APcomma]Short Sword") {
      itemString = "Short Sword,Short Sword";
    }
    if (itemString == "Staff[APcomma]Juggling Ball") {
      itemString = "Staff,Juggling Ball";
    }
    if (itemString == "Tazer[APcomma]Bump") {
      itemString = "Tazer,Bump";
    }
    if (itemString == "Toxic Ooze[APcomma]Slime Ball") {
      itemString = "Toxic Ooze,Slime Ball";
    }
    if (itemString == "Venus Fly Trap[APcomma]Bump") {
      itemString = "Venus Fly Trap,Bump";
    }
    if (itemString == "Whip[APcomma]Bump") {
      itemString = "Whip,Bump";
    }
    if (itemString == "Wooden Shield[APcomma]Spare 4") {
      itemString = "Wooden Shield,Spare 4";
    }
    if (itemString == "Boosterpack:Ice Shatter[APcomma]Snowflake[APcomma]Snowflake") {
      itemString = "Boosterpack:Ice Shatter,Snowflake,Snowflake";
    }
    if (itemString == "Boosterpack:Detonator[APcomma]Liquorice[APcomma]Liquorice") {
      itemString = "Boosterpack:Detonator,Liquorice,Liquorice";
    }
    if (itemString == "Boosterpack:Flame Blast[APcomma]Spark[APcomma]Spark") {
      itemString = "Boosterpack:Flame Blast,Spark,Spark";
    }
    if (itemString == "Boosterpack:High Voltage[APcomma]Buzzer[APcomma]Buzzer") {
      itemString = "Boosterpack:High Voltage,Buzzer,Buzzer";
    }
    if (itemString == "Boosterpack:Hijinx[APcomma]Slapsies[APcomma]Slapsies") {
      itemString = "Boosterpack:Hijinx,Slapsies,Slapsies";
    }
    if (itemString == "Boosterpack:Woof Woof Woof[APcomma]Ruff Ruff Ruff[APcomma]Ruff Ruff Ruff") {
      itemString = "Boosterpack:Woof Woof Woof,Ruff Ruff Ruff,Ruff Ruff Ruff";
    }
    if (itemString == "Boosterpack:Flying Skull[APcomma]Evil Laugh[APcomma]Evil Laugh") {
      itemString = "Boosterpack:Flying Skull,Evil Laugh,Evil Laugh";
    }
    if (itemString == "Boosterpack:Shield Bash[APcomma]Deflect[APcomma]Deflect") {
      itemString = "Boosterpack:Shield Bash,Deflect,Deflect";
    }
    res.push(itemString);
  }
}

return res;
var generator = args[0];
var episode = args[1];
//trace(runscript("diceyap/load_ap_items_by_category", [generator, episode, "levels", "", "2"]));
//trace(runscript("diceyap/load_ap_items_by_category", [generator, episode, "levels", "", "2"])[0]);
self.setvar("levelreward2", "[Equipment:Bump]");
self.setvar("levelreward3", "[Equipment:Bump]");
self.setvar("levelreward4", "[Equipment:Bump]");
self.setvar("levelreward5", "[Equipment:Bump]");
self.setvar("levelreward6", "[Equipment:Bump]");

//self.setvar("levelreward2", "Equipment:" + runscript("diceyap/load_ap_items_by_category", [generator, episode, "levels", "", "2"])[0]);
// self.setvar("levelreward3", runscript("diceyap/load_ap_items_by_category", [generator, episode, "levels", "", "3"]));
// self.setvar("levelreward4", runscript("diceyap/load_ap_items_by_category", [generator, episode, "levels", "", "4"]));
// self.setvar("levelreward5", runscript("diceyap/load_ap_items_by_category", [generator, episode, "levels", "", "5"]));
// self.setvar("levelreward6", runscript("diceyap/load_ap_items_by_category", [generator, episode, "levels", "", "6"]));
trace("levelreward2: " + self.getvar("levelreward2"));
trace("[AP] {\"command\": \"reload_generator\"}");
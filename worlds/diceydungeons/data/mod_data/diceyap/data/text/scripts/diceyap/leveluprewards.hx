var generator = args[0];
var episode = args[1];
var reward;
// leveluprewards(2, "", runscript("diceyap/load_ap_items_by_category", [generator, episode, "levels", "", "2"]));
// leveluprewards(3, "", runscript("diceyap/load_ap_items_by_category", [generator, episode, "levels", "", "3"]));
// leveluprewards(4, "", runscript("diceyap/load_ap_items_by_category", [generator, episode, "levels", "", "4"]));
// leveluprewards(5, "", runscript("diceyap/load_ap_items_by_category", [generator, episode, "levels", "", "5"]));
// leveluprewards(6, "", runscript("diceyap/load_ap_items_by_category", [generator, episode, "levels", "", "6"]));

// Annoying workarounds to make it look nice.
reward = runscript("diceyap/load_ap_items_by_category", [generator, episode, "levels", "", "2"]);
if (reward.length == 1 && reward.indexOf("Dice") >= 0) {
    leveluprewards(2, reward[0]);
} else {
    leveluprewards(2, "", reward);
}

reward = runscript("diceyap/load_ap_items_by_category", [generator, episode, "levels", "", "3"]);
if (reward.length == 1 && reward.indexOf("Dice") >= 0) {
    leveluprewards(3, reward[0]);
} else {
    leveluprewards(3, "", reward);
}

reward = runscript("diceyap/load_ap_items_by_category", [generator, episode, "levels", "", "4"]);
if (reward.length == 1 && reward.indexOf("Dice") >= 0) {
    leveluprewards(4, reward[0]);
} else {
    leveluprewards(4, "", reward);
}

reward = runscript("diceyap/load_ap_items_by_category", [generator, episode, "levels", "", "5"]);
if (reward.length == 1 && reward.indexOf("Dice") >= 0) {
    leveluprewards(5, reward[0]);
} else {
    leveluprewards(5, "", reward);
}

reward = runscript("diceyap/load_ap_items_by_category", [generator, episode, "levels", "", "6"]);
if (reward.length == 1 && reward.indexOf("Dice") >= 0) {
    leveluprewards(6, reward[0]);
} else {
    leveluprewards(6, "", reward);
}

trace("[AP] {\"command\": \"reload_generator\"}");
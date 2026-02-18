from collections.abc import Mapping
from typing import Any

from worlds.AutoWorld import World

from . import items, locations, regions, rules, web_world
from . import options as diceydungeons_options

class DiceyDungeonsWorld(World):
    """
    Dicey Dungeons is a roguelike deck-building game where players navigate through dungeons using dice rolls to defeat enemies.
    """

    game = "Dicey Dungeons"

    web = web_world.DiceyDungeonsWebWorld()

    options_dataclass = diceydungeons_options.DiceyDungeonsOptions
    options: diceydungeons_options.DiceyDungeonsOptions

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID
    item_name_groups = items.item_name_groups

    origin_region_name = regions.STARTING_REGION_NAME

    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)

    def set_rules(self) -> None:
        rules.set_all_rules(self)

    def create_items(self) -> None:
        items.create_all_items(self)

    def create_item(self, name: str) -> items.DiceyDungeonsItem:
        return items.create_item_with_correct_classification(self, name)
    
    def get_filler_item_name(self) -> str:
        return items.get_filler_item_name(self)
    
    def fill_slot_data(self) -> Mapping[str, Any]:
        ret = self.options.as_dict(
            "levelsanity", "checks_per_chest", "checks_per_shop", "checks_per_trade", "episode_progression", "floor_5_shop_selection", "skip_cutscenes"
        )
        
        # Generate token for save file
        save_name = "diceyap_" + str(self.random.random())
        ret["save_name"] = save_name

        return ret

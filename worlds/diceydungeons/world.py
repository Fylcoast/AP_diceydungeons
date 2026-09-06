from collections.abc import Mapping
from typing import Any, ClassVar

from worlds.AutoWorld import World

from . import items, locations, regions, rules, web_world
from . import options as diceydungeons_options
from . import settings as diceydungeons_settings

class DiceyDungeonsWorld(World):
    """
    Dicey Dungeons is a roguelike deck-building game where players navigate through dungeons using dice rolls to defeat enemies.
    """

    game = "Dicey Dungeons"

    settings_key = "diceydungeons_options"
    settings: ClassVar[diceydungeons_settings.DiceyDungeonsSettings]

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
        return items.get_random_filler_item_name(self)
    
    def fill_slot_data(self) -> Mapping[str, Any]:
        ret = self.options.as_dict(
            "levelsanity", 
            "checks_per_chest", 
            "checks_per_shop", 
            "checks_per_trade", 
            "split_dice", 
            "dice_shards_per_die", 
            "spare_dice_shards", 
            "episode_progression", 
            "shop_selection", 
            "skip_cutscenes", 
            "equipment_availability",
            "warrior_2_disable_curse",
            "warrior_3_remove_hp_decrease_on_level",
            "inventor_3_remove_rust",
            "upgrade_equipment",
            "release_episodes_when_completed",
            "character",
            "excluded_equipment",
            "randomize_gadgets",
            "remove_checks_when_sent",
            "use_equipment_from_any_character"
        )
        
        # Generate token for save file
        save_name = "diceyap_" + str(self.random.random())
        ret["save_name"] = save_name

        return ret

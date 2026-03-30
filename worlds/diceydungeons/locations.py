from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import ItemClassification, Location

from . import items
from .data.game_data import * # *_items lists
from .data.episode_data import * # episode location objects
from .data.globals import *

from .options import MAXIMUM_CHECKS_PER_CHEST, MAXIMUM_CHECKS_PER_SHOP, MAXIMUM_CHECKS_PER_TRADE

if TYPE_CHECKING:
    from .world import DiceyDungeonsWorld

LOCATION_NAME_TO_ID: dict[str, int] = {}

# Current Location ID blocks taken:
# 911-966: Episode completion
# 1112-1666: Level ups
# 111101-665599: pickups for all characters

for character_code, character in CHARACTER_CODE_TO_NAME.items():
    for episode in range(1, 7):
        # Level up locations convention:
        # Location name: <Character> - Ep. <Episode> - Level <level>
        # ID: 1<Character Code><Episode Number><Level Number>
            # "Warrior - Ep. 1 - Level 2": 1112,
            # "Warrior - Ep. 2 - Level 3": 1123,
            # "Thief - Ep. 6 - Level 6": 1266
            # etc
        for level in range(2, 7):
            LOCATION_NAME_TO_ID[character + " - Ep. " + str(episode) + " - Level " + str(level)] = 1000 + 100 * character_code + 10 * episode + level
        
        # Episode completion convention:
        # Location name: <Character> - Episode <Episode> Completed
        # ID: 9<Character Code><Episode>
        LOCATION_NAME_TO_ID[character + " - Episode " + str(episode) + " Completed"] = 900 + 10 * character_code + episode


# Physical locations convention:
# Location name: <Character> - Ep. # Fl. # - <Location Type> <Number>
# ID: <Character Code><Episode Number><Floor Number><Location Code><Location Count, 2 digits>
# Character code:
#   1: Warrior
#   2: Thief
# Episode code is 1-6
# Floor code is 1-6
# Location code:
#   1: Chest
#   2: Shop
#   3: Heals
#   4: Upgrades
#   5: Trades
# "Warrior - Ep. 1 Fl. 1 - Chest 1": 111101,
# "Warrior - Ep. 1 Fl. 2 - Chest 2": 112102,
# "Thief - Ep. 2 Fl. 3 - Shop 1": 223201,
# etc
for character_num, character_episodes in enumerate(all_character_episodes, 1):
    for episode_num, episode in enumerate(character_episodes, 1):
        for floor_num, floor in enumerate(episode.floors, 1):
            episode_floor_str = CHARACTER_CODE_TO_NAME[character_num] + " - Ep. " + str(episode_num) + " Fl. " + str(floor_num)
            # Chests
            for chest in range(1, floor.num_chests * MAXIMUM_CHECKS_PER_CHEST + 1):
                LOCATION_NAME_TO_ID[episode_floor_str + " - Chest " + str(chest)] = 100000 * character_num + 10000 * episode_num + 1000 * floor_num + 100 + chest
            # Shops
            for shop in range(1, floor.num_shops * MAXIMUM_CHECKS_PER_SHOP + 1):
                LOCATION_NAME_TO_ID[episode_floor_str + " - Shop " + str(shop)] = 100000 * character_num + 10000 * episode_num + 1000 * floor_num + 200 + shop
            # Heals
            for heal in range(1, floor.num_heals + 1):
                LOCATION_NAME_TO_ID[episode_floor_str + " - Heal " + str(heal)] = 100000 * character_num + 10000 * episode_num + 1000 * floor_num + 300 + heal
            # Upgrades
            for upgrade in range(1, floor.num_upgrades + 1):
                LOCATION_NAME_TO_ID[episode_floor_str + " - Upgrade " + str(upgrade)] = 100000 * character_num + 10000 * episode_num + 1000 * floor_num + 400 + upgrade
            # Trades
            for trade in range(1, floor.num_trades * MAXIMUM_CHECKS_PER_TRADE + 1):
                LOCATION_NAME_TO_ID[episode_floor_str + " - Trade " + str(trade)] = 100000 * character_num + 10000 * episode_num + 1000 * floor_num + 500 + trade

class DiceyDungeonsLocation(Location):
    game: str = "Dicey Dungeons"

def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {name: LOCATION_NAME_TO_ID[name] for name in location_names}

def create_all_locations(world: DiceyDungeonsWorld) -> None:
    create_regular_locations(world)
    create_events(world)

def create_regular_locations(world: DiceyDungeonsWorld) -> None:

    # Populate episode locations based on character choice
    episode_list = all_character_episodes[world.options.character]
    character = CHARACTER_CODE_TO_NAME[world.options.character + 1]
    for episode_num, episode in enumerate(episode_list, 1):
        for floor_num, floor in enumerate(episode.floors, 1):
            episode_floor_str = character + " - Ep. " + str(episode_num) + " Fl. " + str(floor_num)
            episode_floor_region = character + " - Episode " + str(episode_num) + " - Floor " + str(floor_num)
            region = world.get_region(episode_floor_region)
            locs = []
            # Chests
            for chest in range(1, floor.num_chests * world.options.checks_per_chest + 1):
                locs.append(episode_floor_str + " - Chest " + str(chest))
            # Shops
            for shop in range(1, floor.num_shops * world.options.checks_per_shop + 1):
                locs.append(episode_floor_str + " - Shop " + str(shop))
            # Trades
            for trade in range(1, floor.num_trades * world.options.checks_per_trade + 1):
                locs.append(episode_floor_str + " - Trade " + str(trade + 1))
            # Heals AND Upgrades to go here, someday
        
            region.add_locations(get_location_names_with_ids(locs), DiceyDungeonsLocation)


    # Populate episode completions
    for episode in range(1, 7):
        loc_name = character + " - Episode " + str(episode) + " Completed"
        region_name = character + " - Episode " + str(episode) + " - Floor 6"
        region = world.get_region(region_name)
        episode_completed = DiceyDungeonsLocation(world.player, loc_name, LOCATION_NAME_TO_ID[loc_name], region)
        region.locations.append(episode_completed)
        episode_item = items.DiceyDungeonsItem(loc_name, ItemClassification.progression, items.ITEM_NAME_TO_ID[loc_name], world.player)
        episode_completed.place_locked_item(episode_item)

    # Populate level locations if enabled
    if world.options.levelsanity:
        # Place level up locations in floor AFTER the level up is first available
        floor_required: dict[int, str] = {
            2: "Floor 2",
            3: "Floor 3",
            4: "Floor 4",
            5: "Floor 5",
            6: "Floor 6"
        }

        for episode in range(1, 7):
            for level in range(2, 7):
                loc_name = f"{character} - Ep. {episode} - Level {level}"
                region = world.get_region(character + " - Episode " + str(episode) + " - " + floor_required[level])
                level_location = DiceyDungeonsLocation(world.player, loc_name, LOCATION_NAME_TO_ID[loc_name], region)
                region.locations.append(level_location)




def create_events(world: DiceyDungeonsWorld) -> None:
    menu = world.get_region("Menu")

    # Add one event for beating all episodes
    menu.add_event("All episodes completed", "All episodes completed", location_type=DiceyDungeonsLocation, item_type=items.DiceyDungeonsItem, show_in_spoiler=False)

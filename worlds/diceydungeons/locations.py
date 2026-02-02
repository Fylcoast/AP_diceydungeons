from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import ItemClassification, Location

from . import items
from .data.game_data import * # *_items lists
from .data.episode_data import * # episode location objects

from .options import MAXIMUM_CHECKS_PER_CHEST, MAXIMUM_CHECKS_PER_SHOP

if TYPE_CHECKING:
    from .world import DiceyDungeonsWorld

LOCATION_NAME_TO_ID: dict[str, int] = {}

# Current Warrior location ID blocks taken:
# 991-996: Episode completion
# 1012-1066: Level ups
# 11101-65599: chests/shops

for episode in range(1, 7):
    # Level up locations convention:
    # Location name: <Episode> - Level <level>
    # ID: 10<Episode Number><Level Number>
        # "Episode 1 - Level 2": 1012,
        # "Episode 1 - Level 3": 1013,
        # "Episode 2 - Level 2": 1022
        # etc
    for level in range(2, 7):
        LOCATION_NAME_TO_ID["Episode " + str(episode) + " - Level " + str(level)] = 1000 + 10 * episode + level
    
    # Episode completion convention:
    # Location name: Episode <Episode> - Episode Completed
    # ID: 99<Episode>
    LOCATION_NAME_TO_ID["Episode " + str(episode) + " - Episode Completed"] = 990 + episode


# Physical locations convention:
# Location name: <Episode> - <Floor> - <Location Type> <Number>
# ID: <Episode Number><Floor Number><Location Code><Location Count, 2 digits>
# Episode code is 1-6
# Floor code is 1-6
# Location code:
#   1: Chest
#   2: Shop
#   3: Heals
#   4: Upgrades
#   5: Trades
# "Episode 1 - Floor 1 - Chest 1": 11101,
# "Episode 1 - Floor 1 - Chest 2": 11102,
# "Episode 1 - Floor 2 - Chest 1": 12101,
# "Episode 1 - Floor 2 - Shop 1": 12201,
# etc
for episode_num, episode in enumerate(warrior_episodes):
    for floor_num, floor in enumerate(episode.floors):
        episode_floor_str = "Episode " + str(episode_num + 1) + " - Floor " + str(floor_num + 1)
        # Chests
        for chest in range(floor.num_chests * MAXIMUM_CHECKS_PER_CHEST):
            LOCATION_NAME_TO_ID[episode_floor_str + " - Chest " + str(chest + 1)] = 10000 * (episode_num + 1) + 1000 * (floor_num + 1) + 100 + (chest + 1)
        # Shops
        for shop in range(floor.num_shops * floor.num_shop_slots * MAXIMUM_CHECKS_PER_SHOP):
            LOCATION_NAME_TO_ID[episode_floor_str + " - Shop " + str(shop + 1)] = 10000 * (episode_num + 1) + 1000 * (floor_num + 1) + 200 + (shop + 1)
        # Heals
        for heal in range(floor.num_heals):
            LOCATION_NAME_TO_ID[episode_floor_str + " - Heal " + str(heal + 1)] = 10000 * (episode_num + 1) + 1000 * (floor_num + 1) + 300 + (heal + 1)
        # Upgrades
        for upgrade in range(floor.num_upgrades):
            LOCATION_NAME_TO_ID[episode_floor_str + " - Upgrade " + str(upgrade + 1)] = 10000 * (episode_num + 1) + 1000 * (floor_num + 1) + 400 + (upgrade + 1)
        # Trades
        for trade in range(floor.num_trades):
            LOCATION_NAME_TO_ID[episode_floor_str + " - Trade " + str(trade + 1)] = 10000 * (episode_num + 1) + 1000 * (floor_num + 1) + 500 + (trade + 1)

class DiceyDungeonsLocation(Location):
    game: str = "Dicey Dungeons"

def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {name: LOCATION_NAME_TO_ID[name] for name in location_names}

def create_all_locations(world: DiceyDungeonsWorld) -> None:
    create_regular_locations(world)
    create_events(world)

def create_regular_locations(world: DiceyDungeonsWorld) -> None:
    # episode_one = world.get_region("Episode 1")
    # episode_two = world.get_region("Episode 2")
    # episode_three = world.get_region("Episode 3")
    # episode_four = world.get_region("Episode 4")
    # episode_five = world.get_region("Episode 5")
    # episode_six = world.get_region("Episode 6")
    # episode_regions = [episode_one, episode_two, episode_three, episode_four, episode_five, episode_six]

    # Populate episode locations
    for episode_num, episode in enumerate(warrior_episodes):
        # episode_locations = []
        for floor_num, floor in enumerate(episode.floors):
            episode_floor_str = "Episode " + str(episode_num + 1) + " - Floor " + str(floor_num + 1)
            region = world.get_region(episode_floor_str)
            locs = []
            # Chests
            for chest in range(floor.num_chests * world.options.checks_per_chest):
                locs.append(episode_floor_str + " - Chest " + str(chest + 1))
            # Shops
            for shop in range(floor.num_shops * world.options.checks_per_shop):
                locs.append(episode_floor_str + " - Shop " + str(shop + 1))
            # Heals, Upgrades, and Trades to go here, someday
        
            region.add_locations(get_location_names_with_ids(locs), DiceyDungeonsLocation)


    # Populate episode completions
    # menu = world.get_region("Menu")
    # completion_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Episode Completed" in item[0]])
    # menu.add_locations(completion_locations, DiceyDungeonsLocation)
    for episode in range(1, 7):
        loc_name = "Episode " + str(episode) + " - Episode Completed"
        region_name = "Episode " + str(episode) + " - Floor 6"
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
                # level_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Level" in item[0] and "Episode " + str(episode) in item[0]])
                loc_name = f"Episode {episode} - Level {level}"
                region = world.get_region("Episode " + str(episode) + " - " + floor_required[level])
                level_location = DiceyDungeonsLocation(world.player, loc_name, LOCATION_NAME_TO_ID[loc_name], region)
                region.locations.append(level_location)




def create_events(world: DiceyDungeonsWorld) -> None:
    menu = world.get_region("Menu")

    # Add one event for beating all episodes
    menu.add_event("All episodes completed", "All episodes completed", location_type=DiceyDungeonsLocation, item_type=items.DiceyDungeonsItem, show_in_spoiler=False)

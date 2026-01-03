from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import ItemClassification, Location

from . import items
from .data.extracted_data import * # *_items lists
from .data.episode_data import * # episode location objects

from .options import MAX_MAXIMUM_CHECKS_PER_CHEST, MAX_MAXIMUM_CHECKS_PER_SHOP

if TYPE_CHECKING:
    from .world import DiceyDungeonsWorld

# Need locations to match items. We have a good idea of what our items are, so
# we just match locations to fit.
# When more than just warrior, we will need to concat lists and determine unique items.
NEEDED_NUMBER_OF_LOCATIONS: int = len(warrior_items)

LOCATION_NAME_TO_ID: dict[str, int] = {}

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
        for chest in range(floor.num_chests * MAX_MAXIMUM_CHECKS_PER_CHEST):
            LOCATION_NAME_TO_ID[episode_floor_str + " - Chest " + str(chest + 1)] = 10000 * (episode_num + 1) + 1000 * (floor_num + 1) + 100 + (chest + 1)
        # Shops
        for shop in range(floor.num_shops * floor.num_shop_slots * MAX_MAXIMUM_CHECKS_PER_SHOP):
            LOCATION_NAME_TO_ID[episode_floor_str + " - Shop " + str(shop + 1)] = 10000 * (episode_num + 1) + 1000 * (floor_num + 1) + 200 + (shop + 1)
        # Heals - Not used yet but maybe someday
        for heal in range(floor.num_heals):
            LOCATION_NAME_TO_ID[episode_floor_str + " - Heal " + str(heal + 1)] = 10000 * (episode_num + 1) + 1000 * (floor_num + 1) + 300 + (heal + 1)
        # Upgrades - Not used yet but maybe someday
        for upgrade in range(floor.num_upgrades):
            LOCATION_NAME_TO_ID[episode_floor_str + " - Upgrade " + str(upgrade + 1)] = 10000 * (episode_num + 1) + 1000 * (floor_num + 1) + 400 + (upgrade + 1)
        # Trades - Not used yet but maybe someday
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
    episode_one = world.get_region("Episode 1")
    episode_two = world.get_region("Episode 2")
    episode_three = world.get_region("Episode 3")
    episode_four = world.get_region("Episode 4")
    episode_five = world.get_region("Episode 5")
    episode_six = world.get_region("Episode 6")
    episode_regions = [episode_one, episode_two, episode_three, episode_four, episode_five, episode_six]

    # Populate episode locations
    for episode_num, episode in enumerate(warrior_episodes):
        episode_locations = []
        for floor_num, floor in enumerate(episode.floors):
            episode_floor_str = "Episode " + str(episode_num + 1) + " - Floor " + str(floor_num + 1)
            # Chests
            for chest in range(floor.num_chests * world.options.maximum_checks_per_chest):
                episode_locations.append(episode_floor_str + " - Chest " + str(chest + 1))
            # Shops
            for shop in range(floor.num_shops * floor.num_shop_slots * world.options.maximum_checks_per_shop):
                episode_locations.append(episode_floor_str + " - Shop " + str(shop + 1))
            # # Heals - Not used yet but maybe someday
            # for heal in range(floor.num_heals):
            #     LOCATION_NAME_TO_ID["Episode " + episode_num + 1 + " - Floor " + floor_num + 1 + " - Heal " + heal + 1]
            # # Upgrades - Not used yet but maybe someday
            # for upgrade in range(floor.num_upgrades):
            #     LOCATION_NAME_TO_ID["Episode " + episode_num + 1 + " - Floor " + floor_num + 1 + " - Upgrade " + upgrade + 1]
            # # Trades - Not used yet but maybe someday
            # for trade in range(floor.num_trades):
            #     LOCATION_NAME_TO_ID["Episode " + episode_num + 1 + " - Floor " + floor_num + 1 + " - Trade " + trade + 1]
        
        episode_regions[episode_num].add_locations(get_location_names_with_ids(episode_locations), DiceyDungeonsLocation)


    
    # for location_name, location_id in LOCATION_NAME_TO_ID.items():
    #     location = DiceyDungeonsLocation(
    #         player=world.player,
    #         name=location_name,
    #         address=location_id,
    #     )
        # for episode in warrior_episodes:
        #     if episode.name in location_name:
        #         # Chests
        #         if "Chest" in location_name and location_id % 100 <= world.options.maximum_checks_per_chest
        #         # Shops
        # if "Episode 1" in location_name:
        #     episode_one.locations.append(location)
        # elif "Episode 2" in location_name:
        #     episode_two.locations.append(location)
        # elif "Episode 3" in location_name:
        #     episode_three.locations.append(location)
        # elif "Episode 4" in location_name:
        #     episode_four.locations.append(location)
        # elif "Episode 5" in location_name:
        #     episode_five.locations.append(location)
        # elif "Episode 6" in location_name:
        #     episode_six.locations.append(location)

    # episode_one_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Episode 1" in item[0]])
    # episode_one.add_locations(episode_one_locations, DiceyDungeonsLocation)

    # episode_two_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Episode 2" in item[0]])
    # episode_two.add_locations(episode_two_locations, DiceyDungeonsLocation)

    # episode_three_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Episode 3" in item[0]])
    # episode_three.add_locations(episode_three_locations, DiceyDungeonsLocation)

    # episode_four_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Episode 4" in item[0]])
    # episode_four.add_locations(episode_four_locations, DiceyDungeonsLocation)

    # episode_five_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Episode 5" in item[0]])
    # episode_five.add_locations(episode_five_locations, DiceyDungeonsLocation)

    # episode_six_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Episode 6" in item[0]])
    # episode_six.add_locations(episode_six_locations, DiceyDungeonsLocation)

    # Populate level locations if enabled
    if world.options.levelsanity:
        for episode in range(1, 7):
            level_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Level" in item[0] and "Episode " + str(episode) in item[0]])
            region = world.get_region("Episode " + str(episode))
            region.add_locations(level_locations, DiceyDungeonsLocation)




def create_events(world: DiceyDungeonsWorld) -> None:
    menu = world.get_region("Menu")
    episode_one = world.get_region("Episode 1")
    episode_two = world.get_region("Episode 2")
    episode_three = world.get_region("Episode 3")
    episode_four = world.get_region("Episode 4")
    episode_five = world.get_region("Episode 5")
    episode_six = world.get_region("Episode 6")

    episode_list = [
        episode_one,
        episode_two,
        episode_three,
        episode_four,
        episode_five,
        episode_six
    ]

    # Add one event for completing each episode
    for episode in episode_list:
        episode.add_event(
            episode.name + " - Episode Completed",
            episode.name + " - Episode Completed",
            location_type=DiceyDungeonsLocation,
            item_type=items.DiceyDungeonsItem,
        )

    # And finally one event for beating all episodes
    menu.add_event("All episodes completed", "All episodes completed", location_type=DiceyDungeonsLocation, item_type=items.DiceyDungeonsItem)

from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import ItemClassification, Location

from . import items
from .extracted_data import * # *_items lists

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
        LOCATION_NAME_TO_ID["Episode " + episode + " - Level " + level] = 1000 + 10 * episode + level


# Physical locations convention:
# Location name: <Episode> - <Floor> - <Location Type> <Number>
# ID: <Episode Number><Floor Number><Location Code><Location Count>
# Episode code is 1-6
# Floor code is 1-6
# Location code:
#   1: Chest
#   2: Shop
# "Episode 1 - Floor 1 - Chest 1": 1111,
# "Episode 1 - Floor 1 - Chest 2": 1112,
# "Episode 1 - Floor 2 - Chest 1": 1211,
# "Episode 1 - Floor 2 - Shop 1": 1221,
# etc
#TODO: Finish this, or script it out, or something
# May not be able to script? May be episode dependent, character dependent. Maybe find a way to extract?
# Or maybe we script anyway and randomizer / client decides if you get checks on a run or not? Examine generators to see if feasible.

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

    # Populate episode locations
    
    # for location_name in LOCATION_NAME_TO_ID.keys():
    #     location = DiceyDungeonsLocation(
    #         player=world.player,
    #         name=location_name,
    #         address=LOCATION_NAME_TO_ID[location_name],
    #     )
    #     if "Episode 1" in location_name:
    #         episode_one.locations.append(location)
    #     elif "Episode 2" in location_name:
    #         episode_two.locations.append(location)
    #     elif "Episode 3" in location_name:
    #         episode_three.locations.append(location)
    #     elif "Episode 4" in location_name:
    #         episode_four.locations.append(location)
    #     elif "Episode 5" in location_name:
    #         episode_five.locations.append(location)
    #     elif "Episode 6" in location_name:
    #         episode_six.locations.append(location)
    #     else:
    #         menu.locations.append(location)

    episode_one_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Episode 1" in item[0]])
    episode_one.add_locations(episode_one_locations, DiceyDungeonsLocation)

    episode_two_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Episode 2" in item[0]])
    episode_two.add_locations(episode_two_locations, DiceyDungeonsLocation)

    episode_three_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Episode 3" in item[0]])
    episode_three.add_locations(episode_three_locations, DiceyDungeonsLocation)

    episode_four_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Episode 4" in item[0]])
    episode_four.add_locations(episode_four_locations, DiceyDungeonsLocation)

    episode_five_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Episode 5" in item[0]])
    episode_five.add_locations(episode_five_locations, DiceyDungeonsLocation)

    episode_six_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Episode 6" in item[0]])
    episode_six.add_locations(episode_six_locations, DiceyDungeonsLocation)

    # Populate level locations if enabled
    if world.options.levelsanity:
        for episode in range(1, 7):
            level_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Level" in item[0] and "Episode " + episode in item[0]])
            region = world.get_region("Episode " + episode)
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

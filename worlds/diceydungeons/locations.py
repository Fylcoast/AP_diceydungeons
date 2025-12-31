from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import ItemClassification, Location

from . import items

if TYPE_CHECKING:
    from .world import DiceyDungeonsWorld

LOCATION_NAME_TO_ID: dict[str, int] = {
    # Convention:
    # Location name: <Episode> - <Floor> - <Location Type> <Number>
    # ID: <Episode Number><Floor Number><Location Code><Location Count>
    # Episode code is 1-6
    # Floor code is 1-6
    # Location code:
    #   1: Chest
    #   2: Shop
    "Episode One - Floor 1 - Chest 1": 1111,
    "Episode One - Floor 1 - Chest 2": 1112,
    "Episode One - Floor 2 - Chest 1": 1211,
    "Episode One - Floor 2 - Shop 1": 1221,
    # ... (additional locations would be defined here)
}

class DiceyDungeonsLocation(Location):
    game: str = "Dicey Dungeons"

def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {name: LOCATION_NAME_TO_ID[name] for name in location_names}

def create_all_locations(world: DiceyDungeonsWorld) -> None:
    create_regular_locations(world)
    create_events(world)

def create_regular_locations(world: DiceyDungeonsWorld) -> None:
    episode_one = world.get_region("Episode One")
    episode_two = world.get_region("Episode Two")
    episode_three = world.get_region("Episode Three")
    episode_four = world.get_region("Episode Four")
    episode_five = world.get_region("Episode Five")
    episode_six = world.get_region("Episode Six")

    # Populate episode locations
    
    # for location_name in LOCATION_NAME_TO_ID.keys():
    #     location = DiceyDungeonsLocation(
    #         player=world.player,
    #         name=location_name,
    #         address=LOCATION_NAME_TO_ID[location_name],
    #     )
    #     if "Episode One" in location_name:
    #         episode_one.locations.append(location)
    #     elif "Episode Two" in location_name:
    #         episode_two.locations.append(location)
    #     elif "Episode Three" in location_name:
    #         episode_three.locations.append(location)
    #     elif "Episode Four" in location_name:
    #         episode_four.locations.append(location)
    #     elif "Episode Five" in location_name:
    #         episode_five.locations.append(location)
    #     elif "Episode Six" in location_name:
    #         episode_six.locations.append(location)
    #     else:
    #         menu.locations.append(location)

    episode_one_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Episode One" in item[0]])
    episode_one.add_locations(episode_one_locations, DiceyDungeonsLocation)

    episode_two_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Episode Two" in item[0]])
    episode_two.add_locations(episode_two_locations, DiceyDungeonsLocation)

    episode_three_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Episode Three" in item[0]])
    episode_three.add_locations(episode_three_locations, DiceyDungeonsLocation)

    episode_four_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Episode Four" in item[0]])
    episode_four.add_locations(episode_four_locations, DiceyDungeonsLocation)

    episode_five_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Episode Five" in item[0]])
    episode_five.add_locations(episode_five_locations, DiceyDungeonsLocation)

    episode_six_locations = dict([item for item in LOCATION_NAME_TO_ID.items() if "Episode Six" in item[0]])
    episode_six.add_locations(episode_six_locations, DiceyDungeonsLocation)

    # TODO: Add level up checks if Option is enabled


def create_events(world: DiceyDungeonsWorld) -> None:
    menu = world.get_region("Menu")
    episode_one = world.get_region("Episode One")
    episode_two = world.get_region("Episode Two")
    episode_three = world.get_region("Episode Three")
    episode_four = world.get_region("Episode Four")
    episode_five = world.get_region("Episode Five")
    episode_six = world.get_region("Episode Six")

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

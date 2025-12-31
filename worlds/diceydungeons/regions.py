from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Entrance, Region

if TYPE_CHECKING:
    from .world import DiceyDungeonsWorld

STARTING_REGION_NAME = "Menu"

def create_and_connect_regions(world: DiceyDungeonsWorld) -> None:
    create_all_regions(world)
    connect_regions(world)

def create_all_regions(world: DiceyDungeonsWorld) -> None:
    menu = Region("Menu", world.player, world.multiworld)
    episode_one = Region("Episode 1", world.player, world.multiworld)
    episode_two = Region("Episode 2", world.player, world.multiworld)
    episode_three = Region("Episode 3", world.player, world.multiworld)
    episode_four = Region("Episode 4", world.player, world.multiworld)
    episode_five = Region("Episode 5", world.player, world.multiworld)
    episode_six = Region("Episode 6", world.player, world.multiworld)

    regions = [
        menu,
        episode_one,
        episode_two,
        episode_three,
        episode_four,
        episode_five,
        episode_six
    ]

    world.multiworld.regions += regions

def connect_regions(world: DiceyDungeonsWorld) -> None:
    menu = world.get_region("Menu")
    episode_one = world.get_region("Episode 1")
    episode_two = world.get_region("Episode 2")
    episode_three = world.get_region("Episode 3")
    episode_four = world.get_region("Episode 4")
    episode_five = world.get_region("Episode 5")
    episode_six = world.get_region("Episode 6")

    # Menu leads to all episodes, episodes cannot lead to each other.
    for region in [episode_one, episode_two, episode_three, episode_four, episode_five, episode_six]:
        menu.connect(region, region.name)
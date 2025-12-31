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
    episode_one = Region("Episode One", world.player, world.multiworld)
    episode_two = Region("Episode Two", world.player, world.multiworld)
    episode_three = Region("Episode Three", world.player, world.multiworld)
    episode_four = Region("Episode Four", world.player, world.multiworld)
    episode_five = Region("Episode Five", world.player, world.multiworld)
    episode_six = Region("Episode Six", world.player, world.multiworld)

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
    episode_one = world.get_region("Episode One")
    episode_two = world.get_region("Episode Two")
    episode_three = world.get_region("Episode Three")
    episode_four = world.get_region("Episode Four")
    episode_five = world.get_region("Episode Five")
    episode_six = world.get_region("Episode Six")

    # Menu leads to all episodes, episodes cannot lead to each other.
    for region in [episode_one, episode_two, episode_three, episode_four, episode_five, episode_six]:
        menu.connect(region, region.name)
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
    regions = [menu]
    for episode in ["Episode 1", "Episode 2", "Episode 3", "Episode 4", "Episode 5", "Episode 6"]:
        for floor in ["Floor 1", "Floor 2", "Floor 3", "Floor 4", "Floor 5", "Floor 6"]:
            region = Region(episode + " - " + floor, world.player, world.multiworld)
            regions.append(region)

    world.multiworld.regions += regions

def connect_regions(world: DiceyDungeonsWorld) -> None:
    menu = world.get_region("Menu")
    
    floors = ["Floor 1", "Floor 2", "Floor 3", "Floor 4", "Floor 5", "Floor 6"]

    # Menu leads to all floor 1's
    for episode in ["Episode 1", "Episode 2", "Episode 3", "Episode 4", "Episode 5", "Episode 6"]:
        region = world.get_region(episode + " - Floor 1")
        menu.connect(region, region.name)

    # All floors lead to the next floor.
    for i in range(1, len(floors)):
        for episode in ["Episode 1", "Episode 2", "Episode 3", "Episode 4", "Episode 5", "Episode 6"]:
            pre = world.get_region(episode + " - " + floors[i - 1])
            post = world.get_region(episode + " - " + floors[i])
            # Safe to give connection same name as exit location, because everything only has one connection?
            pre.connect(post, post.name)
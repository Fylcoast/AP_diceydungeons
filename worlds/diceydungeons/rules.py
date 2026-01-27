from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import CollectionState
from worlds.generic.Rules import add_rule, set_rule

if TYPE_CHECKING:
    from .world import DiceyDungeonsWorld


def set_all_rules(world: DiceyDungeonsWorld) -> None:
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)


def set_all_entrance_rules(world: DiceyDungeonsWorld) -> None:
    # episode_one = world.get_entrance("Episode 1")
    # episode_two = world.get_entrance("Episode 2")
    # episode_three = world.get_entrance("Episode 3")
    # episode_four = world.get_entrance("Episode 4")
    # episode_five = world.get_entrance("Episode 5")
    # episode_six = world.get_entrance("Episode 6")

    pass


def set_all_location_rules(world: DiceyDungeonsWorld) -> None:
    # Goal location rule
    all_episodes_completed = world.get_location("All episodes completed")
    add_rule(all_episodes_completed, lambda state: state.has_all(("Episode 1 - Episode Completed", 
                                                                  "Episode 2 - Episode Completed", 
                                                                  "Episode 3 - Episode Completed", 
                                                                  "Episode 4 - Episode Completed", 
                                                                  "Episode 5 - Episode Completed", 
                                                                  "Episode 6 - Episode Completed"), 
                                                                  world.player))


def set_completion_condition(world: DiceyDungeonsWorld) -> None:
    world.multiworld.completion_condition[world.player] = lambda state: state.has("All episodes completed", world.player)

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
    # episode_one = world.get_entrance("Episode One")
    # episode_two = world.get_entrance("Episode Two")
    # episode_three = world.get_entrance("Episode Three")
    # episode_four = world.get_entrance("Episode Four")
    # episode_five = world.get_entrance("Episode Five")
    # episode_six = world.get_entrance("Episode Six")

    # TODO: Figure out what region entrance rules will be. Lock episodes behind other episodes?
    pass


def set_all_location_rules(world: DiceyDungeonsWorld) -> None:
    # Only goal location currently has a rule. Since episodes can be run many times, defining location-specific rules seems difficult.
    all_episodes_completed = world.get_location("All episodes completed")
    add_rule(all_episodes_completed, lambda state: state.has_all(("Episode One", "Episode Two", "Episode Three", "Episode Four", "Episode Five", "Episode Six"), world.player))


def set_completion_condition(world: DiceyDungeonsWorld) -> None:
    world.multiworld.completion_condition[world.player] = lambda state: state.has("All episodes completed", world.player)

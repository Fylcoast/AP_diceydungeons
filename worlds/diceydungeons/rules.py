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
    # Fine tune if needed? Main goal is just to make sure they can play the game, so, looser side the better.
    items_needed: dict[str, int] = {
        "Floor 2": 1, 
        "Floor 3": 2, 
        "Floor 4": 4, 
        "Floor 5": 5, 
        "Floor 6": 6
    }

    for episode in ["Episode 1", "Episode 2", "Episode 3", "Episode 4", "Episode 5", "Episode 6"]:
        for floor in ["Floor 2", "Floor 3", "Floor 4", "Floor 5", "Floor 6"]:
            entrance = world.get_entrance(episode + " - " + floor)
            set_rule(entrance, lambda state, required=items_needed[floor]: state.has_group(f"Warrior {episode} Items", world.player, required))
            # if levelsanity is set, consider adding rules for progressive level up to get to X floors. doing whole thing with 2 dice... rough
    
    # Episode progression rules for vanilla progression
    if world.options.episode_progression.value == 0:
        episode_completions_needed: dict[str, int] = {
            "Episode 4": 2,
            "Episode 5": 3,
            "Episode 6": 4
        }

        for episode in episode_completions_needed.keys():
            entrance = world.get_entrance(episode + " - Floor 1")
            set_rule(entrance, lambda state, required=episode_completions_needed[episode]: state.has_group("Warrior Episode Completion", world.player, required))
    


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

from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import CollectionState
from worlds.generic.Rules import add_rule, set_rule

from .data.globals import *

if TYPE_CHECKING:
    from .world import DiceyDungeonsWorld


def set_all_rules(world: DiceyDungeonsWorld) -> None:
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)


def set_all_entrance_rules(world: DiceyDungeonsWorld) -> None:
    character: str = CHARACTER_CODE_TO_NAME[world.options.character.value + 1]

    # Equipment requirements
    items_needed: dict[str, int] = {
        "Floor 2": 1, 
        "Floor 3": 2, 
        "Floor 4": 4, 
        "Floor 5": 5, 
        "Floor 6": 6
    }

    # Branch based on Equipment Availability option and Character
    if world.options.equipment_availability.value == 0:
        for episode in ["Episode 1", "Episode 2", "Episode 3", "Episode 4", "Episode 5", "Episode 6"]:
            for floor in ["Floor 2", "Floor 3", "Floor 4", "Floor 5", "Floor 6"]:
                entrance = world.get_entrance(character + " - " + episode + " - " + floor)
                add_rule(entrance, lambda state, ep=episode, required=items_needed[floor]: state.has_group(f"{character} {ep} Items", world.player, required))
    else:
        for episode in ["Episode 1", "Episode 2", "Episode 3", "Episode 4", "Episode 5", "Episode 6"]:
            for floor in ["Floor 2", "Floor 3", "Floor 4", "Floor 5", "Floor 6"]:
                entrance = world.get_entrance(character + " - " + episode + " - " + floor)
                add_rule(entrance, lambda state, ep=episode, required=items_needed[floor]: state.has_group(f"{character} All Items", world.player, required))
    
    # Levelsanity rules
    if world.options.levelsanity:
        levels_needed: dict[str, int] = {
            "Floor 3": 1, 
            "Floor 4": 2, 
            "Floor 5": 3, 
            "Floor 6": 4
        }

        for episode in range(1, 7):
            for floor, levels in levels_needed.items():
                entrance = world.get_entrance(character + " - Episode " + str(episode) + " - " + floor)
                add_rule(entrance, lambda state, ep=episode, required=levels: state.has(f"{character} - Ep. {ep} Prog. Level Up", world.player, required))

    # Split dice rules
    if world.options.split_dice and world.options.dice_shards_per_die.value > 0:
        dice_needed: dict[str, int] = {
            "Floor 3": 1, 
            "Floor 4": 1, 
            "Floor 5": 2, 
            "Floor 6": 2
        }
        
        for episode in ["Episode 1", "Episode 2", "Episode 3", "Episode 4", "Episode 5", "Episode 6"]:
            for floor, dice in dice_needed.items():
                entrance = world.get_entrance(character + " - " + episode + " - " + floor)
                add_rule(entrance, lambda state, required=dice: state.has("Dice Shard", world.player, required * world.options.dice_shards_per_die.value))
    
    # Episode progression rules for vanilla progression
    if world.options.episode_progression.value == 0:
        episode_completions_needed: dict[str, int] = {
            "Episode 4": 2,
            "Episode 5": 3,
            "Episode 6": 4
        }

        for episode in episode_completions_needed.keys():
            entrance = world.get_entrance(character + " - " + episode + " - Floor 1")
            add_rule(entrance, lambda state, required=episode_completions_needed[episode], character=character: state.has_group(character + " Episode Completion", world.player, required))
    


def set_all_location_rules(world: DiceyDungeonsWorld) -> None:
    character: str = CHARACTER_CODE_TO_NAME[world.options.character.value + 1]

    # Goal location rule
    all_episodes_completed = world.get_location("All episodes completed")
    add_rule(all_episodes_completed, lambda state: state.has_group(character + " Episode Completion", world.player, 6))


def set_completion_condition(world: DiceyDungeonsWorld) -> None:
    world.multiworld.completion_condition[world.player] = lambda state: state.has("All episodes completed", world.player)

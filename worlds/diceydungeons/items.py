from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

from .data.game_data import *

if TYPE_CHECKING:
    from .world import DiceyDungeonsWorld

# Current Warrior item ID blocks taken:
# 1-70ish: warrior items
# 991-996: Episode completion
# 1011-1016: Progressive level ups
# 9990-9999: Filler items

# Warrior items only, to start
ITEM_NAME_TO_ID = dict(
    [
        (item, i) for i, item in enumerate(warrior_items, 1)
    ]
)

DEFAULT_ITEM_CLASSIFICATIONS = dict(
    [
        (item, ItemClassification.progression) for item in warrior_items
    ]
)

for episode in range(1, 7):
    # Episode completions
    ITEM_NAME_TO_ID["Episode " + str(episode) + " - Episode Completed"] = 990 + episode

    # Progressive level ups
    ITEM_NAME_TO_ID["Episode " + str(episode) + " Progressive Level Up"] = 1010 + episode
    DEFAULT_ITEM_CLASSIFICATIONS["Episode " + str(episode) + " Progressive Level Up"] = ItemClassification.progression


# Filler
filler_items: list[str] = ["Frog's Broadsword", "Audrey's Dumbbell", "Rotten Apple's Pet Worm", "Wizard's Spellbook", "Dice Shard"]
for i, item in enumerate(filler_items):
    ITEM_NAME_TO_ID[item] = 9990 + i
    DEFAULT_ITEM_CLASSIFICATIONS[item] = ItemClassification.filler

# Groups
item_name_groups: dict[str, set[str]] = {
    "Warrior Episode 1 Items": set([k for k, v in item_metadata.items() if 1 in v['episode']]),
    "Warrior Episode 2 Items": set([k for k, v in item_metadata.items() if 2 in v['episode']]),
    "Warrior Episode 3 Items": set([k for k, v in item_metadata.items() if 3 in v['episode']]),
    "Warrior Episode 4 Items": set([k for k, v in item_metadata.items() if 4 in v['episode']]),
    "Warrior Episode 5 Items": set([k for k, v in item_metadata.items() if 5 in v['episode']]),
    "Warrior Episode 6 Items": set([k for k, v in item_metadata.items() if 6 in v['episode']]),
    "Warrior Episode Completion": set([f"Episode {i} - Episode Completed" for i in range(1, 7)])
}

class DiceyDungeonsItem(Item):
    game = "Dicey Dungeons"

def get_random_filler_item_name(world: DiceyDungeonsWorld) -> str:
    return world.random.choice(filler_items)

def create_item_with_correct_classification(world: DiceyDungeonsWorld, name: str) -> DiceyDungeonsItem:
    classification = DEFAULT_ITEM_CLASSIFICATIONS[name]
    return DiceyDungeonsItem(name, classification, ITEM_NAME_TO_ID[name], world.player)

def create_all_items(world: DiceyDungeonsWorld) -> None:
    itempool: list[Item] = [
        world.create_item(item) for item in warrior_items
    ]

    if world.options.levelsanity:
        for episode in range(1, 7):
            itempool += [world.create_item(f"Episode {episode} Progressive Level Up") for _ in range(1, 6)]

    # Fill filler slots
    number_of_items = len(itempool)
    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
    needed_number_of_filler_items = number_of_unfilled_locations - number_of_items
    itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]

    world.multiworld.itempool += itempool
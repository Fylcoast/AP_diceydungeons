from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

from .data.game_data import *
from .data.globals import *

if TYPE_CHECKING:
    from .world import DiceyDungeonsWorld

# Current Warrior item ID blocks taken:
# 1-300ish: all equipment
# 911-966: Episode completion
# 1011-1066: Progressive level ups
# 9990-9998: Filler items
# 9999: Dice Shard

# Warrior items only, to start
ITEM_NAME_TO_ID = dict(
    [
        (item, i) for i, item in enumerate(item_metadata.keys(), 1)
    ]
)

DEFAULT_ITEM_CLASSIFICATIONS = dict(
    [
        (item, ItemClassification.progression) for item in item_metadata.keys()
    ]
)

for character_index, character in CHARACTER_CODE_TO_NAME.items():
    for episode in range(1, 7):
        # Episode completions
        ITEM_NAME_TO_ID[character + " - Episode " + str(episode) + " Completed"] = 900 + 10 * character_index + episode
        DEFAULT_ITEM_CLASSIFICATIONS[character + " - Episode " + str(episode) + " Completed"] = ItemClassification.progression

        # Progressive level ups
        ITEM_NAME_TO_ID[character + " - Ep. " + str(episode) + " Prog. Level Up"] = 1000 + 10 * character_index + episode
        DEFAULT_ITEM_CLASSIFICATIONS[character + " - Ep. " + str(episode) + " Prog. Level Up"] = ItemClassification.progression


# Filler
filler_items: list[str] = ["Frog's Broadsword", "Audrey's Dumbbell", "Rotten Apple's Pet Worm", "Wizard's Spellbook"]
for i, item in enumerate(filler_items):
    ITEM_NAME_TO_ID[item] = 9990 + i
    DEFAULT_ITEM_CLASSIFICATIONS[item] = ItemClassification.filler

# Dice Shard
ITEM_NAME_TO_ID["Dice Shard"] = 9999
DEFAULT_ITEM_CLASSIFICATIONS["Dice Shard"] = ItemClassification.progression

# Groups
item_name_groups: dict[str, set[str]] = {
    "Warrior Episode 1 Items": set([k for k, v in item_metadata.items() if 1 in v['warrior']['episode']]),
    "Warrior Episode 2 Items": set([k for k, v in item_metadata.items() if 2 in v['warrior']['episode']]),
    "Warrior Episode 3 Items": set([k for k, v in item_metadata.items() if 3 in v['warrior']['episode']]),
    "Warrior Episode 4 Items": set([k for k, v in item_metadata.items() if 4 in v['warrior']['episode']]),
    "Warrior Episode 5 Items": set([k for k, v in item_metadata.items() if 5 in v['warrior']['episode']]),
    "Warrior Episode 6 Items": set([k for k, v in item_metadata.items() if 6 in v['warrior']['episode']]),
    "Warrior All Items": set([k for k in warrior_items]),
    
    "Thief Episode 1 Items": set([k for k, v in item_metadata.items() if 1 in v['thief']['episode']]),
    "Thief Episode 2 Items": set([k for k, v in item_metadata.items() if 2 in v['thief']['episode']]),
    "Thief Episode 3 Items": set([k for k, v in item_metadata.items() if 3 in v['thief']['episode']]),
    "Thief Episode 4 Items": set([k for k, v in item_metadata.items() if 4 in v['thief']['episode']]),
    "Thief Episode 5 Items": set([k for k, v in item_metadata.items() if 5 in v['thief']['episode']]),
    "Thief Episode 6 Items": set([k for k, v in item_metadata.items() if 6 in v['thief']['episode']]),
    "Thief All Items": set([k for k in thief_items]),
    
    "Robot Episode 1 Items": set([k for k, v in item_metadata.items() if 1 in v['robot']['episode']]),
    "Robot Episode 2 Items": set([k for k, v in item_metadata.items() if 2 in v['robot']['episode']]),
    "Robot Episode 3 Items": set([k for k, v in item_metadata.items() if 3 in v['robot']['episode']]),
    "Robot Episode 4 Items": set([k for k, v in item_metadata.items() if 4 in v['robot']['episode']]),
    "Robot Episode 5 Items": set([k for k, v in item_metadata.items() if 5 in v['robot']['episode']]),
    "Robot Episode 6 Items": set([k for k, v in item_metadata.items() if 6 in v['robot']['episode']]),
    "Robot All Items": set([k for k in robot_items]),
    
    "Warrior Episode Completion": set([f"Warrior - Episode {i} Completed" for i in range(1, 7)]),
    "Thief Episode Completion": set([f"Thief - Episode {i} Completed" for i in range(1, 7)]),
    "Robot Episode Completion": set([f"Robot - Episode {i} Completed" for i in range(1, 7)]),
}

class DiceyDungeonsItem(Item):
    game = "Dicey Dungeons"

def get_random_filler_item_name(world: DiceyDungeonsWorld) -> str:
    return world.random.choice(filler_items)

def create_item_with_correct_classification(world: DiceyDungeonsWorld, name: str) -> DiceyDungeonsItem:
    classification = DEFAULT_ITEM_CLASSIFICATIONS[name]
    return DiceyDungeonsItem(name, classification, ITEM_NAME_TO_ID[name], world.player)

def create_all_items(world: DiceyDungeonsWorld) -> None:
    itempool: list[Item] = []

    # Character choice
    character: str = CHARACTER_CODE_TO_NAME[world.options.character.value + 1]
    item_list: list[str] = all_character_item_lists[world.options.character.value]
    
    # Equipment pool
    itempool += [world.create_item(item) for item in item_list]

    # Levelsanity
    if world.options.levelsanity:
        for episode in range(1, 7):
            itempool += [world.create_item(f"{character} - Ep. {episode} Prog. Level Up") for _ in range(1, 6)]
    
    # Split dice
    if world.options.split_dice and world.options.dice_shards_per_die > 0:
        itempool += [world.create_item("Dice Shard") for _ in range(world.options.dice_shards_per_die * 3)]
        if world.options.spare_dice_shards > 0:
            itempool += [DiceyDungeonsItem("Dice Shard", ItemClassification.useful, ITEM_NAME_TO_ID["Dice Shard"], world.player) for _ in range(world.options.spare_dice_shards)]

    # Fill filler slots
    number_of_items = len(itempool)
    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
    needed_number_of_filler_items = number_of_unfilled_locations - number_of_items
    itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]

    world.multiworld.itempool += itempool
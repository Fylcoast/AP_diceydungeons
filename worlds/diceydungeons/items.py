from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

from .data.extracted_data import *

if TYPE_CHECKING:
    from .world import DiceyDungeonsWorld

# Warrior items only, to start
ITEM_NAME_TO_ID = dict(
    [
        (item, i) for i, item in enumerate(warrior_items)
    ]
)
# ITEM_NAME_TO_ID = dict(
#     [
#         (item, i) for i, item in enumerate(list(set(<all item lists from extracted_data?>)))
#     ]
# )

DEFAULT_ITEM_CLASSIFICATIONS = dict(
    [
        (item, ItemClassification.useful) for item in warrior_items
    ]
)

# Filler
ITEM_NAME_TO_ID["Dice Shard"] = 9999
DEFAULT_ITEM_CLASSIFICATIONS["Dice Shard"] = ItemClassification.filler

class DiceyDungeonsItem(Item):
    game = "Dicey Dungeons"

def get_filler_item_name(world: DiceyDungeonsWorld) -> str:
    # There's not a lot of filler we'd be allowed? Like, we can't really heal the character... right?
    return "Dice Shard"

def create_item_with_correct_classification(world: DiceyDungeonsWorld, name: str) -> DiceyDungeonsItem:
    classification = DEFAULT_ITEM_CLASSIFICATIONS[name]
    return DiceyDungeonsItem(name, classification, ITEM_NAME_TO_ID[name], world.player)

def create_all_items(world: DiceyDungeonsWorld) -> None:
    itempool: list[Item] = [
        world.create_item(item) for item in warrior_items
    ]

    # Fill filler slots
    number_of_items = len(itempool)
    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
    needed_number_of_filler_items = number_of_unfilled_locations - number_of_items
    itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]

    world.multiworld.itempool += itempool
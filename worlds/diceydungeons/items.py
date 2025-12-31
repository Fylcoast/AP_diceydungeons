from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

from .extracted_data import *

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

# TODO: Figure out better item classifications?
# I guess they're all useful, because, how do we decide a player has enough to like, win?
DEFAULT_ITEM_CLASSIFICATIONS = dict(
    [
        (item, ItemClassification.useful) for item in warrior_items
    ]
)

class DiceyDungeonsItem(Item):
    game = "Dicey Dungeons"

def get_random_filler_item_name(world: DiceyDungeonsWorld) -> str:
    # There's not a lot of filler we'd be allowed? Like, we can't really heal the character... right?
    pass

def create_item_with_correct_classification(world: DiceyDungeonsWorld, name: str) -> DiceyDungeonsItem:
    classification = DEFAULT_ITEM_CLASSIFICATIONS[name]
    return DiceyDungeonsItem(name, classification, ITEM_NAME_TO_ID[name], world.player)

def create_all_items(world: DiceyDungeonsWorld) -> None:
    #TODO: Sync number of items with number of locations
    # Actually, that probably is more about locations... We can probably just add all the items we got?
    # Let's go with that.

    itempool: list[Item] = [
        world.create_item(item) for item in DEFAULT_ITEM_CLASSIFICATIONS.keys()
    ]

    #TODO: Filler items?

    world.multiworld.itempool += itempool
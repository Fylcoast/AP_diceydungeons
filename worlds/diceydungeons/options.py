from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle, DefaultOnToggle

# Defined for location creation
MAXIMUM_CHECKS_PER_CHEST: int = 5
MAXIMUM_CHECKS_PER_SHOP: int = 5
MAXIMUM_CHECKS_PER_TRADE: int = 5
MAXIMUM_DICE_SHARDS_PER_DIE: int = 5
MAXIMUM_BONUS_DICE_SHARDS: int = 12

class ChecksPerChest(Range):
    '''
    Determines the number of AP items that can
    be found within any individual chest (e.g. 
    in Episode 1, Floor 1 chest) across runs (1 per run).
    '''
    display_name = "Checks per chest"
    range_start = 0
    range_end = MAXIMUM_CHECKS_PER_CHEST
    default = 1

class ChecksPerShop(Range):
    '''
    Determines the number of AP items that generate
    for any individual shop (e.g. 
    in Episode 1, Floor 2 shop). Also determines the number
    (up to 3) of items in a shop which can be AP at a time.
    Items above 3 will fill in to those shops as they're
    purchased (aka as the location checks are sent).
    '''
    display_name = "Checks per shop"
    range_start = 0
    range_end = MAXIMUM_CHECKS_PER_SHOP
    default = 2

class ChecksPerTrade(Range):
    '''
    Determines the number of AP items that generate
    for any individual trade (e.g. 
    in Episode 1, Floor 4 trade). Only one will be
    given at a time. (Adds 1 check per episode)
    '''
    display_name = "Checks per trade"
    range_start = 0
    range_end = MAXIMUM_CHECKS_PER_TRADE
    default = 1

class Levelsanity(DefaultOnToggle):
    '''
    Determines whether level up rewards grants checks
    (Adds 5 checks for each episode)
    '''
    display_name = "Levelsanity"

class SplitDice(Toggle):
    '''
    Determines whether Dice Shards are required to receive
    dice when leveling up. Shared across episodes.
    '''
    display_name = "Split Dice"

class DiceShardsPerDie(Range):
    '''
    Determines number of pieces to split each level up die into. 
    Only takes effect if Split Dice is On. 
    (Adds 3 items for each Dice Shard per Die)
    '''
    display_name = "Dice Shards Per Die"
    range_start = 0
    range_end = MAXIMUM_DICE_SHARDS_PER_DIE
    default = 0

class SpareDiceShards(Range):
    '''
    Includes bonus dice shards, to make getting your dice 
    a little easier.
    Only takes effect if Split Dice is On.
    (Adds items equal to setting)
    '''
    display_name = "Bonus Dice Shards"
    range_start = 0
    range_end = MAXIMUM_BONUS_DICE_SHARDS
    default = 0

class EpisodeProgression(Choice):
    '''
    Determines how you gain access to Episodes. This affects logic as well.

    vanilla: Episodes are unlocked as normal: 
    Episode 4 requires any 2 prior episodes to be completed. 
    3 for Episode 5, and 4 for Episode 6.

    open_world: All episodes are available from start. 
    Note: This uses base save, so you must have unlocked 
    all episodes prior for this to work.
    '''

    display_name = "Episode progression"

    option_vanilla = 0
    option_open_world = 1

    default = option_vanilla

class Floor5ShopSelection(Choice):
    '''
    Determines what is purchasable in the Floor 5 shops.

    vanilla: Floor 5 shops will include 1 item, 1 upgrade, 
    and 1 heal. The item could be a location check (if 
    configured) or equipment.

    items_only: Floor 5 shops will have all 3 slots
    filled with items, making them just like any other
    shop.
    '''

    display_name = "Floor 5 Shop Selection"

    option_vanilla = 0
    option_items_only = 1

    default = option_vanilla

class SkipCutscenes(DefaultOnToggle):
    '''
    Select whether you want to skip cutscenes before and 
    after episodes, as well as the tutorial at the 
    beginning of the game.
    '''
    display_name = "Skip cutscenes"

@dataclass
class DiceyDungeonsOptions(PerGameCommonOptions):
    levelsanity: Levelsanity
    checks_per_chest: ChecksPerChest
    checks_per_shop: ChecksPerShop
    checks_per_trade: ChecksPerTrade
    split_dice: SplitDice
    dice_shards_per_die: DiceShardsPerDie
    spare_dice_shards: SpareDiceShards
    episode_progression: EpisodeProgression
    floor_5_shop_selection: Floor5ShopSelection
    skip_cutscenes: SkipCutscenes

option_groups = [
    OptionGroup(
        "Location Options",
        [Levelsanity, ChecksPerShop, ChecksPerChest, ChecksPerTrade],
    ),
    OptionGroup(
        "Dice Options",
        [SplitDice, DiceShardsPerDie, SpareDiceShards]
    ),
    OptionGroup(
        "Gameplay Options",
        [EpisodeProgression, Floor5ShopSelection]
    ),
    OptionGroup(
        "Quality of Life",
        [SkipCutscenes]
    )
]

option_presets = {
    "dev-recommended": {
        "levelsanity": True,
        "checks_per_chest": 1,
        "checks_per_shop": 2,
        "checks_per_trade": 1,
        "split_dice": False,
        "dice_shards_per_die": 0,
        "spare_dice_shards": 0,
        "episode_progression": EpisodeProgression.default,
        "floor_5_shop_selection": Floor5ShopSelection.default,
        "skip_cutscenes": True
    },
    "check-lover": {
        "levelsanity": True,
        "checks_per_chest": 3,
        "checks_per_shop": 3,
        "checks_per_trade": 3,
        "split_dice": True,
        "dice_shards_per_die": 3,
        "spare_dice_shards": 6,
        "episode_progression": EpisodeProgression.option_open_world,
        "floor_5_shop_selection": Floor5ShopSelection.option_items_only,
        "skip_cutscenes": True
    }
}
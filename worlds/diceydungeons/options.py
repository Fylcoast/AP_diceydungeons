from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle, DefaultOnToggle

# Defined for location creation
MAXIMUM_CHECKS_PER_CHEST: int = 5
MAXIMUM_CHECKS_PER_SHOP: int = 5
MAXIMUM_CHECKS_PER_TRADE: int = 5

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

@dataclass
class DiceyDungeonsOptions(PerGameCommonOptions):
    levelsanity: Levelsanity
    checks_per_chest: ChecksPerChest
    checks_per_shop: ChecksPerShop
    checks_per_trade: ChecksPerTrade

option_groups = [
    OptionGroup(
        "Location Options",
        [Levelsanity, ChecksPerShop, ChecksPerChest, ChecksPerTrade],
    ),
]
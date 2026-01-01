from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle, DefaultOnToggle

# Defined for location creation
MAX_MAXIMUM_CHECKS_PER_CHEST: int = 5
MAX_MAXIMUM_CHECKS_PER_SHOP: int = 5

#TODO: Add more options?

class MaximumChecksPerChest(Range):
    '''
    Determines the maximum number of AP items that can
    be found within any individual chest (e.g. 
    in Episode 1, Floor 1 chest) across runs.
    '''
    display_name = "Maximum checks per chest"
    range_start = 0
    range_end = MAX_MAXIMUM_CHECKS_PER_CHEST
    default = 2

class MaximumChecksPerShop(Range):
    '''
    Determines the maximum number of AP items that can
    be found within any individual shop (e.g. 
    in Episode 1, Floor 2 shop) across runs.
    '''
    display_name = "Maximum checks per shop"
    range_start = 0
    range_end = MAX_MAXIMUM_CHECKS_PER_SHOP
    default = 3

class Levelsanity(DefaultOnToggle):
    '''
    Determines whether level up rewards grants checks
    (Adds 5 checks for each episode)
    '''
    display_name = "Levelsanity"

# Client will have to implement this one
class GuaranteeSomeChecks(DefaultOnToggle):
    '''
    Guarantees at least 1 AP item will be an option for any location with checks remaining
    (e.g. Shops will always have 1 AP item, as long as there are AP items left for that particular shop)
    '''
    display_name = "Guarantee some checks"

@dataclass
class DiceyDungeonsOptions(PerGameCommonOptions):
    levelsanity: Levelsanity
    guarantee_some_checks: GuaranteeSomeChecks
    maximum_checks_per_chest: MaximumChecksPerChest
    maximum_checks_per_shop: MaximumChecksPerShop

option_groups = [
    OptionGroup(
        "Location Options",
        [Levelsanity, MaximumChecksPerShop, MaximumChecksPerChest],
    ),
    OptionGroup(
        "Quality of Life Options",
        [GuaranteeSomeChecks],
    ),
]
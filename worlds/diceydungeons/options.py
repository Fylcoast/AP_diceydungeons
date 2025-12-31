from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle, DefaultOnToggle

#TODO: Add more options?

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

option_groups = [
    OptionGroup(
        "Location Options",
        [Levelsanity],
    ),
    OptionGroup(
        "Quality of Life Options",
        [GuaranteeSomeChecks],
    ),
]
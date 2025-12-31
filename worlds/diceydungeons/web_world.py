from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld

from .options import option_groups

class DiceyDungeonsWebWorld(WebWorld):
    game = "Dicey Dungeons"
    theme = "partyTime"

    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Dicey Dungeons for MultiWorld.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Fylcoast"],
    )

    tutorials = [setup_en]

    option_groups = option_groups
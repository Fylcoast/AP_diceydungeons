class FloorData:
    num_chests: int
    num_shops: int
    num_shop_slots: int
    num_heals: int
    num_upgrades: int
    num_trades: int

    def __init__(self, _num_chests: int, _num_shops: int, _num_shop_slots: int, _num_heals: int, _num_upgrades: int, _num_trades: int):
        self.num_chests = _num_chests
        self.num_shops = _num_shops
        self.num_shop_slots = _num_shop_slots
        self.num_heals = _num_heals
        self.num_upgrades = _num_upgrades
        self.num_trades = _num_trades

class EpisodeData:
    name: str
    floor1: FloorData
    floor2: FloorData
    floor3: FloorData
    floor4: FloorData
    floor5: FloorData
    floors: list[FloorData]
    # Floor 6 is always just the boss

    level_items: dict[int, str]
    """Any level present here has a predefined item it gives (e.g. Dice) instead of a random item"""

    standard_level_items: dict[int, list[str]]
    """Full list of base level up rewards, for when levelsanity is off"""

    def __init__(self, name: str, floor1: FloorData, floor2: FloorData, floor3: FloorData, floor4: FloorData, floor5: FloorData, level_items: dict[int, str], standard_level_items: dict[int, list[str]]):
        self.name = name
        self.floor1 = floor1
        self.floor2 = floor2
        self.floor3 = floor3
        self.floor4 = floor4
        self.floor5 = floor5
        self.floors = [self.floor1, self.floor2, self.floor3, self.floor4, self.floor5]
        self.level_items = level_items
        self.standard_level_items = standard_level_items

episode1 = EpisodeData(
    "Episode 1",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 1, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 0, 0, 1, 0, 1),
    FloorData(1, 1, 3, 2, 1, 0),
    {2: "Dice", 4: "Dice", 6: "Dice"},
    {2: ["Dice"], 3: ["Equipment:Spiked Shield", "Equipment:Boomerang"], 4: ["Dice"], 5: ["Equipment:Shield Bash", "Upgrade"], 6: ["Dice"]}
)

episode2 = EpisodeData(
    "Episode 2",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 1, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 0, 0, 1, 0, 1),
    FloorData(1, 1, 3, 2, 1, 0),
    {2: "Dice", 4: "Dice", 6: "Dice"},
    {2: ["Dice"], 3: ["Equipment:Spiked Shield+", "Equipment:Boomerang+"], 4: ["Dice"], 5: ["Equipment:Shield Bash+", "Equipment:Pirate Hook+", "Equipment:Midnight Charm+"], 6: ["Dice"]}
)

episode3 = EpisodeData(
    "Episode 3",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 1, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 0, 0, 1, 0, 1),
    FloorData(1, 1, 3, 2, 1, 0),
    {2: "Dice", 4: "Dice", 6: "Dice"},
    {2: ["Dice"], 3: ["Equipment:Spiked Shield", "Equipment:Iron Shield"], 4: ["Dice"], 5: ["Equipment:Shield Bash", "Equipment:Last Stand"], 6: ["Dice"]}
)

episode4 = EpisodeData(
    "Episode 4",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 1, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 0, 0, 1, 0, 1),
    FloorData(1, 1, 3, 2, 1, 0),
    {2: "Dice", 4: "Dice", 6: "Dice"},
    {2: ["Dice"], 3: ["Equipment:Spiked Shield", "Equipment:Boomerang"], 4: ["Dice"], 5: ["Equipment:Shield Bash", "Upgrade"], 6: ["Dice"]}
)

episode5 = EpisodeData(
    "Episode 5",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(2, 1, 3, 1, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 0, 0, 1, 0, 1),
    FloorData(1, 1, 3, 2, 1, 0),
    {2: "Dice", 4: "Dice", 6: "Dice"},
    {2: ["Dice"], 3: ["Equipment:Crescent Moon Blade", "Equipment:Polar Star"], 4: ["Dice"], 5: ["Equipment:Battering Ram", "Upgrade"], 6: ["Dice"]}
)

episode6 = EpisodeData(
    "Episode 6",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 1, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 0, 0, 1, 0, 1),
    FloorData(1, 1, 3, 2, 1, 0),
    {2: "Dice", 4: "Dice", 6: "Dice"},
    {2: ["Dice"], 3: ["Equipment:Crescent Moon Blade", "Equipment:Polar Star"], 4: ["Dice"], 5: ["Equipment:Battering Ram", "Upgrade"], 6: ["Dice"]}
)

warrior_episodes = [episode1, episode2, episode3, episode4, episode5, episode6]

warrior_2_start_game_curse_removals = ["Rules.addplayerinnatestatus(CURSE);"]
warrior_3_start_game_hp_loss_removals = ["Rules.hpchangeonlevelup = -2;", "Rules.lowhpmusic = false;"]

# thief_normal
thief_episode_1 = EpisodeData(
    "Episode 1",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 2, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 1, 3, 2, 0, 1),
    FloorData(1, 1, 3, 3, 1, 0),
    {2: "Dice", 4: "Dice", 6: "Dice"},
    {2: ["Dice"], 3: ["Equipment:Poison Needle", "Equipment:Crowbar"], 4: ["Dice"], 5: ["Equipment:Skeleton Key", "Equipment:Hacksaw", "Upgrade"], 6: ["Dice"]}
)

# thief_finderskeepers
thief_episode_2 = EpisodeData(
    "Episode 2",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(0, 1, 3, 2, 0, 0),
    FloorData(0, 0, 0, 2, 2, 0),
    FloorData(0, 0, 0, 2, 0, 1),
    FloorData(0, 1, 3, 3, 1, 0),
    {2: "Dice", 4: "Dice", 6: "Dice"},
    {2: ["Dice"], 3: ["Equipment:Poison Needle", "Equipment:Crowbar"], 4: ["Dice"], 5: ["Equipment:Skeleton Key", "Equipment:Hacksaw", "Upgrade"], 6: ["Dice"]}
)

# thief_uptick
thief_episode_3 = EpisodeData(
    "Episode 3",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 2, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 1, 3, 2, 0, 1),
    FloorData(1, 1, 3, 3, 1, 0),
    {2: "Dice", 4: "Dice", 6: "Dice"},
    {2: ["Dice"], 3: ["Equipment:Kunai", "Equipment:Hall of Mirrors"], 4: ["Dice"], 5: ["Equipment:Backstab", "Equipment:Hacksaw", "Upgrade"], 6: ["Dice"]}
)

# thief_normal
thief_episode_4 = EpisodeData(
    "Episode 4",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 2, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 1, 3, 2, 0, 1),
    FloorData(1, 1, 3, 3, 1, 0),
    {2: "Dice", 4: "Dice", 6: "Dice"},
    {2: ["Dice"], 3: ["Equipment:Poison Needle", "Equipment:Crowbar"], 4: ["Dice"], 5: ["Equipment:Skeleton Key", "Equipment:Hacksaw", "Upgrade"], 6: ["Dice"]}
)

# thief_paralleluniverse
thief_episode_5 = EpisodeData(
    "Episode 5",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 2, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 1, 3, 2, 0, 1),
    FloorData(1, 1, 3, 3, 1, 0),
    {2: "Dice", 4: "Dice", 6: "Dice"},
    {2: ["Dice"], 3: ["Equipment:Cowbell", "Equipment:Wrecking Ball"], 4: ["Dice"], 5: ["Equipment:Berlin Key", "Equipment:Bronze Cauldron", "Upgrade"], 6: ["Dice"]}
)

# thief_remixgenerator
thief_episode_6 = EpisodeData(
    "Episode 6",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 2, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 1, 3, 2, 0, 1),
    FloorData(1, 1, 3, 3, 1, 0),
    {2: "Dice", 4: "Dice", 6: "Dice"},
    {2: ["Dice"], 3: ["Equipment:Poison Needle", "Equipment:Cowbell"], 4: ["Dice"], 5: ["Equipment:Berlin Key", "Equipment:Hacksaw", "Upgrade"], 6: ["Dice"]}
)

thief_episodes = [thief_episode_1, thief_episode_2, thief_episode_3, thief_episode_4, thief_episode_5, thief_episode_6]

# robot_normal
robot_episode_1 = EpisodeData(
    "Episode 1",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 2, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 0, 0, 2, 0, 1),
    FloorData(1, 1, 3, 2, 1, 0),
    {2: "CPU:2", 4: "CPU:2", 6: "CPU:2"},
    {2: ["CPU:2"], 3: ["Equipment:Buster Sword", "Equipment:Ultima Weapon"], 4: ["CPU:2"], 5: ["Equipment:Heat Sink", "Equipment:Increment"], 6: ["CPU:2"]}
)

# robot_normal
robot_episode_2 = EpisodeData(
    "Episode 2",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 2, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 0, 0, 2, 0, 1),
    FloorData(1, 1, 3, 2, 1, 0),
    {2: "CPU:2", 4: "CPU:2", 6: "CPU:2"},
    {2: ["CPU:2"], 3: ["Equipment:Buster Sword", "Equipment:Ultima Weapon"], 4: ["CPU:2"], 5: ["Equipment:Heat Sink", "Equipment:Increment"], 6: ["CPU:2"]}
)

# robot_youchooseyoulose
robot_episode_3 = EpisodeData(
    "Episode 3",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(0, 1, 3, 2, 0, 0),
    FloorData(0, 1, 3, 2, 1, 0),
    FloorData(1, 0, 0, 2, 0, 1),
    FloorData(0, 1, 3, 2, 1, 0),
    {},
    {2: ["Equipment:Spatula", "Equipment:Doppeldice"], 3: ["Equipment:Buster Sword", "Equipment:Ruby Weapon"], 4: ["Equipment:System Shock", "Equipment:Flame War"], 5: ["Equipment:Chocolate Cookie", "Equipment:Mechanical Arm"], 6: ["Equipment:Dexterity Charm", "Upgrade"]}
)

# robot_normal
robot_episode_4 = EpisodeData(
    "Episode 4",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 2, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 0, 0, 2, 0, 1),
    FloorData(1, 1, 3, 2, 1, 0),
    {2: "CPU:2", 4: "CPU:2", 6: "CPU:2"},
    {2: ["CPU:2"], 3: ["Equipment:Buster Sword", "Equipment:Ultima Weapon"], 4: ["CPU:2"], 5: ["Equipment:Heat Sink", "Equipment:Increment"], 6: ["CPU:2"]}
)

# robot_paralleluniverse
robot_episode_5 = EpisodeData(
    "Episode 5",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 2, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 0, 0, 2, 0, 1),
    FloorData(1, 1, 3, 2, 1, 0),
    {2: "CPU:2", 4: "CPU:2", 6: "CPU:2"},
    {2: ["CPU:2"], 3: ["Equipment:Stack Overflow", "Equipment:Precious Egg@6"], 4: ["CPU:2"], 5: ["Equipment:Cooling Fan", "Equipment:Concatenate"], 6: ["CPU:2"]}
)

# robot_remixgenerator
robot_episode_6 = EpisodeData(
    "Episode 6",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 2, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 0, 0, 2, 0, 1),
    FloorData(1, 1, 3, 2, 1, 0),
    {2: "CPU:2", 4: "CPU:2", 6: "CPU:2"},
    {2: ["CPU:2"], 3: ["Equipment:Missing Score", "Equipment:Spud Cannon"], 4: ["CPU:2"], 5: ["Equipment:Cooling Fan", "Equipment:Increment"], 6: ["CPU:2"]}
)

robot_episodes = [robot_episode_1, robot_episode_2, robot_episode_3, robot_episode_4, robot_episode_5, robot_episode_6]

# inventor_normal
inventor_episode_1 = EpisodeData(
    "Episode 1",
    FloorData(3, 0, 0, 0, 0, 0),
    FloorData(2, 1, 3, 2, 0, 0),
    FloorData(3, 2, 3, 1, 0, 0),
    FloorData(2, 0, 0, 2, 0, 0),
    FloorData(2, 1, 3, 2, 1, 0),
    {2: "Dice", 4: "Dice", 6: "Dice"},
    {2: ["Dice"], 3: ["Equipment:Flamethrower", "Equipment:Doppeldice"], 4: ["Dice"], 5: ["Upgrade", "Equipment:Scrap Metal", "Copy"], 6: ["Dice"]}
)

# inventor_normal
inventor_episode_2 = EpisodeData(
    "Episode 2",
    FloorData(3, 0, 0, 0, 0, 0),
    FloorData(2, 1, 3, 2, 0, 0),
    FloorData(3, 2, 3, 1, 0, 0),
    FloorData(2, 0, 0, 2, 0, 0),
    FloorData(2, 1, 3, 2, 1, 0),
    {2: "Dice", 4: "Dice", 6: "Dice"},
    {2: ["Dice"], 3: ["Equipment:Flamethrower", "Equipment:Doppeldice"], 4: ["Dice"], 5: ["Upgrade", "Equipment:Scrap Metal", "Copy"], 6: ["Dice"]}
)

# inventor_rust
inventor_episode_3 = EpisodeData(
    "Episode 3",
    FloorData(3, 0, 0, 0, 0, 0),
    FloorData(2, 1, 3, 2, 0, 0),
    FloorData(3, 2, 3, 1, 0, 0),
    FloorData(3, 0, 0, 2, 0, 0),
    FloorData(2, 1, 3, 2, 1, 0),
    {2: "Dice", 4: "Dice", 6: "Dice"},
    {2: ["Dice"], 3: ["Equipment:Grindstone", "Equipment:Doppeldice"], 4: ["Dice"], 5: ["Upgrade", "Equipment:Hammer", "Copy"], 6: ["Dice"]}
)

# inventor_normal
inventor_episode_4 = EpisodeData(
    "Episode 4",
    FloorData(3, 0, 0, 0, 0, 0),
    FloorData(2, 1, 3, 2, 0, 0),
    FloorData(3, 2, 3, 1, 0, 0),
    FloorData(2, 0, 0, 2, 0, 0),
    FloorData(2, 1, 3, 2, 1, 0),
    {2: "Dice", 4: "Dice", 6: "Dice"},
    {2: ["Dice"], 3: ["Equipment:Flamethrower", "Equipment:Doppeldice"], 4: ["Dice"], 5: ["Upgrade", "Equipment:Scrap Metal", "Copy"], 6: ["Dice"]}
)

# inventor_paralleluniverse
inventor_episode_5 = EpisodeData(
    "Episode 5",
    FloorData(3, 0, 0, 0, 0, 0),
    FloorData(2, 1, 3, 2, 0, 0),
    FloorData(2, 1, 3, 1, 0, 0),
    FloorData(2, 1, 3, 2, 0, 0),
    FloorData(2, 1, 3, 2, 1, 0),
    {2: "Dice", 4: "Dice", 6: "Dice"},
    {2: ["Dice"], 3: ["Equipment:Molotov Cocktail", "Equipment:Doppeltwice"], 4: ["Dice"], 5: ["Upgrade", "Equipment:Scrap Bump", "Copy"], 6: ["Dice"]}
)

# inventor_remixgenerator
inventor_episode_6 = EpisodeData(
    "Episode 6",
    FloorData(3, 0, 0, 0, 0, 0),
    FloorData(2, 1, 3, 2, 0, 0),
    FloorData(3, 2, 3, 1, 0, 0),
    FloorData(2, 0, 0, 2, 0, 0),
    FloorData(2, 1, 3, 2, 1, 0),
    {2: "Dice", 4: "Dice", 6: "Dice"},
    {2: ["Dice"], 3: ["Equipment:Screwdriver", "Equipment:Chainsaw"], 4: ["Dice"], 5: ["Upgrade", "Equipment:Scrap Spear", "Copy"], 6: ["Dice"]}
)

inventor_episodes = [inventor_episode_1, inventor_episode_2, inventor_episode_3, inventor_episode_4, inventor_episode_5, inventor_episode_6]

all_character_episodes = [warrior_episodes, thief_episodes, robot_episodes, inventor_episodes]

start_game_upgrade_all_equipment_additions = ["Rules.upgradeplayerequipment = true;", "Rules.substitute(~upgrade~[;] ~copyshop~);"]

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

    def __init__(self, name: str, floor1: FloorData, floor2: FloorData, floor3: FloorData, floor4: FloorData, floor5: FloorData):
        self.name = name
        self.floor1 = floor1
        self.floor2 = floor2
        self.floor3 = floor3
        self.floor4 = floor4
        self.floor5 = floor5
        self.floors = [self.floor1, self.floor2, self.floor3, self.floor4, self.floor5]

episode1 = EpisodeData(
    "Episode 1",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 1, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 0, 0, 1, 0, 1),
    FloorData(1, 2, 3, 2, 1, 0)
)

episode2 = EpisodeData(
    "Episode 2",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 1, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 0, 0, 1, 0, 1),
    FloorData(1, 2, 3, 2, 1, 0)
)

episode3 = EpisodeData(
    "Episode 3",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 1, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 0, 0, 1, 0, 1),
    FloorData(1, 2, 3, 2, 1, 0)
)

episode4 = EpisodeData(
    "Episode 4",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 1, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 0, 0, 1, 0, 1),
    FloorData(1, 2, 3, 2, 1, 0)
)

episode5 = EpisodeData(
    "Episode 5",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(2, 1, 3, 1, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 0, 0, 1, 0, 1),
    FloorData(1, 2, 3, 2, 1, 0)
)

episode6 = EpisodeData(
    "Episode 6",
    FloorData(1, 0, 0, 0, 0, 0),
    FloorData(1, 1, 3, 1, 0, 0),
    FloorData(1, 1, 3, 2, 1, 0),
    FloorData(1, 0, 0, 1, 0, 1),
    FloorData(1, 2, 3, 2, 1, 0)
)

warrior_episodes = [episode1, episode2, episode3, episode4, episode5, episode6]

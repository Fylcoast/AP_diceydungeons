from ..data.episode_data import *

generator_names: list[str] = ['warrior_one', 'warrior_two', 'warrior_three', 'warrior_four', 'warrior_five', 'warrior_six']
"""Names for generators, accessed with generator_names[<episode_num - 1>]"""

class ShopItems:
    shop_num: int
    floor_num: int
    episode_num: int
    items: list[str]

    def __init__(self, num: int, episode: int, floor: int):
        self.shop_num = num
        self.episode_num = episode
        self.floor_num = floor
        self.items = []
    
    def add_to_shop(self, item: str):
        self.items.append(item)
    
    def is_shop_filled(self) -> bool:
        shop_limit = warrior_episodes[self.episode_num - 1].floors[self.floor_num - 1].num_shop_slots
        return len(self.items) >= shop_limit

class FloorItems:
    floor_num: int
    episode_num: int
    chests: list[str]
    shops: list[ShopItems]

    def __init__(self, num: int, episode: int):
        self.floor_num = num
        self.episode_num = episode
        self.chests = []
        self.shops = [ShopItems(i + 1, self.episode_num, self.floor_num) for i in range(warrior_episodes[self.episode_num - 1].floors[self.floor_num - 1].num_shops)]
    
    def add_to_chests(self, item: str):
        self.chests.append(item)
    
    def add_to_shops(self, item: str):
        for shop in self.shops:
            if not shop.is_shop_filled():
                shop.add_to_shop(item)
                return
    
    def are_floor_chests_filled(self) -> bool:
        """Are all chests full on floor, for particular episode limits?"""
        floor_limit = warrior_episodes[self.episode_num - 1].floors[self.floor_num - 1].num_chests
        return len(self.chests) >= floor_limit
    
    def are_floor_shops_filled(self) -> bool:
        """Are all shops full on floor, for particular episode limits?"""
        return all([shop.is_shop_filled() for shop in self.shops])
    
    def is_floor_full(self) -> bool:
        """Are all lists full to capacity for floor?"""
        return self.are_floor_chests_filled() and self.are_floor_shops_filled()

    def get_floor_items(self) -> list[dict]:
        """Return all items for chests and shops on floor"""
        rows: list[dict] = []

        # Chests
        for chest_item in self.chests:
            row: dict = {}
            row['name'] = chest_item
            row['generator'] = generator_names[self.episode_num - 1]
            row['list'] = 'chests'
            row['episode'] = self.episode_num
            row['floor'] = self.floor_num
            rows.append(row)
        
        # Shops
        for shop in self.shops:
            for item in shop.items:
                row: dict = {}
                row['name'] = item
                row['generator'] = generator_names[self.episode_num - 1]
                row['list'] = 'shops'
                row['episode'] = self.episode_num
                row['floor'] = self.floor_num
                row['iter'] = shop.shop_num # To handle grabbing multiple shops from the generators.
                rows.append(row)

        return rows

class EpisodeItems:
    episode_num: int
    floor1: FloorItems
    floor2: FloorItems
    floor3: FloorItems
    floor4: FloorItems
    floor5: FloorItems
    floors: list[FloorItems]

    def __init__(self, num: int):
        self.episode_num = num
        self.floor1 = FloorItems(1, self.episode_num)
        self.floor2 = FloorItems(2, self.episode_num)
        self.floor3 = FloorItems(3, self.episode_num)
        self.floor4 = FloorItems(4, self.episode_num)
        self.floor5 = FloorItems(5, self.episode_num)
        self.floors = [self.floor1, self.floor2, self.floor3, self.floor4, self.floor5]

class GeneratedItems:
    warrior: list[EpisodeItems]
    """list of warrior episodes, each of which has deeper structure"""

    def __init__(self):
        self.warrior = [EpisodeItems(1), EpisodeItems(2), EpisodeItems(3), EpisodeItems(4), EpisodeItems(5), EpisodeItems(6)]
    
    def add_item_if_possible(self, location_id: int, item: str) -> bool:
        """Add item to generation if there is space. Returns true if added, false if not (no space)"""
        # self.warrior[<episode number - 1>].floors[<floor_num - 1>].chests/shops to get string lists or add to them
        # Location ID: <Episode Number><Floor Number><Location Code><Location Count, 2 digits>
        # Episode code is 1-6
        # Floor code is 1-6
        # Location code is 1 = chests, 2 = shops
        loc_str: str = str(location_id)
        episode_num: int = int(loc_str[0])
        floor_num: int = int(loc_str[1])
        location_code: int = int(loc_str[2])

        floor: FloorItems = self.warrior[episode_num - 1].floors[floor_num - 1]

        if location_code == 1:
            # chests
            if floor.are_floor_chests_filled():
                return False
            floor.add_to_chests(item)
        elif location_code == 2:
            # shops
            if floor.are_floor_shops_filled():
                return False
            floor.add_to_shops(item)
        
        return True
    
    def add_item_anywhere(self, item: str) -> bool:
        """Add item to generation if there is space ANYWHERE. Returns true if added, false if not (no space)"""
        
        # Adds in ascending order of episode number, floor number, and location type (chest before shop)
        for episode in self.warrior:
            for floor in episode.floors:
                if not floor.are_floor_chests_filled():
                    floor.add_to_chests(item)
                    return True
                if not floor.are_floor_shops_filled():
                    floor.add_to_shops(item)
                    return True
        
        return False
    
    def fill_with_item(self, item: str) -> bool:
        """Fill all open spaces with given item. Returns true if any items added, false if no items added"""
        ret: bool = False

        for episode in self.warrior:
            for floor in episode.floors:
                while not floor.are_floor_chests_filled():
                    floor.add_to_chests(item)
                    ret = True
                while not floor.are_floor_shops_filled():
                    floor.add_to_shops(item)
                    ret = True
        
        return ret

    def get_items_to_export(self) -> list[dict]:
        """Export a list of dicts, for writing to ap_data.csv"""
        rows: list[dict] = []
        for episode in self.warrior:
            for floor in episode.floors:
                rows.extend(floor.get_floor_items())
        
        return rows

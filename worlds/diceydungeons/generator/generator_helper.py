from ..data.episode_data import *
from ..data.game_data import *

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

    def ap_items_allowed(self, shop_limit: int) -> bool:
        """Returns True if there is room in the shop for more AP items, False if not, based on player Options."""
        return sum("[AP]" in item for item in self.items) < shop_limit

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
    
    def add_to_shops_ap(self, item: str, shop_limit: int):
        for shop in self.shops:
            if not shop.is_shop_filled() and shop.ap_items_allowed(shop_limit):
                shop.add_to_shop(item)
                return
    
    def are_floor_chests_filled(self) -> bool:
        """Are all chests full on floor, for particular episode limits?"""
        floor_limit = warrior_episodes[self.episode_num - 1].floors[self.floor_num - 1].num_chests
        return len(self.chests) >= floor_limit
    
    def are_floor_shops_filled(self) -> bool:
        """Are all shops full on floor, for particular episode limits?"""
        return all([shop.is_shop_filled() for shop in self.shops])
    
    def are_floor_shops_filled_ap(self, shop_limit: int) -> bool:
        """Are all shops full on floor, for particular episode limits AND AP Options?"""
        return all([shop.is_shop_filled() or not shop.ap_items_allowed(shop_limit) for shop in self.shops])
    
    def is_floor_full(self) -> bool:
        """Are all lists full to capacity for floor?"""
        return self.are_floor_chests_filled() and self.are_floor_shops_filled()
    
    def add_item_if_possible(self, item: str) -> bool:
        """Try to add item to our floor. If we added it, return True, else, return False."""
        if self.is_floor_full():
            return False
        
        item_data: dict = item_metadata[item]
        
        if not self.are_floor_chests_filled() and self.episode_num in item_data['episode'] and 'chest' in item_data['location_types']:
            self.add_to_chests(item)
            return True
        
        if not self.are_floor_shops_filled() and self.episode_num in item_data['episode'] and 'shop' in item_data['location_types']:
            self.add_to_shops(item)
            return True
        
        return False


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

    levels: dict[int, str]

    def __init__(self, num: int):
        self.episode_num = num
        self.floor1 = FloorItems(1, self.episode_num)
        self.floor2 = FloorItems(2, self.episode_num)
        self.floor3 = FloorItems(3, self.episode_num)
        self.floor4 = FloorItems(4, self.episode_num)
        self.floor5 = FloorItems(5, self.episode_num)
        self.floors = [self.floor1, self.floor2, self.floor3, self.floor4, self.floor5]

        self.levels = {}
    
    def is_level_filled(self, level: int) -> bool:
        """Check if level in this episode is filled. T/F"""
        return level in self.levels
    
    def add_to_level(self, level: int, item: str):
        self.levels[level] = item
    
    def get_level_items(self) -> list[dict]:
        """Return all items for levels in episode."""
        rows: list[dict] = []

        for level, item in self.levels.items():
            row: dict = {}
            row['name'] = item
            row['generator'] = generator_names[self.episode_num - 1]
            row['list'] = 'levels'
            row['episode'] = self.episode_num
            row['iter'] = level
            rows.append(row)
        
        return rows

class GeneratedItems:
    warrior: list[EpisodeItems]
    """list of warrior episodes, each of which has deeper structure"""
    slot_data: dict
    """Player options information"""

    def __init__(self, slot_data: dict):
        self.warrior = [EpisodeItems(1), EpisodeItems(2), EpisodeItems(3), EpisodeItems(4), EpisodeItems(5), EpisodeItems(6)]
        self.slot_data = slot_data
    
    def add_ap_item_if_possible(self, location_id: int, item: str) -> bool:
        """Add item to generation if there is space. Returns true if added, false if not (no space)"""
        loc_str: str = str(location_id)

        # Branch for floor locations vs level locations
        # Currently hardcoded but will need to change if we shift location IDs
        if location_id < 10000:
            # Level up location
            # Location name: <Episode> - Level <level>
            # ID: 10<Episode Number><Level Number>
            episode_num: int = int(loc_str[2])
            level_num: int = int(loc_str[3])

            episode: EpisodeItems = self.warrior[episode_num - 1]
            if episode.is_level_filled(level_num):
                return False
            episode.add_to_level(level_num, f"Equipment:{item}")

        else:
            # self.warrior[<episode number - 1>].floors[<floor_num - 1>].chests/shops to get string lists or add to them
            # Location ID: <Episode Number><Floor Number><Location Code><Location Count, 2 digits>
            # Episode code is 1-6
            # Floor code is 1-6
            # Location code is 1 = chests, 2 = shops
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
                shop_limit: int = self.slot_data["checks_per_shop"]
                if floor.are_floor_shops_filled_ap(shop_limit):
                    return False
                floor.add_to_shops_ap(item, shop_limit)
        
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
    
    def add_item_to_episodes(self, item: str):
        """Add item to generation up to once for each episode it can be added to."""
        for episode in self.warrior:
            # Add item to the episode in earliest floor/location it can.
            # It doesn't matter if episodes are samey, because will regenerate before player could play another one.
            for floor in episode.floors:
                # Try to add. If added, go to next episode
                if floor.add_item_if_possible(item):
                    break
    
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
            rows.extend(episode.get_level_items())
            for floor in episode.floors:
                rows.extend(floor.get_floor_items())
        
        return rows

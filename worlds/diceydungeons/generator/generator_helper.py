import random

from ..data.episode_data import *
from ..data.game_data import *

generator_names: dict[list[str]] = {
    1: ['warrior_one', 'warrior_two', 'warrior_three', 'warrior_four', 'warrior_five', 'warrior_six'],
    2: ['thief_one', 'thief_two', 'thief_three', 'thief_four', 'thief_five', 'thief_six'],
    3: ['robot_one', 'robot_two', 'robot_three', 'robot_four', 'robot_five', 'robot_six'],
    4: ['inventor_one', 'inventor_two', 'inventor_three', 'inventor_four', 'inventor_five', 'inventor_six'],
}
"""Dict of generator names lists, indexed by character code"""

character_episodes: dict[int, list[EpisodeData]] = {
    1: warrior_episodes,
    2: thief_episodes,
    3: robot_episodes,
    4: inventor_episodes,
}
"""Mapping of character code to data for their episodes"""

item_metadata_mapping: dict[int, str] = {
    1: 'warrior',
    2: 'thief',
    3: 'robot',
    4: 'inventor',
}
"""Mapping of character code to item_metadata field we need to examine for availability"""

class LevelItems:
    character_num: int
    episode_num: int
    level_num: int
    items: list[str]

    def __init__(self, num: int, episode: int, character: int):
        self.level_num = num
        self.episode_num = episode
        self.character_num = character
        self.items = []
    
    def is_level_full(self) -> bool:
        return len(self.items) > 0
    
    def add_to_level(self, item: str):
        self.items.append(item)
    
    def add_to_level_list(self, items: list[str], replace_upgrade: bool):
        items_to_add = ["Copy" if item == "Upgrade" and replace_upgrade else item for item in items]
        self.items.extend(items_to_add)

class TradeItems:
    trade_num: int
    floor_num: int
    episode_num: int
    character_num: int
    items: list[str]

    def __init__(self, num: int, episode: int, floor: int, character: int):
        self.trade_num = num
        self.episode_num = episode
        self.floor_num = floor
        self.character_num = character
        self.items = []
    
    def add_to_trade(self, item: str):
        self.items.append(item)
    
    def is_trade_filled(self) -> bool:
        # Trade limit is always 1. I think.
        return len(self.items) >= 1

class ShopItems:
    shop_num: int
    floor_num: int
    episode_num: int
    character_num: int
    items: list[str]

    def __init__(self, num: int, episode: int, floor: int, character: int):
        self.shop_num = num
        self.episode_num = episode
        self.floor_num = floor
        self.character_num = character
        self.items = []
    
    def add_to_shop(self, item: str):
        self.items.append(item)
    
    def is_shop_filled(self) -> bool:
        shop_limit = character_episodes[self.character_num][self.episode_num - 1].floors[self.floor_num - 1].num_shop_slots
        return len(self.items) >= shop_limit

    def ap_items_allowed(self, shop_limit: int) -> bool:
        """Returns True if there is room in the shop for more AP items, False if not, based on player Options."""
        return sum("[AP]" in item for item in self.items) < shop_limit

class FloorItems:
    character_num: int
    floor_num: int
    episode_num: int
    chests: list[str]
    shops: list[ShopItems]
    trades: list[TradeItems]

    def __init__(self, num: int, episode: int, character: int):
        self.floor_num = num
        self.episode_num = episode
        self.character_num = character
        self.chests = []
        self.shops = [ShopItems(i + 1, self.episode_num, self.floor_num, self.character_num) for i in range(character_episodes[character][self.episode_num - 1].floors[self.floor_num - 1].num_shops)]
        self.trades = [TradeItems(i + 1, self.episode_num, self.floor_num, self.character_num) for i in range(character_episodes[character][self.episode_num - 1].floors[self.floor_num - 1].num_trades)]
    
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
    
    def add_to_trades(self, item: str):
        for trade in self.trades:
            if not trade.is_trade_filled():
                trade.add_to_trade(item)
                return
    
    def are_floor_chests_filled(self) -> bool:
        """Are all chests full on floor, for particular episode limits?"""
        floor_limit = character_episodes[self.character_num][self.episode_num - 1].floors[self.floor_num - 1].num_chests
        return len(self.chests) >= floor_limit
    
    def are_floor_shops_filled(self) -> bool:
        """Are all shops full on floor, for particular episode limits?"""
        return all([shop.is_shop_filled() for shop in self.shops])
    
    def are_floor_shops_filled_ap(self, shop_limit: int) -> bool:
        """Are all shops full on floor, for particular episode limits AND AP Options?"""
        return all([shop.is_shop_filled() or not shop.ap_items_allowed(shop_limit) for shop in self.shops])

    def are_floor_trades_filled(self) -> bool:
        """Are all trades full on floor, for particular episode limits?"""
        return all([trade.is_trade_filled() for trade in self.trades])
    
    def is_floor_full(self) -> bool:
        """Are all lists full to capacity for floor?"""
        return self.are_floor_chests_filled() and self.are_floor_shops_filled() and self.are_floor_trades_filled()
    
    def add_item_if_possible(self, item: str, allow_anywhere: bool) -> bool:
        """Try to add item to our floor. If we added it, return True, else, return False."""
        if self.is_floor_full():
            return False
        
        if not allow_anywhere:
            item_data: dict = item_metadata[item][item_metadata_mapping[self.character_num]]
            
            if not self.are_floor_chests_filled() and self.episode_num in item_data['episode'] and 'chest' in item_data['location_types']:
                self.add_to_chests(item)
                return True
            
            if not self.are_floor_shops_filled() and self.episode_num in item_data['episode'] and 'shop' in item_data['location_types']:
                self.add_to_shops(item)
                return True
            
            if not self.are_floor_trades_filled() and self.episode_num in item_data['episode'] and 'trade' in item_data['location_types']:
                self.add_to_trades(item)
                return True
        else:
            if not self.are_floor_chests_filled():
                self.add_to_chests(item)
                return True
            
            if not self.are_floor_shops_filled():
                self.add_to_shops(item)
                return True
            
            if not self.are_floor_trades_filled():
                self.add_to_trades(item)
                return True
        
        return False


    def get_floor_items(self) -> list[dict]:
        """Return all items for chests and shops on floor"""
        rows: list[dict] = []

        # Chests
        for chest_item in self.chests:
            row: dict = {}
            row['name'] = chest_item
            row['generator'] = generator_names[self.character_num][self.episode_num - 1]
            row['list'] = 'chests'
            row['episode'] = self.episode_num
            row['floor'] = self.floor_num
            rows.append(row)
        
        # Shops
        for shop in self.shops:
            for item in shop.items:
                row: dict = {}
                row['name'] = item
                row['generator'] = generator_names[self.character_num][self.episode_num - 1]
                row['list'] = 'shops'
                row['episode'] = self.episode_num
                row['floor'] = self.floor_num
                row['iter'] = shop.shop_num # To handle grabbing multiple shops from the generators.
                rows.append(row)
        
        # Trades
        for trade in self.trades:
            for item in trade.items:
                row: dict = {}
                row['name'] = item
                row['generator'] = generator_names[self.character_num][self.episode_num - 1]
                row['list'] = 'trades'
                row['episode'] = self.episode_num
                row['floor'] = self.floor_num
                row['iter'] = trade.trade_num # To handle grabbing multiple trades from the generators, if that ever happens.
                rows.append(row)

        return rows

class EpisodeItems:
    character_num: int
    episode_num: int
    floor1: FloorItems
    floor2: FloorItems
    floor3: FloorItems
    floor4: FloorItems
    floor5: FloorItems
    floors: list[FloorItems]

    levels: list[LevelItems]

    def __init__(self, num: int, character_num: int):
        self.episode_num = num
        self.character_num = character_num
        self.floor1 = FloorItems(1, self.episode_num, self.character_num)
        self.floor2 = FloorItems(2, self.episode_num, self.character_num)
        self.floor3 = FloorItems(3, self.episode_num, self.character_num)
        self.floor4 = FloorItems(4, self.episode_num, self.character_num)
        self.floor5 = FloorItems(5, self.episode_num, self.character_num)
        self.floors = [self.floor1, self.floor2, self.floor3, self.floor4, self.floor5]

        self.levels =   [
                            LevelItems(2, self.episode_num, self.character_num),
                            LevelItems(3, self.episode_num, self.character_num),
                            LevelItems(4, self.episode_num, self.character_num),
                            LevelItems(5, self.episode_num, self.character_num),
                            LevelItems(6, self.episode_num, self.character_num)
                        ]
    
    def item_allowed_for_levels(self, item: str, allow_anywhere: bool) -> bool:
        """Check if item is allowed in levels for this episode."""
        item_data: dict = item_metadata[item][item_metadata_mapping[self.character_num]]
        return allow_anywhere or (self.episode_num in item_data['episode'] and 'chest' in item_data['location_types'])

    def is_level_filled(self, level: int) -> bool:
        """Check if level in this episode is filled. T/F"""
        return self.levels[level - 2].is_level_full()
    
    def add_to_level(self, level: int, item: str):
        self.levels[level - 2].add_to_level(item)
    
    def get_level_items(self) -> list[dict]:
        """Return all items for levels in episode."""
        rows: list[dict] = []

        for level in self.levels:
            for item in level.items:
                row: dict = {}
                row['name'] = item
                row['generator'] = generator_names[self.character_num][self.episode_num - 1]
                row['list'] = 'levels'
                row['episode'] = self.episode_num
                row['iter'] = level.level_num
                rows.append(row)
        
        return rows

class CharacterItems:
    id: int
    """id of Character. 1 == Warrior, 2 = Thief, 3 = Robot, 4 = Inventor"""
    episodes: list[EpisodeItems]
    """list of episodes, each of which has deeper structure"""

    def __init__(self, id: int):
        self.id = id
        self.episodes = [EpisodeItems(1, id), EpisodeItems(2, id), EpisodeItems(3, id), EpisodeItems(4, id), EpisodeItems(5, id), EpisodeItems(6, id)]


class GeneratedItems:
    warrior: CharacterItems
    """Warrior episodes container"""
    thief: CharacterItems
    """Thief episodes container"""
    robot: CharacterItems
    """Robot episodes container"""
    inventor: CharacterItems
    """Inventor episodes container"""
    characters_playing: list[CharacterItems]
    """List of characters we are playing, based on options."""
    all_characters: list[CharacterItems]
    """All characters, for when looking them up this way is easier."""
    slot_data: dict
    """Player options information"""
    level_ups: dict[dict[str, int]]
    """Level up items we've received for each character for each episode. Outer key is character, inner key is episode, value is count."""
    dice_received: int
    """Number of dice player has received, if playing with Split Dice."""

    def __init__(self, slot_data: dict, level_ups: dict[str, int], dice_received: int):
        self.warrior = CharacterItems(1)
        self.thief = CharacterItems(2)
        self.robot = CharacterItems(3)
        self.inventor = CharacterItems(4)
        self.all_characters = [self.warrior, self.thief, self.robot, self.inventor]
        self.slot_data = slot_data
        self.level_ups = level_ups
        self.dice_received = dice_received

        self.characters_playing = []

        if slot_data['character'] + 1 == 1:
            self.characters_playing.append(self.warrior)
        elif slot_data['character'] + 1 == 2:
            self.characters_playing.append(self.thief)
        elif slot_data['character'] + 1 == 3:
            self.characters_playing.append(self.robot)
        elif slot_data['character'] + 1 == 4:
            self.characters_playing.append(self.inventor)
        else:
            # Fallback
            self.characters_playing.append(self.warrior)
    
    def prefill_floor_5_shops(self):
        """
        Prefill floor 5 shops with an upgrade and a heal.
        """
        for character in self.characters_playing:
            for episode in character.episodes:
                floor_5 = episode.floors[4]
                floor_5.add_to_shops("health")
                if character.id == 1:
                    # Only add upgrade for Warrior
                    floor_5.add_to_shops("upgrade")
    
    def add_ap_item_if_possible(self, location_id: int, item: str) -> bool:
        """Add item to generation if there is space. Returns true if added, false if not (no space)"""
        loc_str: str = str(location_id)

        # Branch for floor locations vs level locations
        # Currently hardcoded but will need to change if we shift location IDs
        if location_id < 10000:
            # Level up location
            # Location name: <Episode> - Level <level>
            # ID: 1<Character Number><Episode Number><Level Number>
            character_num: int = int(loc_str[1])
            episode_num: int = int(loc_str[2])
            level_num: int = int(loc_str[3])

            character = self.all_characters[character_num - 1]
            episode: EpisodeItems = character.episodes[episode_num - 1]
            if episode.is_level_filled(level_num):
                return False
            episode.add_to_level(level_num, f"Equipment:{item}")

        else:
            # self.all_characters[<character code>].episodes[<episode number - 1>].floors[<floor_num - 1>].chests/shops to get string lists or add to them
            # Location ID: <Character Code><Episode Number><Floor Number><Location Code><Location Count, 2 digits>
            # Character code is 1 = Warrior, 2 = Thief, 3 = Robot, 4 = Inventor
            # Episode code is 1-6
            # Floor code is 1-6
            # Location code is 1 = chests, 2 = shops, 5 = trades
            character_code: int = int(loc_str[0])
            episode_num: int = int(loc_str[1])
            floor_num: int = int(loc_str[2])
            location_code: int = int(loc_str[3])

            floor: FloorItems = self.all_characters[character_code - 1].episodes[episode_num - 1].floors[floor_num - 1]

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
            elif location_code == 5:
                # trades
                if floor.are_floor_trades_filled():
                    return False
                floor.add_to_trades(item)
        
        return True
    
    def prefill_level_locations(self):
        """Prefill level locations for any guaranteed items."""
        for character in self.characters_playing:
            for episode in character.episodes:
                max_level = self.level_ups[character.id][character_episodes[character.id][episode.episode_num - 1].name] + 1
                for level in range(2, 7):
                    # Want to fill in an item if:
                    # 1. If there's a defined prefill item
                    # 2. We have unlocked enough level ups for this episode to cover it
                    # 3. It's not already filled, somehow
                    # 4. If dice, and Split dice is on, we need to be able to add it
                    if level in character_episodes[character.id][episode.episode_num - 1].level_items and level <= max_level and not episode.is_level_filled(level):
                        # Consider using a more legible condition for Split Dice in the future
                        if self.slot_data["split_dice"] and level % 2 == 0 and level // 2 > self.dice_received:
                            continue
                        episode.add_to_level(level, character_episodes[character.id][episode.episode_num - 1].level_items[level])
    
    def assign_standard_level_ups(self):
        """For Levelsanity = off, give normal level ups"""
        upgrade_all_equipment = self.slot_data["upgrade_equipment"] == 2
        for character in self.characters_playing:
            for episode in character.episodes:
                for level in episode.levels:
                    # Consider using a more legible condition for Split Dice in the future
                    if self.slot_data["split_dice"] and level.level_num % 2 == 0 and level.level_num // 2 > self.dice_received:
                        continue
                    level.add_to_level_list(character_episodes[character.id][episode.episode_num - 1].standard_level_items[level.level_num], upgrade_all_equipment)
    
    def add_item_to_episodes(self, item: str):
        """Add item to generation up to once for each episode it can be added to."""
        for character in self.characters_playing:
            for episode in character.episodes:
                # Add item to the episode in earliest level/floor/location it can.
                # It doesn't matter if episodes are samey, because will regenerate before player could play another one.
                max_level = self.level_ups[character.id][character_episodes[character.id][episode.episode_num - 1].name] + 1
                filled: bool = False
                allow_anywhere: bool = self.slot_data["equipment_availability"] == 1

                for level in range(2, 7):
                    if level <= max_level and not episode.is_level_filled(level) and episode.item_allowed_for_levels(item, allow_anywhere):
                        episode.add_to_level(level, f"Equipment:{item}")
                        filled = True
                        break
                    
                if not filled:
                    for floor in episode.floors:
                        # Try to add. If added, go to next episode
                        if floor.add_item_if_possible(item, allow_anywhere):
                            break
    
    def fill_with_random_items(self, items: list[str]) -> bool:
        """Fill all open spaces randomly from given item list. Returns true if any items added, false if no items added"""
        ret: bool = False

        for character in self.characters_playing:
            for episode in character.episodes:
                for level in range(2, 7):
                    if not episode.is_level_filled(level):
                        episode.add_to_level(level, f"Equipment:{random.choice(items)}")
                        ret = True

                for floor in episode.floors:
                    while not floor.are_floor_chests_filled():
                        floor.add_to_chests(random.choice(items))
                        ret = True
                    while not floor.are_floor_shops_filled():
                        floor.add_to_shops(random.choice(items))
                        ret = True
                    while not floor.are_floor_trades_filled():
                        floor.add_to_trades(random.choice(items))
                        ret = True
        
        return ret

    def get_items_to_export(self) -> list[dict]:
        """Export a list of dicts, for writing to ap_data.csv"""
        rows: list[dict] = []
        for character in self.characters_playing:
            for episode in character.episodes:
                rows.extend(episode.get_level_items())
                for floor in episode.floors:
                    rows.extend(floor.get_floor_items())
        
        return rows

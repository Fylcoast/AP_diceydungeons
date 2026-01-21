import os
import csv

from NetUtils import NetworkItem

from worlds.diceydungeons.data.episode_data import *
import worlds.diceydungeons.generator.generator_helper as gen_helper
    

ap_data_column_list: list[str] = [
    'name',
    'generator',
    'list',
    'episode',
    'floor',
    'iter'

]
"""Column list for export csv"""

class DiceyDungeonsAPItemGenerator:
    """Generator for telling game which items to pick up where."""
    output_file: str = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Dicey Dungeons\\mods\\diceyap\\data\\text\\scripts\\diceyap\\ap_data.csv"
    """Path and name of our output file, where our generators will read our items from."""
    locations: dict[int, NetworkItem]
    """Useless? - All fillable locations in our game, and the item they are filled with."""
    checked_locations: set[int]
    """All location_id's which have already been checked, according to the server."""
    items_received: list[str]
    """All items which we have been given from our base game, according to the server."""
    ap_item_mapping: dict[int, str]
    """ap item names mapping with loc_id --> string to be put into csv"""


    def __init__(self, ap_item_names: dict[int, str], locations_info: dict[int, NetworkItem], checked_locations: set[int], items_received: list[NetworkItem]):
        self.ap_item_mapping = ap_item_names
        self.locations = locations_info
        self.checked_locations = checked_locations
        self.items_received = items_received
    
    def generate(self):
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=ap_data_column_list)
            writer.writeheader()
            #TODO: add in our own items, and shuffle lists so they don't get them all just what they need based on episode_data.py
            # rows = []
            # for loc_id, net_item in self.locations.items(): 
            #     # Don't add it if we've already picked it up!
            #     if loc_id in self.checked_locations:
            #         continue
            #     # Parse loc_id to figure out where in the game they should be.
            #     loc_str: str = str(loc_id)
            #     # First digit is episode number 1-6
            #     episode = loc_str[0]
            #     # Second digit is floor number, 1-5
            #     floor = loc_str[1]
            #     # Third digit is location code
            #     item_list = ['chests', 'shops', 'heals', 'upgrades', 'trades'][int(loc_str[2]) - 1]
            #     # Final 2 digits are location count. Only used for multiple shops on a floor.
            #     item_count = int(loc_str[3:])
            #     iter = (item_count - 1) // 3 + 1 if item_list == 'shops' else 1 # 3 items per shop
            #     # Generator for now is defined based on episode only
            #     generator = ['warrior_one', 'warrior_two', 'warrior_three', 'warrior_four', 'warrior_five', 'warrior_six'][int(episode) - 1]

            #     row: dict = {}
            #     row['name'] = self.ap_item_mapping[loc_id]
            #     row['generator'] = generator
            #     row['list'] = item_list
            #     row['episode'] = episode
            #     row['floor'] = floor
            #     row['iter'] = iter
            #     rows.append(row)

            generator = gen_helper.GeneratedItems()
            # Add remaining AP items
            for loc_id, item_str in self.ap_item_mapping.items():
                if loc_id in self.checked_locations:
                    continue
                generator.add_item_if_possible(loc_id, item_str)
            
            # Add real items to fill
            for item in self.items_received:
                generator.add_item_anywhere(item)
            
            # Fill up rest with filler
            generator.fill_with_item("Dice Shard")

            # Export items
            rows: list[dict] = generator.get_items_to_export()
            
            writer.writerows(rows)

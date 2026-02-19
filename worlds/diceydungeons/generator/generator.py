import os
import csv

from NetUtils import NetworkItem

from ..data.episode_data import *
from . import generator_helper as gen_helper


filler_items: list[str] = ["Frog's Broadsword", "Audrey's Dumbbell", "Rotten Apple's Pet Worm", "Wizard's Spellbook", "Dice Shard"]    

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
    output_file: str
    """Path and name of our output file, where our generators will read our items from."""
    locations: dict[int, NetworkItem]
    """Useless? - All fillable locations in our game, and the item they are filled with."""
    checked_locations: set[int]
    """All location_id's which have already been checked, according to the server."""
    items_received: list[str]
    """All items which we have been given from our base game, according to the server."""
    ap_item_mapping: dict[int, str]
    """ap item names mapping with loc_id --> string to be put into csv"""
    slot_data: dict
    """Player options information"""
    level_ups: dict[str, int]
    """Level up items we've received for each episode. Key is episode, value is count."""


    def __init__(self, install_location: str, slot_data: dict, ap_item_names: dict[int, str], locations_info: dict[int, NetworkItem], checked_locations: set[int], items_received: list[NetworkItem], level_ups: dict[str, int]):
        self.slot_data = slot_data
        self.ap_item_mapping = ap_item_names
        self.locations = locations_info
        self.checked_locations = checked_locations
        self.items_received = items_received
        self.level_ups = level_ups
        self.output_file = os.path.join(install_location, "mods", "diceyap", "data", "text", "scripts", "diceyap", "ap_data.csv")
    
    def generate(self):
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=ap_data_column_list)
            writer.writeheader()

            generator = gen_helper.GeneratedItems(self.slot_data, self.level_ups)
            
            if self.slot_data["floor_5_shop_selection"] == 0:
                # Ensure floor 5 shops have upgrade and health
                generator.prefill_floor_5_shops()

            # Add remaining AP items
            for loc_id, item_str in self.ap_item_mapping.items():
                if loc_id in self.checked_locations:
                    continue
                generator.add_ap_item_if_possible(loc_id, item_str)
            
            if self.slot_data["levelsanity"]:
                # Prefill level locations, if earned.
                generator.prefill_level_locations()
            else:
                # Give normal level ups
                generator.assign_standard_level_ups()
            
            # Add real items to fill, up to 1 per episode
            for item in self.items_received:
                generator.add_item_to_episodes(item)
            
            # Fill up rest with filler
            generator.fill_with_random_items(filler_items)

            # Export items
            rows: list[dict] = generator.get_items_to_export()
            
            writer.writerows(rows)

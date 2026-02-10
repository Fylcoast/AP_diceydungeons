import os
from typing import TYPE_CHECKING, Optional
import csv
from collections import OrderedDict
import zipfile
import io
from importlib.resources import files
import shutil

from BaseClasses import Location, Item, ItemClassification

if TYPE_CHECKING:
    from . import DiceyDungeonsWorld

default_item_info: OrderedDict = {
    'Name': '',
    'Description': '',
    'Size': '1',
    'Script: On Execute': '',
    'Gadget': '',
    'Slots': '',
    'NEED TOTAL?': '',
    'Colour': 'GRAY',
    'Upgrade': '',
    'Weaken': '',
    'Alternate Status Trigger':	'',
    'SFX': 'none',
    'Uses?': '0',
    'Cast Backwards?': 'NO',
    'Single use?': 'NO',
    'Tags': 'excludefromrandomlists|cannotsteal|skillcard',
    'Witch Spell': '',
    'Script: Before Combat': '',
    'Script: After Combat': '',
    'Script: Before Start Turn': '',
    'Script: On Start Turn': '',
    'Script: On any equipment use': '',
    'Script: On any countdown reduce': '',
    'Script: End Turn': '',
    'Script: Before execute': '',
    'Script: On Snap': '',
    'Script: On Fury': '',
    'Script: On Dodge': ''
}

equipment_field_list: list[str] = default_item_info.keys()

dice_shard: dict = {
    'Name': 'Dice Shard',
    'Description': 'Merely a fragment of a die.',
    'Size': '1',
    'Script: On Execute': '',
    'Gadget': '',
    'Slots': '',
    'NEED TOTAL?': '',
    'Colour': 'GRAY',
    'Upgrade': '',
    'Weaken': '',
    'Alternate Status Trigger':	'',
    'SFX': 'none',
    'Uses?': '0',
    'Cast Backwards?': 'NO',
    'Single use?': 'NO',
    'Tags': 'excludefromrandomlists|cannotsteal|skillcard',
    'Witch Spell': '',
    'Script: Before Combat': '',
    'Script: After Combat': '',
    'Script: Before Start Turn': '',
    'Script: On Start Turn': '',
    'Script: On any equipment use': '',
    'Script: On any countdown reduce': '',
    'Script: End Turn': '',
    'Script: Before execute': '',
    'Script: On Snap': '',
    'Script: On Fury': '',
    'Script: On Dodge': ''
}

def item_flag_mapping(flags: int) -> ItemClassification:
    if flags & 0b001:  # advancement
        return ItemClassification.progression
    elif flags & 0b010:  # useful
        return ItemClassification.useful
    elif flags & 0b100:  # trap
        return ItemClassification.trap
    else:
        return ItemClassification.filler

item_classification_text_mapping: dict = {
    ItemClassification.filler: 'They probably don''t|need this...',
    ItemClassification.progression: 'They could probably|use this!',
    ItemClassification.trap: 'They would likely|rather not have this!',
    ItemClassification.useful: 'They could probably|use this!',
    ItemClassification.deprioritized: 'They probably don''t|need this...',
    ItemClassification.progression_deprioritized: 'They probably don''t|need this...',
    ItemClassification.progression_deprioritized_skip_balancing: 'They probably don''t|need this...',
    ItemClassification.progression_skip_balancing: 'They might need this.',
    ItemClassification.skip_balancing: 'This might be useful.'
}

class DiceyDungeonsClientModGenerator():
    game_path: str
    """Install path for Dicey Dungeons root folder"""
    equipment: list[tuple[str, str, int]]
    """List of items from multiworld we want in our equipment.csv, with player name and flags for usefulness"""
    mod_name: str
    """Name of the mod (probably 'diceyap')"""

    def __init__(self, game_path: str, equipment: list[tuple[str, str, int]]):
        self.game_path = game_path
        self.equipment = equipment
        self.mod_name = 'diceyap'
    
    def get_equipment_row(self, item: tuple[str, str, int]):
        owner = item[1]

        row = default_item_info.copy()
        row['Name'] = item[0]
        row['Description'] = f"Owner: {owner}| |{item_classification_text_mapping[item_flag_mapping(item[2])]}"

        return row
    
    def _write_package_files_to_dir(self, base_path, mod_name: str, dest_dir: str):
        """Recursively write files from package resources to a destination directory"""
        def walk_files(path, prefix=''):
            for item in path.iterdir():
                if item.is_file():
                    content = item.read_bytes()
                    arcname = f'{prefix}/{item.name}'.lstrip('/')
                    out_path = os.path.join(dest_dir, arcname)
                    os.makedirs(os.path.dirname(out_path), exist_ok=True)
                    with open(out_path, 'wb') as f:
                        f.write(content)
                elif item.is_dir():
                    walk_files(item, f'{prefix}/{item.name}')
        
        walk_files(base_path, mod_name)
    
    def _generate_equipment_csv(self, path: str):
        """Generate equipment.csv content as a string."""
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=equipment_field_list)
            writer.writeheader()
            rows = []
            for item in self.equipment:
                rows.append(self.get_equipment_row(item))
            # Dice shard, for our filler.
            rows.append(dice_shard)
            writer.writerows(rows)
        
    
    def generate(self):
        base_files = files(__package__).joinpath('data', 'mod_data', self.mod_name)
        dest_dir = os.path.join(self.game_path, "mods")

        # Clear out previous mod installation if exists
        if os.path.exists(os.path.join(dest_dir, self.mod_name)):
            shutil.rmtree(os.path.join(dest_dir, self.mod_name))
        
        # Copy base files to Dicey Dungeons install dir in mods folder
        self._write_package_files_to_dir(base_files, self.mod_name, dest_dir)

        # Make new equipment file
        if self.equipment:
            equipment_path = os.path.join(dest_dir, self.mod_name, '_append', 'data', 'text')
            if not os.path.exists(equipment_path):
                os.makedirs(equipment_path)
            equipment_path = os.path.join(equipment_path, 'equipment.csv')
            self._generate_equipment_csv(equipment_path)

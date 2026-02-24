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

# Insta-kill for testing
murder_spell: dict = {
    'Name': 'Murder Spell',
    'Description': 'DEATH',
    'Size': '1',
    'Script: On Execute': 'attack(999);',
    'Gadget': 'Refrigerator',
    'Slots': 'NORMAL',
    'NEED TOTAL?': '',
    'Colour': 'BRIGHTCYAN',
    'Upgrade': '',
    'Weaken': 'change_power',
    'Alternate Status Trigger':	'',
    'SFX': 'none',
    'Uses?': '0',
    'Cast Backwards?': 'NO',
    'Single use?': 'NO',
    'Tags': '',
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

filler_items: dict[str, str] = {
    "Frog's Broadsword": "Too big to wield!", 
    "Audrey's Dumbbell": "Too slippery to use!", 
    "Rotten Apple's Pet Worm": "Cuddly!", 
    "Wizard's Spellbook": "Unfortunately[;] the text is|in an arcane script|you cannot read."
}
"""Dict (name -> description) of filler items to populate into equipment"""

def get_filler_items() -> list[dict]:
    ret: list[dict] = []
    for name, desc in filler_items.items():
        item = default_item_info.copy()
        item['Name'] = name
        item['Description'] = desc
        ret.append(item)
    
    return ret

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
    slot_data: dict
    """Player options information"""

    def __init__(self, game_path: str, equipment: list[tuple[str, str, int]], slot_data: dict):
        self.game_path = game_path
        self.equipment = equipment
        self.slot_data = slot_data
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
    
    def _generate_progresssettings_file(self, path: str, save_name: str):
        """Generate progresssettings.txt content"""
        with open(path, 'w', newline='') as f:
            f.write(save_name)
    
    def _generate_equipment_csv(self, path: str):
        """Generate equipment.csv content as a string."""
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=equipment_field_list)
            writer.writeheader()
            rows = []
            for item in self.equipment:
                rows.append(self.get_equipment_row(item))
            # Testing spell
            rows.append(murder_spell)
            # Filler items.
            rows.extend(get_filler_items())
            writer.writerows(rows)
        
    
    def generate(self):
        common_files = files(__package__).joinpath('data', 'common_mod_data', self.mod_name)
        dest_dir = os.path.join(self.game_path, "mods")

        # Clear out previous mod installation if exists
        if os.path.exists(os.path.join(dest_dir, self.mod_name)):
            shutil.rmtree(os.path.join(dest_dir, self.mod_name))
        
        # Copy base files to Dicey Dungeons install dir in mods folder
        self._write_package_files_to_dir(common_files, self.mod_name, dest_dir)

        # Conditionally populate other files, based on Options selected.
        if self.slot_data['episode_progression'] == 0:
            # Vanilla progression
            vanilla_files = files(__package__).joinpath('data', 'vanilla_progression_data', self.mod_name)
            self._write_package_files_to_dir(vanilla_files, self.mod_name, dest_dir)
        else:
            # Open world
            open_world_files = files(__package__).joinpath('data', 'open_world_data', self.mod_name)
            self._write_package_files_to_dir(open_world_files, self.mod_name, dest_dir)

        if self.slot_data['skip_cutscenes']:
            skip_cutscenes_files = files(__package__).joinpath('data', 'skip_cutscenes_data', self.mod_name)
            self._write_package_files_to_dir(skip_cutscenes_files, self.mod_name, dest_dir)

        # Conditionally give save file info
        # If episode_progression is vanilla (0), need save file to force progression logic
        if self.slot_data['episode_progression'] == 0:
            save_path = os.path.join(dest_dir, self.mod_name, 'data', 'text', 'progresssettings.txt')
            self._generate_progresssettings_file(save_path, self.slot_data['save_name'])


        # Make new equipment file
        if self.equipment:
            equipment_path = os.path.join(dest_dir, self.mod_name, '_append', 'data', 'text', 'equipment.csv')
            self._generate_equipment_csv(equipment_path)


import os
from typing import TYPE_CHECKING, Optional
import csv
from collections import OrderedDict
import zipfile
import io
from importlib.resources import files
import shutil

from BaseClasses import Location, Item, ItemClassification

from .data.episode_data import *

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
            # Filler items.
            rows.extend(get_filler_items())
            writer.writerows(rows)
    
    def replace_text_in_column(self, path: str, col: str, old: str, new: str):
        """Replace an old string with a new string in chosen column of csv at path. 
        Does nothing if new string already present."""
        with open(path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
        
        for row in rows:
            if new not in row[col]:
                row[col] = row[col].replace(old, new)
        
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows) 
    
    def modify_episode_start_script(self, path: str, character: str, level: int, filter: str, add: bool = False):
        """Modify start script to either add given string or remove given string."""
        with open(path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
        
        for row in rows:
            if row["Character"] == character and int(row["Level"]) == level:
                if add:
                    if filter not in row["Script: Start Game"]:
                        row["Script: Start Game"] = row["Script: Start Game"] + filter
                else:
                    row["Script: Start Game"] = row["Script: Start Game"].replace(filter, "")
        
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows) 
    
    def add_to_all_start_scripts(self, path: str, text_to_add: str):
        """Modify start script to either add given string or remove given string."""
        with open(path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
        
        for row in rows:
            if text_to_add not in row["Script: Start Game"]:
                row["Script: Start Game"] = row["Script: Start Game"] + text_to_add
        
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows) 
    
    def upgrade_starting_equipment(self, path: str):
        """Upgrade all starting equipment for all episodes"""
        with open(path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
        
        for row in rows:
            if row["Equipment"]:
                starting_equipment = row["Equipment"].split("|")
                upgraded_starting_equipment = list(map(lambda equip : f"{equip}+" if "+" not in equip else equip, starting_equipment))
                row["Equipment"] = "|".join(upgraded_starting_equipment)
        
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
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
            if self.slot_data['character'] == 0:
                # Warrior
                vanilla_files = files(__package__).joinpath('data', 'warrior_vanilla_progression_data', self.mod_name)
                self._write_package_files_to_dir(vanilla_files, self.mod_name, dest_dir)
            else:
                # Thief
                vanilla_files = files(__package__).joinpath('data', 'thief_vanilla_progression_data', self.mod_name)
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
            equipment_path = os.path.join(dest_dir, self.mod_name, '_append', 'data', 'text')
            if not os.path.exists(equipment_path):
                os.makedirs(equipment_path)
            equipment_path = os.path.join(equipment_path, 'equipment.csv')
            self._generate_equipment_csv(equipment_path)
        
        # Modify episodes.csv based on options (QoL options)
        episodes_path = os.path.join(dest_dir, self.mod_name, 'data', 'text', 'episodes.csv')

        # Warrior Episode 2 - Disable Curse
        if 'warrior_2_disable_curse' in self.slot_data and self.slot_data['warrior_2_disable_curse']:
            for removal in warrior_2_start_game_curse_removals:
                self.modify_episode_start_script(episodes_path, 'Warrior', 2, removal)

        # Warrior Episode 3 - Prevent HP Loss
        if 'warrior_3_remove_hp_decrease_on_level' in self.slot_data and self.slot_data['warrior_3_remove_hp_decrease_on_level']:
            for removal in warrior_3_start_game_hp_loss_removals:
                self.modify_episode_start_script(episodes_path, 'Warrior', 3, removal)
        
        # Upgrade Equipment

        # Upgrade starting equipment
        if 'upgrade_equipment' in self.slot_data and self.slot_data['upgrade_equipment'] >= 1:
            self.upgrade_starting_equipment(episodes_path)
            # Make sure to include episode 6
            upgraded_initial_equipment_files = files(__package__).joinpath('data', 'upgrade_starting_equipment', self.mod_name)
            self._write_package_files_to_dir(upgraded_initial_equipment_files, self.mod_name, dest_dir)

        # Upgrade all equipment
        if 'upgrade_equipment' in self.slot_data and self.slot_data['upgrade_equipment'] == 2:
            for addition in start_game_upgrade_all_equipment_additions:
                self.add_to_all_start_scripts(episodes_path, addition)
            # Also handle level ups.
            self.replace_text_in_column(episodes_path, 'Script: Define Level Up Rewards', 'leveluprewards', 'upgraded_leveluprewards')


import os
import shutil
from typing import TYPE_CHECKING, Optional
import csv
from collections import OrderedDict

from BaseClasses import Location, Item, ItemClassification

#TODO: List of files we need to include in output:
# DONE - _append/data/text/equipment.csv - dynamic 
# data/text/episodes.csv - static - do level up rewards?
# DONE? data/text/generators for warrior_one through _six - static
# data/text/scripts/diceyap
#       ap_data.csv - dynamic - maybe do from client only? can generate on /dicey call and whenever we get call from game.
#       DONE load_ap_items_by_category - static
#       DONE send_location_checks - static


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
    'Upgrade': 'change_power',
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

class DiceyDungeonsModGenerator():
    world: "DiceyDungeonsWorld"
    """Dicey Dungeons World"""
    output_directory: str
    """Exclusively the output path, aka output/AP_..."""
    output_zip_name: str
    """Will be the name of zip which will live in output directory"""
    equipment: list[str]
    """List of items from multiworld we want in our equipment.csv"""
    mod_name: str
    """Name of the mod (probably 'diceyap')"""

    def __init__(self, world: "DiceyDungeonsWorld", output_dir: str):
        self.world = world
        self.output_directory = output_dir
        self.output_zip_name = world.multiworld.get_out_file_name_base(world.player)
        self.equipment = world.multiworld.get_items()
        self.mod_name = 'diceyap'
    
    def get_equipment_row(self, location: Location):
        location_id = str(location.address)
        item = location.item
        owner = self.world.multiworld.player_name[item.player] if self.world.player != item.player else "You!"

        row = default_item_info.copy()
        row['Name'] = f"{item.name} [AP][{location_id}]"
        row['Description'] = f"Owner: {owner}| |{item_classification_text_mapping[item.classification]}"

        return row
        
    
    def generate(self):
        diceyap_path = os.path.join(self.output_directory, self.mod_name)
        output_zip_full = os.path.join(self.output_directory, self.output_zip_name)
        
        os.mkdir(diceyap_path)

        # Copy base files first.
        base_file_path = os.path.join(os.path.dirname(__file__), 'data', 'mod_data', self.mod_name)
        shutil.copytree(base_file_path, diceyap_path, dirs_exist_ok=True)

        data_text_directory = os.path.join(diceyap_path, '_append', 'data', 'text')
        
        # Generate equipment.csv
        equipment_filename = os.path.join(data_text_directory, "equipment.csv")
        with open(equipment_filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=equipment_field_list)
            writer.writeheader()
            rows = []
            for location in self.world.get_locations():
                rows.append(self.get_equipment_row(location))
            # Testing spell
            rows.append(murder_spell)
            # Dice shard, for our filler.
            rows.append(dice_shard)
            writer.writerows(rows)

        shutil.make_archive(output_zip_full, 'zip', self.output_directory, self.mod_name)

        # Delete the working folder
        if os.path.exists(diceyap_path):
            shutil.rmtree(diceyap_path)

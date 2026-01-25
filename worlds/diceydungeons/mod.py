import os
from typing import TYPE_CHECKING, Optional
import csv
from collections import OrderedDict
import zipfile
import io
from importlib.resources import files

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
    
    def _write_package_files_to_zip(self, zf: zipfile.ZipFile, base_path, mod_name: str):
        """Recursively write files from package resources to zip file."""
        def walk_files(path, prefix=''):
            for item in path.iterdir():
                if item.is_file():
                    content = item.read_bytes()
                    arcname = f'{prefix}/{item.name}'.lstrip('/')
                    zf.writestr(arcname, content)
                elif item.is_dir():
                    walk_files(item, f'{prefix}/{item.name}')
        
        walk_files(base_path, mod_name)
    
    def _generate_equipment_csv_string(self) -> str:
        """Generate equipment.csv content as a string."""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=equipment_field_list)
        writer.writeheader()
        rows = []
        for location in self.world.get_locations():
            rows.append(self.get_equipment_row(location))
        # Testing spell
        rows.append(murder_spell)
        # Dice shard, for our filler.
        rows.append(dice_shard)
        writer.writerows(rows)
        return output.getvalue()
        
    
    def generate(self):
        output_zip_full = os.path.join(self.output_directory, self.output_zip_name + '.zip')
        
        # Get the base mod data from package resources
        base_files = files(__package__).joinpath('data', 'mod_data', self.mod_name)
        
        with zipfile.ZipFile(output_zip_full, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Copy base files first
            self._write_package_files_to_zip(zf, base_files, self.mod_name)
            
            # Generate and write equipment.csv
            equipment_csv_content = self._generate_equipment_csv_string()
            zf.writestr(f'{self.mod_name}/_append/data/text/equipment.csv', equipment_csv_content)

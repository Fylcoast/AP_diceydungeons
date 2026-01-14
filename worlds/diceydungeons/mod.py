import os
import shutil

class DiceyDungeonsModGenerator():
    output_directory: str # Exclusively the output path, aka output/AP_...
    output_zip_name: str # Will be the name of zip which will live in output directory
    equipment: list[str] # List of items from multiworld we want in our equipment.csv
    mod_name: str # Name of the mod (probably 'diceyap')

    def __init__(self, output_dir: str, output_zip: str, items: list[str]):
        self.output_directory = output_dir
        self.output_zip_name = output_zip
        self.equipment = items
        self.mod_name = 'diceyap'
    
    def generate(self):
        diceyap_path = os.path.join(self.output_directory, self.mod_name)
        output_zip_full = os.path.join(self.output_directory, self.output_zip_name)
        
        os.mkdir(diceyap_path)
        filename = os.path.join(diceyap_path, "Equipment.txt")
        with open(filename, 'w') as f:
            f.writelines([item.name + '\n' for item in self.equipment])

        shutil.make_archive(output_zip_full, 'zip', self.output_directory, self.mod_name)

        # Delete the working folder
        if os.path.exists(diceyap_path):
            shutil.rmtree(diceyap_path)

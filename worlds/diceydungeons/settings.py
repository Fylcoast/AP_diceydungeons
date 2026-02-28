import settings

class DiceyDungeonsSettings(settings.Group):
    class InstallFolder(settings.LocalFolderPath):
        """Path to the Dicey Dungeons installation folder"""
        description = "The Dicey Dungeons installation folder"
    
    install_folder: InstallFolder = InstallFolder("Dicey Dungeons")
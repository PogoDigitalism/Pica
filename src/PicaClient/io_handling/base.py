import ctypes
import sys

from .structure_parser import SchematicParser

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class File:
    """
    Bundles file operations, used in IOHandler
    """
    def __init__(self, file_name: str, file_location: str, file_size: int) -> None:
        self.file_name = file_name
        self.file_location = file_location
        self.file_Size = file_size

        # TEMP FILE CREATION LOGIC:

class IOHandler(SchematicParser): # NO INHERITANCE REALLY NEEDED
    def __init__(self, schematic: str) -> None:

        # parse schematic
        super().__init__(schematic = schematic)
        if not self.parsed_schematic:
            ...

    def new_file(self) -> File:
        ...

    def file_write(self):
        ...
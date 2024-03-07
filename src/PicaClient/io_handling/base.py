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
    def __init__(self) -> None:
        pass

class IOHandler(SchematicParser): # NO INHERITANCE REALLY NEEDED
    def __init__(self, schematic: str) -> None:

        # parse schematic
        super().__init__(schematic = schematic)
        if not self.parsed_schematic:
            ...

    def new_file(self):
        ...

    def file_write(self):
        ...
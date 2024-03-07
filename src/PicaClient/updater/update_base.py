import ctypes
import sys

from .structure_parser import SchematicParser

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class UpdateHandler(SchematicParser):
    def __init__(self, schematic: str) -> None:

        # parse schematic
        super().__init__(schematic = str)
        if not self.parsed_schematic:
            ...


    def implement(self):
        ...
"""
schematic:

[{"file_name": "example.py",
    "relative_location": ".src\\server\\",
    "action_types": [0x00000001],
    "type_data": {0x00000001: None}
    },
]
"""

#ACTION TYPES
INSERT = 0x00000000
DELETE = 0x00000001
MODIFY = 0x00000002
MOVE = 0x00000003

RENAME = 0x00000010

class SchematicParser:
    """
    Custom download schematic parser
    """
    def __init__(self, schematic: str) -> None:
        self.parsed_schematic = None

        # TODO IMPLEMENT PARSING LOGIC AND SET TO self._parse_result
        ...
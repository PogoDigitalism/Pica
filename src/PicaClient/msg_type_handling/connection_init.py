from __future__ import annotations
import typing

from updater.update_base import UpdateHandler

from base.constants import *
from base.classes import RecvData
from base.exceptions import AccessDeniedError

def MSG_HANDSHAKE_handler(obj: object, parsed_data: RecvData, var_to_set: str = None):
    if var_to_set:
        setattr(obj, var_to_set, parsed_data.msg_data)

def MSG_SCHEMATIC_handler(obj: object, parsed_data: RecvData, var_to_set: str = None):
    update_handler = UpdateHandler(schematic=parsed_data.msg_data)
    if var_to_set:
        setattr(obj, var_to_set, update_handler)

def MSG_ACCESS_DENIED_handler(obj: object, parsed_data: RecvData, var_to_set: str = None):
    raise AccessDeniedError

CONNECTION_INIT_HANDLING: dict[int, tuple[typing.Callable, str]] = {
    MSG_HANDSHAKE: (MSG_HANDSHAKE_handler, '_handshake'),
    MSG_SCHEMATIC: (MSG_SCHEMATIC_handler, '_update_handler'),
    MSG_ACCESS_DENIED: (MSG_ACCESS_DENIED_handler, ''),
}
from concurrent.futures import ThreadPoolExecutor
import typing
import socket
import traceback
import time

from base._types import (identifier, 
                             success,
                             host_names)
from base.classes import (SocketBase,
                               RecvData)
from base.constants import *
from base.exceptions import *

from .updater.update_base import UpdateHandler

from .message_type_handling.connection_init import CONNECTION_INIT_HANDLING

#Constants
VERSION_LOCATION = "..\pica.version"
version_file = open(file=VERSION_LOCATION, mode="r", )
VERSION = version_file.read()
print(VERSION)


class Client(SocketBase):
    """
    Connectant sided socket
    """
    def __init__(self, host_name: host_names = None) -> None:
        self._host_name = host_name or socket.gethostname()
        self._open_new_socket()

        self.progress_callback: typing.Callable = None

    def _parse_data(self, data: bytes) -> RecvData | None:
        data = data.decode(encoding="utf-8")

        data: list[bytes] = data.split(sep=DATA_SEPERATOR)
        if len(data) < 3:
            return

        parsed_data = RecvData(msg_type=data[0],
                               msg_info=data[1],
                               msg_data=data[3])
        
        return parsed_data

    def _receive_data(self) -> None:
        while True:
            try:
                data = self._socket.recv(C_RECV_SIZE)
                if data:
                    parsed_data = self._parse_data(data)
                else:
                    print("DISCONNECTION")
                    break
            except KeyError: # TODO CHANGE TO socket.timeout EXCEPTION HANDLER
                pass

    def _open_new_socket(self):
        self._socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self._socket.settimeout(C_SOCKET_TIMEOUT)

    def _connect_to_socket(self):
        self._socket.connect((self._host_name, SOCKET_PORT))

        while True:
            data = self._socket.recv(C_RECV_SIZE)
            if data:
                parsed_data: RecvData = self._parse_data(data)
                print(parsed_data)

                func_tuple = CONNECTION_INIT_HANDLING[parsed_data.msg_type]
                func_tuple[0](obj=self, parsed_data=parsed_data, var_to_set=func_tuple[1])

    def open(self) -> bool:
        """
        connect connectant socket to download server
        """
        try:
            self._connect_to_socket()
        except Exception as e:
            traceback.print_exc()
            raise
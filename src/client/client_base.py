from concurrent.futures import ThreadPoolExecutor
import typing
import socket

import time

from base.base_types import (identifier, 
                             success,
                             host_names)

from .updater.update_base import UpdateHandler

#Constants
SOCKET_PORT = 80
MAX_CONNECTIONS = 5


class Client:
    """
    Connectant sided socket
    """
    def __init__(self, host_name: host_names = None) -> None:
        self._host_name = host_name or socket.gethostname()

        self._socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)


    def open(self) -> None:
        """
        connect connectant socket to download server
        """
        # TODO: UpdateHandler(schematic) addition

        self._socket.connect((self._host_name, 80))

        h = self._socket.send(b"THIS IS A TEST")

        print("im done for", h)

        print(self._socket.getsockname())

        m = self._socket.recv(6*1024)
        print("im done forss", m)
        print(m)
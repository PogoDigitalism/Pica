from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import typing
import socket
import traceback
import time
import threading

from base._types import (identifier, 
                             success,
                             host_names,
                             file_scope)
from base.classes import (ABCSocketBase,
                               RecvData)
from base.constants import *
from base.exceptions import *

from .io_handling.base import IOHandler

# from .msg_type_handling.connection_init import CONNECTION_INIT_HANDLING

#Constants
VERSION_LOCATION = "..\pica.version"
version_file = open(file=VERSION_LOCATION, mode="r", )
VERSION = version_file.read()
print(VERSION)

class MSGHandler:
    def __init__(self) -> None:
        self.progress_callbacks: dict[file_scope, dict[str]] = dict()
        self.progress: dict[file_scope, tuple[str, tuple[int, int]]] = tuple()
    
    def MSG_ACCESS_DENIED_handler(self, parsed_data: RecvData):
        raise AccessDeniedError

    def MSG_HANDSHAKE_handler(self, parsed_data: RecvData):
        self._handshake = parsed_data.msg_data
        return True

    def MSG_SCHEMATIC_handler(self, parsed_data: RecvData):
        self._update_version = parsed_data.msg_info
        self._update_handler = IOHandler(schematic=parsed_data.msg_data)
        return False

    def MSG_NEW_FILE_handler(self, parsed_data: RecvData):
        self._current_file = self._update_handler.new_file(parsed_data)
        return True

    def MSG_FILE_PAYLOAD_handler(self, parsed_data: RecvData):
        self._update_handler.file_write(parsed_data)
        return True
      
    MSG_CALLBACKS: dict[int, tuple[typing.Callable, str]] = {
        MSG_ACCESS_DENIED: MSG_ACCESS_DENIED_handler,
        MSG_HANDSHAKE: MSG_HANDSHAKE_handler,
        MSG_SCHEMATIC: MSG_SCHEMATIC_handler,
        MSG_NEW_FILE: MSG_NEW_FILE_handler,
        MSG_FILE_PAYLOAD: MSG_FILE_PAYLOAD_handler
    }

class Client(ABCSocketBase, MSGHandler):
    """
    Connectant sided socket
    """
    def __init__(self, host_name: host_names = None) -> None:
        super().__init__()

        self._host_name = host_name or socket.gethostname()
        self._open_new_socket()

        self._lock = threading.Lock()

        self._is_active = False
        self._is_open = False
        self._data_queue: list[bytes] = list() 

        #MSG HANDLER ATTRS
        self._handshake: bytes = None
        self._update_version: str = None
        self._update_handler: IOHandler = None

        self.progress_callback: typing.Callable = None

    def _parse_incoming_data(self, data: bytes) -> RecvData | None:
        data = data.decode(encoding="utf-8")

        data: list[bytes] = data.split(sep=DATA_SEPERATOR)
        if len(data) < 3:
            return

        parsed_data = RecvData(int(msg_type=data[0]),
                               msg_info=data[1],
                               msg_data=data[3])
        
        return parsed_data

    def _put_data_queue(self, data: RecvData):
        data_to_send = f'{data.msg_type};;;{data.msg_info};;;{data.msg_data}'

        with self._lock:
            self._data_queue.append(data_to_send)

    def _send_data_loop(self) -> None:
        """
        Threaded main data forwarding loop
        """
        while self._is_open:
            with self._lock:
                if self._data_queue:
                    data = self._data_queue.pop(0)

            try:
                self._socket.send(data)
            except Exception as e: # TODO CHANGE TO socket.timeout EXCEPTION HANDLER
                traceback.print_exc()

    def _receive_data_loop(self) -> None:
        """
        Main data receiving loop
        """
        while self._is_open:
            try:
                data = self._socket.recv(C_RECV_SIZE)
                if data:
                    parsed_data = self._parse_incoming_data(data)

                    repeat = self.MSG_CALLBACKS[parsed_data.msg_type](parsed_data)

                    # if not repeat:
                    #     break
            except KeyError: # TODO CHANGE TO socket.timeout EXCEPTION HANDLER
                pass

    def _open_new_socket(self):
        self._socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self._socket.settimeout(C_SOCKET_TIMEOUT)

    def _close_socket(self):
        self._socket.close()
        self._is_open = False

        self._sending_thread.join()

    def _connect_to_socket(self):
        self._socket.connect((self._host_name, SOCKET_PORT))
        self._is_open = True
    
    def close_connection(self):
        self._close_socket()

    def initialize_connection(self):
        """
        connect connectant socket to download server
        """
        if not self._is_open:
            try:
                self._connect_to_socket()
                
                self._receive_data_loop()
                self._sending_thread = threading.Thread(target=self._send_data_loop)
                self._sending_thread.start()

                RecvData(msg_type=MSG_DOWNLOAD_INIT,
                         msg_data=VERSION)
                self._put_data_queue(data=RecvData)

            except Exception as e:
                traceback.print_exc()
                raise
        else:
            raise AlreadyOpenError
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import typing
import socket
import traceback
import time
import threading
import queue

from base._types import (identifier, 
                             success,
                             host_names,
                             file_scope)
from base.classes import (ABCSocketBase,
                               RecvData)
from base.constants import *
from base.exceptions import *

from .io_handling.base import IOHandler, File

# from .msg_type_handling.connection_init import CONNECTION_INIT_HANDLING

#Constants
VERSION_LOCATION = "..\pica.version"
version_file = open(file=VERSION_LOCATION, mode="r", )
VERSION = version_file.read()
print(VERSION)

class MSGHandler:
    def __init__(self, data_queue: queue.Queue) -> None:
        self.__send_data_queue = data_queue

        self.progress_callbacks: dict[file_scope, dict[str]] = dict()
        self.progress: dict[file_scope, tuple[str, tuple[int, int]]] = tuple()

    def MSG_ACCESS_DENIED_handler(self, parsed_data: RecvData):
        self._is_active = None
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
        self._host_name = host_name or socket.gethostname()
        self._open_new_socket()

        self._lock = threading.Lock()

        self._is_active = True # set to true for the execution loop
        self._is_open = False

        self._send_data_queue = queue.Queue()
        self._recv_callback_queue = queue.Queue()

        self._incomplete_chunks: list[bytes] = list()
        self._data_buffer: bytes = b''
        self._latest_payload: bytes = b''

        #MSG HANDLER ATTRS
        self._handshake: bytes = None
        self._update_version: str = None
        self._update_handler: IOHandler = None
        self._current_file: File = None

        self.progress_callback: typing.Callable = None

        super().__init__(data_queue=self._send_data_queue)

    def _validate_data(self, data: bytes):
        start_index = data.find(b'%s' % DATA_START)
        end_index = data.find(b'%s' % DATA_END)

        if start_index != -1:
            if end_index != -1:
                if start_index < end_index:
                    # normal new clean msg
                    ...
                else:
                    # left over in buffer
                    completed_buffer = self._data_buffer + data[:end_index + len(DATA_END)]
                    self._data_buffer = b''

                    self._recv_callback_queue.put(completed_buffer)

                    temp_buffer = data[end_index + len(DATA_END):]
                    
                    end_index = temp_buffer.find(b'%s' % DATA_END, start_index)

                    if end_index != -1:
                        ...
                        self._recv_callback_queue.put(temp_buffer)

                    else:
                        self._data_buffer = temp_buffer
                # start and end indicators found
                ...
            else:
                ...
                # start indicator found, end indicator missing
        else:
            if end_index != -1:
                ...
                # end indicator found, start indicator missing
            else:
                ...
                # start and end indicators missing

    @staticmethod
    def _parse_payload(data: str) -> RecvData | None:
        data = data.split(sep=DATA_SEPERATOR)
        if len(data) < 3:
            return

        parsed_data = RecvData(int(msg_type=data[0]),
                               msg_info=data[1],
                               msg_data=data[3])
        
        return parsed_data

    def _put_payload_queue(self, data: RecvData):
        data_to_send = f'{DATA_START}{data.msg_type}{DATA_SEPERATOR}{data.msg_info}{DATA_SEPERATOR}{data.msg_data}{DATA_END}'
        self._send_data_queue.put(item=data_to_send)

    def _send_data_loop(self) -> None:
        """
        Threaded main data forwarding loop
        """
        while self._is_open:
            data = self._send_data_queue.get(block=True)

            try:
                self._socket.send(data)
            except Exception as e: # TODO CHANGE TO socket.timeout EXCEPTION HANDLER
                traceback.print_exc()

    def _execute_msg_callbacks(self):
        while self._is_active:
            validated_data = self._recv_callback_queue.get(block=True)

            parsed_data = self._parse_payload(validated_data)

            repeat = self.MSG_CALLBACKS[parsed_data.msg_type](parsed_data)

    def _receive_data_loop(self) -> None:
        """
        Main data receiving loop
        """
        while self._is_open:
            try:
                data = self._socket.recv(C_RECV_SIZE)
                if data:
                    # validate and parse based on the protocol and put it in the callback queue
                    self._validate_data(data)


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
                self._put_payload_queue(data=RecvData)

            except Exception as e:
                traceback.print_exc()
                raise
        else:
            raise AlreadyOpenError
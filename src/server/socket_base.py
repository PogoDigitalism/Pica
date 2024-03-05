from concurrent.futures import ThreadPoolExecutor
import typing
import socket

from base.base_types import (identifier, 
                             success,
                             host_names)

#Constants
SOCKET_PORT = 80
MAX_CONNECTIONS = 5


class _Client:
    """
    Unique connection handler between connectant and server.
    """
    def __init__(self, connectant: identifier, client_socket: socket.socket) -> None:
        self.client_socket = client_socket
        self.connectant = connectant


class Server:
    """
    Server sided socket
    """
    def __init__(self, host_name: host_names = None) -> None:
        self._host_name = host_name or socket.gethostname()

        self._thread_pool = ThreadPoolExecutor(max_workers=MAX_CONNECTIONS,
            thread_name_prefix="SOCKET_CLIENT-"
        )

        self._socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self._socket.bind((self._host_name, SOCKET_PORT))
        self._socket.listen(MAX_CONNECTIONS)

        self._active_clients: dict[identifier, _Client]

    def _create_new_client(self, connectant: identifier, client_socket: socket.socket):
        client = _Client(connectant=identifier, client_socket=client_socket)
        self._active_clients[connectant] = client


    def _handle_new_connection(self, connectant: identifier, client_socket: socket.socket) -> success:
        self._thread_pool.submit(self._create_new_client, connectant=connectant, client_socket=client_socket)


    def open(self) -> None:
        """
        open server socket and receive connection requests
        """
        try:
            while True:
                client_socket, address = self._socket.accept()

                self._handle_new_connection(connectant=address, client_socket=client_socket)
        except KeyboardInterrupt:
            print("reached!")

            self._socket.close()

            raise
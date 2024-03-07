#FRAMEWORK CLASS FOR PICA CLIENT SOCKET
import typing

from client_base import Client

from src.base._types import (identifier, 
                             success,
                             host_names,
                             file_scope)
from src.base.classes import (SocketBase,
                               RecvData)
from src.base.constants import *


class PicaUpdater(Client):
    """
    The base client class for connecting the client to your Pica server.\n
    `PicaUpdater` is used for initiating and controlling the Pica updater client
    """
    def __init__(self, host_name: host_names = None) -> None:
        super().__init__(host_name=host_name)

    def connect(self):
        """
        Connect to a Pica server with the client and start the updating procedure
        """
        self.initialize_connection()

    def stop(self):
        ...

    def resume(self):
        ...

    def pause(self):
        ...

    def close(self):
        """
        Close the Pica updater client

        If a connection is active, schedules a socket disconnection. 
            `->` If a download is in progress, the disconnection is executed after the current file is finished downloading and writing. 
        """
        ...

    def progress_callback(self, scope: file_scope, func: typing.Callable, *args, **kwargs):
        """
        Set a callback function whenever the scoped object changes.
        Useful for giving download progress feedback in a GUI.

        Note: Setting a callback to "APPLICATION" scope will fire after all update files are processed.
        """
        self.progress_callbacks[scope] = {'func': func,
                                          'args': args,
                                          'kwargs': kwargs}


    def get_progress(self, scope: file_scope) -> tuple[str, tuple[int, int]] | None:
        """
        Returns progress information (consisting of the name of the scoped object, processed byte size and the total byte size).

        scope: 
            `"FILE"` -> Get the progress information of the file that is currently being downloaded\n
            `"APPLICATION"` -> Get the progress information of the total update

        Returns a tuple: (name, (processed, total))
        """
        return self.progress[scope]
        ...
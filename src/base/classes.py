from abc import (ABC,
                 abstractmethod,
                 abstractstaticmethod,
                 abstractclassmethod)
from dataclasses import dataclass

# ABSTRACT BASE CLASSES
class ABCSocketBase(ABC):
    """
    ABC used for any socket related handlers
    """
    @abstractmethod
    def open(self):
        ...


# DATACLASSES
@dataclass
class RecvData:
    msg_type: int
    msg_info: str = ''
    msg_data: bytes = b''
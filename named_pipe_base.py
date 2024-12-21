from abc import ABC, abstractmethod
from typing import TypeVar


class NamedPipeBase(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """Initialize the SPI bus master to allow data transfer to slave devices"""

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    def mkfifo():
        pass

    def open():
        pass

    def close():
        pass

    def read():
        pass

    def write():
        pass


NamedPipe = TypeVar("NamedPipe", bound=NamedPipe)

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar


class NamedPipeBase(ABC):
    def __init__(self, path: str) -> None:
        """Initialize namedPipe"""
        self._path = path
        return

    def __enter__(self) -> NamedPipeBase:
        return self.mkfifo()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        return self.unlink()

    @abstractmethod
    def mkfifo(self) -> NamedPipeBase:
        """Create the namedPipe"""

    @abstractmethod
    def unlink(self) -> None:
        """Unlink / remove the namedPipe"""


NamedPipe = TypeVar("NamedPipe", bound=NamedPipeBase)


class PipeEndBase(ABC):
    def __enter__(self):
        """Return the PipeEnd for read or write"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Close the PipeEnd"""
        return self._close()

    @abstractmethod
    def _open(self, named_pipe: NamedPipeBase, mode: str) -> None:
        """Open the named pipe in read xor write mode"""

    @abstractmethod
    def _close(self) -> None:
        """Close the namedPipe"""


PipeEnd = TypeVar("PipeEnd", bound=PipeEndBase)


class WritePipeEndBase(PipeEndBase):
    def __init__(self, path: str) -> None:
        """Open the NamedPipe in write mode"""
        return super().__init__(path, "w")

    @abstractmethod
    def write(self, string: str):
        """Writes to the pipe"""


WritePipeEnd = TypeVar("WritePipeEnd", bound=WritePipeEndBase)


class ReadPipeEndBase(PipeEndBase):
    def __init__(self, path: str) -> None:
        """Open the NamedPipe in read mode"""
        return super().__init__(path, "r")

    @abstractmethod
    def read(self) -> str:
        """Reads from the pipe"""


ReadPipeEnd = TypeVar("ReadPipeEnd", bound=ReadPipeEndBase)

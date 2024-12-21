from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar


class NamedPipeBase(ABC):
    """
    Abstract base class for named pipes.

    This class provides a basic structure for creating and managing named pipes.
    """

    def __init__(self, path: str) -> None:
        """
        Initialize a named pipe.

        :param path: The path to the named pipe.
        """
        self._path = path
        return

    def __enter__(self) -> NamedPipeBase:
        """
        Context manager entry point.

        Creates the named pipe and returns the instance.
        """
        return self.mkfifo()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Context manager exit point.

        Removes the named pipe.
        """
        return self.unlink()

    @abstractmethod
    def mkfifo(self) -> NamedPipeBase:
        """
        Create the named pipe.

        This method should be implemented by subclasses to create the named pipe.
        """

    @abstractmethod
    def unlink(self) -> None:
        """
        Unlink / remove the named pipe.

        This method should be implemented by subclasses to remove the named pipe.
        """


NamedPipe = TypeVar("NamedPipe", bound=NamedPipeBase)


class PipeEndBase(ABC):
    """
    Abstract base class for pipe ends.

    This class provides a basic structure for opening and closing.
    """

    def __init__(self, named_pipe: NamedPipeBase, mode: str) -> None:
        """
        Initialize a pipe end.

        :param named_pipe: The named pipe which should be used for opening and closing.
        :param mode: The mode to open the pipe in (e.g., 'r' or 'w').
        """
        self._named_pipe = named_pipe
        self._mode = mode

    def __enter__(self):
        """
        Context manager entry point.

        Opens and returns the pipe end instance.
        """
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Context manager exit point.

        Closes the pipe end instance.
        """
        return self.close()

    def open(self) -> None:
        """Open the named pipe in the specified mode."""
        return self._open(self._named_pipe, self._mode)

    def close(self) -> None:
        """Close the named pipe."""
        return self._close(self._named_pipe)

    @abstractmethod
    def _open(self, named_pipe: NamedPipeBase, mode: str) -> None:
        """
        Open the named pipe in read or write mode.

        This method should be implemented by subclasses to open the pipe end.

        :param named_pipe: The named pipe instance.
        :param mode: The mode to open the pipe in (e.g., 'r' or 'w').
        """

    @abstractmethod
    def _close(self, named_pipe: NamedPipeBase) -> None:
        """
        Close the pipe end.

        This method should be implemented by subclasses to close the pipe end.

        :param named_pipe: The named pipe instance.
        """


PipeEnd = TypeVar("PipeEnd", bound=PipeEndBase)


class WritePipeEndBase(PipeEndBase):
    """
    Abstract base class for write pipe ends.

    This class provides a basic structure for writing to named pipes.
    """

    def __init__(self, named_pipe: NamedPipeBase) -> None:
        """
        Initialize a write pipe end.

        :param named_pipe: The named pipe to create the pipe end for.
        """
        return super().__init__(named_pipe, "w")

    @abstractmethod
    def write(self, string: str) -> None:
        """
        Write to the pipe.

        :param string: The string to write to the pipe.
        """


WritePipeEnd = TypeVar("WritePipeEnd", bound=WritePipeEndBase)


class ReadPipeEndBase(PipeEndBase):
    """
    Abstract base class for read pipe ends.

    This class provides a basic structure for reading from named pipes.
    """

    def __init__(self, named_pipe: NamedPipeBase) -> None:
        """
        Initialize a read pipe end.

        :param named_pipe: The named pipe to create the pipe end for.
        """
        return super().__init__(named_pipe, "r")

    @abstractmethod
    def read(self) -> str:
        """
        Read from the pipe.

        Returns the string read from the pipe.
        """


ReadPipeEnd = TypeVar("ReadPipeEnd", bound=ReadPipeEndBase)

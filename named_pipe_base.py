from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from time import sleep

from warnings import warn


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
    def get_path(self) -> str:
        """
        Get the path of the NamedPipe.
        """

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

    def __init__(self, named_pipe: NamedPipeBase | str, mode: str) -> None:
        """
        Initialize a pipe end.

        :param named_pipe: The named pipe which should be used for opening and closing.
        :param mode: The mode to open the pipe in (e.g., 'r' or 'w').
        """
        if isinstance(named_pipe, str):
            self._named_pipe = self._create_named_pipe_from_path(named_pipe)
        else:
            self._named_pipe = named_pipe
        self._mode = mode

    def __enter__(self):
        """
        Context manager entry point.

        Opens and returns the pipe end instance.
        """
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Context manager exit point.

        Closes the pipe end instance.
        """
        return self.close()

    def open(self, retries: int = 3, delay: float = 0.5) -> PipeEndBase:
        """
        Open the named pipe in the specified mode.

        :param retries: The number of retries to open pipe, before failure.
        :param delay: The delay between consecutive retries to open the pipe.
        """
        for i in range(retries):
            try:
                return self._open(self._named_pipe, self._mode)
            except Exception as e:
                warn(
                    f"PipeEnd open() attempt {i+1}: Pipe not available: {e}",
                    UserWarning,
                )
                sleep(delay)

        raise OSError(f"PipeEnd {self} not available for opening.")

    def close(self) -> None:
        """Close the named pipe."""
        return self._close(self._named_pipe)

    @abstractmethod
    def _open(self, named_pipe: NamedPipeBase, mode: str) -> PipeEndBase:
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

    @abstractmethod
    def _create_named_pipe_from_path(self, path: str) -> NamedPipeBase:
        """
        Create a named pipe from a path.

        This method should be implemented by subclasses to allow convenience
        creation of pipe ends on the client side, not responsible for creating
        the named pipe resource with the operating system.

        :param path: The path to the named pipe.
        """


PipeEnd = TypeVar("PipeEnd", bound=PipeEndBase)


class WritePipeEndBase(PipeEndBase):
    """
    Abstract base class for write pipe ends.

    This class provides a basic structure for writing to named pipes.
    """

    def __init__(self, named_pipe: NamedPipeBase | str) -> None:
        """
        Initialize a write pipe end.

        :param named_pipe: The named pipe to create the pipe end for.
        """
        return super().__init__(named_pipe, "w")

    @abstractmethod
    def write(self, data: bytes) -> None:
        """
        Write to the pipe.

        :param data: The data to write to the pipe.
        """


WritePipeEnd = TypeVar("WritePipeEnd", bound=WritePipeEndBase)


class ReadPipeEndBase(PipeEndBase):
    """
    Abstract base class for read pipe ends.

    This class provides a basic structure for reading from named pipes.
    """

    def __init__(self, named_pipe: NamedPipeBase | str) -> None:
        """
        Initialize a read pipe end.

        :param named_pipe: The named pipe to create the pipe end for.
        """
        return super().__init__(named_pipe, "r")

    @abstractmethod
    def read(self) -> bytes:
        """
        Read from the pipe.

        Returns the string read from the pipe.
        """


ReadPipeEnd = TypeVar("ReadPipeEnd", bound=ReadPipeEndBase)

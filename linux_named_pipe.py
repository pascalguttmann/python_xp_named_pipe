from __future__ import annotations

import os

from named_pipe_base import (
    NamedPipeBase,
    PipeEndBase,
    ReadPipeEndBase,
    WritePipeEndBase,
)


class NamedPipe(NamedPipeBase):
    """Linux named pipes creation."""

    def get_path(self) -> str:
        return self._path

    def mkfifo(self) -> NamedPipe:
        os.mkfifo(self.get_path())  # # pyright: ignore[reportAttributeAccessIssue]
        return self

    def unlink(self) -> None:
        os.unlink(self.get_path())
        return


class PipeEnd(PipeEndBase):
    def _open(self, named_pipe: NamedPipeBase, mode: str) -> PipeEnd:
        """
        Open the named pipe in read or write mode.

        :param named_pipe: The named pipe instance.
        :param mode: The mode to open the pipe in (e.g., 'r' or 'w').
        """
        if mode == "w":
            rw_flag = os.O_WRONLY
        elif mode == "r":
            rw_flag = os.O_RDONLY
        else:
            raise OSError(
                87,
                f"Opening mode of NamedPipe should be 'r' or 'w', but is {mode}",
            )

        pipe = os.open(named_pipe.get_path(), rw_flag)

        self._pipe_end_handle = pipe
        return self

    def _close(self, named_pipe: NamedPipeBase) -> None:
        """
        Close the pipe end.

        :param named_pipe: The named pipe instance.
        """
        os.close(self._pipe_end_handle)

    def _create_named_pipe_from_path(self, path: str) -> NamedPipeBase:
        """
        Create a named pipe from a path.

        :param path: The path to the named pipe.
        """
        return NamedPipe(path)


class WritePipeEnd(PipeEnd, WritePipeEndBase):
    def write(self, data: bytearray) -> None:
        """
        Write to the pipe.

        :param data: The data to write to the pipe.
        """
        num_bytes_written = os.write(self._pipe_end_handle, data)


class ReadPipeEnd(PipeEnd, ReadPipeEndBase):
    def read(self) -> bytearray:
        """
        Reads from the pipe.
        """
        return os.read(self._pipe_end_handle, 65536)

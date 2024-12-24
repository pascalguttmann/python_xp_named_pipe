from __future__ import annotations

from named_pipe_base import (
    NamedPipeBase,
    PipeEndBase,
    ReadPipeEndBase,
    WritePipeEndBase,
)

import win32pipe
import win32file
import pywintypes


class WinNamedPipe(NamedPipeBase):
    """Windows named pipes creation via Win32API."""

    winprefix = "\\\\.\\pipe\\"

    @staticmethod
    def path_to_winpath(path: str):
        return path.replace("/", "\\")

    @classmethod
    def prepend_winprefix(cls, pipename: str):
        return cls.winprefix + pipename

    @classmethod
    def strip_winprefix(cls, path: str):
        return path.removeprefix(cls.winprefix)

    def is_windows_named_pipe_server_process(self) -> bool:
        return hasattr(self, "_win_pipe_handle")

    def get_pipe_handle(self) -> int:
        return self._win_pipe_handle

    def get_path(self) -> str:
        """
        Get the path of the WinNamedPipe, which is prefixed by self.winprefix
        to allow arbitrary pipe names.
        """
        return self.path_to_winpath(self.prepend_winprefix(self._path))

    def mkfifo(self) -> WinNamedPipe:
        sa = pywintypes.SECURITY_ATTRIBUTES()
        sa.bInheritHandle = 1
        sa.SECURITY_DESCRIPTOR = pywintypes.SECURITY_DESCRIPTOR()

        pipe = win32pipe.CreateNamedPipe(
            self.get_path(),
            win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_BYTE
            | win32pipe.PIPE_READMODE_BYTE
            | win32pipe.PIPE_WAIT,
            1,
            65536,
            65536,
            300,
            sa,
        )

        self._win_pipe_handle = pipe
        return self

    def unlink(self) -> None:
        win32file.CloseHandle(self._win_pipe_handle)
        del self._win_pipe_handle
        return


class WinPipeEnd(PipeEndBase):
    def _open(self, named_pipe: NamedPipeBase, mode: str) -> WinPipeEnd:
        """
        Open the named pipe in read or write mode.

        :param named_pipe: The named pipe instance.
        :param mode: The mode to open the pipe in (e.g., 'r' or 'w').
        """
        if named_pipe.is_windows_named_pipe_server_process():  # pyright: ignore
            pipe = named_pipe.get_pipe_handle()  # pyright: ignore
            win32pipe.ConnectNamedPipe(pipe, None)
        else:
            if mode == "w":
                desired_access = win32file.GENERIC_WRITE
            elif mode == "r":
                desired_access = win32file.GENERIC_READ
            else:
                raise OSError(
                    87,
                    f"Opening mode of WinNamedPipe should be 'r' or 'w', but is {mode}",
                )

            pipe = win32file.CreateFile(
                named_pipe.get_path(),
                desired_access,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None,
            )

        self._win_pipe_end_handle = pipe
        return self

    def _close(self, named_pipe: NamedPipeBase) -> None:
        """
        Close the pipe end.

        :param named_pipe: The named pipe instance.
        """
        pipe = self._win_pipe_end_handle
        if named_pipe.is_windows_named_pipe_server_process():  # pyright: ignore
            win32pipe.DisconnectNamedPipe(pipe)
        else:
            win32file.CloseHandle(pipe)

    def _create_named_pipe_from_path(self, path: str) -> NamedPipeBase:
        """
        Create a named pipe from a path.

        :param path: The path to the named pipe.
        """
        return WinNamedPipe(path)


class WriteWinPipeEnd(WinPipeEnd, WritePipeEndBase):
    def write(self, data: bytes) -> None:
        """
        Write to the pipe.

        :param data: The data to write to the pipe.
        """
        win32file.WriteFile(
            self._win_pipe_end_handle,  # pyright: ignore[reportArgumentType]
            data,
        )
        win32file.FlushFileBuffers(
            self._win_pipe_end_handle  # pyright: ignore[reportArgumentType]
        )


class ReadWinPipeEnd(WinPipeEnd, ReadPipeEndBase):
    def read(self) -> bytes:
        """
        Reads from the pipe.
        """
        num_bytes_read, data = win32file.ReadFile(
            self._win_pipe_end_handle,  # pyright: ignore[reportArgumentType]
            65536,
        )
        if isinstance(data, str):
            return data.encode("utf-8")
        else:
            return data

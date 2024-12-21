from __future__ import annotations

from named_pipe_base import NamedPipeBase

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

    def mkfifo(self) -> WinNamedPipe:
        sa = pywintypes.SECURITY_ATTRIBUTES()
        sa.bInheritHandle = 1
        sa.SECURITY_DESCRIPTOR = pywintypes.SECURITY_DESCRIPTOR()

        pipe = win32pipe.CreateNamedPipe(
            self.path_to_winpath(self.prepend_winprefix(self._path)),
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
        return

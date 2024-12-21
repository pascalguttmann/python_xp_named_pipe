import sys

import win32pipe
import win32file
import pywintypes


def pipe_write_line_win(pipe, data: bytes):
    win32file.WriteFile(pipe, data)
    win32file.FlushFileBuffers(pipe)
    return


def pipe_open_win(path):
    path_win = ("\\\\.\\pipe\\" + path).replace("/", "\\")
    pipe = win32file.CreateFile(
        path_win,
        win32file.GENERIC_READ | win32file.GENERIC_WRITE,
        0,
        None,
        win32file.OPEN_EXISTING,
        0,
        None,
    )

    print("Opened named pipe " + path_win + f" handle={pipe}")
    return pipe


def mkfifo_win(path):
    path_win = ("\\\\.\\pipe\\" + path).replace("/", "\\")

    sa = pywintypes.SECURITY_ATTRIBUTES()
    sa.bInheritHandle = 1
    sa.SECURITY_DESCRIPTOR = pywintypes.SECURITY_DESCRIPTOR()

    pipe = win32pipe.CreateNamedPipe(
        path_win,
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_READMODE_BYTE | win32pipe.PIPE_WAIT,
        1,
        65536,
        65536,
        300,
        sa,
    )
    print("Created named pipe " + path_win + f" handle={pipe}")
    return pipe


def pipe_read_line_win(pipe):
    line = ""
    while True:
        data = win32file.ReadFile(pipe, 1)[1]  # read string of len() == 1 from pipe
        if not data:
            break
        char = data.decode("utf-8")  # pyright: ignore
        if char == "\n":
            break
        line += char
    return line

def pipe_close_win():
# win32file.CloseHandle(c2s)

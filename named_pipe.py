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

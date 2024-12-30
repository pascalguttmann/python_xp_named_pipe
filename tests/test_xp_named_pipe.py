import unittest
import os
import sys
import multiprocessing

from time import sleep

from xp_named_pipe import NamedPipe, ReadPipeEnd, WritePipeEnd


class TestXpNamedPipe(unittest.TestCase):
    test_pipe_path: str = "the_pipe"

    def test_mkfifo_unlink(self):
        pipe = NamedPipe(self.test_pipe_path)
        self.assertFalse(os.access(pipe.get_path(), os.F_OK))
        pipe.mkfifo()
        self.assertTrue(os.access(pipe.get_path(), os.F_OK))
        pipe.unlink()
        self.assertFalse(os.access(pipe.get_path(), os.F_OK))

    def test_context_management_protocol(self):
        pipe = NamedPipe(self.test_pipe_path)
        self.assertFalse(os.access(pipe.get_path(), os.F_OK))

        with NamedPipe(self.test_pipe_path) as pipe:
            self.assertTrue(os.access(pipe.get_path(), os.F_OK))

        self.assertFalse(os.path.exists(pipe.get_path()))


class TestPipeEnd(unittest.TestCase):
    test_pipe_path: str = "the_pipe7"
    test_data: bytes = bytes(b"this is my data")

    @staticmethod
    def create_writer_process(send: bytes):
        return multiprocessing.Process(target=TestPipeEnd.writer, args=(send,))

    @staticmethod
    def writer(send: bytes):

        with NamedPipe(TestPipeEnd.test_pipe_path) as pipe:
            with WritePipeEnd(pipe) as pipe_end:
                pipe_end.write(TestPipeEnd.test_data)  # pyright: ignore

        sys.exit(0)

    def test_pipe_end(self):

        writer = self.create_writer_process(self.test_data)
        writer.start()

        with ReadPipeEnd(NamedPipe(self.test_pipe_path)) as pipe_end:
            read_data = pipe_end.read()  # pyright: ignore

        writer.join(timeout=5)
        if writer.is_alive():
            writer.terminate()
            self.fail("Writer process timed out")
        self.assertEqual(writer.exitcode, 0)

        self.assertTrue(read_data == self.test_data)


if __name__ == "__main__":
    unittest.main()

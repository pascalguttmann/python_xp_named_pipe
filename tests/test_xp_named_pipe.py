import unittest
import os
from xp_named_pipe import NamedPipe, WritePipeEnd, ReadPipeEnd


class TestXpNamedPipe(unittest.TestCase):
    test_pipe_path = "the_pipe"

    def test_mkfifo_unlink(self):
        pipe = NamedPipe(self.test_pipe_path)
        print(pipe.get_path())
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


if __name__ == "__main__":
    unittest.main()

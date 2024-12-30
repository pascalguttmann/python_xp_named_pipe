from typing import assert_type
import unittest
import base64

from base64_encoder_decoder import Base64DatagrammeEncoderDecoder as base64_end_dec


class TestBase64DatagrammeEncoderDecoder(unittest.TestCase):
    message_1 = b"Hello"
    message_2 = b"World"
    message_3 = b"and the rest of the universe."
    message_1_enc = base64.b64encode(message_1)
    message_2_enc = base64.b64encode(message_2)
    message_3_enc = base64.b64encode(message_3)
    delim = b"\x00"

    def read_mock(self) -> bytes:
        return self.message_1_enc + self.delim

    def read_incomplete_datagramme(self) -> bytes:
        return (
            self.message_1_enc
            + self.delim
            + self.message_2_enc
            + self.delim
            + self.message_3_enc[0:2]
        )

    def write_mock(self, data: bytes) -> None:
        return None

    def write_assert(self, data: bytes, expected: bytes):
        self.assertEqual(data, expected)
        return

    def test_read_decoding_and_incomplete_datagramme_detection(self):
        b64 = base64_end_dec(self.read_incomplete_datagramme, self.write_mock)
        message_1_actual = b64.read()
        self.assertEqual(message_1_actual, self.message_1)
        self.assertFalse(b64._datagrammes_fifo_is_empty())
        self.assertEqual(b64._datagrammes[0], self.message_2)
        self.assertEqual(b64._partial_enc_datagramme, self.message_3_enc[0:2])
        message_2_actual = b64.read()
        self.assertEqual(message_2_actual, self.message_2)
        self.assertTrue(b64._datagrammes_fifo_is_empty())
        self.assertEqual(b64._partial_enc_datagramme, self.message_3_enc[0:2])
        return

    def test_write_encoding_and_delim_appended(self):
        def write_assert_message_2_enc_and_delim(data: bytes):
            return self.write_assert(data, self.message_2_enc + self.delim)

        b64 = base64_end_dec(self.read_mock, write_assert_message_2_enc_and_delim)
        b64.write(self.message_2)
        return

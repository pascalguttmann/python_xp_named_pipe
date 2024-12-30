import base64

from typing import Callable


class Base64DatagrammeEncoderDecoder:
    def __init__(
        self,
        read_func: Callable[[], bytearray],
        write_func: Callable[[bytearray], None],
    ) -> None:
        self.read_func = read_func
        self.write_func = write_func
        self._datagrammes = []
        self._partial_enc_datagramme = bytes()

    def _datagrammes_fifo_put(self, datagramme: bytearray) -> None:
        self._datagrammes.append(datagramme)

    def _datagrammes_fifo_pop(self) -> bytearray:
        return self._datagrammes.pop(0)

    def _datagrammes_fifo_is_empty(self) -> bool:
        if not self._datagrammes:
            return True
        else:
            return False

    def _set_partial_enc_datagramme(self, datagramme: bytearray) -> None:
        self._partial_enc_datagramme = datagramme

    def _pop_partial_enc_datagramme(self) -> bytearray:
        partial_enc_datagramme = self._partial_enc_datagramme
        self._set_partial_enc_datagramme(bytearray())
        return partial_enc_datagramme

    def _read_datagrammes_to_fifo(self) -> None:
        data = self.read_func()
        enc_datagrammes = (self._pop_partial_enc_datagramme() + data).split(b"\x00")

        if not data.endswith(b"\x00"):
            self._set_partial_enc_datagramme(enc_datagrammes[-1])
            del enc_datagrammes[-1]

        for enc_dg in enc_datagrammes:
            dec_dg = bytearray(base64.b64decode(enc_dg.rstrip(b"\x00")))
            self._datagrammes_fifo_put(dec_dg)
        return None

    def write(self, data: bytearray) -> None:
        encoded_data = bytearray(base64.b64encode(data))
        self.write_func(encoded_data + b"\x00")

    def read(self) -> bytearray:
        while self._datagrammes_fifo_is_empty():
            self._read_datagrammes_to_fifo()
        return self._datagrammes_fifo_pop()

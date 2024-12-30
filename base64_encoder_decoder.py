import base64

from typing import Callable


class Base64DatagrammeEncoderDecoder:
    _delim = b"\x00"

    def __init__(
        self,
        read_func: Callable[[], bytes],
        write_func: Callable[[bytes], None],
    ) -> None:
        self.read_func = read_func
        self.write_func = write_func
        self._datagrammes = []
        self._partial_enc_datagramme = bytes()

    def _datagrammes_fifo_put(self, datagramme: bytes) -> None:
        self._datagrammes.append(datagramme)

    def _datagrammes_fifo_pop(self) -> bytes:
        return self._datagrammes.pop(0)

    def _datagrammes_fifo_is_empty(self) -> bool:
        if not self._datagrammes:
            return True
        else:
            return False

    def _set_partial_enc_datagramme(self, datagramme: bytes) -> None:
        self._partial_enc_datagramme = datagramme

    def _pop_partial_enc_datagramme(self) -> bytes:
        partial_enc_datagramme = self._partial_enc_datagramme
        self._set_partial_enc_datagramme(bytes())
        return partial_enc_datagramme

    def _read_datagrammes_to_fifo(self) -> None:
        data = self.read_func()
        enc_datagrammes = (
            (self._pop_partial_enc_datagramme() + data)
            .rstrip(self._delim)
            .split(self._delim)
        )

        if not data.endswith(self._delim):
            self._set_partial_enc_datagramme(enc_datagrammes[-1])
            del enc_datagrammes[-1]

        for enc_dg in enc_datagrammes:
            dec_dg = bytes(base64.b64decode(enc_dg))
            self._datagrammes_fifo_put(dec_dg)
        return None

    def write(self, data: bytes) -> None:
        encoded_data = bytes(base64.b64encode(data))
        self.write_func(encoded_data + self._delim)

    def read(self) -> bytes:
        while self._datagrammes_fifo_is_empty():
            self._read_datagrammes_to_fifo()
        return self._datagrammes_fifo_pop()

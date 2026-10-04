import json
import struct
from io import RawIOBase

class IncidenteOutputStream(RawIOBase):
    HEADER_SIZE = 4  

    def __init__(self, destino, objetos: list[RelatorioIncidente], quantidade: int):
        super().__init__()
        self._destino = destino
        self._objetos = objetos
        self._quantidade = quantidade

    def writable(self) -> bool:
        return True

    def write(self, b: bytes) -> int:
        return self._destino.write(b)

    def flush(self) -> None:
        if hasattr(self._destino, "flush"):
            self._destino.flush()


    def escrever_objetos(self) -> int:
        total = 0
        n = min(self._quantidade, len(self._objetos))

        for i in range(n):
            obj = self._objetos[i]
            payload = json.dumps(obj.to_dict(), ensure_ascii=False).encode("utf-8")
            header = struct.pack(">I", len(payload))  # >I = uint32 big-endian

            total += self.write(header)
            total += self.write(payload)

        self.flush()
        return total
import io
import json
import struct

if __package__ and "." in __package__:
    from ..POJO import RelatorioIncidente
else:
    from POJO import RelatorioIncidente


class IncidenteInputStream(io.RawIOBase):
    def __init__(self, origem: io.BufferedIOBase | io.RawIOBase):
        super().__init__()
        self._origem = origem

    def readable(self) -> bool:
        return True

    def read(self, size: int = -1) -> bytes:
        return self._origem.read(size)

    def _read_exact(self, n: int) -> bytes | None:
        buf = bytearray()
        while len(buf) < n:
            # Arquivos, pipes e TCP podem entregar menos bytes que o pedido.
            chunk = self._origem.read(n - len(buf))
            if not chunk:                      # origem fechou
                if not buf:
                    return None                
                raise EOFError(f"EOF inesperado: esperava {n}, recebeu {len(buf)}")
            buf.extend(chunk)
        return bytes(buf)

    def ler_objeto(self) -> RelatorioIncidente | None:
        """Lê um objeto. Retorna None se atingiu EOF limpo."""
        header = self._read_exact(4)
        if header is None:
            return None

        tamanho = struct.unpack(">I", header)[0]
        json_bytes = self._read_exact(tamanho)
        if json_bytes is None:
            raise EOFError("EOF inesperado: esperava JSON")

        d = json.loads(json_bytes.decode("utf-8"))
        return RelatorioIncidente.from_dict(d)

    def ler_objetos(self, quantidade: int | None = None) -> list[RelatorioIncidente]:
        """
        Se quantidade=None → lê até EOF.
        Se quantidade=N     → lê exatamente N objetos (erro se acabar antes).
        """
        objetos: list[RelatorioIncidente] = []

        if quantidade is None:
            while True:
                obj = self.ler_objeto()
                if obj is None:
                    break
                objetos.append(obj)
        else:
            for _ in range(quantidade):
                obj = self.ler_objeto()
                if obj is None:
                    raise EOFError("EOF antes de ler todos os objetos esperados")
                objetos.append(obj)

        return objetos

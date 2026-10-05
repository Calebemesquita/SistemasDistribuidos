import json
import struct

from .mensagem import Mensagem


class Protocolo:
    """
    Converte Mensagem <-> bytes.

    Formato do frame:
        [4 bytes big-endian: tamanho N][N bytes: JSON UTF-8 da mensagem]
    """

    # ---------- EMPACOTAR ----------
    @staticmethod
    def empacotar(mensagem: Mensagem) -> bytes:
        """Mensagem → bytes prontos para enviar pelo socket."""
        json_str = json.dumps(mensagem.to_dict(), ensure_ascii=False)
        json_bytes = json_str.encode("utf-8")
        header = struct.pack(">I", len(json_bytes))
        return header + json_bytes

    # ---------- DESEMPACOTAR ----------
    @staticmethod
    def desempacotar(stream) -> Mensagem | None:
        """
        Lê um frame completo do stream e devolve a Mensagem.
        Retorna None se o stream fechou limpo (EOF entre mensagens).
        """
        header = Protocolo._read_exact(stream, 4)
        if header is None:
            return None

        tamanho = struct.unpack(">I", header)[0]
        json_bytes = Protocolo._read_exact(stream, tamanho)
        if json_bytes is None:
            raise EOFError("EOF inesperado no meio do payload")

        d = json.loads(json_bytes.decode("utf-8"))
        return Mensagem.from_dict(d)

    # ---------- HELPER ----------
    @staticmethod
    def _read_exact(stream, n: int) -> bytes | None:
        """Lê exatamente n bytes. None = EOF limpo."""
        buf = b""
        while len(buf) < n:
            chunk = stream.read(n - len(buf))
            if not chunk:
                if not buf:
                    return None
                raise EOFError(f"EOF: esperava {n}, recebeu {len(buf)}")
            buf += chunk
        return buf
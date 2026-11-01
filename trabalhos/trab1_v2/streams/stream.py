import json
import io

from ..modelos.models import Ataque

class AtaqueOutputStream(io.RawIOBase):
    def __init__(self, destino, ataques, quantidade):
        super().__init__()
        self.destino = destino
        self.ataques = ataques
        self.quantidade = quantidade

    def writable(self):
        return not self.closed and self.destino.writable()

    def write(self, b):
        if self.closed:
            raise ValueError("I/O operation on closed stream")
        dados = memoryview(b).cast("B")
        total = 0
        while total < len(dados):
            escritos = self.destino.write(dados[total:])
            if escritos is None or escritos <= 0:
                raise OSError("destino não aceitou os dados")
            total += escritos
        return total

    def flush(self):
        if not self.closed:
            self.destino.flush()

    def enviar_dados(self):
        enviados = 0
        for ataque in self.ataques[:self.quantidade]:
            texto = json.dumps(ataque.to_dict()) + "\n"
            self.write(texto.encode("utf-8"))
            enviados += 1
        self.flush()
        return enviados


class AtaqueInputStream(io.RawIOBase):
    def __init__(self, origem):
        super().__init__()
        self.origem = origem

    def readable(self):
        return not self.closed and self.origem.readable()

    def readinto(self, b):
        if self.closed:
            raise ValueError("I/O operation on closed stream")
        dados = self.origem.read(len(b))
        if dados is None:
            return None
        tamanho = len(dados)
        b[:tamanho] = dados
        return tamanho

    def receber_dados(self):
        ataques = []
        for linha in self:
            if linha.strip():
                dados = json.loads(linha.decode("utf-8"))
                ataques.append(Ataque.from_dict(dados))
        return ataques

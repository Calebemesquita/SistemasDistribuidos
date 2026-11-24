import io
import json
import struct
from POJO import RelatorioIncidente


# io.RawIOBase -> classe abstrata do python
# stream binario de saida
# ganhamos aqui metodos como 
# readable, seekable, close

class IncidenteOutputStream(io.RawIOBase):
    """
    OutputStream que envia um array de RelatorioIncidente
    para um destino qualquer que pode ser 
        stdout
        arquivo
        socket TCP

    
    Formato do stream:
        [
            [4 bytes big-endian: tamanho do JSON][JSON UTF-8 do objeto]
            [4 bytes big-endian: tamanho do JSON][JSON UTF-8 do objeto]
            ...
        ]
    """

    def __init__(self, destino, objetos: list[RelatorioIncidente], quantidade: int):
        super().__init__()
        self._destino = destino                 # onde vou escrever
        self._objetos = objetos                 # lista de objetos POJO [relatorio1, relatorio2, ...]
        self._quantidade = max(0, quantidade)   # quantidade que vou enviar, 3 primeiros, 2 primerios, etc


    """ Pegunta se pode escrever aqui"""
    def writable(self) -> bool:
        return True

    """ Recebo b bytes e retorno inteiro"""
    def write(self, b: bytes) -> int:
        view = memoryview(b)
        total = 0
        while total < len(view):
            # Note qeu esse write é do destino (Rede, arquivo, STDOUT)
            # note que view[total:] vai pegar do começo ate onde ele conseguir dependendo de rede, socket, arquivo, saida
            # e ele vai começar total na proxima vez, (que vai ser incrementado pelo escritos)
            escritos = self._destino.write(view[total:])
            if escritos is None:

                # Alguns destinos binários documentam write() sem retorno.
                # Nesse caso pegamos tamanho da view e diminui pelo total 
                escritos = len(view) - total
            if escritos <= 0:
                raise OSError("o destino não conseguiu gravar os dados")
            total += escritos
        return total


    # verificamos aqui se rede, arquivo, ou saida padrão tem 
    # flush
    # e 
    # Verifica se a porta do buffer esta fechada
    def flush(self) -> None:
        if hasattr(self._destino, "flush") and not getattr(self._destino, "closed", False):
            self._destino.flush()

    def close(self) -> None:
        try:
            self.flush()
        finally:
            super().close()

    def escrever_objetos(self) -> int:
        total = 0                                                                               # contar os bytes
        for i in range(min(self._quantidade, len(self._objetos))):
            obj = self._objetos[i]
            json_bytes = json.dumps(obj.to_dict(), ensure_ascii=False).encode("utf-8")          # ensure_ascci mantém formatção do brasil sem estragar os acentos.

            # crio um header passa para ele um
            # struct.pack traduz nuemros humanos para binarios
            # ">I"
            #   I - Pega o len(json_bytes) forçe ele a ocupar 4bytes
            #   > Big-Endian. É a "regra gramatical" oficial da internet, para ler normal
            header = struct.pack(">I", len(json_bytes))

            # monta pacote 4bytes header  e json
            total += self.write(header)
            total += self.write(json_bytes)

        self.flush()
        return total

class ConexaoDeRedeLenta:
    """ Simula um destino (socket ou arquivo) que não grava tudo de uma vez. """
    def write(self, b) -> int:
        # Pega no máximo 3 bytes da view que recebeu
        pedaco = b[:3]
        
        # Converte a view de volta para bytes só para imprimir na tela
        print(f"[Hardware] Gravando pedaço: {bytes(pedaco)}") 
        
        # Retorna quantos bytes realmente conseguiu gravar
        return len(pedaco)

class MeuGravador:
    def __init__(self, destino):
        self._destino = destino

    def write(self, b: bytes) -> int:
        """ Recebo b bytes e retorno inteiro """
        view = memoryview(b)
        total = 0
        while total < len(view):
            escritos = self._destino.write(view[total:])
            
            if escritos is None:
                # Alguns destinos binários documentam write() sem retorno.
                escritos = len(view) - total
            if escritos <= 0:
                raise OSError("o destino não conseguiu gravar os dados")
            
            total += escritos
            print(f" -> Progresso: {total}/{len(view)} bytes gravados.\n")
            
        return total

destino_lento = ConexaoDeRedeLenta()
gravador = MeuGravador(destino_lento)

dados_grandes = b"Python_MemoryView_emuitomassabixokajsajjsksajkjskajskajs"

print("Iniciando a gravacao...")
total_gravado = gravador.write(dados_grandes)

print(f"Sucesso! Total gravado: {total_gravado} bytes.")
"""
Cliente TCP para teste de stream com origem remota (item 2.d).

O cliente conecta no servidor, envolve o socket num objeto binário
(socket.makefile("rb")) e usa esse objeto como origem de um
CandidatoInputStream — a MESMA classe usada nos testes com stdin e
arquivo, só muda o que é passado no construtor.

Uso (em dois terminais, depois de iniciar o servidor):
    python -m sockets_streams.servidor_tcp
    python -m sockets_streams.cliente_tcp
"""

import socket
import sys
import time

from common.streams import CandidatoInputStream

HOST = "127.0.0.1"
PORTA = 5050


def executar(host: str = HOST, porta: int = PORTA, tentativas: int = 10):
    ultimo_erro = None
    for _ in range(tentativas):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((host, porta))
                print(f"[cliente_tcp] Conectado ao servidor {host}:{porta}")
                origem = sock.makefile("rb")
                stream = CandidatoInputStream(origem)
                votos = stream.ler_todos()
                for v in votos:
                    print(f"Voto lido: eleitor={v.id_eleitor} candidato={v.id_candidato} ts={v.timestamp}")
                print(f"Total lido via TCP: {len(votos)} voto(s)")
                return votos
        except ConnectionRefusedError as e:
            ultimo_erro = e
            time.sleep(0.3)  # servidor pode ainda não estar pronto
    print(f"[cliente_tcp] Não foi possível conectar em {host}:{porta}: {ultimo_erro}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    executar()

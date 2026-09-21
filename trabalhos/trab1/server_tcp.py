"""
Servidor TCP para teste de stream com destino remoto (item 1.d).

O servidor aceita uma conexão, envolve o socket num objeto binário
(socket.makefile("wb")) e usa esse objeto como destino de um
CandidatoOutputStream — ou seja, a MESMA classe usada nos testes com
stdout e arquivo, só muda o que é passado no construtor.

Uso:
    python -m sockets_streams.servidor_tcp
"""
import socket
import time

from common.pojos import Voto
from common.streams import CandidatoOutputStream

HOST = "0.0.0.0"
PORTA = 5050


def votos_de_exemplo():
    agora = int(time.time())
    return [
        Voto(id_eleitor=1, id_candidato=10, timestamp=agora),
        Voto(id_eleitor=2, id_candidato=11, timestamp=agora),
        Voto(id_eleitor=3, id_candidato=10, timestamp=agora),
        Voto(id_eleitor=4, id_candidato=12, timestamp=agora),
        Voto(id_eleitor=5, id_candidato=10, timestamp=agora),
    ]


def executar(host: str = HOST, porta: int = PORTA):
    votos = votos_de_exemplo()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((host, porta))
        servidor.listen(1)
        print(f"[servidor_tcp] Escutando em {host}:{porta}, aguardando cliente...")

        conexao, endereco = servidor.accept()
        print(f"[servidor_tcp] Cliente conectado: {endereco}")
        with conexao:
            destino = conexao.makefile("wb")
            stream = CandidatoOutputStream(destino, votos, len(votos))
            stream.escrever()
            destino.close()
            print(f"[servidor_tcp] {len(votos)} votos enviados via TCP para {endereco}")


if __name__ == "__main__":
    executar()

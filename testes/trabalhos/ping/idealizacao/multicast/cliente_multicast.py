import json
import socket
import struct
import sys
import threading

from .servidor_multicast import (
    GRUPO_MULTICAST,
    HOST_TCP,
    INTERFACE_MULTICAST,
    PORTA_MULTICAST,
    PORTA_TCP,
)


'''
Login -
retorna um dict com grupo e porta multicast liberados
'''
def autenticar(cliente_id: str, host: str = HOST_TCP, porta: int = PORTA_TCP) -> dict:
    with socket.create_connection((host, porta)) as conexao, conexao.makefile("rwb") as fluxo:
        fluxo.write((json.dumps({"cliente_id": cliente_id}) + "\n").encode("utf-8"))
        fluxo.flush()
        resposta = json.loads(fluxo.readline().decode("utf-8"))
    return resposta




"""
entrar no grupo abre um socket UDP e entra no
grupo multicast
"""
def entrar_no_grupo(grupo: str = GRUPO_MULTICAST, porta: int = PORTA_MULTICAST) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", porta))

    mreq = struct.pack(
        "4s4s", socket.inet_aton(grupo), socket.inet_aton(INTERFACE_MULTICAST)
    )

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return sock



"""
Sai do grupo e remove o socket 
"""
def sair_do_grupo(sock: socket.socket, grupo: str = GRUPO_MULTICAST) -> None:
    try:
        mreq = struct.pack(
            "4s4s", socket.inet_aton(grupo), socket.inet_aton(INTERFACE_MULTICAST)
        )
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
    except OSError:
        pass
    sock.close()




"""
Classe cliente multicast
"""
class ClienteMulticast:
    def __init__(self, cliente_id: str):
        self.cliente_id = cliente_id
        self.sock = None
        self._executando = threading.Event()

    def escutar(self) -> None:
        while self._executando.is_set():
            try:
                dados, _ = self.sock.recvfrom(4096)
            except OSError:
                break
            alerta = json.loads(dados.decode("utf-8"))
            print(f"\n[{alerta['tipo']}] {alerta['mensagem']}  ({alerta['timestamp']})")


    def interagir(self) -> None:
        print("Conectado. Digite 'sair' para encerrar.")
        while self._executando.is_set():
            comando = input("> ").strip().lower()
            if comando in {"sair", "exit", "quit"}:
                self.parar()
                break


    def iniciar(self) -> None:
        resposta = autenticar(self.cliente_id)
        if not resposta.get("sucesso"):
            raise RuntimeError(resposta.get("erro", "falha na autenticação"))

        self.sock = entrar_no_grupo(resposta["grupo"], resposta["porta_multicast"])
        self._executando.set()

        thread_escuta = threading.Thread(target=self.escutar, daemon=True)
        thread_interacao = threading.Thread(target=self.interagir, daemon=True)
        thread_escuta.start()
        thread_interacao.start()
        thread_interacao.join()
        self.parar()
        thread_escuta.join(timeout=1)

    def parar(self) -> None:
        self._executando.clear()
        if self.sock:
            sair_do_grupo(self.sock)


if __name__ == "__main__":
    nome = sys.argv[1] if len(sys.argv) > 1 else "cliente-1"
    ClienteMulticast(nome).iniciar()

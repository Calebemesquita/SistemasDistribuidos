import json
import os
import socket
import struct
import threading
import time

from ..servicos.sevice import ServicoNotificacao


INTERFACE_MULTICAST = os.environ.get("MULTICAST_INTERFACE", "127.0.0.1")
HOST_TCP, PORTA_TCP = "127.0.0.1", 5052    
GRUPO_MULTICAST = "230.0.0.1"              
PORTA_MULTICAST = 5007                  

servico_notificacao = ServicoNotificacao()



def criar_socket_multicast_envio() -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ttl = struct.pack("b", 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    sock.setsockopt(
        socket.IPPROTO_IP,
        socket.IP_MULTICAST_IF,
        socket.inet_aton(INTERFACE_MULTICAST),
    )
    return sock


def enviar_multicast(sock: socket.socket, tipo: str, mensagem: str) -> dict:
    alerta = servico_notificacao.montar_alerta(tipo, mensagem)
    dados = json.dumps(alerta).encode("utf-8")
    sock.sendto(dados, (GRUPO_MULTICAST, PORTA_MULTICAST))
    return alerta


def enviar_varios_concorrentemente(sock: socket.socket, alertas) -> list:
    resultados = []
    lock = threading.Lock()

    def _publicar(tipo, mensagem):
        alerta = enviar_multicast(sock, tipo, mensagem)
        with lock:
            resultados.append(alerta)

    threads = [threading.Thread(target=_publicar, args=par) for par in alertas]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return resultados


class ServidorAutenticacao:
    def __init__(self, host: str = HOST_TCP, porta: int = PORTA_TCP):
        self.host = host
        self.porta = porta
        self._lock = threading.Lock()
        self._socket_servidor = None

    def autenticar(self, credenciais: dict) -> dict:
        cliente_id = credenciais.get("cliente_id")
        if not cliente_id:
            return {"sucesso": False, "erro": "cliente_id obrigatório"}
        with self._lock:
            servico_notificacao.inscrever(cliente_id)
        return {
            "sucesso": True,
            "grupo": GRUPO_MULTICAST,
            "porta_multicast": PORTA_MULTICAST,
        }

    def atender_cliente(self, conexao, endereco) -> None:
        with conexao, conexao.makefile("rwb") as fluxo:
            linha = fluxo.readline()
            if not linha:
                return
            credenciais = json.loads(linha.decode("utf-8"))
            resposta = self.autenticar(credenciais)
            fluxo.write((json.dumps(resposta) + "\n").encode("utf-8"))
            fluxo.flush()

    def iniciar_socket(self) -> socket.socket:
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((self.host, self.porta))
        servidor.listen()
        self.porta = servidor.getsockname()[1]
        self._socket_servidor = servidor
        return servidor

    def executar(self) -> None:
        servidor = self._socket_servidor or self.iniciar_socket()
        while True:
            conexao, endereco = servidor.accept()
            threading.Thread(
                target=self.atender_cliente, args=(conexao, endereco), daemon=True
            ).start()

    def executar_em_thread(self) -> int:
        self.iniciar_socket()
        threading.Thread(target=self.executar, daemon=True).start()
        return self.porta


def executar_servidor_completo():
    auth = ServidorAutenticacao()
    auth.executar_em_thread()
    sock_envio = criar_socket_multicast_envio()
    print(f"Pronto para publicar em {GRUPO_MULTICAST}:{PORTA_MULTICAST}")
    return sock_envio


def _heartbeat(sock: socket.socket) -> None:
    while True:
        time.sleep(20)
        enviar_multicast(sock, "ATUALIZACAO", "heartbeat do servidor")


def _console_admin(sock: socket.socket) -> None:
    print("Console do admin: digite uma mensagem para publicar como ALERTA ou 'sair'.")
    while True:
        try:
            texto = input("> ").strip()
        except EOFError:
            break
        if texto.lower() in {"sair", "exit", "quit"}:
            break
        if texto:
            enviar_multicast(sock, "ALERTA", texto)


if __name__ == "__main__":
    sock = executar_servidor_completo()
    threading.Thread(target=_heartbeat, args=(sock,), daemon=True).start()
    try:
        _console_admin(sock)
    except KeyboardInterrupt:
        pass

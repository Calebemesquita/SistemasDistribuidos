"""Cliente interativo de votação com listener UDP em thread própria."""
from __future__ import annotations

import json
import socket
import threading

from Q3.mensagem import Mensagem
from Q3.protocolo import Protocolo
from .servidor import GRUPO, MULTICAST_INTERFACE, PORTA_TCP, PORTA_UDP

HOST = "127.0.0.1"


def escutar_notas(parar: threading.Event) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", PORTA_UDP))
        membership = socket.inet_aton(GRUPO) + socket.inet_aton(MULTICAST_INTERFACE)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
        sock.settimeout(0.5)
        while not parar.is_set():
            try:
                dados, _ = sock.recvfrom(65_507)
            except socket.timeout:
                continue
            try:
                nota = json.loads(dados.decode("utf-8"))
                print(f"\n[NOTA {nota.get('timestamp')}] {nota.get('autor')}: {nota.get('mensagem')}\n> ", end="", flush=True)
            except (UnicodeDecodeError, json.JSONDecodeError):
                print("\n[NOTA] mensagem multicast inválida\n> ", end="", flush=True)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, membership)


class ClienteVotacao:
    def __init__(self) -> None:
        self.sock = socket.create_connection((HOST, PORTA_TCP))
        self.entrada = self.sock.makefile("rb")
        self.saida = self.sock.makefile("wb")
        self.proximo_id = 1

    def requisitar(self, tipo: str, payload: dict | None = None) -> Mensagem:
        req = Mensagem(tipo=tipo, id=self.proximo_id, payload=payload)
        self.proximo_id += 1
        self.saida.write(Protocolo.empacotar(req))
        self.saida.flush()
        resposta = Protocolo.desempacotar(self.entrada)
        if resposta is None:
            raise ConnectionError("servidor encerrou a conexão")
        print(resposta.payload if resposta.status == "OK" else f"ERRO: {resposta.payload.get('mensagem')}")
        return resposta

    def fechar(self) -> None:
        self.entrada.close()
        self.saida.close()
        self.sock.close()


def main() -> None:
    cliente = ClienteVotacao()
    parar = threading.Event()
    listener = None
    try:
        usuario = input("Usuário: ").strip()
        senha = input("Senha: ").strip()
        login = cliente.requisitar("LOGIN", {"usuario": usuario, "senha": senha})
        if login.status != "OK":
            return
        papel = login.payload["papel"]
        listener = threading.Thread(target=escutar_notas, args=(parar,), daemon=True)
        listener.start()
        print("Comandos: candidatos | votar ID | nota TEXTO (admin) | adicionar NOME | remover ID | resultado | sair")
        while True:
            linha = input("> ").strip()
            comando, _, argumento = linha.partition(" ")
            try:
                if comando in {"sair", "quit", "exit"}:
                    break
                if comando == "candidatos":
                    cliente.requisitar("LISTAR_CANDIDATOS")
                elif comando == "votar":
                    cliente.requisitar("VOTAR", {"candidato_id": int(argumento)})
                elif comando == "nota":
                    cliente.requisitar("NOTA", {"mensagem": argumento})
                elif comando == "adicionar":
                    cliente.requisitar("ADICIONAR_CANDIDATO", {"nome": argumento})
                elif comando == "remover":
                    cliente.requisitar("REMOVER_CANDIDATO", {"id": int(argumento)})
                elif comando == "resultado":
                    cliente.requisitar("RESULTADO")
                else:
                    print("Comando desconhecido")
            except ValueError:
                print("Informe os argumentos numéricos nos comandos votar/remover")
    except (EOFError, KeyboardInterrupt, OSError, ConnectionError) as exc:
        if str(exc): print(f"[cliente] {exc}")
    finally:
        parar.set()
        if listener is not None: listener.join(timeout=2)
        cliente.fechar()


if __name__ == "__main__":
    main()

"""Cliente: autenticação TCP, joinGroup UDP e escuta concorrente."""
from __future__ import annotations

import json
import os
import socket
import threading

HOST = "127.0.0.1"
PORTA_TCP = 7000
MULTICAST_INTERFACE = os.environ.get("MULTICAST_INTERFACE", "0.0.0.0")


def autenticar(usuario: str, senha: str) -> tuple[str, int]:
    with socket.create_connection((HOST, PORTA_TCP), timeout=5) as sock:
        sock.sendall((json.dumps({"usuario": usuario, "senha": senha}) + "\n").encode("utf-8"))
        resposta = json.loads(sock.makefile("rb").readline().decode("utf-8"))
    if not resposta.get("ok"):
        raise PermissionError(resposta.get("mensagem", "acesso negado"))
    return resposta["grupo"], resposta["porta"]


def escutar(grupo: str, porta: int, parar: threading.Event) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", porta))
        membership = socket.inet_aton(grupo) + socket.inet_aton(MULTICAST_INTERFACE)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
        sock.settimeout(0.5)
        print(f"[cliente] joinGroup({grupo}:{porta}) concluído; digite sair para encerrar")
        while not parar.is_set():
            try:
                dados, _ = sock.recvfrom(65_507)
            except socket.timeout:
                continue
            try:
                evento = json.loads(dados.decode("utf-8"))
                print(f"\n[{evento.get('timestamp')}] {evento.get('tipo')}: {evento.get('mensagem')}\n> ", end="", flush=True)
            except (UnicodeDecodeError, json.JSONDecodeError):
                print("\n[multicast] pacote inválido\n> ", end="", flush=True)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, membership)
        print("\n[cliente] leaveGroup concluído")


def main() -> None:
    usuario = input("Usuário: ").strip()
    senha = input("Senha: ").strip()
    grupo, porta = autenticar(usuario, senha)
    parar = threading.Event()
    listener = threading.Thread(target=escutar, args=(grupo, porta, parar), daemon=True)
    listener.start()
    try:
        while input("> ").strip().lower() not in {"sair", "quit", "exit"}:
            pass
    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        parar.set()
        listener.join(timeout=2)


if __name__ == "__main__":
    main()

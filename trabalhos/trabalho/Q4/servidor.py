"""Autentica clientes por TCP e publica notificações em UDP multicast."""
from __future__ import annotations

import json
import os
import socket
import threading
from datetime import datetime, timezone

HOST = "0.0.0.0"
PORTA_TCP = 7000
GRUPO = "239.10.10.10"
PORTA_UDP = 7001
# Endereço da interface local usada para multicast; 0.0.0.0 deixa a escolha ao SO.
MULTICAST_INTERFACE = os.environ.get("MULTICAST_INTERFACE", "0.0.0.0")
# Credenciais de demonstração. Em produção, use armazenamento seguro de senhas.
USUARIOS = {"admin": "admin123", "aluno": "aluno123", "ana": "ana123"}


def ler_linha(sock: socket.socket) -> dict:
    dados = bytearray()
    while True:
        parte = sock.recv(1)
        if not parte:
            raise ConnectionError("cliente encerrou antes de enviar a requisição")
        if parte == b"\n":
            return json.loads(dados.decode("utf-8"))
        dados.extend(parte)
        if len(dados) > 16_384:
            raise ValueError("requisição muito grande")


class ServidorMulticast:
    def __init__(self) -> None:
        self._socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._socket_udp.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        self._socket_udp.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        if MULTICAST_INTERFACE != "0.0.0.0":
            self._socket_udp.setsockopt(
                socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(MULTICAST_INTERFACE)
            )
        self._lock = threading.Lock()

    def autenticar_cliente(self, conn: socket.socket, endereco) -> None:
        with conn:
            try:
                req = ler_linha(conn)
                usuario, senha = req.get("usuario"), req.get("senha")
                ok = isinstance(usuario, str) and USUARIOS.get(usuario) == senha
                resp = {"ok": ok, "grupo": GRUPO, "porta": PORTA_UDP,
                        "mensagem": "autenticado" if ok else "credenciais inválidas"}
                conn.sendall((json.dumps(resp, ensure_ascii=False) + "\n").encode("utf-8"))
                print(f"[tcp] {endereco}: {'autenticado' if ok else 'negado'}")
            except (ConnectionError, ValueError, json.JSONDecodeError, OSError) as exc:
                print(f"[tcp] erro com {endereco}: {exc}")

    def enviar(self, tipo: str, mensagem: str) -> None:
        pacote = json.dumps({
            "tipo": tipo.upper(), "mensagem": mensagem,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, ensure_ascii=False).encode("utf-8")
        with self._lock:
            self._socket_udp.sendto(pacote, (GRUPO, PORTA_UDP))
        print(f"[multicast] {tipo.upper()}: {mensagem}")

    def iniciar(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            servidor.bind((HOST, PORTA_TCP))
            servidor.listen()
            print(f"Autenticação TCP em :{PORTA_TCP}; multicast {GRUPO}:{PORTA_UDP}")
            print("Comandos: NOTIFICACAO mensagem | ALERTA mensagem | ATUALIZACAO mensagem | sair")
            threading.Thread(target=self._aceitar, args=(servidor,), daemon=True).start()
            try:
                while True:
                    linha = input("> ").strip()
                    if linha.lower() in {"sair", "quit", "exit"}:
                        break
                    tipo, _, mensagem = linha.partition(" ")
                    if tipo.upper() not in {"NOTIFICACAO", "ALERTA", "ATUALIZACAO"} or not mensagem:
                        print("Use: NOTIFICACAO|ALERTA|ATUALIZACAO mensagem")
                        continue
                    threading.Thread(
                        target=self.enviar, args=(tipo, mensagem), daemon=True
                    ).start()
            except (EOFError, KeyboardInterrupt):
                pass
            finally:
                self._socket_udp.close()
                print("Servidor encerrado.")

    def _aceitar(self, servidor: socket.socket) -> None:
        while True:
            try:
                conn, addr = servidor.accept()
            except OSError:
                return
            threading.Thread(target=self.autenticar_cliente, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    ServidorMulticast().iniciar()

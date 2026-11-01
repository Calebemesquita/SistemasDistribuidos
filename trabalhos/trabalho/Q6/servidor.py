"""Servidor multithreaded de votação: TCP para operações e UDP para notas."""
from __future__ import annotations

import os
import socket
import threading
import time

from Q3.mensagem import Mensagem
from Q3.protocolo import Protocolo

HOST = "0.0.0.0"
PORTA_TCP = 7100
GRUPO = "239.10.10.20"
PORTA_UDP = 7101
MULTICAST_INTERFACE = os.environ.get("MULTICAST_INTERFACE", "0.0.0.0")
# Contas de demonstração; altere antes de qualquer uso real.
ADMINISTRADORES = {"admin": "admin123"}
ELEITORES = {"ana": "ana123", "bia": "bia123", "caio": "caio123"}
CANDIDATOS_INICIAIS = {1: "Alice", 2: "Bruno", 3: "Carla"}
DURACAO_SEGUNDOS = int(os.environ.get("VOTACAO_DURACAO_SEGUNDOS", "120"))


class EstadoVotacao:
    def __init__(self, duracao: int = DURACAO_SEGUNDOS) -> None:
        self.inicio = time.monotonic()
        self.prazo = self.inicio + duracao
        self.candidatos = CANDIDATOS_INICIAIS.copy()
        self.votos: dict[int, str] = {}
        self.proximo_id = max(self.candidatos, default=0) + 1
        self.lock = threading.RLock()
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        self.udp.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        if MULTICAST_INTERFACE != "0.0.0.0":
            self.udp.setsockopt(
                socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(MULTICAST_INTERFACE)
            )

    def aberta(self) -> bool:
        return time.monotonic() < self.prazo

    def processar(self, req: Mensagem, usuario: str | None = None, papel: str | None = None) -> Mensagem:
        try:
            with self.lock:
                tipo, dados = req.tipo, req.payload
                if tipo == "LOGIN":
                    nome, senha = dados.get("usuario"), dados.get("senha")
                    if ADMINISTRADORES.get(nome) == senha:
                        return self.reply(req, {"papel": "admin", "candidatos": self.lista_candidatos(), "prazo_restante": self.restante()})
                    if ELEITORES.get(nome) == senha:
                        return self.reply(req, {"papel": "eleitor", "candidatos": self.lista_candidatos(), "prazo_restante": self.restante()})
                    return self.erro(req, "usuário ou senha inválidos")

                if usuario is None or papel is None:
                    return self.erro(req, "faça login antes da operação")
                if tipo == "LISTAR_CANDIDATOS":
                    return self.reply(req, {"candidatos": self.lista_candidatos(), "prazo_restante": self.restante()})
                if tipo == "VOTAR":
                    if papel != "eleitor": return self.erro(req, "operação exclusiva para eleitores")
                    if not self.aberta(): return self.erro(req, "prazo de votação encerrado")
                    if usuario in self.votos: return self.erro(req, "este eleitor já votou")
                    candidato_id = dados.get("candidato_id")
                    if candidato_id not in self.candidatos: return self.erro(req, "candidato inexistente")
                    self.votos[usuario] = candidato_id
                    return self.reply(req, {"mensagem": "voto registrado"})
                if tipo == "ADICIONAR_CANDIDATO":
                    if papel != "admin": return self.erro(req, "operação exclusiva para administradores")
                    if not self.aberta(): return self.erro(req, "prazo de votação encerrado")
                    nome = dados.get("nome")
                    if not isinstance(nome, str) or not nome.strip(): return self.erro(req, "nome inválido")
                    candidato_id = self.proximo_id
                    self.proximo_id += 1
                    self.candidatos[candidato_id] = nome.strip()
                    return self.reply(req, {"id": candidato_id, "nome": nome.strip()})
                if tipo == "REMOVER_CANDIDATO":
                    if papel != "admin": return self.erro(req, "operação exclusiva para administradores")
                    if not self.aberta(): return self.erro(req, "prazo de votação encerrado")
                    candidato_id = dados.get("id")
                    if candidato_id not in self.candidatos: return self.erro(req, "candidato inexistente")
                    if candidato_id in self.votos.values(): return self.erro(req, "não é possível remover candidato que recebeu voto")
                    nome = self.candidatos.pop(candidato_id)
                    return self.reply(req, {"removido": nome})
                if tipo == "RESULTADO":
                    if papel != "admin": return self.erro(req, "resultados disponíveis apenas para administradores")
                    if self.aberta(): return self.erro(req, f"votação ainda aberta por {self.restante()} segundo(s)")
                    return self.reply(req, self.calcular_resultado())
                if tipo == "NOTA":
                    if papel != "admin": return self.erro(req, "operação exclusiva para administradores")
                    texto = dados.get("mensagem")
                    if not isinstance(texto, str) or not texto.strip(): return self.erro(req, "nota vazia")
                    self.enviar_nota(usuario, texto.strip())
                    return self.reply(req, {"mensagem": "nota enviada por multicast"})
                return self.erro(req, f"operação desconhecida: {tipo}")
        except (KeyError, TypeError, ValueError) as exc:
            return self.erro(req, f"requisição inválida: {exc}")

    @staticmethod
    def reply(req: Mensagem, payload: dict) -> Mensagem:
        return Mensagem(tipo=req.tipo, id=req.id, payload=payload)

    @staticmethod
    def erro(req: Mensagem, texto: str) -> Mensagem:
        return Mensagem(tipo=req.tipo, id=req.id, status="ERRO", payload={"mensagem": texto})

    def lista_candidatos(self) -> list[dict]:
        return [{"id": i, "nome": nome} for i, nome in self.candidatos.items()]

    def restante(self) -> int:
        return max(0, int(self.prazo - time.monotonic() + 0.999))

    def calcular_resultado(self) -> dict:
        contagem = {ident: 0 for ident in self.candidatos}
        for ident in self.votos.values():
            if ident in contagem:
                contagem[ident] += 1
        total = sum(contagem.values())
        candidatos = [{"id": ident, "nome": nome, "votos": contagem[ident],
                       "percentual": round(contagem[ident] * 100 / total, 2) if total else 0.0}
                      for ident, nome in self.candidatos.items()]
        maior = max(contagem.values(), default=0)
        ganhadores = [c["nome"] for c in candidatos if c["votos"] == maior and maior > 0]
        return {"total_votos": total, "candidatos": candidatos,
                "ganhador": ganhadores[0] if len(ganhadores) == 1 else ("Empate: " + ", ".join(ganhadores) if ganhadores else None)}

    def enviar_nota(self, autor: str, texto: str) -> None:
        import json
        from datetime import datetime, timezone
        pacote = json.dumps({"tipo": "NOTA", "autor": autor, "mensagem": texto,
                             "timestamp": datetime.now(timezone.utc).isoformat()}, ensure_ascii=False).encode("utf-8")
        self.udp.sendto(pacote, (GRUPO, PORTA_UDP))


class ServidorVotacao:
    def __init__(self) -> None:
        self.estado = EstadoVotacao()

    def tratar_cliente(self, conn: socket.socket, addr) -> None:
        usuario = papel = None
        with conn, conn.makefile("rb") as entrada, conn.makefile("wb") as saida:
            try:
                while True:
                    req = Protocolo.desempacotar(entrada)
                    if req is None: return
                    if req.tipo == "LOGIN":
                        resposta = self.estado.processar(req)
                        if resposta.status == "OK":
                            usuario = req.payload.get("usuario")
                            papel = resposta.payload["papel"]
                    else:
                        resposta = self.estado.processar(req, usuario, papel)
                    saida.write(Protocolo.empacotar(resposta))
                    saida.flush()
            except (OSError, EOFError, ValueError) as exc:
                print(f"[tcp] cliente {addr} desconectado: {exc}")

    def iniciar(self) -> None:
        print(f"Votação aberta por {DURACAO_SEGUNDOS}s; TCP :{PORTA_TCP}; multicast {GRUPO}:{PORTA_UDP}")
        print("Admin: admin / admin123. Eleitores: ana/ana123, bia/bia123, caio/caio123.")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            servidor.bind((HOST, PORTA_TCP))
            servidor.listen()
            while True:
                conn, addr = servidor.accept()
                threading.Thread(target=self.tratar_cliente, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    ServidorVotacao().iniciar()

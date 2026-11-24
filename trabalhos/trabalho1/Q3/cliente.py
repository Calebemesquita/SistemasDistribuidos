import socket

from .mensagem import Mensagem
from .protocolo import Protocolo


HOST = "127.0.0.1"
PORT = 6000


class ClienteSerializacao:
    def __init__(self):
        self.sock = None
        self.stream_in = None
        self.stream_out = None
        self._proximo_id = 1

    def conectar(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.stream_in = self.sock.makefile("rb")
        self.stream_out = self.sock.makefile("wb")
        print(f"[cliente] conectado a {HOST}:{PORT}")

    def enviar(self, tipo: str, payload: dict | None = None) -> Mensagem:
        req = Mensagem(tipo=tipo, payload=payload, id=self._proximo_id)
        self._proximo_id += 1

        # 1. EMPACOTA e envia request
        pacote = Protocolo.empacotar(req)
        self.stream_out.write(pacote)
        self.stream_out.flush()
        print(f"[cliente] → request enviado: {req}")

        # 2. DESEMPACOTA reply
        reply = Protocolo.desempacotar(self.stream_in)
        if reply is None:
            raise ConnectionError("Servidor fechou a conexão")
        print(f"[cliente] ← reply recebido: {reply}")
        return reply

    def fechar(self):
        if self.stream_in:
            self.stream_in.close()
        if self.stream_out:
            self.stream_out.close()
        if self.sock:
            self.sock.close()
        print("[cliente] conexão encerrada")


# ---------- Demonstração ----------
if __name__ == "__main__":
    c = ClienteSerializacao()
    try:
        c.conectar()

        c.enviar("CRIAR_INCIDENTE", {
            "id": 1,
            "titulo": "Servidor caiu",
            "descricao": "CPU 100% no DC1",
            "severidade": "ALTA",
            "status": "ABERTO",
            "data_hora": None,
            "reportado_por": "joao",
            "local": "DC1",
        })
        c.enviar("BUSCAR_INCIDENTE", {"id": 1})
        c.enviar("LISTAR_INCIDENTES")
        c.enviar("CRIAR_RELATORIO", {
            "id": 1,
            "incidente_id": 1,
            "analista": "Ana",
            "conclusao": "Reiniciado",
            "acoes": "Reboot",
            "data_fechamento": None,
            "anexos": ["log.txt"],
        })
        c.enviar("BUSCAR_RELATORIO", {"id": 1})
        c.enviar("BUSCAR_INCIDENTE", {"id": 999})
    finally:
        c.fechar()

import socket

from POJO import Incidente, RelatorioIncidente
from servicos import ServicoIncidente, ServicoRelatorio
from .mensagem import Mensagem
from .protocolo import Protocolo


HOST = "127.0.0.1"
PORT = 6000


class ServidorSerializacao:
    def __init__(self):
        self.servico_incidente = ServicoIncidente()
        self.servico_relatorio = ServicoRelatorio()

    # ---------- Roteamento ----------
    def processar(self, req: Mensagem) -> Mensagem:
        """Recebe um request, devolve um reply."""
        try:
            if req.tipo == "CRIAR_INCIDENTE":
                inc = Incidente(**req.payload)
                novo_id = self.servico_incidente.criar_incidente(inc)
                return Mensagem(tipo=req.tipo, id=req.id,
                                payload={"incidente_id": novo_id})

            elif req.tipo == "BUSCAR_INCIDENTE":
                inc = self.servico_incidente.buscar_incidente(req.payload["id"])
                if inc is None:
                    return Mensagem(tipo=req.tipo, id=req.id, status="ERRO",
                                    payload={"mensagem": "Incidente não encontrado"})
                return Mensagem(tipo=req.tipo, id=req.id, payload=inc.to_dict())

            elif req.tipo == "LISTAR_INCIDENTES":
                lista = self.servico_incidente.listar_incidentes()
                return Mensagem(tipo=req.tipo, id=req.id,
                                payload={"incidentes": [i.to_dict() for i in lista]})

            elif req.tipo == "CRIAR_RELATORIO":
                rel = RelatorioIncidente.from_dict(req.payload)
                novo_id = self.servico_relatorio.criar_relatorio(rel)
                return Mensagem(tipo=req.tipo, id=req.id,
                                payload={"relatorio_id": novo_id})

            elif req.tipo == "BUSCAR_RELATORIO":
                rel = self.servico_relatorio.buscar_relatorio(req.payload["id"])
                if rel is None:
                    return Mensagem(tipo=req.tipo, id=req.id, status="ERRO",
                                    payload={"mensagem": "Relatório não encontrado"})
                return Mensagem(tipo=req.tipo, id=req.id, payload=rel.to_dict())

            else:
                return Mensagem(tipo=req.tipo, id=req.id, status="ERRO",
                                payload={"mensagem": f"Operação desconhecida: {req.tipo}"})

        except Exception as e:
            return Mensagem(tipo=req.tipo, id=req.id, status="ERRO",
                            payload={"mensagem": f"Erro no servidor: {e}"})

    # ---------- Loop principal ----------
    def servir_cliente(self, conn: socket.socket, addr: tuple[str, int]) -> None:
        print(f"[servidor] cliente conectado: {addr}")
        with conn.makefile("rb") as stream_in, conn.makefile("wb") as stream_out:
            while True:
                req = Protocolo.desempacotar(stream_in)
                if req is None:
                    print(f"[servidor] cliente desconectou: {addr}")
                    return

                print(f"[servidor] request recebido: {req}")
                reply = self.processar(req)
                stream_out.write(Protocolo.empacotar(reply))
                stream_out.flush()
                print(f"[servidor] reply enviado: {reply}")

    def iniciar(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind((HOST, PORT))
            srv.listen(5)
            print(f"[servidor] aguardando em {HOST}:{PORT}...")

            while True:
                conn, addr = srv.accept()
                with conn:
                    self.servir_cliente(conn, addr)


if __name__ == "__main__":
    ServidorSerializacao().iniciar()

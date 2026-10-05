import io
import unittest

from Q3.mensagem import Mensagem
from Q3.protocolo import Protocolo
from Q3.servidor import ServidorSerializacao


class LeituraEmPedacos(io.BytesIO):
    def read(self, size: int = -1) -> bytes:
        return super().read(min(size, 3) if size >= 0 else 3)


class TesteSerializacao(unittest.TestCase):
    def test_mensagem_serializada_e_lida_em_pedacos(self) -> None:
        original = Mensagem(
            tipo="BUSCAR_INCIDENTE",
            payload={"id": 17, "titulo": "Falha de rede"},
            id=4,
        )
        lida = Protocolo.desempacotar(LeituraEmPedacos(Protocolo.empacotar(original)))
        self.assertIsNotNone(lida)
        self.assertEqual(original.to_dict(), lida.to_dict())

    def test_request_reply_de_incidente_e_relatorio(self) -> None:
        servidor = ServidorSerializacao()

        criar_incidente = Mensagem(
            "CRIAR_INCIDENTE",
            {
                "id": 1,
                "titulo": "Servidor caiu",
                "descricao": "CPU alta",
                "severidade": "ALTA",
                "status": "ABERTO",
                "data_hora": None,
                "reportado_por": "Ana",
                "local": "DC1",
            },
            id=1,
        )
        reply = servidor.processar(criar_incidente)
        self.assertEqual("OK", reply.status)
        self.assertEqual({"incidente_id": 1}, reply.payload)

        buscar = servidor.processar(Mensagem("BUSCAR_INCIDENTE", {"id": 1}, id=2))
        self.assertEqual("OK", buscar.status)
        self.assertEqual("Servidor caiu", buscar.payload["titulo"])
        self.assertIsNotNone(buscar.payload["data_hora"])

        criar_relatorio = Mensagem(
            "CRIAR_RELATORIO",
            {
                "id": 8,
                "incidente_id": 1,
                "analista": "Bia",
                "conclusao": "Resolvido",
                "acoes": "Reiniciado",
                "data_fechamento": None,
                "anexos": [],
            },
            id=3,
        )
        reply_relatorio = servidor.processar(criar_relatorio)
        self.assertEqual("OK", reply_relatorio.status)
        lido = servidor.processar(Mensagem("BUSCAR_RELATORIO", {"id": 8}, id=4))
        self.assertEqual("OK", lido.status)
        self.assertEqual([], lido.payload["anexos"])
        self.assertIsNotNone(lido.payload["data_fechamento"])

    def test_operacao_inexistente_retorna_erro(self) -> None:
        reply = ServidorSerializacao().processar(Mensagem("BUSCAR_INCIDENTE", {"id": 9}))
        self.assertEqual("ERRO", reply.status)


if __name__ == "__main__":
    unittest.main()

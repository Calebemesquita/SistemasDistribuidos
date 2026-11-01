import io
import unittest
from datetime import datetime

from POJO import RelatorioIncidente
from fluxo import IncidenteInputStream, IncidenteOutputStream


class LeituraEmPedacos(io.BytesIO):
    """Origem de teste que devolve no máximo dois bytes por leitura."""

    def read(self, size: int = -1) -> bytes:
        return super().read(min(size, 2) if size >= 0 else 2)


class TesteStreams(unittest.TestCase):
    def setUp(self) -> None:
        self.relatorios = [
            RelatorioIncidente(1, 1, "Ana", "ok", "reboot", datetime(2024, 1, 2), []),
            RelatorioIncidente(
                2, 2, "Bia", "ok", "escalado", datetime(2024, 2, 3), ["log.txt"]
            ),
        ]
        self.buffer = io.BytesIO()
        IncidenteOutputStream(
            self.buffer, self.relatorios, len(self.relatorios)
        ).escrever_objetos()
        self.dados = self.buffer.getvalue()

    def test_round_trip_de_multiplos_objetos(self) -> None:
        lidos = IncidenteInputStream(io.BytesIO(self.dados)).ler_objetos()
        self.assertEqual(
            [item.to_dict() for item in self.relatorios],
            [item.to_dict() for item in lidos],
        )
        self.assertEqual([], lidos[0].anexos)

    def test_leituras_parciais(self) -> None:
        lidos = IncidenteInputStream(LeituraEmPedacos(self.dados)).ler_objetos()
        self.assertEqual(
            [item.to_dict() for item in self.relatorios],
            [item.to_dict() for item in lidos],
        )

    def test_eof_no_meio_do_cabecalho_ou_json(self) -> None:
        for dados_truncados in (b"\x00\x00", self.dados[:-1]):
            with self.subTest(dados=dados_truncados):
                with self.assertRaises(EOFError):
                    IncidenteInputStream(io.BytesIO(dados_truncados)).ler_objetos()

    def test_quantidade_exata(self) -> None:
        leitor = IncidenteInputStream(io.BytesIO(self.dados))
        self.assertEqual(1, len(leitor.ler_objetos(1)))
        with self.assertRaises(EOFError):
            IncidenteInputStream(io.BytesIO(self.dados)).ler_objetos(3)


if __name__ == "__main__":
    unittest.main()

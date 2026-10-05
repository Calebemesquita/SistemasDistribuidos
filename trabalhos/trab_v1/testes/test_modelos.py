import inspect
import unittest
from datetime import datetime

from POJO import Incidente, Registro, RelatorioIncidente, Serializavel


class TesteModelos(unittest.TestCase):
    def test_hierarquia_abstrata(self) -> None:
        self.assertTrue(issubclass(Registro, Serializavel))
        self.assertTrue(issubclass(Incidente, Registro))
        self.assertTrue(issubclass(RelatorioIncidente, Registro))
        with self.assertRaises(TypeError):
            Registro(1)

    def test_assinaturas_dos_construtores_preservadas(self) -> None:
        self.assertEqual(
            [
                "self", "id", "titulo", "descricao", "severidade", "status",
                "data_hora", "reportado_por", "local",
            ],
            list(inspect.signature(Incidente.__init__).parameters),
        )
        self.assertEqual(
            [
                "self", "id", "incidente_id", "analista", "conclusao", "acoes",
                "data_fechamento", "anexos",
            ],
            list(inspect.signature(RelatorioIncidente.__init__).parameters),
        )

    def test_agregacao_sem_alterar_dicionario_serializado(self) -> None:
        incidente = Incidente(1, "Falha", "Descrição", "ALTA", "ABERTO", None, "Ana", "DC1")
        relatorio = RelatorioIncidente(2, 1, "Bia", "Resolvido", "Reinício", None, [])
        incidente.adicionar_relatorio(relatorio)

        self.assertEqual([relatorio], incidente.getRelatorios())
        self.assertEqual(
            {
                "id", "titulo", "descricao", "severidade", "status", "data_hora",
                "reportado_por", "local",
            },
            set(incidente.to_dict()),
        )
        self.assertNotIn("relatorios", incidente.to_dict())
        self.assertTrue(incidente.remover_relatorio(relatorio))
        self.assertFalse(incidente.remover_relatorio(relatorio))

    def test_round_trip_preserva_campos_e_datas(self) -> None:
        data_incidente = datetime(2025, 4, 3, 12, 30)
        incidente = Incidente(4, "Rede", "Sem conexão", "MEDIA", "ABERTO", data_incidente, "Caio", "DC2")
        restaurado = Incidente.from_dict(incidente.to_dict())
        self.assertEqual(incidente.to_dict(), restaurado.to_dict())
        self.assertEqual(4, restaurado.getId())

        data_relatorio = datetime(2025, 4, 4, 9, 15)
        relatorio = RelatorioIncidente(8, 4, "Ana", "Resolvido", "Roteador reiniciado", data_relatorio, [])
        restaurado_relatorio = RelatorioIncidente.from_dict(relatorio.to_dict())
        self.assertEqual(relatorio.to_dict(), restaurado_relatorio.to_dict())
        self.assertEqual(8, restaurado_relatorio.getId())


if __name__ == "__main__":
    unittest.main()

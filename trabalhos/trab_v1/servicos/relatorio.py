from typing import Optional
from POJO import RelatorioIncidente


class ServicoRelatorio:
    def __init__(self):
        self._relatorios: dict[int, RelatorioIncidente] = {}

    def criar_relatorio(self, relatorio: RelatorioIncidente) -> int:
        self._relatorios[relatorio.getId()] = relatorio
        return relatorio.getId()

    def buscar_relatorio(self, id: int) -> Optional[RelatorioIncidente]:
        return self._relatorios.get(id)

    def listar_relatorios(self) -> list[RelatorioIncidente]:
        return list(self._relatorios.values())

    def atualizar_relatorio(self, relatorio: RelatorioIncidente) -> bool:
        if relatorio.getId() in self._relatorios:
            self._relatorios[relatorio.getId()] = relatorio
            return True
        return False

    def remover_relatorio(self, id: int) -> bool:
        return self._relatorios.pop(id, None) is not None

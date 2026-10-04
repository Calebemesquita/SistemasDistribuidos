from typing import Optional


from ..POJO import Incidente
from ..POJO import RelatorioIncidente

class ServicoIncidente:
    def __init__(self):
        self._incidentes: dict[int, Incidente] = {}

    def criar_incidente(self, incidente: Incidente) -> int:
        self._incidentes[incidente.getId()] = incidente
        return incidente.getId()

    def buscar_incidente(self, id: int) -> Optional[Incidente]:
        return self._incidentes.get(id)

    def listar_incidentes(self) -> list[Incidente]:
        return list(self._incidentes.values())

    def atualizar_incidente(self, incidente: Incidente) -> bool:
        if incidente.getId() in self._incidentes:
            self._incidentes[incidente.getId()] = incidente
            return True
        return False

    def remover_incidente(self, id: int) -> bool:
        return self._incidentes.pop(id, None) is not None


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
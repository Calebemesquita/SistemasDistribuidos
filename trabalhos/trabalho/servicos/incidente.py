from typing import Optional
from POJO import Incidente


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

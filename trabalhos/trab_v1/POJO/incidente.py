from __future__ import annotations
from datetime import datetime
from .registro import Registro
from .RelatorioIncidente import RelatorioIncidente


class Incidente(Registro):
    def __init__( self, id: int, titulo: str, descricao: str, severidade: str, status: str, data_hora: datetime | None, reportado_por: str, local: str):
        super().__init__(id)
        self.titulo = titulo
        self.descricao = descricao
        self.severidade = severidade
        self.status = status
        self.reportado_por = reportado_por
        self.data_hora = data_hora if data_hora is not None else datetime.now()
        self.local = local
        self.relatorios: list[RelatorioIncidente] = []

    def getTitulo(self) -> str: return self.titulo
    def getDesc(self) -> str: return self.descricao
    def getSeveridade(self) -> str: return self.severidade
    def getStatus(self) -> str: return self.status
    def getDataHora(self) -> datetime: return self.data_hora
    def getReportadoPor(self) -> str: return self.reportado_por
    def getLocal(self) -> str: return self.local

    def getRelatorios(self) -> list[RelatorioIncidente]: return self.relatorios
    def setTitulo(self, titulo: str) -> None: self.titulo = titulo
    def setDesc(self, descricao: str) -> None: self.descricao = descricao
    def setSeveridade(self, severidade: str) -> None: self.severidade = severidade
    def setStatus(self, status: str) -> None: self.status = status
    def setDataHora(self, data_hora: datetime) -> None: self.data_hora = data_hora
    def setReportadoPor(self, reportado_por: str) -> None: self.reportado_por = reportado_por
    def setLocal(self, local: str) -> None: self.local = local
    
    
    def adicionar_relatorio(self, relatorio: RelatorioIncidente) -> None: 
        self.relatorios.append(relatorio)
    
    def remover_relatorio(self, relatorio: RelatorioIncidente) -> bool:
        if relatorio not in self.relatorios:
            return False
        self.relatorios.remove(relatorio)
        return True

    def to_dict(self) -> dict:
        return {
            "id": self.getId(),
            "titulo": self.getTitulo(),
            "descricao": self.getDesc(),
            "severidade": self.getSeveridade(),
            "status": self.getStatus(),
            "data_hora": self.getDataHora().isoformat(),
            "reportado_por": self.getReportadoPor(),
            "local": self.getLocal(),
        }

    @staticmethod
    def from_dict(d: dict) -> Incidente:
        data_hora = d.get("data_hora")
        return Incidente(
            id=d["id"],
            titulo=d["titulo"],
            descricao=d["descricao"],
            severidade=d["severidade"],
            status=d["status"],
            data_hora=datetime.fromisoformat(data_hora) if data_hora else None,
            reportado_por=d["reportado_por"],
            local=d["local"],
        )

    def __str__(self) -> str:
        return (
            f"Incidente(id={self.id}, titulo='{self.titulo}', "
            f"severidade={self.severidade}, status={self.status})"
        )


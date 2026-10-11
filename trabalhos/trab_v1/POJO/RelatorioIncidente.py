from __future__ import annotations
from datetime import datetime
from .registro import Registro


class RelatorioIncidente(Registro):
    def __init__( self, id: int, incidente_id: int, analista: str, conclusao: str, acoes: str, data_fechamento: datetime | None, anexos: list[str] | None,):
        super().__init__(id)
        self.incidente_id = incidente_id
        self.analista = analista
        self.conclusao = conclusao
        self.acoes = acoes
        self.data_fechamento = (data_fechamento if data_fechamento is not None else datetime.now())
        self.anexos = anexos if anexos is not None else []

    def getIncidenteId(self) -> int: return self.incidente_id
    def getAnalista(self) -> str: return self.analista
    def getConclusao(self) -> str: return self.conclusao
    def getAcoes(self) -> str: return self.acoes
    def getDataFechamento(self) -> datetime: return self.data_fechamento
    def getAnexos(self) -> list[str]: return self.anexos

    def setIncidenteId(self, incidente_id: int) -> None: self.incidente_id = incidente_id
    def setAnalista(self, analista: str) -> None: self.analista = analista
    def setConclusao(self, conclusao: str) -> None: self.conclusao = conclusao
    def setAcoes(self, acoes: str) -> None: self.acoes = acoes
    def setDataFechamento(self, data_fechamento: datetime) -> None: self.data_fechamento = data_fechamento
    def setAnexos(self, anexos: list[str]) -> None: self.anexos = anexos

    def to_dict(self) -> dict:
        return {
            "id": self.getId(),
            "incidente_id": self.getIncidenteId(),
            "analista": self.getAnalista(),
            "conclusao": self.getConclusao(),
            "acoes": self.getAcoes(),
            "data_fechamento": self.getDataFechamento().isoformat(),
            "anexos": self.getAnexos(),
        }

    @staticmethod
    def from_dict(d: dict) -> RelatorioIncidente:
        data_fechamento = d.get("data_fechamento")
        return RelatorioIncidente(
            id=d["id"],
            incidente_id=d["incidente_id"],
            analista=d["analista"],
            conclusao=d["conclusao"],
            acoes=d["acoes"],
            data_fechamento=(
                datetime.fromisoformat(data_fechamento) if data_fechamento else None
            ),
            anexos=d.get("anexos", []),
        )

    def __str__(self) -> str:
        return (
            f"RelatorioIncidente(id={self.id}, "
            f"incidente_id={self.incidente_id}, "
            f"analista='{self.analista}', "
            f"data_fechamento={self.data_fechamento})"
        )





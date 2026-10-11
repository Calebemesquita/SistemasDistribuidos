"""Objeto de domínio usado nas mensagens de notificação."""
from __future__ import annotations

from datetime import datetime
from .registro import Registro


class Notificacao(Registro):
    def __init__(self, id: int, tipo: str, mensagem: str, timestamp: datetime | None = None,
                 incidente_id: int | None = None, autor: str = "") -> None:
        super().__init__(id)
        self.tipo = tipo
        self.mensagem = mensagem
        self.timestamp = timestamp or datetime.now()
        self.incidente_id = incidente_id
        self.autor = autor

    def getTipo(self) -> str: return self.tipo
    def getMensagem(self) -> str: return self.mensagem
    def getTimestamp(self) -> datetime: return self.timestamp
    def getIncidente_id(self) -> int | None: return self.incidente_id
    def getAutor(self) -> str: return self.autor

    def setTipo(self, tipo: str) -> None: self.tipo = tipo
    def setMensagem(self, mensagem: str) -> None: self.mensagem = mensagem
    def setTimestamp(self, timestamp: datetime) -> None: self.timestamp = timestamp
    def setIncidente_id(self, incidente_id: int | None) -> None: self.incidente_id = incidente_id
    def setAutor(self, autor: str) -> None: self.autor = autor

    def to_dict(self) -> dict:
        return {
            "id": self.getId(),
            "tipo": self.getTipo(),
            "mensagem": self.getMensagem(),
            "timestamp": self.getTimestamp().isoformat(),
            "incidente_id": self.getIncidente_id(),
            "autor": self.getAutor(),
        }

    @staticmethod
    def from_dict(d: dict) -> "Notificacao":
        timestamp = d.get("timestamp")
        return Notificacao(
            id=d["id"], tipo=d["tipo"], mensagem=d["mensagem"],
            timestamp=datetime.fromisoformat(timestamp) if timestamp else None,
            incidente_id=d.get("incidente_id"), autor=d.get("autor", ""),
        )

    def __str__(self) -> str:
        return f"Notificacao(id={self.id}, tipo={self.tipo!r}, mensagem={self.mensagem!r})"

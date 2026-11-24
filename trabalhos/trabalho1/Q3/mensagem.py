from typing import Any


class Mensagem:
    """
    Envelope de uma mensagem trocada entre cliente e servidor.

    Atributos:
        id      → identificador da requisição (para casar request/reply)
        tipo    → string que identifica a operação (ex: "BUSCAR_INCIDENTE")
        status  → "OK" ou "ERRO" (só usado em replies)
        payload → dicionário com os dados (args ou resultado)
    """

    def __init__(self, tipo: str, payload: dict | None = None, id: int | None = None, status: str = "OK"):
        self.id = id
        self.tipo = tipo
        self.status = status
        self.payload = payload if payload is not None else {}

    # ---------- SERIALIZAÇÃO ----------
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tipo": self.tipo,
            "status": self.status,
            "payload": self.payload,
        }

    @staticmethod
    def from_dict(d: dict) -> "Mensagem":
        return Mensagem(
            id=d.get("id"),
            tipo=d["tipo"],
            status=d.get("status", "OK"),
            payload=d.get("payload", {}),
        )

    def __str__(self) -> str:
        return (f"Mensagem(id={self.id}, tipo='{self.tipo}', "
                f"status='{self.status}', payload={self.payload})")
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Request:
    action: str
    username: str
    password: str
    payload: dict[str, Any] = field(default_factory=dict)

    def to_bytes(self) -> bytes:
        return json.dumps(
            self.__dict__,
            ensure_ascii=False,
        ).encode()

    @classmethod
    def from_bytes(cls, data: bytes) -> "Request":
        request = json.loads(data.decode())

        if not isinstance(request, dict):
            raise TypeError("Requisição deve ser um objeto JSON")

        request.setdefault("action", "LOGIN")
        request.setdefault("payload", {})
        if not isinstance(request["payload"], dict):
            raise TypeError("Payload da requisição deve ser um objeto JSON")
        return cls(**request)
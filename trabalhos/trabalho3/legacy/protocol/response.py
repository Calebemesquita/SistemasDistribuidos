import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Response:
    success: bool | None = None
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_bytes(self) -> bytes:
        return json.dumps(
            {
                key: value
                for key, value in self.__dict__.items()
                if value is not None
            },
            ensure_ascii=False,
        ).encode()

    @classmethod
    def from_bytes(cls, data: bytes) -> "Response":
        response = json.loads(data.decode())
        if not isinstance(response, dict):
            raise TypeError("Resposta deve ser um objeto JSON")

        response.setdefault("data", {})
        if not isinstance(response["data"], dict):
            raise TypeError("Dados da resposta devem ser um objeto JSON")
        return cls(**response)
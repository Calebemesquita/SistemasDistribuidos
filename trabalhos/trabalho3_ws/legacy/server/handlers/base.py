from typing import Protocol

from legacy.protocol.request import Request
from legacy.protocol.response import Response


class Handler(Protocol):
    def __call__(self, request: Request) -> Response:
        ...
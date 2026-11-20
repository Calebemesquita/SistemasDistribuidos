from functools import wraps

from legacy.domain.auth import authenticate
from legacy.protocol.request import Request
from legacy.protocol.response import Response

from .base import Handler


def requires_authentication(handler: Handler) -> Handler:
    @wraps(handler)
    def wrapper(request: Request) -> Response:
        if not authenticate(request.username, request.password):
            return Response(success=False, error="Acesso negado")
        return handler(request)

    return wrapper

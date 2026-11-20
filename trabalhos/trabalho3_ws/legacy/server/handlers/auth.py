from legacy.domain.auth import authenticate
from legacy.protocol.request import Request
from legacy.protocol.response import Response


def handle_login(request: Request) -> Response:
    authenticated = authenticate(request.username, request.password)
    return Response(
        success=authenticated,
        data={"authenticated": authenticated},
        error=None if authenticated else "Acesso negado",
    )
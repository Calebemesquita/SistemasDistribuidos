from legacy.protocol.request import Request
from legacy.protocol.response import Response

from .auth import handle_login
from .library import handle_borrow_book, handle_list_books
from .notification import handle_publish

HANDLERS = {
    "LOGIN": handle_login,
    "PUBLISH": handle_publish,
    "LIST_BOOKS": handle_list_books,
    "BORROW_BOOK": handle_borrow_book,
}


def process_request(line: bytes) -> Response:
    try:
        request = Request.from_bytes(line)
        handler = HANDLERS.get(request.action)

        if not handler:
            return Response(
                success=False,
                error=f"Ação inválida: {request.action}",
            )

        return handler(request)
    except (KeyError, ValueError, TypeError) as error:
        return Response(
            success=False,
            error=f"Requisição inválida: {error}",
        )
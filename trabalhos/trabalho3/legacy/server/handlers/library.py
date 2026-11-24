from dataclasses import asdict

from legacy.domain.book_service import BookService
from legacy.domain.loan_service import LoanService
from legacy.protocol.request import Request
from legacy.protocol.response import Response

from .security import requires_authentication

book_service = BookService()
loan_service = LoanService(book_service)


@requires_authentication
def handle_list_books(request: Request) -> Response:
    books = [asdict(book) for book in book_service.list_books()]
    return Response(success=True, data={"books": books})


@requires_authentication
def handle_borrow_book(request: Request) -> Response:
    book_id = request.payload.get("book_id")
    if not isinstance(book_id, int):
        return Response(success=False, error="ID do livro ausente ou inválido")

    loan = loan_service.borrow_book(book_id, request.username)
    if loan is None:
        return Response(
            success=False,
            error="Livro indisponível para empréstimo",
        )

    return Response(
        success=True,
        data={
            "loan": asdict(loan),
            "message": "Livro emprestado com sucesso",
        },
    )
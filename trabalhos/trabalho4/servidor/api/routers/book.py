from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status

from api.dependencies.services import get_book_service, get_notification_service
from api.models.book import BookResponse, CreateBookRequest
from api.services.book_service import BookService
from api.services.notification_service import NotificationService
from notifications.publisher import NotificationPublishError

router = APIRouter(prefix="/books", tags=["Livros"], responses={404: {"description": "Not found"}})

@router.get(
    path="/",
    response_model=list[BookResponse],
    name="Get all books",
    description="Get all books in the library",
    response_description="List of books in the library",
    status_code=HTTPStatus.OK,
)
async def list_books(
    book_service: Annotated[BookService, Depends(get_book_service)]
) -> list[dict]:
    """Retorna os livros do agregado Biblioteca compartilhado."""
    return book_service.list_books()


@router.post(
    path="/",
    response_model=BookResponse,
    name="Create a book",
    description="Adds a book to the library catalog",
    status_code=HTTPStatus.CREATED,
)
def create_book(
    book_request: Annotated[
        CreateBookRequest,
        Body(openapi_examples={
            "novo-livro": {
                "summary": "Cadastrar um livro",
                "value": {"title": "Dom Casmurro", "author": "Machado de Assis"},
            },
        }),
    ],
    book_service: Annotated[BookService, Depends(get_book_service)],
    notification_service: Annotated[
        NotificationService, Depends(get_notification_service)
    ],
) -> dict:
    """Cadastra um livro no catálogo."""
    with book_service.library.transacao():
        try:
            created_book = book_service.add_book(
                title=book_request.title,
                author=book_request.author,
                librarian_id=book_request.librarian_id,
                librarian_name=book_request.librarian_name,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc
        try:
            notification_service.publish_latest()
        except NotificationPublishError as exc:
            book_service.rollback_created_book(created_book["id"])
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Livro não cadastrado: serviço de notificações indisponível.",
            ) from exc
        book_service.commit_created_book(created_book["id"])
        return created_book

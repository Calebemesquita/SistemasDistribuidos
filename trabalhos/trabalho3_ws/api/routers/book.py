from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies.services import get_book_service
from api.models.book import Book
from api.schemas.book_schema import BookResponse
from api.services.book_service import BookService

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
) -> list[Book]:
    """Retorna uma lista de todos os livros na biblioteca."""
    return book_service.list_items()

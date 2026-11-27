from functools import lru_cache

from biblioteca_rpc.entities import Biblioteca, CanalNotificacoes, Livro

from api.services.book_service import BookService
from api.services.loan_service import LoanService
from api.services.notification_service import NotificationService


@lru_cache
def get_library() -> Biblioteca:
    """Cria o agregado do Trabalho 2 compartilhado por todas as rotas."""
    library = Biblioteca(CanalNotificacoes())
    for isbn, title, author in (
        ("1", "The Great Gatsby", "F. Scott Fitzgerald"),
        ("2", "To Kill a Mockingbird", "Harper Lee"),
        ("3", "1984", "George Orwell"),
    ):
        library.catalogo.livros[isbn] = Livro(isbn, title, author)
    return library


@lru_cache
def get_book_service() -> BookService:
    return BookService(get_library())


@lru_cache
def get_loan_service() -> LoanService:
    return LoanService(get_library())


@lru_cache
def get_notification_service() -> NotificationService:
    return NotificationService(get_library())

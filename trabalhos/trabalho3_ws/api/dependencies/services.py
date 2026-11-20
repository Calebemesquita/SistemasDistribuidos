from functools import lru_cache

from api.services.book_service import BookService
from api.services.loan_service import LoanService


@lru_cache
def get_book_service() -> BookService:
    """Retorna a instância compartilhada do serviço de livros."""
    return BookService()

@lru_cache
def get_loan_service() -> LoanService:
    """Retorna a instância do serviço de empréstimos."""
    return LoanService(get_book_service())
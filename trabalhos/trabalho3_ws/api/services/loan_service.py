from api.models.loan import Loan
from api.services.base_service import BaseService
from api.services.book_service import BookService


class LoanService(BaseService[Loan]):
    def __init__(self, book_service: BookService):
        super().__init__()

        self.book_service = book_service

    def create_item(self, item: Loan) -> Loan:
        book = self.book_service.get_item(item.book_id)

        if book is None:
            raise ValueError("Book not found.")
        if not book.available:
            raise ValueError("Book unavailable.")

        loan = super().create_item(item)
        book.available = False

        return loan

    def rollback_created_item(self, item: Loan) -> None:
        if self.items.get(item.id) is not item:
            raise ValueError(f"Loan {item.id} is not stored by this service")

        del self.items[item.id]
        book = self.book_service.get_item(item.book_id)
        if book is None:
            raise ValueError(f"Book {item.book_id} not found during rollback")

        book.available = True
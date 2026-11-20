from legacy.domain.book_service import BookService
from legacy.domain.loan import Loan


class LoanService:
    def __init__(self, book_service: BookService):
        self.book_service = book_service
        self.loans: dict[int, Loan] = {}
        self.next_id: int = 1

    def borrow_book(self, book_id: int, username: str) -> Loan | None:
        book = self.book_service.get_book(book_id)
        if book is None or not book.available:
            return None

        book.available = False

        loan = Loan(id=self.next_id, book_id=book_id, username=username)
        self.loans[self.next_id] = loan
        self.next_id += 1

        return loan

    def return_book(self, loan_id: int) -> bool:
        loan = self.loans.get(loan_id)
        if loan is None or loan.returned:
            return False

        book = self.book_service.get_book(loan.book_id)
        if book is None:
            return False

        loan.returned = True
        book.available = True
        
        return True
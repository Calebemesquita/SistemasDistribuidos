from biblioteca_domain.models import Book, Loan


class BookService:
    def __init__(self):
        self.books: dict[int, Book] = {
            1: Book(id=1, title="The Great Gatsby", author="F. Scott Fitzgerald"),
            2: Book(id=2, title="To Kill a Mockingbird", author="Harper Lee"),
            3: Book(id=3, title="1984", author="George Orwell"),
        }

    def list_books(self) -> list[Book]:
        return list(self.books.values())

    def get_book(self, book_id: int) -> Book | None:
        return self.books.get(book_id)

    def add_book(self, title: str, author: str) -> Book:
        if not title.strip() or not author.strip():
            raise ValueError("Title and author are required.")

        next_id = max(self.books, default=0) + 1
        book = Book(
            id=next_id,
            title=title.strip(),
            author=author.strip(),
        )
        self.books[next_id] = book
        return book


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

    def list_loans(self) -> list[Loan]:
        return list(self.loans.values())

    def get_loan(self, loan_id: int) -> Loan | None:
        return self.loans.get(loan_id)

    def create_loan(self, book_id: int, username: str) -> Loan:
        if not username.strip():
            raise ValueError("Username cannot be blank.")

        book = self.book_service.get_book(book_id)
        if book is None:
            raise ValueError("Book not found.")
        if not book.available:
            raise ValueError("Book unavailable.")

        loan = self.borrow_book(book_id, username)
        if loan is None:
            raise ValueError("Book unavailable.")
        return loan

    def rollback_created_loan(self, loan: Loan) -> None:
        if self.loans.get(loan.id) is not loan or loan.returned:
            raise ValueError(f"Loan {loan.id} cannot be rolled back.")

        book = self.book_service.get_book(loan.book_id)
        if book is None:
            raise ValueError(f"Book {loan.book_id} not found during rollback.")

        del self.loans[loan.id]
        book.available = True
        if self.next_id == loan.id + 1:
            self.next_id = loan.id

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

    def return_loan(self, loan_id: int) -> Loan:
        loan = self.loans.get(loan_id)
        if loan is None:
            raise ValueError("Loan not found.")
        if loan.returned:
            raise ValueError("Loan already returned.")
        if not self.return_book(loan_id):
            raise ValueError("Book not found.")
        return loan

    def rollback_returned_loan(self, loan: Loan) -> None:
        if self.loans.get(loan.id) is not loan or not loan.returned:
            raise ValueError(f"Loan {loan.id} is not stored as returned.")

        book = self.book_service.get_book(loan.book_id)
        if book is None:
            raise ValueError(f"Book {loan.book_id} not found during rollback.")

        loan.returned = False
        book.available = False

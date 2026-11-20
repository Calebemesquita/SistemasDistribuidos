from legacy.domain.book import Book


class BookService:
    def __init__(self):
        self.books: dict[int, Book] = {
            1: Book(id=1, title="The Great Gatsby", author="F. Scott Fitzgerald"),
            2: Book(id=2, title="To Kill a Mockingbird", author="Harper Lee"),
            3: Book(id=3, title="1984", author="George Orwell"),
        }

    def list_books(self) -> list[Book]:
        return list(self.books.values())

    def get_book(self, book_id: int) -> Book:
        return self.books.get(book_id)
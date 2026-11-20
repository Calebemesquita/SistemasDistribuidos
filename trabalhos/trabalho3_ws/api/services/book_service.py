from api.models.book import Book
from api.services.base_service import BaseService


class BookService(BaseService[Book]):
    def __init__(self) -> None:
        super().__init__()

        self.items = {
            1: Book(id=1, title="The Great Gatsby", author="F. Scott Fitzgerald"),
            2: Book(id=2, title="To Kill a Mockingbird", author="Harper Lee"),
            3: Book(id=3, title="1984", author="George Orwell"),
        }
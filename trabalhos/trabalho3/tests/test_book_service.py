import unittest

from legacy.domain.book_service import BookService


class BookServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = BookService()

    def test_list_books_returns_all_books(self):
        books = self.service.list_books()

        self.assertEqual(len(books), 3)
        self.assertEqual(books[0].title, "The Great Gatsby")

    def test_get_book_returns_matching_book(self):
        book = self.service.get_book(1)

        self.assertIsNotNone(book)
        self.assertEqual(book.id, 1)

    def test_get_book_returns_none_for_unknown_id(self):
        self.assertIsNone(self.service.get_book(999))

    def test_add_book_assigns_next_id(self):
        book = self.service.add_book("Brás Cubas", "Machado de Assis")

        self.assertEqual(book.id, 4)
        self.assertIs(self.service.get_book(4), book)


if __name__ == "__main__":
    unittest.main()

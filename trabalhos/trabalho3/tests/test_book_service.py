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


if __name__ == "__main__":
    unittest.main()

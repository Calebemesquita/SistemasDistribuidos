import unittest

from api.dependencies.services import get_book_service


class BookServiceDependencyTests(unittest.TestCase):
    def test_get_book_service_returns_the_same_instance(self):
        self.assertIs(get_book_service(), get_book_service())


if __name__ == "__main__":
    unittest.main()

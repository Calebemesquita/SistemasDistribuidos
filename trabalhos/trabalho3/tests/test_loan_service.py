import unittest

from legacy.domain.book_service import BookService
from legacy.domain.loan_service import LoanService


class LoanServiceTests(unittest.TestCase):
    def setUp(self):
        self.books = BookService()
        self.service = LoanService(self.books)

    def test_borrow_book_marks_book_unavailable(self):
        loan = self.service.borrow_book(1, "ash")

        self.assertIsNotNone(loan)
        self.assertEqual(loan.book_id, 1)
        self.assertEqual(loan.username, "ash")
        self.assertFalse(self.books.get_book(1).available)

    def test_cannot_borrow_unavailable_book_twice(self):
        first_loan = self.service.borrow_book(1, "ash")

        second_loan = self.service.borrow_book(1, "misty")

        self.assertIsNotNone(first_loan)
        self.assertIsNone(second_loan)

    def test_cannot_borrow_unknown_book(self):
        self.assertIsNone(self.service.borrow_book(999, "ash"))

    def test_return_book_marks_book_available(self):
        loan = self.service.borrow_book(1, "ash")

        returned = self.service.return_book(loan.id)

        self.assertTrue(returned)
        self.assertTrue(self.books.get_book(1).available)
        self.assertTrue(loan.returned)

    def test_cannot_return_unknown_loan(self):
        self.assertFalse(self.service.return_book(999))

    def test_cannot_return_same_loan_twice(self):
        loan = self.service.borrow_book(1, "ash")

        first_return = self.service.return_book(loan.id)
        second_return = self.service.return_book(loan.id)

        self.assertTrue(first_return)
        self.assertFalse(second_return)

    def test_create_and_rollback_loan_preserves_domain_state(self):
        loan = self.service.create_loan(1, "ana")
        self.assertEqual(loan.id, 1)
        self.assertFalse(self.books.get_book(1).available)

        self.service.rollback_created_loan(loan)

        self.assertEqual(self.service.list_loans(), [])
        self.assertTrue(self.books.get_book(1).available)

    def test_return_loan_and_rollback_return(self):
        loan = self.service.create_loan(1, "ana")

        self.assertIs(self.service.return_loan(loan.id), loan)
        self.assertTrue(loan.returned)
        self.service.rollback_returned_loan(loan)
        self.assertFalse(loan.returned)
        self.assertFalse(self.books.get_book(1).available)


if __name__ == "__main__":
    unittest.main()

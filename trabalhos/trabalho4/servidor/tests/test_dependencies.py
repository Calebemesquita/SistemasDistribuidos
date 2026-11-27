import unittest

from api.dependencies.services import get_book_service, get_library, get_loan_service, get_notification_service


class BookServiceDependencyTests(unittest.TestCase):
    def test_get_book_service_returns_the_same_instance(self):
        self.assertIs(get_book_service(), get_book_service())

    def test_all_http_services_share_the_work2_library_aggregate(self):
        self.assertIs(get_book_service().library, get_library())
        self.assertIs(get_loan_service().library, get_library())
        self.assertIs(get_notification_service().library, get_library())


if __name__ == "__main__":
    unittest.main()

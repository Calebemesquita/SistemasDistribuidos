import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.dependencies.services import (
    get_library,
    get_book_service,
    get_loan_service,
    get_notification_service,
)
from api.main import app
from notifications.publisher import NotificationPublishError
from protocol.notification import Notification


class ApiNotificationTests(unittest.TestCase):
    def setUp(self):
        get_book_service.cache_clear()
        get_loan_service.cache_clear()
        get_notification_service.cache_clear()
        get_library.cache_clear()
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        get_loan_service.cache_clear()
        get_book_service.cache_clear()
        get_notification_service.cache_clear()
        get_library.cache_clear()

    @patch("api.services.notification_service.publish_notification")
    def test_created_loan_publishes_notification(self, publish_notification):
        response = self.client.post(
            "/loans/",
            json={"book_id": 1, "username": "ash"},
        )

        self.assertEqual(response.status_code, 201)
        notification = publish_notification.call_args.args[0]
        self.assertIsInstance(notification, Notification)
        self.assertIn("ash", notification.content)
        self.assertIn("#1", notification.content)

    @patch(
        "api.services.notification_service.publish_notification",
        side_effect=NotificationPublishError("broker unavailable"),
    )
    def test_publish_failure_returns_503_and_reverts_loan(self, publish_notification):
        response = self.client.post(
            "/loans/",
            json={"book_id": 1, "username": "ash"},
        )

        self.assertEqual(response.status_code, 503)
        self.assertFalse(self.client.get("/loans/").json())
        books = self.client.get("/books/").json()
        self.assertTrue(next(book for book in books if book["id"] == 1)["available"])
        self.assertEqual(self.client.get("/users/").json(), [])

    @patch(
        "api.services.notification_service.publish_notification",
        side_effect=NotificationPublishError("broker unavailable"),
    )
    def test_publish_failure_rolls_back_new_book_and_librarian(self, publish_notification):
        response = self.client.post(
            "/books/",
            json={
                "title": "Livro temporário",
                "author": "Autora",
                "librarian_id": "bia",
                "librarian_name": "Bia",
            },
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(len(self.client.get("/books/").json()), 3)
        self.assertEqual(self.client.get("/users/").json(), [])
        self.assertEqual(self.client.get("/notifications/").json(), [])


if __name__ == "__main__":
    unittest.main()

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


class ApiObjectsTests(unittest.TestCase):
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

    def test_root_describes_the_api_and_distributed_objects(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["objetos_distribuidos"],
            ["catalogo", "emprestimos", "notificacoes"],
        )
        self.assertEqual(self.client.get("/health").json(), {"status": "ok"})

    @patch("api.services.notification_service.publish_notification")
    def test_book_resource_lists_and_creates_books(self, publish):
        response = self.client.post(
            "/books/",
            json={"title": "Dom Casmurro", "author": "Machado de Assis"},
        )

        self.assertEqual(response.status_code, 201)
        created_book = response.json()
        self.assertEqual(created_book["id"], 4)
        self.assertTrue(created_book["available"])
        self.assertIn(created_book, self.client.get("/books/").json())

    @patch("api.services.notification_service.publish_notification")
    def test_loan_and_return_update_the_book_and_publish_events(self, publish):
        loan_response = self.client.post(
            "/loans/",
            json={"book_id": 1, "username": "ana"},
        )
        loan = loan_response.json()

        self.assertEqual(loan_response.status_code, 201)
        self.assertFalse(
            next(
                book
                for book in self.client.get("/books/").json()
                if book["id"] == 1
            )["available"]
        )

        return_response = self.client.post(f"/loans/{loan['id']}/return")

        self.assertEqual(return_response.status_code, 200)
        self.assertTrue(return_response.json()["returned"])
        self.assertTrue(
            next(
                book
                for book in self.client.get("/books/").json()
                if book["id"] == 1
            )["available"]
        )
        self.assertEqual(publish.call_count, 2)

    def test_http_subscription_receives_domain_alerts_and_updates(self):
        self.client.post(
            "/notifications/subscriptions",
            json={"client_id": "ana", "name": "Ana"},
        )
        with patch("api.services.notification_service.publish_notification"):
            loan = self.client.post(
                "/loans/",
                json={"book_id": 1, "username": "ana"},
            ).json()
            self.client.post(f"/loans/{loan['id']}/return")
        events = self.client.get(
            "/notifications/subscriptions/ana?after=0"
        ).json()["events"]
        self.assertEqual([event["type"] for event in events], ["ALERTA", "ATUALIZACAO"])
        self.assertTrue(any("ana solicitou" in event["content"] for event in events))
        self.assertEqual(self.client.delete("/notifications/subscriptions/ana").status_code, 200)

    def test_api_registers_work2_user_roles(self):
        with patch("api.services.notification_service.publish_notification"):
            self.client.post(
                "/books/",
                json={
                    "title": "Livro de teste",
                    "author": "Autora",
                    "librarian_id": "bia",
                    "librarian_name": "Bia",
                },
            )
            self.client.post("/loans/", json={"book_id": 1, "username": "ana"})
        users = {user["id"]: user for user in self.client.get("/users/").json()}
        self.assertEqual(users["bia"]["role"], "bibliotecario")
        self.assertEqual(users["ana"]["role"], "leitor")

    @patch("api.services.notification_service.publish_notification")
    def test_notification_resource_publishes_and_lists_events(self, publish):
        response = self.client.post(
            "/notifications/",
            json={"type": "ALERTA", "content": "Livro reservado"},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["type"], "ALERTA")
        self.assertEqual(
            self.client.get("/notifications/").json(),
            [response.json()],
        )
        publish.assert_called_once()


if __name__ == "__main__":
    unittest.main()

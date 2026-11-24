import json
import unittest
from unittest.mock import patch

from legacy.protocol.response import Response
from legacy.server.handlers import process_request


class ProcessRequestTests(unittest.TestCase):
    def test_login_returns_response_object(self):
        request = {
            "action": "LOGIN",
            "username": "ash",
            "password": "pikachu",
        }

        response = process_request(json.dumps(request).encode())

        self.assertEqual(
            response,
            Response(success=True, data={"authenticated": True}),
        )

    @patch("legacy.server.handlers.notification.pika.BlockingConnection")
    def test_publish_sends_notification_and_returns_message(self, blocking_connection):
        request = {
            "action": "PUBLISH",
            "username": "ash",
            "password": "pikachu",
            "payload": {
                "type": "ALERTA",
                "content": "Teste",
            },
        }

        response = process_request(json.dumps(request).encode())

        connection = blocking_connection.return_value.__enter__.return_value
        connection.channel.return_value.basic_publish.assert_called_once()
        self.assertTrue(response.success)
        self.assertEqual(
            response.data["message"],
            "Notificação publicada com sucesso",
        )
        self.assertEqual(Response.from_bytes(response.to_bytes()), response)

    def test_list_books_returns_books_in_response_data(self):
        request = {
            "action": "LIST_BOOKS",
            "username": "ash",
            "password": "pikachu",
        }

        response = process_request(json.dumps(request).encode())

        self.assertTrue(response.success)
        self.assertEqual(len(response.data["books"]), 3)

    def test_borrow_book_reads_id_from_payload(self):
        request = {
            "action": "BORROW_BOOK",
            "username": "ash",
            "password": "pikachu",
            "payload": {"book_id": 1},
        }

        response = process_request(json.dumps(request).encode())

        self.assertTrue(response.success)
        self.assertEqual(response.data["loan"]["book_id"], 1)

    def test_invalid_action_returns_response_object(self):
        request = {
            "action": "OTHER",
            "username": "ash",
            "password": "pikachu",
        }

        response = process_request(json.dumps(request).encode())

        self.assertIsInstance(response, Response)
        self.assertFalse(response.success)
        self.assertEqual(response.error, "Ação inválida: OTHER")

    def test_missing_action_defaults_to_login(self):
        request = {"username": "ash", "password": "pikachu"}

        response = process_request(json.dumps(request).encode())

        self.assertEqual(
            response,
            Response(success=True, data={"authenticated": True}),
        )


if __name__ == "__main__":
    unittest.main()

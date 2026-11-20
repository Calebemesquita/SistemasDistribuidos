import unittest

from legacy.protocol.request import Request


class RequestTests(unittest.TestCase):
    def test_round_trip_preserves_payload(self):
        original = Request(
            action="PUBLISH",
            username="ash",
            password="pikachu",
            payload={"type": "ALERTA", "content": "Teste"},
        )

        self.assertEqual(Request.from_bytes(original.to_bytes()), original)

    def test_missing_action_and_payload_use_defaults(self):
        request = Request.from_bytes(
            b'{"username": "ash", "password": "pikachu"}'
        )

        self.assertEqual(request.action, "LOGIN")
        self.assertEqual(request.payload, {})


if __name__ == "__main__":
    unittest.main()

import unittest

from legacy.protocol.response import Response


class ResponseTests(unittest.TestCase):
    def test_round_trip_preserves_data(self):
        original = Response(
            success=True,
            data={"authenticated": True},
        )

        self.assertEqual(Response.from_bytes(original.to_bytes()), original)


if __name__ == "__main__":
    unittest.main()

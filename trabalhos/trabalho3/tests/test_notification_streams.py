import unittest
from io import BytesIO

from protocol.notification import Notification
from legacy.protocol.notification_input_stream import NotificationInputStream
from legacy.protocol.notification_output_stream import NotificationOutputStream
from protocol.notification_type import NotificationType


class NotificationStreamTests(unittest.TestCase):
    def test_output_stream_notifications_can_be_read_back(self):
        notifications = [
            Notification(NotificationType.ALERT, "Livro disponível"),
            Notification(NotificationType.UPDATE, "Novo livro"),
        ]
        destination = BytesIO()

        output = NotificationOutputStream(
            destination=destination,
            notifications=notifications,
            count=len(notifications),
        )
        output.write_notifications()

        source = NotificationInputStream(BytesIO(destination.getvalue()))
        restored = [
            source.read_notification(),
            source.read_notification(),
        ]

        self.assertEqual(restored, notifications)
        self.assertIsNone(source.read_notification())

    def test_output_stream_respects_count(self):
        notifications = [
            Notification(NotificationType.ALERT, "Primeira"),
            Notification(NotificationType.UPDATE, "Segunda"),
        ]
        destination = BytesIO()

        output = NotificationOutputStream(
            destination=destination,
            notifications=notifications,
            count=1,
        )
        output.write_notifications()

        source = NotificationInputStream(BytesIO(destination.getvalue()))
        self.assertEqual(source.read_notification(), notifications[0])
        self.assertIsNone(source.read_notification())


if __name__ == "__main__":
    unittest.main()

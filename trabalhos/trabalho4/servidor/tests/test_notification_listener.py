import unittest
from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from notifications.listener import consume_notifications, queue_name_for
from notifications.config import EXCHANGE_NAME
from protocol.notification import Notification
from protocol.notification_type import NotificationType


class NotificationListenerTests(unittest.TestCase):
    def test_queue_name_uses_the_subscriber_username(self):
        self.assertEqual(queue_name_for("ana"), "alertas.ana")

    def test_empty_username_is_rejected(self):
        with self.assertRaises(ValueError):
            queue_name_for("  ")

    @patch("notifications.listener.pika.BlockingConnection")
    def test_listener_declares_queue_displays_and_acknowledges_message(
        self,
        blocking_connection,
    ):
        connection = blocking_connection.return_value.__enter__.return_value
        channel = connection.channel.return_value
        notification = Notification(
            NotificationType.NOTIFICATION,
            "Novo empréstimo solicitado",
        )

        def deliver_one_message():
            callback = channel.basic_consume.call_args.kwargs["on_message_callback"]
            callback(
                channel,
                SimpleNamespace(delivery_tag=42),
                None,
                notification.to_bytes(),
            )

        channel.start_consuming.side_effect = deliver_one_message
        output = StringIO()

        with redirect_stdout(output):
            consume_notifications("ana")

        channel.exchange_declare.assert_called_once_with(
            exchange=EXCHANGE_NAME,
            exchange_type="fanout",
            durable=True,
        )
        channel.queue_declare.assert_called_once_with(
            queue="alertas.ana",
            durable=True,
        )
        channel.queue_bind.assert_called_once_with(
            exchange=EXCHANGE_NAME,
            queue="alertas.ana",
        )
        channel.queue_unbind.assert_called_once_with(
            exchange=EXCHANGE_NAME,
            queue="alertas.ana",
        )
        channel.basic_ack.assert_called_once_with(delivery_tag=42)
        self.assertIn("Novo empréstimo solicitado", output.getvalue())


if __name__ == "__main__":
    unittest.main()

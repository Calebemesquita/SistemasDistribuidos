import pika

from notifications.config import EXCHANGE_NAME, RABBITMQ_HOST, RABBITMQ_PORT
from protocol.notification import Notification


class NotificationPublishError(RuntimeError):
    pass


def publish_notification(notification: Notification) -> None:
    try:
        with pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
            )
        ) as connection:
            channel = connection.channel()
            channel.exchange_declare(
                exchange=EXCHANGE_NAME,
                exchange_type="fanout",
                durable=True,
            )
            channel.confirm_delivery()
            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key="",
                body=notification.to_bytes(),
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=2,
                ),
                mandatory=True,
            )
    except pika.exceptions.AMQPError as exc:
        raise NotificationPublishError(
            "Could not publish notification to RabbitMQ."
        ) from exc

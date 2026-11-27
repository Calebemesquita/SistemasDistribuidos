import argparse
from datetime import datetime

import pika

from notifications.config import (
    EXCHANGE_NAME,
    RABBITMQ_HOST,
    RABBITMQ_PASSWORD,
    RABBITMQ_PORT,
    RABBITMQ_USERNAME,
)
from protocol.notification import Notification


def queue_name_for(username: str) -> str:
    if not username.strip():
        raise ValueError("Username cannot be empty.")
    return f"alertas.{username}"


def consume_notifications(username: str) -> None:
    queue_name = queue_name_for(username)
    with pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=pika.PlainCredentials(
                RABBITMQ_USERNAME,
                RABBITMQ_PASSWORD,
            ),
        )
    ) as connection:
        channel = connection.channel()
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type="fanout",
            durable=True,
        )
        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name)

        def receive(channel, method, properties, body) -> None:
            notification = Notification.from_bytes(body)
            timestamp = datetime.fromtimestamp(
                notification.timestamp
            ).astimezone().isoformat(timespec="seconds")
            print(
                f"[{username}] {notification.type.value} - "
                f"{notification.content} ({timestamp})",
                flush=True,
            )
            channel.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(
            queue=queue_name,
            on_message_callback=receive,
            auto_ack=False,
        )
        print(f"Ouvindo {queue_name}. Ctrl+C para encerrar.", flush=True)
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
        finally:
            channel.queue_unbind(
                exchange=EXCHANGE_NAME,
                queue=queue_name,
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Listen to library notifications for a username."
    )
    parser.add_argument("username", help="Username used in the alertas.<username> queue")
    args = parser.parse_args()
    consume_notifications(args.username)


if __name__ == "__main__":
    main()

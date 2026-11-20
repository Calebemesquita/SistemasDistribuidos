import pika

from protocol.notification import Notification
from protocol.notification_type import NotificationType
from legacy.protocol.request import Request
from legacy.protocol.response import Response

from .security import requires_authentication


@requires_authentication
def handle_publish(request: Request) -> Response:
    notification_type = request.payload.get("type")
    content = request.payload.get("content")
    if not isinstance(notification_type, str) or not isinstance(content, str):
        return Response(success=False, error="Campos obrigatórios ausentes")

    notification = Notification(
        type=NotificationType(notification_type),
        content=content,
    )

    try:
        with pika.BlockingConnection(
            pika.ConnectionParameters(host="127.0.0.1", port=5672)
        ) as conn:
            channel = conn.channel()
            channel.confirm_delivery()

            channel.basic_publish(
                exchange="biblioteca.alertas",
                routing_key="",
                body=notification.to_bytes(),
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=2
                ),
                mandatory=True
            )
    except pika.exceptions.AMQPError as error:
        print(f"Failed to publish alert to RabbitMQ: {error}")
        return Response(success=False, error="Unable to publish alert.")

    print(f"Notificação enviada por {request.username}")
    return Response(
        success=True,
        data={"message": "Notificação publicada com sucesso"},
    )
import socket

from protocol.notification import Notification
from legacy.protocol.notification_output_stream import NotificationOutputStream
from protocol.notification_type import NotificationType

HOST = "127.0.0.1"
PORT = 5002

notifications = [
    Notification(NotificationType.ALERT, "Livro disponível!"),
    Notification(NotificationType.UPDATE, "Acervo atualizado!"),
    Notification(NotificationType.NOTIFICATION, "Novo empréstimo!")
]

with socket.create_connection((HOST, PORT)) as client, client.makefile("wb") as destination:
    stream = NotificationOutputStream(
        destination=destination,
        notifications=notifications,
        count=len(notifications)
    )

    stream.write_notifications()

print("Notificações enviadas!")
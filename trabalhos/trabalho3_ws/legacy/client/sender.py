from legacy.client.auth_client import send_request
from protocol.notification import Notification
from protocol.notification_type import NotificationType
from legacy.protocol.request import Request


def main():
    username = input("Usuário: ")
    password = input("Senha: ")

    notification = Notification(
        type=NotificationType.ALERT,
        content="O livro Duna está disponível!",
    )
    request = Request(
        action="PUBLISH",
        username=username,
        password=password,
        payload={
            "type": notification.type.value,
            "content": notification.content,
        },
    )

    print(send_request(request))


if __name__ == "__main__":
    main()

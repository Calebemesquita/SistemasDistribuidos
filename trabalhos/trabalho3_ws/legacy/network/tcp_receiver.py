# import socket

# HOST = "127.0.0.1"
# PORT = 5002

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
#     server.bind((HOST, PORT))
#     server.listen(1)

#     print("Aguardando conexão TCP...")

#     conn, address = server.accept()

#     with conn, conn.makefile("rb") as stream:
#         for line in stream:
#             print("Recebido:", line.decode("utf-8").strip())

import socket

from legacy.protocol.notification_input_stream import NotificationInputStream

HOST = "127.0.0.1"
PORT = 5002

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen(1)

    print("Aguardando conexão TCP...")

    conn, address = server.accept()

    with conn, conn.makefile("rb") as source:
        stream = NotificationInputStream(source)

        while True:
            notification = stream.read_notification()

            if notification is None:
                break

            print(
                f"Recebido: {notification.type.value} "
                f"- {notification.content}"
            )
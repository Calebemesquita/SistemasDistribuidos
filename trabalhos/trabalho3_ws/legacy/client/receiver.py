import socket
import struct
import threading
import pika

from legacy.client.auth_client import borrow_book, get_books, login
from legacy.network.config import GROUP, PORT
from legacy.network.listener import Listener
from protocol.notification import Notification
from legacy.protocol.response import Response


def show_notifications(data):
    notification = Notification.from_bytes(data)
    print(f"Received notification: {notification.type.value} - {notification.content} at {notification.timestamp}")


def create_multicast_socket(group, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", port))

    member = struct.pack("4s4s", socket.inet_aton(group), socket.inet_aton("0.0.0.0"))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, member)  # Join the multicast group

    return sock, member


def _show_books(response: Response) -> None:
    if not response.success:
        print(response.error or "Não foi possível consultar os livros.")
        return

    books = response.data.get("books")
    if not isinstance(books, list):
        print("Resposta inválida do servidor ao consultar os livros.")
        return

    if not books:
        print("Nenhum livro cadastrado.")
        return

    print("\n=== LIVROS ===")
    for book in books:
        if not isinstance(book, dict):
            print("Resposta inválida do servidor ao consultar os livros.")
            return

        availability = "disponível" if book.get("available") else "emprestado"
        print(
            f'{book.get("id")}. {book.get("title")} - {book.get("author")} '
            f"({availability})"
        )


def show_menu(username: str, password: str):
    while True:
        print("\n=== BIBLIOTECA ===")
        print("1. Consultar livros")
        print("2. Solicitar empréstimo")
        print("3. Sair")

        option = input("Escolha: ")

        if option == "1":
            try:
                _show_books(get_books(username, password))
            except OSError as error:
                print(f"Não foi possível conectar ao servidor: {error}")
            except ValueError as error:
                print(f"Resposta inválida do servidor: {error}")

        elif option == "2":
            book_id_text = input("ID do livro: ")
            try:
                book_id = int(book_id_text)
            except ValueError:
                print("ID inválido. Informe um número.")
                continue

            if book_id <= 0:
                print("ID inválido. Informe um número positivo.")
                continue

            try:
                response = borrow_book(username, password, book_id)
            except OSError as error:
                print(f"Não foi possível conectar ao servidor: {error}")
                continue
            except ValueError as error:
                print(f"Resposta inválida do servidor: {error}")
                continue

            if response.success:
                print(response.data.get("message", "Empréstimo solicitado com sucesso."))
            else:
                print(response.error or "Não foi possível solicitar o empréstimo.")

        elif option == "3":
            return

        else:
            print("Opção inválida!")

def listen_for_notifications(queue):
    with pika.BlockingConnection(
        pika.ConnectionParameters(host="127.0.0.1", port=5672)
    ) as conn:
        channel = conn.channel()

        def receive(channel, delivery, props, body):
            show_notifications(body)
            channel.basic_ack(delivery_tag=delivery.delivery_tag)

        channel.basic_consume(
            queue=queue,
            on_message_callback=receive,
            auto_ack=False
        )

        channel.start_consuming()

def main():
    username = input("Usuário: ")
    password = input("Senha: ")

    if not login(username, password):
        print("Acesso negado!")
        return

    print("Bem-vindo!")

    fila = f"alertas.{username}"

    thread = threading.Thread(
        target=listen_for_notifications,
        args=(fila,),
        daemon=True,
    )
    thread.start()

    show_menu(username, password)

if __name__ == "__main__":
    main()
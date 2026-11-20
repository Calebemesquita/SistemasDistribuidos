
import socket
import threading

from legacy.server.handlers import process_request

HOST = "127.0.0.1"
TCP_PORT = 5001


def handle_client(conn, address):
    with conn, conn.makefile("rb") as reader:
        data = reader.readline()

        if not data:
            return

        response = process_request(data)

        conn.sendall(response.to_bytes() + b"\n")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server.bind((HOST, TCP_PORT))
        server.listen()

        print(f"Servidor iniciado em {HOST}:{TCP_PORT}")

        while True:
            conn, address = server.accept()

            thread = threading.Thread(
                target=handle_client,
                args=(conn, address),
                daemon=True
            )

            thread.start()


if __name__ == "__main__":
    main()

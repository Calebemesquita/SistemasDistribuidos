import socket

from legacy.protocol.request import Request
from legacy.protocol.response import Response

HOST = "127.0.0.1"
PORT = 5001

def login(username, password):
    request = Request(action="LOGIN", username=username, password=password)

    with socket.create_connection((HOST, PORT)) as client:
        data = request.to_bytes() + b"\n"
        client.sendall(data)

        with client.makefile("rb") as reader:
            data = reader.readline()
            
    response = Response.from_bytes(data)
    return response.success is True

def send_request(request: Request) -> Response:
    with socket.create_connection((HOST, PORT)) as client:
        data = request.to_bytes() + b"\n"
        client.sendall(data)

        with client.makefile("rb") as reader:
            data = reader.readline()
            
    return Response.from_bytes(data)


def get_books(username: str, password: str) -> Response:
    request = Request(
        action="LIST_BOOKS",
        username=username,
        password=password,
    )
    return send_request(request)


def borrow_book(username: str, password: str, book_id: int) -> Response:
    request = Request(
        action="BORROW_BOOK",
        username=username,
        password=password,
        payload={"book_id": book_id},
    )
    return send_request(request)
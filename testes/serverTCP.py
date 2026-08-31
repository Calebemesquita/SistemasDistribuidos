import socket


HOST = 127.0.0.1
PORT = 9090


def run_server():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind((HOST, POST))

    server.listen(0)
    print(f"Listing on {HOST} and {PORT}")


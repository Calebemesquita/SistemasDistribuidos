import socket
import json
import threading
import time

HOST = "127.0.0.1"
PORT = 5001

TOTAL = 10

# Barreira: todas as threads aguardam até estarem prontas.
barrier = threading.Barrier(TOTAL)


def publish(number):
    request = {
        "action": "PUBLISH",
        "username": "ash",
        "password": "pikachu",
        "payload": {
            "type": "ALERTA",
            "content": f"Notificação concorrente #{number}",
        },
    }

    # Cada thread utiliza sua própria conexão TCP.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))

        # Aguarda todas as threads chegarem aqui.
        barrier.wait()

        data = (json.dumps(request) + "\n").encode("utf-8")

        start = time.perf_counter()
        client.sendall(data)

        with client.makefile("r", encoding="utf-8") as reader:
            response = json.loads(reader.readline())

        elapsed = (time.perf_counter() - start) * 1000

        print(f"Thread {number}: {response} ({elapsed:.2f} ms)")


threads = [
    threading.Thread(target=publish, args=(i,))
    for i in range(TOTAL)
]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

print("\nTeste de concorrência finalizado!")
import socket

from Q1.main import construir_relatorios
from fluxo import IncidenteOutputStream

HOST = "127.0.0.1"
PORT = 5000


def main() -> None:
    relatorios = construir_relatorios()
    with socket.create_connection((HOST, PORT)) as sock:
        print(f"[cliente] conectado a {HOST}:{PORT}")
        with sock.makefile("wb") as stream_saida:
            stream = IncidenteOutputStream(stream_saida, relatorios, len(relatorios))
            total = stream.escrever_objetos()
            print(f"[cliente] {total} bytes enviados")


if __name__ == "__main__":
    main()

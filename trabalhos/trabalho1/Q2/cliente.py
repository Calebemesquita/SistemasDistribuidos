"""Cliente TCP da Q2; serializa com o IncidenteOutputStream da Q1."""

import socket

from Q1.main import construir_relatorios
from fluxo import IncidenteOutputStream

HOST = "127.0.0.1"
PORT = 5001


def main() -> None:
    relatorios = construir_relatorios()
    with socket.create_connection((HOST, PORT)) as sock:
        with sock.makefile("wb") as stream_saida:
            escritor = IncidenteOutputStream(stream_saida, relatorios, len(relatorios))
            total = escritor.escrever_objetos()
        print(f"[cliente] {total} bytes enviados para {HOST}:{PORT}")


if __name__ == "__main__":
    main()

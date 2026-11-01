import socket

from fluxo import IncidenteInputStream

HOST = "127.0.0.1"
PORT = 5001

def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(1)
        print(f"[servidor] aguardando em {HOST}:{PORT}...")

        conn, addr = srv.accept()
        with conn:
            print(f"[servidor] conectado por {addr}")
            with conn.makefile("rb") as stream_entrada:
                leitor = IncidenteInputStream(stream_entrada)
                objetos = leitor.ler_objetos()

        print(f"[servidor] {len(objetos)} objeto(s) recebido(s):")
        for indice, objeto in enumerate(objetos, 1):
            print(f"  [{indice}] {objeto}")


if __name__ == "__main__":
    main()

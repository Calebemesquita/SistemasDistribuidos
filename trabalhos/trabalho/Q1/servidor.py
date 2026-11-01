import socket

HOST = "127.0.0.1"
PORT = 5000

def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(1)
        print(f"[servidor] aguardando conexão em {HOST}:{PORT}...")

        conn, addr = srv.accept()
        with conn:
            print(f"[servidor] conectado por {addr}")
            with conn.makefile("rb") as entrada, open("recebido.bin", "wb") as saida:
                total = 0
                while chunk := entrada.read(4096):
                    saida.write(chunk)
                    total += len(chunk)
            print(f"[servidor] recebidos {total} bytes; salvo em recebido.bin")


if __name__ == "__main__":
    main()

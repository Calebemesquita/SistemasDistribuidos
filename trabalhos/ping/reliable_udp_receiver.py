import json
import random
import socket


class ReliableUDPReceiver:
    def __init__(self, host, port, loss_rate=0.3, average_delay=100):
        self.host = host
        self.port = port
        self.loss_rate = loss_rate
        self.average_delay = average_delay
        self.socket = None
        self.running = True
        self.last_seq = -1

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        print("Servidor em execução!")

        while self.running:
            try:
                data, address = self.socket.recvfrom(1024)
                msg = data.decode('utf-8').strip()
                pkt = json.loads(msg)

                if random.random() < self.loss_rate:
                    print("Resposta não enviada, pacote perdido.")
                else:
                    if pkt["seq"] > self.last_seq:
                        self.last_seq = pkt["seq"]
                        print(f"Pacote recebido: {pkt['data']}")
                    else:
                        print(f"Pacote duplicado recebido: {pkt['data']}")
                    self.socket.sendto(str(pkt["seq"]).encode('utf-8'), address)

            except OSError as e:
                if self.running:
                    print(f"Erro: {e}")

    def stop(self):
        print("Encerrando servidor...")
        self.running = False
        if self.socket:
            self.socket.close()

import sys

def main():
    if len(sys.argv) != 3:
        print("Uso: python <nome_arquivo>.py <host> <port>")
        return

    host = sys.argv[1]
    port = int(sys.argv[2])

    receiver = ReliableUDPReceiver(host, port)

    try:
        receiver.start()
    except KeyboardInterrupt:
        receiver.stop()

if __name__ == "__main__":
    main()
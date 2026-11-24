import json
import random
import socket


class ReliableUDPSender:
    def __init__(self, ip, port, packets_amount, loss_rate=0.3):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(1)
        self.packets_amount = packets_amount
        self.num_seq = 0
        self.loss_rate = loss_rate

    def send(self, data):
        while True:
            try:
                msg = json.dumps({
                    "seq": self.num_seq,
                    "data": data
                })

                if random.random() >= self.loss_rate:
                    self.socket.sendto(msg.encode('utf-8'), (self.ip, self.port))
                else:
                    print("Pacote não enviado, pacote perdido.")

                data_recv, _ = self.socket.recvfrom(1024)
                ack = data_recv.decode("utf-8").strip()

                self.num_seq = int(ack) + 1
                print("Dados enviados com sucesso.")
                break
            except TimeoutError:
                print("Timeout: ACK não recebido.")

import sys

def main():
    if len(sys.argv) != 4:
        print("Uso: python <nome_arquivo>.py <host> n")
        return

    host = sys.argv[1]
    port = int(sys.argv[2])
    n = int(sys.argv[3])

    sender = ReliableUDPSender(host, port, n)
    for i in range(n):
        sender.send(f"Mensagem {i}")

if __name__ == "__main__":
    main()
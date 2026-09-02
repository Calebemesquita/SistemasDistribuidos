import socket
import random 
import time 
import sys 
import random
import time
import sys


class PingServer:
    def __init__(self, host, port, loss_rate=0.3, average_delay=100):
        self.host = host
        self.port = port
        self.loss_rate = loss_rate
        self.average_delay = average_delay
        self.socket = None 
        self.running = True 


        #self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.socket.bind(("0.0.0.0", self.port))



    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        print(f"Servidor de ping escutando na ip {self.host} e na porta{self.port}")
        

        
        while self.running:
            try: 
                data, address = self.socket.recvfrom(1024)
                msg = data.decode("utf-8").strip() # strip remove pulo de linha
                self.print_data(address, msg) 
                
                # Simulando erro da rede 
                if random.random() < self.loss_rate:
                    print("resposta não enviada, pacote perdido")
                    continue

                # Simulando o atrasso da rede 
                delay = (random.random() * 2 * self.average_delay) / 1000.0
                time.sleep(delay)

                self.socket.sendto(data, address)
                print("resposta enviada")
            
            except OSError as e:
                if self.running:
                    print(f"Error: {e}")
                
        

    def print_data(self, address, msg):
        ip, port = address
        print(f"Porta e IP [{port}:{ip}] Recebido: {msg}")

    def stop(self):
        print("Encerrando servidor...")
        self.running = False
        if self.socket:
            self.socket.close()


def main():
    if len(sys.argv) != 3:
        print("python3 script.py <host> <port>")
        return
    try:
        port = int(sys.argv[2])
    except ValueError:
        print("porta é um inteiro")
        return

    try:
        host = sys.argv[1]
    except:
        print("Error")

    server = PingServer(host, port)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()

if __name__ == "__main__":
    main()


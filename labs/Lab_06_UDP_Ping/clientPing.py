import socket
import time
import sys
# ta tendo erro quando o pacote é perdido
class PingCliente:
    def __init__(self, ip_server, port, n):
        self.ip_server = ip_server
        self.port = port
        self.n = n
        self.running = True
        self.rtt_list = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self, n):
        msg = f"Ping de {self.ip_server} na porta {self.port} \r\n"
        print(msg)

        for seq in range(self.n):
            self.send_one_ping(seq)
            time.sleep(1)

        self.print_statistics()
        self.stop()

    def send_one_ping(self, num_seq):
        time_send = time.time()
        msg = f"{self.ip_server} : {self.port}"

        try:
        
            self.socket.sendto(msg.encode('utf-8'), (self.ip_server, self.port))
            
            data, server = self.socket.recvfrom(1024)
            
            time_recived = time.time()
            
            rtt = (time_send - time_recived) * 1000
            self.rtt_list.append(rtt)
        
            reply = data.decode("utf-8", errors="ignore").strip()
            print(f"ping {self.ip_server}:{self.port} seq={num_seq} rtt={rtt:.2f}")
        
        except socket.timeout:
        
            print(f"ping {num_seq} falhou, timeout")

    
    def print_statistics(self):

        enviados = self.n
        recebidos = len(self.rtt_list)
        perdidos_pct = 100 * (enviados - recebidos) / enviados if enviados else 0

        print("ping")
        print(f"{enviados} pacotes transmitidos, {recebidos} recebidos, "
              f"{perdidos_pct:.0f}% de perda")

        if self.rtt_list:
            print(
                f"rtt min/avg/max ="
                f"{min(self.rtt_list)}"
                f"{sum(self.rtt_list)}"
                f"{max(self.rtt_list)}"
            )

    def stop(self):
        if self.running == True:
            self.running = False
            self.socket.close()
    
def main():
    if len(sys.argv) != 4:
        print("Error scrpt.py <host> <porta> <numero_pacotes_icmp>")
        return
    server_ip = sys.argv[1]
    try:
        server_port = int(sys.argv[2])
        num = int(sys.argv[3])

    except ValueError:
        print("porta deve ser ineteiro")
        return

    cliente = PingCliente(server_ip, server_port, num)
    try:
        cliente.start(num)
    except KeyboardInterrupt:
        print("Teclado interrompeu")
        cliente.stop()


if __name__ == "__main__":
    main()


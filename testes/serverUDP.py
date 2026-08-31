import socket


class UDPServer:
    def __init__(self, port, host):
        self.host = host
        self.port = port


        self.socket(socket.AF_INET, socket.SOCK_DGRAM)


    def start(self):
        self.socket.bind((self.host, self.port))

        data, address = self.socket.recvfrom(1024)
        print(data)
        print(address)

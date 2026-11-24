class Listener:
    def __init__(self, sock, callback):
        self._sock = sock
        self._callback = callback

    def listen(self):
        while True:
            data, _ = self._sock.recvfrom(4096)
            self._callback(data)
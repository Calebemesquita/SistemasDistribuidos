from io import RawIOBase
from typing import Protocol

from protocol.notification import Notification


class ReadableStream(Protocol):
    def read(self, size: int = -1) -> bytes: ...
    def readline(self) -> bytes: ...

class NotificationInputStream(RawIOBase):
    def __init__(self, source: ReadableStream):
        super().__init__()
        self.source = source

    def readable(self) -> bool:
        return True

    def read(self, size: int = -1) -> bytes:
        return self.source.read(size)
    
    def read_notification(self) -> Notification | None:
        data = self.source.readline()

        if not data:
            return None

        return Notification.from_bytes(data)

    def readline(self) -> bytes:
        return self.source.readline()
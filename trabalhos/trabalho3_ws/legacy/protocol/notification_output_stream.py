from collections.abc import Sequence
from io import RawIOBase
from typing import Protocol

from protocol.notification import Notification


class WritableStream(Protocol):
    def write(self, data: bytes) -> int: ...

    def flush(self) -> None: ...

class NotificationOutputStream(RawIOBase):
    def __init__(self, destination: WritableStream, notifications: Sequence[Notification], count: int):
        super().__init__()
        
        self.destination = destination
        self.notifications = notifications
        self.count = count

    def writable(self) -> bool:
        return True

    def write(self, data) -> int:
        return self.destination.write(data)

    def write_notifications(self) -> None:
        for notification in self.notifications[:self.count]:
            data = notification.to_bytes() + b"\n" 
            self.write(data)

        self.destination.flush()

    def flush(self) -> None:
        self.destination.flush()
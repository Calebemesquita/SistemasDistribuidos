import json
import time
from dataclasses import dataclass, field

from protocol.notification_type import NotificationType


@dataclass
class Notification:
    type: NotificationType
    content: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self):
        return {
            "type": self.type.value,
            "content": self.content,
            "timestamp": self.timestamp
        }

    def to_bytes(self):
        return json.dumps(
            self.to_dict(), 
            ensure_ascii=False
        ).encode()

    @classmethod
    def from_bytes(cls, data: bytes):
        data_dict = json.loads(data.decode())

        return cls(
            type=NotificationType(data_dict["type"]),
            content=data_dict["content"],
            timestamp=data_dict["timestamp"]
        )
from pydantic import BaseModel, Field, field_validator

from protocol.notification_type import NotificationType


class CreateNotificationRequest(BaseModel):
    type: NotificationType = NotificationType.NOTIFICATION
    content: str = Field(..., min_length=1, max_length=500)

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Notification content cannot be blank.")
        return value


class NotificationRecord(BaseModel):
    id: int
    type: NotificationType
    content: str
    timestamp: float


class SubscriptionRequest(BaseModel):
    client_id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=100)

    @field_validator("client_id", "name")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Value cannot be blank.")
        return value

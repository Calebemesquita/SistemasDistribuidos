from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies.services import get_notification_service
from api.models.notification import (
    CreateNotificationRequest,
    NotificationRecord,
    SubscriptionRequest,
)
from api.services.notification_service import NotificationService
from notifications.publisher import NotificationPublishError

router = APIRouter(
    prefix="/notifications",
    tags=["Notificações"],
)


@router.get(
    path="/",
    response_model=list[NotificationRecord],
    name="List notifications",
    status_code=HTTPStatus.OK,
)
def list_notifications(
    notification_service: Annotated[
        NotificationService,
        Depends(get_notification_service),
    ],
) -> list[NotificationRecord]:
    """Lista notificações publicadas desde que a API iniciou."""
    return notification_service.list_items()


@router.post("/subscriptions", name="Subscribe to API notifications")
def subscribe(
    request: SubscriptionRequest,
    notification_service: Annotated[
        NotificationService, Depends(get_notification_service)
    ],
) -> dict:
    try:
        return notification_service.subscribe(request.client_id, request.name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/subscriptions/{client_id}", name="Cancel API notification subscription")
def unsubscribe(
    client_id: str,
    notification_service: Annotated[
        NotificationService, Depends(get_notification_service)
    ],
) -> dict:
    return notification_service.unsubscribe(client_id)


@router.get("/subscriptions/{client_id}", name="Poll API notifications")
def poll_notifications(
    client_id: str,
    notification_service: Annotated[
        NotificationService, Depends(get_notification_service)
    ],
    after: int = 0,
) -> dict:
    try:
        result = notification_service.poll(client_id, after)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return {
        "events": [
            {
                "id": event["sequencia"],
                "type": event["tipo"],
                "content": event["mensagem"],
                "timestamp": event["data_hora"],
            }
            for event in result["eventos"]
        ],
        "cursor": result["ultimo"],
    }


@router.post(
    path="/",
    response_model=NotificationRecord,
    name="Publish a notification",
    status_code=HTTPStatus.CREATED,
)
def create_notification(
    request: CreateNotificationRequest,
    notification_service: Annotated[
        NotificationService,
        Depends(get_notification_service),
    ],
) -> NotificationRecord:
    """Publica no canal da biblioteca e no RabbitMQ."""
    try:
        return notification_service.publish(
            content=request.content,
            type=request.type,
        )
    except NotificationPublishError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de notificações indisponível.",
        ) from exc

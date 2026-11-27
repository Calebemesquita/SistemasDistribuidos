from datetime import datetime

from biblioteca_rpc.entities import Biblioteca, Notificacao, serializar

from api.models.notification import NotificationRecord
from notifications.publisher import publish_notification
from protocol.notification import Notification
from protocol.notification_type import NotificationType


_DOMAIN_TO_PROTOCOL = {
    "ALERTA": NotificationType.ALERT,
    "NOTIFICACAO": NotificationType.NOTIFICATION,
    "ATUALIZACAO": NotificationType.UPDATE,
}
_PROTOCOL_TO_DOMAIN = {
    NotificationType.ALERT: "ALERTA",
    NotificationType.NOTIFICATION: "NOTIFICACAO",
    NotificationType.UPDATE: "ATUALIZACAO",
}


class NotificationService:
    """Adapta notificações do canal T2 ao protocolo e broker do Trabalho 3."""

    def __init__(self, library: Biblioteca) -> None:
        self.library = library

    def list_items(self) -> list[NotificationRecord]:
        with self.library.transacao():
            return [self._to_record(event) for event in self.library.canal.notificacoes]

    @staticmethod
    def _to_record(event: Notificacao) -> NotificationRecord:
        data = serializar(event)
        event_type = _DOMAIN_TO_PROTOCOL[data["tipo"]]
        timestamp = datetime.fromisoformat(data["data_hora"]).timestamp()
        return NotificationRecord(
            id=data["sequencia"],
            type=event_type,
            content=data["mensagem"],
            timestamp=timestamp,
        )

    def publish_existing(self, event: Notificacao) -> NotificationRecord:
        with self.library.transacao():
            record = self._to_record(event)
            protocol_event = Notification(
                type=record.type,
                content=record.content,
                timestamp=record.timestamp,
            )
            try:
                publish_notification(protocol_event)
            except Exception:
                self.library.canal.cancelar_ultima(record.id)
                raise
            return record

    def publish(
        self,
        content: str,
        type: NotificationType = NotificationType.NOTIFICATION,
    ) -> NotificationRecord:
        with self.library.transacao():
            domain_type = _PROTOCOL_TO_DOMAIN[type]
            self.library.canal.publicar(content, domain_type)
            event = self.library.canal.notificacoes[-1]
            return self.publish_existing(event)

    def publish_latest(self) -> NotificationRecord:
        with self.library.transacao():
            if not self.library.canal.notificacoes:
                raise ValueError("No domain notification is available to publish.")
            return self.publish_existing(self.library.canal.notificacoes[-1])

    def subscribe(self, client_id: str, name: str) -> dict:
        with self.library.transacao():
            return self.library.canal.inscrever(client_id, name)

    def unsubscribe(self, client_id: str) -> dict:
        with self.library.transacao():
            return self.library.canal.cancelar_inscricao(client_id)

    def poll(self, client_id: str, after: int = 0) -> dict:
        with self.library.transacao():
            return self.library.canal.consultar(client_id, after)

import unittest
from unittest.mock import patch

from api.dependencies.services import get_library
from api.services.book_service import BookService
from api.services.loan_service import LoanService
from api.services.notification_service import NotificationService
from biblioteca_rpc.entities import (
    Alerta,
    Atualizacao,
    Bibliotecario,
    Biblioteca,
    CanalNotificacoes,
    Catalogo,
    HistoricoEmprestimos,
    Inscricoes,
    Leitor,
    Livro,
    Notificacao,
    Serializavel,
    Usuario,
    serializar,
)
from protocol.notification import Notification
from protocol.notification_type import NotificationType


class Trabalho2DomainIntegrationTests(unittest.TestCase):
    def setUp(self):
        get_library.cache_clear()
        self.library = get_library()

    def test_aggregate_contains_the_classes_from_the_class_diagram(self):
        self.assertIsInstance(self.library, Biblioteca)
        self.assertIsInstance(self.library.catalogo, Catalogo)
        self.assertIsInstance(self.library.historico, HistoricoEmprestimos)
        self.assertIsInstance(self.library.canal, CanalNotificacoes)
        self.assertIsInstance(self.library.canal.inscricoes, Inscricoes)
        self.assertIsInstance(self.library.catalogo.livros["1"], Livro)

    def test_domain_roles_and_notifications_use_inheritance_and_serialization(self):
        reader = Leitor("ana", "Ana")
        librarian = Bibliotecario("bia", "Bia", "mat-1")
        alert = Alerta(1, "Empréstimo", "agora")
        update = Atualizacao(2, "Devolução", "agora")
        for entity in (reader, librarian, Livro("1", "Título", "Autora"), alert, update):
            self.assertIsInstance(entity, Serializavel)
            self.assertIsInstance(serializar(entity), dict)
        self.assertIsInstance(reader, Usuario)
        self.assertIsInstance(librarian, Usuario)
        self.assertIsInstance(alert, Notificacao)
        self.assertIsInstance(update, Notificacao)

    @patch("api.services.notification_service.publish_notification")
    def test_http_services_change_the_same_work2_objects(self, publish):
        books = BookService(self.library)
        loans = LoanService(self.library)
        notifications = NotificationService(self.library)

        book = books.add_book("Novo título", "Autora", "bia", "Bia")
        self.assertEqual(book["id"], 4)
        self.assertIsInstance(self.library.usuarios["bia"], Bibliotecario)
        notifications.publish_latest()
        self.assertIsInstance(self.library.canal.notificacoes[-1], Atualizacao)

        loan = loans.create_loan(book["id"], "ana")
        self.assertIsInstance(self.library.usuarios["ana"], Leitor)
        self.assertEqual(self.library.usuarios["ana"].emprestimos, ["4"])
        notifications.publish_latest()
        self.assertIsInstance(self.library.canal.notificacoes[-1], Alerta)

        returned = loans.return_loan(loan["id"])
        notifications.publish_latest()
        self.assertTrue(returned["returned"])
        self.assertEqual(self.library.usuarios["ana"].emprestimos, [])
        self.assertIsInstance(self.library.canal.notificacoes[-1], Atualizacao)
        self.assertEqual(publish.call_count, 3)
        self.assertIsInstance(publish.call_args_list[1].args[0], Notification)

    @patch("api.services.notification_service.publish_notification")
    def test_notification_api_adapter_reuses_work2_channel(self, publish):
        service = NotificationService(self.library)
        service.subscribe("ana", "Ana")
        record = service.publish("Livro reservado", NotificationType.ALERT)
        polled = service.poll("ana", after=0)
        self.assertEqual(record.type, NotificationType.ALERT)
        self.assertEqual(polled["eventos"][0]["mensagem"], "Livro reservado")
        self.assertIsInstance(self.library.canal.notificacoes[0], Alerta)
        self.assertEqual(service.list_items(), [record])
        publish.assert_called_once()


if __name__ == "__main__":
    unittest.main()

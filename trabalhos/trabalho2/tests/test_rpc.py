import unittest
from xmlrpc.client import Binary
from biblioteca_rpc.client import RPCClient, RPCError
from biblioteca_rpc.entities import Alerta, Atualizacao, Leitor, Usuario, Bibliotecario, Notificacao
from biblioteca_rpc.protocol import make_request, decode_json, payload
from biblioteca_rpc.server import RPCDispatcher


class LocalTransport:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
    def exchange(self, binary):
        return self.dispatcher.exchange(binary)


class Tests(unittest.TestCase):
    def setUp(self):
        self.dispatcher = RPCDispatcher()
        self.client = RPCClient.__new__(RPCClient)
        self.client._transport = LocalTransport(self.dispatcher)
        self.biblioteca = self.client.object("biblioteca")
        self.canal = self.biblioteca.call("obter_canal")

    def test_heranca(self):
        self.assertIsInstance(Leitor("1", "Ana"), Usuario)
        self.assertIsInstance(Bibliotecario("2", "Bia"), Usuario)
        self.assertIsInstance(Alerta(1, "X", "hoje"), Notificacao)
        self.assertIsInstance(Atualizacao(1, "X", "hoje"), Notificacao)

    def test_referencia_remota(self):
        self.assertEqual(self.canal.remote_ref, "notificacoes")

    def test_serializacao_e_notificacao_multipla(self):
        self.canal.call("inscrever", cliente_id="A", nome="Ana")
        self.canal.call("inscrever", cliente_id="B", nome="Bruno")
        self.biblioteca.call("cadastrar_livro", livro={"isbn": "123", "titulo": "Livro", "autor": "Autor"})
        a = self.canal.call("consultar", cliente_id="A", apos=0)
        b = self.canal.call("consultar", cliente_id="B", apos=0)
        self.assertEqual(a["eventos"], b["eventos"])
        self.assertEqual(a["eventos"][0]["tipo"], "ATUALIZACAO")
        self.assertEqual(self.canal.call("consultar", cliente_id="B", apos=1)["eventos"], [])

    def test_metodos_remotos(self):
        self.biblioteca.call("cadastrar_livro", livro={"isbn": "5", "titulo": "ABC", "autor": "X"})
        self.assertEqual(len(self.biblioteca.call("listar_livros")), 1)
        self.assertEqual(self.biblioteca.call("emprestar_livro", isbn="5", leitor_id="A")["isbn"], "5")
        with self.assertRaises(RPCError):
            self.biblioteca.call("emprestar_livro", isbn="5", leitor_id="B")
        self.assertTrue(self.biblioteca.call("devolver_livro", isbn="5")["disponivel"])

    def test_requisicao_duplicada_nao_reexecuta(self):
        request = make_request("notificacoes", "publicar", {"mensagem": "Teste", "tipo": "ALERTA"}, request_id="fixo")
        first = self.dispatcher.exchange(Binary(request)).data
        second = self.dispatcher.exchange(Binary(request)).data
        self.assertEqual(first, second)
        self.assertEqual(len(self.dispatcher.canal.notificacoes), 1)
        self.assertEqual(payload(decode_json(first))["result"]["mensagem"], "Teste")

    def test_requisicao_mal_formada(self):
        with self.assertRaises(ValueError):
            self.dispatcher.getRequest(b'{}')


if __name__ == "__main__":
    unittest.main()

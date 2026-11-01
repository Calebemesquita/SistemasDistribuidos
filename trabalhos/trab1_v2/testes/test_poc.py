from __future__ import annotations

import io
import socket
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from ..cliente.client import criar_relatorio_remoto
from ..modelos.models import Ataque, Severidade
from ..servidor.server import atender_cliente
from ..streams.stream import AtaqueInputStream, AtaqueOutputStream


def ataques_exemplo():
    return [
        Ataque.novo("10.0.0.2", "10.0.0.1", "PORT_SCAN", Severidade.ALTA, 10.0, "varredura"),
        Ataque.novo("10.0.0.4", "10.0.0.3", "DDoS", Severidade.CRITICA, 20.0, "pico"),
    ]


class ProvasDeConceitoTest(unittest.TestCase):
    def test_ataque_output_stream_e_subclasse_de_outputstream(self):
        stream = AtaqueOutputStream(io.BytesIO(), ataques_exemplo(), 1)
        self.assertIsInstance(stream, io.RawIOBase)
        self.assertIsInstance(stream, io.IOBase)
        self.assertTrue(stream.writable())

        n = stream.write(b"bytes crus\n")
        self.assertEqual(n, len(b"bytes crus\n"))

    def test_ataque_input_stream_e_subclasse_de_inputstream(self):
        stream = AtaqueInputStream(io.BytesIO(b"linha\n"))
        self.assertIsInstance(stream, io.RawIOBase)
        self.assertIsInstance(stream, io.IOBase)
        self.assertTrue(stream.readable())

        self.assertEqual(stream.readline(), b"linha\n")

    def test_streams_saida_padrao_e_entrada_padrao(self):
        
        bytes_saida = io.BytesIO()
        saida_padrao = io.TextIOWrapper(bytes_saida, encoding="utf-8")
        with patch("sys.stdout", saida_padrao):
            AtaqueOutputStream(sys.stdout.buffer, ataques_exemplo(), 1).enviar_dados()

        bytes_entrada = io.BytesIO(bytes_saida.getvalue())
        entrada_padrao = io.TextIOWrapper(bytes_entrada, encoding="utf-8")
        with patch("sys.stdin", entrada_padrao):
            recebidos = AtaqueInputStream(sys.stdin.buffer).receber_dados()
        self.assertEqual(len(recebidos), 1)

    def test_streams_em_arquivo(self):
        with tempfile.TemporaryFile("w+b") as arquivo:
            AtaqueOutputStream(arquivo, ataques_exemplo(), 2).enviar_dados()
            arquivo.seek(0)
            recebidos = AtaqueInputStream(arquivo).receber_dados()
            self.assertEqual(len(recebidos), 2)

    def test_output_stream_para_servidor_tcp(self):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.bind(("127.0.0.1", 0))
        servidor.listen(1)
        porta = servidor.getsockname()[1]
        recebidos = []

        def receber():
            conexao, _ = servidor.accept()
            with conexao, conexao.makefile("rb") as origem:
                recebidos.extend(AtaqueInputStream(origem).receber_dados())
            servidor.close()

        thread = threading.Thread(target=receber)
        thread.start()
        with socket.create_connection(("127.0.0.1", porta)) as cliente, cliente.makefile("wb") as destino:
            AtaqueOutputStream(destino, ataques_exemplo(), 2).enviar_dados()
        thread.join(timeout=2)
        self.assertEqual(len(recebidos), 2)

    def test_input_stream_de_cliente_tcp(self):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.bind(("127.0.0.1", 0))
        servidor.listen(1)
        porta = servidor.getsockname()[1]

        def enviar():
            conexao, _ = servidor.accept()
            with conexao, conexao.makefile("wb") as destino:
                AtaqueOutputStream(destino, ataques_exemplo(), 2).enviar_dados()
            servidor.close()

        thread = threading.Thread(target=enviar)
        thread.start()
        with socket.create_connection(("127.0.0.1", porta)) as cliente, cliente.makefile("rb") as origem:
            recebidos = AtaqueInputStream(origem).receber_dados()
            self.assertEqual(len(recebidos), 2)
        thread.join(timeout=2)

    def test_serializacao_cliente_servidor(self):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.bind(("127.0.0.1", 0))
        servidor.listen(1)
        porta = servidor.getsockname()[1]

        def aceitar():
            conexao, endereco = servidor.accept()
            atender_cliente(conexao, endereco)
            servidor.close()

        thread = threading.Thread(target=aceitar)
        thread.start()
        with redirect_stdout(io.StringIO()):
            relatorio = criar_relatorio_remoto("127.0.0.1", porta, "analista", ataques_exemplo())
            thread.join(timeout=2)
        self.assertEqual(relatorio.gerado_por, "analista")
        self.assertEqual(len(relatorio.ataques), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)

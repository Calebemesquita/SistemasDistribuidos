from __future__ import annotations

import json
import threading
import time
import unittest


from ..multicast.cliente_multicast import autenticar, entrar_no_grupo, sair_do_grupo


from ..multicast.servidor_multicast import (
    GRUPO_MULTICAST,
    PORTA_MULTICAST,
    ServidorAutenticacao,
    criar_socket_multicast_envio,
    enviar_multicast,
    enviar_varios_concorrentemente,
)


class MulticastTest(unittest.TestCase):
    def setUp(self):
        self.auth = ServidorAutenticacao(host="127.0.0.1", porta=0)
        self.porta_tcp = self.auth.executar_em_thread()

    def test_autenticacao_tcp_libera_dados_do_grupo(self):
        resposta = autenticar("analista-1", host="127.0.0.1", porta=self.porta_tcp)
        self.assertTrue(resposta["sucesso"])
        self.assertEqual(resposta["grupo"], GRUPO_MULTICAST)
        self.assertEqual(resposta["porta_multicast"], PORTA_MULTICAST)

    def test_autenticacao_falha_sem_cliente_id(self):
        resposta = autenticar("", host="127.0.0.1", porta=self.porta_tcp)
        self.assertFalse(resposta["sucesso"])

    def test_join_e_leave_group(self):
        sock = entrar_no_grupo()
        sair_do_grupo(sock)
        with self.assertRaises(OSError):
            sock.recvfrom(1024)

    def test_multiplos_clientes_recebem_a_mesma_mensagem(self):
        receptores = [entrar_no_grupo() for _ in range(2)]
        for sock in receptores:
            sock.settimeout(2)

        emissor = criar_socket_multicast_envio()
        time.sleep(0.2)  
        enviar_multicast(emissor, "ALERTA", "novo dado disponível")
        emissor.close()

        recebidos = []
        for sock in receptores:
            dados, _ = sock.recvfrom(4096)
            recebidos.append(json.loads(dados.decode("utf-8")))
            sair_do_grupo(sock)

        self.assertEqual(len(recebidos), 2)
        for alerta in recebidos:
            self.assertEqual(alerta["tipo"], "ALERTA")
            self.assertEqual(alerta["mensagem"], "novo dado disponível")

    def test_thread_de_escuta_independente_da_interacao(self):
        sock = entrar_no_grupo()
        sock.settimeout(2)
        recebidos = []

        def escutar():
            dados, _ = sock.recvfrom(4096)
            recebidos.append(json.loads(dados.decode("utf-8")))

        thread_escuta = threading.Thread(target=escutar)
        thread_escuta.start()

        emissor = criar_socket_multicast_envio()
        time.sleep(0.2)
        enviar_multicast(emissor, "NOTIFICACAO", "thread de escuta ativa")
        emissor.close()

        thread_escuta.join(timeout=3)
        sair_do_grupo(sock)

        self.assertEqual(len(recebidos), 1)
        self.assertEqual(recebidos[0]["tipo"], "NOTIFICACAO")

    def test_envio_concorrente_de_multiplas_mensagens(self):
        receptor = entrar_no_grupo()
        receptor.settimeout(3)

        emissor = criar_socket_multicast_envio()
        time.sleep(0.2)

        alertas_para_enviar = [
            ("ALERTA", "mensagem concorrente 1"),
            ("ALERTA", "mensagem concorrente 2"),
            ("NOTIFICACAO", "mensagem concorrente 3"),
            ("ATUALIZACAO", "mensagem concorrente 4"),
        ]
        publicados = enviar_varios_concorrentemente(emissor, alertas_para_enviar)
        emissor.close()

        self.assertEqual(len(publicados), len(alertas_para_enviar))

        recebidos = []
        try:
            for _ in range(len(alertas_para_enviar)):
                dados, _ = receptor.recvfrom(4096)
                recebidos.append(json.loads(dados.decode("utf-8")))
        finally:
            sair_do_grupo(receptor)

        self.assertEqual(len(recebidos), len(alertas_para_enviar))
        mensagens_recebidas = {r["mensagem"] for r in recebidos}
        mensagens_esperadas = {m for _, m in alertas_para_enviar}
        self.assertEqual(mensagens_recebidas, mensagens_esperadas)


if __name__ == "__main__":
    unittest.main(verbosity=2)
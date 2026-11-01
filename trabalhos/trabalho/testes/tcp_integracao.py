"""Exercita os clientes/servidores TCP das questões 1, 2 e 3 em loopback."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
AMBIENTE = os.environ | {"PYTHONPATH": str(RAIZ)}


def verificar_par_tcp(
    modulo_servidor: str,
    modulo_cliente: str,
    texto_cliente: str,
    texto_servidor: str,
    servidor_persistente: bool = False,
) -> None:
    with tempfile.TemporaryDirectory(prefix="trabalho1-tcp-") as diretorio:
        servidor = subprocess.Popen(
            [sys.executable, "-u", "-m", modulo_servidor],
            cwd=diretorio,
            env=AMBIENTE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            linha_pronta = servidor.stdout.readline()
            if "aguardando" not in linha_pronta:
                raise RuntimeError(
                    f"{modulo_servidor} não iniciou: {linha_pronta}"
                )

            cliente = subprocess.run(
                [sys.executable, "-m", modulo_cliente],
                cwd=diretorio,
                env=AMBIENTE,
                capture_output=True,
                text=True,
                timeout=15,
                check=True,
            )
            if texto_cliente not in cliente.stdout:
                raise AssertionError(
                    f"saída inesperada de {modulo_cliente}: {cliente.stdout}"
                )

            if servidor_persistente:
                servidor.terminate()
            saida_servidor, _ = servidor.communicate(timeout=5)
            if texto_servidor not in saida_servidor:
                raise AssertionError(
                    f"saída inesperada de {modulo_servidor}: {saida_servidor}"
                )

            if modulo_servidor == "Q1.servidor":
                arquivo_recebido = Path(diretorio, "recebido.bin")
                if not arquivo_recebido.exists() or arquivo_recebido.stat().st_size == 0:
                    raise AssertionError("Q1 não gravou os bytes recebidos")
        finally:
            if servidor.poll() is None:
                servidor.terminate()
                servidor.communicate(timeout=5)


def main() -> None:
    verificar_par_tcp(
        "Q1.servidor", "Q1.cliente", "bytes enviados", "salvo em recebido.bin"
    )
    print("Q1 TCP: cliente enviou e servidor gravou os bytes")

    verificar_par_tcp(
        "Q2.servidor", "Q2.cliente", "bytes enviados", "3 objeto(s) recebido(s)"
    )
    print("Q2 TCP: servidor reconstruiu os relatórios")

    verificar_par_tcp(
        "Q3.servidor",
        "Q3.cliente",
        "status='ERRO'",
        "cliente desconectou",
        servidor_persistente=True,
    )
    print("Q3 TCP: cliente e servidor trocaram requests e replies")


if __name__ == "__main__":
    main()

import json
import socket
import threading

from ..modelos.models import Ataque
from ..servicos.sevice import ServicoRelatorios


HOST, PORTA = "127.0.0.1", 5051
servico = ServicoRelatorios()
_lock_servico = threading.Lock()


def processar_requisicao(requisicao: dict) -> dict:
    try:
        if requisicao.get("operacao") != "criar_relatorio":
            return {"sucesso": False, "erro": "operação desconhecida"}

        params = requisicao["parametros"]
        ataques = [Ataque.from_dict(item) for item in params.get("ataques", [])]
        with _lock_servico:
            relatorio = servico.criar_relatorio(params["gerado_por"], ataques)

        return {"sucesso": True, "relatorio": relatorio.to_dict()}
    except (KeyError, TypeError, ValueError) as erro:
        return {"sucesso": False, "erro": str(erro)}


def atender_cliente(conexao, endereco):
    print(f"\n SERVER ->  Conexão tcp estabelecida com o cliente {endereco}.")
    with conexao, conexao.makefile("rwb") as fluxo:
        linha = fluxo.readline()
        if not linha:
            return
        
        requisicao = json.loads(linha.decode("utf-8"))
        print(f"[SERVIDOR] Mensagem de request desempacotada com sucess a pperação: {requisicao.get('operacao')}")
        
        resposta = processar_requisicao(requisicao)

        print("SERVER -> Empacotando mensagem de reply para enviar ao cliente...")

        fluxo.write((json.dumps(resposta) + "\n").encode("utf-8"))
        fluxo.flush()
        print("SERVER ->  Reply enviado e conexão encerrada")


def executar(host: str = HOST, porta: int = PORTA) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((host, porta))
        servidor.listen()
        print(f"Servidor de serialização em {host}:{porta}")
        while True:
            conexao, endereco = servidor.accept()
            threading.Thread(target=atender_cliente, args=(conexao, endereco), daemon=True).start()


if __name__ == "__main__":
    executar()

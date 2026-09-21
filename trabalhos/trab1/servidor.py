"""
Servidor de demonstração da Serialização (item 3 do enunciado).

Implementa comunicação cliente-servidor via socket TCP trocando fluxos de
bytes, com empacotamento/desempacotamento explícito de cada mensagem:

    - o servidor DESEMPACOTA a mensagem de requisição enviada pelo cliente;
    - o servidor processa a requisição chamando ServicoVotacao/ServicoAdministracao;
    - o servidor EMPACOTA a mensagem de resposta (reply) e a envia para o cliente.

O servidor é multithreaded: cada conexão de cliente é atendida em uma
thread própria, permitindo vários clientes simultâneos. Esse mesmo padrão
(reutilizando common/protocolo.py e common/servicos.py) é reaproveitado,
com mais operações, no servidor final de votação em votacao/servidor.py.

Uso:
    python -m serializacao.servidor
"""
import socket
import threading

from common.pojos import Candidato
from common.protocolo import desempacotar, enviar_mensagem
from common.servicos import ErroServico, ServicoAdministracao, ServicoVotacao

HOST = "0.0.0.0"
PORTA = 5051

# Estado compartilhado por todos os clientes desta demonstração.
servico_votacao = ServicoVotacao(
    candidatos=[
        Candidato(id=1, nome="Ana Souza", partido="Partido Verde"),
        Candidato(id=2, nome="Bruno Lima", partido="Partido Azul"),
    ]
)
servico_admin = ServicoAdministracao(servico_votacao)


def processar_requisicao(requisicao: dict) -> dict:
    """Executa a operação pedida e devolve o dict de resposta (ainda não empacotado)."""
    operacao = requisicao.get("operacao")
    parametros = requisicao.get("parametros", {})
    try:
        if operacao == "login_eleitor":
            eleitor = servico_votacao.login_eleitor(parametros["titulo"], parametros["nome"])
            return {"sucesso": True, "dados": eleitor.to_dict()}

        if operacao == "listar_candidatos":
            candidatos = servico_votacao.listar_candidatos()
            return {"sucesso": True, "dados": [c.to_dict() for c in candidatos]}

        if operacao == "votar":
            voto = servico_votacao.votar(parametros["titulo"], parametros["id_candidato"])
            return {"sucesso": True, "dados": voto.to_dict()}

        if operacao == "login_admin":
            servico_admin.login_admin(parametros["usuario"], parametros["senha"])
            return {"sucesso": True, "dados": {"autenticado": True}}

        return {"sucesso": False, "erro": f"Operação desconhecida: {operacao}"}
    except ErroServico as e:
        return {"sucesso": False, "erro": str(e)}
    except KeyError as e:
        return {"sucesso": False, "erro": f"Parâmetro obrigatório ausente: {e}"}


def atender_cliente(conexao: socket.socket, endereco):
    print(f"[servidor] Cliente conectado: {endereco}")
    arquivo_leitura = conexao.makefile("rb")
    arquivo_escrita = conexao.makefile("wb")
    try:
        while True:
            try:
                # o servidor DESEMPACOTA a mensagem de requisição do cliente
                requisicao = desempacotar(arquivo_leitura)
            except ConnectionError:
                break  # cliente encerrou a conexão

            print(f"[servidor] Requisição de {endereco}: {requisicao}")
            resposta = processar_requisicao(requisicao)

            # o servidor EMPACOTA a mensagem de reply e envia para o cliente
            enviar_mensagem(arquivo_escrita, resposta)
            print(f"[servidor] Resposta enviada para {endereco}: {resposta}")
    finally:
        arquivo_leitura.close()
        arquivo_escrita.close()
        conexao.close()
        print(f"[servidor] Cliente desconectado: {endereco}")


def executar(host: str = HOST, porta: int = PORTA):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((host, porta))
        servidor.listen(5)
        print(f"[servidor] Escutando em {host}:{porta}")
        while True:
            conexao, endereco = servidor.accept()
            threading.Thread(target=atender_cliente, args=(conexao, endereco), daemon=True).start()


if __name__ == "__main__":
    executar()

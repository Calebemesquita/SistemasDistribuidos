"""Demonstração rápida. Execute com o servidor ligado."""
from .client import RPCClient


def main():
    client = RPCClient()
    biblioteca = client.object("biblioteca")
    canal = biblioteca.call("obter_canal")  # referência a outro objeto remoto
    canal.call("inscrever", cliente_id="cliente-A", nome="Ana")
    canal.call("inscrever", cliente_id="cliente-B", nome="Bruno")
    try:
        biblioteca.call("cadastrar_livro", livro={"isbn": "978-01", "titulo": "Sistemas Distribuídos", "autor": "Coulouris"})
    except Exception as exc:
        print("Cadastro:", exc)
    print("Livros:", biblioteca.call("listar_livros"))
    print("Cliente A recebeu:", canal.call("consultar", cliente_id="cliente-A", apos=0)["eventos"])
    print("Cliente B recebeu:", canal.call("consultar", cliente_id="cliente-B", apos=0)["eventos"])
    canal.call("cancelar_inscricao", cliente_id="cliente-B")


if __name__ == "__main__":
    main()

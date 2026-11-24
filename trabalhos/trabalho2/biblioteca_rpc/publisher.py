"""Publicador textual de notificações, usando RPC."""
from .client import RPCClient


def main():
    canal = RPCClient().object("biblioteca").call("obter_canal")
    print("Tipos: NOTIFICACAO, ALERTA, ATUALIZACAO. Ctrl+C para sair.")
    try:
        while True:
            tipo = input("Tipo [NOTIFICACAO]: ").strip().upper() or "NOTIFICACAO"
            mensagem = input("Mensagem: ").strip()
            print(canal.call("publicar", mensagem=mensagem, tipo=tipo))
    except (KeyboardInterrupt, EOFError):
        print("\nEncerrado")


if __name__ == "__main__":
    main()

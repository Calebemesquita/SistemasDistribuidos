"""Cliente textual que acompanha as notificações via consultas RPC periódicas."""
import argparse
import time
from uuid import uuid4
from .client import RPCClient, RPCError


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nome", default="Cliente")
    parser.add_argument("--intervalo", type=float, default=1.0)
    args = parser.parse_args()
    client = RPCClient()
    canal = client.object("biblioteca").call("obter_canal")
    client_id = uuid4().hex
    canal.call("inscrever", cliente_id=client_id, nome=args.nome)
    print(f"{args.nome}: inscrito em {canal.remote_ref}; pressione Ctrl+C para sair")
    cursor = 0
    try:
        while True:
            lote = canal.call("consultar", cliente_id=client_id, apos=cursor)
            for evento in lote["eventos"]:
                print(f"[{evento['tipo']}] #{evento['sequencia']}: {evento['mensagem']}")
                cursor = evento["sequencia"]
            time.sleep(args.intervalo)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            canal.call("cancelar_inscricao", cliente_id=client_id)
        except (RPCError, OSError):
            pass


if __name__ == "__main__":
    main()

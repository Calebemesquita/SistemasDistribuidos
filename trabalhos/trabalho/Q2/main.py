import sys

from fluxo import IncidenteInputStream


def imprimir(objetos):
    print(f"\n→ {len(objetos)} objeto(s) lido(s):\n")
    for i, o in enumerate(objetos, 1):
        print(f"  [{i}] {o}")
        print(f"       to_dict: {o.to_dict()}")


def teste_2b_stdin():
    """Lê objetos da entrada padrão (via pipe)."""
    stream = IncidenteInputStream(sys.stdin.buffer)
    objetos = stream.ler_objetos()      # lê até EOF
    imprimir(objetos)


def teste_2c_arquivo(caminho: str = "saida.bin"):
    """Lê objetos de um arquivo binário."""
    with open(caminho, "rb") as f:
        stream = IncidenteInputStream(f)
        objetos = stream.ler_objetos()  # lê até EOF
    imprimir(objetos)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stdin":
        teste_2b_stdin()
    else:
        teste_2c_arquivo()

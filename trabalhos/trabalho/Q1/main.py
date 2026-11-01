import sys

from POJO import RelatorioIncidente
from fluxo import IncidenteOutputStream


def construir_relatorios() -> list[RelatorioIncidente]:
    return [
        RelatorioIncidente(1, 1, "Ana", "Resolvido", "Reboot no servidor", None, []),
        RelatorioIncidente(2, 1, "Bia", "Escalado", "Enviado ao Tier 2", None, ["log.txt"]),
        RelatorioIncidente(3, 2, "Caio", "Resolvido", "Troca de disco", None, ["foto.png", "dmesg.log"]),
    ]


def main() -> None:
    relatorio = construir_relatorios()

    print("c1b: destino = stdout", file=sys.stderr)
    stream = IncidenteOutputStream(sys.stdout.buffer, relatorio, len(relatorio))
    stream.escrever_objetos()

    # ---- 1c: destino = arquivo ----
    print(" 1c: destino = arquivo ", file=sys.stderr)
    with open("saida.bin", "wb") as f:
        stream = IncidenteOutputStream(f, relatorio, len(relatorio))
        bytes_escritos = stream.escrever_objetos()
    print(f"{bytes_escritos} bytes escritos em saida.bin", file=sys.stderr)

if __name__ == "__main__":
    main()

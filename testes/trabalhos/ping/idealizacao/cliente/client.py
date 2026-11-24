import json
import socket
import sys

from ..modelos.models import Ataque, RelatorioIncidente, Severidade

def criar_relatorio_remoto(host: str, porta: int, gerado_por: str, ataques: list[Ataque]) -> RelatorioIncidente:
    print("\n CLIENTE ->  Empacotando mensagem de request")
    request = {
        "operacao": "criar_relatorio",
        "parametros": {"gerado_por": gerado_por, "ataques": [ataque.to_dict() for ataque in ataques]},
    }

    with socket.create_connection((host, porta)) as conexao, conexao.makefile("rwb") as fluxo:
        fluxo.write((json.dumps(request) + "\n").encode("utf-8"))
        fluxo.flush()

        resposta = json.loads(fluxo.readline().decode("utf-8"))


    
    print(f" CLIENTE ->  Reply desempacotado recebido do servidor: {resposta}")

    if not resposta["sucesso"]:
        raise RuntimeError(resposta["erro"])
    return RelatorioIncidente.from_dict(resposta["relatorio"])


def main() -> None:
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    porta = int(sys.argv[2]) if len(sys.argv) > 2 else 5051
    gerado_por = sys.argv[3] if len(sys.argv) > 3 else "analista-1"
    ataques = [
        Ataque.novo(
            ip_dst="10.0.0.2",
            ip_source="10.0.0.1",
            incident_type="PORT_SCAN",
            severity=Severidade.ALTA,
            thetime=1234567890.0,
            desc="Varredura detectada (ataque de exemplo)",
        )
    ]
    relatorio = criar_relatorio_remoto(host, porta, gerado_por, ataques)
    print("Relatório recebido:")
    print(json.dumps(relatorio.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


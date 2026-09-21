import json
import socket

from ..modelos.models import Ataque, RelatorioIncidente

def criar_relatorio_remoto(host: str, porta: int, gerado_por: str, ataques: list[Ataque]) -> RelatorioIncidente:
    request = {
        "operacao": "criar_relatorio",
        "parametros": {"gerado_por": gerado_por, "ataques": [ataque.to_dict() for ataque in ataques]},
    }

    with socket.create_connection((host, porta)) as conexao, conexao.makefile("rwb") as fluxo:
        fluxo.write((json.dumps(request) + "\n").encode("utf-8"))
        fluxo.flush()

        resposta = json.loads(fluxo.readline().decode("utf-8"))

    if not resposta["sucesso"]:
        raise RuntimeError(resposta["erro"])
    return RelatorioIncidente.from_dict(resposta["relatorio"])

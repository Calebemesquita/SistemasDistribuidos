from datetime import datetime
import uuid

from ..modelos.models import RelatorioIncidente


class ServicoRelatorios:
    def __init__(self):
        self.relatorios = {}

    def criar_relatorio(self, gerado_por, ataques=None):
        ataques = list(ataques or [])
        relatorio = RelatorioIncidente(
            str(uuid.uuid4()), len(ataques), datetime.now().timestamp(), gerado_por, ataques
        )
        self.relatorios[relatorio.id_relatorio] = relatorio
        return relatorio

    def buscar_por_id(self, id_relatorio):
        return self.relatorios.get(id_relatorio)

    def buscar_por_severidade(self, severidade):
        return [
            ataque
            for relatorio in self.relatorios.values()
            for ataque in relatorio.ataques
            if ataque.severity == severidade
        ]

    def listar_todos(self):
        return list(self.relatorios.values())


class ServicoNotificacao:
    def __init__(self):
        self.inscritos = set()

    def inscrever(self, cliente_id):
        self.inscritos.add(cliente_id)

    def desinscrever(self, cliente_id):
        self.inscritos.discard(cliente_id)

    def montar_alerta(self, tipo, mensagem):
        return {"tipo": tipo, "mensagem": mensagem, "timestamp": datetime.now().timestamp()}

    def total_inscritos(self):
        return len(self.inscritos)

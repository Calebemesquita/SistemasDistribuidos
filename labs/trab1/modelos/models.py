import time
import datetime
import uuid
from enum import Enum
from typing import List, Optional

'''Sistema de Coleta de Vulnerabilidades e Alertas de Rede'''

# Modelo.py
# Aqui devem ficar os dois POJOS


class Severidade(Enum):
    BAIXA = 'BAIXA'
    MEDIA = 'MEDIA'
    ALTA = 'ALTA'
    CRITICA = 'CRITICA'


'''
to_dict() manual
Quando quer controlar os campos retornados

self.__dict__
Quando quer obter os atributos armazenados

dataclasses.asdict()
Quando usa dataclass para representar dados
'''


class Ataque:

    # construtor da classe Ataque
    def __init__(
        self,
        id: str,
        ip_dst: str,
        ip_source: str,
        incident_type: str,
        severity: Severidade | str,
        thetime: float,
        desc: str,
    ):
        self.id = id
        self.ip_dst = ip_dst
        self.ip_source = ip_source
        self.incident_type = incident_type
        self.severity = self._normalizar_severidade(severity)
        self.thetime = thetime
        self.desc = desc




    '''
    @staticmethod
    def _normalizar_severidade(severity: Severidade | str) -> Severidade:
        if isinstance(severity, Severidade):
            return severity

        if isinstance(severity, str):
            return Severidade[severity.upper()]

        raise ValueError(f'Severidade inválida: {severity}')
    '''

    @staticmethod
    def novo(ip_dst, ip_source, incident_type, severity, thetime, desc):
        return Ataque(
            id=str(uuid.uuid4()),
            ip_dst=ip_dst,
            ip_source=ip_source,
            incident_type=incident_type,
            severity=severity,
            thetime=thetime,
            desc=desc,
        )

    ''''
    Pegamos objeto da classe, e transfromamos em um dict python
    Para depois converter em json
    '''
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'ip_origem': self.ip_source,
            'ip_destino': self.ip_dst,
            'tipo_alerta': self.incident_type,
            'severidade': self.severity.value,
            'tempo': self.thetime,
            'desc': self.desc,
        }

    '''
    Pegamos um dict python e transfromamos em objeto Ataque
    '''
    @staticmethod
    def from_dict(d: dict) -> 'Ataque':
        return Ataque(
            id=d['id'],
            ip_dst=d['ip_destino'],
            ip_source=d['ip_origem'],
            incident_type=d['tipo_alerta'],
            severity=d.get('severidade', Severidade.BAIXA),
            thetime=d.get('tempo', time.time()),
            desc=d.get('desc', ''),
        )


'''
    def to_pack(self) -> bytes:

    def un_pack():


    def read_file(self, arquivo_name):
        arquivo = open(arquivo_name, 'r')

        conteudo = arquivo.read()
        print(conteudo)


    def write_file(self, arquivo_name, input_arquivo):
        arquivo = open(arquivo_name, 'w')
        arquivo.write(input_arquivo)
        arquivo.close()
'''









class RelatorioIncidente:
    def __init__( self, id_relatorio: str,num_ataques: str, gerado_data: float, gerado_por: str, ataques: Optional[List[Ataque]] = None):
        self.id_relatorio = id_relatorio
        self.num_ataques = num_ataques
        self.gerado_data = gerado_data
        self.gerado_por = gerado_por
        self.ataques = ataques if ataques is not None else []


    def add_ataque(self, ataque: Ataque) -> None:
        self.ataques.append(ataque)

    def to_dict(self) -> dict:
        return {
            'id_relatorio': self.id_relatorio,
            'num_ataques': self.num_ataques,
            'gerado_data': self.gerado_data,
            'gerado_por': self.gerado_por,
            'ataques': [a.to_dict() for a in self.ataques],
        }

    @staticmethod
    def from_dict(d: dict) -> 'RelatorioIncidente':
        relatorio = RelatorioIncidente(
            id_relatorio=d['id_relatorio'],
            num_ataques=d['num_ataques'],
            gerado_data=d['gerado_data'],
            gerado_por=d['gerado_por'],
        )

        relatorio.ataques = [Ataque.from_dict(a) for a in d.get('ataques', [])]
        return relatorio





class ServicoRelatorios:
 
    def __init__(self):
        self._relatorios: dict = {}

 
    def criar_relatorio(self, gerado_por: str, ataques: Optional[List[Ataque]] = None) -> RelatorioIncidente:
        relatorio = RelatorioIncidente(
            id_relatorio=str(uuid.uuid4()),
            gerado_por=gerado_por,
            gerado_data=datetime.now().timestamp(),
            ataques=ataques or [],
        )
        self._relatorios[relatorio.id_relatorio] = relatorio
        return relatorio
    
 
    def buscar_por_id(self, id_relatorio: str) -> Optional[RelatorioIncidente]:
        return self._relatorios.get(id_relatorio)
 
    def buscar_por_severidade(self, severidade: Severidade) -> List[Ataque]:
        encontrados = []
        for relatorio in self._relatorios.values():
            encontrados.extend(
                a for a in relatorio.ataques if a.severidade == severidade
            )
        return encontrados
 
    def buscar_por_periodo(self, inicio: float, fim: float) -> List[RelatorioIncidente]:
        return [r for r in self._relatorios.values() if inicio <= r.gerado_data <= fim]
 
    def listar_todos(self) -> List[RelatorioIncidente]:
        return list(self._relatorios.values())
 


 
class ServicoNotificacao:
    def __init__(self):
        self._inscritos: set = set()
 
    def inscrever(self, cliente_id: str) -> None:
        self._inscritos.add(cliente_id)
 
    def desinscrever(self, cliente_id: str) -> None:
        self._inscritos.discard(cliente_id)
 
    def montar_alerta(self, tipo: str, mensagem: str) -> dict:
        return {
            "tipo": tipo,
            "mensagem": mensagem,
            "timestamp": datetime.now().timestamp(),
        }
 
    def total_inscritos(self) -> int:
        return len(self._inscritos)
 

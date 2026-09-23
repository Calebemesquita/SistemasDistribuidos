import time
from datetime import datetime
import uuid
from enum import Enum
from typing import List, Optional

'''Sistema de Coleta de Vulnerabilidades e Alertas de Rede'''
'''
Duas POJO duas serviço
Classes:
Severidade: Enum para os niveis de severidade
Ataque: Representa um ataque detectado
RelatorioIncidente: Um relatorio de inciente que contem ataques
ServicoRelatorios: Servico para gerenciar relatorios
ServicoNotificacao: Servico para gerenciar notificacoes
'''


class Severidade(Enum):
    BAIXA = 'BAIXA'
    MEDIA = 'MEDIA'
    ALTA = 'ALTA'
    CRITICA = 'CRITICA'


class Ataque:

    # construtor da classe Ataque
    def __init__( self, id: str, ip_dst: str, ip_source: str, incident_type: str, severity: Severidade | str, thetime: float, desc: str):
        self.id = id
        self.ip_dst = ip_dst
        self.ip_source = ip_source
        self.incident_type = incident_type
        self.severity = self._normalizar_severidade(severity)
        self.thetime = thetime
        self.desc = desc

    @staticmethod
    def novo(ip_dst, ip_source, incident_type, severity, thetime, desc):
        return Ataque(id=str(uuid.uuid4()), ip_dst=ip_dst, ip_source=ip_source, incident_type=incident_type, severity=severity, thetime=thetime, desc=desc)

    @staticmethod
    def _normalizar_severidade(severity: Severidade | str) -> Severidade:
        if isinstance(severity, Severidade):
            return severity
        if isinstance(severity, str):
            return Severidade[severity.upper()]
        raise ValueError(f"Severidade inválida: {severity}")

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
        return Ataque( id=d['id'], ip_dst=d['ip_destino'], ip_source=d['ip_origem'], incident_type=d['tipo_alerta'], severity=d.get('severidade', Severidade.BAIXA), thetime=d.get('tempo', time.time()), desc=d.get('desc', ''))


    def __eq__(self, other) -> bool:
        if not isinstance(other, Ataque):
            return False
        return (self.id == other.id and self.ip_source == other.ip_source and self.ip_dst == other.ip_dst and self.incident_type == other.incident_type)





class RelatorioIncidente:
    def __init__( self, id_relatorio: str, num_ataques: int, gerado_data: float, gerado_por: str, ataques: Optional[List[Ataque]] = None):
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
        relatorio = RelatorioIncidente(id_relatorio=d['id_relatorio'], num_ataques=d['num_ataques'], gerado_data=d['gerado_data'], gerado_por=d['gerado_por'])
        relatorio.ataques = [Ataque.from_dict(a) for a in d.get('ataques', [])]
        return relatorio

from datetime import datetime
import uuid
import socket

class Incidente:
    def __init__(self, id: int, titulo: str, descricao: str, severidade: str, status: str, data_hora: datetime, reportado_por: str, local: str):
        self.id = id
        self.titulo = titulo
        self.descricao= descricao
        self.severidade = severidade
        self.status = status
        self.reportado_por = reportado_por
        self.data_hora = data_hora if data_hora else datetime.now()
        self.local = local


    ''' METODOS GETs SETs'''

    def getId(self) -> int:
        return self.id

    def setId(self, id: int) -> None:
        self.id = id

    def getTitulo(self) -> str:
        return self.titulo

    def setTitulo(self, titulo: str) -> None:
        self.titulo = titulo

    def getDesc(self) -> str:
        return self.desc

    def setDesc(self, descricao: str) -> None:
        self.descricao = descricao

    def getSeveridade(self) -> str:
        return self.severidade

    def setSeveridade(self, severidade: str) -> None:
        self.severidade = severidade

    def getStatus(self) -> str:
        return self.status

    def setStatus(self, status: str) -> None:
        self.status = status

    def getDataHora(self) -> datetime:
        return self.data_hora

    def setDataHora(self, data_hora: datetime) -> None:
        self.data_hora = data_hora

    def getReportadoPor(self) -> str:
        return self.reportado_por

    def setReportadoPor(self, reportado_por: str) -> None:
        self.reportado_por = reportado_por

    def getLocal(self) -> str:
        return self.local

    def setLocal(self, local: str) -> None:
        self.local = local
    




    ''' Outros methods'''

    @staticmethod
    def to_dict(self) -> dict:
        return {
            'id': self.getId(),
            'titulo': self.getTitulo(),
            'descricao': self.getDesc(),
            'severidade': self.getSeveridade(),
            'status': self.getStatus(),
            'data_hora': self.getDataHora().isoformat(),
            'reportado_por': self.getReportadoPor(),
            'local': self.getLocal()
        }
    
    def from_dict(d: dict) -> "Incidente":
        return Incidente(
            id=d['id'],
            titulo=d['titulo'],
            descricao=d['descricao'],
            severidade=d['severidade'],
            status=d['status'],
            data_hora=d['data_hora'],
            reportado_por=d['reportado_por'],
            local=d['local']
            )

    def __str__(self) -> str:
        return f"Incidente(id={self.id}, titulo={self.titulo}, severidade={self.severidade}, status={self.status})"
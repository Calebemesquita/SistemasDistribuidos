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
        return self.descricao

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
    # Não preciso de um Incidente para transformar dict -> ObjIncidente
    @staticmethod    
    def from_dict(d: dict) -> "Incidente":
        return Incidente(
            id=d['id'],
            titulo=d['titulo'],
            descricao=d['descricao'],
            severidade=d['severidade'],
            status=d['status'],
            data_hora= datetime.fromisoformat(d['data_hora']),
            reportado_por=d['reportado_por'],
            local=d['local']
            )

    def __str__(self) -> str:
        return f"Incidente(id={self.id}, titulo={self.titulo}, severidade={self.severidade}, status={self.status})"






class RelatorioIncidente:
    def __init__(self, id: int, incidente_id: int, analista: str, conclusao: str, acoes: str, data_fechamento: datetime, anexos: list[str]):
        self.id = id
        self.incidente_id = incidente_id
        self.conclusao = conclusao
        self.analista = analista
        self.acoes = acoes
        self.data_fechamento = data_fechamento if data_fechamento else datatime.now()
        self.anexos = anexos if anexos else []

    
    def getId(self) -> int:
        return self.id

    def getIncidente_id(self) -> int:
        return self.incidente_id

    def getAnalista(self) -> str:
        return self.analista

    def getConclusao(self) -> str:
        return self.conclusao

    def getAcoes(self) -> str:
        return self.acoes

    def getData_fechamento(self) -> datetime:
        return self.data_fechamento

    def getAnexos(self) -> list[str]:
        return self.anexos

    # SETTERS

    def setId(self, id: int) -> None:
        self.id = id

    def setIncidente_id(self, incidente_id: int) -> None:
        self.incidente_id = incidente_id

    def setAnalista(self, analista: str) -> None:
        self.analista = analista

    def setConclusao(self, conclusao: str) -> None:
        self.conclusao = conclusao

    def setAcoes(self, acoes: str) -> None:
        self.acoes = acoes

    def setData_fechamento(self, data_fechamento: datetime) -> None:
        self.data_fechamento = data_fechamento

    def setAnexos(self, anexos: list[str]) -> None:
        self.anexos = anexos


    # self, id: int, incidente_id: int, analista: str, conclusao: str, acoes: str, data_fechamento: datetime, anexos: list[str]
    def to_dict(self) -> dict:
        return {
            'id': self.getId(),
            'incidente_id': self.getIncidente_id(),
            'analista': self.getAnalista(),
            'conclusao': self.getConclusao(),
            'acoes': self.getAcoes(),
            'data_fechamento': self.getData_fechamento(),
            'anexos': self.getAnexos(),
        }

    @staticmethod
    def from_dict(d: dict) -> "RelatorioIncidente":
        return RelatorioIncidente(
            id=d['id'],
            incidente_id=d['incidente_id'],
            analista=d['analista'],
            conclusao=d['conclusao'],
            acoes=d['acoes'],
            data_fechamento=datetime.fromisoformat(d['data_fechamento']),
            anexos=d['anexos']
        )

    def __str__(self) -> str:
        return (f"RelatorioIncidente(id={self.id}, "
            f"incidente_id={self.incidente_id}, "
            f"analista='{self.analista}', "
            f"data_fechamento={self.data_fechamento})")
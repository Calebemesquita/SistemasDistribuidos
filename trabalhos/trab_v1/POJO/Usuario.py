from .registro import Registro
#from enum import Enum


class Usuario(Registro):
    def __init__(self, id: int, nome: str, funcao: str, ativo: bool):
        super().__init__(id)
        self.nome = nome
        self.funcao = funcao
        self.ativo = ativo
    

    def getId(self): return self.id
    def getNome(self): return self.nome
    def getFuncao(self): return self.funcao
    def getAtivo(self): return self.ativo

    def setNome(self, nome): self.nome = nome
    def setFuncao(self, funcao): self.funcao = funcao
    def setAtico(self, ativo: bool): self.ativo = ativo 

    def to_dict(self) -> dict:
        return {
            "id": self.getId(),
            "nome": self.getNome(),
            "funcao": self.getFuncao(),
            "ativo": self.getAtivo()
        }

    @staticmethod
    def from_dict(d) -> "Usuario":
        return Usuario(d["id"], d["nome"], d["funcao"], d["ativo"])


"""
TESTES - CALEBE
u = Usuario(10, "Calebe", "Estagias", True)
d = Usuario(10, "Denilson", "Senior", False)

print(u.getId())

print(u.to_dict())

novo_usuario = Usuario.from_dict(d.to_dict())

print(novo_usuario.to_dict())
"""
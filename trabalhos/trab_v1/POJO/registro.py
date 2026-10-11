from abc import ABC, abstractmethod


# Classe abstrata ABC para se comportar como interface e 
# Atender ao nosso trabalho so que em python
class Serializavel(ABC):
    @abstractmethod
    def to_dict(self) -> dict: ...
        # raise NotImplementedError é mais comun metodos que opcialmente devem ser sobrescritos
        # como estamos simulando a interface vamos usar ... pois eles devem ser obrigatoriamente sobrescritoss
        #raise NotImplementedError

    @staticmethod
    @abstractmethod
    def from_dict(d: dict) -> "Serializavel": ...
        #raise NotImplementedError


# Não implementa os metodos abstratos então não pode ser isntanciado
class Registro(Serializavel):
    def __init__(self, id: int):
        self.id = id

    def getId(self) -> int:
        return self.id

    def setId(self, id: int) -> None:
        self.id = id

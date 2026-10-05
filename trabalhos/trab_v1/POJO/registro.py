from abc import ABC, abstractmethod


class Serializavel(ABC):

    @abstractmethod
    def to_dict(self) -> dict:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def from_dict(d: dict) -> "Serializavel":
        raise NotImplementedError


class Registro(Serializavel):

    def __init__(self, id: int):
        self.id = id

    def getId(self) -> int:
        return self.id

    def setId(self, id: int) -> None:
        self.id = id

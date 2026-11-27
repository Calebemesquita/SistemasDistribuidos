"""Entidades do domínio com herança e agregação explícitas."""
from dataclasses import dataclass, field, asdict
from contextlib import contextmanager
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Iterator, Protocol, runtime_checkable


@runtime_checkable
class Serializavel(Protocol):
    """Contrato de domínio para objetos que podem virar JSON/dict."""

    def para_dict(self) -> dict[str, Any]: ...


def serializar(objeto: Serializavel) -> dict[str, Any]:
    """Serializa um objeto de domínio pelo contrato Serializavel."""
    if not isinstance(objeto, Serializavel):
        raise TypeError(f"{type(objeto).__name__} não implementa Serializavel")
    return objeto.para_dict()


@dataclass
class Usuario:
    identificador: str
    nome: str

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Leitor(Usuario):
    emprestimos: list[str] = field(default_factory=list)


@dataclass
class Bibliotecario(Usuario):
    matricula_funcional: str = ""


@dataclass
class Livro:
    isbn: str
    titulo: str
    autor: str
    disponivel: bool = True

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Notificacao:
    sequencia: int
    mensagem: str
    data_hora: str
    tipo: str = "NOTIFICACAO"

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Alerta(Notificacao):
    tipo: str = "ALERTA"


@dataclass
class Atualizacao(Notificacao):
    tipo: str = "ATUALIZACAO"


@dataclass
class Catalogo:
    livros: dict[str, Livro] = field(default_factory=dict)

    def para_dict(self) -> dict[str, Any]:
        return {isbn: serializar(livro) for isbn, livro in self.livros.items()}


@dataclass
class HistoricoEmprestimos:
    registros: list[dict] = field(default_factory=list)
    proximo_id: int = 1

    def para_dict(self) -> dict[str, Any]:
        return {
            "registros": [dict(registro) for registro in self.registros],
            "proximo_id": self.proximo_id,
        }


@dataclass
class Inscricoes:
    clientes: dict[str, str] = field(default_factory=dict)

    def para_dict(self) -> dict[str, Any]:
        return dict(self.clientes)


class CanalNotificacoes:
    """Agrega Inscricoes e Notificacoes. Guarda histórico consultável por cursor."""
    def __init__(self):
        self.inscricoes = Inscricoes()  # tem-um (agregação)
        self.notificacoes: list[Notificacao] = []  # tem-muitos (agregação)
        self._lock = RLock()

    def inscrever(self, cliente_id: str, nome: str) -> dict:
        if not cliente_id.strip() or not nome.strip():
            raise ValueError("Cliente e nome devem ser preenchidos")
        with self._lock:
            self.inscricoes.clientes[cliente_id] = nome
            return {"cliente_id": cliente_id, "ativo": True}

    def cancelar_inscricao(self, cliente_id: str) -> dict:
        with self._lock:
            existia = self.inscricoes.clientes.pop(cliente_id, None) is not None
            return {"cliente_id": cliente_id, "removido": existia}

    def cancelar_ultima(self, sequencia: int) -> None:
        """Remove o último evento caso uma publicação externa falhe."""
        with self._lock:
            if not self.notificacoes or self.notificacoes[-1].sequencia != sequencia:
                raise ValueError("Somente a última notificação pode ser revertida")
            self.notificacoes.pop()

    def para_dict(self) -> dict[str, Any]:
        with self._lock:
            return {
                "inscricoes": serializar(self.inscricoes),
                "notificacoes": [serializar(evento) for evento in self.notificacoes],
            }

    def publicar(self, mensagem: str, tipo: str = "NOTIFICACAO") -> dict:
        if not mensagem.strip():
            raise ValueError("Mensagem não pode estar vazia")
        with self._lock:
            seq = len(self.notificacoes) + 1
            now = datetime.now(timezone.utc).isoformat()
            classes = {"NOTIFICACAO": Notificacao, "ALERTA": Alerta, "ATUALIZACAO": Atualizacao}
            if tipo not in classes:
                raise ValueError("Tipo inválido")
            registro = classes[tipo](seq, mensagem, now)
            self.notificacoes.append(registro)
            return serializar(registro)

    def consultar(self, cliente_id: str, apos: int = 0) -> dict:
        with self._lock:
            if cliente_id not in self.inscricoes.clientes:
                raise ValueError("Cliente não está inscrito")
            eventos = [serializar(n) for n in self.notificacoes if n.sequencia > apos]
            return {"eventos": eventos, "ultimo": self.notificacoes[-1].sequencia if self.notificacoes else 0}


class Biblioteca:
    """Agrega Catalogo e HistoricoEmprestimos."""
    def __init__(self, canal: CanalNotificacoes):
        self.catalogo = Catalogo()  # tem-um (agregação)
        self.historico = HistoricoEmprestimos()  # tem-um (agregação)
        self.canal = canal
        self.usuarios: dict[str, Usuario] = {}
        self._lock = RLock()

    @contextmanager
    def transacao(self) -> Iterator["Biblioteca"]:
        """Sincroniza uma operação composta por regra de domínio e efeito externo."""
        with self._lock:
            yield self

    def registrar_usuario(self, usuario: Usuario) -> Usuario:
        with self._lock:
            atual = self.usuarios.get(usuario.identificador)
            if atual is not None and type(atual) is not type(usuario):
                raise ValueError("Identificador já registrado com outro papel")
            if atual is not None:
                atual.nome = usuario.nome
                if isinstance(atual, Bibliotecario):
                    atual.matricula_funcional = usuario.matricula_funcional
                return atual
            self.usuarios[usuario.identificador] = usuario
            return usuario

    def listar_usuarios(self) -> list[Usuario]:
        with self._lock:
            return list(self.usuarios.values())

    def para_dict(self) -> dict[str, Any]:
        with self._lock:
            return {
                "catalogo": serializar(self.catalogo),
                "historico": serializar(self.historico),
                "canal": serializar(self.canal),
                "usuarios": {
                    identificador: serializar(usuario)
                    for identificador, usuario in self.usuarios.items()
                },
            }

    def cadastrar_livro(
        self,
        livro: dict,
        bibliotecario: Bibliotecario | None = None,
    ) -> dict:
        novo = Livro(**livro)
        if not novo.isbn.strip() or not novo.titulo.strip():
            raise ValueError("ISBN e título são obrigatórios")
        with self._lock:
            if novo.isbn in self.catalogo.livros:
                raise ValueError("ISBN já cadastrado")
            if bibliotecario is not None:
                self.registrar_usuario(bibliotecario)
            self.catalogo.livros[novo.isbn] = novo
            self.canal.publicar(f"Novo livro: {novo.titulo}", "ATUALIZACAO")
            return serializar(novo)

    def listar_livros(self) -> list[dict]:
        with self._lock:
            return [serializar(livro) for livro in self.catalogo.livros.values()]

    def remover_livro(self, isbn: str) -> None:
        with self._lock:
            livro = self.catalogo.livros.get(isbn)
            if livro is None:
                raise ValueError("Livro não encontrado")
            if not livro.disponivel:
                raise ValueError("Livro está emprestado")
            del self.catalogo.livros[isbn]

    def emprestar_livro(
        self,
        isbn: str,
        leitor_id: str,
        leitor: Leitor | None = None,
    ) -> dict:
        with self._lock:
            livro = self.catalogo.livros.get(isbn)
            if livro is None:
                raise ValueError("Livro não encontrado")
            if not livro.disponivel:
                raise ValueError("Livro indisponível")
            if not leitor_id.strip():
                raise ValueError("Identificador do leitor obrigatório")
            usuario = self.usuarios.get(leitor_id)
            leitor_novo = usuario is None
            if usuario is None:
                usuario = leitor or Leitor(leitor_id, leitor_id)
                if usuario.identificador != leitor_id:
                    raise ValueError("Identificador do leitor não corresponde")
                self.usuarios[leitor_id] = usuario
            if not isinstance(usuario, Leitor):
                raise ValueError("O usuário não possui papel de leitor")
            livro.disponivel = False
            usuario.emprestimos.append(isbn)
            evento = {
                "id": self.historico.proximo_id,
                "isbn": isbn,
                "leitor_id": leitor_id,
                "leitor_novo": leitor_novo,
                "returned": False,
            }
            self.historico.proximo_id += 1
            self.historico.registros.append(evento)
            self.canal.publicar(
                f"{usuario.nome} solicitou o livro #{isbn}: {livro.titulo}",
                "ALERTA",
            )
            return dict(evento)

    def listar_emprestimos(self) -> list[dict]:
        with self._lock:
            return [dict(registro) for registro in self.historico.registros]

    def devolver_livro(self, isbn: str, emprestimo_id: int | None = None) -> dict:
        with self._lock:
            livro = self.catalogo.livros.get(isbn)
            if livro is None:
                raise ValueError("Livro não encontrado")
            if livro.disponivel:
                raise ValueError("Livro não estava emprestado")

            registro = next(
                (
                    item
                    for item in reversed(self.historico.registros)
                    if item["isbn"] == isbn
                    and not item["returned"]
                    and (emprestimo_id is None or item["id"] == emprestimo_id)
                ),
                None,
            )
            if registro is None:
                raise ValueError("Empréstimo não encontrado")

            livro.disponivel = True
            registro["returned"] = True
            leitor = self.usuarios.get(registro["leitor_id"])
            if isinstance(leitor, Leitor) and isbn in leitor.emprestimos:
                leitor.emprestimos.remove(isbn)
            nome_leitor = registro["leitor_id"]
            leitor = self.usuarios.get(nome_leitor)
            nome = leitor.nome if isinstance(leitor, Leitor) else nome_leitor
            self.canal.publicar(
                f"{nome} devolveu o livro #{isbn}: {livro.titulo}",
                "ATUALIZACAO",
            )
            return serializar(livro)

    def devolver_emprestimo(self, emprestimo_id: int) -> dict:
        with self._lock:
            registro = next(
                (item for item in self.historico.registros if item["id"] == emprestimo_id),
                None,
            )
            if registro is None:
                raise ValueError("Empréstimo não encontrado")
            if registro["returned"]:
                raise ValueError("Empréstimo já devolvido")

            self.devolver_livro(registro["isbn"], emprestimo_id)
            return dict(registro)

    def reverter_emprestimo(self, emprestimo_id: int) -> None:
        """Reverte empréstimo recém-criado se RabbitMQ não aceitar o evento."""
        with self._lock:
            registro = next(
                (item for item in self.historico.registros if item["id"] == emprestimo_id),
                None,
            )
            if registro is None:
                raise ValueError("Empréstimo não encontrado")
            if registro["returned"]:
                raise ValueError("Empréstimo já devolvido")
            livro = self.catalogo.livros[registro["isbn"]]
            livro.disponivel = True
            leitor = self.usuarios.get(registro["leitor_id"])
            if isinstance(leitor, Leitor) and registro["isbn"] in leitor.emprestimos:
                leitor.emprestimos.remove(registro["isbn"])
                if registro.get("leitor_novo") and not leitor.emprestimos:
                    del self.usuarios[registro["leitor_id"]]
            self.historico.registros.remove(registro)
            if self.historico.proximo_id == emprestimo_id + 1:
                self.historico.proximo_id = emprestimo_id

    def reverter_devolucao(self, emprestimo_id: int) -> None:
        with self._lock:
            registro = next(
                (item for item in self.historico.registros if item["id"] == emprestimo_id),
                None,
            )
            if registro is None or not registro["returned"]:
                raise ValueError("Devolução não encontrada")
            livro = self.catalogo.livros[registro["isbn"]]
            livro.disponivel = False
            registro["returned"] = False
            leitor = self.usuarios.get(registro["leitor_id"])
            if isinstance(leitor, Leitor):
                leitor.emprestimos.append(registro["isbn"])

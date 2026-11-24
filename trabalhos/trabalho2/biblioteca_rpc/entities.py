"""Entidades do domínio com herança e agregação explícitas."""
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from threading import RLock


@dataclass
class Usuario:
    identificador: str
    nome: str


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


@dataclass
class Notificacao:
    sequencia: int
    mensagem: str
    data_hora: str
    tipo: str = "NOTIFICACAO"

    def para_dict(self):
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


@dataclass
class HistoricoEmprestimos:
    registros: list[dict] = field(default_factory=list)


@dataclass
class Inscricoes:
    clientes: dict[str, str] = field(default_factory=dict)


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
            return registro.para_dict()

    def consultar(self, cliente_id: str, apos: int = 0) -> dict:
        with self._lock:
            if cliente_id not in self.inscricoes.clientes:
                raise ValueError("Cliente não está inscrito")
            eventos = [n.para_dict() for n in self.notificacoes if n.sequencia > apos]
            return {"eventos": eventos, "ultimo": self.notificacoes[-1].sequencia if self.notificacoes else 0}


class Biblioteca:
    """Agrega Catalogo e HistoricoEmprestimos."""
    def __init__(self, canal: CanalNotificacoes):
        self.catalogo = Catalogo()  # tem-um (agregação)
        self.historico = HistoricoEmprestimos()  # tem-um (agregação)
        self.canal = canal
        self._lock = RLock()

    def cadastrar_livro(self, livro: dict) -> dict:
        novo = Livro(**livro)
        if not novo.isbn.strip() or not novo.titulo.strip():
            raise ValueError("ISBN e título são obrigatórios")
        with self._lock:
            if novo.isbn in self.catalogo.livros:
                raise ValueError("ISBN já cadastrado")
            self.catalogo.livros[novo.isbn] = novo
            self.canal.publicar(f"Novo livro: {novo.titulo}", "ATUALIZACAO")
            return asdict(novo)

    def listar_livros(self) -> list[dict]:
        with self._lock:
            return [asdict(l) for l in self.catalogo.livros.values()]

    def emprestar_livro(self, isbn: str, leitor_id: str) -> dict:
        with self._lock:
            livro = self.catalogo.livros.get(isbn)
            if livro is None:
                raise ValueError("Livro não encontrado")
            if not livro.disponivel:
                raise ValueError("Livro indisponível")
            if not leitor_id.strip():
                raise ValueError("Identificador do leitor obrigatório")
            livro.disponivel = False
            evento = {"isbn": isbn, "leitor_id": leitor_id}
            self.historico.registros.append(evento)
            self.canal.publicar(f"Livro emprestado: {livro.titulo}", "ALERTA")
            return evento

    def devolver_livro(self, isbn: str) -> dict:
        with self._lock:
            livro = self.catalogo.livros.get(isbn)
            if livro is None:
                raise ValueError("Livro não encontrado")
            if livro.disponivel:
                raise ValueError("Livro não estava emprestado")
            livro.disponivel = True
            self.canal.publicar(f"Livro disponível: {livro.titulo}", "ATUALIZACAO")
            return asdict(livro)

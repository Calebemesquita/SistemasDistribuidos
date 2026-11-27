# Arquitetura, classes e orientação a objetos

O Trabalho 4 usa as classes de domínio do Trabalho 2 pela API HTTP. O pacote do
Trabalho 3 fornece o formato de eventos que o adaptador publica no RabbitMQ.
Os diagramas abaixo ficam no Markdown e podem ser visualizados pelo GitHub ou
por qualquer editor com suporte a Mermaid.

## Visão distribuída

```mermaid
flowchart LR
    CLI["CLI Python em outra máquina"] -->|HTTP + JSON| API["FastAPI :8000"]
    Java["Cliente Java"] -->|HTTP + JSON| API
    Node["Cliente Node.js"] -->|HTTP + JSON| API

    subgraph T4["Processo servidor — Trabalho 4"]
        API --> Books["Router /books"]
        API --> Loans["Router /loans"]
        API --> Notifications["Router /notifications"]
        API --> Users["Router /users"]
        Books --> BookService["BookService adaptador"]
        Loans --> LoanService["LoanService adaptador"]
        Notifications --> NotificationService["NotificationService adaptador"]
        Users --> Biblioteca
        BookService --> Biblioteca
        LoanService --> Biblioteca
        NotificationService --> Canal
    end

    subgraph T2["Domínio compartilhado — Trabalho 2"]
        Biblioteca["Biblioteca"] --> Catalogo["Catalogo"]
        Biblioteca --> Historico["HistoricoEmprestimos"]
        Biblioteca --> Canal["CanalNotificacoes"]
        Catalogo --> Livro["Livro"]
        Historico --> Emprestimos["registros de empréstimo"]
        Canal --> Inscricoes["Inscricoes"]
        Canal --> Notificacao["Notificacao / Alerta / Atualizacao"]
        Usuario["Usuario"] --> Leitor["Leitor"]
        Usuario --> Bibliotecario["Bibliotecario"]
    end

    Biblioteca --> Usuario
    CLI -->|inscrever e consultar cursor| API
    NotificationService -->|adaptar JSON| Protocol["Notification / NotificationType — T3"]
    Protocol -->|AMQP publish| Rabbit["RabbitMQ fanout"]
    Node -->|AMQP consume opcional| Rabbit
    Listener["Listener Python"] -->|AMQP consume opcional| Rabbit
```

A API e o CLI conversam por HTTP, inclusive quando estão em computadores
diferentes. O polling do CLI consulta o canal do processo servidor pelo cursor.
RabbitMQ é uma segunda rota de distribuição: clientes Node.js e o listener
Python podem consumir eventos diretamente.

## Diagrama de classes

```mermaid
classDiagram
    direction LR

    class Serializavel {
        <<interface / Protocol T2>>
        +para_dict() dict
    }
    class Usuario {
        <<dataclass T2>>
        +identificador: str
        +nome: str
        +para_dict() dict
    }
    class Leitor {
        <<dataclass T2>>
        +emprestimos: list[str]
    }
    class Bibliotecario {
        <<dataclass T2>>
        +matricula_funcional: str
    }
    class Livro {
        <<dataclass T2>>
        +isbn: str
        +titulo: str
        +autor: str
        +disponivel: bool
        +para_dict() dict
    }
    class Notificacao {
        <<dataclass T2>>
        +sequencia: int
        +mensagem: str
        +data_hora: str
        +tipo: str
    }
    class Alerta {
        <<dataclass T2>>
        +tipo: ALERTA
    }
    class Atualizacao {
        <<dataclass T2>>
        +tipo: ATUALIZACAO
    }
    class Catalogo {
        <<aggregate T2>>
        +livros: dict[str, Livro]
        +para_dict() dict
    }
    class HistoricoEmprestimos {
        <<aggregate T2>>
        +registros: list[dict]
        +proximo_id: int
    }
    class Inscricoes {
        <<aggregate T2>>
        +clientes: dict[str, str]
    }
    class CanalNotificacoes {
        <<aggregate T2>>
        +inscricoes: Inscricoes
        +notificacoes: list[Notificacao]
        +inscrever(id, nome)
        +publicar(mensagem, tipo)
        +consultar(id, cursor)
    }
    class Biblioteca {
        <<aggregate T2>>
        +catalogo: Catalogo
        +historico: HistoricoEmprestimos
        +usuarios: dict[str, Usuario]
        +cadastrar_livro(livro, bibliotecario)
        +emprestar_livro(isbn, leitor_id)
        +devolver_emprestimo(id)
    }
    class BookService {
        <<HTTP adapter T4>>
        +library: Biblioteca
        +list_books()
        +add_book(titulo, autor, bibliotecario)
    }
    class LoanService {
        <<HTTP adapter T4>>
        +library: Biblioteca
        +create_loan(book_id, username)
        +return_loan(id)
        +rollback_created_loan(loan)
    }
    class NotificationService {
        <<adapter T4 to T3>>
        +library: Biblioteca
        +publish_latest()
        +subscribe(id, nome)
        +poll(id, cursor)
    }
    class ProtocolNotification {
        <<dataclass T3>>
        +type: NotificationType
        +content: str
        +timestamp: float
        +to_bytes() bytes
    }
    class NotificationType {
        <<enum T3>>
        ALERT
        NOTIFICATION
        UPDATE
    }
    class RabbitMQ {
        <<external service>>
        fanout exchange
        subscriber queues
    }

    Usuario <|-- Leitor
    Usuario <|-- Bibliotecario
    Notificacao <|-- Alerta
    Notificacao <|-- Atualizacao
    Serializavel <|.. Usuario
    Serializavel <|.. Livro
    Serializavel <|.. Notificacao
    Serializavel <|.. Catalogo
    Serializavel <|.. HistoricoEmprestimos
    Serializavel <|.. Inscricoes
    Serializavel <|.. CanalNotificacoes
    Serializavel <|.. Biblioteca
    Biblioteca o-- Catalogo : agrega
    Biblioteca o-- HistoricoEmprestimos : agrega
    Biblioteca --> CanalNotificacoes : usa
    Biblioteca --> Usuario : registra
    Catalogo o-- Livro : mantém
    CanalNotificacoes o-- Inscricoes : agrega
    CanalNotificacoes o-- Notificacao : histórico
    BookService --> Biblioteca : adapta HTTP
    LoanService --> Biblioteca : adapta HTTP
    NotificationService --> Biblioteca : consulta canal
    NotificationService ..> ProtocolNotification : converte evento
    ProtocolNotification --> NotificationType : usa
    ProtocolNotification --> RabbitMQ : publicado por AMQP
```

## Fluxo de empréstimo

```mermaid
sequenceDiagram
    participant C as Cliente remoto
    participant R as Router HTTP
    participant S as LoanService adaptador
    participant B as Biblioteca T2
    participant N as CanalNotificacoes T2
    participant A as NotificationService
    participant Q as RabbitMQ

    C->>R: POST /loans/ {book_id, username}
    R->>S: create_loan(...)
    S->>B: emprestar_livro(..., Leitor)
    B->>B: atualiza Livro, Leitor e HistoricoEmprestimos
    B->>N: publicar(..., ALERTA)
    S-->>R: empréstimo criado
    R->>A: publicar evento do canal
    A->>Q: Notification JSON (AMQP)
    R-->>C: HTTP 201 + LoanResponse
    C->>R: GET /notifications/subscriptions/ana?after=0
    R->>N: consultar(ana, cursor)
    N-->>R: eventos e cursor atual
    R-->>C: HTTP 200 + eventos
```

## Onde as classes entram

- **Herança:** `Leitor` e `Bibliotecario` especializam `Usuario`. `Alerta` e
  `Atualizacao` especializam `Notificacao`; a operação de domínio escolhe o
  subtipo e o adaptador preserva seu tipo ao converter o evento.
- **Agregação:** `Biblioteca` mantém `Catalogo` e `HistoricoEmprestimos`.
  `CanalNotificacoes` mantém `Inscricoes` e o histórico consultável de eventos.
- **Polimorfismo/serialização:** `Serializavel` é um `Protocol` do Python;
  `serializar()` aceita qualquer objeto que implemente `para_dict()`. Serviços
  e rotas chamam esse contrato para produzir dados JSON.
- **Estado compartilhado:** `get_library()` cria uma instância única. Os
  adaptadores de livro, empréstimo, notificação e usuário recebem esse mesmo
  `Biblioteca` por injeção de dependência; o empréstimo atualiza o livro que
  `/books/` lista.
- **Adaptação incremental:** os DTOs HTTP mapeiam `isbn/titulo/disponivel` para
  `id/title/available`. O adaptador de notificações converte `Notificacao` do
  Trabalho 2 para `Notification`/`NotificationType` do Trabalho 3 e chama o
  publicador RabbitMQ.

## Executar e validar

Inicie o servidor com `uv run uvicorn api.main:app --host 0.0.0.0 --port 8000`.
Em outro computador, conecte o [CLI Python](../cliente_cli/README.md) com
`python3 client.py --url http://IP_DO_SERVIDOR:8000 --username ana`; menu 9
inscreve e menu 10 consulta eventos. Os testes automatizados dos três projetos
estão descritos no [README do Trabalho 4](../README.md).

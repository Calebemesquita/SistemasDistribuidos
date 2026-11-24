# Trabalho 3 — Biblioteca

Os comandos de API, notificações e testes devem ser executados a partir da raiz do projeto. Na raiz do repositório, entre nela com:

```sh
cd trabalhos/trabalho3
```

## Organização

- `api/`: aplicação FastAPI, modelos, rotas e serviços.
- `clients/client_a/`: cliente Java para listar livros e solicitar empréstimos.
- `clients/client_b/`: cliente Node.js para usar a API e receber notificações.
- `notifications/`: publicação RabbitMQ pela API e listener de terminal.
- `protocol/`: formato compartilhado das mensagens de notificação.
- `legacy/`: cliente e servidor TCP antigos, mantidos como referência.
- `tests/`: testes automatizados.

## Pré-requisitos

- Python 3.13 ou mais recente e [uv](https://docs.astral.sh/uv/) para a API e o
  listener Python.
- Node.js 18 ou mais recente e npm para o cliente Node.js.
- JDK 11 ou mais recente para compilar o cliente Java.
- RabbitMQ acessível em `127.0.0.1:5672` para criar empréstimos e receber
  notificações. O projeto não inicia o broker automaticamente.

## Executar a API

Na raiz de `trabalho3/`, instale as dependências e inicie a API:

```sh
uv sync
uv run uvicorn api.main:app --reload
```

Abra `http://127.0.0.1:8000/docs` para a documentação interativa. A API
disponibiliza:

- `GET /books/`: lista os livros e informa se estão disponíveis.
- `GET /loans/`: lista os empréstimos do processo atual.
- `POST /loans/`: cria um empréstimo. Exemplo de corpo JSON:
  `{"book_id": 1, "username": "ana"}`.

O POST responde `201` quando o empréstimo é criado, `400` quando o livro não
existe ou já está emprestado e `503` quando o RabbitMQ está indisponível. Nesse
último caso, a API desfaz o empréstimo. Os dados ficam em memória e são
reiniciados quando a API reinicia.

Um empréstimo criado por `POST /loans/` publica uma notificação no exchange
fanout `biblioteca.alertas`.

## Ver notificações no terminal

Com o RabbitMQ ativo e a partir da raiz de `trabalho3/`, abra um terminal
por assinante e execute, por exemplo:

```sh
uv run python -m notifications.listener ana
uv run python -m notifications.listener bruno
```

Cada listener declara automaticamente o exchange durável, a fila durável
`alertas.<usuário>` e o vínculo entre eles. Inicie os listeners antes de criar
um empréstimo para ver o evento aparecer nos terminais. Use `Ctrl+C` para
encerrar cada listener. O host e a porta do RabbitMQ usados pelo listener e
pela API estão definidos em `notifications/config.py`.

## Cliente Java

O cliente Java lista livros e solicita empréstimos. Em um terminal:

```sh
cd clients/client_a
javac Client.java
java Client http://127.0.0.1:8000
```

O argumento com a URL da API é opcional; sem ele, o cliente usa
`http://127.0.0.1:8000`. O nome enviado nos empréstimos está fixo como `ash` em
`Client.java`. Este cliente não escuta notificações RabbitMQ.

## Cliente Node.js

O cliente Node.js oferece as mesmas ações HTTP do cliente Java e também pode
escutar as notificações RabbitMQ do usuário configurado. Em um terminal:

```sh
cd clients/client_b
npm install
npm start -- http://127.0.0.1:8000 bruno
```

O primeiro argumento opcional é a URL da API e o segundo é o nome do usuário.
Sem argumentos, o cliente usa `http://127.0.0.1:8000` e o usuário `node`. As
configurações também podem ser fornecidas pelas variáveis `API_URL`,
`LIBRARY_USERNAME` e `RABBITMQ_URL`. A opção 3 do menu inicia a escuta; a opção
4 a encerra. A URL padrão do broker é `amqp://127.0.0.1:5672`; o publicador da
API usa o host e a porta definidos em `notifications/config.py`.

Cada usuário usa a fila durável `alertas.<usuário>` no exchange
`biblioteca.alertas`, como o listener Python. Dois processos usando o mesmo
usuário competem pela mesma fila: cada mensagem é entregue a um consumidor,
não copiada para os dois. Use nomes de usuário diferentes se quiser que cada
cliente receba sua própria cópia.

## Sistema legado

O cliente e o servidor TCP anteriores foram movidos para `legacy/`, não
excluídos. O fluxo novo de empréstimos usa a API; a publicação de notificações
pela API usa o mesmo exchange RabbitMQ. Os formatos TCP antigos permanecem em
`legacy/protocol/`.

## Testes

```sh
uv run python -m unittest discover -s tests -t .
```

`tests/integration/publish_concurrency.py` é um teste manual do servidor TCP
legado e requer que ele esteja em execução.

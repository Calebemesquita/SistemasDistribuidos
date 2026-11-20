# Biblioteca

## Organização

- `api/`: aplicação FastAPI, modelos, rotas e serviços.
- `clients/client_a/` e `clients/client_b/`: espaços reservados para os dois
  clientes futuros; não contêm implementações ainda.
- `notifications/`: publicação RabbitMQ pela API e listener de terminal.
- `protocol/`: formato compartilhado das mensagens de notificação.
- `legacy/`: cliente e servidor TCP antigos, mantidos como referência.
- `tests/`: testes automatizados.

## Executar a API

Na raiz do projeto:

```powershell
uv run uvicorn api.main:app --reload
```

Abra `http://127.0.0.1:8000/docs`. Um empréstimo criado por `POST /loans/`
publica uma notificação no exchange fanout `biblioteca.alertas`.

## Ver notificações no terminal

É necessário ter o RabbitMQ ativo e acessível em `127.0.0.1:5672`. Abra um
terminal por assinante e execute, por exemplo:

```powershell
uv run python -m notifications.listener ana
uv run python -m notifications.listener bruno
```

Cada listener declara automaticamente o exchange durável, a fila durável
`alertas.<usuário>` e o vínculo entre eles. Inicie os listeners antes de criar
um empréstimo para ver o evento aparecer nos terminais. Use `Ctrl+C` para
encerrar cada listener.

Se o RabbitMQ estiver indisponível, a API responde `503` e desfaz a criação do
empréstimo em memória. Os dados da API são locais ao processo e reiniciar a
aplicação os reinicializa.

## Sistema legado

O cliente e o servidor TCP anteriores foram movidos para `legacy/`, não
excluídos. O fluxo novo de empréstimos usa a API; a publicação de notificações
pela API usa o mesmo exchange RabbitMQ. Os formatos TCP antigos permanecem em
`legacy/protocol/`.

## Testes

```powershell
uv run python -m unittest discover -s tests -t .
```

`tests/integration/publish_concurrency.py` é um teste manual do servidor TCP
legado e requer que ele esteja em execução.

# Projeto servidor — Trabalho 4

API REST FastAPI para catálogo, empréstimos e notificações. O domínio usa o
agregado `Biblioteca` do pacote local `biblioteca-rpc` em `../../trabalho2`;
o protocolo RabbitMQ `Notification` vem do pacote `biblioteca-trabalho3` em
`../../trabalho3`.

```sh
uv sync
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000
```

A documentação OpenAPI fica em `/docs`. Consulte o [README do Trabalho 4](../README.md)
para ver os endpoints, configurar RabbitMQ, iniciar os clientes e rodar o CLI
de teste HTTP.

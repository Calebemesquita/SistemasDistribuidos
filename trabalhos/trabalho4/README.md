# Trabalho 4 — Web Service da Biblioteca

Este trabalho expõe a biblioteca como API REST FastAPI. O domínio vem das
classes do Trabalho 2 (`Biblioteca`, `Catalogo`, `HistoricoEmprestimos`,
`CanalNotificacoes`, papéis de usuário e tipos de notificação). O protocolo
`Notification` do Trabalho 3 adapta esses eventos para RabbitMQ. Os clientes
Java, Node.js e Python acessam o mesmo processo servidor por HTTP.

## Organização

- `servidor/`: API FastAPI, serviços adaptadores, testes e integração RabbitMQ.
- `cliente_java/` e `cliente_node/`: clientes independentes em duas linguagens.
- `cliente_cli/`: menu Python para testes HTTP reais e uso em outra máquina.
- `RELATORIO.md`: relatório da implementação.
- [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md): diagramas de processos,
  classes, herança, composição e fluxo de eventos.

O servidor instala `biblioteca-rpc` de `trabalho2/` e
`biblioteca-trabalho3` de `trabalho3/` como dependências locais. Mantenha a
estrutura deste repositório ao executar `uv sync`.

## Iniciar API e RabbitMQ

No computador servidor, inicie RabbitMQ e depois a API:

```sh
cd trabalhos/trabalho4/servidor
uv sync
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000
```

A interface OpenAPI fica em `http://IP_DO_SERVIDOR:8000/docs`. O host
`0.0.0.0` permite acesso pela rede; clientes devem usar o IP LAN do servidor.
O broker padrão é `127.0.0.1:5672`, usuário e senha `guest`. Configure
`RABBITMQ_HOST`, `RABBITMQ_PORT`, `RABBITMQ_USERNAME` e `RABBITMQ_PASSWORD`
no processo da API quando RabbitMQ estiver em outra máquina.

Para uso entre máquinas, RabbitMQ não aceita a conta padrão `guest` por
conexões remotas. Crie uma conta dedicada no computador do broker e configure
as mesmas credenciais nos componentes que publicam/consomem:

```sh
sudo rabbitmqctl add_user biblioteca senha-de-demonstracao
sudo rabbitmqctl set_permissions -p / biblioteca ".*" ".*" ".*"
```

No processo da API, defina `RABBITMQ_HOST`, `RABBITMQ_USERNAME` e
`RABBITMQ_PASSWORD`. No cliente Node, defina
`RABBITMQ_URL=amqp://biblioteca:senha-de-demonstracao@IP_DO_BROKER:5672`.

## Recursos HTTP

| Recurso | Uso |
| --- | --- |
| `GET /`, `GET /health` | Identificar o serviço e verificar se está ativo. |
| `GET /books/`, `POST /books/` | Consultar/cadastrar livros no `Catalogo`; cadastro registra um `Bibliotecario`. |
| `GET /loans/`, `POST /loans/` | Consultar histórico e emprestar; empréstimo registra um `Leitor`. |
| `POST /loans/{id}/return` | Registrar devolução e atualizar o mesmo livro e histórico. |
| `GET /users/` | Ver os usuários e seus papéis (`Leitor`/`Bibliotecario`). |
| `GET/POST /notifications/` | Consultar ou publicar eventos pelo canal e RabbitMQ. |
| `POST /notifications/subscriptions` | Inscrever um cliente no canal HTTP com `{ "client_id": "ana", "name": "Ana" }`. |
| `GET /notifications/subscriptions/{client_id}?after=N` | Consultar eventos após o cursor `N`; a resposta inclui novo `cursor`. |
| `DELETE /notifications/subscriptions/{client_id}` | Cancelar inscrição no canal HTTP. |

Cadastro, empréstimo e devolução usam as classes `Atualizacao` e `Alerta` do
Trabalho 2. O adaptador converte esses objetos para o protocolo JSON do Trabalho
3 e publica no exchange RabbitMQ `biblioteca.alertas`. O catálogo, usuários,
empréstimos e o canal HTTP ficam em memória e são apagados quando o servidor
reinicia. Se RabbitMQ não aceitar a publicação, a operação de domínio é
revertida.

## Testar em máquinas diferentes com o CLI

Inicie a API no servidor acima. Em outro computador na mesma rede, execute:

```sh
cd trabalhos/trabalho4/cliente_cli
python3 client.py --url http://192.168.1.20:8000 --username ana
```

Troque `192.168.1.20` pelo IP LAN real do servidor. No menu, escolha **9**
para inscrever `ana`, e **10** para consultar novos eventos. Em outro
computador, uma segunda pessoa inicia outro CLI com seu próprio usuário,
cadastra ou empresta um livro. Ao consultar novamente, o primeiro cliente vê
o evento e o cursor avança. Esse teste usa HTTP, então clientes precisam
alcançar a porta TCP 8000 do servidor.

Para automatizar cadastro, empréstimo, devolução, papéis e polling HTTP contra
o servidor em execução:

```sh
python3 client.py --url http://192.168.1.20:8000 --username smoke --smoke-test
```

O smoke test também publica no RabbitMQ, que precisa estar disponível para o
servidor. Os objetos criados permanecem em memória até reiniciar a API.

## Cliente Java

```sh
cd trabalhos/trabalho4/cliente_java
javac Client.java
java Client http://192.168.1.20:8000 ana
```

## Cliente Node.js e escuta RabbitMQ

```sh
cd trabalhos/trabalho4/cliente_node
npm install
npm start -- http://192.168.1.20:8000 bruno
```

Para escutar o broker no cliente Node, defina `RABBITMQ_URL`, por exemplo
`amqp://usuario:senha@192.168.1.30:5672`. O menu tem opções para inscrever e
cancelar a fila individual `alertas.bruno`. O listener Python do servidor
também pode ser iniciado com `RABBITMQ_HOST`, `RABBITMQ_PORT`,
`RABBITMQ_USERNAME` e `RABBITMQ_PASSWORD` definidos.

## Testes

```sh
cd trabalhos/trabalho2
uv run python -m unittest discover -s tests -v

cd ../trabalho3
uv run python -m unittest discover -s tests -t .

cd ../trabalho4/servidor
uv run python -m unittest discover -s tests -t .
```

O CLI `--smoke-test` faz a validação HTTP de ponta a ponta com servidor e
RabbitMQ ativos.

## Entrega

O enunciado pede o código-fonte, este relatório e um vídeo ou apresentação em
sala. Envie o link do repositório e o vídeo pelo Moodle.

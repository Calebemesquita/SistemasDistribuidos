# Relatório — Trabalho 4: Web Services e API

## Identificação

Disciplina: Sistemas Distribuídos — UFC, Campus de Quixadá

- Calebe Mesquita da Silva — matrícula 566342
- Francisco Emilson Santos Souza Filho — matrícula 565685

## Objetivo e arquitetura

O Trabalho 4 expõe a biblioteca por HTTP e JSON usando FastAPI. A API fornece
objetos distribuídos para catálogo, empréstimos e notificações. O domínio não
foi duplicado na API: o servidor instala o pacote local do Trabalho 2 e usa
seu agregado `Biblioteca`, com `Catalogo`, `HistoricoEmprestimos`,
`CanalNotificacoes`, `Inscricoes` e as entidades do diagrama. O protocolo
`Notification`/`NotificationType` do Trabalho 3 é usado somente para publicar
as notificações de domínio no RabbitMQ.

O diagrama de processos e classes está em
[`docs/ARQUITETURA.md`](docs/ARQUITETURA.md). A interface
`Serializavel` é um protocolo estrutural implementado pelas entidades do T2;
o adaptador HTTP chama `serializar()` ao projetar essas entidades em DTOs.

## Recursos remotos

| Responsabilidade | Recursos |
| --- | --- |
| Catálogo | `GET/POST /books/` |
| Empréstimos | `GET/POST /loans/`, `POST /loans/{id}/return` |
| Usuários e papéis | `GET /users/` |
| Eventos | `GET/POST /notifications/` |
| Inscrição HTTP com polling | `POST /notifications/subscriptions`, `GET /notifications/subscriptions/{client_id}?after=N`, `DELETE /notifications/subscriptions/{client_id}` |

O `BookService` HTTP cadastra livros pelo método do agregado e associa um
`Bibliotecario`. O `LoanService` chama o agregado para emprestar/devolver;
`Leitor.emprestimos` e o histórico são atualizados sobre o mesmo catálogo que a
rota de livros lista. As notificações criadas pelo domínio são subclasses
`Alerta` e `Atualizacao`; o adaptador as converte para JSON do Trabalho 3 e
publica no exchange fanout `biblioteca.alertas`.

Pydantic valida os dados de entrada e saída na fronteira HTTP. O processo
FastAPI atende as rotas sem criar sockets na aplicação e sem usar RMI. A
especificação OpenAPI fica em `/docs`.

## Clientes e distribuição

O cliente Java usa `java.net.http.HttpClient`, o cliente Node.js usa `fetch`,
e ambos acessam a API HTTP. O Node.js também pode consumir RabbitMQ com
`amqplib`. A CLI Python usa `urllib`, não importa o código do servidor e tem
um menu para catálogo, empréstimos, usuários, inscrições e consulta por cursor.

Para demonstração entre máquinas, o servidor deve escutar em `0.0.0.0:8000`.
Clientes usam o IP LAN do servidor. Com a inscrição HTTP, duas máquinas
consultam o mesmo `CanalNotificacoes` do processo API; com RabbitMQ, listeners
independentes recebem cópias do exchange fanout. Abra na rede as portas 8000
(API) e 5672 (broker) conforme o fluxo usado.

Exemplo do cliente remoto:

```sh
cd trabalhos/trabalho4/cliente_cli
python3 client.py --url http://IP_DO_SERVIDOR:8000 --username ana
```

No menu, opção 9 inscreve e opção 10 consulta novos eventos. O cursor retornado
evita reler eventos anteriores.

## Validação

Os testes unitários verificam a composição do agregado, herança dos papéis e
tipos de notificação, contrato `Serializavel`, uso do mesmo estado pelas rotas,
polling por inscrição e rollback quando RabbitMQ falha. O comando de smoke test
faz chamadas HTTP reais para cadastrar livro, emprestar, devolver, listar
usuários e consultar eventos; precisa de API e RabbitMQ ativos.

```sh
cd trabalhos/trabalho4/cliente_cli
python3 client.py --url http://127.0.0.1:8000 --username smoke --smoke-test
```

O servidor mantém o domínio em memória, então reiniciar apaga catálogo,
usuários, empréstimos e eventos. Não há autenticação ou autorização; o usuário
do menu identifica o papel funcional, mas não é uma credencial.

## Entrega

Além do código-fonte e deste relatório, o enunciado pede um vídeo ou uma
apresentação em sala mostrando o serviço e os clientes. O link do repositório e
o vídeo devem ser enviados pelo Moodle.

## Relação incremental entre trabalhos

- **Trabalho 2:** define as entidades e agregados que a API usa como domínio.
- **Trabalho 3:** fornece o formato de evento JSON e a integração RabbitMQ.
- **Trabalho 4:** adiciona transporte HTTP, DTOs, adaptadores, clientes
  independentes e demonstração entre máquinas.

Assim, o Trabalho 4 acrescenta um transporte remoto ao domínio já criado, em
vez de manter um segundo conjunto de classes de livro e empréstimo.

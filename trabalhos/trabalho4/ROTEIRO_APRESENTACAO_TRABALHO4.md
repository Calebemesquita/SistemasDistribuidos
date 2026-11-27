# Roteiro de apresentação — Trabalho 4: Web Service/API

**Duração sugerida:** 5 minutos.

## 0:00–0:40 — Objetivo

Explique que o Trabalho 4 adiciona transporte HTTP ao sistema da biblioteca.
O domínio é o agregado do Trabalho 2; o protocolo de eventos RabbitMQ vem do
Trabalho 3. O servidor é Python/FastAPI, e os clientes Java, Node.js e Python
são processos separados.

## 0:40–1:40 — Classes e OOP

Abra `docs/ARQUITETURA.md`. Mostre que `Leitor` e `Bibliotecario` herdam de
`Usuario`; `Alerta` e `Atualizacao` herdam de `Notificacao`; `Biblioteca`
agrega `Catalogo` e `HistoricoEmprestimos`; `CanalNotificacoes` agrega
`Inscricoes` e os eventos. Aponte que `Serializavel` converte objetos do
domínio para JSON e que os adaptadores HTTP recebem a mesma instância de
`Biblioteca`.

## 1:40–2:20 — API e menu

Abra `/docs` para mostrar `/books`, `/loans`, `/users` e as rotas de inscrição
e consulta do canal. Mostre o CLI Python: ele usa HTTP real, e não importa
serviços internos do servidor.

## 2:20–4:30 — Demonstração em duas máquinas

1. No computador servidor, inicie RabbitMQ e a API em `0.0.0.0:8000`.
2. No computador A, inicie o CLI com o IP LAN do servidor e usuário `ana`.
3. No CLI A, escolha **9** para inscrever `ana` no canal HTTP.
4. No computador B, inicie outro CLI com usuário `bruno`; cadastre um livro e
   faça um empréstimo.
5. No CLI A, escolha **10**. Mostre o alerta recebido e o cursor avançado.
6. Devolva o empréstimo no computador B e consulte novamente no computador A
   para ver a atualização.
7. Mostre `/users/` ou a opção **8** para observar os papéis do domínio.

Para também demonstrar RabbitMQ diretamente, use a opção de escuta do cliente
Node.js ou o listener Python em uma fila própria.

## 4:30–5:00 — Fechamento

Resuma a integração incremental dos três trabalhos. Diga que o catálogo,
usuários, empréstimos e eventos permanecem em memória e são reiniciados quando
a API para. O relatório e os comandos ficam em `RELATORIO.md` e `README.md`.

# Trabalho 2 — Biblioteca e notificações via RPC

Implementação didática de comunicação cliente-servidor com requisição-resposta, `xmlrpc` da biblioteca padrão do Python e serialização JSON. **O projeto não cria sockets manualmente.** O transporte XML-RPC utiliza infraestrutura de rede da biblioteca padrão.

> **Decisão arquitetural importante:** O Trabalho 1 exigia UDP multicast; o Trabalho 2 exige RPC/RMI e proíbe criar sockets. Aqui, a difusão de notificações foi reimplementada como **distribuição lógica para vários clientes por RPC**, por meio de inscrição e consultas periódicas (`polling`). Isso **não constitui multicast IP**. Confirme com o professor se ele exige multicast IP literal, pois esse aspecto é incompatível com a implementação apenas por RPC sem um serviço intermediário próprio de multicast.

## Requisitos

Python 3.10+; nenhuma dependência externa.

## Executar

Abra terminais na raiz do projeto:

**Terminal 1 — servidor**
```bash
python -m biblioteca_rpc.server
```

**Terminal 2 — cliente receptor A**
```bash
python -m biblioteca_rpc.listener --nome Ana
```

**Terminal 3 — cliente receptor B**
```bash
python -m biblioteca_rpc.listener --nome Bruno
```

**Terminal 4 — publicador**
```bash
python -m biblioteca_rpc.publisher
```

Digite `ALERTA` e uma mensagem. Ambos os receptores receberão o evento pelo canal de consultas RPC. Para demonstrar a biblioteca e uma referência remota recebida como resultado:
```bash
python -m biblioteca_rpc.demo
```

**Testes automatizados:**
```bash
python -m unittest discover -s tests -v
```

## Arquitetura

- `RPCClient.doOperation(remote_object_ref, method_id, arguments: bytes) -> bytes`: empacota a solicitação, transmite via XML-RPC e valida o identificador da resposta.
- `RPCDispatcher.getRequest(raw: bytes) -> dict`: desempacota e valida a requisição.
- `RPCDispatcher.sendReply(response: bytes) -> Binary`: empacota a resposta para o transporte XML-RPC.
- `RPCDispatcher.exchange`: único ponto de entrada remoto, responsável pelo despacho do método especificado em `objectReference` / `methodId`.
- `RemoteProxy`: encapsula uma referência remota (`biblioteca` ou `notificacoes`), sem copiar o estado do objeto no servidor.
- Passagem por valor: os argumentos de entidades, como os dados de um `Livro`, são codificados como JSON UTF-8.
- Passagem por referência: `biblioteca.obter_canal()` retorna uma identificação de outro objeto remoto; o cliente a converte em `RemoteProxy`. Isso implementa referências remotas na camada de aplicação, **não o sistema de referências nativo de Java RMI**.

## Estrutura de mensagem

```json
{
  "messageType": "Request",
  "requestId": "id-unico",
  "objectReference": "notificacoes",
  "methodId": "publicar",
  "arguments": [123,34,109,101,110,115,97,103,101,109,34,58,34,79,105,34,125]
}
```

O campo `arguments` contém a lista dos bytes da representação JSON UTF-8. A resposta replica os campos de identificação, altera `messageType` para `Reply` e transporta `result` ou `error` nos bytes de `arguments`.

## Entidades e relacionamentos

- Entidades: `Usuario`, `Leitor`, `Bibliotecario`, `Livro`, `Notificacao`, `Alerta`, `Atualizacao`, `Catalogo`, `HistoricoEmprestimos`, `Inscricoes`.
- Herança 1: `Leitor` **é um** `Usuario`; herança 2: `Bibliotecario` **é um** `Usuario`. Há ainda `Alerta` e `Atualizacao` herdando de `Notificacao`.
- Agregação 1: `Biblioteca` **tem um** `Catalogo`; agregação 2: `Biblioteca` **tem um** `HistoricoEmprestimos`. `CanalNotificacoes` agrega `Inscricoes` e uma lista de notificações.
- Métodos remotos: `cadastrar_livro`, `listar_livros`, `emprestar_livro`, `devolver_livro`, `obter_canal`, `inscrever`, `cancelar_inscricao`, `publicar`, `consultar`.

## Limitações conscientes

- O serviço de notificação usa *polling* (intervalo padrão de 1s), não push UDP multicast.
- Os registros são mantidos somente em memória; reiniciar o servidor remove o estado.
- A cache de deduplicação armazena no máximo 2048 respostas por execução, sem persistência. Portanto, não há garantia irrestrita de no-máximo-uma-vez após reinício/expiração.
- O servidor deve ser usado em localhost para demonstração; não há autenticação nem autorização implementadas.

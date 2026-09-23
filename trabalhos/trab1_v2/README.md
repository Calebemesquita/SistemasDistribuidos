# Trabalho 1 — Comunicação entre processos

#### Dupla
- Calebe Mesquita da Silva - 566342
- Francisco Emilson Santos Souza Filho - 565685

Implementação do Trabalho 1 da disciplina **Sistemas Distribuídos**.

O serviço remoto escolhido é um **sistema de alertas de rede**, que representa ataques detectados e gera relatórios de incidentes.

#### Diretorio
A pasta deste repositório chama-se `trab1_v2` e é o pacote Python usado nos comandos abaixo.

## Serviço escolhido
Os modelos e serviços estão em `modelos/models.py` e `servicos/sevice.py`.

- **POJOs:** `Ataque` descreve um evento de rede; `RelatorioIncidente` reúne os ataques de um relatório.
- **Serviços:** `ServicoRelatorios` cria e consulta relatórios; `ServicoNotificacao` prepara alertas e acompanha inscrições.
- **Formato de intercâmbio:** JSON codificado em UTF-8.

## Questão 1 — `AtaqueOutputStream`
Implementada em `streams/stream.py`.
- O construtor recebe o destino, a lista de ataques e a quantidade a enviar.
- Cada ataque é convertido para JSON e escrito como uma linha de bytes.

Os testes cobrem os destinos pedidos:
- saída padrão `sys.stdout` em Python;
- arquivo temporário, equivalente ao `FileOutputStream`;
- conexão TCP com um servidor receptor.

## Questão 2 — `AtaqueInputStream`
Também implementada em `streams/stream.py`. O construtor recebe a origem dos bytes, lê uma linha JSON por ataque e reconstrói objetos `Ataque`.

Os testes cobrem:
- entrada padrão  o `sys.stdin`;
- arquivo temporário, equivalente ao `FileInputStream`;
- conexão TCP com um cliente que envia os dados.

## Questão 3 — Serialização cliente-servidor

#### Cliente
O cliente em `cliente/client.py` empacota uma requisição JSON, envia-a por TCP e reconstrói o relatório recebido. 

#### Servidor
O servidor em `servidor/server.py` desempacota a requisição, executa `ServicoRelatorios`, empacota a resposta e a envia de volta. O servidor atende conexões em threads.

O teste cliente-servidor verifica o envio dos ataques e o recebimento do relatório.

## Questão 4 — Multicast

O código está em `multicast/` e usa **230.0.0.1**, porta UDP fixa **5007** e mensagens JSON com tipo, mensagem e timestamp.

1. O cliente autentica por TCP com o servidor em `127.0.0.1:5052`.
2. Após autenticar, o cliente entra no grupo multicast (`entrar_no_grupo`) e recebe mensagens em uma thread. Outra thread permite encerrar pelo terminal com `sair`.
3. O servidor envia mensagens `NOTIFICACAO`, `ALERTA` e `ATUALIZACAO`. O console do servidor publica alertas; uma thread publica atualizações periódicas.
4. O servidor atende autenticações em threads e também oferece `enviar_varios_concorrentemente` para publicar mensagens simultaneamente.
5. Ao sair, o cliente deixa o grupo (`sair_do_grupo`).

O multicast usa por padrão a interface local `127.0.0.1`, adequada para testar na mesma máquina. Para outra interface, defina `MULTICAST_INTERFACE` com o IPv4 da interface nos processos servidor e cliente.

## Questão extra — Sistema de votação
Não realizamos implementação da questão extra

## Estrutura do projeto

```text
trab1_v2/
├── cliente/       # cliente TCP da serialização
├── modelos/       # Ataque e RelatorioIncidente
├── multicast/     # autenticação TCP e publicação/recepção UDP
├── servidor/      # servidor TCP da serialização
├── servicos/      # regras de relatório e notificação
├── streams/       # streams de entrada e saída de Ataque
└── testes/        # testes das questões 1 a 4
```

## Executar os testes

MUITO IMPORTANTE: Para executar os testes esteja no diretorio `trabalhos` para os respectivos comandos testes a seguir

```bash
python3 -m unittest trab1_v2.testes.test_poc trab1_v2.testes.test_multicast -v
```

Os testes exercitam streams, comunicação TCP, serialização, autenticação e recebimento multicast por múltiplos clientes.

## Executar a serialização manualmente
Em um terminal, inicie o servidor:

```bash
python3 -m trab1_v2.servidor.server
```

- O servidor escuta em `127.0.0.1:5051`. 
- Em outro terminal, execute o cliente com um ataque de exemplo:

```bash
python3 -m trab1_v2.cliente.client
```

## Executar o multicast manualmente

Inicie o servidor (autenticação TCP e console de publicação):

```bash
python3 -m trab1_v2.multicast.servidor_multicast
```

Em outro terminal, inicie um ou mais clientes:

```bash
python3 -m trab1_v2.multicast.cliente_multicast analista-1
python3 -m trab1_v2.multicast.cliente_multicast analista-2
```

Digite uma mensagem no console do servidor para publicar um `ALERTA`. Os clientes conectados a esse grupo recebem as mensagens. Digite `sair` no cliente para deixar o grupo e encerrar.

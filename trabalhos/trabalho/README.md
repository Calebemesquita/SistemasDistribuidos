# Trabalho 1 — Comunicação entre Processos

**Disciplina:** QXD0043 — Sistemas Distribuídos, UFC Campus de Quixadá  
**Integrantes:** Calebe Mesquita da Silva (566342) e Francisco Emilson Santos Souza Filho (565685)

Este repositório implementa um serviço de gerenciamento de incidentes e relatórios. Este guia explica as questões 1–4 do PDF e traz um roteiro de apresentação de cinco minutos. A questão extra de votação está documentada ao final.

Execute os comandos a partir da raiz do projeto. Use `python` no lugar de `python3` se esse for o comando instalado.

## Visão geral

```text
POJO/       modelos de dados: Incidente, RelatorioIncidente, Usuario e Notificacao
servicos/   operações de cadastro, busca e remoção de incidentes e relatórios
fluxo/      IncidenteOutputStream e IncidenteInputStream
Q1/         testes do stream de saída: stdout, arquivo e TCP
Q2/         testes do stream de entrada: stdin, arquivo e TCP
Q3/         mensagens serializadas e chamadas request/reply por TCP
Q4/         autenticação TCP e notificações UDP multicast
Q6/         questão extra: votação distribuída
```

## Conceito comum às questões 1 e 2: formato do stream

Cada relatório é transformado em JSON UTF-8 e enviado neste formato:

```text
[4 bytes com o tamanho do JSON, big-endian][JSON UTF-8]
```

Os quatro primeiros bytes permitem ao leitor saber quantos bytes pertencem ao objeto seguinte. Esse enquadramento também funciona em TCP, onde uma leitura pode receber só parte dos bytes enviados.

## Questão 1 — stream de saída (`OutputStream`)

O POJO escolhido para transmitir é `RelatorioIncidente`. `IncidenteOutputStream` recebe um destino, uma lista de relatórios e a quantidade a enviar. Para cada relatório, chama `to_dict()`, codifica o JSON em UTF-8, escreve o cabeçalho de tamanho e depois o conteúdo. O método também trata escritas parciais e faz `flush()` no destino.

### 1b e 1c — stdout e arquivo

```bash
python3 -m Q1.main > stdout.bin
python3 -m Q1.verificar_bin
cmp stdout.bin saida.bin
```

`Q1.main` envia o stream binário para `sys.stdout.buffer` e grava os mesmos relatórios em `saida.bin` usando um arquivo. As mensagens de acompanhamento são escritas em stderr; assim, não se misturam aos bytes de `stdout.bin`. O verificador abre `saida.bin`, separa cada frame pelo tamanho e mostra os JSONs reconstruídos. `cmp` confirma que stdout e arquivo contêm os mesmos bytes.

### 1d — destino TCP

Terminal 1:

```bash
python3 -m Q1.servidor
```

Terminal 2:

```bash
python3 -m Q1.cliente
```

O cliente conecta ao servidor na porta TCP `5000` e entrega os relatórios ao `IncidenteOutputStream`, cujo destino é o stream de escrita do socket. O servidor lê os bytes até o cliente encerrar a conexão e salva o fluxo em `recebido.bin`.

## Questão 2 — stream de entrada (`InputStream`)

`IncidenteInputStream` recebe um stream de origem e reconstrói instâncias de `RelatorioIncidente`. Primeiro lê exatamente quatro bytes; depois usa o tamanho indicado para ler o JSON completo e chama `RelatorioIncidente.from_dict()`. `_read_exact` repete as leituras quando chegam poucos bytes, diferencia EOF normal de um frame truncado e `ler_objetos()` pode ler até EOF ou uma quantidade definida.

### 2b e 2c — stdin e arquivo

Gere `saida.bin` pela demonstração da questão 1 e execute:

```bash
python3 -m Q2.main stdin < saida.bin   # lê da entrada padrão
python3 -m Q2.main                     # lê o arquivo saida.bin
```

Nos dois casos, os objetos são reconstruídos e impressos. O primeiro comando conecta o stream à entrada padrão binária; o segundo abre o arquivo em modo binário.

### 2d — origem TCP

Terminal 1:

```bash
python3 -m Q2.servidor
```

Terminal 2:

```bash
python3 -m Q2.cliente
```

O cliente envia relatórios por TCP com o mesmo stream de saída da questão 1. O servidor envolve o socket recebido em `IncidenteInputStream`, lê os frames até EOF e imprime os relatórios reconstruídos. Para interromper o servidor após a demonstração, use `Ctrl+C`.

## Questão 3 — serialização de request e reply

Aqui a mensagem inteira é serializada como JSON e enquadrada com o mesmo cabeçalho de quatro bytes. O envelope contém `id`, `tipo`, `status` e `payload`. O ID permite relacionar cada resposta à requisição correspondente.

O cliente empacota e envia operações como `CRIAR_INCIDENTE`, `BUSCAR_INCIDENTE`, `LISTAR_INCIDENTES` e `CRIAR_RELATORIO`. O servidor desempacota o frame, encaminha a operação aos serviços, serializa a resposta e a envia de volta. O cliente também desempacota a reply. A demonstração termina buscando um incidente inexistente para mostrar uma resposta `ERRO`. Os dados ficam em memória no servidor.

Terminal 1:

```bash
python3 -m Q3.servidor
```

Terminal 2:

```bash
python3 -m Q3.cliente
```

A comunicação usa TCP na porta `6000`. Uma conexão pode carregar várias requisições e respostas antes de ser fechada.

## Questão 4 — multicast de notificações

A questão combina dois tipos de comunicação:

- **TCP unicast:** o cliente envia usuário e senha ao servidor na porta `7000`; o servidor responde se a autenticação foi aceita e informa o grupo e a porta multicast.
- **UDP multicast:** clientes autenticados entram no grupo classe D `239.10.10.10`, porta fixa `7001`. O servidor envia datagramas JSON com tipo, mensagem e timestamp para todos os membros do grupo.

No cliente, uma thread fica bloqueada esperando datagramas e os exibe em tempo real; a thread principal continua lendo a entrada do usuário. Ao digitar `sair`, o cliente sinaliza o encerramento da thread e remove a associação ao grupo (`leaveGroup`). O servidor aceita autenticações em threads e publica cada mensagem em uma thread; um lock protege o socket de envio.

### Demonstração local com dois clientes

Em loopback, configure `MULTICAST_INTERFACE=127.0.0.1` nos três processos. Terminal 1:

```bash
MULTICAST_INTERFACE=127.0.0.1 python3 -m Q4.servidor
```

Terminais 2 e 3 — execute em ambos para demonstrar vários clientes:

```bash
MULTICAST_INTERFACE=127.0.0.1 python3 -m Q4.cliente
```

Credenciais de demonstração: `admin / admin123`, `aluno / aluno123` ou `ana / ana123`. Depois que os clientes entrarem no grupo, digite no servidor:

```text
NOTIFICACAO Novo dado disponível
ALERTA Incidente crítico no servidor
ATUALIZACAO Relatório concluído
```

As mensagens devem aparecer nos dois clientes. Digite `sair` em cada cliente para sair do grupo e `sair` no servidor para encerrar. As credenciais são fixas no código e servem apenas para a demonstração acadêmica.

### Execução em máquinas diferentes

`MULTICAST_INTERFACE` deve apontar para a interface local que alcança os outros participantes. Configure o IP da interface de rede no servidor e o IP da interface correspondente em cada cliente; altere também `HOST` em `Q4/cliente.py` para o endereço do servidor. O padrão `0.0.0.0` deixa a escolha da interface a cargo do sistema operacional. Firewalls e roteadores podem bloquear multicast.

## Roteiro sugerido para falar por cinco minutos

1. **0:00–0:30 — Contexto:** “O serviço trabalha com incidentes e relatórios. Vou mostrar três formas de representar e transportar os dados: stream, request/reply serializado e multicast.”
2. **0:30–1:20 — Q1:** mostre a lista de relatórios, o frame tamanho + JSON, e rode stdout/arquivo. Explique que o destino é intercambiável. Se houver tempo, demonstre cliente e servidor TCP.
3. **1:20–2:10 — Q2:** leia `saida.bin` por arquivo e por stdin; explique a leitura exata do cabeçalho e do payload. Depois mostre servidor/cliente TCP para comprovar que os mesmos bytes podem ser reconstruídos pela rede.
4. **2:10–3:20 — Q3:** inicie servidor e cliente. Aponte um request de criação, uma busca e a resposta de erro. Explique que cliente e servidor empacotam e desempacotam JSON em frames, e que `id` associa reply ao request.
5. **3:20–4:50 — Q4:** inicie o servidor e dois clientes. Autentique ambos, publique `NOTIFICACAO` e `ALERTA`, e mostre as duas telas recebendo as mensagens. Explique TCP para autenticação, UDP multicast para distribuição e thread separada no cliente.
6. **4:50–5:00 — Fechamento:** reforce a diferença: Q1/Q2 transportam um fluxo de objetos; Q3 faz operações remotas request/reply; Q4 distribui eventos a vários clientes.

Para caber no tempo, deixe os servidores e terminais preparados. Os comandos de execução completa de cada item estão nas seções acima.

## Questão extra — votação distribuída

A pasta `Q6/` contém a aplicação extra. Login, candidatos, votos e administração usam TCP na porta `7100`; o servidor atende conexões em threads. Notas informativas do administrador são enviadas por UDP multicast ao grupo `239.10.10.20:7101`. O prazo padrão é 120 segundos e pode ser reduzido para demonstração:

```bash
MULTICAST_INTERFACE=127.0.0.1 VOTACAO_DURACAO_SEGUNDOS=30 python3 -m Q6.servidor
MULTICAST_INTERFACE=127.0.0.1 python3 -m Q6.cliente
```

Contas: administrador `admin / admin123`; eleitores `ana / ana123`, `bia / bia123` e `caio / caio123`. Comandos do cliente: `candidatos`, `votar ID`, `adicionar NOME`, `remover ID`, `nota TEXTO`, `resultado` e `sair`. Cada eleitor vota uma vez; votos e alteração de candidatos são recusados após o prazo. O resultado mostra totais, percentuais e ganhador ou empate.

## Verificações

Os testes existentes cobrem os modelos, streams e serialização das questões 1–3. Execute:

```bash
python3 -m unittest discover -s testes -t . -v
python3 -m testes.tcp_integracao
```

## Materiais de estudo e apresentação

Há guias teóricos para Q1–Q3 e um roteiro prático de execução e falas para Q4:

- [Streams e enquadramento — questões 1 e 2](README_TEORICO_1_STREAMS_Q1_Q2.md)
- [Serialização e request/reply — questão 3](README_TEORICO_2_SERIALIZACAO_Q3.md)
- [Roteiro de apresentação — questão 4](README_APRESENTACAO_Q4.md)

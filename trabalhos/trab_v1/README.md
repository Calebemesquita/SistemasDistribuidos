# Trabalho 1 — Comunicação entre Processos
- Calebe Mesquita da Silva 566342
- Francisco Emilson Santos Souza Filho - 565685
Implementação das questões 1, 2 e 3 do trabalho de Sistemas Distribuídos 
## Organização

```text
POJO/       modelos Incidente e RelatorioIncidente
servicos/   operações dos objetos de domínio
fluxo/      streams de saída e entrada para relatórios
Q1/         envio para stdout, arquivo e TCP
Q2/         leitura de stdin, arquivo e TCP
Q3/         protocolo JSON e comunicação request/reply por TCP
testes/     testes locais das questões 1, 2 e 3
rascunhos/  exemplos e experimentos de estudo
```

Execute os comandos a seguir a partir da raiz do repositório. Se necessário, troque `python3` por `python`.

## Questão 1 — enviar relatórios

O formato dos streams das questões 1 e 2 é `[tam 4 bytes big-endian] [JSON UTF-8] `

**stdout e arquivo:** o programa envia bytes para stdout e grava `saida.bin`.
O redirecionamento salva a cópia de stdout sem misturar texto no arquivo:

```bash
python3 -m Q1.main > stdout.bin
python3 -m Q1.verificar_bin
```

O verificador lê `saida.bin` e mostra os relatórios reconstruídos.
Para comprovar TCP, abra dois terminais na raiz do projeto:

```bash
# Terminal 1
python3 -m Q1.servidor

# Terminal 2
python3 -m Q1.cliente
```

O servidor grava o fluxo recebido em `recebido.bin`.

## Questão 2 — ler relatórios
Gere `saida.bin` pela Questão 1 assim
a leitura de stdin e a leitura de arquivo exibem os objetos reconstruídos:

```bash
python3 -m Q2.main stdin < saida.bin  # stdin (2b)
python3 -m Q2.main                    # arquivo saida.bin (2c)
```

Para TCP, abra dois terminais. 
O cliente usa o `IncidenteOutputStream` da Questão 1; 
O leitor do servidor trata leituras parciais e termina quando o cliente fecha a conexão:

```bash
# Terminal 1
python3 -m Q2.servidor

# Terminal 2
python3 -m Q2.cliente
```

## Questão 3 — serializar request e reply

O cliente empacota requests como JSON UTF-8 com cabeçalho de tamanho de 4 bytes big-endian.

O servidor desempacota, executa operações sobre incidentes/relatórios, empacota a resposta e o cliente a desempacota.

O exemplo cria e busca objetos e também solicita um incidente inexistente para demonstrar a resposta de erro.

Abra dois terminais na raiz do projeto:

```bash
# Terminal 1
python3 -m Q3.servidor

# Terminal 2
python3 -m Q3.cliente
```

Confira no terminal do cliente as replies `OK` e `ERRO`;
o servidor continua aceitando conexões depois que um cliente encerra.

## Verificação local
Rode os testes sem abrir sockets.
Eles verificam round-trip de vários relatórios, origem que entrega poucos bytes por leitura, dados truncados, serialização JSON e processamento de requests/replies:

```bash
python3 -m unittest discover -s testes -t . -v
```

Para executar também uma checagem ponta a ponta que inicia os clientes e servidores das três questões em loopback TCP:

```bash
python3 -m testes.tcp_integracao
```

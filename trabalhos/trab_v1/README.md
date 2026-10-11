# Trabalho 1 — Comunicação entre Processos

**Disciplina:** QXD0043 — Sistemas Distribuídos, UFC Campus de Quixadá  
**Integrantes:** Calebe Mesquita da Silva (566342) e Francisco Emilson Santos Souza Filho (565685)

Implementação do serviço remoto de gerenciamento de incidentes e relatórios, incluindo streams, serialização TCP, notificações multicast e a questão extra de votação.

## Organização

```text
POJO/       modelos Incidente, RelatorioIncidente, Usuario e Notificacao
servicos/   operações de incidentes e relatórios
fluxo/      streams de entrada e saída dos relatórios
Q1/         envio para stdout, arquivo e TCP
Q2/         leitura de stdin, arquivo e TCP
Q3/         protocolo JSON enquadrado e chamadas request/reply TCP
Q4/         autenticação TCP e notificações UDP multicast
Q6/         votação TCP multithreaded e notas UDP multicast
testes/     testes existentes das questões 1–3
```

Execute os comandos na raiz do repositório. Se necessário, troque `python3` por `python`.

## Questão 1 — OutputStream de relatórios

O formato compartilhado pelas questões 1 e 2 é `[tamanho: 4 bytes big-endian][JSON UTF-8]` para cada objeto.

**stdout e arquivo:** o programa escreve os frames em stdout binário e também em `saida.bin`. Mensagens de demonstração vão para stderr para não corromper o fluxo redirecionado.

```bash
python3 -m Q1.main > stdout.bin
python3 -m Q1.verificar_bin
```

**TCP:** inicie o servidor e, em outro terminal, o cliente. O servidor grava os bytes recebidos em `recebido.bin`.

```bash
python3 -m Q1.servidor
python3 -m Q1.cliente
```

## Questão 2 — InputStream de relatórios

```bash
python3 -m Q2.main stdin < saida.bin   # stdin
python3 -m Q2.main                     # arquivo saida.bin
```

Para a leitura TCP, rode `python3 -m Q2.servidor` e depois `python3 -m Q2.cliente` em outro terminal. O leitor trata entregas parciais e encerra ao receber EOF limpo.

## Questão 3 — serialização request/reply

O cliente e o servidor serializam mensagens JSON em frames `[tamanho: 4 bytes big-endian][JSON UTF-8]`. O servidor mantém os serviços de incidentes e relatórios em memória. A demonstração cria e busca objetos e mostra também uma resposta de erro.

```bash
python3 -m Q3.servidor
python3 -m Q3.cliente
```

O servidor aceita múltiplas operações na conexão e continua aceitando novos clientes.

## Questão 4 — notificações multicast

O servidor autentica conexões por TCP na porta `7000` e publica datagramas JSON no grupo multicast `239.10.10.10:7001`. Cada cliente usa uma thread para escutar e pode sair com `sair`, o que remove sua associação ao grupo.

Na mesma máquina, selecione loopback nos dois processos para garantir que os pacotes multicast retornem ao host. Terminal 1:

```bash
MULTICAST_INTERFACE=127.0.0.1 python3 -m Q4.servidor
```

Terminal 2 (repita para abrir outros clientes):

```bash
MULTICAST_INTERFACE=127.0.0.1 python3 -m Q4.cliente
```

Credenciais de demonstração: `admin / admin123`, `aluno / aluno123` ou `ana / ana123`. No servidor, publique mensagens digitando `NOTIFICACAO texto`, `ALERTA texto` ou `ATUALIZACAO texto`; `sair` encerra o servidor. Clientes devem autenticar e entrar no grupo antes da publicação para receber as mensagens. A autenticação serve como demonstração acadêmica e usa credenciais em memória; não é adequada para produção.

## Questão extra — votação distribuída

A votação usa TCP na porta `7100` para login, consulta de candidatos, votos e administração. O servidor atende cada conexão em uma thread. O prazo padrão é de 120 segundos a partir da inicialização. Para uma demonstração curta, configure a duração antes de iniciar o servidor:

```bash
VOTACAO_DURACAO_SEGUNDOS=30 python3 -m Q6.servidor
```

Em outro terminal, rode `MULTICAST_INTERFACE=127.0.0.1 python3 -m Q6.cliente` (abra clientes adicionais para simular eleitores simultâneos). Defina `MULTICAST_INTERFACE=127.0.0.1` também no comando do servidor quando todos os processos estiverem na mesma máquina. Em uma rede local, use em cada processo o endereço IP da interface de rede que alcança os demais clientes. Os dados de demonstração são:

- Administrador: `admin / admin123`
- Eleitores: `ana / ana123`, `bia / bia123`, `caio / caio123`

Comandos do cliente:

```text
candidatos           lista candidatos e prazo restante
votar ID             registra um voto (um voto por eleitor)
adicionar NOME        adiciona candidato (administrador)
remover ID            remove candidato sem votos (administrador)
nota TEXTO            envia nota informativa via multicast (administrador)
resultado             exibe total, percentuais e ganhador após o prazo (administrador)
sair                  encerra a conexão
```

Candidatos iniciais: IDs 1 (Alice), 2 (Bruno) e 3 (Carla). A votação recusa votos e alterações de candidatos após o prazo. A remoção é bloqueada para candidatos que já receberam votos. A nota multicast usa o grupo `239.10.10.20:7101`; clientes associados ao grupo recebem as notas em tempo real.

## Execução em redes locais

Os endereços multicast são fixos no código. `MULTICAST_INTERFACE` escolhe a interface local; o padrão `0.0.0.0` deixa a seleção ao sistema operacional. Multicast pode ser filtrado por firewall, roteador, VPN ou configuração da interface. Para a demonstração local, use `127.0.0.1`; entre máquinas, configure o IP da interface de rede em cada processo e altere `HOST` no cliente para o endereço do servidor. As credenciais, candidatos e votos ficam apenas em memória e são reinicializados quando o servidor reinicia.

## Testes existentes

Os testes presentes no repositório cobrem as questões 1–3:

```bash
python3 -m unittest discover -s testes -t . -v
python3 -m testes.tcp_integracao
```

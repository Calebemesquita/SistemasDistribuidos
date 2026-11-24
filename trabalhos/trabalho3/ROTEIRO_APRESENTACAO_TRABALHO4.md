# Roteiro de apresentação — Trabalho 4: Comunicação Indireta

**Duração:** 5 minutos  
**Abordagem:** publicar-assinar (Publish-Subscribe) com RabbitMQ  
**Escopo deste roteiro:** demonstração do mecanismo de notificações em `notifications/` e `protocol/`. Os comandos não iniciam nem usam `api/`.

## Preparação antes da apresentação

Faça esta preparação antes de começar a contar os cinco minutos:

1. Deixe o RabbitMQ em execução e acessível em `127.0.0.1:5672`.
2. Na raiz do projeto, instale as dependências:

   ```sh
   cd trabalhos/trabalho3
   uv sync
   ```

3. Abra quatro terminais nessa pasta: dois para os listeners `ana` e `bruno`, um para publicar eventos e um para o listener `carla`.

O projeto não inicia o RabbitMQ automaticamente. Se o broker não estiver ativo, os listeners e o publicador não conseguirão conectar.

## Roteiro falado e demonstração

### 0:00–0:30 — Apresentar o projeto

> “Nosso projeto é um sistema de biblioteca, com eventos como empréstimos e atualizações do acervo. Neste trabalho, mostramos como esses eventos podem ser distribuídos sem o produtor precisar conhecer cada consumidor. Para deixar essa comunicação indireta visível, a demonstração usa o módulo de notificações e o RabbitMQ.”

### 0:30–1:20 — Explicar os conceitos

> “Na comunicação direta, o remetente precisa endereçar o destinatário. Na comunicação indireta, ele publica um evento para um intermediário. Escolhemos Publish-Subscribe: o produtor publica, e os assinantes recebem os eventos de interesse. Isso reduz o acoplamento espacial: o produtor conhece o broker, mas não precisa saber o IP ou a porta dos consumidores. Com filas duráveis e mensagens persistentes, também podemos manter eventos para um consumidor que fique temporariamente offline, desde que sua fila já exista.”

### 1:20–2:15 — Mostrar a arquitetura

> “O publicador chama `notifications.publisher` e envia a notificação para o exchange `biblioteca.alertas`. Por ser `fanout`, o exchange encaminha uma cópia para cada fila vinculada, como `alertas.ana` e `alertas.bruno`. Cada listener lê sua fila. O publicador conhece o broker, mas não os endereços nem a quantidade de consumidores.”

### 2:15–3:10 — Explicar as decisões e os limites

> “Usamos um exchange do tipo `fanout`, chamado `biblioteca.alertas`, porque o evento deve ser copiado para as filas assinadas, sem depender de uma chave de roteamento. Cada usuário tem uma fila durável, como `alertas.ana`. O exchange e as filas são duráveis, e o produtor envia mensagens persistentes. O consumidor confirma cada mensagem com ACK depois de processá-la.”

### 3:10–4:40 — Executar a demonstração

#### 1. Iniciar dois consumidores

No **Terminal 1**:

```sh
uv run python -m notifications.listener ana
```

No **Terminal 2**:

```sh
uv run python -m notifications.listener bruno
```

Espere os dois terminais mostrarem que estão ouvindo suas filas.

#### 2. Publicar um evento e mostrar a distribuição

No **Terminal 3**, publique um evento de demonstração chamando diretamente o publicador do projeto:

```sh
uv run python -c 'from notifications.publisher import publish_notification; from protocol.notification import Notification; from protocol.notification_type import NotificationType; publish_notification(Notification(NotificationType.ALERT, "Empréstimo de demonstração: O Pequeno Príncipe"))'
```

Mostre que o mesmo evento aparece nos terminais de `ana` e `bruno`.

> “O produtor publicou uma única vez no exchange. Como ele é `fanout`, o RabbitMQ encaminhou uma cópia para cada fila vinculada. O produtor não precisou abrir uma conexão com cada consumidor.”

#### 3. Mostrar entrega após o consumidor voltar

No **Terminal 4**, inicie o listener de `carla`:

```sh
uv run python -m notifications.listener carla
```

Espere aparecer `Ouvindo alertas.carla` e pressione `Ctrl+C`. A fila foi criada e é durável; o consumidor agora está offline.

Publique outro evento no **Terminal 3**:

```sh
uv run python -c 'from notifications.publisher import publish_notification; from protocol.notification import Notification; from protocol.notification_type import NotificationType; publish_notification(Notification(NotificationType.UPDATE, "Aviso publicado enquanto Carla está offline"))'
```

Os listeners que continuaram ativos recebem o evento imediatamente. Depois, reinicie o listener de `carla`:

```sh
uv run python -m notifications.listener carla
```

Mostre o aviso pendente sendo entregue à Carla.

> “A fila de Carla já existia quando o evento foi publicado. Por isso, o RabbitMQ pôde mantê-lo enquanto o consumidor estava offline e entregá-lo quando voltou.”

### 4:40–5:00 — Fechar com resultado e limite

> “Vimos o desacoplamento espacial: o publicador conhece o broker, não os consumidores. Também vimos a entrega posterior, desde que a fila durável já exista. Isso reduz o acoplamento direto, mas exige manter o broker e gerenciar as filas.”

Encerre os listeners com `Ctrl+C`.

## Conceitos teóricos em uma frase

| Conceito | Como aparece na demonstração |
| --- | --- |
| Comunicação indireta | O produtor publica no RabbitMQ, que encaminha os eventos aos consumidores. |
| Publish-Subscribe | Um produtor publica eventos; filas assinadas recebem cópias do evento. |
| Desacoplamento espacial | O produtor não configura o endereço de cada consumidor. |
| Desacoplamento temporal | Uma fila durável existente pode guardar mensagens para um consumidor offline. |
| Exchange `fanout` | Distribui cada publicação às filas vinculadas, sem filtrar por chave. |
| ACK | Confirma ao broker que o consumidor processou a mensagem. |

## Arquivos para apontar durante a explicação

- `notifications/publisher.py`: declara o exchange e publica a mensagem persistente.
- `notifications/listener.py`: cria e vincula a fila durável e confirma mensagens com ACK.
- `notifications/config.py`: define o nome do exchange e o endereço do RabbitMQ.
- `protocol/notification.py`: serializa e desserializa o evento.

## Observação para a demonstração

O comando de publicação acima gera um evento de exemplo chamando o mesmo módulo `notifications.publisher` usado pelo sistema. Isso permite demonstrar o broker e os consumidores sem executar `api/`. A fila de um consumidor precisa ter sido criada antes da publicação para que ela retenha mensagens durante a ausência desse consumidor.

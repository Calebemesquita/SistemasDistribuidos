# Roteiro de comandos — apresentação do Trabalho 4

Guia operacional para preparar e executar a demonstração de Publish-Subscribe com RabbitMQ. A demonstração usa `notifications/` e `protocol/`; não inicia nem usa `api/`.

## 1. Preparar o projeto antes da apresentação

Abra um terminal na raiz do repositório:

```sh
cd /home/arkj/CC/VI/SD/trabalhos/code/trabalhos/trabalho3
uv sync
```

Deixe o broker e as dependências prontos antes de começar a contar os cinco minutos.

## 2. Iniciar o RabbitMQ com Podman

Este projeto conecta-se a `127.0.0.1:5672` usando as credenciais padrão do Pika (`guest/guest`). A porta abaixo fica publicada somente no próprio computador.

### Se o container já existe

Confira seu estado:

```sh
podman ps -a --filter name=rabbitmq-trabalho4
```

Se estiver parado, inicie-o:

```sh
podman start rabbitmq-trabalho4
```

Se estiver em execução, não precisa iniciá-lo novamente.

### Se o container ainda não existe

Crie a configuração local que permite ao cliente do host conectar com o usuário padrão através da rede do container:

```sh
cat > /tmp/rabbitmq-trabalho4.conf <<'EOF'
loopback_users = none
EOF
```

Crie e inicie o container:

```sh
podman run -d \
  --name rabbitmq-trabalho4 \
  -p 127.0.0.1:5672:5672 \
  -v /tmp/rabbitmq-trabalho4.conf:/etc/rabbitmq/rabbitmq.conf:ro \
  docker.io/rabbitmq:4-management
```

O arquivo de configuração relaxa a regra de loopback do usuário `guest` dentro do broker. Use esta configuração somente para a demonstração local; o acesso publicado pelo Podman fica limitado a `127.0.0.1`.

### Esperar o broker e confirmar a conexão

Veja os logs até aparecer `Server startup complete`:

```sh
podman logs --tail 30 rabbitmq-trabalho4
```

Confirme que a porta está acessível:

```sh
nc -vz 127.0.0.1 5672
```

Confirme a conexão AMQP com a mesma biblioteca usada pelo projeto:

```sh
uv run python -c 'import pika; connection = pika.BlockingConnection(pika.ConnectionParameters(host="127.0.0.1", port=5672)); print("Conexão AMQP confirmada"); connection.close()'
```

O último comando deve imprimir `Conexão AMQP confirmada`. Se aparecer `AMQPConnectionError`, confira se o container está em execução e se os logs indicam que o servidor terminou de iniciar.

## 3. Abrir os terminais da demonstração

Abra quatro terminais, todos na pasta do projeto:

```sh
cd /home/arkj/CC/VI/SD/trabalhos/code/trabalhos/trabalho3
```

- **Terminal 1:** listener de Ana.
- **Terminal 2:** listener de Bruno.
- **Terminal 3:** publicador de eventos.
- **Terminal 4:** listener de Carla, usado no teste de consumidor offline.

Deixe os comandos de publicação prontos para colar no Terminal 3. Isso evita perder tempo digitando durante a apresentação.

## 4. Execução ao vivo — cinco minutos

### 0:00–0:30 — Apresentar o projeto

Sem comando: explique que o projeto de biblioteca distribui notificações de forma indireta.

### 0:30–1:20 — Explicar os conceitos

Sem comando: apresente Publish-Subscribe, broker e desacoplamento espacial e temporal.

### 1:20–2:15 — Mostrar a arquitetura

Sem comando: explique o fluxo `publicador → exchange biblioteca.alertas → filas dos assinantes → listeners`.

### 2:15–3:10 — Explicar as decisões

Sem comando: explique `fanout`, filas duráveis, mensagens persistentes e ACK. Diga que a fila precisa existir antes da publicação para reter mensagens durante a ausência do consumidor.

### 3:10–4:40 — Demonstrar a execução

#### Iniciar Ana e Bruno

No **Terminal 1**:

```sh
uv run python -m notifications.listener ana
```

No **Terminal 2**:

```sh
uv run python -m notifications.listener bruno
```

Espere os dois terminais exibirem `Ouvindo alertas...`. Isso confirma que as filas dos dois assinantes foram criadas e vinculadas.

#### Publicar um evento para os dois assinantes

No **Terminal 3**:

```sh
uv run python -c 'from notifications.publisher import publish_notification; from protocol.notification import Notification; from protocol.notification_type import NotificationType; publish_notification(Notification(NotificationType.ALERT, "Empréstimo de demonstração: O Pequeno Príncipe"))'
```

Mostre a mesma notificação nos terminais de Ana e Bruno. Explique que cada um recebe sua cópia porque tem uma fila diferente vinculada ao exchange `fanout`.

#### Publicar enquanto Carla está offline

No **Terminal 4**, crie primeiro a fila de Carla:

```sh
uv run python -m notifications.listener carla
```

Espere `Ouvindo alertas.carla` e pressione `Ctrl+C`. Isso encerra o processo listener, mas mantém a fila durável no RabbitMQ.

No **Terminal 3**, publique enquanto Carla está offline:

```sh
uv run python -c 'from notifications.publisher import publish_notification; from protocol.notification import Notification; from protocol.notification_type import NotificationType; publish_notification(Notification(NotificationType.UPDATE, "Aviso publicado enquanto Carla está offline"))'
```

Ana e Bruno devem receber a atualização imediatamente. Reinicie o listener de Carla no **Terminal 4**:

```sh
uv run python -m notifications.listener carla
```

Mostre a mensagem pendente sendo entregue. A fila de Carla já existia quando o evento foi publicado.

### 4:40–5:00 — Concluir

Sem comando: recapitule o desacoplamento espacial e a entrega posterior condicionada à existência da fila durável.

## 5. Encerrar depois da apresentação

Encerre cada listener com `Ctrl+C`. Depois pare o broker:

```sh
podman stop rabbitmq-trabalho4
```

Para usá-lo novamente:

```sh
podman start rabbitmq-trabalho4
```

## Observações importantes

- Os comandos publicam uma notificação de demonstração chamando diretamente `notifications.publisher`; não registram um empréstimo real.
- A fila precisa ser criada e vinculada antes para reter uma mensagem enquanto o consumidor está offline. Um assinante que nunca criou a fila não recebe mensagens anteriores.
- Use nomes de usuário diferentes para demonstrar cópias independentes. Consumidores com o mesmo nome compartilham uma fila e dividem as mensagens.
- Se o broker não estiver disponível em `127.0.0.1:5672`, o listener retorna `AMQPConnectionError`. `uv sync` instala dependências Python, mas não inicia o RabbitMQ.
- Esta demonstração é local e não configura redundância ou alta disponibilidade do broker.

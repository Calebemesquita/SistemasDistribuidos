# Roteiro de comandos — apresentação do Trabalho 4

Este roteiro usa três projetos separados. Para executar em computadores
diferentes, substitua `HOST_DO_SERVIDOR` pelo IP do computador com a API e
configure um RabbitMQ acessível pelo servidor e pelos assinantes.

## Preparar o servidor

No computador servidor, inicie um RabbitMQ e configure as credenciais de
`RABBITMQ_USERNAME` e `RABBITMQ_PASSWORD`. Para teste local, o projeto usa
`guest/guest` em `127.0.0.1:5672` por padrão. Em seguida:

```sh
cd trabalhos/trabalho4/servidor
uv sync
RABBITMQ_HOST=HOST_DO_BROKER RABBITMQ_USERNAME=USUARIO RABBITMQ_PASSWORD=SENHA uv run uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Em uma configuração local com broker no mesmo computador, pode-se omitir
`RABBITMQ_HOST`. Confirme a API em `http://HOST_DO_SERVIDOR:8000/docs`.

Em uso remoto, RabbitMQ exige uma conta própria (o usuário `guest` só aceita
conexões locais por padrão). Crie a conta no broker com `rabbitmqctl` e
configure as mesmas credenciais na API e nos assinantes.

## Iniciar o cliente Java

Em outro terminal ou computador:

```sh
cd trabalhos/trabalho4/cliente_java
javac Client.java
java Client http://HOST_DO_SERVIDOR:8000 ana
```

## Iniciar o cliente Node.js

Em outro terminal ou computador, com `HOST_DO_BROKER` acessível:

```sh
cd trabalhos/trabalho4/cliente_node
npm install
RABBITMQ_URL=amqp://USUARIO:SENHA@HOST_DO_BROKER:5672 npm start -- http://HOST_DO_SERVIDOR:8000 bruno
```

No menu, escolha a opção **8** para assinar notificações. Deixe esse cliente
aberto durante o empréstimo ou devolução feito pelo cliente Java.

## Testar o canal HTTP em duas máquinas

Em outro computador, inicie a CLI Python apontando para o IP LAN do servidor:

```sh
cd trabalhos/trabalho4/cliente_cli
python3 client.py --url http://HOST_DO_SERVIDOR:8000 --username ana
```

Escolha **9** para inscrever `ana`; em uma segunda CLI ou no cliente Java/Node,
cadastre um livro ou solicite empréstimo. Escolha **10** na CLI de `ana` para
ver os eventos e o cursor. A assinatura HTTP não precisa de RabbitMQ no cliente;
o broker permanece necessário para publicações feitas pelo servidor.

## Sequência da demonstração

1. No cliente Node.js, inicie a escuta.
2. No cliente Java, liste os livros e solicite um empréstimo.
3. Mostre a resposta da API e a notificação recebida no Node.js.
4. Consulte os empréstimos no cliente Node.js e devolva o livro.
5. Mostre a notificação da devolução e cancele a assinatura com a opção **9**.

## Encerrar

Encerre os clientes pelos respectivos menus e pare o servidor com `Ctrl+C`.
Se o RabbitMQ for um container iniciado para a apresentação, pare-o com o
comando correspondente ao runtime usado.

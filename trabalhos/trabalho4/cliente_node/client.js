const amqp = require("amqplib");
const readline = require("node:readline/promises");

const apiUrl = (
  process.env.API_URL || process.argv[2] || "http://127.0.0.1:8000"
).replace(/\/+$/, "");
const username = process.env.LIBRARY_USERNAME || process.argv[3] || "node";
const rabbitmqUrl = process.env.RABBITMQ_URL || "amqp://127.0.0.1:5672";
const exchangeName = "biblioteca.alertas";

const input = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

let rabbitConnection;
let rabbitChannel;
let consumerTag;
let notificationQueue;

async function showResponse(response) {
  const body = await response.text();
  let formattedBody = body;

  try {
    formattedBody = JSON.stringify(JSON.parse(body), null, 2);
  } catch {
    // Mantém o corpo original quando a resposta não for JSON.
  }

  console.log(`HTTP ${response.status}`);
  if (formattedBody) {
    console.log(formattedBody);
  }
}

async function listBooks() {
  try {
    const response = await fetch(`${apiUrl}/books/`, {
      signal: AbortSignal.timeout(5000),
    });
    await showResponse(response);
  } catch (error) {
    console.log(`Não consegui acessar a API: ${error.message}`);
  }
}

async function requestLoan() {
  const answer = (await input.question("ID do livro: ")).trim();
  const bookId = Number(answer);

  if (!Number.isInteger(bookId) || bookId < 1) {
    console.log("Digite um ID inteiro positivo.");
    return;
  }

  try {
    await postJson(`${apiUrl}/loans/`, { book_id: bookId, username });
  } catch (error) {
    console.log(`Não consegui acessar a API: ${error.message}`);
  }
}

async function postJson(url, value) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(value),
    signal: AbortSignal.timeout(5000),
  });
  await showResponse(response);
}

async function createBook() {
  const title = (await input.question("Título: ")).trim();
  const author = (await input.question("Autor: ")).trim();
  try {
    await postJson(`${apiUrl}/books/`, {
      title,
      author,
      librarian_id: username,
      librarian_name: username,
    });
  } catch (error) {
    console.log(`Não consegui acessar a API: ${error.message}`);
  }
}

async function listLoans() {
  try {
    const response = await fetch(`${apiUrl}/loans/`, {
      signal: AbortSignal.timeout(5000),
    });
    await showResponse(response);
  } catch (error) {
    console.log(`Não consegui acessar a API: ${error.message}`);
  }
}

async function returnBook() {
  const answer = (await input.question("ID do empréstimo: ")).trim();
  const loanId = Number(answer);
  if (!Number.isInteger(loanId) || loanId < 1) {
    console.log("Digite um ID inteiro positivo.");
    return;
  }

  try {
    await postJson(`${apiUrl}/loans/${loanId}/return`, {});
  } catch (error) {
    console.log(`Não consegui acessar a API: ${error.message}`);
  }
}

async function listNotifications() {
  try {
    const response = await fetch(`${apiUrl}/notifications/`, {
      signal: AbortSignal.timeout(5000),
    });
    await showResponse(response);
  } catch (error) {
    console.log(`Não consegui acessar a API: ${error.message}`);
  }
}

async function publishNotification() {
  const content = (await input.question("Mensagem: ")).trim();
  try {
    await postJson(`${apiUrl}/notifications/`, {
      type: "NOTIFICAÇÃO",
      content,
    });
  } catch (error) {
    console.log(`Não consegui acessar a API: ${error.message}`);
  }
}

function displayNotification(channel, message) {
  try {
    const notification = JSON.parse(message.content.toString("utf8"));
    const timestamp = Number(notification.timestamp);
    const date = Number.isFinite(timestamp)
      ? new Date(timestamp * 1000).toLocaleString()
      : "data desconhecida";

    console.log(
      `\n[${username}] ${notification.type} - ${notification.content} (${date})`,
    );
  } catch (error) {
    console.log(`\nNotificação inválida recebida: ${error.message}`);
  } finally {
    try {
      channel.ack(message);
    } catch {
      // O canal pode ter sido encerrado enquanto a mensagem era processada.
    }
  }
}

async function startNotificationListener() {
  if (rabbitConnection) {
    console.log("A escuta de notificações já está ativa.");
    return;
  }
  if (!username.trim()) {
    console.log("O nome de usuário não pode ficar vazio.");
    return;
  }

  try {
    const connection = await amqp.connect(rabbitmqUrl);
    rabbitConnection = connection;
    const channel = await connection.createChannel();
    rabbitChannel = channel;

    const queueName = `alertas.${username}`;
    notificationQueue = queueName;
    await channel.assertExchange(exchangeName, "fanout", {
      durable: true,
    });
    await channel.assertQueue(queueName, { durable: true });
    await channel.bindQueue(queueName, exchangeName, "");

    const result = await channel.consume(
      queueName,
      (message) => {
        if (message) {
          displayNotification(channel, message);
        }
      },
      { noAck: false },
    );
    consumerTag = result.consumerTag;

    connection.on("error", (error) => {
      console.log(`\nConexão RabbitMQ: ${error.message}`);
    });
    channel.on("error", (error) => {
      console.log(`\nCanal RabbitMQ: ${error.message}`);
    });
    connection.on("close", () => {
      if (rabbitConnection !== connection) {
        return;
      }
      rabbitConnection = undefined;
      rabbitChannel = undefined;
      consumerTag = undefined;
      notificationQueue = undefined;
      console.log("\nConexão com RabbitMQ encerrada pelo broker.");
    });

    console.log(`Ouvindo notificações em ${queueName}.`);
  } catch (error) {
    await stopNotificationListener();
    console.log(`Não consegui conectar ao RabbitMQ: ${error.message}`);
  }
}

async function stopNotificationListener() {
  const channel = rabbitChannel;
  const connection = rabbitConnection;
  const tag = consumerTag;
  const queueName = notificationQueue;

  rabbitChannel = undefined;
  rabbitConnection = undefined;
  consumerTag = undefined;
  notificationQueue = undefined;

  try {
    if (channel && tag) {
      await channel.cancel(tag);
    }
    if (channel && queueName) {
      await channel.unbindQueue(queueName, exchangeName, "");
    }
    if (channel) {
      await channel.close();
    }
  } catch {
    // A conexão pode já ter sido encerrada pelo broker.
  }

  try {
    if (connection) {
      await connection.close();
    }
  } catch {
    // A conexão pode já ter sido encerrada pelo broker.
  }
}

async function main() {
  console.log(`API: ${apiUrl} | usuário: ${username}`);

  try {
    while (true) {
      console.log("\n=== BIBLIOTECA (Node.js) ===");
      console.log("1. Listar livros");
      console.log("2. Cadastrar livro");
      console.log("3. Solicitar empréstimo");
      console.log("4. Listar empréstimos");
      console.log("5. Devolver livro");
      console.log("6. Listar notificações");
      console.log("7. Publicar notificação");
      console.log("8. Ouvir notificações");
      console.log("9. Cancelar inscrição de notificações");
      console.log("0. Sair");

      const choice = (await input.question("Escolha: ")).trim();
      switch (choice) {
        case "1":
          await listBooks();
          break;
        case "2":
          await createBook();
          break;
        case "3":
          await requestLoan();
          break;
        case "4":
          await listLoans();
          break;
        case "5":
          await returnBook();
          break;
        case "6":
          await listNotifications();
          break;
        case "7":
          await publishNotification();
          break;
        case "8":
          await startNotificationListener();
          break;
        case "9":
          await stopNotificationListener();
          console.log("Inscrição de notificações cancelada.");
          break;
        case "0":
          return;
        default:
          console.log("Opção inválida.");
      }
    }
  } finally {
    await stopNotificationListener();
    input.close();
  }
}

main().catch((error) => {
  console.error(`Erro no cliente: ${error.message}`);
  process.exitCode = 1;
});

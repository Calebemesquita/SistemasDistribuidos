import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Scanner;

public class Client {
    private static final HttpClient HTTP = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_1_1)
            .connectTimeout(Duration.ofSeconds(5))
            .build();

    public static void main(String[] args) throws InterruptedException {
        String api = (args.length > 0 ? args[0] : "http://127.0.0.1:8000")
                .replaceAll("/+$", "");
        String username = args.length > 1 ? args[1] : "java";

        try (Scanner scan = new Scanner(System.in)) {
            while (true) {
                System.out.println("\n=== BIBLIOTECA ===");
                System.out.println("1. Listar livros");
                System.out.println("2. Cadastrar livro");
                System.out.println("3. Solicitar empréstimo");
                System.out.println("4. Listar empréstimos");
                System.out.println("5. Devolver livro");
                System.out.println("6. Listar notificações");
                System.out.println("7. Publicar notificação");
                System.out.println("0. Sair");
                System.out.print("Escolha: ");

                try {
                    switch (scan.nextLine().trim()) {
                        case "1":
                            listBooks(api);
                            break;
                        case "2":
                            System.out.print("Título: ");
                            String title = scan.nextLine().trim();
                            System.out.print("Autor: ");
                            String author = scan.nextLine().trim();
                            createBook(api, title, author, username);
                            break;
                        case "3":
                            System.out.print("ID do livro: ");
                            int id = Integer.parseInt(scan.nextLine().trim());
                            loanBook(api, id, username);
                            break;
                        case "4":
                            listLoans(api);
                            break;
                        case "5":
                            System.out.print("ID do empréstimo: ");
                            int loanId = Integer.parseInt(scan.nextLine().trim());
                            returnBook(api, loanId);
                            break;
                        case "6":
                            listNotifications(api);
                            break;
                        case "7":
                            System.out.print("Mensagem: ");
                            publishNotification(api, scan.nextLine().trim());
                            break;
                        case "0":
                            return;
                        default:
                            System.out.println("Opção inválida.");
                    }
                } catch (NumberFormatException e) {
                    System.out.println("Digite um ID inteiro.");
                } catch (IOException e) {
                    System.out.println("Não consegui acessar a API: " + e);
                }
            }
        }
    }

    private static void listBooks(String api)
            throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(api + "/books/"))
                .timeout(Duration.ofSeconds(5))
                .GET()
                .build();

        send(request);
    }

    private static void loanBook(String api, int id, String username)
            throws IOException, InterruptedException {
        String json = String.format(
                "{\"book_id\":%d,\"username\":\"%s\"}",
                id,
                escapeJson(username));

        sendJson(api + "/loans/", json);
    }

    private static void createBook(
            String api, String title, String author, String librarianId)
            throws IOException, InterruptedException {
        String json = String.format(
                "{\"title\":\"%s\",\"author\":\"%s\","
                        + "\"librarian_id\":\"%s\",\"librarian_name\":\"%s\"}",
                escapeJson(title),
                escapeJson(author),
                escapeJson(librarianId),
                escapeJson(librarianId));
        sendJson(api + "/books/", json);
    }

    private static void returnBook(String api, int loanId)
            throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(api + "/loans/" + loanId + "/return"))
                .timeout(Duration.ofSeconds(5))
                .POST(HttpRequest.BodyPublishers.noBody())
                .build();
        send(request);
    }

    private static void listLoans(String api)
            throws IOException, InterruptedException {
        sendGet(api + "/loans/");
    }

    private static void listNotifications(String api)
            throws IOException, InterruptedException {
        sendGet(api + "/notifications/");
    }

    private static void publishNotification(String api, String content)
            throws IOException, InterruptedException {
        sendJson(api + "/notifications/", String.format(
                "{\"type\":\"NOTIFICAÇÃO\",\"content\":\"%s\"}",
                escapeJson(content)));
    }

    private static void sendJson(String url, String json)
            throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .timeout(Duration.ofSeconds(5))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .build();
        send(request);
    }

    private static void sendGet(String url)
            throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .timeout(Duration.ofSeconds(5))
                .GET()
                .build();
        send(request);
    }

    private static String escapeJson(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private static void send(HttpRequest request)
            throws IOException, InterruptedException {
        HttpResponse<String> resposta = HTTP.send(
                request, HttpResponse.BodyHandlers.ofString());

        System.out.println("HTTP " + resposta.statusCode());
        System.out.println(resposta.body());
    }
}

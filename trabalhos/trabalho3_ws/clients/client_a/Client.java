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
        String api = args.length > 0 ? args[0] : "http://127.0.0.1:8000";

        try (Scanner scan = new Scanner(System.in)) {
            while (true) {
                System.out.println("\n=== BIBLIOTECA ===");
                System.out.println("1. Listar livros");
                System.out.println("2. Solicitar empréstimo");
                System.out.println("0. Sair");
                System.out.print("Escolha: ");

                try {
                    switch (scan.nextLine().trim()) {
                        case "1":
                            listBooks(api);
                            break;
                        case "2":
                            System.out.print("ID do livro: ");
                            int id = Integer.parseInt(scan.nextLine().trim());
                            loanBook(api, id);
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

    private static void loanBook(String api, int id)
            throws IOException, InterruptedException {
        String json = String.format("{\"book_id\":%d,\"username\":\"ash\"}", id);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(api + "/loans/"))
                .timeout(Duration.ofSeconds(5))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .build();

        send(request);
    }

    private static void send(HttpRequest request)
            throws IOException, InterruptedException {
        HttpResponse<String> resposta = HTTP.send(
                request, HttpResponse.BodyHandlers.ofString());

        System.out.println("HTTP " + resposta.statusCode());
        System.out.println(resposta.body());
    }
}
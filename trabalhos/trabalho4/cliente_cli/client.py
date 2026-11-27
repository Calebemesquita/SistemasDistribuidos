"""Terminal client for exercising a running Trabalho 4 API over real HTTP."""

import argparse
import json
import os
import time
from urllib.parse import quote
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ApiError(RuntimeError):
    pass


class LibraryApiClient:
    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request(self, path: str, method: str = "GET", body: dict | None = None):
        encoded_body = None if body is None else json.dumps(body).encode("utf-8")
        headers = {} if encoded_body is None else {"Content-Type": "application/json"}
        request = Request(
            f"{self.base_url}{path}",
            data=encoded_body,
            headers=headers,
            method=method,
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                response_body = response.read().decode("utf-8")
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise ApiError(f"HTTP {error.code}: {detail}") from error
        except URLError as error:
            raise ApiError(f"Não consegui acessar {self.base_url}: {error.reason}") from error

        if not response_body:
            return None
        try:
            return json.loads(response_body)
        except json.JSONDecodeError as error:
            raise ApiError("A API respondeu com JSON inválido.") from error

    def list_books(self):
        return self.request("/books/")

    def create_book(self, title: str, author: str, librarian_id: str = "bibliotecario"):
        return self.request(
            "/books/",
            "POST",
            {
                "title": title,
                "author": author,
                "librarian_id": librarian_id,
                "librarian_name": librarian_id,
            },
        )

    def list_loans(self):
        return self.request("/loans/")

    def create_loan(self, book_id: int, username: str):
        return self.request(
            "/loans/",
            "POST",
            {"book_id": book_id, "username": username},
        )

    def return_loan(self, loan_id: int):
        return self.request(f"/loans/{loan_id}/return", "POST")

    def list_notifications(self):
        return self.request("/notifications/")

    def publish_notification(self, content: str, notification_type: str):
        return self.request(
            "/notifications/",
            "POST",
            {"content": content, "type": notification_type},
        )

    def list_users(self):
        return self.request("/users/")

    def subscribe(self, client_id: str, name: str):
        return self.request(
            "/notifications/subscriptions",
            "POST",
            {"client_id": client_id, "name": name},
        )

    def poll_notifications(self, client_id: str, after: int = 0):
        encoded_id = quote(client_id, safe="")
        return self.request(
            f"/notifications/subscriptions/{encoded_id}?after={after}"
        )

    def cancel_subscription(self, client_id: str):
        encoded_id = quote(client_id, safe="")
        return self.request(
            f"/notifications/subscriptions/{encoded_id}", "DELETE"
        )


class LibraryCLI:
    def __init__(self, client: LibraryApiClient, username: str) -> None:
        self.client = client
        self.username = username
        self.notification_cursor = 0

    def run(self) -> None:
        while True:
            print("\n=== Teste real da API da Biblioteca ===")
            print(f"API: {self.client.base_url} | usuário: {self.username}")
            print("1. Listar livros")
            print("2. Cadastrar livro")
            print("3. Solicitar empréstimo")
            print("4. Listar empréstimos")
            print("5. Devolver livro")
            print("6. Listar notificações")
            print("7. Publicar notificação")
            print("8. Listar usuários e papéis")
            print("9. Inscrever-se no canal HTTP")
            print("10. Consultar novas notificações")
            print("11. Cancelar inscrição HTTP")
            print("0. Sair")

            choice = input("Escolha: ").strip()
            try:
                if choice == "1":
                    self._show(self.client.list_books())
                elif choice == "2":
                    title = input("Título: ").strip()
                    author = input("Autor: ").strip()
                    self._show(
                        self.client.create_book(title, author, self.username)
                    )
                elif choice == "3":
                    book_id = self._read_id("ID do livro: ")
                    self._show(self.client.create_loan(book_id, self.username))
                elif choice == "4":
                    self._show(self.client.list_loans())
                elif choice == "5":
                    loan_id = self._read_id("ID do empréstimo: ")
                    self._show(self.client.return_loan(loan_id))
                elif choice == "6":
                    self._show(self.client.list_notifications())
                elif choice == "7":
                    content = input("Mensagem: ").strip()
                    notification_type = input(
                        "Tipo [NOTIFICAÇÃO/ALERTA/ATUALIZAÇÃO]: "
                    ).strip().upper() or "NOTIFICAÇÃO"
                    self._show(
                        self.client.publish_notification(content, notification_type)
                    )
                elif choice == "8":
                    self._show(self.client.list_users())
                elif choice == "9":
                    self._show(self.client.subscribe(self.username, self.username))
                    self.notification_cursor = 0
                elif choice == "10":
                    result = self.client.poll_notifications(
                        self.username,
                        self.notification_cursor,
                    )
                    self.notification_cursor = result["cursor"]
                    self._show(result)
                elif choice == "11":
                    self._show(self.client.cancel_subscription(self.username))
                elif choice == "0":
                    return
                else:
                    print("Opção inválida.")
            except (ApiError, ValueError) as error:
                print(f"Erro: {error}")

    @staticmethod
    def _read_id(prompt: str) -> int:
        value = int(input(prompt).strip())
        if value < 1:
            raise ValueError("O ID deve ser positivo.")
        return value

    @staticmethod
    def _show(value) -> None:
        print(json.dumps(value, ensure_ascii=False, indent=2))


def smoke_test(client: LibraryApiClient, username: str) -> None:
    """Run a real user/catalog/loan/subscription flow against the API."""
    client.subscribe(username, username)
    librarian_id = f"{username}-bibliotecario"
    book = client.create_book(
        title=f"Smoke test {time.time_ns()}",
        author="Cliente CLI",
        librarian_id=librarian_id,
    )
    loan = client.create_loan(book["id"], username)
    if loan["book_id"] != book["id"] or loan["returned"]:
        raise ApiError("A API retornou um empréstimo inesperado.")

    returned_loan = client.return_loan(loan["id"])
    if not returned_loan["returned"]:
        raise ApiError("A API não registrou a devolução.")

    book_after_return = next(
        current
        for current in client.list_books()
        if current["id"] == book["id"]
    )
    if not book_after_return["available"]:
        raise ApiError("O livro continuou indisponível após a devolução.")

    polled = client.poll_notifications(username, 0)
    recent_messages = [event["content"] for event in polled["events"]]
    if not any(f"{username} solicitou" in message for message in recent_messages):
        raise ApiError("O alerta de empréstimo não chegou ao assinante HTTP.")
    if not any(f"{username} devolveu" in message for message in recent_messages):
        raise ApiError("A atualização de devolução não chegou ao assinante HTTP.")
    users = client.list_users()
    if not any(user["id"] == username and user["role"] == "leitor" for user in users):
        raise ApiError("O papel de Leitor não foi registrado no domínio.")
    if not any(
        user["id"] == librarian_id and user["role"] == "bibliotecario"
        for user in users
    ):
        raise ApiError("O papel de Bibliotecário não foi registrado no domínio.")
    client.cancel_subscription(username)

    print("Smoke test HTTP concluído:")
    print(f"  livro de teste #{book['id']} cadastrado, emprestado e devolvido")
    print(f"  empréstimo #{loan['id']} marcado como devolvido")
    print(f"  {len(polled['events'])} eventos entregues pelo canal HTTP")
    print("  usuário Leitor, Bibliotecário e inscrição também foram verificados")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CLI para testar a API real do Trabalho 4."
    )
    parser.add_argument(
        "--url",
        default=os.getenv("API_URL", "http://127.0.0.1:8000"),
        help="URL base da API (padrão: API_URL ou localhost:8000)",
    )
    parser.add_argument(
        "--username",
        default=os.getenv("LIBRARY_USERNAME", "cli"),
        help="Nome usado nos empréstimos",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="executa uma operação real de empréstimo e devolução",
    )
    args = parser.parse_args()
    client = LibraryApiClient(args.url)

    try:
        if args.smoke_test:
            smoke_test(client, args.username)
        else:
            LibraryCLI(client, args.username).run()
    except ApiError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()

"""HTTP adapter over the Trabalho 2 Biblioteca aggregate."""

from biblioteca_rpc.entities import Bibliotecario, Biblioteca, Livro, serializar


class BookService:
    def __init__(self, library: Biblioteca) -> None:
        self.library = library
        self._pending_librarians: dict[int, str | None] = {}

    @staticmethod
    def _to_http(book: Livro) -> dict:
        data = serializar(book)
        return {
            "id": int(data["isbn"]),
            "title": data["titulo"],
            "author": data["autor"],
            "available": data["disponivel"],
        }

    def list_books(self) -> list[dict]:
        return [self._to_http(book) for book in self.library.catalogo.livros.values()]

    def get_book(self, book_id: int) -> Livro | None:
        return self.library.catalogo.livros.get(str(book_id))

    def add_book(
        self,
        title: str,
        author: str,
        librarian_id: str = "bibliotecario",
        librarian_name: str = "Bibliotecário",
    ) -> dict:
        next_id = max((int(isbn) for isbn in self.library.catalogo.livros), default=0) + 1
        librarian_was_new = librarian_id not in self.library.usuarios
        librarian = Bibliotecario(librarian_id, librarian_name, librarian_id)
        book = self.library.cadastrar_livro(
            {"isbn": str(next_id), "titulo": title.strip(), "autor": author.strip()},
            bibliotecario=librarian,
        )
        self._pending_librarians[next_id] = librarian_id if librarian_was_new else None
        return {
            "id": int(book["isbn"]),
            "title": book["titulo"],
            "author": book["autor"],
            "available": book["disponivel"],
        }

    def rollback_created_book(self, book_id: int) -> None:
        self.library.remover_livro(str(book_id))
        librarian_id = self._pending_librarians.pop(book_id, None)
        if librarian_id is not None:
            librarian = self.library.usuarios.get(librarian_id)
            if isinstance(librarian, Bibliotecario):
                del self.library.usuarios[librarian_id]

    def commit_created_book(self, book_id: int) -> None:
        self._pending_librarians.pop(book_id, None)


__all__ = ["BookService"]

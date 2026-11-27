"""HTTP adapter over Trabalho 2 loan history and reader entities."""

from biblioteca_rpc.entities import Biblioteca, Leitor


class LoanService:
    def __init__(self, library: Biblioteca) -> None:
        self.library = library

    @staticmethod
    def _to_http(record: dict) -> dict:
        return {
            "id": record["id"],
            "book_id": int(record["isbn"]),
            "username": record["leitor_id"],
            "returned": record["returned"],
        }

    def list_loans(self) -> list[dict]:
        return [self._to_http(record) for record in self.library.listar_emprestimos()]

    def create_loan(self, book_id: int, username: str) -> dict:
        user_id = username.strip()
        if not user_id:
            raise ValueError("Username cannot be blank.")
        reader = self.library.usuarios.get(user_id)
        if reader is None:
            reader = Leitor(user_id, user_id)
        record = self.library.emprestar_livro(str(book_id), user_id, leitor=reader)
        return self._to_http(record)

    def get_loan(self, loan_id: int) -> dict | None:
        record = next(
            (item for item in self.library.historico.registros if item["id"] == loan_id),
            None,
        )
        return None if record is None else self._to_http(record)

    def return_loan(self, loan_id: int) -> dict:
        return self._to_http(self.library.devolver_emprestimo(loan_id))

    def rollback_created_loan(self, loan: dict) -> None:
        self.library.reverter_emprestimo(loan["id"])

    def rollback_returned_loan(self, loan: dict) -> None:
        self.library.reverter_devolucao(loan["id"])


__all__ = ["LoanService"]

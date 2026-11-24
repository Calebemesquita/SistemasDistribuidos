from dataclasses import dataclass


@dataclass
class Loan:
    id: int
    book_id: int
    username: str
    returned: bool = False
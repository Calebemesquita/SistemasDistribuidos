from dataclasses import dataclass


@dataclass
class Book:
    id: int
    title: str
    author: str
    available: bool = True


@dataclass
class Loan:
    id: int
    book_id: int
    username: str
    returned: bool = False

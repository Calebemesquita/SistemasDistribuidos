from pydantic import BaseModel, Field


class Loan(BaseModel):
    id: int
    book_id: int
    username: str = Field(...)
    returned: bool = False

class CreateLoanRequest(BaseModel):
    book_id: int
    username: str # até o momento só uma duplicação, sem necessidade de refatorar ainda
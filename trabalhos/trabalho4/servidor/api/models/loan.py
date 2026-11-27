from pydantic import BaseModel, ConfigDict, Field, field_validator


class LoanResponse(BaseModel):
    """HTTP representation of the shared domain Loan dataclass."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    username: str
    returned: bool = False

class CreateLoanRequest(BaseModel):
    book_id: int
    username: str = Field(..., min_length=1)

    @field_validator("username")
    @classmethod
    def username_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Username cannot be blank.")
        return value

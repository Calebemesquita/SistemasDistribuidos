from pydantic import BaseModel, ConfigDict, Field


class BookResponse(BaseModel):
    """HTTP representation of the shared domain Book dataclass."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=100)
    available: bool = True


class CreateBookRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=100)
    librarian_id: str = Field(default="bibliotecario", min_length=1)
    librarian_name: str = Field(default="Bibliotecário", min_length=1)

from pydantic import BaseModel, Field


class BookResponse(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=100)
    available: bool
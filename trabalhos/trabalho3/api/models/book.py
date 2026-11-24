from pydantic import BaseModel, Field


class Book(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=100)
    available: bool = Field(default=True)


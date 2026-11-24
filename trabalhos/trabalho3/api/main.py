from fastapi import FastAPI

from api.routers.book import router as book_router
from api.routers.loan import router as loan_router

app = FastAPI(
    title="Library API",
    summary="API for managing a library of books",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Francisco Emilson Santos Souza Filho e Calebe Mesquita da Silva",
        "url": "https://github.com/Calebemesquita/Sistemas-Distribuidos",
    }
)

app.include_router(book_router)
app.include_router(loan_router)

@app.get("/")
def read_root():
    return { "Hello": "World!" }
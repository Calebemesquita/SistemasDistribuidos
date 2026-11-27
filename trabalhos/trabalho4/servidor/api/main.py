from fastapi import FastAPI

from api.routers.book import router as book_router
from api.routers.loan import router as loan_router
from api.routers.notification import router as notification_router
from api.routers.user import router as user_router

app = FastAPI(
    title="API Distribuída da Biblioteca",
    summary="Catálogo, empréstimos e notificações por HTTP",
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
app.include_router(notification_router)
app.include_router(user_router)

@app.get("/")
def read_root():
    return {
        "servico": "Biblioteca API",
        "estado": "online",
        "documentacao": "/docs",
        "objetos_distribuidos": ["catalogo", "emprestimos", "notificacoes"],
    }


@app.get("/health", tags=["Sistema"])
def health_check():
    return {"status": "ok"}

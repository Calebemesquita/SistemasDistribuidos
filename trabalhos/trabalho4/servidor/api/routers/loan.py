from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status

from api.dependencies.services import get_loan_service, get_notification_service
from api.models.loan import CreateLoanRequest, LoanResponse
from api.services.loan_service import LoanService
from api.services.notification_service import NotificationService
from notifications.publisher import NotificationPublishError

router = APIRouter(prefix="/loans", tags=["Empréstimos"], responses={404: {"description": "Not found"}})

@router.get(
    path="/",
    response_model=list[LoanResponse],
    name="List all loans",
    description="Lista todos os empréstimos registrados",
    response_description="Lista de empréstimos retornada com sucesso",
    status_code=HTTPStatus.OK,
)
async def list_loans(
    loan_service: Annotated[LoanService, Depends(get_loan_service)],
) -> list[dict]:
    """Lista o histórico de empréstimos do agregado Biblioteca."""
    return loan_service.list_loans()


@router.post(
    path="/",
    response_model=LoanResponse,
    name="Create a new loan",
    description="Create a new loan for a book",
    response_description="Loan created successfully",
    status_code=HTTPStatus.CREATED,
)
def create_loan(
    loan_request: Annotated[
        CreateLoanRequest,
        Body(openapi_examples={
            "livro-1": {
                "summary": "Emprestar o livro 1",
                "value": {"book_id": 1, "username": "ash"},
            },
            "livro-2": {
                "summary": "Emprestar o livro 2",
                "value": {"book_id": 2, "username": "ash"},
            },
            "livro-3": {
                "summary": "Emprestar o livro 3",
                "value": {"book_id": 3, "username": "ash"},
            },
        }),
    ],
    loan_service: Annotated[LoanService, Depends(get_loan_service)],
    notification_service: Annotated[
        NotificationService,
        Depends(get_notification_service),
    ],
) -> dict:
    """Cria um empréstimo de livro."""

    with loan_service.library.transacao():
        try:
            created_loan = loan_service.create_loan(
                book_id=loan_request.book_id,
                username=loan_request.username,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        try:
            notification_service.publish_latest()
        except NotificationPublishError as exc:
            loan_service.rollback_created_loan(created_loan)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Empréstimo não registrado: serviço de notificações indisponível.",
            ) from exc

        return created_loan


@router.post(
    path="/{loan_id}/return",
    response_model=LoanResponse,
    name="Return a loan",
    description="Returns a borrowed book",
    status_code=HTTPStatus.OK,
)
def return_loan(
    loan_id: int,
    loan_service: Annotated[LoanService, Depends(get_loan_service)],
    notification_service: Annotated[NotificationService, Depends(get_notification_service)],
) -> dict:
    """Registra a devolução e publica uma notificação."""
    with loan_service.library.transacao():
        try:
            loan = loan_service.return_loan(loan_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        try:
            notification_service.publish_latest()
        except NotificationPublishError as exc:
            loan_service.rollback_returned_loan(loan)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Devolução não registrada: serviço de notificações indisponível.",
            ) from exc

        return loan

from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status

from api.dependencies.services import get_loan_service
from api.models.loan import CreateLoanRequest
from api.services.loan_service import Loan, LoanService
from notifications.publisher import NotificationPublishError, publish_notification
from protocol.notification import Notification
from protocol.notification_type import NotificationType

router = APIRouter(prefix="/loans", tags=["Empréstimos"], responses={404: {"description": "Not found"}})

@router.get(
    path="/",
    response_model=list[Loan],
    name="List all loans",
    description="Lista todos os empréstimos registrados",
    response_description="Lista de empréstimos retornada com sucesso",
    status_code=HTTPStatus.OK,
)
async def list_loans(
    loan_service: Annotated[LoanService, Depends(get_loan_service)],
) -> list[Loan]:
    """Lista todos os empréstimos."""
    return loan_service.list_items()


@router.post(
    path="/",
    response_model=Loan,
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
    loan_service: Annotated[LoanService, Depends(get_loan_service)]
) -> Loan:
    """Cria um empréstimo de livro."""

    loans = loan_service.list_items()
    next_id = max((loan.id for loan in loans), default=0) + 1 # não gosto muito dessa abordagem (O(n)), mas é um exemplo trivial
    loan = Loan(id=next_id, **loan_request.model_dump())

    try:
        created_loan = loan_service.create_item(loan)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    notification = Notification(
        type=NotificationType.NOTIFICATION,
        content=(
            f"{created_loan.username} solicitou o livro "
            f"#{created_loan.book_id}."
        ),
    )
    try:
        publish_notification(notification)
    except NotificationPublishError as exc:
        loan_service.rollback_created_item(created_loan)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Empréstimo não registrado: serviço de notificações indisponível.",
        ) from exc

    return created_loan
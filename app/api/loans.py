from fastapi import APIRouter, status

from app.api.dependencies import LoanServiceDep
from app.api.schemas import LoanCreate, LoanOut

router = APIRouter(tags=["loans"])


@router.post("/loans", status_code=status.HTTP_201_CREATED)
def borrow_book(payload: LoanCreate, service: LoanServiceDep) -> LoanOut:
    loan = service.borrow(book_id=payload.book_id, member_id=payload.member_id)
    return LoanOut.model_validate(loan)


@router.post("/books/{book_id}/return")
def return_book(book_id: int, service: LoanServiceDep) -> LoanOut:
    loan = service.return_book(book_id=book_id)
    return LoanOut.model_validate(loan)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    BookAlreadyBorrowedError,
    BookNotBorrowedError,
    BookNotFoundError,
    DomainError,
    LoanLimitReachedError,
    MemberNotFoundError,
)

STATUS_BY_ERROR: dict[type[DomainError], int] = {
    BookNotFoundError: 404,
    MemberNotFoundError: 404,
    BookAlreadyBorrowedError: 409,
    LoanLimitReachedError: 409,
    BookNotBorrowedError: 409,
}


def register_error_handlers(app: FastAPI) -> None:
    """Translate business errors into HTTP responses, in one place."""

    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        status_code = STATUS_BY_ERROR.get(type(exc), 400)
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

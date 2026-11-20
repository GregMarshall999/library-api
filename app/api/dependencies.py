from collections.abc import Generator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from app.config import get_settings
from app.repositories.interfaces import BookRepository, LoanRepository, MemberRepository
from app.repositories.sql import SqlBookRepository, SqlLoanRepository, SqlMemberRepository
from app.services.loan_service import LoanService


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_settings().database_url, pool_pre_ping=True)


def get_session() -> Generator[Session, None, None]:
    """One session (one transaction) per request: commit on success, roll back on error."""
    with Session(get_engine()) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


SessionDep = Annotated[Session, Depends(get_session)]


def get_book_repository(session: SessionDep) -> BookRepository:
    return SqlBookRepository(session)


def get_member_repository(session: SessionDep) -> MemberRepository:
    return SqlMemberRepository(session)


def get_loan_repository(session: SessionDep) -> LoanRepository:
    return SqlLoanRepository(session)


BookRepoDep = Annotated[BookRepository, Depends(get_book_repository)]
MemberRepoDep = Annotated[MemberRepository, Depends(get_member_repository)]
LoanRepoDep = Annotated[LoanRepository, Depends(get_loan_repository)]


def get_loan_service(books: BookRepoDep, members: MemberRepoDep, loans: LoanRepoDep) -> LoanService:
    return LoanService(books, members, loans)


LoanServiceDep = Annotated[LoanService, Depends(get_loan_service)]

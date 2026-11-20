from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.exceptions import BookAlreadyBorrowedError
from app.domain.models import Book, Loan, Member
from app.repositories.sql import SqlBookRepository, SqlLoanRepository, SqlMemberRepository
from app.services.loan_service import LoanService

pytestmark = pytest.mark.integration


def test_database_rejects_two_active_loans_for_the_same_book(
    db_session: Session, now: datetime
) -> None:
    book = SqlBookRepository(db_session).add(Book(title="Dune", author="Frank Herbert"))
    members = SqlMemberRepository(db_session)
    alice = members.add(Member(name="Alice", email="alice@example.com"))
    bob = members.add(Member(name="Bob", email="bob@example.com"))
    assert book.id is not None 
    assert alice.id is not None 
    assert bob.id is not None
    loans = SqlLoanRepository(db_session)
    loans.add(Loan(book_id=book.id, member_id=alice.id, borrowed_at=now))
    second_loan = Loan(book_id=book.id, member_id=bob.id, borrowed_at=now)

    with pytest.raises(IntegrityError):
        loans.add(second_loan)


def test_loan_service_works_unchanged_on_postgres(db_session: Session, now: datetime) -> None:
    books = SqlBookRepository(db_session)
    members = SqlMemberRepository(db_session)
    service = LoanService(books, members, SqlLoanRepository(db_session), clock=lambda: now)
    book = books.add(Book(title="Dune", author="Frank Herbert"))
    alice = members.add(Member(name="Alice", email="alice@example.com"))
    bob = members.add(Member(name="Bob", email="bob@example.com"))
    assert book.id is not None 
    assert alice.id is not None 
    assert bob.id is not None

    service.borrow(book_id=book.id, member_id=alice.id)
    with pytest.raises(BookAlreadyBorrowedError):
        service.borrow(book_id=book.id, member_id=bob.id)
    returned = service.return_book(book_id=book.id)
    loan = service.borrow(book_id=book.id, member_id=bob.id)

    assert returned.returned_at == now
    assert loan.member_id == bob.id
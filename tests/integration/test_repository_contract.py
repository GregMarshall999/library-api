from dataclasses import dataclass
from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from app.domain.models import Book, Loan, Member
from app.repositories.in_memory import (
    InMemoryBookRepository,
    InMemoryLoanRepository,
    InMemoryMemberRepository,
)
from app.repositories.interfaces import BookRepository, LoanRepository, MemberRepository
from app.repositories.sql import SqlBookRepository, SqlLoanRepository, SqlMemberRepository


@dataclass
class Repos:
    books: BookRepository
    members: MemberRepository
    loans: LoanRepository


@pytest.fixture(params=["memory", pytest.param("sql", marks=pytest.mark.integration)])
def repos(request: pytest.FixtureRequest) -> Repos:
    if request.param == "memory":
        return Repos(InMemoryBookRepository(), InMemoryMemberRepository(), InMemoryLoanRepository())
    session: Session = request.getfixturevalue("db_session")
    return Repos(
        SqlBookRepository(session), SqlMemberRepository(session), SqlLoanRepository(session)
    )


def _new_loan(repos: Repos, now: datetime) -> Loan:
    """Store a book, a member and an active loan between them."""
    book = repos.books.add(Book(title="Dune", author="Frank Herbert"))
    member = repos.members.add(Member(name="Alice", email="alice@example.com"))
    assert book.id is not None
    assert member.id is not None
    return repos.loans.add(Loan(book_id=book.id, member_id=member.id, borrowed_at=now))


# ---------- books & members ----------


def test_added_book_gets_an_id_and_can_be_read_back(repos: Repos) -> None:
    book = repos.books.add(Book(title="Dune", author="Frank Herbert"))

    assert book.id is not None
    assert repos.books.get(book.id) == book


def test_added_member_gets_an_id_and_can_be_read_back(repos: Repos) -> None:
    member = repos.members.add(Member(name="Alice", email="alice@example.com"))

    assert member.id is not None
    assert repos.members.get(member.id) == member


def test_unknown_ids_return_none(repos: Repos) -> None:
    assert repos.books.get(999_999) is None
    assert repos.members.get(999_999) is None


# ---------- loans ----------


def test_new_loan_is_active(repos: Repos, now: datetime) -> None:
    loan = _new_loan(repos, now)

    assert loan.id is not None
    assert repos.loans.get_active_for_book(loan.book_id) == loan
    assert repos.loans.count_active_for_member(loan.member_id) == 1


def test_updated_loan_is_no_longer_active(repos: Repos, now: datetime) -> None:
    loan = _new_loan(repos, now)

    loan.returned_at = now
    updated = repos.loans.update(loan)

    assert updated.returned_at == now
    assert repos.loans.get_active_for_book(loan.book_id) is None
    assert repos.loans.count_active_for_member(loan.member_id) == 0


def test_update_unknown_loan_raises(repos: Repos, now: datetime) -> None:
    loan = _new_loan(repos, now)
    loan.id = 999_999

    with pytest.raises(ValueError, match="999999"):
        repos.loans.update(loan)


def test_update_loan_without_id_raises(repos: Repos, now: datetime) -> None:
    loan = _new_loan(repos, now)
    loan.id = None

    with pytest.raises(ValueError):
        repos.loans.update(loan)


def test_returned_objects_are_copies(repos: Repos, now: datetime) -> None:
    loan = _new_loan(repos, now)

    loan.returned_at = now

    stored = repos.loans.get_active_for_book(loan.book_id)
    assert stored is not None
    assert stored.is_active

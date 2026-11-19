from collections.abc import Callable
from datetime import UTC, datetime

import pytest

from app.domain.models import Book, Member
from app.repositories.in_memory import (
    InMemoryBookRepository,
    InMemoryLoanRepository,
    InMemoryMemberRepository,
)
from app.services.loan_service import LoanService


@pytest.fixture
def now() -> datetime:
    return datetime(2026, 1, 15, 10, 0, tzinfo=UTC)


@pytest.fixture
def books() -> InMemoryBookRepository:
    return InMemoryBookRepository()


@pytest.fixture
def members() -> InMemoryMemberRepository:
    return InMemoryMemberRepository()


@pytest.fixture
def loans() -> InMemoryLoanRepository:
    return InMemoryLoanRepository()


@pytest.fixture
def service(
    books: InMemoryBookRepository,
    members: InMemoryMemberRepository,
    loans: InMemoryLoanRepository,
    now: datetime,
) -> LoanService:
    return LoanService(books, members, loans, clock=lambda: now)


@pytest.fixture
def make_book(books: InMemoryBookRepository) -> Callable[[], int]:
    def _make() -> int:
        book = books.add(Book(title="Dune", author="Frank Herbert"))
        assert book.id is not None
        return book.id

    return _make


@pytest.fixture
def make_member(members: InMemoryMemberRepository) -> Callable[[], int]:
    def _make() -> int:
        member = members.add(Member(name="Alice", email="alice@example.com"))
        assert member.id is not None
        return member.id

    return _make

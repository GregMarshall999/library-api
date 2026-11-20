from collections.abc import Callable, Iterator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_book_repository,
    get_loan_service,
    get_member_repository,
)
from app.main import create_app
from app.repositories.in_memory import (
    InMemoryBookRepository,
    InMemoryLoanRepository,
    InMemoryMemberRepository,
)
from app.services.loan_service import LoanService


@pytest.fixture
def client(now: datetime) -> Iterator[TestClient]:
    """The real app, with the database swapped for in-memory fakes. No DB needed."""
    books = InMemoryBookRepository()
    members = InMemoryMemberRepository()
    loans = InMemoryLoanRepository()

    app = create_app()
    app.dependency_overrides[get_book_repository] = lambda: books
    app.dependency_overrides[get_member_repository] = lambda: members
    app.dependency_overrides[get_loan_service] = lambda: LoanService(
        books, members, loans, clock=lambda: now
    )

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def make_book(client: TestClient) -> Callable[[], int]:
    def _make() -> int:
        response = client.post("/books", json={"title": "Dune", "author": "Frank Herbert"})
        assert response.status_code == 201
        book_id: int = response.json()["id"]
        return book_id

    return _make


@pytest.fixture
def make_member(client: TestClient) -> Callable[[], int]:
    def _make() -> int:
        response = client.post("/members", json={"name": "Alice", "email": "alice@example.com"})
        assert response.status_code == 201
        member_id: int = response.json()["id"]
        return member_id

    return _make

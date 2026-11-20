"""The full stack: HTTP -> router -> service -> SQL repository -> PostgreSQL."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.main import create_app

pytestmark = pytest.mark.integration


@pytest.fixture
def pg_client(db_session: Session) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    with TestClient(app) as client:
        yield client


def test_borrow_and_return_through_the_api(pg_client: TestClient) -> None:
    book = pg_client.post("/books", json={"title": "Dune", "author": "Frank Herbert"}).json()
    alice = pg_client.post("/members", json={"name": "Alice", "email": "alice@example.com"}).json()
    bob = pg_client.post("/members", json={"name": "Bob", "email": "bob@example.com"}).json()

    first = pg_client.post("/loans", json={"book_id": book["id"], "member_id": alice["id"]})
    second = pg_client.post("/loans", json={"book_id": book["id"], "member_id": bob["id"]})
    returned = pg_client.post(f"/books/{book['id']}/return")

    assert first.status_code == 201
    assert second.status_code == 409
    assert returned.status_code == 200
    assert returned.json()["returned_at"] is not None

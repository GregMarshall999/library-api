from typing import Any

import pytest
from fastapi.testclient import TestClient


def test_create_book_returns_201_and_the_book(client: TestClient) -> None:
    response = client.post("/books", json={"title": "Dune", "author": "Frank Herbert"})

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Dune"
    assert body["author"] == "Frank Herbert"
    assert isinstance(body["id"], int)


def test_created_book_can_be_fetched(client: TestClient) -> None:
    book_id = client.post("/books", json={"title": "Dune", "author": "Frank Herbert"}).json()["id"]

    response = client.get(f"/books/{book_id}")

    assert response.status_code == 200
    assert response.json() == {"id": book_id, "title": "Dune", "author": "Frank Herbert"}


def test_unknown_book_returns_404(client: TestClient) -> None:
    response = client.get("/books/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Book 999 not found"}


@pytest.mark.parametrize(
    "payload",
    [
        {},  # nothing
        {"title": "Dune"},  # missing author
        {"title": "", "author": "Frank Herbert"},  # empty
        {"title": "   ", "author": "Frank Herbert"},  # only spaces
        {"title": "x" * 201, "author": "Frank Herbert"},  # too long
        {"title": 42, "author": "Frank Herbert"},  # wrong type
    ],
)
def test_invalid_book_payload_returns_422(client: TestClient, payload: dict[str, Any]) -> None:
    response = client.post("/books", json=payload)

    assert response.status_code == 422


def test_create_member_returns_201(client: TestClient) -> None:
    response = client.post("/members", json={"name": "Alice", "email": "alice@example.com"})

    assert response.status_code == 201
    assert response.json()["email"] == "alice@example.com"


@pytest.mark.parametrize("email", ["", "alice", "alice@", "@example.com", "a lice@example.com"])
def test_invalid_email_returns_422(client: TestClient, email: str) -> None:
    response = client.post("/members", json={"name": "Alice", "email": email})

    assert response.status_code == 422


def test_unknown_member_returns_404(client: TestClient) -> None:
    assert client.get("/members/999").status_code == 404


def test_created_member_can_be_fetched(client: TestClient) -> None:
    member_id = client.post(
        "/members", json={"name": "Alice", "email": "alice@example.com"}
    ).json()["id"]

    response = client.get(f"/members/{member_id}")

    assert response.status_code == 200
    assert response.json() == {"id": member_id, "name": "Alice", "email": "alice@example.com"}

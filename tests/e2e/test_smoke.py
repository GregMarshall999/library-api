import httpx2
import pytest

pytestmark = pytest.mark.e2e


def test_health(api: httpx2.Client) -> None:
    response = api.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_created_book_is_still_there_in_the_next_request(api: httpx2.Client) -> None:
    created = api.post("/books", json={"title": "Dune", "author": "Frank Herbert"})
    assert created.status_code == 201

    fetched = api.get(f"/books/{created.json()['id']}")

    assert fetched.status_code == 200
    assert fetched.json() == created.json()


def _create(api: httpx2.Client, path: str, payload: dict[str, str]) -> int:
    response = api.post(path, json=payload)
    assert response.status_code == 201
    new_id: int = response.json()["id"]
    return new_id


def test_full_loan_flow(api: httpx2.Client) -> None:
    book_id = _create(api, "/books", {"title": "Dune", "author": "Frank Herbert"})
    alice_id = _create(api, "/members", {"name": "Alice", "email": "alice@example.com"})
    bob_id = _create(api, "/members", {"name": "Bob", "email": "bob@example.com"})

    borrowed = api.post("/loans", json={"book_id": book_id, "member_id": alice_id})
    refused = api.post("/loans", json={"book_id": book_id, "member_id": bob_id})
    returned = api.post(f"/books/{book_id}/return")
    borrowed_again = api.post("/loans", json={"book_id": book_id, "member_id": bob_id})

    assert borrowed.status_code == 201
    assert refused.status_code == 409
    assert returned.status_code == 200
    assert borrowed_again.status_code == 201

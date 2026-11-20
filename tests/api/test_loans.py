from collections.abc import Callable
from datetime import datetime

from fastapi.testclient import TestClient

MakeId = Callable[[], int]


def test_borrow_returns_201_and_the_loan(
    client: TestClient, make_book: MakeId, make_member: MakeId, now: datetime
) -> None:
    book_id, member_id = make_book(), make_member()

    response = client.post("/loans", json={"book_id": book_id, "member_id": member_id})

    assert response.status_code == 201
    body = response.json()
    assert body["book_id"] == book_id
    assert body["member_id"] == member_id
    assert datetime.fromisoformat(body["borrowed_at"]) == now
    assert body["returned_at"] is None


def test_borrow_unknown_book_returns_404(client: TestClient, make_member: MakeId) -> None:
    member_id = make_member()

    response = client.post("/loans", json={"book_id": 999, "member_id": member_id})

    assert response.status_code == 404


def test_borrow_a_book_already_on_loan_returns_409(
    client: TestClient, make_book: MakeId, make_member: MakeId
) -> None:
    book_id = make_book()
    client.post("/loans", json={"book_id": book_id, "member_id": make_member()})
    other_member_id = make_member()

    response = client.post("/loans", json={"book_id": book_id, "member_id": other_member_id})

    assert response.status_code == 409
    assert "already on loan" in response.json()["detail"]


def test_fourth_loan_returns_409(
    client: TestClient, make_book: MakeId, make_member: MakeId
) -> None:
    member_id = make_member()
    for _ in range(3):
        client.post("/loans", json={"book_id": make_book(), "member_id": member_id})
    extra_book_id = make_book()

    response = client.post("/loans", json={"book_id": extra_book_id, "member_id": member_id})

    assert response.status_code == 409


def test_return_book_returns_200_and_closes_the_loan(
    client: TestClient, make_book: MakeId, make_member: MakeId, now: datetime
) -> None:
    book_id = make_book()
    client.post("/loans", json={"book_id": book_id, "member_id": make_member()})

    response = client.post(f"/books/{book_id}/return")

    assert response.status_code == 200
    assert datetime.fromisoformat(response.json()["returned_at"]) == now


def test_return_a_book_not_on_loan_returns_409(client: TestClient, make_book: MakeId) -> None:
    book_id = make_book()

    response = client.post(f"/books/{book_id}/return")

    assert response.status_code == 409


def test_invalid_loan_ids_return_422(client: TestClient) -> None:
    response = client.post("/loans", json={"book_id": 0, "member_id": -1})

    assert response.status_code == 422

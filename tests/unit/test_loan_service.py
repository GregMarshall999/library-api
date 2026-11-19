from collections.abc import Callable
from datetime import datetime

import pytest

from app.domain.exceptions import (
    BookAlreadyBorrowedError,
    BookNotBorrowedError,
    BookNotFoundError,
    LoanLimitReachedError,
    MemberNotFoundError,
)
from app.repositories.in_memory import (
    InMemoryBookRepository,
    InMemoryLoanRepository,
    InMemoryMemberRepository,
)
from app.services.loan_service import LoanService

MakeId = Callable[[], int]


# ---------- borrowing ----------


def test_borrow_create_an_active_load(
    service: LoanService, make_book: MakeId, make_member: MakeId, now: datetime
) -> None:
    book_id = make_book()
    member_id = make_member()

    loan = service.borrow(book_id=book_id, member_id=member_id)

    assert loan.id is not None
    assert loan.book_id == book_id
    assert loan.member_id == member_id
    assert loan.borrowed_at == now
    assert loan.is_active


def test_cannot_borrow_unknown_book(service: LoanService, make_member: MakeId) -> None:
    member_id = make_member()

    with pytest.raises(BookNotFoundError, match="999"):
        service.borrow(book_id=999, member_id=member_id)


def test_cannot_borrow_with_unknown_member(service: LoanService, make_book: MakeId) -> None:
    book_id = make_book()

    with pytest.raises(MemberNotFoundError):
        service.borrow(book_id=book_id, member_id=999)


def test_cannot_borrow_a_book_already_on_loan(
    service: LoanService, make_book: MakeId, make_member: MakeId
) -> None:
    book_id = make_book()
    service.borrow(book_id=book_id, member_id=make_member())
    other_member_id = make_member()

    with pytest.raises(BookAlreadyBorrowedError):
        service.borrow(book_id=book_id, member_id=other_member_id)


# ---------- loan limit ----------


@pytest.mark.parametrize("limit", [1, 3, 5])
def test_member_can_borrow_up_to_the_limit_and_no_more(
    limit: int,
    books: InMemoryBookRepository,
    members: InMemoryMemberRepository,
    loans: InMemoryLoanRepository,
    now: datetime,
    make_book: MakeId,
    make_member: MakeId,
) -> None:
    service = LoanService(books, members, loans, max_active_loans=limit, clock=lambda: now)
    member_id = make_member()
    for _ in range(limit):
        service.borrow(book_id=make_book(), member_id=member_id)
    extra_book_id = make_book()

    with pytest.raises(LoanLimitReachedError):
        service.borrow(book_id=extra_book_id, member_id=member_id)


def test_returning_a_book_frees_a_loan_slot(
    service: LoanService, make_book: MakeId, make_member: MakeId
) -> None:
    member_id = make_member()
    book_ids = [make_book() for _ in range(3)]
    for book_id in book_ids:
        service.borrow(book_id=book_id, member_id=member_id)

    service.return_book(book_id=book_ids[0])
    loan = service.borrow(book_id=make_book(), member_id=member_id)

    assert loan.is_active


# ---------- returning ----------


def test_return_book_closes_the_loan(
    service: LoanService, make_book: MakeId, make_member: MakeId, now: datetime
) -> None:
    book_id = make_book()
    service.borrow(book_id=book_id, member_id=make_member())

    loan = service.return_book(book_id=book_id)

    assert loan.returned_at == now
    assert not loan.is_active


def test_returned_book_can_be_borrowed_again(
    service: LoanService, make_book: MakeId, make_member: MakeId
) -> None:
    book_id = make_book()
    service.borrow(book_id=book_id, member_id=make_member())
    service.return_book(book_id=book_id)

    loan = service.borrow(book_id=book_id, member_id=make_member())

    assert loan.is_active


def test_cannot_return_a_book_that_is_not_on_loan(service: LoanService, make_book: MakeId) -> None:
    book_id = make_book()

    with pytest.raises(BookNotBorrowedError):
        service.return_book(book_id=book_id)

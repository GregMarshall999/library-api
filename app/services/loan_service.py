from collections.abc import Callable
from datetime import UTC, datetime

from app.domain.exceptions import (
    BookAlreadyBorrowedError,
    BookNotBorrowedError,
    BookNotFoundError,
    LoanLimitReachedError,
    MemberNotFoundError,
)
from app.domain.models import Loan
from app.repositories.interfaces import BookRepository, LoanRepository, MemberRepository


def utc_now() -> datetime:
    return datetime.now(UTC)


class LoanService:
    def __init__(
        self,
        books: BookRepository,
        members: MemberRepository,
        loans: LoanRepository,
        *,
        max_active_loans: int = 3,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._books = books
        self._members = members
        self._loans = loans
        self._max_active_loans = max_active_loans
        self._clock = clock

    def borrow(self, book_id: int, member_id: int) -> Loan:
        if self._books.get(book_id) is None:
            raise BookNotFoundError(f"Book {book_id} not found")
        if self._members.get(member_id) is None:
            raise MemberNotFoundError(f"Member {member_id} not found")
        if self._loans.get_active_for_book(book_id) is not None:
            raise BookAlreadyBorrowedError(f"Book {book_id} already on loan")
        if self._loans.count_active_for_member(member_id) >= self._max_active_loans:
            raise LoanLimitReachedError(
                f"Member {member_id} already has {self._max_active_loans} active loans"
            )

        loan = Loan(book_id=book_id, member_id=member_id, borrowed_at=self._clock())
        return self._loans.add(loan)

    def return_book(self, book_id: int) -> Loan:
        loan = self._loans.get_active_for_book(book_id)
        if loan is None:
            raise BookNotBorrowedError(f"Book {book_id} is not on loan")

        loan.returned_at = self._clock()
        return self._loans.update(loan)

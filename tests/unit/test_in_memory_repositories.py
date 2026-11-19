from datetime import datetime

import pytest

from app.domain.models import Loan
from app.repositories.in_memory import InMemoryLoanRepository


def test_update_unknown_loan_raises(loans: InMemoryLoanRepository, now: datetime) -> None:
    loan = Loan(book_id=1, member_id=1, borrowed_at=now, id=42)

    with pytest.raises(ValueError, match="42"):
        loans.update(loan)


def test_update_loan_without_id_raises(loans: InMemoryLoanRepository, now: datetime) -> None:
    loan = Loan(book_id=1, member_id=1, borrowed_at=now)

    with pytest.raises(ValueError):
        loans.update(loan)


def test_returned_objects_are_copies(loans: InMemoryLoanRepository, now: datetime) -> None:
    loan = loans.add(Loan(book_id=1, member_id=1, borrowed_at=now))

    loan.returned_at = now 

    stored = loans.get_active_for_book(book_id=1)
    assert stored is not None
    assert stored.is_active
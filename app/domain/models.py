from dataclasses import dataclass
from datetime import datetime


@dataclass
class Book:
    title: str
    author: str
    id: int | None = None


@dataclass
class Member:
    name: str
    email: str
    id: int | None = None


@dataclass
class Loan:
    book_id: int
    member_id: int
    borrowed_at: datetime
    returned_at: datetime | None = None
    id: int | None = None

    @property
    def is_active(self) -> bool:
        return self.returned_at is None

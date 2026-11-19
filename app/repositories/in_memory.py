from dataclasses import replace

from app.domain.models import Book, Loan, Member
from app.repositories.interfaces import BookRepository, LoanRepository, MemberRepository


class InMemoryBookRepository(BookRepository):
    def __init__(self) -> None:
        self._books: dict[int, Book] = {}
        self._next_id = 1

    def add(self, book: Book) -> Book:
        stored = replace(book, id=self._next_id)
        self._books[self._next_id] = stored
        self._next_id += 1
        return replace(stored)

    def get(self, book_id: int) -> Book | None:
        book = self._books.get(book_id)
        return replace(book) if book is not None else None


class InMemoryMemberRepository(MemberRepository):
    def __init__(self) -> None:
        self._members: dict[int, Member] = {}
        self._next_id = 1

    def add(self, member: Member) -> Member:
        stored = replace(member, id=self._next_id)
        self._members[self._next_id] = stored
        self._next_id += 1
        return replace(stored)

    def get(self, member_id: int) -> Member | None:
        member = self._members.get(member_id)
        return replace(member) if member is not None else None


class InMemoryLoanRepository(LoanRepository):
    def __init__(self) -> None:
        self._loans: dict[int, Loan] = {}
        self._next_id = 1

    def add(self, loan: Loan) -> Loan:
        stored = replace(loan, id=self._next_id)
        self._loans[self._next_id] = stored
        self._next_id += 1
        return replace(stored)

    def update(self, loan: Loan) -> Loan:
        if loan.id is None or loan.id not in self._loans:
            raise ValueError(f"Loan {loan.id} does not exist")
        self._loans[loan.id] = replace(loan)
        return replace(loan)

    def get_active_for_book(self, book_id: int) -> Loan | None:
        for loan in self._loans.values():
            if loan.book_id == book_id and loan.is_active:
                return replace(loan)
        return None

    def count_active_for_member(self, member_id: int) -> int:
        return sum(
            1 for loan in self._loans.values() if loan.member_id == member_id and loan.is_active
        )

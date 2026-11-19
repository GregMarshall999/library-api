from abc import ABC, abstractmethod

from app.domain.models import Book, Loan, Member


class BookRepository(ABC):
    @abstractmethod
    def add(self, book: Book) -> Book: ...

    @abstractmethod
    def get(self, book_id: int) -> Book | None: ...


class MemberRepository(ABC):
    @abstractmethod
    def add(self, member: Member) -> Member: ...

    @abstractmethod
    def get(self, member_id: int) -> Member | None: ...


class LoanRepository(ABC):
    @abstractmethod
    def add(self, loan: Loan) -> Loan: ...

    @abstractmethod
    def update(self, loan: Loan) -> Loan: ...

    @abstractmethod
    def get_active_for_book(self, book_id: int) -> Loan | None: ...

    @abstractmethod
    def count_active_for_member(self, member_id: int) -> int: ...

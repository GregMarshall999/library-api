from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.tables import BookRow, LoanRow, MemberRow
from app.domain.models import Book, Loan, Member
from app.repositories.interfaces import BookRepository, LoanRepository, MemberRepository


def _to_book(row: BookRow) -> Book:
    return Book(id=row.id, title=row.title, author=row.author)


def _to_member(row: MemberRow) -> Member:
    return Member(id=row.id, name=row.name, email=row.email)


def _to_loan(row: LoanRow) -> Loan:
    return Loan(
        id=row.id,
        book_id=row.book_id,
        member_id=row.member_id,
        borrowed_at=row.borrowed_at,
        returned_at=row.returned_at,
    )


class SqlBookRepository(BookRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, book: Book) -> Book:
        row = BookRow(title=book.title, author=book.author)
        self._session.add(row)
        self._session.flush()
        return _to_book(row)

    def get(self, book_id: int) -> Book | None:
        row = self._session.get(BookRow, book_id)
        return _to_book(row) if row is not None else None


class SqlMemberRepository(MemberRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, member: Member) -> Member:
        row = MemberRow(name=member.name, email=member.email)
        self._session.add(row)
        self._session.flush()
        return _to_member(row)

    def get(self, member_id: int) -> Member | None:
        row = self._session.get(MemberRow, member_id)
        return _to_member(row) if row is not None else None


class SqlLoanRepository(LoanRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, loan: Loan) -> Loan:
        row = LoanRow(
            book_id=loan.book_id,
            member_id=loan.member_id,
            borrowed_at=loan.borrowed_at,
            returned_at=loan.returned_at,
        )
        self._session.add(row)
        self._session.flush()
        return _to_loan(row)

    def update(self, loan: Loan) -> Loan:
        row = self._session.get(LoanRow, loan.id) if loan.id is not None else None
        if row is None:
            raise ValueError(f"Loan {loan.id} does not exist")
        row.book_id = loan.book_id
        row.member_id = loan.member_id
        row.borrowed_at = loan.borrowed_at
        row.returned_at = loan.returned_at
        self._session.flush()
        return _to_loan(row)

    def get_active_for_book(self, book_id: int) -> Loan | None:
        stmt = select(LoanRow).where(LoanRow.book_id == book_id, LoanRow.returned_at.is_(None))
        row = self._session.scalars(stmt).first()
        return _to_loan(row) if row is not None else None

    def count_active_for_member(self, member_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(LoanRow)
            .where(LoanRow.member_id == member_id, LoanRow.returned_at.is_(None))
        )
        return self._session.scalar(stmt) or 0
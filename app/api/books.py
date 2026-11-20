from fastapi import APIRouter, status

from app.api.dependencies import BookRepoDep
from app.api.schemas import BookCreate, BookOut
from app.domain.exceptions import BookNotFoundError
from app.domain.models import Book

router = APIRouter(prefix="/books", tags=["books"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate, books: BookRepoDep) -> BookOut:
    book = books.add(Book(title=payload.title, author=payload.author))
    return BookOut.model_validate(book)


@router.get("/{book_id}")
def get_book(book_id: int, books: BookRepoDep) -> BookOut:
    book = books.get(book_id)
    if book is None:
        raise BookNotFoundError(f"Book {book_id} not found")
    return BookOut.model_validate(book)

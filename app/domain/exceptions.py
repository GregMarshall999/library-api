class DomainError(Exception):
    """Base class for every business-rule violation."""


class BookNotFoundError(DomainError):
    """The requested book does not exist."""


class MemberNotFoundError(DomainError):
    """The requested member does not exist."""


class BookAlreadyBorrowedError(DomainError):
    """The book is currently on loan."""


class LoanLimitReachedError(DomainError):
    """The member already has the maximum number of active loans."""


class BookNotBorrowedError(DomainError):
    """The book cannot be returned because it is not currently on loan."""

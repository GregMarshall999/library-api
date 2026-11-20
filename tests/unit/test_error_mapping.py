from app.api.errors import STATUS_BY_ERROR
from app.domain.exceptions import DomainError


def test_every_domain_error_has_an_http_status() -> None:
    """Fails if someone adds a new business error and forgets to map it."""
    missing = [cls.__name__ for cls in DomainError.__subclasses__() if cls not in STATUS_BY_ERROR]

    assert missing == []

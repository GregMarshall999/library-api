from datetime import UTC, datetime

from app.services.loan_service import utc_now


def test_utc_now_returns_current_time_in_utc() -> None:
    before = datetime.now(UTC)

    result = utc_now()

    after = datetime.now(UTC)
    assert result.tzinfo is UTC
    assert before <= result <= after
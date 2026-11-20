from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from app.api.dependencies import get_engine, get_session
from app.config import get_settings


@pytest.fixture
def fake_session(mocker: MockerFixture) -> MagicMock:
    """Replace the real Session class (and engine) so no database is touched."""
    mocker.patch("app.api.dependencies.get_engine")
    session_class = mocker.patch("app.api.dependencies.Session")
    session: MagicMock = session_class.return_value.__enter__.return_value
    return session


def test_session_is_committed_when_the_request_succeeds(fake_session: MagicMock) -> None:
    dependency = get_session()
    session = next(dependency)

    with pytest.raises(StopIteration):
        next(dependency)

    assert session is fake_session
    fake_session.commit.assert_called_once()
    fake_session.rollback.assert_not_called()


def test_session_is_rolled_back_and_error_reraised_when_the_request_fails(
    fake_session: MagicMock,
) -> None:
    dependency = get_session()
    next(dependency)
    error = RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        dependency.throw(error)

    fake_session.rollback.assert_called_once()
    fake_session.commit.assert_not_called()


def test_engine_uses_the_configured_url_and_is_created_once() -> None:
    get_engine.cache_clear()

    engine = get_engine()

    assert engine.url.render_as_string(hide_password=False) == get_settings().database_url
    assert get_engine() is engine
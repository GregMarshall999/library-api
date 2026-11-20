
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


@pytest.fixture
def now() -> datetime:
    return datetime(2026, 1, 15, 10, 0, tzinfo=UTC)
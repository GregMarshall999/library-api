import os
from collections.abc import Iterator

import httpx2
import pytest


@pytest.fixture(scope="session")
def api() -> Iterator[httpx2.Client]:
    """An HTTP client pointed at a *running* instance of the app."""
    base_url = os.environ.get("E2E_BASE_URL")
    if not base_url:
        if os.environ.get("CI"):
            pytest.fail("E2E_BASE_URL must be set in CI: a skipped e2e suite is a false green")
        pytest.skip("E2E_BASE_URL is not set: start the stack and set it to run e2e tests")
    with httpx2.Client(base_url=base_url, timeout=10) as client:
        yield client
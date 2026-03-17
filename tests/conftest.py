"""Shared fixtures for all test modules."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import history as history_service


@pytest.fixture()
def client() -> TestClient:
    """Return a synchronous TestClient wired to the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_history() -> None:
    """Clear the in-memory history store before every test.

    autouse=True means this runs automatically — no test needs to import it.
    """
    history_service.clear()

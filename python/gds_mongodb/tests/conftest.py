"""Pytest configuration and shared fixtures for gds_mongodb tests."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_mongo_client():
    """Create a mock MongoDB client for testing."""
    mock = MagicMock()
    mock.admin = MagicMock()
    mock.admin.command = MagicMock(return_value={"ok": 1})
    mock.close = MagicMock()
    return mock


@pytest.fixture
def sample_mongodb_uri() -> str:
    """Return a sample MongoDB connection URI for testing."""
    return "mongodb://localhost:27017/testdb"

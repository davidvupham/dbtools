"""Pytest configuration and shared fixtures for gds_postgres tests."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_postgres_connection():
    """Create a mock PostgreSQL connection for testing."""
    mock = MagicMock()
    mock.cursor = MagicMock()
    mock.cursor.return_value.execute = MagicMock()
    mock.cursor.return_value.fetchall = MagicMock(return_value=[])
    mock.close = MagicMock()
    return mock


@pytest.fixture
def sample_postgres_dsn() -> str:
    """Return a sample PostgreSQL DSN for testing."""
    return "postgresql://user:password@localhost:5432/testdb"

"""Pytest configuration and shared fixtures for gds_mssql tests."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_mssql_connection():
    """Create a mock SQL Server connection for testing."""
    mock = MagicMock()
    mock.cursor = MagicMock()
    mock.cursor.return_value.execute = MagicMock()
    mock.cursor.return_value.fetchall = MagicMock(return_value=[])
    mock.close = MagicMock()
    return mock


@pytest.fixture
def sample_mssql_connection_string() -> str:
    """Return a sample SQL Server connection string for testing."""
    return "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=testdb;UID=sa;PWD=password"

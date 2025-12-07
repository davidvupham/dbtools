"""Pytest configuration and shared fixtures for gds_snowflake tests."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_snowflake_connection():
    """Create a mock Snowflake connection for testing."""
    mock = MagicMock()
    mock.cursor = MagicMock()
    mock.cursor.return_value.execute = MagicMock()
    mock.cursor.return_value.fetchall = MagicMock(return_value=[])
    mock.close = MagicMock()
    return mock


@pytest.fixture
def sample_snowflake_config() -> dict:
    """Return sample Snowflake configuration for testing."""
    return {
        "account": "test-account",
        "user": "test-user",
        "warehouse": "test-warehouse",
        "database": "test-database",
        "schema": "public",
    }

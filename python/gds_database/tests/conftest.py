"""Pytest configuration and shared fixtures for gds_database tests."""

import pytest


@pytest.fixture
def sample_connection_string() -> str:
    """Return a sample connection string for testing."""
    return "postgresql://user:password@localhost:5432/testdb"

"""Pytest configuration and shared fixtures for gds_vault tests."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_vault_client():
    """Create a mock Vault client for testing."""
    mock = MagicMock()
    mock.is_authenticated = MagicMock(return_value=True)
    mock.secrets = MagicMock()
    mock.secrets.kv = MagicMock()
    mock.secrets.kv.v2 = MagicMock()
    mock.secrets.kv.v2.read_secret_version = MagicMock(return_value={"data": {"data": {"key": "value"}}})
    return mock


@pytest.fixture
def sample_vault_config() -> dict:
    """Return sample Vault configuration for testing."""
    return {
        "url": "http://localhost:8200",
        "token": "test-token",
        "mount_point": "secret",
    }

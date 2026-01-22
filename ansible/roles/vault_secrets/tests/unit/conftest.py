"""Pytest configuration for vault_secrets role tests."""

from pathlib import Path

import pytest


@pytest.fixture
def role_path():
    """Return the path to the vault_secrets role."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def mock_vault_response():
    """Return a mock Vault secret response."""
    return {
        "request_id": "test-request-id",
        "lease_id": "",
        "renewable": False,
        "lease_duration": 0,
        "data": {
            "data": {
                "username": "testuser",
                "password": "testpass123",
                "host": "db.example.com",
                "port": 5432,
            },
            "metadata": {
                "created_time": "2026-01-01T00:00:00Z",
                "deletion_time": "",
                "destroyed": False,
                "version": 1,
            },
        },
    }


@pytest.fixture
def mock_vault_login_response():
    """Return a mock Vault login response."""
    return {
        "auth": {
            "client_token": "hvs.test-token-12345",
            "accessor": "test-accessor",
            "policies": ["default", "myapp-read"],
            "token_policies": ["default", "myapp-read"],
            "metadata": {"role_name": "myapp"},
            "lease_duration": 3600,
            "renewable": True,
        }
    }


@pytest.fixture
def sample_secrets_to_fetch():
    """Return sample vault_secrets_to_fetch configuration."""
    return [
        {
            "path": "myapp/database",
            "key": "password",
            "fact_name": "db_password",
        },
        {
            "path": "myapp/api",
            "key": "api_key",
            "fact_name": "api_key",
        },
        {
            "path": "myapp/config",
            "fact_name": "app_config",
        },
    ]


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("VAULT_ADDR", "https://vault.example.com:8200")
    monkeypatch.setenv("VAULT_ROLE_ID", "test-role-id")
    monkeypatch.setenv("VAULT_SECRET_ID", "test-secret-id")
    monkeypatch.setenv("VAULT_NAMESPACE", "")

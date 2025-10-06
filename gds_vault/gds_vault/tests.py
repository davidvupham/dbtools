"""
Basic integration tests for gds_vault package.

These tests require a running Vault dev server and valid environment variables.
Tests will be skipped if the required environment variables are not set.
"""

import os

import pytest

from gds_vault.vault import VaultError, get_secret_from_vault

# These tests require a running Vault dev server and valid env vars.
# To skip if not configured:
pytestmark = pytest.mark.skipif(
    not (
        os.getenv("VAULT_ROLE_ID")
        and os.getenv("VAULT_SECRET_ID")
        and os.getenv("VAULT_ADDR")
    ),
    reason="Vault env vars not set",
)


def test_secret_fetch(monkeypatch):
    """
    Test that get_secret_from_vault raises VaultError without valid vault.
    """
    # Example: monkeypatch env vars for test/dev
    monkeypatch.setenv("VAULT_ROLE_ID", "test-role-id")
    monkeypatch.setenv("VAULT_SECRET_ID", "test-secret-id")
    monkeypatch.setenv("VAULT_ADDR", "http://127.0.0.1:8200")
    # This will fail unless Vault dev server is running and configured
    with pytest.raises(VaultError):
        get_secret_from_vault("secret/data/myapp")

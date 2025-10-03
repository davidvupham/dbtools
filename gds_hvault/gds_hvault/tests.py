import os
import pytest
from gds_hvault.vault import get_secret_from_vault, VaultError

# These tests require a running Vault dev server and valid env vars.
# To skip if not configured:
pytestmark = pytest.mark.skipif(
    not (
        os.getenv("HVAULT_ROLE_ID")
        and os.getenv("HVAULT_SECRET_ID")
        and (os.getenv("HVAULT_ADDR") or os.getenv("VAULT_ADDR"))
    ),
    reason="Vault env vars not set",
)


def test_secret_fetch(monkeypatch):
    # Example: monkeypatch env vars for test/dev
    monkeypatch.setenv("HVAULT_ROLE_ID", "test-role-id")
    monkeypatch.setenv("HVAULT_SECRET_ID", "test-secret-id")
    monkeypatch.setenv("HVAULT_ADDR", "http://127.0.0.1:8200")
    # This will fail unless Vault dev server is running and configured
    with pytest.raises(VaultError):
        get_secret_from_vault("secret/data/myapp")

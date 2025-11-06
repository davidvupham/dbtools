#!/usr/bin/env python3
"""
Enhanced Vault client with additional features.

This is an example of how gds_vault could be extended with:
- Token caching
- Retry logic
- Context manager support
- Multiple secret operations
"""

import os
import time
from functools import wraps
from typing import Any, Optional

import requests


class VaultError(Exception):
    """Vault operation error."""

    pass


def retry_on_failure(max_retries=3, backoff_factor=2):
    """Decorator to retry failed operations with exponential backoff."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = backoff_factor**attempt
                        time.sleep(wait_time)
            raise VaultError(f"Failed after {max_retries} attempts: {last_exception}")

        return wrapper

    return decorator


class EnhancedVaultClient:
    """
    Enhanced Vault client with additional features.

    Features:
    - Token caching and renewal
    - Retry logic with exponential backoff
    - Context manager support
    - Read/write/delete operations
    - List secrets
    """

    def __init__(
        self,
        vault_addr: Optional[str] = None,
        role_id: Optional[str] = None,
        secret_id: Optional[str] = None,
        token: Optional[str] = None,
        timeout: int = 10,
        max_retries: int = 3,
        verify_ssl: bool = True,
    ):
        """
        Initialize Vault client.

        Args:
            vault_addr: Vault server address
            role_id: AppRole role_id
            secret_id: AppRole secret_id
            token: Direct token (alternative to AppRole)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            verify_ssl: Verify SSL certificates
        """
        self.vault_addr = vault_addr or os.getenv("VAULT_ADDR")
        if not self.vault_addr:
            raise VaultError("Vault address must be provided")

        self.role_id = role_id or os.getenv("VAULT_ROLE_ID")
        self.secret_id = secret_id or os.getenv("VAULT_SECRET_ID")
        self.token = token
        self.timeout = timeout
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl

        self._token_cache = None
        self._token_expiry = None

    def __enter__(self):
        """Context manager entry."""
        self.authenticate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - revoke token."""
        if self._token_cache and not self.token:
            # Only revoke if we created the token
            try:
                self.revoke_token()
            except Exception:
                pass  # Best effort cleanup

    @retry_on_failure(max_retries=3)
    def authenticate(self):
        """Authenticate with Vault using AppRole."""
        if self.token:
            self._token_cache = self.token
            return

        if not self.role_id or not self.secret_id:
            raise VaultError("AppRole credentials required")

        url = f"{self.vault_addr}/v1/auth/approle/login"
        payload = {"role_id": self.role_id, "secret_id": self.secret_id}

        resp = requests.post(
            url, json=payload, timeout=self.timeout, verify=self.verify_ssl
        )

        if not resp.ok:
            raise VaultError(f"Authentication failed: {resp.text}")

        data = resp.json()
        self._token_cache = data["auth"]["client_token"]

        # Cache token expiry for renewal
        if "lease_duration" in data["auth"]:
            self._token_expiry = time.time() + data["auth"]["lease_duration"]

    def _get_token(self) -> str:
        """Get current token, authenticating if needed."""
        if not self._token_cache:
            self.authenticate()

        # Check if token needs renewal
        if self._token_expiry and time.time() > self._token_expiry - 300:
            # Renew 5 minutes before expiry
            try:
                self.renew_token()
            except Exception:
                # Re-authenticate if renewal fails
                self.authenticate()

        return self._token_cache

    @retry_on_failure(max_retries=3)
    def read_secret(self, path: str, version: Optional[int] = None) -> dict[str, Any]:
        """
        Read a secret from Vault.

        Args:
            path: Secret path
            version: Specific version (KV v2 only)

        Returns:
            Secret data as dictionary
        """
        url = f"{self.vault_addr}/v1/{path}"
        if version:
            url += f"?version={version}"

        headers = {"X-Vault-Token": self._get_token()}

        resp = requests.get(
            url, headers=headers, timeout=self.timeout, verify=self.verify_ssl
        )

        if not resp.ok:
            raise VaultError(f"Failed to read secret: {resp.text}")

        data = resp.json()

        # Handle KV v1 vs v2
        if "data" in data and "data" in data["data"]:
            return data["data"]["data"]
        if "data" in data:
            return data["data"]
        raise VaultError("Unexpected response format")

    @retry_on_failure(max_retries=3)
    def write_secret(self, path: str, data: dict[str, Any]) -> bool:
        """
        Write a secret to Vault.

        Args:
            path: Secret path
            data: Secret data to write

        Returns:
            True if successful
        """
        url = f"{self.vault_addr}/v1/{path}"
        headers = {"X-Vault-Token": self._get_token()}

        # Wrap data for KV v2
        if "/data/" in path:
            payload = {"data": data}
        else:
            payload = data

        resp = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )

        if not resp.ok:
            raise VaultError(f"Failed to write secret: {resp.text}")

        return True

    @retry_on_failure(max_retries=3)
    def delete_secret(self, path: str) -> bool:
        """
        Delete a secret from Vault.

        Args:
            path: Secret path

        Returns:
            True if successful
        """
        url = f"{self.vault_addr}/v1/{path}"
        headers = {"X-Vault-Token": self._get_token()}

        resp = requests.delete(
            url, headers=headers, timeout=self.timeout, verify=self.verify_ssl
        )

        if not resp.ok:
            raise VaultError(f"Failed to delete secret: {resp.text}")

        return True

    @retry_on_failure(max_retries=3)
    def list_secrets(self, path: str) -> list:
        """
        List secrets at a path.

        Args:
            path: Path to list

        Returns:
            List of secret names
        """
        url = f"{self.vault_addr}/v1/{path}"
        headers = {"X-Vault-Token": self._get_token()}
        params = {"list": "true"}

        resp = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )

        if not resp.ok:
            raise VaultError(f"Failed to list secrets: {resp.text}")

        data = resp.json()
        return data.get("data", {}).get("keys", [])

    def renew_token(self) -> bool:
        """Renew the current token."""
        if not self._token_cache:
            return False

        url = f"{self.vault_addr}/v1/auth/token/renew-self"
        headers = {"X-Vault-Token": self._token_cache}

        resp = requests.post(
            url, headers=headers, timeout=self.timeout, verify=self.verify_ssl
        )

        if not resp.ok:
            return False

        data = resp.json()
        if "auth" in data and "lease_duration" in data["auth"]:
            self._token_expiry = time.time() + data["auth"]["lease_duration"]

        return True

    def revoke_token(self) -> bool:
        """Revoke the current token."""
        if not self._token_cache:
            return False

        url = f"{self.vault_addr}/v1/auth/token/revoke-self"
        headers = {"X-Vault-Token": self._token_cache}

        resp = requests.post(
            url, headers=headers, timeout=self.timeout, verify=self.verify_ssl
        )

        self._token_cache = None
        self._token_expiry = None

        return resp.ok


# Example usage
if __name__ == "__main__":
    # Using context manager (automatic token cleanup)
    with EnhancedVaultClient() as client:
        # Read secret
        secret = client.read_secret("secret/data/myapp")
        print(f"Password: {secret.get('password')}")

        # Write secret
        client.write_secret(
            "secret/data/myapp/api", {"key": "value", "token": "abc123"}
        )

        # List secrets
        secrets = client.list_secrets("secret/metadata/myapp")
        print(f"Available secrets: {secrets}")

        # Delete secret
        client.delete_secret("secret/data/myapp/temp")

    # Token automatically revoked when exiting context

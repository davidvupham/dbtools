"""Tests for VaultClient class."""

import os
import unittest
from unittest.mock import Mock, patch

import requests

from gds_vault import VaultClient, VaultError


class TestVaultClientInit(unittest.TestCase):
    """Test VaultClient initialization."""

    def setUp(self):
        """Clear environment variables before each test."""
        env_vars = ["VAULT_ROLE_ID", "VAULT_SECRET_ID", "VAULT_ADDR"]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]

    def test_init_with_parameters(self):
        """Test initialization with explicit parameters."""
        client = VaultClient(
            vault_addr="https://vault.example.com",
            role_id="test-role",
            secret_id="test-secret",
            timeout=30,
        )
        self.assertEqual(client.vault_addr, "https://vault.example.com")
        self.assertEqual(client.role_id, "test-role")
        self.assertEqual(client.secret_id, "test-secret")
        self.assertEqual(client.timeout, 30)
        self.assertIsNone(client._token)
        self.assertIsNone(client._token_expiry)
        self.assertEqual(len(client._secret_cache), 0)

    @patch.dict(
        os.environ,
        {
            "VAULT_ADDR": "https://vault.env.com",
            "VAULT_ROLE_ID": "env-role",
            "VAULT_SECRET_ID": "env-secret",
        },
    )
    def test_init_from_environment(self):
        """Test initialization from environment variables."""
        client = VaultClient()
        self.assertEqual(client.vault_addr, "https://vault.env.com")
        self.assertEqual(client.role_id, "env-role")
        self.assertEqual(client.secret_id, "env-secret")
        self.assertEqual(client.timeout, 10)  # Default timeout

    def test_init_missing_vault_addr(self):
        """Test initialization fails without vault address."""
        with self.assertRaises(VaultError) as context:
            VaultClient(role_id="role", secret_id="secret")
        self.assertIn("Vault address must be provided", str(context.exception))

    @patch.dict(os.environ, {"VAULT_ADDR": "https://vault.com"})
    def test_init_missing_credentials(self):
        """Test initialization fails without credentials."""
        with self.assertRaises(VaultError) as context:
            VaultClient()
        self.assertIn("VAULT_ROLE_ID and VAULT_SECRET_ID", str(context.exception))

    @patch.dict(os.environ, {"VAULT_ADDR": "https://vault.com", "VAULT_ROLE_ID": "role"})
    def test_init_missing_secret_id(self):
        """Test initialization fails with only role_id."""
        with self.assertRaises(VaultError) as context:
            VaultClient()
        self.assertIn("VAULT_ROLE_ID and VAULT_SECRET_ID", str(context.exception))


class TestVaultClientAuthentication(unittest.TestCase):
    """Test VaultClient authentication."""

    @patch("gds_vault.vault.requests.post")
    @patch("gds_vault.vault.time.time")
    def test_authenticate_success(self, mock_time, mock_post):
        """Test successful authentication."""
        mock_time.return_value = 1000.0
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {
                "client_token": "test-token-123",
                "lease_duration": 3600,
            }
        }

        client = VaultClient(
            vault_addr="https://vault.com",
            role_id="role",
            secret_id="secret",
        )
        token = client.authenticate()

        self.assertEqual(token, "test-token-123")
        self.assertEqual(client._token, "test-token-123")
        self.assertEqual(client._token_expiry, 1000.0 + 3600 - 300)  # 5 min buffer

        mock_post.assert_called_once_with(
            "https://vault.com/v1/auth/approle/login",
            json={"role_id": "role", "secret_id": "secret"},
            timeout=10,
        )

    @patch("gds_vault.vault.requests.post")
    def test_authenticate_connection_error(self, mock_post):
        """Test authentication connection error."""
        mock_post.side_effect = requests.RequestException("Connection failed")

        client = VaultClient(
            vault_addr="https://vault.com",
            role_id="role",
            secret_id="secret",
        )

        with self.assertRaises(VaultError) as context:
            client.authenticate()
        self.assertIn("Failed to connect", str(context.exception))

    @patch("gds_vault.vault.requests.post")
    def test_authenticate_failure(self, mock_post):
        """Test authentication failure."""
        mock_post.return_value = Mock(ok=False, text="invalid credentials")

        client = VaultClient(
            vault_addr="https://vault.com",
            role_id="role",
            secret_id="secret",
        )

        with self.assertRaises(VaultError) as context:
            client.authenticate()
        self.assertIn("AppRole login failed", str(context.exception))
        self.assertIn("invalid credentials", str(context.exception))


class TestVaultClientGetSecret(unittest.TestCase):
    """Test VaultClient.get_secret method."""

    @patch("gds_vault.vault.requests.get")
    @patch("gds_vault.vault.requests.post")
    def test_get_secret_kv_v2(self, mock_post, mock_get):
        """Test getting secret from KV v2."""
        # Mock authentication
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "token", "lease_duration": 3600}
        }

        # Mock secret fetch
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {
            "data": {"data": {"password": "secret123", "username": "admin"}}
        }

        client = VaultClient(
            vault_addr="https://vault.com",
            role_id="role",
            secret_id="secret",
        )
        secret = client.get_secret("secret/data/myapp")

        self.assertEqual(secret, {"password": "secret123", "username": "admin"})
        mock_get.assert_called_once()

    @patch("gds_vault.vault.requests.get")
    @patch("gds_vault.vault.requests.post")
    def test_get_secret_kv_v1(self, mock_post, mock_get):
        """Test getting secret from KV v1."""
        # Mock authentication
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "token", "lease_duration": 3600}
        }

        # Mock secret fetch (KV v1 format)
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {
            "data": {"password": "secret123", "username": "admin"}
        }

        client = VaultClient(
            vault_addr="https://vault.com",
            role_id="role",
            secret_id="secret",
        )
        secret = client.get_secret("secret/myapp")

        self.assertEqual(secret, {"password": "secret123", "username": "admin"})

    @patch("gds_vault.vault.requests.get")
    @patch("gds_vault.vault.requests.post")
    def test_get_secret_with_version(self, mock_post, mock_get):
        """Test getting specific version of secret."""
        # Mock authentication
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "token", "lease_duration": 3600}
        }

        # Mock secret fetch
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {
            "data": {"data": {"password": "old-secret"}}
        }

        client = VaultClient(
            vault_addr="https://vault.com",
            role_id="role",
            secret_id="secret",
        )
        secret = client.get_secret("secret/data/myapp", version=2)

        self.assertEqual(secret, {"password": "old-secret"})
        # Verify version parameter was passed
        call_args = mock_get.call_args
        self.assertEqual(call_args[1]["params"], {"version": 2})

    @patch("gds_vault.vault.requests.get")
    @patch("gds_vault.vault.requests.post")
    def test_get_secret_caching(self, mock_post, mock_get):
        """Test that secrets are cached."""
        # Mock authentication
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "token", "lease_duration": 3600}
        }

        # Mock secret fetch
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {
            "data": {"data": {"password": "secret123"}}
        }

        client = VaultClient(
            vault_addr="https://vault.com",
            role_id="role",
            secret_id="secret",
        )

        # First call - should fetch from Vault
        secret1 = client.get_secret("secret/data/myapp")
        self.assertEqual(secret1, {"password": "secret123"})
        self.assertEqual(mock_get.call_count, 1)

        # Second call - should use cache
        secret2 = client.get_secret("secret/data/myapp")
        self.assertEqual(secret2, {"password": "secret123"})
        self.assertEqual(mock_get.call_count, 1)  # No additional call

        # Verify cache info
        cache_info = client.get_cache_info()
        self.assertEqual(cache_info["cached_secrets_count"], 1)
        self.assertIn("secret/data/myapp", cache_info["cached_secret_paths"])

    @patch("gds_vault.vault.requests.get")
    @patch("gds_vault.vault.requests.post")
    def test_get_secret_bypass_cache(self, mock_post, mock_get):
        """Test bypassing cache with use_cache=False."""
        # Mock authentication
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "token", "lease_duration": 3600}
        }

        # Mock secret fetch
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {
            "data": {"data": {"password": "secret123"}}
        }

        client = VaultClient(
            vault_addr="https://vault.com",
            role_id="role",
            secret_id="secret",
        )

        # First call with caching disabled
        client.get_secret("secret/data/myapp", use_cache=False)
        self.assertEqual(mock_get.call_count, 1)

        # Second call should still fetch from Vault
        client.get_secret("secret/data/myapp", use_cache=False)
        self.assertEqual(mock_get.call_count, 2)

    @patch("gds_vault.vault.requests.get")
    @patch("gds_vault.vault.requests.post")
    def test_get_secret_fetch_failure(self, mock_post, mock_get):
        """Test secret fetch failure."""
        # Mock authentication
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "token", "lease_duration": 3600}
        }

        # Mock failed secret fetch
        mock_get.return_value = Mock(ok=False, text="permission denied")

        client = VaultClient(
            vault_addr="https://vault.com",
            role_id="role",
            secret_id="secret",
        )

        with self.assertRaises(VaultError) as context:
            client.get_secret("secret/data/myapp")
        self.assertIn("secret fetch failed", str(context.exception))

    @patch("gds_vault.vault.requests.get")
    @patch("gds_vault.vault.requests.post")
    def test_get_secret_malformed_response(self, mock_post, mock_get):
        """Test malformed response handling."""
        # Mock authentication
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "token", "lease_duration": 3600}
        }

        # Mock malformed response
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"unexpected": "format"}

        client = VaultClient(
            vault_addr="https://vault.com",
            role_id="role",
            secret_id="secret",
        )

        with self.assertRaises(VaultError) as context:
            client.get_secret("secret/data/myapp")
        self.assertIn("Secret data not found", str(context.exception))


class TestVaultClientTokenReuse(unittest.TestCase):
    """Test VaultClient token caching and reuse."""

    @patch("gds_vault.vault.requests.get")
    @patch("gds_vault.vault.requests.post")
    @patch("gds_vault.vault.time.time")
    def test_token_reuse_multiple_secrets(self, mock_time, mock_post, mock_get):
        """Test that token is reused for multiple secret fetches."""
        mock_time.return_value = 1000.0

        # Mock authentication
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "token123", "lease_duration": 3600}
        }

        # Mock secret fetches
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {
            "data": {"data": {"value": "test"}}
        }

        client = VaultClient(
            vault_addr="https://vault.com",
            role_id="role",
            secret_id="secret",
        )

        # Fetch multiple secrets
        client.get_secret("secret/data/app1")
        client.get_secret("secret/data/app2")
        client.get_secret("secret/data/app3")

        # Should authenticate only once
        self.assertEqual(mock_post.call_count, 1)
        # Should fetch 3 secrets
        self.assertEqual(mock_get.call_count, 3)




class TestVaultClientListSecrets(unittest.TestCase):
    """Test VaultClient.list_secrets method."""

    @patch("gds_vault.vault.requests.request")
    @patch("gds_vault.vault.requests.post")
    def test_list_secrets(self, mock_post, mock_request):
        """Test listing secrets."""
        # Mock authentication
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "token", "lease_duration": 3600}
        }

        # Mock list operation
        mock_request.return_value = Mock(ok=True)
        mock_request.return_value.json.return_value = {
            "data": {"keys": ["app1", "app2", "app3"]}
        }

        client = VaultClient(
            vault_addr="https://vault.com",
            role_id="role",
            secret_id="secret",
        )
        secrets = client.list_secrets("secret/metadata")

        self.assertEqual(secrets, ["app1", "app2", "app3"])
        mock_request.assert_called_once_with(
            "LIST",
            "https://vault.com/v1/secret/metadata",
            headers={"X-Vault-Token": "token"},
            timeout=10,
        )

    @patch("gds_vault.vault.requests.request")
    @patch("gds_vault.vault.requests.post")
    def test_list_secrets_failure(self, mock_post, mock_request):
        """Test list operation failure."""
        # Mock authentication
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "token", "lease_duration": 3600}
        }

        # Mock failed list
        mock_request.return_value = Mock(ok=False, text="permission denied")

        client = VaultClient(
            vault_addr="https://vault.com",
            role_id="role",
            secret_id="secret",
        )

        with self.assertRaises(VaultError) as context:
            client.list_secrets("secret/metadata")
        self.assertIn("list operation failed", str(context.exception))


class TestVaultClientCacheManagement(unittest.TestCase):
    """Test VaultClient cache management."""

    @patch("gds_vault.vault.requests.get")
    @patch("gds_vault.vault.requests.post")
    def test_clear_cache(self, mock_post, mock_get):
        """Test clearing cache."""
        # Mock authentication
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "token", "lease_duration": 3600}
        }

        # Mock secret fetch
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {
            "data": {"data": {"value": "test"}}
        }

        client = VaultClient(
            vault_addr="https://vault.com",
            role_id="role",
            secret_id="secret",
        )

        # Fetch some secrets
        client.get_secret("secret/data/app1")
        client.get_secret("secret/data/app2")

        # Verify cache has data
        cache_info = client.get_cache_info()
        self.assertEqual(cache_info["cached_secrets_count"], 2)
        self.assertTrue(cache_info["has_token"])

        # Clear cache
        client.clear_cache()

        # Verify cache is cleared
        cache_info = client.get_cache_info()
        self.assertEqual(cache_info["cached_secrets_count"], 0)
        self.assertFalse(cache_info["has_token"])

    @patch("gds_vault.vault.requests.post")
    def test_get_cache_info(self, mock_post):
        """Test getting cache information."""
        # Mock authentication
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "token", "lease_duration": 3600}
        }

        client = VaultClient(
            vault_addr="https://vault.com",
            role_id="role",
            secret_id="secret",
        )

        # Before authentication
        info = client.get_cache_info()
        self.assertFalse(info["has_token"])
        self.assertFalse(info["token_valid"])
        self.assertEqual(info["cached_secrets_count"], 0)
        self.assertEqual(info["cached_secret_paths"], [])

        # After authentication
        client.authenticate()
        info = client.get_cache_info()
        self.assertTrue(info["has_token"])
        self.assertTrue(info["token_valid"])


class TestVaultClientContextManager(unittest.TestCase):
    """Test VaultClient as context manager."""

    @patch("gds_vault.vault.requests.get")
    @patch("gds_vault.vault.requests.post")
    def test_context_manager(self, mock_post, mock_get):
        """Test using VaultClient as context manager."""
        # Mock authentication
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "token", "lease_duration": 3600}
        }

        # Mock secret fetch
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {
            "data": {"data": {"password": "secret123"}}
        }

        with VaultClient(
            vault_addr="https://vault.com",
            role_id="role",
            secret_id="secret",
        ) as client:
            secret = client.get_secret("secret/data/myapp")
            self.assertEqual(secret, {"password": "secret123"})

            # Cache should have data inside context
            cache_info = client.get_cache_info()
            self.assertEqual(cache_info["cached_secrets_count"], 1)

        # Cache should be cleared after context exit
        cache_info = client.get_cache_info()
        self.assertEqual(cache_info["cached_secrets_count"], 0)
        self.assertFalse(cache_info["has_token"])


if __name__ == "__main__":
    unittest.main()

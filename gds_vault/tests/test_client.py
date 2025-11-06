"""
Comprehensive tests for the VaultClient with OOP improvements.

This test suite covers all aspects of the modern VaultClient including:
- Properties and magic methods
- Authentication strategies
- Caching mechanisms
- Retry logic
- Error handling
- Resource management
"""

import os
import time
import unittest
from unittest.mock import Mock, patch

import requests

from gds_vault import (
    RetryPolicy,
    TokenAuth,
    TTLCache,
    VaultAuthError,
    VaultConnectionError,
    VaultClient,
    VaultConfigurationError,
    VaultPermissionError,
    VaultSecretNotFoundError,
    get_secret_from_vault,
)


class TestVaultClientInitialization(unittest.TestCase):
    """Test VaultClient initialization and configuration."""

    def setUp(self):
        """Set up test environment."""
        # Clear relevant env vars
        for var in ["VAULT_ADDR", "VAULT_ROLE_ID", "VAULT_SECRET_ID"]:
            if var in os.environ:
                del os.environ[var]

    @patch.dict(
        os.environ,
        {
            "VAULT_ADDR": "https://vault.example.com",
            "VAULT_ROLE_ID": "test-role",
            "VAULT_SECRET_ID": "test-secret",
        },
    )
    def test_initialization_from_environment(self):
        """Test client initialization from environment variables."""
        client = VaultClient()
        self.assertEqual(client.vault_addr, "https://vault.example.com")
        self.assertEqual(client.timeout, 10)
        self.assertFalse(client.is_authenticated)

    @patch.dict(os.environ, {"VAULT_ROLE_ID": "role", "VAULT_SECRET_ID": "secret"})
    def test_initialization_with_explicit_vault_addr(self):
        """Test initialization with explicit vault address."""
        client = VaultClient(vault_addr="https://custom.vault.com")
        self.assertEqual(client.vault_addr, "https://custom.vault.com")

    @patch.dict(os.environ, {"VAULT_ROLE_ID": "role", "VAULT_SECRET_ID": "secret"})
    def test_initialization_missing_vault_addr(self):
        """Test that missing VAULT_ADDR raises error."""
        with self.assertRaises(VaultConfigurationError):
            VaultClient()

    @patch.dict(
        os.environ,
        {"VAULT_ADDR": "invalid-url", "VAULT_ROLE_ID": "r", "VAULT_SECRET_ID": "s"},
    )
    def test_initialization_invalid_vault_addr(self):
        """Test that invalid VAULT_ADDR format raises error."""
        with self.assertRaises(VaultConfigurationError):
            VaultClient()

    @patch.dict(
        os.environ,
        {
            "VAULT_ADDR": "https://vault.example.com",
            "VAULT_ROLE_ID": "r",
            "VAULT_SECRET_ID": "s",
        },
    )
    def test_initialization_with_custom_components(self):
        """Test initialization with custom cache and retry policy."""
        cache = TTLCache(max_size=20, default_ttl=120)
        retry = RetryPolicy(max_retries=5)

        client = VaultClient(cache=cache, retry_policy=retry)

        self.assertEqual(len(client), 0)
        self.assertEqual(retry.max_retries, 5)


class TestVaultClientProperties(unittest.TestCase):
    """Test VaultClient properties."""

    @patch.dict(
        os.environ,
        {
            "VAULT_ADDR": "https://vault.example.com",
            "VAULT_ROLE_ID": "r",
            "VAULT_SECRET_ID": "s",
        },
    )
    def setUp(self):
        """Set up client for property tests."""
        self.client = VaultClient()

    def test_vault_addr_property(self):
        """Test vault_addr property."""
        self.assertEqual(self.client.vault_addr, "https://vault.example.com")

    def test_timeout_property_getter(self):
        """Test timeout property getter."""
        self.assertEqual(self.client.timeout, 10)

    def test_timeout_property_setter(self):
        """Test timeout property setter."""
        self.client.timeout = 20
        self.assertEqual(self.client.timeout, 20)

    def test_timeout_property_setter_validation(self):
        """Test timeout setter validates positive values."""
        with self.assertRaises(ValueError):
            self.client.timeout = -5

        with self.assertRaises(ValueError):
            self.client.timeout = 0

    def test_is_authenticated_property(self):
        """Test is_authenticated property."""
        self.assertFalse(self.client.is_authenticated)

        # Simulate authentication
        self.client._token = "test-token"
        self.client._token_expiry = time.time() + 3600
        self.client._authenticated = True

        self.assertTrue(self.client.is_authenticated)

    def test_is_authenticated_expired_token(self):
        """Test is_authenticated with expired token."""
        self.client._token = "test-token"
        self.client._token_expiry = time.time() - 100  # Expired
        self.client._authenticated = True

        self.assertFalse(self.client.is_authenticated)

    def test_cached_secret_count_property(self):
        """Test cached_secret_count property."""
        self.assertEqual(self.client.cached_secret_count, 0)

        # Add secrets to cache
        self.client._cache.set("secret/data/app1", {"key": "value1"})
        self.client._cache.set("secret/data/app2", {"key": "value2"})

        self.assertEqual(self.client.cached_secret_count, 2)

    def test_cache_stats_property(self):
        """Test cache_stats property."""
        stats = self.client.cache_stats
        self.assertIn("size", stats)
        self.assertIn("max_size", stats)
        self.assertEqual(stats["size"], 0)


class TestVaultClientMagicMethods(unittest.TestCase):
    """Test VaultClient magic methods."""

    @patch.dict(
        os.environ,
        {
            "VAULT_ADDR": "https://vault.example.com",
            "VAULT_ROLE_ID": "r",
            "VAULT_SECRET_ID": "s",
        },
    )
    def setUp(self):
        """Set up client for magic method tests."""
        self.client = VaultClient()

    def test_repr(self):
        """Test __repr__ method."""
        repr_str = repr(self.client)
        self.assertIn("VaultClient", repr_str)
        self.assertIn("https://vault.example.com", repr_str)
        self.assertIn("not authenticated", repr_str)

    def test_str(self):
        """Test __str__ method."""
        str_repr = str(self.client)
        self.assertIn("Vault Client", str_repr)
        self.assertIn("https://vault.example.com", str_repr)

    def test_len(self):
        """Test __len__ method."""
        self.assertEqual(len(self.client), 0)

        self.client._cache.set("secret/data/app1", {"key": "value"})
        self.assertEqual(len(self.client), 1)

    def test_contains(self):
        """Test __contains__ method."""
        self.assertNotIn("secret/data/app1", self.client)

        self.client._cache.set("secret/data/app1", {"key": "value"})
        self.assertIn("secret/data/app1", self.client)

    def test_bool(self):
        """Test __bool__ method."""
        # Not authenticated
        self.assertFalse(bool(self.client))

        # Authenticated
        self.client._token = "test-token"
        self.client._token_expiry = time.time() + 3600
        self.client._authenticated = True
        self.assertTrue(bool(self.client))

    @patch.dict(
        os.environ,
        {
            "VAULT_ADDR": "https://vault.example.com",
            "VAULT_ROLE_ID": "r",
            "VAULT_SECRET_ID": "s",
        },
    )
    def test_eq(self):
        """Test __eq__ method."""
        client2 = VaultClient()

        # Same vault address and auth type
        self.assertEqual(self.client, client2)

    @patch.dict(
        os.environ,
        {
            "VAULT_ADDR": "https://other.vault.com",
            "VAULT_ROLE_ID": "r",
            "VAULT_SECRET_ID": "s",
        },
    )
    def test_eq_different_addr(self):
        """Test __eq__ with different vault addresses."""
        client2 = VaultClient()
        self.assertNotEqual(self.client, client2)

    def test_hash(self):
        """Test __hash__ method."""
        # Should be hashable for use in sets/dicts
        client_set = {self.client}
        self.assertIn(self.client, client_set)


class TestVaultClientAuthentication(unittest.TestCase):
    """Test VaultClient authentication."""

    @patch.dict(
        os.environ,
        {
            "VAULT_ADDR": "https://vault.example.com",
            "VAULT_ROLE_ID": "test-role",
            "VAULT_SECRET_ID": "test-secret",
        },
    )
    def setUp(self):
        """Set up client for authentication tests."""
        self.client = VaultClient()

    @patch("gds_vault.auth.requests.post")
    def test_successful_authentication(self, mock_post):
        """Test successful authentication."""
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "test-token-123", "lease_duration": 3600}
        }

        result = self.client.authenticate()

        self.assertTrue(result)
        self.assertTrue(self.client.is_authenticated)
        mock_post.assert_called_once()

    @patch("gds_vault.auth.requests.post")
    def test_authentication_failure(self, mock_post):
        """Test authentication failure."""
        mock_post.return_value = Mock(ok=False, text="Invalid credentials")

        with self.assertRaises(VaultAuthError):
            self.client.authenticate()

        self.assertFalse(self.client.is_authenticated)


class TestVaultClientSecretRetrieval(unittest.TestCase):
    """Test VaultClient secret retrieval."""

    @patch.dict(
        os.environ,
        {
            "VAULT_ADDR": "https://vault.example.com",
            "VAULT_ROLE_ID": "test-role",
            "VAULT_SECRET_ID": "test-secret",
        },
    )
    def setUp(self):
        """Set up client for secret retrieval tests."""
        self.client = VaultClient()
        # Simulate authentication
        self.client._token = "test-token"
        self.client._token_expiry = time.time() + 3600
        self.client._authenticated = True

    @patch("gds_vault.client.requests.get")
    def test_get_secret_kv_v2(self, mock_get):
        """Test getting secret from KV v2."""
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {
            "data": {"data": {"password": "secret123", "username": "admin"}}
        }
        mock_get.return_value.raise_for_status = Mock()

        secret = self.client.get_secret("secret/data/myapp")

        self.assertEqual(secret, {"password": "secret123", "username": "admin"})
        mock_get.assert_called_once()

    @patch("gds_vault.client.requests.get")
    def test_get_secret_kv_v1(self, mock_get):
        """Test getting secret from KV v1."""
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {
            "data": {"api_key": "abc123", "endpoint": "https://api.example.com"}
        }
        mock_get.return_value.raise_for_status = Mock()

        secret = self.client.get_secret("secret/myapp")

        self.assertEqual(
            secret, {"api_key": "abc123", "endpoint": "https://api.example.com"}
        )

    @patch("gds_vault.client.requests.get")
    def test_get_secret_with_caching(self, mock_get):
        """Test secret caching."""
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"data": {"data": {"key": "value"}}}
        mock_get.return_value.raise_for_status = Mock()

        # First call - should fetch from Vault
        secret1 = self.client.get_secret("secret/data/app1")
        self.assertEqual(mock_get.call_count, 1)

        # Second call - should use cache
        secret2 = self.client.get_secret("secret/data/app1")
        self.assertEqual(mock_get.call_count, 1)  # No additional call

        self.assertEqual(secret1, secret2)

    @patch("gds_vault.client.requests.get")
    def test_get_secret_without_caching(self, mock_get):
        """Test getting secret with caching disabled."""
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"data": {"data": {"key": "value"}}}
        mock_get.return_value.raise_for_status = Mock()

        # Both calls should fetch from Vault
        self.client.get_secret("secret/data/app1", use_cache=False)
        self.client.get_secret("secret/data/app1", use_cache=False)

        self.assertEqual(mock_get.call_count, 2)

    @patch("gds_vault.client.requests.get")
    def test_get_secret_not_found(self, mock_get):
        """Test VaultSecretNotFoundError for 404."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value.raise_for_status.side_effect = requests.HTTPError(
            response=mock_response
        )

        with self.assertRaises(VaultSecretNotFoundError):
            self.client.get_secret("secret/data/nonexistent")

    @patch("gds_vault.client.requests.get")
    def test_get_secret_permission_denied(self, mock_get):
        """Test VaultPermissionError for 403."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_get.return_value.raise_for_status.side_effect = requests.HTTPError(
            response=mock_response
        )

        with self.assertRaises(VaultPermissionError):
            self.client.get_secret("secret/data/restricted")

    @patch("gds_vault.client.requests.get")
    def test_get_secret_network_error_maps_to_connection_error(self, mock_get):
        """Test RequestException maps to VaultConnectionError."""
        mock_get.side_effect = requests.RequestException("net down")

        with self.assertRaises(VaultConnectionError):
            self.client.get_secret("secret/data/myapp")


class TestVaultClientClassMethods(unittest.TestCase):
    """Test VaultClient class methods (alternative constructors)."""

    @patch.dict(
        os.environ,
        {
            "VAULT_ADDR": "https://vault.example.com",
            "VAULT_ROLE_ID": "r",
            "VAULT_SECRET_ID": "s",
        },
    )
    def test_from_environment(self):
        """Test from_environment class method."""
        client = VaultClient.from_environment()
        self.assertEqual(client.vault_addr, "https://vault.example.com")

    @patch.dict(os.environ, {"VAULT_ROLE_ID": "r", "VAULT_SECRET_ID": "s"})
    def test_from_config(self):
        """Test from_config class method."""
        config = {
            "vault_addr": "https://vault.test.com",
            "timeout": 15,
            "max_retries": 5,
        }

        client = VaultClient.from_config(config)

        self.assertEqual(client.vault_addr, "https://vault.test.com")
        self.assertEqual(client.timeout, 15)

    @patch.dict(os.environ, {"VAULT_ADDR": "https://vault.example.com"})
    def test_from_token(self):
        """Test from_token class method."""
        client = VaultClient.from_token(token="hvs.CAESIF123")

        self.assertIsInstance(client._auth, TokenAuth)


class TestVaultClientSSLBehavior(unittest.TestCase):
    """Test SSL verify propagation in modern client."""

    @patch.dict(
        os.environ,
        {
            "VAULT_ADDR": "https://vault.example.com",
            "VAULT_ROLE_ID": "r",
            "VAULT_SECRET_ID": "s",
        },
    )
    @patch("gds_vault.auth.requests.post")
    @patch("gds_vault.client.requests.get")
    def test_ssl_cert_path_used_for_verify(self, mock_get, mock_post):
        """When ssl_cert_path is set, verify should use that path."""
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "token", "lease_duration": 3600}
        }
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"data": {"data": {"k": "v"}}}

        client = VaultClient(ssl_cert_path="/tmp/ca.pem")
        client.get_secret("secret/data/x", use_cache=False)

        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs.get("verify"), "/tmp/ca.pem")

    @patch.dict(
        os.environ,
        {
            "VAULT_ADDR": "https://vault.example.com",
            "VAULT_ROLE_ID": "r",
            "VAULT_SECRET_ID": "s",
        },
    )
    @patch("gds_vault.auth.requests.post")
    @patch("gds_vault.client.requests.get")
    def test_verify_ssl_false_is_propagated(self, mock_get, mock_post):
        """When verify_ssl is False and no cert path, verify should be False."""
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "token", "lease_duration": 3600}
        }
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"data": {"data": {"k": "v"}}}

        client = VaultClient(verify_ssl=False)
        client.get_secret("secret/data/x", use_cache=False)

        args, kwargs = mock_get.call_args
        self.assertFalse(kwargs.get("verify"))


class TestVaultClientContextManager(unittest.TestCase):
    """Test VaultClient as context manager."""

    @patch.dict(
        os.environ,
        {
            "VAULT_ADDR": "https://vault.example.com",
            "VAULT_ROLE_ID": "r",
            "VAULT_SECRET_ID": "s",
        },
    )
    @patch("gds_vault.auth.requests.post")
    def test_context_manager(self, mock_post):
        """Test using client as context manager."""
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "token", "lease_duration": 3600}
        }

        with VaultClient() as client:
            self.assertIsInstance(client, VaultClient)
            # Client should initialize on enter
            self.assertTrue(client.is_initialized)

    @patch.dict(
        os.environ,
        {
            "VAULT_ADDR": "https://vault.example.com",
            "VAULT_ROLE_ID": "r",
            "VAULT_SECRET_ID": "s",
        },
    )
    def test_context_manager_cleanup(self):
        """Test context manager cleanup."""
        client = VaultClient()
        client._cache.set("secret/data/app1", {"key": "value"})

        with client:
            self.assertEqual(len(client), 1)

        # Cache should be cleared on exit
        self.assertEqual(len(client), 0)


class TestConvenienceFunction(unittest.TestCase):
    """Test get_secret_from_vault convenience function."""

    @patch.dict(
        os.environ,
        {
            "VAULT_ADDR": "https://vault.example.com",
            "VAULT_ROLE_ID": "r",
            "VAULT_SECRET_ID": "s",
        },
    )
    @patch("gds_vault.auth.requests.post")
    @patch("gds_vault.client.requests.get")
    def test_get_secret_from_vault(self, mock_get, mock_post):
        """Test convenience function."""
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "token", "lease_duration": 3600}
        }

        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {
            "data": {"data": {"password": "secret123"}}
        }
        mock_get.return_value.raise_for_status = Mock()

        secret = get_secret_from_vault("secret/data/myapp")

        self.assertEqual(secret, {"password": "secret123"})


if __name__ == "__main__":
    unittest.main()

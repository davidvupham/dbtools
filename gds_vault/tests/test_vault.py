"""Unit tests for gds_vault.vault module."""

import os
import unittest
from unittest.mock import Mock, patch

from gds_vault.vault import VaultError, get_secret_from_vault


class TestVaultError(unittest.TestCase):
    """Test VaultError exception."""

    def test_vault_error_is_exception(self):
        """VaultError should be an Exception."""
        self.assertTrue(issubclass(VaultError, Exception))

    def test_vault_error_message(self):
        """VaultError should store error message."""
        msg = "Test error message"
        error = VaultError(msg)
        self.assertEqual(str(error), msg)


class TestGetSecretFromVault(unittest.TestCase):
    """Test get_secret_from_vault function."""

    def setUp(self):
        """Clear environment variables before each test."""
        env_vars = ["VAULT_ROLE_ID", "VAULT_SECRET_ID", "VAULT_ADDR"]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]

    @patch.dict(
        os.environ,
        {
            "VAULT_ROLE_ID": "test-role-id",
            "VAULT_SECRET_ID": "test-secret-id",
            "VAULT_ADDR": "https://vault.example.com",
        },
    )
    @patch("gds_vault.vault.requests.post")
    @patch("gds_vault.vault.requests.get")
    def test_successful_secret_retrieval_kv_v2(self, mock_get, mock_post):
        """Test successful secret retrieval from KV v2."""
        # Mock AppRole login response
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "test-token-123"}
        }

        # Mock KV v2 secret fetch response
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {
            "data": {"data": {"password": "super-secret-password", "username": "admin"}}
        }

        result = get_secret_from_vault("secret/data/myapp")

        self.assertEqual(
            result, {"password": "super-secret-password", "username": "admin"}
        )

        # Verify API calls
        mock_post.assert_called_once_with(
            "https://vault.example.com/v1/auth/approle/login",
            json={"role_id": "test-role-id", "secret_id": "test-secret-id"},
            timeout=10,
            verify=True,
        )
        mock_get.assert_called_once_with(
            "https://vault.example.com/v1/secret/data/myapp",
            headers={"X-Vault-Token": "test-token-123"},
            timeout=10,
            verify=True,
        )

    @patch.dict(
        os.environ,
        {
            "VAULT_ROLE_ID": "test-role",
            "VAULT_SECRET_ID": "test-secret",
            "VAULT_ADDR": "https://vault.test.com",
        },
    )
    @patch("gds_vault.vault.requests.post")
    @patch("gds_vault.vault.requests.get")
    def test_successful_secret_retrieval_kv_v1(self, mock_get, mock_post):
        """Test successful secret retrieval from KV v1."""
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            "auth": {"client_token": "token-456"}
        }

        # Mock KV v1 response (no nested data.data)
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {
            "data": {"api_key": "abc123", "endpoint": "https://api.example.com"}
        }

        result = get_secret_from_vault("secret/myapp")

        self.assertEqual(
            result, {"api_key": "abc123", "endpoint": "https://api.example.com"}
        )

    def test_missing_role_id_raises_error(self):
        """Test VaultError when VAULT_ROLE_ID is missing."""
        with self.assertRaises(VaultError) as context:
            get_secret_from_vault("secret/data/test")

        self.assertIn(
            "VAULT_ROLE_ID and VAULT_SECRET_ID must be set", str(context.exception)
        )

    @patch.dict(os.environ, {"VAULT_ROLE_ID": "test-role"})
    def test_missing_secret_id_raises_error(self):
        """Test VaultError when VAULT_SECRET_ID is missing."""
        with self.assertRaises(VaultError) as context:
            get_secret_from_vault("secret/data/test")

        self.assertIn(
            "VAULT_ROLE_ID and VAULT_SECRET_ID must be set", str(context.exception)
        )

    @patch.dict(os.environ, {"VAULT_ROLE_ID": "role", "VAULT_SECRET_ID": "secret"})
    def test_missing_vault_addr_raises_error(self):
        """Test VaultError when Vault address is not provided."""
        with self.assertRaises(VaultError) as context:
            get_secret_from_vault("secret/data/test")

        self.assertIn("Vault address must be set", str(context.exception))

    @patch.dict(os.environ, {"VAULT_ROLE_ID": "role", "VAULT_SECRET_ID": "secret"})
    def test_vault_addr_from_vault_addr_env(self):
        """Test using VAULT_ADDR environment variable."""
        os.environ["VAULT_ADDR"] = "https://vault-from-standard.com"

        with patch("gds_vault.vault.requests.post") as mock_post:
            mock_post.return_value = Mock(ok=False, text="Expected for test")

            with self.assertRaises(VaultError):
                get_secret_from_vault("secret/data/test")

            # Verify it used VAULT_ADDR
            self.assertIn("https://vault-from-standard.com", mock_post.call_args[0][0])

    @patch.dict(
        os.environ,
        {
            "VAULT_ROLE_ID": "role",
            "VAULT_SECRET_ID": "secret",
            "VAULT_ADDR": "https://vault.com",
        },
    )
    @patch("gds_vault.vault.requests.post")
    def test_vault_addr_parameter_override(self, mock_post):
        """Test vault_addr parameter overrides environment variables."""
        mock_post.return_value = Mock(ok=False, text="test")

        with self.assertRaises(VaultError):
            get_secret_from_vault("secret/data/test", vault_addr="https://override.com")

        # Should use the parameter
        self.assertIn("https://override.com", mock_post.call_args[0][0])

    @patch.dict(
        os.environ,
        {
            "VAULT_ROLE_ID": "role",
            "VAULT_SECRET_ID": "secret",
            "VAULT_ADDR": "https://vault.com",
        },
    )
    @patch("gds_vault.vault.requests.post")
    def test_approle_login_failure(self, mock_post):
        """Test VaultError on failed AppRole login."""
        mock_post.return_value = Mock(
            ok=False, text="permission denied: invalid credentials"
        )

        with self.assertRaises(VaultError) as context:
            get_secret_from_vault("secret/data/test")

        self.assertIn("Vault AppRole login failed", str(context.exception))
        self.assertIn("permission denied", str(context.exception))

    @patch.dict(
        os.environ,
        {
            "VAULT_ROLE_ID": "role",
            "VAULT_SECRET_ID": "secret",
            "VAULT_ADDR": "https://vault.com",
        },
    )
    @patch("gds_vault.vault.requests.post")
    @patch("gds_vault.vault.requests.get")
    def test_secret_fetch_failure(self, mock_get, mock_post):
        """Test VaultError on failed secret fetch."""
        # Successful login
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {"auth": {"client_token": "token"}}

        # Failed secret fetch
        mock_get.return_value = Mock(ok=False, text="404 not found")

        with self.assertRaises(VaultError) as context:
            get_secret_from_vault("secret/data/nonexistent")

        self.assertIn("Vault secret fetch failed", str(context.exception))
        self.assertIn("404 not found", str(context.exception))

    @patch.dict(
        os.environ,
        {
            "VAULT_ROLE_ID": "role",
            "VAULT_SECRET_ID": "secret",
            "VAULT_ADDR": "https://vault.com",
        },
    )
    @patch("gds_vault.vault.requests.post")
    @patch("gds_vault.vault.requests.get")
    def test_malformed_response_raises_error(self, mock_get, mock_post):
        """Test VaultError when response is malformed."""
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {"auth": {"client_token": "token"}}

        # Response without expected data structure
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"unexpected": "format"}

        with self.assertRaises(VaultError) as context:
            get_secret_from_vault("secret/data/test")

        self.assertIn("Secret data not found", str(context.exception))


if __name__ == "__main__":
    unittest.main()

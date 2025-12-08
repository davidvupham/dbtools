"""Tests for authentication strategies."""

import os
import unittest
from unittest.mock import Mock, patch

from gds_vault.auth import AppRoleAuth, EnvironmentAuth, TokenAuth
from gds_vault.exceptions import VaultAuthError


class TestAppRoleAuth(unittest.TestCase):
    """Test AppRoleAuth strategy."""

    def setUp(self):
        """Clear environment variables."""
        for var in ["VAULT_ROLE_ID", "VAULT_SECRET_ID"]:
            if var in os.environ:
                del os.environ[var]

    def test_init_with_credentials(self):
        """Test initialization with explicit credentials."""
        auth = AppRoleAuth(role_id="test-role", secret_id="test-secret")
        self.assertEqual(auth.role_id, "test-role")
        self.assertEqual(auth.secret_id, "test-secret")

    @patch.dict(os.environ, {"VAULT_ROLE_ID": "env-role", "VAULT_SECRET_ID": "env-secret"})
    def test_init_from_environment(self):
        """Test initialization from environment variables."""
        auth = AppRoleAuth()
        self.assertEqual(auth.role_id, "env-role")
        self.assertEqual(auth.secret_id, "env-secret")

    def test_init_missing_credentials(self):
        """Test that missing credentials raises error."""
        with self.assertRaises(VaultAuthError):
            AppRoleAuth()

    @patch("gds_vault.auth.requests.post")
    def test_successful_authentication(self, mock_post):
        """Test successful authentication."""
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {"auth": {"client_token": "test-token", "lease_duration": 3600}}

        auth = AppRoleAuth(role_id="role", secret_id="secret")
        token, expiry = auth.authenticate("https://vault.example.com", timeout=10)

        self.assertEqual(token, "test-token")
        self.assertIsInstance(expiry, float)
        mock_post.assert_called_once()

    @patch("gds_vault.auth.requests.post")
    def test_failed_authentication(self, mock_post):
        """Test failed authentication."""
        mock_post.return_value = Mock(ok=False, text="Invalid credentials")

        auth = AppRoleAuth(role_id="role", secret_id="secret")

        with self.assertRaises(VaultAuthError):
            auth.authenticate("https://vault.example.com", timeout=10)

    def test_repr(self):
        """Test __repr__ method."""
        auth = AppRoleAuth(role_id="test-role-id", secret_id="secret")
        repr_str = repr(auth)
        self.assertIn("AppRoleAuth", repr_str)
        self.assertIn("test-rol", repr_str)  # Masked

    def test_str(self):
        """Test __str__ method."""
        auth = AppRoleAuth(role_id="role", secret_id="secret")
        self.assertEqual(str(auth), "AppRole Authentication")


class TestTokenAuth(unittest.TestCase):
    """Test TokenAuth strategy."""

    def test_init_with_token(self):
        """Test initialization with token."""
        auth = TokenAuth(token="hvs.CAESIF123", ttl=1800)
        self.assertEqual(auth.token, "hvs.CAESIF123")
        self.assertEqual(auth.ttl, 1800)

    def test_init_missing_token(self):
        """Test that missing token raises error."""
        with self.assertRaises(VaultAuthError):
            TokenAuth(token="")

    def test_authenticate(self):
        """Test authentication returns token."""
        auth = TokenAuth(token="test-token", ttl=3600)
        token, expiry = auth.authenticate("https://vault.example.com", timeout=10)

        self.assertEqual(token, "test-token")
        self.assertIsInstance(expiry, float)

    def test_repr(self):
        """Test __repr__ method."""
        auth = TokenAuth(token="hvs.CAESIF123")
        repr_str = repr(auth)
        self.assertIn("TokenAuth", repr_str)
        self.assertIn("hvs.CAES", repr_str)  # Masked

    def test_str(self):
        """Test __str__ method."""
        auth = TokenAuth(token="token")
        self.assertEqual(str(auth), "Direct Token Authentication")


class TestEnvironmentAuth(unittest.TestCase):
    """Test EnvironmentAuth strategy."""

    def setUp(self):
        """Clear environment variables."""
        if "VAULT_TOKEN" in os.environ:
            del os.environ["VAULT_TOKEN"]

    @patch.dict(os.environ, {"VAULT_TOKEN": "env-token"})
    def test_init_from_environment(self):
        """Test initialization from VAULT_TOKEN."""
        auth = EnvironmentAuth()
        self.assertEqual(auth.token, "env-token")

    def test_init_missing_env_token(self):
        """Test that missing VAULT_TOKEN raises error."""
        with self.assertRaises(VaultAuthError):
            EnvironmentAuth()

    @patch.dict(os.environ, {"VAULT_TOKEN": "env-token"})
    def test_authenticate(self):
        """Test authentication returns token from environment."""
        auth = EnvironmentAuth(ttl=1800)
        token, expiry = auth.authenticate("https://vault.example.com", timeout=10)

        self.assertEqual(token, "env-token")
        self.assertIsInstance(expiry, float)

    @patch.dict(os.environ, {"VAULT_TOKEN": "env-token"})
    def test_repr(self):
        """Test __repr__ method."""
        auth = EnvironmentAuth()
        repr_str = repr(auth)
        self.assertIn("EnvironmentAuth", repr_str)

    @patch.dict(os.environ, {"VAULT_TOKEN": "env-token"})
    def test_str(self):
        """Test __str__ method."""
        auth = EnvironmentAuth()
        self.assertIn("Environment", str(auth))


if __name__ == "__main__":
    unittest.main()

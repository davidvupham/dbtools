"""
Tests for mount point functionality in VaultClient.

This module tests the mount_point parameter and VAULT_MOUNT_POINT
environment variable support across both the modern client.py
and legacy vault.py implementations.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from gds_vault import VaultClient
from gds_vault.auth import AppRoleAuth
from gds_vault.cache import NoOpCache
from gds_vault.exceptions import VaultAuthError
from gds_vault.vault import VaultClient as LegacyVaultClient


class TestMountPointModernClient(unittest.TestCase):
    """Test mount point functionality in modern VaultClient (client.py)."""

    def setUp(self):
        """Set up test environment."""
        # Set required environment variables
        os.environ["VAULT_ADDR"] = "https://vault.example.com"
        os.environ["VAULT_ROLE_ID"] = "test-role-id"
        os.environ["VAULT_SECRET_ID"] = "test-secret-id"

    def tearDown(self):
        """Clean up environment variables."""
        for key in ["VAULT_ADDR", "VAULT_ROLE_ID", "VAULT_SECRET_ID", "VAULT_MOUNT_POINT"]:
            os.environ.pop(key, None)

    def test_mount_point_parameter(self):
        """Test mount_point parameter in constructor."""
        client = VaultClient(mount_point="kv-v2")
        self.assertEqual(client.mount_point, "kv-v2")

    def test_mount_point_env_var(self):
        """Test VAULT_MOUNT_POINT environment variable."""
        os.environ["VAULT_MOUNT_POINT"] = "secret"
        client = VaultClient()
        self.assertEqual(client.mount_point, "secret")

    def test_mount_point_parameter_overrides_env(self):
        """Test that parameter overrides environment variable."""
        os.environ["VAULT_MOUNT_POINT"] = "secret"
        client = VaultClient(mount_point="kv-v2")
        self.assertEqual(client.mount_point, "kv-v2")

    def test_mount_point_none_by_default(self):
        """Test that mount_point is None when not specified."""
        client = VaultClient()
        self.assertIsNone(client.mount_point)

    def test_mount_point_property_setter(self):
        """Test mount_point property setter."""
        client = VaultClient()
        self.assertIsNone(client.mount_point)
        
        client.mount_point = "kv-v2"
        self.assertEqual(client.mount_point, "kv-v2")

    def test_construct_secret_path_without_mount_point(self):
        """Test path construction without mount point."""
        client = VaultClient()
        path = client._construct_secret_path("secret/data/myapp")
        self.assertEqual(path, "secret/data/myapp")

    def test_construct_secret_path_with_mount_point(self):
        """Test path construction with mount point."""
        client = VaultClient(mount_point="kv-v2")
        path = client._construct_secret_path("data/myapp")
        self.assertEqual(path, "kv-v2/data/myapp")

    def test_construct_secret_path_no_duplicate_mount_point(self):
        """Test that mount point is not duplicated if already present."""
        client = VaultClient(mount_point="kv-v2")
        path = client._construct_secret_path("kv-v2/data/myapp")
        self.assertEqual(path, "kv-v2/data/myapp")

    @patch("gds_vault.client.requests.post")
    @patch("gds_vault.client.requests.get")
    def test_get_secret_with_mount_point(self, mock_get, mock_post):
        """Test get_secret prepends mount point to path."""
        # Mock authentication
        mock_post.return_value = MagicMock(
            ok=True,
            json=lambda: {
                "auth": {"client_token": "test-token", "lease_duration": 3600}
            },
        )

        # Mock secret fetch
        mock_get.return_value = MagicMock(
            ok=True,
            json=lambda: {"data": {"data": {"password": "secret123"}}},
        )

        client = VaultClient(mount_point="kv-v2", cache=NoOpCache())
        secret = client.get_secret("data/myapp")

        # Verify the request was made to the correct URL
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("kv-v2/data/myapp", call_args[0][0])
        self.assertEqual(secret, {"password": "secret123"})

    @patch("gds_vault.client.requests.post")
    @patch("gds_vault.client.requests.request")
    def test_list_secrets_with_mount_point(self, mock_request, mock_post):
        """Test list_secrets prepends mount point to path."""
        # Mock authentication
        mock_post.return_value = MagicMock(
            ok=True,
            json=lambda: {
                "auth": {"client_token": "test-token", "lease_duration": 3600}
            },
        )

        # Mock list operation
        mock_request.return_value = MagicMock(
            ok=True,
            json=lambda: {"data": {"keys": ["app1", "app2", "app3"]}},
        )

        client = VaultClient(mount_point="kv-v2")
        secrets = client.list_secrets("metadata/myapp")

        # Verify the request was made to the correct URL
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertIn("kv-v2/metadata/myapp", call_args[0][1])
        self.assertEqual(secrets, ["app1", "app2", "app3"])

    def test_mount_point_in_config(self):
        """Test mount_point is included in configuration."""
        client = VaultClient(mount_point="kv-v2")
        config = client.get_all_config()
        self.assertEqual(config["mount_point"], "kv-v2")

    def test_from_config_with_mount_point(self):
        """Test from_config class method with mount_point."""
        config = {
            "vault_addr": "https://vault.example.com",
            "mount_point": "kv-v2",
            "timeout": 15,
        }
        client = VaultClient.from_config(config)
        self.assertEqual(client.mount_point, "kv-v2")

    @patch("gds_vault.client.requests.post")
    @patch("gds_vault.client.requests.get")
    def test_get_secret_from_vault_with_mount_point(self, mock_get, mock_post):
        """Test convenience function with mount_point parameter."""
        from gds_vault.client import get_secret_from_vault

        # Mock authentication
        mock_post.return_value = MagicMock(
            ok=True,
            json=lambda: {
                "auth": {"client_token": "test-token", "lease_duration": 3600}
            },
        )

        # Mock secret fetch
        mock_get.return_value = MagicMock(
            ok=True,
            json=lambda: {"data": {"data": {"password": "secret123"}}},
        )

        secret = get_secret_from_vault("data/myapp", mount_point="kv-v2")

        # Verify the request was made to the correct URL
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("kv-v2/data/myapp", call_args[0][0])
        self.assertEqual(secret, {"password": "secret123"})


class TestMountPointLegacyClient(unittest.TestCase):
    """Test mount point functionality in legacy VaultClient (vault.py)."""

    def setUp(self):
        """Set up test environment."""
        os.environ["VAULT_ADDR"] = "https://vault.example.com"
        os.environ["VAULT_ROLE_ID"] = "test-role-id"
        os.environ["VAULT_SECRET_ID"] = "test-secret-id"

    def tearDown(self):
        """Clean up environment variables."""
        for key in ["VAULT_ADDR", "VAULT_ROLE_ID", "VAULT_SECRET_ID", "VAULT_MOUNT_POINT"]:
            os.environ.pop(key, None)

    def test_mount_point_parameter(self):
        """Test mount_point parameter in constructor."""
        client = LegacyVaultClient(mount_point="kv-v2")
        self.assertEqual(client.mount_point, "kv-v2")

    def test_mount_point_env_var(self):
        """Test VAULT_MOUNT_POINT environment variable."""
        os.environ["VAULT_MOUNT_POINT"] = "secret"
        client = LegacyVaultClient()
        self.assertEqual(client.mount_point, "secret")

    def test_mount_point_parameter_overrides_env(self):
        """Test that parameter overrides environment variable."""
        os.environ["VAULT_MOUNT_POINT"] = "secret"
        client = LegacyVaultClient(mount_point="kv-v2")
        self.assertEqual(client.mount_point, "kv-v2")

    def test_mount_point_none_by_default(self):
        """Test that mount_point is None when not specified."""
        client = LegacyVaultClient()
        self.assertIsNone(client.mount_point)

    def test_construct_secret_path_without_mount_point(self):
        """Test path construction without mount point."""
        client = LegacyVaultClient()
        path = client._construct_secret_path("secret/data/myapp")
        self.assertEqual(path, "secret/data/myapp")

    def test_construct_secret_path_with_mount_point(self):
        """Test path construction with mount point."""
        client = LegacyVaultClient(mount_point="kv-v2")
        path = client._construct_secret_path("data/myapp")
        self.assertEqual(path, "kv-v2/data/myapp")

    def test_construct_secret_path_no_duplicate_mount_point(self):
        """Test that mount point is not duplicated if already present."""
        client = LegacyVaultClient(mount_point="kv-v2")
        path = client._construct_secret_path("kv-v2/data/myapp")
        self.assertEqual(path, "kv-v2/data/myapp")

    @patch("gds_vault.vault.requests.post")
    @patch("gds_vault.vault.requests.get")
    def test_get_secret_with_mount_point(self, mock_get, mock_post):
        """Test get_secret prepends mount point to path."""
        # Mock authentication
        mock_post.return_value = MagicMock(
            ok=True,
            json=lambda: {
                "auth": {"client_token": "test-token", "lease_duration": 3600}
            },
        )

        # Mock secret fetch
        mock_get.return_value = MagicMock(
            ok=True,
            json=lambda: {"data": {"data": {"password": "secret123"}}},
        )

        client = LegacyVaultClient(mount_point="kv-v2")
        secret = client.get_secret("data/myapp")

        # Verify the request was made to the correct URL
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("kv-v2/data/myapp", call_args[0][0])
        self.assertEqual(secret, {"password": "secret123"})

    @patch("gds_vault.vault.requests.post")
    @patch("gds_vault.vault.requests.request")
    def test_list_secrets_with_mount_point(self, mock_request, mock_post):
        """Test list_secrets prepends mount point to path."""
        # Mock authentication
        mock_post.return_value = MagicMock(
            ok=True,
            json=lambda: {
                "auth": {"client_token": "test-token", "lease_duration": 3600}
            },
        )

        # Mock list operation
        mock_request.return_value = MagicMock(
            ok=True,
            json=lambda: {"data": {"keys": ["app1", "app2", "app3"]}},
        )

        client = LegacyVaultClient(mount_point="kv-v2")
        secrets = client.list_secrets("metadata/myapp")

        # Verify the request was made to the correct URL
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertIn("kv-v2/metadata/myapp", call_args[0][1])
        self.assertEqual(secrets, ["app1", "app2", "app3"])

    @patch("gds_vault.vault.requests.post")
    @patch("gds_vault.vault.requests.get")
    def test_functional_api_with_mount_point(self, mock_get, mock_post):
        """Test functional API get_secret_from_vault with mount_point."""
        from gds_vault.vault import get_secret_from_vault

        # Mock authentication
        mock_post.return_value = MagicMock(
            ok=True,
            json=lambda: {
                "auth": {"client_token": "test-token", "lease_duration": 3600}
            },
        )

        # Mock secret fetch
        mock_get.return_value = MagicMock(
            ok=True,
            json=lambda: {"data": {"data": {"password": "secret123"}}},
        )

        secret = get_secret_from_vault("data/myapp", mount_point="kv-v2")

        # Verify the request was made to the correct URL
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("kv-v2/data/myapp", call_args[0][0])
        self.assertEqual(secret, {"password": "secret123"})

    @patch("gds_vault.vault.requests.post")
    @patch("gds_vault.vault.requests.get")
    def test_functional_api_with_mount_point_env(self, mock_get, mock_post):
        """Test functional API with VAULT_MOUNT_POINT environment variable."""
        from gds_vault.vault import get_secret_from_vault

        os.environ["VAULT_MOUNT_POINT"] = "secret"

        # Mock authentication
        mock_post.return_value = MagicMock(
            ok=True,
            json=lambda: {
                "auth": {"client_token": "test-token", "lease_duration": 3600}
            },
        )

        # Mock secret fetch
        mock_get.return_value = MagicMock(
            ok=True,
            json=lambda: {"data": {"data": {"password": "secret123"}}},
        )

        secret = get_secret_from_vault("data/myapp")

        # Verify the request was made to the correct URL with mount point
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("secret/data/myapp", call_args[0][0])
        self.assertEqual(secret, {"password": "secret123"})


class TestMountPointEdgeCases(unittest.TestCase):
    """Test edge cases for mount point functionality."""

    def setUp(self):
        """Set up test environment."""
        os.environ["VAULT_ADDR"] = "https://vault.example.com"
        os.environ["VAULT_ROLE_ID"] = "test-role-id"
        os.environ["VAULT_SECRET_ID"] = "test-secret-id"

    def tearDown(self):
        """Clean up environment variables."""
        for key in ["VAULT_ADDR", "VAULT_ROLE_ID", "VAULT_SECRET_ID", "VAULT_MOUNT_POINT"]:
            os.environ.pop(key, None)

    def test_empty_mount_point(self):
        """Test empty string mount point is treated as None."""
        client = VaultClient(mount_point="")
        # Empty string should be falsy
        path = client._construct_secret_path("data/myapp")
        self.assertEqual(path, "data/myapp")

    def test_mount_point_with_trailing_slash(self):
        """Test mount point with trailing slash."""
        client = VaultClient(mount_point="kv-v2/")
        path = client._construct_secret_path("data/myapp")
        # Should handle trailing slash gracefully
        self.assertIn("data/myapp", path)

    def test_complex_secret_path_with_mount_point(self):
        """Test complex nested secret paths with mount point."""
        client = VaultClient(mount_point="kv-v2")
        path = client._construct_secret_path("data/team/project/myapp")
        self.assertEqual(path, "kv-v2/data/team/project/myapp")

    def test_mount_point_changes_affect_subsequent_calls(self):
        """Test that changing mount_point affects subsequent operations."""
        client = VaultClient()
        
        # Without mount point
        path1 = client._construct_secret_path("data/myapp")
        self.assertEqual(path1, "data/myapp")
        
        # Set mount point
        client.mount_point = "kv-v2"
        path2 = client._construct_secret_path("data/myapp")
        self.assertEqual(path2, "kv-v2/data/myapp")
        
        # Change mount point
        client.mount_point = "secret"
        path3 = client._construct_secret_path("data/myapp")
        self.assertEqual(path3, "secret/data/myapp")


if __name__ == "__main__":
    unittest.main()

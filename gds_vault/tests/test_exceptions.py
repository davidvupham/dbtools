"""Tests for exception hierarchy."""

import unittest

from gds_vault.exceptions import (
    VaultAuthError,
    VaultCacheError,
    VaultConfigurationError,
    VaultConnectionError,
    VaultError,
    VaultPermissionError,
    VaultSecretNotFoundError,
)


class TestExceptionHierarchy(unittest.TestCase):
    """Test exception class hierarchy."""

    def test_vault_error_is_base(self):
        """Test VaultError is base exception."""
        self.assertTrue(issubclass(VaultError, Exception))

    def test_auth_error_inherits_from_vault_error(self):
        """Test VaultAuthError inherits from VaultError."""
        self.assertTrue(issubclass(VaultAuthError, VaultError))

    def test_connection_error_inherits_from_vault_error(self):
        """Test VaultConnectionError inherits from VaultError."""
        self.assertTrue(issubclass(VaultConnectionError, VaultError))

    def test_secret_not_found_error_inherits_from_vault_error(self):
        """Test VaultSecretNotFoundError inherits from VaultError."""
        self.assertTrue(issubclass(VaultSecretNotFoundError, VaultError))

    def test_permission_error_inherits_from_vault_error(self):
        """Test VaultPermissionError inherits from VaultError."""
        self.assertTrue(issubclass(VaultPermissionError, VaultError))

    def test_configuration_error_inherits_from_vault_error(self):
        """Test VaultConfigurationError inherits from VaultError."""
        self.assertTrue(issubclass(VaultConfigurationError, VaultError))

    def test_cache_error_inherits_from_vault_error(self):
        """Test VaultCacheError inherits from VaultError."""
        self.assertTrue(issubclass(VaultCacheError, VaultError))

    def test_exception_messages(self):
        """Test exceptions store error messages."""
        msg = "Test error message"

        error = VaultError(msg)
        self.assertEqual(str(error), msg)

        auth_error = VaultAuthError(msg)
        self.assertEqual(str(auth_error), msg)

    def test_catch_all_vault_errors(self):
        """Test catching all vault errors with base class."""
        try:
            raise VaultAuthError("Auth failed")
        except VaultError as e:
            self.assertIsInstance(e, VaultError)
            self.assertIsInstance(e, VaultAuthError)

    def test_catch_specific_error(self):
        """Test catching specific error types."""
        try:
            raise VaultSecretNotFoundError("Secret not found")
        except VaultSecretNotFoundError as e:
            self.assertIn("not found", str(e))
        except VaultError:
            self.fail("Should catch specific exception first")


if __name__ == "__main__":
    unittest.main()

"""
Exception classes for gds_vault package.

This module defines a hierarchy of exceptions for different error scenarios,
enabling precise error handling and better debugging.
"""


class VaultError(Exception):
    """
    Base exception for all Vault-related errors.

    This is the parent class for all custom exceptions in the package,
    allowing users to catch all package-specific errors with a single handler.

    Example:
        try:
            client.get_secret("secret/data/myapp")
        except VaultError as e:
            logger.error(f"Vault operation failed: {e}")
    """

    pass


class VaultAuthError(VaultError):
    """
    Exception raised for authentication failures.

    Raised when:
    - AppRole credentials are invalid
    - Token has expired or is invalid
    - Authentication endpoint is unreachable

    Example:
        try:
            client.authenticate()
        except VaultAuthError as e:
            logger.error(f"Authentication failed: {e}")
    """

    pass


class VaultConnectionError(VaultError):
    """
    Exception raised for network/connection errors.

    Raised when:
    - Vault server is unreachable
    - Network timeout occurs
    - DNS resolution fails

    Example:
        try:
            client.get_secret("secret/data/myapp")
        except VaultConnectionError as e:
            logger.error(f"Cannot connect to Vault: {e}")
    """

    pass


class VaultSecretNotFoundError(VaultError):
    """
    Exception raised when a secret is not found.

    Raised when:
    - Secret path does not exist
    - Secret has been deleted
    - Insufficient permissions to read secret

    Example:
        try:
            secret = client.get_secret("secret/data/nonexistent")
        except VaultSecretNotFoundError as e:
            logger.error(f"Secret not found: {e}")
    """

    pass


class VaultPermissionError(VaultError):
    """
    Exception raised for permission/authorization errors.

    Raised when:
    - Token lacks required permissions
    - Policy denies access to secret
    - Token has been revoked

    Example:
        try:
            client.get_secret("secret/data/restricted")
        except VaultPermissionError as e:
            logger.error(f"Permission denied: {e}")
    """

    pass


class VaultConfigurationError(VaultError):
    """
    Exception raised for configuration errors.

    Raised when:
    - Required environment variables are missing
    - Invalid configuration values provided
    - Vault address is malformed

    Example:
        try:
            client = VaultClient(vault_addr="invalid-url")
        except VaultConfigurationError as e:
            logger.error(f"Configuration error: {e}")
    """

    pass


class VaultCacheError(VaultError):
    """
    Exception raised for cache-related errors.

    Raised when:
    - Cache operation fails
    - Cache is corrupted
    - Cache size limits exceeded

    Example:
        try:
            cache.set("key", very_large_secret)
        except VaultCacheError as e:
            logger.warning(f"Caching failed: {e}")
    """

    pass

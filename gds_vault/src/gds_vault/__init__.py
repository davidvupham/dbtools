"""
gds-vault: HashiCorp Vault helper for secret retrieval.

This package provides a modern, production-ready HashiCorp Vault client
with comprehensive OOP design, flexible authentication, caching, and retry logic.
"""

# Main client and convenience function
# Authentication strategies
from gds_vault.auth import AppRoleAuth, EnvironmentAuth, TokenAuth

# Base classes for extensibility
from gds_vault.base import AuthStrategy, Configurable, ResourceManager, SecretProvider

# Cache implementations
from gds_vault.cache import NoOpCache, RotationAwareCache, SecretCache, TTLCache
from gds_vault.client import VaultClient, get_secret_from_vault

# Exceptions
from gds_vault.exceptions import (
    VaultAuthError,
    VaultCacheError,
    VaultConfigurationError,
    VaultConnectionError,
    VaultError,
    VaultPermissionError,
    VaultSecretNotFoundError,
)

# Retry mechanisms
from gds_vault.retry import RetryPolicy, retry_with_backoff

__version__ = "0.2.0"

__all__ = [
    # Core client
    "VaultClient",
    "get_secret_from_vault",
    # Exceptions
    "VaultError",
    "VaultAuthError",
    "VaultConnectionError",
    "VaultSecretNotFoundError",
    "VaultPermissionError",
    "VaultConfigurationError",
    "VaultCacheError",
    # Authentication
    "AppRoleAuth",
    "TokenAuth",
    "EnvironmentAuth",
    # Caching
    "SecretCache",
    "TTLCache",
    "RotationAwareCache",
    "NoOpCache",
    # Retry
    "RetryPolicy",
    "retry_with_backoff",
    # Base classes
    "SecretProvider",
    "AuthStrategy",
    "ResourceManager",
    "Configurable",
]

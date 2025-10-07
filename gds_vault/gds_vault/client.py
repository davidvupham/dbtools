"""
Modern HashiCorp Vault client with comprehensive OOP design.

This module provides a production-ready Vault client that demonstrates
Python OOP best practices including inheritance, composition, proper
encapsulation, and extensive use of magic methods and properties.
"""

import logging
import os
import time
from typing import Any, Optional

import requests

from gds_vault.auth import AppRoleAuth
from gds_vault.base import Configurable, ResourceManager, SecretProvider
from gds_vault.cache import SecretCache
from gds_vault.exceptions import (
    VaultAuthError,
    VaultConfigurationError,
    VaultConnectionError,
    VaultError,
    VaultPermissionError,
    VaultSecretNotFoundError,
)
from gds_vault.retry import RetryPolicy

logger = logging.getLogger(__name__)


class VaultClient(SecretProvider, ResourceManager, Configurable):
    """
    Production-ready HashiCorp Vault client with modern OOP design.

    This client implements multiple interfaces (SecretProvider, ResourceManager,
    Configurable) to provide a well-structured, extensible implementation that
    follows Python best practices.

    Features:
        - Multiple authentication strategies (AppRole, Token, etc.)
        - Configurable caching with TTL support
        - Automatic retry with exponential backoff
        - Context manager support for resource management
        - Comprehensive error handling with specific exceptions
        - Properties for Pythonic attribute access
        - Magic methods for intuitive usage

    Args:
        vault_addr: Vault server address (or None for VAULT_ADDR env var)
        auth: Authentication strategy (defaults to AppRoleAuth from env)
        cache: Cache implementation (defaults to SecretCache)
        retry_policy: Retry policy (defaults to RetryPolicy with 3 retries)
        timeout: Request timeout in seconds (default: 10)
        config: Additional configuration dict

    Example:
        # Basic usage with environment variables
        client = VaultClient()
        secret = client.get_secret('secret/data/myapp')

        # Context manager usage
        with VaultClient() as client:
            secret = client.get_secret('secret/data/myapp')

        # Custom configuration
        from gds_vault.auth import TokenAuth
        from gds_vault.cache import TTLCache

        client = VaultClient(
            vault_addr="https://vault.example.com",
            auth=TokenAuth(token="hvs.CAESIF..."),
            cache=TTLCache(max_size=50, default_ttl=600),
        )
        
        # With SSL certificate
        client = VaultClient(
            vault_addr="https://vault.example.com",
            ssl_cert_path="/path/to/ca-bundle.crt"
        )
        
        # Disable SSL verification (not recommended for production)
        client = VaultClient(
            vault_addr="https://vault.example.com",
            verify_ssl=False
        )
    """

    def __init__(
        self,
        vault_addr: Optional[str] = None,
        auth=None,
        cache=None,
        retry_policy: Optional[RetryPolicy] = None,
        timeout: int = 10,
        config: Optional[dict[str, Any]] = None,
        verify_ssl: bool = True,
        ssl_cert_path: Optional[str] = None,
    ):
        """Initialize Vault client with OOP best practices."""
        # Initialize base classes
        Configurable.__init__(self)
        ResourceManager.__init__(self)

        # Configuration
        self._config = config or {}
        self._vault_addr = vault_addr or os.getenv("VAULT_ADDR")
        self._timeout = timeout
        
        # SSL Configuration
        self._verify_ssl = verify_ssl
        self._ssl_cert_path = ssl_cert_path or os.getenv("VAULT_SSL_CERT")

        # Validate configuration
        self._validate_configuration()

        # Components (composition over inheritance)
        self._auth = auth or AppRoleAuth()
        self._cache = cache if cache is not None else SecretCache()
        self._retry_policy = retry_policy or RetryPolicy(max_retries=3)

        # State
        self._token: Optional[str] = None
        self._token_expiry: Optional[float] = None
        self._initialized = False
        self._authenticated = False

        logger.debug("VaultClient initialized with SSL verification: %s", self._verify_ssl)

    def _validate_configuration(self) -> None:
        """Validate client configuration."""
        if not self._vault_addr:
            raise VaultConfigurationError(
                "Vault address must be provided or set in VAULT_ADDR "
                "environment variable"
            )

        if not self._vault_addr.startswith(("http://", "https://")):
            raise VaultConfigurationError(
                f"Invalid Vault address: {self._vault_addr}. "
                "Must start with http:// or https://"
            )

    # ========================================================================
    # Properties - Pythonic attribute access
    # ========================================================================

    @property
    def vault_addr(self) -> str:
        """Vault server address."""
        return self._vault_addr

    @property
    def timeout(self) -> int:
        """Request timeout in seconds."""
        return self._timeout

    @timeout.setter
    def timeout(self, value: int) -> None:
        """Set request timeout with validation."""
        if value <= 0:
            raise ValueError("Timeout must be positive")
        self._timeout = value
        logger.debug("Timeout updated to %ds", value)

    @property
    def is_authenticated(self) -> bool:
        """Check if client has valid authentication token."""
        if not self._authenticated or not self._token:
            return False

        # Check token expiry
        if self._token_expiry and time.time() >= self._token_expiry:
            logger.debug("Token expired")
            self._authenticated = False
            return False

        return True

    @property
    def is_initialized(self) -> bool:
        """Check if client resources are initialized."""
        return self._initialized

    @property
    def cached_secret_count(self) -> int:
        """Number of cached secrets."""
        return len(self._cache)

    @property
    def cache_stats(self) -> dict[str, Any]:
        """Cache statistics."""
        return self._cache.get_stats()
    
    @property
    def verify_ssl(self) -> bool:
        """Whether SSL certificate verification is enabled."""
        return self._verify_ssl
    
    @verify_ssl.setter
    def verify_ssl(self, value: bool) -> None:
        """Set SSL verification (use with caution in production)."""
        self._verify_ssl = value
        logger.warning("SSL verification set to: %s", value)
    
    @property
    def ssl_cert_path(self) -> Optional[str]:
        """Path to SSL certificate bundle."""
        return self._ssl_cert_path
    
    @ssl_cert_path.setter
    def ssl_cert_path(self, value: Optional[str]) -> None:
        """Set SSL certificate path."""
        self._ssl_cert_path = value
        logger.info("SSL certificate path set to: %s", value)

    # ========================================================================
    # SecretProvider interface implementation
    # ========================================================================

    def authenticate(self) -> bool:
        """
        Authenticate with Vault using configured auth strategy.

        Returns:
            bool: True if authentication successful

        Raises:
            VaultAuthError: If authentication fails
        """
        try:
            logger.info("Authenticating with Vault at %s", self._vault_addr)

            def _auth():
                # Pass SSL configuration to auth strategy
                return self._auth.authenticate(
                    self._vault_addr, 
                    self._timeout,
                    verify_ssl=self._verify_ssl,
                    ssl_cert_path=self._ssl_cert_path
                )

            self._token, self._token_expiry = self._retry_policy.execute(_auth)
            self._authenticated = True

            logger.info("Successfully authenticated with Vault")
            return True

        except Exception as e:
            logger.error("Authentication failed: %s", e)
            self._authenticated = False
            raise VaultAuthError(f"Authentication failed: {e}") from e

    def get_secret(
        self, path: str, use_cache: bool = True, version: Optional[int] = None, **kwargs
    ) -> dict[str, Any]:
        """
        Retrieve a secret from Vault.

        Args:
            path: Path to the secret (e.g., 'secret/data/myapp')
            use_cache: Whether to use cached secret if available
            version: Specific version to retrieve (KV v2 only)
            **kwargs: Additional options

        Returns:
            dict: Secret data as key-value pairs

        Raises:
            VaultSecretNotFoundError: If secret not found
            VaultPermissionError: If access denied
            VaultConnectionError: If connection fails
            VaultError: For other errors
        """
        cache_key = f"{path}:v{version}" if version else path

        # Check cache first
        if use_cache:
            cached = self._cache.get(cache_key)
            if cached is not None:
                logger.debug("Cache hit for secret: %s", path)
                return cached

        # Fetch from Vault
        logger.info("Fetching secret from Vault: %s", path)

        def _fetch():
            return self._fetch_secret_from_vault(path, version)

        try:
            secret_data = self._retry_policy.execute(_fetch)
        except requests.HTTPError as e:
            # Parse HTTP errors into specific exception types
            if e.response.status_code == 404:
                raise VaultSecretNotFoundError(f"Secret not found: {path}") from e
            elif e.response.status_code == 403:
                raise VaultPermissionError(
                    f"Permission denied for secret: {path}"
                ) from e
            else:
                raise VaultError(f"Failed to fetch secret {path}: {e}") from e
        except requests.RequestException as e:
            raise VaultConnectionError(f"Failed to connect to Vault: {e}") from e

        # Cache the secret
        if use_cache:
            self._cache.set(cache_key, secret_data)
            logger.debug("Cached secret: %s", cache_key)

        return secret_data

    def _fetch_secret_from_vault(
        self, secret_path: str, version: Optional[int] = None
    ) -> dict[str, Any]:
        """
        Internal method to fetch secret from Vault.

        Args:
            secret_path: Path to the secret
            version: Specific version to retrieve

        Returns:
            dict: Secret data

        Raises:
            requests.HTTPError: If HTTP request fails
            VaultError: If response format is unexpected
        """
        # Ensure authenticated
        if not self.is_authenticated:
            self.authenticate()

        secret_url = f"{self._vault_addr}/v1/{secret_path}"
        headers = {"X-Vault-Token": self._token}
        params = {"version": version} if version else None
        
        # Configure SSL verification
        verify = self._ssl_cert_path if self._ssl_cert_path else self._verify_ssl

        resp = requests.get(
            secret_url, headers=headers, params=params, timeout=self._timeout,
            verify=verify
        )
        resp.raise_for_status()

        data = resp.json()

        # Support both KV v1 and v2
        if "data" in data and "data" in data["data"]:
            # KV v2
            logger.debug("Successfully fetched KV v2 secret: %s", secret_path)
            return data["data"]["data"]
        elif "data" in data:
            # KV v1
            logger.debug("Successfully fetched KV v1 secret: %s", secret_path)
            return data["data"]
        else:
            raise VaultError(f"Unexpected response format for secret {secret_path}")

    # ========================================================================
    # Additional Vault operations
    # ========================================================================

    def list_secrets(self, path: str) -> list[str]:
        """
        List secrets at the given path.

        Args:
            path: Path to list (e.g., 'secret/metadata/myapp')

        Returns:
            list: List of secret names

        Raises:
            VaultError: If list operation fails
        """
        logger.info("Listing secrets at path: %s", path)

        def _list():
            if not self.is_authenticated:
                self.authenticate()

            list_url = f"{self._vault_addr}/v1/{path}"
            headers = {"X-Vault-Token": self._token}
            
            # Configure SSL verification
            verify = self._ssl_cert_path if self._ssl_cert_path else self._verify_ssl

            resp = requests.request(
                "LIST", list_url, headers=headers, timeout=self._timeout,
                verify=verify
            )
            resp.raise_for_status()
            return resp.json()

        try:
            data = self._retry_policy.execute(_list)
            keys = data.get("data", {}).get("keys", [])
            logger.info("Found %d secrets at %s", len(keys), path)
            return keys
        except requests.RequestException as e:
            raise VaultConnectionError(f"Failed to list secrets at {path}: {e}") from e

    # ========================================================================
    # ResourceManager interface implementation
    # ========================================================================

    def initialize(self) -> None:
        """Initialize client resources."""
        logger.debug("Initializing VaultClient resources")
        self._initialized = True
        # Optionally pre-authenticate
        if not self.is_authenticated:
            try:
                self.authenticate()
            except VaultAuthError:
                logger.warning("Pre-authentication failed during initialization")

    def cleanup(self) -> None:
        """Clean up client resources."""
        logger.debug("Cleaning up VaultClient resources")
        self.clear_cache()
        self._token = None
        self._token_expiry = None
        self._authenticated = False
        self._initialized = False

    # ========================================================================
    # Configurable interface implementation
    # ========================================================================

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value
        logger.debug("Config updated: %s = %s", key, value)

    def get_all_config(self) -> dict[str, Any]:
        """Get all configuration values."""
        return {
            "vault_addr": self._vault_addr,
            "timeout": self._timeout,
            "verify_ssl": self._verify_ssl,
            "ssl_cert_path": self._ssl_cert_path,
            "cache_type": type(self._cache).__name__,
            "auth_type": type(self._auth).__name__,
            "retry_max_retries": self._retry_policy.max_retries,
            **self._config,
        }

    # ========================================================================
    # Cache management
    # ========================================================================

    def clear_cache(self) -> None:
        """Clear all cached secrets."""
        self._cache.clear()
        logger.info("Cache cleared")

    def remove_from_cache(self, path: str) -> bool:
        """
        Remove a specific secret from cache.

        Args:
            path: Secret path to remove from cache

        Returns:
            bool: True if removed, False if not in cache
        """
        return self._cache.remove(path)

    # ========================================================================
    # Class methods - Alternative constructors
    # ========================================================================

    @classmethod
    def from_environment(cls, **kwargs) -> "VaultClient":
        """
        Create client using only environment variables.

        Reads VAULT_ADDR, VAULT_ROLE_ID, and VAULT_SECRET_ID from environment.

        Args:
            **kwargs: Additional arguments to pass to constructor

        Returns:
            VaultClient: Configured client

        Example:
            client = VaultClient.from_environment()
        """
        return cls(**kwargs)

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "VaultClient":
        """
        Create client from configuration dictionary.

        Args:
            config: Configuration dictionary with keys:
                - vault_addr: Vault server address
                - timeout: Request timeout
                - max_retries: Maximum retry attempts
                - cache_max_size: Cache size limit

        Returns:
            VaultClient: Configured client

        Example:
            config = {
                "vault_addr": "https://vault.example.com",
                "timeout": 15,
                "max_retries": 5
            }
            client = VaultClient.from_config(config)
        """
        vault_addr = config.get("vault_addr")
        timeout = config.get("timeout", 10)
        max_retries = config.get("max_retries", 3)

        retry_policy = RetryPolicy(max_retries=max_retries)

        return cls(
            vault_addr=vault_addr,
            timeout=timeout,
            retry_policy=retry_policy,
            config=config,
        )

    @classmethod
    def from_token(
        cls, token: str, vault_addr: Optional[str] = None, **kwargs
    ) -> "VaultClient":
        """
        Create client using direct token authentication.

        Args:
            token: Vault token
            vault_addr: Vault server address (or None for env var)
            **kwargs: Additional arguments

        Returns:
            VaultClient: Configured client

        Example:
            client = VaultClient.from_token(
                token="hvs.CAESIF...",
                vault_addr="https://vault.example.com"
            )
        """
        from gds_vault.auth import TokenAuth

        auth = TokenAuth(token=token)
        return cls(vault_addr=vault_addr, auth=auth, **kwargs)

    # ========================================================================
    # Magic methods - Making the class more Pythonic
    # ========================================================================

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        auth_status = "authenticated" if self.is_authenticated else "not authenticated"  # noqa: E501
        return (
            f"VaultClient(vault_addr={self._vault_addr!r}, "
            f"timeout={self._timeout}, {auth_status})"
        )

    def __str__(self) -> str:
        """User-friendly representation."""
        auth_status = "authenticated" if self.is_authenticated else "not authenticated"  # noqa: E501
        return f"Vault Client at {self._vault_addr} ({auth_status})"

    def __len__(self) -> int:
        """Number of cached secrets."""
        return len(self._cache)

    def __contains__(self, secret_path: str) -> bool:
        """Check if secret is in cache."""
        return secret_path in self._cache

    def __bool__(self) -> bool:
        """Truthiness based on authentication status."""
        return self.is_authenticated

    def __eq__(self, other) -> bool:
        """Compare two VaultClient instances."""
        if not isinstance(other, VaultClient):
            return NotImplemented
        return (
            self._vault_addr == other._vault_addr
            and type(self._auth).__name__ == type(other._auth).__name__
        )

    def __hash__(self) -> int:
        """Make VaultClient hashable."""
        return hash((self._vault_addr, type(self._auth).__name__))


# ========================================================================
# Convenience function for backward compatibility
# ========================================================================


def get_secret_from_vault(
    secret_path: str, vault_addr: Optional[str] = None
) -> dict[str, Any]:
    """
    Retrieve a secret from Vault using AppRole authentication.

    This is a convenience function that creates a client, fetches
    the secret, and cleans up resources automatically.

    Args:
        secret_path: Path to the secret (e.g., 'secret/data/myapp')
        vault_addr: Vault address (overrides VAULT_ADDR env var)

    Returns:
        dict: Secret data

    Raises:
        VaultError: On failure to authenticate or fetch secret

    Example:
        secret = get_secret_from_vault('secret/data/myapp')
        password = secret['password']
    """
    with VaultClient(vault_addr=vault_addr) as client:
        return client.get_secret(secret_path)

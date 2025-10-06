"""
Enhanced Vault client with OOP improvements.

This module provides an enhanced Vault client that inherits from base classes
to demonstrate proper OOP inheritance and abstraction.
"""

import logging
import os
import time
from typing import Any, Callable, Optional

import requests

# Import base classes (assuming they're available)
try:
    from gds_snowflake.base import (
        ConfigurableComponent,
        ResourceManager,
        RetryableOperation,
        SecretProvider,
    )
except ImportError:
    # Fallback for standalone usage
    from abc import ABC, abstractmethod

    class SecretProvider(ABC):
        @abstractmethod
        def get_secret(self, path: str, **kwargs) -> dict[str, Any]:
            pass

        @abstractmethod
        def authenticate(self) -> bool:
            pass

        @abstractmethod
        def is_authenticated(self) -> bool:
            pass

    class ConfigurableComponent:
        def __init__(self, config: Optional[dict[str, Any]] = None):
            self.config = config or {}

        def get_config(self, key: str, default: Any = None) -> Any:
            return self.config.get(key, default)

        def set_config(self, key: str, value: Any) -> None:
            self.config[key] = value

    class ResourceManager:
        def __enter__(self):
            self.initialize()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.cleanup()
            return False

        def initialize(self) -> None:
            pass

        def cleanup(self) -> None:
            pass

        def is_initialized(self) -> bool:
            return True

    class RetryableOperation:
        def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
            self.max_retries = max_retries
            self.backoff_factor = backoff_factor


logger = logging.getLogger(__name__)


class VaultError(Exception):
    """Exception raised for Vault operation errors."""


class EnhancedVaultClient(
    SecretProvider, ConfigurableComponent, ResourceManager, RetryableOperation
):
    """
    Enhanced Vault client with proper OOP inheritance.

    Inherits from multiple base classes to demonstrate:
    - SecretProvider interface
    - ConfigurableComponent for settings management
    - ResourceManager for context management
    - RetryableOperation for retry logic
    """

    def __init__(
        self,
        vault_addr: Optional[str] = None,
        role_id: Optional[str] = None,
        secret_id: Optional[str] = None,
        timeout: int = 10,
        config: Optional[dict[str, Any]] = None,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
    ):
        """
        Initialize enhanced Vault client.

        Args:
            vault_addr: Vault server address
            role_id: AppRole role_id
            secret_id: AppRole secret_id
            timeout: Request timeout in seconds
            config: Configuration dictionary
            max_retries: Maximum retry attempts
            backoff_factor: Exponential backoff factor
        """
        # Initialize base classes
        ConfigurableComponent.__init__(self, config)
        RetryableOperation.__init__(self, max_retries, backoff_factor)

        # Vault configuration
        self.vault_addr = vault_addr or os.getenv("VAULT_ADDR")
        self.role_id = role_id or os.getenv("VAULT_ROLE_ID")
        self.secret_id = secret_id or os.getenv("VAULT_SECRET_ID")
        self.timeout = timeout

        # State management
        self._token: Optional[str] = None
        self._token_expiry: Optional[float] = None
        self._secret_cache: dict[str, dict[str, Any]] = {}
        self._initialized = False
        self._authenticated = False

        # Validate configuration
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate Vault configuration."""
        if not self.vault_addr:
            raise VaultError(
                "Vault address must be provided or set in VAULT_ADDR environment variable"
            )

        if not self.role_id or not self.secret_id:
            raise VaultError(
                "VAULT_ROLE_ID and VAULT_SECRET_ID must be provided or set in environment"
            )

    # SecretProvider interface implementation
    def get_secret(self, path: str, **kwargs) -> dict[str, Any]:
        """Retrieve a secret from Vault."""
        use_cache = kwargs.get("use_cache", True)
        version = kwargs.get("version")

        cache_key = f"{path}:v{version}" if version else path

        # Check cache first
        if use_cache and cache_key in self._secret_cache:
            logger.debug("Cache hit for secret: %s", path)
            return self._secret_cache[cache_key]

        # Fetch from Vault with retry logic
        def _fetch_secret():
            return self._fetch_secret_from_vault(path, version)

        # Use retry logic from base class
        try:
            secret_data = self._execute_with_retry_logic(_fetch_secret)
        except Exception as e:
            logger.error(
                "Failed to fetch secret %s after %d retries: %s",
                path,
                self.max_retries,
                e,
            )
            raise VaultError(f"Failed to fetch secret {path}: {e}") from e

        # Cache the secret
        if use_cache:
            self._secret_cache[cache_key] = secret_data
            logger.debug("Cached secret: %s", cache_key)

        return secret_data

    def authenticate(self) -> bool:
        """Authenticate with Vault using AppRole."""
        try:
            self._token = self._authenticate_with_vault()
            self._authenticated = True
            logger.info("Successfully authenticated with Vault")
            return True
        except Exception as e:
            logger.error("Authentication failed: %s", e)
            self._authenticated = False
            return False

    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        if not self._authenticated or not self._token:
            return False

        # Check token expiry
        if self._token_expiry and time.time() >= self._token_expiry:
            logger.debug("Token expired, re-authentication needed")
            self._authenticated = False
            return False

        return True

    # ResourceManager interface implementation
    def initialize(self) -> None:
        """Initialize Vault client resources."""
        logger.debug("Initializing Enhanced Vault client")
        self._initialized = True

    def cleanup(self) -> None:
        """Clean up Vault client resources."""
        logger.debug("Cleaning up Enhanced Vault client")
        self.clear_cache()
        self._initialized = False
        self._authenticated = False

    def is_initialized(self) -> bool:
        """Check if resources are initialized."""
        return self._initialized

    # Enhanced methods with retry logic
    def _execute_with_retry_logic(self, operation: Callable) -> Any:
        """Execute operation with retry logic."""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return operation()
            except Exception as e:
                last_exception = e
                if attempt == self.max_retries:
                    break

                # Calculate delay with exponential backoff
                delay = min(self.backoff_factor**attempt, 60)  # Max 60 seconds
                logger.warning(
                    "Operation failed (attempt %d/%d): %s. Retrying in %.1fs...",
                    attempt + 1,
                    self.max_retries + 1,
                    e,
                    delay,
                )
                time.sleep(delay)

        raise last_exception

    def _authenticate_with_vault(self) -> str:
        """Authenticate with Vault using AppRole."""
        login_url = f"{self.vault_addr}/v1/auth/approle/login"
        login_payload = {"role_id": self.role_id, "secret_id": self.secret_id}

        try:
            resp = requests.post(login_url, json=login_payload, timeout=self.timeout)
        except requests.RequestException as e:
            raise VaultError(f"Failed to connect to Vault: {e}") from e

        if not resp.ok:
            raise VaultError(f"Vault AppRole login failed: {resp.text}")

        auth_data = resp.json()["auth"]
        token = auth_data["client_token"]

        # Cache token with expiry
        lease_duration = auth_data.get("lease_duration", 3600)
        self._token_expiry = (
            time.time() + lease_duration - 300
        )  # 5-minute early refresh

        return token

    def _fetch_secret_from_vault(
        self, secret_path: str, version: Optional[int] = None
    ) -> dict[str, Any]:
        """Fetch secret from Vault."""
        if not self.is_authenticated():
            self.authenticate()

        secret_url = f"{self.vault_addr}/v1/{secret_path}"
        headers = {"X-Vault-Token": self._token}
        params = {"version": version} if version else None

        try:
            resp = requests.get(
                secret_url, headers=headers, params=params, timeout=self.timeout
            )
        except requests.RequestException as e:
            raise VaultError(f"Failed to connect to Vault: {e}") from e

        if not resp.ok:
            raise VaultError(f"Vault secret fetch failed: {resp.text}")

        data = resp.json()

        # Support both KV v1 and v2
        if "data" in data and "data" in data["data"]:
            # KV v2
            return data["data"]["data"]
        if "data" in data:
            # KV v1
            return data["data"]
        raise VaultError("Secret data not found in Vault response")

    def clear_cache(self) -> None:
        """Clear cached token and secrets."""
        cached_count = len(self._secret_cache)
        self._token = None
        self._token_expiry = None
        self._secret_cache.clear()
        logger.info("Cleared cache (removed %d secrets)", cached_count)

    def get_cache_info(self) -> dict[str, Any]:
        """Get information about cached data."""
        return {
            "has_token": self._token is not None,
            "token_valid": self.is_authenticated(),
            "cached_secrets_count": len(self._secret_cache),
            "cached_secret_paths": list(self._secret_cache.keys()),
            "initialized": self._initialized,
            "authenticated": self._authenticated,
        }

    # Configuration management
    def get_vault_config(self) -> dict[str, Any]:
        """Get Vault configuration."""
        return {
            "vault_addr": self.vault_addr,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "backoff_factor": self.backoff_factor,
            "role_id": self.role_id[:4] + "..."
            if self.role_id
            else None,  # Masked for security
            "secret_id": self.secret_id[:4] + "..."
            if self.secret_id
            else None,  # Masked for security
        }

    def update_timeout(self, timeout: int) -> None:
        """Update request timeout."""
        self.timeout = timeout
        self.set_config("timeout", timeout)

    def update_retry_config(self, max_retries: int, backoff_factor: float) -> None:
        """Update retry configuration."""
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.set_config("max_retries", max_retries)
        self.set_config("backoff_factor", backoff_factor)


# Factory function for backward compatibility
def create_vault_client(
    vault_addr: Optional[str] = None,
    role_id: Optional[str] = None,
    secret_id: Optional[str] = None,
    enhanced: bool = True,
) -> Any:
    """
    Factory function to create Vault client.

    Args:
        vault_addr: Vault server address
        role_id: AppRole role_id
        secret_id: AppRole secret_id
        enhanced: Whether to use enhanced client with OOP features

    Returns:
        Vault client instance
    """
    if enhanced:
        return EnhancedVaultClient(
            vault_addr=vault_addr, role_id=role_id, secret_id=secret_id
        )
    # Import original VaultClient for fallback
    from .vault import VaultClient

    return VaultClient(vault_addr=vault_addr, role_id=role_id, secret_id=secret_id)

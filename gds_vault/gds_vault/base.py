"""
Base classes and interfaces for the gds_vault package.

This module provides abstract base classes and protocols that define
the contracts for secret providers, authentication strategies, caching,
and retry mechanisms.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol


class SecretProvider(ABC):
    """
    Abstract base class for secret providers.

    This defines the interface that all secret provider implementations
    must follow, enabling polymorphic usage and easy testing with mocks.

    Example:
        class MySecretProvider(SecretProvider):
            def get_secret(self, path: str, **kwargs) -> dict[str, Any]:
                # Implementation
                pass

            def authenticate(self) -> bool:
                # Implementation
                pass

            def is_authenticated(self) -> bool:
                # Implementation
                pass
    """

    @abstractmethod
    def get_secret(self, path: str, **kwargs) -> dict[str, Any]:
        """
        Retrieve a secret from the provider.

        Args:
            path: Path to the secret
            **kwargs: Additional provider-specific options

        Returns:
            dict: Secret data as key-value pairs

        Raises:
            Exception: If secret retrieval fails
        """
        pass

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the secret provider.

        Returns:
            bool: True if authentication successful, False otherwise

        Raises:
            Exception: If authentication fails
        """
        pass

    @abstractmethod
    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated with valid credentials.

        Returns:
            bool: True if authenticated with valid credentials
        """
        pass


class AuthStrategy(ABC):
    """
    Abstract base class for authentication strategies.

    This enables the Strategy pattern for different authentication methods
    (AppRole, Token, Kubernetes, etc.) without modifying the client code.

    Example:
        class AppRoleAuth(AuthStrategy):
            def __init__(self, role_id: str, secret_id: str):
                self.role_id = role_id
                self.secret_id = secret_id

            def authenticate(self, vault_addr: str, timeout: int) -> tuple[str, float]:
                # Implementation returns (token, expiry_time)
                pass
    """

    @abstractmethod
    def authenticate(
        self,
        vault_addr: str,
        timeout: int,
        verify_ssl: bool = True,
        ssl_cert_path: Optional[str] = None,
    ) -> tuple[str, float]:
        """
        Authenticate and return token with expiry.

        Args:
            vault_addr: Vault server address
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates (default: True)
            ssl_cert_path: Path to SSL certificate bundle (optional)

        Returns:
            tuple: (token, expiry_timestamp)

        Raises:
            Exception: If authentication fails
        """
        pass


class CacheProtocol(Protocol):
    """
    Protocol for cache implementations.

    This uses Python's structural subtyping (Protocol) to define
    what methods a cache must implement without requiring inheritance.
    """

    def get(self, key: str) -> Optional[dict[str, Any]]:
        """Get cached value by key."""
        ...

    def set(self, key: str, value: dict[str, Any], **kwargs) -> None:
        """Set cached value for key. Extra kwargs are allowed for extensions."""
        ...

    def clear(self) -> None:
        """Clear all cached values."""
        ...

    def __len__(self) -> int:
        """Return number of cached items."""
        ...

    def __contains__(self, key: str) -> bool:
        """Check if key is in cache."""
        ...


class ResourceManager(ABC):
    """
    Abstract base class for resource management.

    Provides lifecycle management methods for resources that need
    initialization and cleanup (connections, file handles, etc.).
    """

    @abstractmethod
    def initialize(self) -> None:
        """Initialize resources."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources."""
        pass

    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
        return False


class Configurable(ABC):
    """
    Abstract base class for configurable components.

    Provides a standard interface for components that can be
    configured via dictionaries or key-value pairs.
    """

    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        pass

    @abstractmethod
    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value."""
        pass

    @abstractmethod
    def get_all_config(self) -> dict[str, Any]:
        """Get all configuration values."""
        pass

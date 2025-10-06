"""
GDS Vault Exercises - SOLUTIONS
================================

Complete solutions for all exercises. Try to solve them yourself first!
"""

from abc import ABC, abstractmethod
from typing import Optional, Any


# ============================================================================
# EXERCISE 1 SOLUTION: Abstract Base Classes
# ============================================================================

class AuthStrategy(ABC):
    """Abstract base class for authentication strategies."""

    @abstractmethod
    def authenticate(self) -> str:
        """Authenticate and return token."""
        pass


class SimpleTokenAuth(AuthStrategy):
    """Simple token authentication."""

    def __init__(self, token: str):
        self.token = token

    def authenticate(self) -> str:
        """Return the token."""
        return self.token


# ============================================================================
# EXERCISE 2 SOLUTION: Properties
# ============================================================================

class CacheConfig:
    """Configuration for cache."""

    def __init__(self, max_size: Optional[int] = None):
        self._max_size = max_size

    @property
    def max_size(self) -> Optional[int]:
        """Get max_size."""
        return self._max_size

    @max_size.setter
    def max_size(self, value: Optional[int]) -> None:
        """Set max_size with validation."""
        if value is not None and value <= 0:
            raise ValueError("max_size must be positive")
        self._max_size = value

    @property
    def is_unlimited(self) -> bool:
        """Check if cache is unlimited."""
        return self._max_size is None


# ============================================================================
# EXERCISE 3 SOLUTION: Magic Methods
# ============================================================================

class SimpleCache:
    """Simple in-memory cache."""

    def __init__(self):
        self._cache = {}

    def __len__(self) -> int:
        """Return number of cached items."""
        return len(self._cache)

    def __contains__(self, key: str) -> bool:
        """Check if key is in cache."""
        return key in self._cache

    def __getitem__(self, key: str) -> Any:
        """Get cached value by key."""
        return self._cache[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set cached value for key."""
        self._cache[key] = value

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"SimpleCache(size={len(self)})"


# ============================================================================
# EXERCISE 4 SOLUTION: Context Managers
# ============================================================================

class SimpleClient:
    """Simple client with context manager support."""

    def __init__(self):
        self._connected = False

    def __enter__(self):
        """Enter context manager."""
        self._connected = True
        print("Connected")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self._connected = False
        print("Disconnected")
        return False


# ============================================================================
# EXERCISE 5 SOLUTION: Strategy Pattern
# ============================================================================

class NoOpCache:
    """Cache that doesn't cache anything."""

    def get(self, key: str) -> Optional[Any]:
        """Always returns None."""
        return None

    def set(self, key: str, value: Any) -> None:
        """Does nothing."""
        pass


class MemoryCache:
    """Cache that stores in memory."""

    def __init__(self):
        self._cache = {}

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        self._cache[key] = value


# ============================================================================
# EXERCISE 6 SOLUTION: Exception Hierarchy
# ============================================================================

class SecretError(Exception):
    """Base exception for secret operations."""
    pass


class SecretNotFoundError(SecretError):
    """Secret not found."""
    pass


class SecretPermissionError(SecretError):
    """Permission denied for secret."""
    pass


# ============================================================================
# EXERCISE 7 SOLUTION: Composition
# ============================================================================

class Client:
    """Client that uses composition for caching."""

    def __init__(self, cache):
        self._cache = cache

    def store_secret(self, key: str, value: Any) -> None:
        """Store secret in cache."""
        self._cache.set(key, value)

    def get_secret(self, key: str) -> Optional[Any]:
        """Get secret from cache."""
        return self._cache.get(key)


# ============================================================================
# EXERCISE 8 SOLUTION: Multiple Inheritance
# ============================================================================

class Authenticatable:
    """Mixin for authentication."""

    def __init__(self):
        self._authenticated = False

    def authenticate(self):
        """Authenticate."""
        self._authenticated = True
        print("Authenticated")

    def is_authenticated(self) -> bool:
        """Check if authenticated."""
        return self._authenticated


class Cacheable:
    """Mixin for caching."""

    def __init__(self):
        self._cache = {}

    def clear_cache(self):
        """Clear cache."""
        self._cache.clear()
        print("Cache cleared")


class VaultClient(Authenticatable, Cacheable):
    """Client with both authentication and caching."""

    def __init__(self):
        Authenticatable.__init__(self)
        Cacheable.__init__(self)


# ============================================================================
# EXERCISE 9 SOLUTION: Complete Mini-Client
# ============================================================================

class SecretProvider(ABC):
    """Abstract base for secret providers."""

    @abstractmethod
    def get_secret(self, path: str) -> Optional[dict]:
        """Get secret by path."""
        pass

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with provider."""
        pass


class SecretClient(SecretProvider):
    """Complete secret client implementation."""

    def __init__(self, auth_strategy, cache_strategy):
        self._auth = auth_strategy
        self._cache = cache_strategy
        self._authenticated = False

    def authenticate(self) -> bool:
        """Authenticate using auth strategy."""
        token = self._auth.authenticate()
        self._authenticated = token is not None
        return self._authenticated

    def get_secret(self, path: str) -> Optional[dict]:
        """Get secret (mock implementation)."""
        # Check cache first
        cached = self._cache.get(path)
        if cached:
            return cached

        # Mock: Return dummy secret
        secret = {"password": "secret123", "api_key": "abc123"}

        # Cache it
        self._cache.set(path, secret)

        return secret

    @property
    def is_authenticated(self) -> bool:
        """Check if authenticated."""
        return self._authenticated

    def __enter__(self):
        """Enter context manager."""
        self.authenticate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self._cache.set = lambda k, v: None  # Mock cleanup
        return False

    def __repr__(self) -> str:
        """Developer representation."""
        status = "authenticated" if self._authenticated else "not authenticated"
        return f"SecretClient({status})"

    def __len__(self) -> int:
        """Return number of cached secrets."""
        if hasattr(self._cache, '__len__'):
            return len(self._cache._cache)
        return 0


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    print("Testing all solutions...\n")

    # Test 1
    print("Test 1: Abstract Base Classes")
    auth = SimpleTokenAuth("test-token")
    assert auth.authenticate() == "test-token"
    print("✅ Passed\n")

    # Test 2
    print("Test 2: Properties")
    config = CacheConfig(100)
    assert config.max_size == 100
    assert not config.is_unlimited
    config.max_size = 200
    assert config.max_size == 200
    try:
        config.max_size = -5
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    print("✅ Passed\n")

    # Test 3
    print("Test 3: Magic Methods")
    cache = SimpleCache()
    cache["key1"] = "value1"
    assert len(cache) == 1
    assert "key1" in cache
    assert cache["key1"] == "value1"
    assert "SimpleCache" in repr(cache)
    print("✅ Passed\n")

    # Test 4
    print("Test 4: Context Managers")
    with SimpleClient() as client:
        assert client._connected
    assert not client._connected
    print("✅ Passed\n")

    # Test 5
    print("Test 5: Strategy Pattern")
    noop = NoOpCache()
    noop.set("key", "value")
    assert noop.get("key") is None
    memory = MemoryCache()
    memory.set("key", "value")
    assert memory.get("key") == "value"
    print("✅ Passed\n")

    # Test 6
    print("Test 6: Exception Hierarchy")
    try:
        raise SecretNotFoundError("Not found")
    except SecretError:
        pass
    print("✅ Passed\n")

    # Test 7
    print("Test 7: Composition")
    client = Client(cache=MemoryCache())
    client.store_secret("key", "value")
    assert client.get_secret("key") == "value"
    print("✅ Passed\n")

    # Test 8
    print("Test 8: Multiple Inheritance")
    vault_client = VaultClient()
    vault_client.authenticate()
    assert vault_client.is_authenticated()
    vault_client._cache["key"] = "value"
    vault_client.clear_cache()
    assert len(vault_client._cache) == 0
    print("✅ Passed\n")

    # Test 9
    print("Test 9: Complete Mini-Client")
    with SecretClient(SimpleTokenAuth("token"), MemoryCache()) as client:
        assert client.is_authenticated
        secret = client.get_secret("secret/data/test")
        assert secret is not None
    print("✅ Passed\n")

    print("🎉 All tests passed!")

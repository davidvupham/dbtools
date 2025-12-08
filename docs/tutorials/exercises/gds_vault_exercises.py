"""
GDS Vault Exercises - Learn Python Through Real Code
===================================================

These exercises help you understand the Python concepts used in gds_vault
by building simplified versions of its components.

Complete exercises in order - each builds on previous ones!
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

# ============================================================================
# EXERCISE 1: Abstract Base Classes (Easy)
# ============================================================================
"""
Learn: Abstract Base Classes define contracts that subclasses must follow.

Task: Create an abstract `AuthStrategy` base class with an
      `authenticate()` method. Then create a concrete `SimpleTokenAuth`
      class that implements it.

Expected output:
    auth = SimpleTokenAuth("my-token")
    token = auth.authenticate()
    print(token)  # "my-token"
"""


# TODO: Implement this
class AuthStrategy(ABC):
    """Abstract base class for authentication strategies."""

    pass
    # Add abstract method: authenticate() -> str


# TODO: Implement this
class SimpleTokenAuth(AuthStrategy):
    """Simple token authentication."""

    pass
    # Add __init__(self, token: str)
    # Add authenticate(self) -> str (returns the token)


def test_exercise_1():
    """Test Exercise 1."""
    print("\n" + "=" * 60)
    print("EXERCISE 1: Abstract Base Classes")
    print("=" * 60)

    try:
        auth = SimpleTokenAuth("test-token-123")
        token = auth.authenticate()
        expected = "test-token-123"
        assert token == expected, f"Expected '{expected}', got '{token}'"
        print("✅ Exercise 1 PASSED!")
    except Exception as e:
        print(f"❌ Exercise 1 FAILED: {e}")


# ============================================================================
# EXERCISE 2: Properties (Easy)
# ============================================================================
"""
Learn: Properties provide controlled access to attributes.

Task: Create a `CacheConfig` class with:
      - A `max_size` property that can be read and written
      - Validation: max_size must be positive
      - A `is_unlimited` property that returns True if max_size is None

Expected output:
    config = CacheConfig(max_size=100)
    print(config.max_size)      # 100
    config.max_size = 200       # Works
    config.max_size = -5        # Raises ValueError
    print(config.is_unlimited)  # False
"""


# TODO: Implement this
class CacheConfig:
    """Configuration for cache."""

    def __init__(self, max_size: Optional[int] = None):
        """
        Initialize cache config.

        Args:
            max_size: Maximum cache size (None for unlimited)
        """
        pass  # Store max_size

    # TODO: Add @property for max_size (getter)

    # TODO: Add @property setter for max_size (with validation)

    # TODO: Add @property for is_unlimited (computed property)


def test_exercise_2():
    """Test Exercise 2."""
    print("\n" + "=" * 60)
    print("EXERCISE 2: Properties")
    print("=" * 60)

    try:
        # Test basic usage
        config = CacheConfig(max_size=100)
        assert config.max_size == 100, f"Expected 100, got {config.max_size}"
        assert not config.is_unlimited, "Should not be unlimited"

        # Test setter
        config.max_size = 200
        assert config.max_size == 200, f"Expected 200, got {config.max_size}"

        # Test validation
        try:
            config.max_size = -5
            print("❌ Should have raised ValueError for negative max_size")
            return
        except ValueError:
            pass  # Expected

        # Test unlimited
        config_unlimited = CacheConfig(max_size=None)
        assert config_unlimited.is_unlimited, "Should be unlimited"

        print("✅ Exercise 2 PASSED!")
    except Exception as e:
        print(f"❌ Exercise 2 FAILED: {e}")


# ============================================================================
# EXERCISE 3: Magic Methods (Medium)
# ============================================================================
"""
Learn: Magic methods enable Pythonic usage (len, in, [], etc.)

Task: Create a `SimpleCache` class with:
      - __init__: Initialize empty cache dictionary
      - __len__: Return number of cached items
      - __contains__: Check if key is in cache
      - __getitem__: Get cached value by key
      - __setitem__: Set cached value for key
      - __repr__: Developer-friendly representation

Expected output:
    cache = SimpleCache()
    cache["key1"] = "value1"
    cache["key2"] = "value2"
    print(len(cache))           # 2
    print("key1" in cache)      # True
    print(cache["key1"])        # "value1"
    print(repr(cache))          # "SimpleCache(size=2)"
"""


# TODO: Implement this
class SimpleCache:
    """Simple in-memory cache."""

    def __init__(self):
        """Initialize empty cache."""
        pass  # Create empty dict

    # TODO: Add __len__

    # TODO: Add __contains__

    # TODO: Add __getitem__

    # TODO: Add __setitem__

    # TODO: Add __repr__


def test_exercise_3():
    """Test Exercise 3."""
    print("\n" + "=" * 60)
    print("EXERCISE 3: Magic Methods")
    print("=" * 60)

    try:
        cache = SimpleCache()

        # Test __setitem__ and __len__
        cache["key1"] = "value1"
        cache["key2"] = "value2"
        assert len(cache) == 2, f"Expected length 2, got {len(cache)}"

        # Test __contains__
        assert "key1" in cache, "key1 should be in cache"
        assert "key3" not in cache, "key3 should not be in cache"

        # Test __getitem__
        value = cache["key1"]
        assert value == "value1", f"Expected 'value1', got {value}"

        # Test __repr__
        repr_str = repr(cache)
        msg = "__repr__ should contain 'SimpleCache'"
        assert "SimpleCache" in repr_str, msg

        print("✅ Exercise 3 PASSED!")
    except Exception as e:
        print(f"❌ Exercise 3 FAILED: {e}")


# ============================================================================
# EXERCISE 4: Context Managers (Medium)
# ============================================================================
"""
Learn: Context managers ensure proper resource cleanup.

Task: Create a `SimpleClient` class that:
      - Has __init__, __enter__, and __exit__ methods
      - Tracks if it's connected (self._connected)
      - __enter__: Set _connected = True, print "Connected"
      - __exit__: Set _connected = False, print "Disconnected"
      - Can be used with 'with' statement

Expected output:
    with SimpleClient() as client:
        print(client._connected)  # True
    # Prints "Connected" on enter, "Disconnected" on exit
"""


# TODO: Implement this
class SimpleClient:
    """Simple client with context manager support."""

    def __init__(self):
        """Initialize client."""
        pass  # Set _connected = False

    # TODO: Add __enter__

    # TODO: Add __exit__


def test_exercise_4():
    """Test Exercise 4."""
    print("\n" + "=" * 60)
    print("EXERCISE 4: Context Managers")
    print("=" * 60)

    try:
        client = SimpleClient()
        assert not client._connected, "Should start disconnected"

        with client as c:
            assert c._connected, "Should be connected inside with block"

        assert not client._connected, "Should be disconnected after with block"

        print("✅ Exercise 4 PASSED!")
    except Exception as e:
        print(f"❌ Exercise 4 FAILED: {e}")


# ============================================================================
# EXERCISE 5: Strategy Pattern (Medium)
# ============================================================================
"""
Learn: Strategy pattern enables swappable implementations.

Task: Create multiple cache strategies:
      1. NoOpCache: Does nothing (always returns None)
      2. MemoryCache: Stores in dictionary
      Both implement same interface: get(key) and set(key, value)

Expected output:
    # NoOpCache
    cache = NoOpCache()
    cache.set("key", "value")
    print(cache.get("key"))  # None (doesn't store anything)

    # MemoryCache
    cache = MemoryCache()
    cache.set("key", "value")
    print(cache.get("key"))  # "value"
"""


# TODO: Implement this
class NoOpCache:
    """Cache that doesn't cache anything."""

    def get(self, key: str) -> Optional[Any]:
        """Always returns None."""
        pass

    def set(self, key: str, value: Any) -> None:
        """Does nothing."""
        pass


# TODO: Implement this
class MemoryCache:
    """Cache that stores in memory."""

    def __init__(self):
        """Initialize cache."""
        pass  # Create empty dict

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        pass


def test_exercise_5():
    """Test Exercise 5."""
    print("\n" + "=" * 60)
    print("EXERCISE 5: Strategy Pattern")
    print("=" * 60)

    try:
        # Test NoOpCache
        noop = NoOpCache()
        noop.set("key", "value")
        assert noop.get("key") is None, "NoOpCache should always return None"

        # Test MemoryCache
        memory = MemoryCache()
        memory.set("key", "value")
        result = memory.get("key")
        assert result == "value", f"Expected 'value', got {result}"
        assert memory.get("missing") is None, "Missing key should return None"

        print("✅ Exercise 5 PASSED!")
    except Exception as e:
        print(f"❌ Exercise 5 FAILED: {e}")


# ============================================================================
# EXERCISE 6: Exception Hierarchy (Easy)
# ============================================================================
"""
Learn: Custom exception hierarchies enable precise error handling.

Task: Create an exception hierarchy:
      - SecretError (base)
        - SecretNotFoundError
        - SecretPermissionError

Expected output:
    try:
        raise SecretNotFoundError("Secret not found")
    except SecretError as e:
        print(f"Caught: {e}")  # Can catch specific or base class
"""


# TODO: Implement this
class SecretError(Exception):
    """Base exception for secret operations."""

    pass


# TODO: Implement this
class SecretNotFoundError(SecretError):
    """Secret not found."""

    pass


# TODO: Implement this
class SecretPermissionError(SecretError):
    """Permission denied for secret."""

    pass


def test_exercise_6():
    """Test Exercise 6."""
    print("\n" + "=" * 60)
    print("EXERCISE 6: Exception Hierarchy")
    print("=" * 60)

    try:
        # Test inheritance
        msg1 = "Should inherit from SecretError"
        assert issubclass(SecretNotFoundError, SecretError), msg1
        msg2 = "Should inherit from SecretError"
        assert issubclass(SecretPermissionError, SecretError), msg2

        # Test catching specific exception
        try:
            raise SecretNotFoundError("Not found")
        except SecretNotFoundError as e:
            assert str(e) == "Not found", f"Expected 'Not found', got '{e}'"

        # Test catching base exception
        try:
            raise SecretPermissionError("Permission denied")
        except SecretError as e:  # Catch base class
            expected = "Permission denied"
            assert str(e) == expected, f"Expected '{expected}', got '{e}'"

        print("✅ Exercise 6 PASSED!")
    except Exception as e:
        print(f"❌ Exercise 6 FAILED: {e}")


# ============================================================================
# EXERCISE 7: Composition (Medium)
# ============================================================================
"""
Learn: Composition creates flexible objects from smaller components.

Task: Create a `Client` class that uses composition:
      - Takes a cache strategy in __init__
      - Uses cache.get() and cache.set()
      - Doesn't inherit from cache - just uses it!

Expected output:
    # With MemoryCache
    client = Client(cache=MemoryCache())
    client.store_secret("key", "value")
    print(client.get_secret("key"))  # "value"

    # With NoOpCache
    client = Client(cache=NoOpCache())
    client.store_secret("key", "value")
    print(client.get_secret("key"))  # None
"""


# TODO: Implement this
class Client:
    """Client that uses composition for caching."""

    def __init__(self, cache):
        """
        Initialize client with cache strategy.

        Args:
            cache: Cache implementation (MemoryCache or NoOpCache)
        """
        pass  # Store cache

    def store_secret(self, key: str, value: Any) -> None:
        """Store secret in cache."""
        pass  # Use self._cache.set()

    def get_secret(self, key: str) -> Optional[Any]:
        """Get secret from cache."""
        pass  # Use self._cache.get()


def test_exercise_7():
    """Test Exercise 7."""
    print("\n" + "=" * 60)
    print("EXERCISE 7: Composition")
    print("=" * 60)

    try:
        # Test with MemoryCache
        client1 = Client(cache=MemoryCache())
        client1.store_secret("key", "value")
        result1 = client1.get_secret("key")
        assert result1 == "value", "Should return cached value"

        # Test with NoOpCache
        client2 = Client(cache=NoOpCache())
        client2.store_secret("key", "value")
        result2 = client2.get_secret("key")
        assert result2 is None, "NoOpCache should return None"

        print("✅ Exercise 7 PASSED!")
    except Exception as e:
        print(f"❌ Exercise 7 FAILED: {e}")


# ============================================================================
# EXERCISE 8: Multiple Inheritance (Hard)
# ============================================================================
"""
Learn: Multiple inheritance combines features from multiple base classes.

Task: Create a VaultClient that inherits from:
      1. Authenticatable (has authenticate() method)
      2. Cacheable (has clear_cache() method)

Expected output:
    client = VaultClient()
    client.authenticate()  # From Authenticatable
    client.clear_cache()   # From Cacheable
"""


# TODO: Implement this
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


# TODO: Implement this
class Cacheable:
    """Mixin for caching."""

    def __init__(self):
        self._cache = {}

    def clear_cache(self):
        """Clear cache."""
        self._cache.clear()
        print("Cache cleared")


# TODO: Implement this
class VaultClient(Authenticatable, Cacheable):
    """Client with both authentication and caching."""

    def __init__(self):
        """Initialize both parent classes."""
        pass  # Call __init__ on both parents


def test_exercise_8():
    """Test Exercise 8."""
    print("\n" + "=" * 60)
    print("EXERCISE 8: Multiple Inheritance")
    print("=" * 60)

    try:
        client = VaultClient()

        # Test Authenticatable methods
        assert not client.is_authenticated(), "Should start unauthenticated"
        client.authenticate()
        assert client.is_authenticated(), "Should be authenticated"

        # Test Cacheable methods
        client._cache["key"] = "value"
        assert len(client._cache) == 1, "Cache should have 1 item"
        client.clear_cache()
        assert len(client._cache) == 0, "Cache should be empty"

        print("✅ Exercise 8 PASSED!")
    except Exception as e:
        print(f"❌ Exercise 8 FAILED: {e}")


# ============================================================================
# EXERCISE 9: Complete Mini-Client (Hard)
# ============================================================================
"""
Learn: Combine all concepts to build a complete client.

Task: Create a fully functional `SecretClient` that:
      - Inherits from an abstract `SecretProvider` base class
      - Uses an auth strategy (composition)
      - Uses a cache strategy (composition)
      - Implements get_secret() and authenticate()
      - Works as a context manager
      - Has proper magic methods (__repr__, __len__)

This exercise combines:
- Abstract base classes
- Properties
- Magic methods
- Context managers
- Strategy pattern
- Composition
- Exception handling
"""


# Base class
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


# TODO: Implement this
class SecretClient(SecretProvider):
    """
    Complete secret client implementation.

    Should have:
    - __init__(auth_strategy, cache_strategy)
    - authenticate() -> bool
    - get_secret(path) -> dict
    - __enter__ and __exit__ for context manager
    - __repr__ for representation
    - __len__ for number of cached secrets
    - is_authenticated property
    """

    def __init__(self, auth_strategy, cache_strategy):
        """Initialize with strategies."""
        pass

    # TODO: Implement all required methods


def test_exercise_9():
    """Test Exercise 9."""
    print("\n" + "=" * 60)
    print("EXERCISE 9: Complete Mini-Client")
    print("=" * 60)

    try:
        # Create client with strategies
        auth = SimpleTokenAuth("test-token")
        cache = MemoryCache()

        # Test context manager
        with SecretClient(auth, cache) as client:
            # Test authentication
            assert client.is_authenticated, "Should be authenticated"

            # Test get_secret (mock implementation)
            # In real client, this would call Vault API
            # For this exercise, just return a dummy secret
            secret = client.get_secret("secret/data/test")
            assert secret is not None, "Should return a secret"

            # Test __len__
            assert len(client) >= 0, "__len__ should work"

            # Test __repr__
            repr_str = repr(client)
            msg = "__repr__ should contain class name"
            assert "SecretClient" in repr_str, msg

        print("✅ Exercise 9 PASSED!")
        print("\n🎉 Congratulations! You've completed all exercises!")
    except Exception as e:
        print(f"❌ Exercise 9 FAILED: {e}")


# ============================================================================
# Run All Tests
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("GDS VAULT EXERCISES")
    print("Learn Python Through Real Code")
    print("=" * 60)

    test_exercise_1()
    test_exercise_2()
    test_exercise_3()
    test_exercise_4()
    test_exercise_5()
    test_exercise_6()
    test_exercise_7()
    test_exercise_8()
    test_exercise_9()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

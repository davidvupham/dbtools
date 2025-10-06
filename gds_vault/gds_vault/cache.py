"""
Caching implementations for Vault secrets.

This module provides various caching strategies for Vault secrets,
improving performance and reducing load on the Vault server.
"""

import logging
import time
from typing import Any, Optional

from gds_vault.exceptions import VaultCacheError

logger = logging.getLogger(__name__)


class SecretCache:
    """
    Simple in-memory cache for Vault secrets.

    This cache stores secrets in memory without TTL (time-to-live).
    Secrets remain cached until explicitly cleared or the client is destroyed.

    Args:
        max_size: Maximum number of secrets to cache (default: 100)

    Example:
        cache = SecretCache(max_size=50)
        cache.set("secret/data/app1", {"password": "secret123"})
        secret = cache.get("secret/data/app1")
        if secret:
            print(secret["password"])
    """

    def __init__(self, max_size: int = 100):
        """Initialize the secret cache."""
        if max_size <= 0:
            raise VaultCacheError("Cache max_size must be positive")

        self._cache: dict[str, dict[str, Any]] = {}
        self.max_size = max_size
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[dict[str, Any]]:
        """
        Get cached secret by key.

        Args:
            key: Cache key (typically the secret path)

        Returns:
            Cached secret data or None if not found
        """
        if key in self._cache:
            self._hits += 1
            logger.debug("Cache hit for key: %s", key)
            return self._cache[key]

        self._misses += 1
        logger.debug("Cache miss for key: %s", key)
        return None

    def set(self, key: str, value: dict[str, Any]) -> None:
        """
        Set cached secret for key.

        Args:
            key: Cache key
            value: Secret data to cache

        Raises:
            VaultCacheError: If cache is full and eviction is needed
        """
        if key not in self._cache and len(self._cache) >= self.max_size:
            # Simple FIFO eviction - remove oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            logger.debug("Cache full, evicted key: %s", oldest_key)

        self._cache[key] = value
        logger.debug("Cached secret for key: %s", key)

    def clear(self) -> None:
        """Clear all cached secrets."""
        count = len(self._cache)
        self._cache.clear()
        logger.info("Cleared cache (%d secrets removed)", count)

    def remove(self, key: str) -> bool:
        """
        Remove a specific key from cache.

        Args:
            key: Cache key to remove

        Returns:
            True if key was removed, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug("Removed key from cache: %s", key)
            return True
        return False

    def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            dict: Cache statistics including size, hits, misses, hit rate
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "keys": list(self._cache.keys()),
        }

    def __len__(self) -> int:
        """Return number of cached items."""
        return len(self._cache)

    def __contains__(self, key: str) -> bool:
        """Check if key is in cache."""
        return key in self._cache

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"SecretCache(size={len(self._cache)}, max_size={self.max_size})"

    def __str__(self) -> str:
        """User-friendly representation."""
        return f"Secret Cache ({len(self._cache)}/{self.max_size} entries)"


class TTLCache(SecretCache):
    """
    Time-to-live (TTL) cache for Vault secrets.

    This cache extends SecretCache by adding TTL support. Secrets expire
    after a specified duration and are automatically removed on access.

    Args:
        max_size: Maximum number of secrets to cache
        default_ttl: Default TTL in seconds (default: 300 = 5 minutes)

    Example:
        cache = TTLCache(max_size=50, default_ttl=600)  # 10-minute TTL
        cache.set("secret/data/app1", {"key": "value"}, ttl=300)

        # After 300 seconds, the secret will expire
        secret = cache.get("secret/data/app1")  # Returns None after expiry
    """

    def __init__(self, max_size: int = 100, default_ttl: int = 300):
        """Initialize TTL cache."""
        super().__init__(max_size)
        self.default_ttl = default_ttl
        self._expiry: dict[str, float] = {}

    def get(self, key: str) -> Optional[dict[str, Any]]:
        """
        Get cached secret if not expired.

        Args:
            key: Cache key

        Returns:
            Cached secret or None if not found or expired
        """
        if key in self._cache:
            # Check if expired
            if key in self._expiry and time.time() >= self._expiry[key]:
                logger.debug("Cache entry expired for key: %s", key)
                self.remove(key)
                self._misses += 1
                return None

            self._hits += 1
            logger.debug("Cache hit for key: %s", key)
            return self._cache[key]

        self._misses += 1
        logger.debug("Cache miss for key: %s", key)
        return None

    def set(self, key: str, value: dict[str, Any], ttl: Optional[int] = None) -> None:
        """
        Set cached secret with TTL.

        Args:
            key: Cache key
            value: Secret data to cache
            ttl: Time-to-live in seconds (uses default_ttl if None)
        """
        super().set(key, value)
        ttl = ttl if ttl is not None else self.default_ttl
        self._expiry[key] = time.time() + ttl
        logger.debug("Cached secret for key: %s (TTL: %ds)", key, ttl)

    def remove(self, key: str) -> bool:
        """Remove key from cache and expiry tracking."""
        if key in self._expiry:
            del self._expiry[key]
        return super().remove(key)

    def clear(self) -> None:
        """Clear all cached secrets and expiry data."""
        super().clear()
        self._expiry.clear()

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from cache.

        Returns:
            Number of entries removed
        """
        now = time.time()
        expired_keys = [
            key for key, expiry_time in self._expiry.items() if now >= expiry_time
        ]

        for key in expired_keys:
            self.remove(key)

        if expired_keys:
            logger.info("Cleaned up %d expired cache entries", len(expired_keys))

        return len(expired_keys)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics including TTL information."""
        stats = super().get_stats()
        stats["default_ttl"] = self.default_ttl

        # Calculate average remaining TTL
        now = time.time()
        remaining_ttls = [
            expiry - now for expiry in self._expiry.values() if expiry > now
        ]
        stats["avg_remaining_ttl"] = (
            sum(remaining_ttls) / len(remaining_ttls) if remaining_ttls else 0.0
        )

        return stats

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"TTLCache(size={len(self._cache)}, max_size={self.max_size}, "
            f"default_ttl={self.default_ttl})"
        )

    def __str__(self) -> str:
        """User-friendly representation."""
        return (
            f"TTL Secret Cache ({len(self._cache)}/{self.max_size} entries, "
            f"TTL: {self.default_ttl}s)"
        )


class NoOpCache:
    """
    No-operation cache that doesn't cache anything.

    This is useful for disabling caching without changing client code.
    It implements the same interface but always returns None on get().

    Example:
        cache = NoOpCache()  # Disable caching
        client = VaultClient(cache=cache)
    """

    def get(self, key: str) -> Optional[dict[str, Any]]:
        """Always returns None (no caching)."""
        return None

    def set(self, key: str, value: dict[str, Any], ttl: Optional[int] = None) -> None:
        """Does nothing (no caching)."""
        pass

    def clear(self) -> None:
        """Does nothing (no cache to clear)."""
        pass

    def remove(self, key: str) -> bool:
        """Always returns False (nothing to remove)."""
        return False

    def get_stats(self) -> dict[str, Any]:
        """Return empty stats."""
        return {"type": "no-op", "enabled": False}

    def __len__(self) -> int:
        """Always returns 0."""
        return 0

    def __contains__(self, key: str) -> bool:
        """Always returns False."""
        return False

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return "NoOpCache()"

    def __str__(self) -> str:
        """User-friendly representation."""
        return "No-Op Cache (caching disabled)"

"""
Caching implementations for Vault secrets.

This module provides various caching strategies for Vault secrets,
improving performance and reducing load on the Vault server.
"""

import logging
import threading
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
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[dict[str, Any]]:
        """
        Get cached secret by key.

        Args:
            key: Cache key (typically the secret path)

        Returns:
            Cached secret data or None if not found
        """
        with self._lock:
            if key in self._cache:
                self._hits += 1
                logger.debug("Cache hit for key: %s", key)
                return self._cache[key]

            self._misses += 1
            logger.debug("Cache miss for key: %s", key)
            return None

    def set(self, key: str, value: dict[str, Any], **kwargs) -> None:
        """
        Set cached secret for key.

        Args:
            key: Cache key
            value: Secret data to cache

        Raises:
            VaultCacheError: If cache is full and eviction is needed
        """
        with self._lock:
            if key not in self._cache and len(self._cache) >= self.max_size:
                # Simple FIFO eviction - remove oldest entry
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                logger.debug("Cache full, evicted key: %s", oldest_key)

            self._cache[key] = value
            logger.debug("Cached secret for key: %s", key)

    def clear(self) -> None:
        """Clear all cached secrets."""
        with self._lock:
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
        with self._lock:
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
        with self._lock:
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
        with self._lock:
            return len(self._cache)

    def __contains__(self, key: str) -> bool:
        """Check if key is in cache."""
        with self._lock:
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
        with self._lock:
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

    def set(
        self,
        key: str,
        value: dict[str, Any],
        ttl: Optional[int] = None,
        rotation_metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Set cached secret with TTL.

        Args:
            key: Cache key
            value: Secret data to cache
            ttl: Time-to-live in seconds (uses default_ttl if None)
            rotation_metadata: Optional rotation metadata for TTL calculation
        """
        with self._lock:
            super().set(key, value)

        # Use rotation metadata to calculate TTL if available and no manual TTL provided
        if rotation_metadata and ttl is None:
            try:
                from gds_vault.rotation import calculate_rotation_ttl

                calculated_ttl = calculate_rotation_ttl(
                    rotation_metadata.get("last_rotation"),
                    rotation_metadata.get("schedule"),
                    buffer_minutes=10,  # Default buffer
                )

                effective_ttl = calculated_ttl if calculated_ttl > 0 else self.default_ttl
                logger.debug(
                    "Using rotation-based TTL for %s: %ds (from schedule: %s)",
                    key,
                    effective_ttl,
                    rotation_metadata.get("schedule"),
                )

            except Exception as e:
                logger.debug("Failed to calculate rotation TTL, using default: %s", e)
                effective_ttl = self.default_ttl
        else:
            # Use provided TTL or default
            effective_ttl = ttl if ttl is not None else self.default_ttl

        with self._lock:
            self._expiry[key] = time.time() + effective_ttl
            logger.debug("Cached secret for key: %s (TTL: %ds)", key, effective_ttl)

    def remove(self, key: str) -> bool:
        """Remove key from cache and expiry tracking."""
        with self._lock:
            if key in self._expiry:
                del self._expiry[key]
            return super().remove(key)

    def clear(self) -> None:
        """Clear all cached secrets and expiry data."""
        with self._lock:
            super().clear()
            self._expiry.clear()

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from cache.

        Returns:
            Number of entries removed
        """
        with self._lock:
            now = time.time()
            expired_keys = [key for key, expiry_time in self._expiry.items() if now >= expiry_time]

            for key in expired_keys:
                self.remove(key)

            if expired_keys:
                logger.info("Cleaned up %d expired cache entries", len(expired_keys))

            return len(expired_keys)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics including TTL information."""
        with self._lock:
            stats = super().get_stats()
            stats["default_ttl"] = self.default_ttl

        # Calculate average remaining TTL
        now = time.time()
        remaining_ttls = [expiry - now for expiry in self._expiry.values() if expiry > now]
        stats["avg_remaining_ttl"] = sum(remaining_ttls) / len(remaining_ttls) if remaining_ttls else 0.0

        return stats

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"TTLCache(size={len(self._cache)}, max_size={self.max_size}, default_ttl={self.default_ttl})"

    def __str__(self) -> str:
        """User-friendly representation."""
        return f"TTL Secret Cache ({len(self._cache)}/{self.max_size} entries, TTL: {self.default_ttl}s)"


class RotationAwareCache(SecretCache):
    """
    Rotation-aware cache for Vault secrets with rotation schedule support.

    This cache automatically calculates TTL based on Vault secret rotation schedules
    and cron expressions. Secrets are automatically refreshed before their next
    scheduled rotation with a configurable buffer time.

    Args:
        max_size: Maximum number of secrets to cache
        buffer_minutes: Safety buffer in minutes before rotation (default: 10)
        fallback_ttl: Default TTL when no rotation schedule is available (default: 300)

    Example:
        cache = RotationAwareCache(max_size=50, buffer_minutes=15)

        # Cache with rotation metadata
        rotation_metadata = {
            'last_rotation': '2024-01-01T02:00:00Z',
            'schedule': '0 2 * * *'  # Daily at 2 AM
        }
        cache.set("secret/data/app1", {"key": "value"}, rotation_metadata=rotation_metadata)

        # Secret will be automatically invalidated 15 minutes before next 2 AM
        secret = cache.get("secret/data/app1")  # Returns None if within buffer time
    """

    def __init__(self, max_size: int = 100, buffer_minutes: int = 10, fallback_ttl: int = 300):
        """Initialize rotation-aware cache."""
        super().__init__(max_size)
        self.buffer_minutes = buffer_minutes
        self.fallback_ttl = fallback_ttl

        # Store rotation metadata for each secret
        self._rotation_metadata: dict[str, dict[str, Any]] = {}
        self._expiry: dict[str, float] = {}

    def get(self, key: str) -> Optional[dict[str, Any]]:
        """
        Get cached secret, checking rotation schedule.

        Returns None if secret is expired based on rotation schedule
        or if within buffer time of next rotation.
        """
        # Check if key exists in cache
        with self._lock:
            if key not in self._cache:
                return None

        # Check rotation-based expiration
        if self._is_rotation_expired(key):
            logger.debug("Secret expired due to rotation schedule: %s", key)
            self.remove(key)
            return None

        # Check standard TTL expiration
        if key in self._expiry:
            if time.time() >= self._expiry[key]:
                logger.debug("Secret TTL expired: %s", key)
                self.remove(key)
                return None

        return super().get(key)

    def set(
        self,
        key: str,
        value: dict[str, Any],
        rotation_metadata: Optional[dict[str, Any]] = None,
        ttl: Optional[int] = None,
    ) -> None:
        """
        Set cached secret with optional rotation metadata.

        Args:
            key: Cache key
            value: Secret data to cache
            rotation_metadata: Vault rotation metadata with 'last_rotation' and 'schedule'
            ttl: Manual TTL override (uses rotation schedule if None)
        """
        with self._lock:
            super().set(key, value)

        # Store rotation metadata if provided
        if rotation_metadata:
            with self._lock:
                self._rotation_metadata[key] = rotation_metadata

            # Calculate TTL based on rotation schedule
            try:
                from gds_vault.rotation import calculate_rotation_ttl

                calculated_ttl = calculate_rotation_ttl(
                    rotation_metadata.get("last_rotation"),
                    rotation_metadata.get("schedule"),
                    self.buffer_minutes,
                )

                # Use calculated TTL or fallback
                effective_ttl = calculated_ttl if calculated_ttl > 0 else self.fallback_ttl
                with self._lock:
                    self._expiry[key] = time.time() + effective_ttl

                logger.debug(
                    "Cached secret with rotation-based TTL: %s (TTL: %ds)",
                    key,
                    effective_ttl,
                )

            except Exception as e:
                logger.warning(
                    "Failed to calculate rotation TTL for %s, using fallback: %s",
                    key,
                    e,
                )
                with self._lock:
                    self._expiry[key] = time.time() + self.fallback_ttl
        else:
            # Use manual TTL or fallback
            effective_ttl = ttl if ttl is not None else self.fallback_ttl
            with self._lock:
                self._expiry[key] = time.time() + effective_ttl
            logger.debug("Cached secret with manual TTL: %s (TTL: %ds)", key, effective_ttl)

    def _is_rotation_expired(self, key: str) -> bool:
        """Check if secret is expired based on rotation schedule."""
        if key not in self._rotation_metadata:
            return False

        rotation_data = self._rotation_metadata[key]
        if not rotation_data.get("last_rotation") or not rotation_data.get("schedule"):
            return False

        try:
            from gds_vault.rotation import should_refresh_secret

            return should_refresh_secret(
                rotation_data["last_rotation"],
                rotation_data["schedule"],
                self.buffer_minutes,
            )
        except Exception as e:
            logger.warning("Error checking rotation schedule for %s, assuming expired: %s", key, e)
            return True

    def remove(self, key: str) -> bool:
        """Remove key from cache, rotation metadata, and expiry tracking."""
        with self._lock:
            if key in self._rotation_metadata:
                del self._rotation_metadata[key]
            if key in self._expiry:
                del self._expiry[key]
            return super().remove(key)

    def clear(self) -> None:
        """Clear all cached secrets, rotation metadata, and expiry data."""
        with self._lock:
            super().clear()
            self._rotation_metadata.clear()
            self._expiry.clear()

    def cleanup_expired(self) -> int:
        """Clean up expired secrets based on both TTL and rotation schedules."""
        with self._lock:
            removed_count = 0
            current_time = time.time()

            # Get keys to check (copy to avoid modification during iteration)
            keys_to_check = list(self._cache.keys())

            for key in keys_to_check:
                should_remove = False

                # Check TTL expiration
                if key in self._expiry and current_time >= self._expiry[key]:
                    should_remove = True
                    logger.debug("Removing TTL-expired secret: %s", key)

                # Check rotation expiration
                elif self._is_rotation_expired(key):
                    should_remove = True
                    logger.debug("Removing rotation-expired secret: %s", key)

                if should_remove:
                    self.remove(key)
                    removed_count += 1

            if removed_count > 0:
                logger.info("Cleaned up %d expired secrets", removed_count)

            return removed_count

    def force_refresh_check(self, key: str) -> bool:
        """
        Force check if a secret needs immediate refresh.

        Returns True if secret should be refreshed immediately due to
        rotation schedule, even if still in cache.
        """
        if key not in self._rotation_metadata:
            return False

        return self._is_rotation_expired(key)

    def get_rotation_info(self, key: str) -> Optional[dict[str, Any]]:
        """Get rotation metadata for a cached secret."""
        with self._lock:
            return self._rotation_metadata.get(key)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics including rotation information."""
        with self._lock:
            stats = super().get_stats()
            stats.update(
                {
                    "buffer_minutes": self.buffer_minutes,
                    "fallback_ttl": self.fallback_ttl,
                    "secrets_with_rotation": len(self._rotation_metadata),
                }
            )

        # Calculate secrets needing refresh
        needs_refresh = 0
        for key in self._cache:
            if self._is_rotation_expired(key):
                needs_refresh += 1

        stats["secrets_needing_refresh"] = needs_refresh

        # Calculate average remaining TTL
        current_time = time.time()
        remaining_ttls = [expiry - current_time for expiry in self._expiry.values() if expiry > current_time]
        stats["avg_remaining_ttl"] = sum(remaining_ttls) / len(remaining_ttls) if remaining_ttls else 0.0

        return stats

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"RotationAwareCache(size={len(self._cache)}, max_size={self.max_size}, "
            f"buffer_minutes={self.buffer_minutes}, with_rotation={len(self._rotation_metadata)})"
        )

    def __str__(self) -> str:
        """User-friendly representation."""
        return (
            f"Rotation-Aware Cache ({len(self._cache)}/{self.max_size} entries, "
            f"{len(self._rotation_metadata)} with rotation schedules)"
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

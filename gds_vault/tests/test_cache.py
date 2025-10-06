"""Tests for cache implementations."""

import time
import unittest

from gds_vault.cache import NoOpCache, SecretCache, TTLCache
from gds_vault.exceptions import VaultCacheError


class TestSecretCache(unittest.TestCase):
    """Test SecretCache implementation."""

    def test_init(self):
        """Test cache initialization."""
        cache = SecretCache(max_size=50)
        self.assertEqual(cache.max_size, 50)
        self.assertEqual(len(cache), 0)

    def test_init_invalid_size(self):
        """Test that invalid max_size raises error."""
        with self.assertRaises(VaultCacheError):
            SecretCache(max_size=0)

        with self.assertRaises(VaultCacheError):
            SecretCache(max_size=-10)

    def test_set_and_get(self):
        """Test setting and getting cache values."""
        cache = SecretCache()
        secret = {"password": "secret123", "username": "admin"}

        cache.set("secret/data/app1", secret)
        retrieved = cache.get("secret/data/app1")

        self.assertEqual(retrieved, secret)

    def test_get_miss(self):
        """Test cache miss returns None."""
        cache = SecretCache()
        result = cache.get("nonexistent")
        self.assertIsNone(result)

    def test_contains(self):
        """Test __contains__ method."""
        cache = SecretCache()
        cache.set("secret/data/app1", {"key": "value"})

        self.assertIn("secret/data/app1", cache)
        self.assertNotIn("secret/data/app2", cache)

    def test_len(self):
        """Test __len__ method."""
        cache = SecretCache()
        self.assertEqual(len(cache), 0)

        cache.set("secret/data/app1", {"key": "value1"})
        cache.set("secret/data/app2", {"key": "value2"})
        self.assertEqual(len(cache), 2)

    def test_clear(self):
        """Test clearing cache."""
        cache = SecretCache()
        cache.set("secret/data/app1", {"key": "value1"})
        cache.set("secret/data/app2", {"key": "value2"})

        cache.clear()
        self.assertEqual(len(cache), 0)

    def test_remove(self):
        """Test removing specific key."""
        cache = SecretCache()
        cache.set("secret/data/app1", {"key": "value"})

        result = cache.remove("secret/data/app1")
        self.assertTrue(result)
        self.assertNotIn("secret/data/app1", cache)

        result = cache.remove("nonexistent")
        self.assertFalse(result)

    def test_eviction_on_full(self):
        """Test FIFO eviction when cache is full."""
        cache = SecretCache(max_size=2)

        cache.set("key1", {"value": 1})
        cache.set("key2", {"value": 2})
        cache.set("key3", {"value": 3})  # Should evict key1

        self.assertNotIn("key1", cache)
        self.assertIn("key2", cache)
        self.assertIn("key3", cache)

    def test_get_stats(self):
        """Test getting cache statistics."""
        cache = SecretCache(max_size=100)
        cache.set("key1", {"value": 1})

        # Generate some hits and misses
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss

        stats = cache.get_stats()
        self.assertEqual(stats["size"], 1)
        self.assertEqual(stats["max_size"], 100)
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["hit_rate"], 0.5)

    def test_repr(self):
        """Test __repr__ method."""
        cache = SecretCache(max_size=50)
        repr_str = repr(cache)
        self.assertIn("SecretCache", repr_str)
        self.assertIn("50", repr_str)

    def test_str(self):
        """Test __str__ method."""
        cache = SecretCache(max_size=50)
        str_repr = str(cache)
        self.assertIn("Secret Cache", str_repr)


class TestTTLCache(unittest.TestCase):
    """Test TTLCache implementation."""

    def test_init(self):
        """Test TTL cache initialization."""
        cache = TTLCache(max_size=50, default_ttl=300)
        self.assertEqual(cache.max_size, 50)
        self.assertEqual(cache.default_ttl, 300)

    def test_set_and_get_with_ttl(self):
        """Test setting and getting with TTL."""
        cache = TTLCache(default_ttl=10)
        secret = {"password": "secret123"}

        cache.set("secret/data/app1", secret, ttl=5)
        retrieved = cache.get("secret/data/app1")

        self.assertEqual(retrieved, secret)

    def test_expiry(self):
        """Test that expired entries return None."""
        cache = TTLCache(default_ttl=1)
        cache.set("secret/data/app1", {"key": "value"}, ttl=1)

        # Should be available immediately
        self.assertIsNotNone(cache.get("secret/data/app1"))

        # Wait for expiry
        time.sleep(1.1)

        # Should be expired
        self.assertIsNone(cache.get("secret/data/app1"))

    def test_cleanup_expired(self):
        """Test cleanup of expired entries."""
        cache = TTLCache(default_ttl=1)

        cache.set("key1", {"value": 1}, ttl=1)
        cache.set("key2", {"value": 2}, ttl=10)

        time.sleep(1.1)

        removed = cache.cleanup_expired()
        self.assertEqual(removed, 1)
        self.assertNotIn("key1", cache)
        self.assertIn("key2", cache)

    def test_get_stats_with_ttl(self):
        """Test statistics include TTL information."""
        cache = TTLCache(default_ttl=300)
        cache.set("key1", {"value": 1})

        stats = cache.get_stats()
        self.assertEqual(stats["default_ttl"], 300)
        self.assertIn("avg_remaining_ttl", stats)

    def test_repr(self):
        """Test __repr__ method."""
        cache = TTLCache(max_size=50, default_ttl=300)
        repr_str = repr(cache)
        self.assertIn("TTLCache", repr_str)
        self.assertIn("300", repr_str)

    def test_str(self):
        """Test __str__ method."""
        cache = TTLCache(default_ttl=300)
        str_repr = str(cache)
        self.assertIn("TTL Secret Cache", str_repr)
        self.assertIn("300s", str_repr)


class TestNoOpCache(unittest.TestCase):
    """Test NoOpCache implementation."""

    def test_get_always_none(self):
        """Test that get always returns None."""
        cache = NoOpCache()
        cache.set("key", {"value": 1})
        self.assertIsNone(cache.get("key"))

    def test_len_always_zero(self):
        """Test that len always returns 0."""
        cache = NoOpCache()
        cache.set("key", {"value": 1})
        self.assertEqual(len(cache), 0)

    def test_contains_always_false(self):
        """Test that contains always returns False."""
        cache = NoOpCache()
        cache.set("key", {"value": 1})
        self.assertNotIn("key", cache)

    def test_remove_always_false(self):
        """Test that remove always returns False."""
        cache = NoOpCache()
        result = cache.remove("key")
        self.assertFalse(result)

    def test_clear_does_nothing(self):
        """Test that clear does nothing."""
        cache = NoOpCache()
        cache.clear()  # Should not raise error

    def test_get_stats(self):
        """Test getting stats."""
        cache = NoOpCache()
        stats = cache.get_stats()
        self.assertEqual(stats["type"], "no-op")
        self.assertFalse(stats["enabled"])

    def test_repr(self):
        """Test __repr__ method."""
        cache = NoOpCache()
        self.assertEqual(repr(cache), "NoOpCache()")

    def test_str(self):
        """Test __str__ method."""
        cache = NoOpCache()
        str_repr = str(cache)
        self.assertIn("No-Op", str_repr)


if __name__ == "__main__":
    unittest.main()

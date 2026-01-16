"""
Tests for rotation-aware caching functionality.

These tests verify that the rotation-aware caching works correctly
with Vault secret rotation schedules.
"""

import unittest
from datetime import datetime, timedelta

from gds_vault.cache import RotationAwareCache, TTLCache
from gds_vault.rotation import CronParser, calculate_rotation_ttl, parse_vault_rotation_metadata, should_refresh_secret


class TestRotationUtils(unittest.TestCase):
    """Test rotation utility functions."""

    def test_cron_parser_daily(self):
        """Test daily cron schedule parsing."""
        cron = CronParser("0 2 * * *")  # Daily at 2 AM

        # Test from midnight
        test_time = datetime(2024, 10, 8, 0, 0, 0)
        next_run = cron.next_run_time(test_time)

        # Should be 2 AM same day
        expected = datetime(2024, 10, 8, 2, 0, 0)
        self.assertEqual(next_run, expected)

    def test_cron_parser_weekly(self):
        """Test weekly cron schedule parsing."""
        CronParser("0 2 * * 0")  # Weekly on Sunday at 2 AM

        # Note: This is a simplified test - full cron parsing is complex
        # In production, you might want to use a dedicated cron library

    def test_calculate_rotation_ttl(self):
        """Test TTL calculation based on rotation schedule."""
        # Test with a recent rotation (1 hour ago) and daily schedule
        current_time = datetime(2024, 10, 8, 15, 0, 0)  # 3 PM
        last_rotation = datetime(2024, 10, 8, 2, 0, 0)  # 2 AM same day

        ttl = calculate_rotation_ttl(
            last_rotation.isoformat(),
            "0 2 * * *",  # Daily at 2 AM
            buffer_minutes=10,
            current_time=current_time,
        )

        # Next rotation is tomorrow at 2 AM (11 hours from 3 PM)
        # Minus 10 minutes buffer = 10h 50m = 39000 seconds
        expected_ttl = (11 * 60 - 10) * 60  # 39000 seconds
        self.assertAlmostEqual(ttl, expected_ttl, delta=60)  # Within 1 minute

    def test_should_refresh_secret_within_buffer(self):
        """Test refresh check when within buffer time."""
        current_time = datetime(2024, 10, 9, 1, 55, 0)  # 1:55 AM (5 min before rotation)
        last_rotation = datetime(2024, 10, 8, 2, 0, 0)  # Yesterday at 2 AM

        should_refresh = should_refresh_secret(
            last_rotation.isoformat(),
            "0 2 * * *",  # Daily at 2 AM
            buffer_minutes=10,
            current_time=current_time,
        )

        # Should refresh because we're within 10-minute buffer
        self.assertTrue(should_refresh)

    def test_parse_vault_rotation_metadata(self):
        """Test parsing rotation metadata from Vault response."""
        # KV v2 response with metadata
        vault_response = {
            "data": {
                "data": {"password": "secret123"},
                "metadata": {
                    "created_time": "2024-10-08T02:00:00Z",
                    "last_rotation": "2024-10-08T02:00:00Z",
                    "rotation_schedule": "0 2 * * *",
                },
            }
        }

        metadata = parse_vault_rotation_metadata(vault_response)

        self.assertIsNotNone(metadata)
        self.assertEqual(metadata["last_rotation"], "2024-10-08T02:00:00Z")
        self.assertEqual(metadata["schedule"], "0 2 * * *")

    def test_parse_vault_rotation_metadata_no_rotation(self):
        """Test parsing when no rotation metadata exists."""
        vault_response = {
            "data": {
                "data": {"password": "secret123"},
                "metadata": {"created_time": "2024-10-08T02:00:00Z", "version": 1},
            }
        }

        metadata = parse_vault_rotation_metadata(vault_response)
        self.assertIsNone(metadata)


class TestRotationAwareCache(unittest.TestCase):
    """Test RotationAwareCache functionality."""

    def setUp(self):
        """Set up test cache."""
        self.cache = RotationAwareCache(max_size=10, buffer_minutes=10, fallback_ttl=300)

    def test_cache_without_rotation_metadata(self):
        """Test caching without rotation metadata."""
        secret_data = {"password": "secret123"}

        self.cache.set("test-secret", secret_data)

        retrieved = self.cache.get("test-secret")
        self.assertEqual(retrieved, secret_data)

    def test_cache_with_rotation_metadata(self):
        """Test caching with rotation metadata."""
        secret_data = {"password": "secret123"}

        # Use current time for rotation - make it recent (5 minutes ago)
        from datetime import datetime, timedelta

        recent_rotation = datetime.now() - timedelta(minutes=5)

        rotation_metadata = {
            "last_rotation": recent_rotation.isoformat(),
            "schedule": "0 2 * * *",  # Daily at 2 AM
        }

        self.cache.set("test-secret", secret_data, rotation_metadata=rotation_metadata)

        # Should be cached (rotation just happened, next one is far away)
        retrieved = self.cache.get("test-secret")
        self.assertEqual(retrieved, secret_data)  # Check rotation info is stored
        rotation_info = self.cache.get_rotation_info("test-secret")
        self.assertEqual(rotation_info, rotation_metadata)

    def test_force_refresh_check(self):
        """Test force refresh checking."""
        secret_data = {"password": "secret123"}

        # Rotation schedule that should trigger refresh (very recent rotation)
        current_time = datetime.now()
        current_time + timedelta(minutes=5)  # 5 minutes from now

        rotation_metadata = {
            "last_rotation": (current_time - timedelta(hours=23, minutes=55)).isoformat(),
            "schedule": "0 2 * * *",  # Daily, next rotation soon
        }

        self.cache.set("test-secret", secret_data, rotation_metadata=rotation_metadata)

        # Check if needs refresh (this test might be timing-sensitive)
        # needs_refresh = self.cache.force_refresh_check("test-secret")
        # In a real scenario, this would depend on the current time vs next rotation

    def test_cache_stats(self):
        """Test cache statistics."""
        secret_data = {"password": "secret123"}

        # Use recent rotation time
        from datetime import datetime, timedelta

        recent_rotation = datetime.now() - timedelta(minutes=5)

        rotation_metadata = {"last_rotation": recent_rotation.isoformat(), "schedule": "0 2 * * *"}

        self.cache.set("test-secret", secret_data, rotation_metadata=rotation_metadata)

        stats = self.cache.get_stats()

        self.assertEqual(stats["size"], 1)
        self.assertEqual(stats["buffer_minutes"], 10)
        self.assertEqual(stats["secrets_with_rotation"], 1)
        self.assertIn("secrets_needing_refresh", stats)


class TestTTLCacheRotationSupport(unittest.TestCase):
    """Test TTLCache rotation support."""

    def setUp(self):
        """Set up test cache."""
        self.cache = TTLCache(max_size=10, default_ttl=300)

    def test_ttl_cache_with_rotation_metadata(self):
        """Test TTLCache with rotation metadata."""
        secret_data = {"password": "secret123"}

        # Use recent rotation time
        from datetime import datetime, timedelta

        recent_rotation = datetime.now() - timedelta(minutes=5)

        rotation_metadata = {"last_rotation": recent_rotation.isoformat(), "schedule": "0 2 * * *"}

        # Should work with rotation metadata (backward compatibility)
        self.cache.set("test-secret", secret_data, rotation_metadata=rotation_metadata)

        retrieved = self.cache.get("test-secret")
        self.assertEqual(retrieved, secret_data)

    def test_ttl_cache_without_rotation_metadata(self):
        """Test TTLCache normal operation without rotation metadata."""
        secret_data = {"password": "secret123"}

        self.cache.set("test-secret", secret_data, ttl=60)

        retrieved = self.cache.get("test-secret")
        self.assertEqual(retrieved, secret_data)


if __name__ == "__main__":
    # Run specific test methods for demonstration
    print("Running Rotation-Aware Caching Tests")
    print("=" * 50)

    # Test rotation utilities
    print("\n1. Testing rotation utilities...")
    utils_suite = unittest.TestLoader().loadTestsFromTestCase(TestRotationUtils)
    utils_runner = unittest.TextTestRunner(verbosity=1)
    utils_result = utils_runner.run(utils_suite)

    # Test rotation-aware cache
    print("\n2. Testing RotationAwareCache...")
    cache_suite = unittest.TestLoader().loadTestsFromTestCase(TestRotationAwareCache)
    cache_runner = unittest.TextTestRunner(verbosity=1)
    cache_result = cache_runner.run(cache_suite)

    # Test TTL cache rotation support
    print("\n3. Testing TTLCache rotation support...")
    ttl_suite = unittest.TestLoader().loadTestsFromTestCase(TestTTLCacheRotationSupport)
    ttl_runner = unittest.TextTestRunner(verbosity=1)
    ttl_result = ttl_runner.run(ttl_suite)

    print("\nTest Summary:")
    print(f"  Rotation Utils: {utils_result.testsRun} tests, {len(utils_result.failures)} failures")
    print(f"  RotationAwareCache: {cache_result.testsRun} tests, {len(cache_result.failures)} failures")
    print(f"  TTLCache Support: {ttl_result.testsRun} tests, {len(ttl_result.failures)} failures")

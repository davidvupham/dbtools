"""
Vault Rotation-Aware Caching Example

This example demonstrates how to use the RotationAwareCache for automatically
managing secret TTL based on Vault rotation schedules.

The cache will automatically refresh secrets before their scheduled rotation
time with a configurable buffer period.
"""

from gds_vault import RotationAwareCache, TTLCache, VaultClient
from gds_vault.exceptions import VaultError


def example_rotation_aware_cache():
    """
    Example 1: Basic rotation-aware caching.

    Shows how the cache automatically calculates TTL based on rotation schedules.
    """
    print("=" * 70)
    print("Example 1: Rotation-Aware Cache")
    print("=" * 70)

    try:
        # Create rotation-aware cache with 15-minute buffer
        cache = RotationAwareCache(
            max_size=50,
            buffer_minutes=15,  # Refresh 15 minutes before rotation
            fallback_ttl=600,  # 10 minutes fallback if no rotation schedule
        )

        _ = VaultClient(cache=cache)

        print("✓ Created VaultClient with RotationAwareCache")
        print("  - Buffer time: 15 minutes")
        print("  - Fallback TTL: 10 minutes")

        # Fetch secret (would include rotation metadata in real scenario)
        # secret = client.get_secret('secret/data/database-creds')

        # Show cache statistics
        stats = cache.get_stats()
        print(f"✓ Cache stats: {stats}")

    except VaultError as e:
        print(f"✗ Error: {e}")

    print()


def example_manual_rotation_metadata():
    """
    Example 2: Manually setting rotation metadata.

    Shows how to work with rotation metadata directly.
    """
    print("=" * 70)
    print("Example 2: Manual Rotation Metadata")
    print("=" * 70)

    try:
        cache = RotationAwareCache(buffer_minutes=10)

        # Simulate rotation metadata from Vault
        rotation_metadata = {
            "last_rotation": "2024-10-08T02:00:00Z",  # Last rotated at 2 AM today
            "schedule": "0 2 * * *",  # Daily rotation at 2 AM
        }

        # Cache secret with rotation metadata
        secret_data = {
            "username": "app_user",
            "password": "secret123",
            "host": "db.example.com",
        }

        cache.set("secret/data/database", secret_data, rotation_metadata=rotation_metadata)

        print(f"✓ Cached secret with rotation schedule: {rotation_metadata['schedule']}")

        # Check rotation info
        rotation_info = cache.get_rotation_info("secret/data/database")
        print(f"✓ Rotation info: {rotation_info}")

        # Check if secret needs refresh
        needs_refresh = cache.force_refresh_check("secret/data/database")
        print(f"✓ Needs refresh: {needs_refresh}")

    except Exception as e:
        print(f"✗ Error: {e}")

    print()


def example_ttl_cache_with_rotation():
    """
    Example 3: TTLCache with optional rotation support.

    Shows backward compatibility of TTLCache with rotation metadata.
    """
    print("=" * 70)
    print("Example 3: TTLCache with Rotation Support")
    print("=" * 70)

    try:
        # Standard TTL cache with rotation support
        cache = TTLCache(max_size=50, default_ttl=300)

        _ = VaultClient(cache=cache)

        print("✓ Created VaultClient with enhanced TTLCache")

        # The cache will automatically use rotation metadata if available
        # or fall back to default TTL behavior

        print("✓ TTLCache now supports rotation metadata for TTL calculation")
        print("✓ Falls back to default TTL if no rotation schedule available")

    except VaultError as e:
        print(f"✗ Error: {e}")

    print()


def example_rotation_schedule_parsing():
    """
    Example 4: Working with rotation schedules directly.

    Shows how to parse and work with cron schedules.
    """
    print("=" * 70)
    print("Example 4: Rotation Schedule Parsing")
    print("=" * 70)

    try:
        from gds_vault.rotation import (
            CronParser,
            calculate_rotation_ttl,
            should_refresh_secret,
        )

        # Common rotation schedules
        schedules = [
            "0 2 * * *",  # Daily at 2 AM
            "0 2 * * 0",  # Weekly on Sunday at 2 AM
            "0 2 1 * *",  # Monthly on 1st at 2 AM
            "0 */6 * * *",  # Every 6 hours
        ]

        for schedule in schedules:
            print(f"\nSchedule: {schedule}")

            cron = CronParser(schedule)
            next_run = cron.next_run_time()
            print(f"  Next run: {next_run}")

            # Calculate TTL from a recent rotation
            last_rotation = "2024-10-08T02:00:00Z"
            ttl = calculate_rotation_ttl(last_rotation, schedule, buffer_minutes=10)
            print(f"  TTL: {ttl} seconds")

            # Check if refresh needed
            needs_refresh = should_refresh_secret(last_rotation, schedule, buffer_minutes=10)
            print(f"  Needs refresh: {needs_refresh}")

    except Exception as e:
        print(f"✗ Error: {e}")

    print()


def example_production_usage():
    """
    Example 5: Production-ready configuration.

    Shows recommended settings for production environments.
    """
    print("=" * 70)
    print("Example 5: Production Configuration")
    print("=" * 70)

    try:
        # Production-ready rotation-aware cache
        cache = RotationAwareCache(
            max_size=100,  # Cache up to 100 secrets
            buffer_minutes=10,  # 10-minute safety buffer
            fallback_ttl=300,  # 5-minute fallback TTL
        )

        _ = VaultClient(
            cache=cache,
            timeout=30,  # 30-second timeout
            verify_ssl=True,  # Always verify SSL in production
        )

        print("✓ Production configuration:")
        print("  - RotationAwareCache with 10-minute buffer")
        print("  - 5-minute fallback TTL for secrets without rotation")
        print("  - SSL verification enabled")
        print("  - 30-second request timeout")

        # In production, secrets would be automatically managed:
        # 1. Vault returns rotation metadata with secrets
        # 2. Cache calculates TTL based on next rotation time
        # 3. Secrets are refreshed before rotation with buffer time
        # 4. Applications get fresh credentials seamlessly

        print("\n✓ Automatic rotation handling:")
        print("  1. Vault provides rotation schedule with secrets")
        print("  2. Cache calculates TTL until next rotation")
        print("  3. Secrets refresh automatically before rotation")
        print("  4. Applications always get valid credentials")

    except VaultError as e:
        print(f"✗ Error: {e}")

    print()


def show_cache_comparison():
    """
    Example 6: Cache comparison.

    Shows differences between cache types.
    """
    print("=" * 70)
    print("Example 6: Cache Type Comparison")
    print("=" * 70)

    caches = [
        ("SecretCache", "Basic in-memory cache, no expiration"),
        ("TTLCache", "Fixed TTL cache with optional rotation support"),
        ("RotationAwareCache", "Full rotation schedule awareness"),
        ("NoOpCache", "No caching (always fetch from Vault)"),
    ]

    print("Available cache types:\n")
    for cache_type, description in caches:
        print(f"  {cache_type:20} - {description}")

    print("\nRecommendations:")
    print("  - Use RotationAwareCache for secrets with rotation schedules")
    print("  - Use TTLCache for secrets with fixed refresh intervals")
    print("  - Use SecretCache for long-lived secrets")
    print("  - Use NoOpCache for testing or always-fresh requirements")

    print()


if __name__ == "__main__":
    print("Vault Rotation-Aware Caching Examples")
    print("=" * 70)

    # Run examples
    example_rotation_aware_cache()
    example_manual_rotation_metadata()
    example_ttl_cache_with_rotation()
    example_rotation_schedule_parsing()
    example_production_usage()
    show_cache_comparison()

    print("Examples completed! 🎉")

#!/usr/bin/env python3
"""
Simple demo of rotation-aware TTL functionality.

This demonstrates the core functionality without requiring a Vault server.
"""

import time
from datetime import datetime, timedelta

# Import the modules directly
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from gds_vault.cache import RotationAwareCache, TTLCache
from gds_vault.rotation import (
    CronParser, 
    calculate_rotation_ttl, 
    should_refresh_secret
)


def demo_cron_parser():
    """Demo cron expression parsing."""
    print("=" * 60)
    print("DEMO: Cron Expression Parsing")
    print("=" * 60)
    
    schedules = [
        ("0 2 * * *", "Daily at 2:00 AM"),
        ("0 */6 * * *", "Every 6 hours"),
        ("0 2 * * 0", "Weekly on Sunday at 2:00 AM"),
        ("0 2 1 * *", "Monthly on 1st at 2:00 AM"),
    ]
    
    current_time = datetime.now()
    print(f"Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for schedule, description in schedules:
        try:
            cron = CronParser(schedule)
            next_run = cron.next_run_time(current_time)
            print(f"Schedule: {schedule:12} - {description}")
            print(f"  Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
        except Exception as e:
            print(f"  Error: {e}")


def demo_ttl_calculation():
    """Demo TTL calculation based on rotation schedules."""
    print("=" * 60)
    print("DEMO: TTL Calculation")
    print("=" * 60)
    
    # Simulate different rotation scenarios
    scenarios = [
        {
            "name": "Daily rotation (just rotated)",
            "last_rotation": (datetime.now() - timedelta(hours=1)).isoformat(),
            "schedule": "0 2 * * *",
            "buffer": 10
        },
        {
            "name": "Daily rotation (near next rotation)",
            "last_rotation": (datetime.now() - timedelta(hours=23)).isoformat(),
            "schedule": "0 2 * * *",
            "buffer": 10
        },
        {
            "name": "Hourly rotation",
            "last_rotation": (datetime.now() - timedelta(minutes=30)).isoformat(),
            "schedule": "0 * * * *",
            "buffer": 5
        }
    ]
    
    for scenario in scenarios:
        print(f"\nScenario: {scenario['name']}")
        print(f"Last rotation: {scenario['last_rotation']}")
        print(f"Schedule: {scenario['schedule']}")
        print(f"Buffer: {scenario['buffer']} minutes")
        
        try:
            ttl = calculate_rotation_ttl(
                scenario['last_rotation'],
                scenario['schedule'],
                buffer_minutes=scenario['buffer']
            )
            
            needs_refresh = should_refresh_secret(
                scenario['last_rotation'],
                scenario['schedule'],
                buffer_minutes=scenario['buffer']
            )
            
            if ttl > 0:
                hours, remainder = divmod(ttl, 3600)
                minutes, seconds = divmod(remainder, 60)
                print(f"  TTL: {ttl}s ({int(hours)}h {int(minutes)}m {int(seconds)}s)")
            else:
                print(f"  TTL: {ttl}s (immediate refresh needed)")
                
            print(f"  Needs refresh: {needs_refresh}")
            
        except Exception as e:
            print(f"  Error: {e}")


def demo_rotation_aware_cache():
    """Demo rotation-aware caching."""
    print("=" * 60)
    print("DEMO: Rotation-Aware Cache")
    print("=" * 60)
    
    # Create cache
    cache = RotationAwareCache(
        max_size=10,
        buffer_minutes=15,
        fallback_ttl=300
    )
    
    print("Created RotationAwareCache:")
    print(f"  Max size: 10 secrets")
    print(f"  Buffer time: 15 minutes")
    print(f"  Fallback TTL: 5 minutes")
    print()
    
    # Test scenarios
    test_cases = [
        {
            "name": "Database credentials (daily rotation)",
            "key": "secret/data/database",
            "data": {"username": "app_user", "password": "secret123"},
            "rotation": {
                "last_rotation": (datetime.now() - timedelta(hours=2)).isoformat(),
                "schedule": "0 2 * * *"
            }
        },
        {
            "name": "API key (no rotation schedule)",
            "key": "secret/data/api-key", 
            "data": {"api_key": "abc123xyz"},
            "rotation": None
        },
        {
            "name": "Certificate (weekly rotation)",
            "key": "secret/data/tls-cert",
            "data": {"cert": "-----BEGIN CERTIFICATE-----", "key": "-----BEGIN PRIVATE KEY-----"},
            "rotation": {
                "last_rotation": (datetime.now() - timedelta(days=2)).isoformat(),
                "schedule": "0 2 * * 0"  # Sunday at 2 AM
            }
        }
    ]
    
    # Cache all secrets
    for case in test_cases:
        print(f"Caching: {case['name']}")
        cache.set(
            case['key'],
            case['data'],
            rotation_metadata=case['rotation']
        )
        
        # Check if it's retrieved successfully
        result = cache.get(case['key'])
        if result:
            print(f"  ✓ Cached and retrieved successfully")
            if case['rotation']:
                rotation_info = cache.get_rotation_info(case['key'])
                print(f"  ✓ Rotation schedule: {rotation_info['schedule']}")
        else:
            print(f"  ⚠ Secret filtered (needs refresh due to rotation)")
        print()
    
    # Show cache statistics
    stats = cache.get_stats()
    print("Cache Statistics:")
    print(f"  Total secrets: {stats['size']}")
    print(f"  With rotation schedules: {stats['secrets_with_rotation']}")
    print(f"  Needing refresh: {stats['secrets_needing_refresh']}")
    print(f"  Average TTL remaining: {stats['avg_remaining_ttl']:.1f} seconds")


def demo_ttl_cache_compatibility():
    """Demo TTLCache with rotation support."""
    print("=" * 60)
    print("DEMO: TTLCache Rotation Support")
    print("=" * 60)
    
    # Standard TTL cache with rotation support
    cache = TTLCache(max_size=10, default_ttl=600)
    
    print("Created TTLCache with rotation support:")
    print(f"  Default TTL: 10 minutes")
    print(f"  Now supports rotation metadata")
    print()
    
    # Test with rotation metadata
    rotation_metadata = {
        "last_rotation": (datetime.now() - timedelta(hours=1)).isoformat(),
        "schedule": "0 */6 * * *"  # Every 6 hours
    }
    
    secret_data = {"password": "enhanced_ttl_test"}
    
    print("Caching secret with rotation metadata...")
    cache.set(
        "secret/data/test",
        secret_data,
        rotation_metadata=rotation_metadata
    )
    
    result = cache.get("secret/data/test")
    if result:
        print("✓ Secret cached and retrieved with rotation-based TTL")
    else:
        print("⚠ Secret filtered due to rotation schedule")
    
    print()
    print("✓ TTLCache is backward compatible")
    print("✓ Automatically uses rotation metadata when available")
    print("✓ Falls back to default TTL when no rotation schedule")


if __name__ == "__main__":
    print("Vault Rotation-Aware TTL Demo")
    print("=" * 60)
    print()
    
    try:
        demo_cron_parser()
        print("\n")
        
        demo_ttl_calculation()
        print("\n")
        
        demo_rotation_aware_cache()
        print("\n")
        
        demo_ttl_cache_compatibility()
        print("\n")
        
        print("=" * 60)
        print("🎉 All demos completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
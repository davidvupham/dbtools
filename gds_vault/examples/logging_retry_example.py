#!/usr/bin/env python3
"""
Example demonstrating logging and retry logic in gds_vault.

This example shows:
1. How to configure logging for different scenarios
2. How retry logic automatically handles transient failures
3. Production-ready logging patterns
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from gds_vault import VaultClient, VaultError


def example_basic_logging():
    """Example 1: Basic console logging."""
    print("\n" + "="*60)
    print("Example 1: Basic Console Logging")
    print("="*60)

    # Configure basic logging to console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Set environment variables (in production, these come from env)
    os.environ['VAULT_ADDR'] = 'https://vault.example.com'
    os.environ['VAULT_ROLE_ID'] = 'my-role-id'
    os.environ['VAULT_SECRET_ID'] = 'my-secret-id'

    try:
        VaultClient()
        print("\nVaultClient created successfully")
        print("Check the logs above - you'll see authentication attempts")
        print("(In production, this would connect to real Vault)")
    except VaultError as e:
        print(f"\nExpected error (no real Vault server): {e}")


def example_debug_logging():
    """Example 2: Debug logging for troubleshooting."""
    print("\n" + "="*60)
    print("Example 2: Debug Logging (Verbose)")
    print("="*60)

    # Clear existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Configure DEBUG level for detailed information
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)-8s - %(message)s'
    )

    print("\nWith DEBUG level, you see:")
    print("- Cache hits/misses")
    print("- Token expiry details")
    print("- KV version detection")
    print("- All retry attempts")

    try:
        VaultClient()
        print("\nCheck logs for detailed DEBUG messages")
    except VaultError as e:
        print(f"\nExpected error: {e}")


def example_production_file_logging():
    """Example 3: Production-ready file logging with rotation."""
    print("\n" + "="*60)
    print("Example 3: Production File Logging with Rotation")
    print("="*60)

    # Clear existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Create a logger for gds_vault
    logger = logging.getLogger('gds_vault.vault')
    logger.setLevel(logging.INFO)

    # Console handler (errors only)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_formatter = logging.Formatter('ERROR: %(message)s')
    console_handler.setFormatter(console_formatter)

    # File handler with rotation (simulated - would write to /var/log in production)
    try:
        file_handler = RotatingFileHandler(
            '/tmp/vault_example.log',
            maxBytes=1*1024*1024,  # 1MB
            backupCount=3
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        print("\nFile logging configured: /tmp/vault_example.log")
        print("- Rotates at 1MB")
        print("- Keeps 3 backup files")
    except Exception as e:
        print(f"\nFile logging setup failed: {e}")

    logger.addHandler(console_handler)

    try:
        VaultClient()
        print("\nLogs written to /tmp/vault_example.log")
        print("Only ERRORs appear on console")
    except VaultError as e:
        print(f"\nExpected error: {e}")


def example_cache_behavior():
    """Example 4: Observing cache behavior through logs."""
    print("\n" + "="*60)
    print("Example 4: Cache Behavior Logging")
    print("="*60)

    # Clear existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)-8s - %(message)s'
    )

    print("\nThis example would show:")
    print("- First fetch: 'INFO: Fetching secret from Vault: secret/data/myapp'")
    print("- Second fetch: 'DEBUG: Cache hit for secret: secret/data/myapp'")
    print("- Cache clear: 'INFO: Cleared cache (removed 1 secrets)'")
    print("\n(With a real Vault server)")


def example_retry_behavior():
    """Example 5: Understanding retry logic."""
    print("\n" + "="*60)
    print("Example 5: Retry Logic Explanation")
    print("="*60)

    print("\nRetry logic with exponential backoff:")
    print("\nWhen a network error occurs, gds_vault automatically:")
    print("1. Logs a WARNING with the error and retry delay")
    print("2. Waits for the calculated delay")
    print("3. Retries the operation")
    print("4. Repeats up to 3 times")
    print("\nExample log output on transient failure:")
    print("  WARNING: authenticate attempt 1 failed: Connection timeout. Retrying in 1.0s...")
    print("  WARNING: authenticate attempt 2 failed: Connection timeout. Retrying in 2.0s...")
    print("  INFO: Successfully authenticated with Vault. Token valid for 3600s")
    print("\nDelay pattern: 1s → 2s → 4s (exponential backoff)")
    print("Total max time: ~7 seconds")
    print("\nThis handles:")
    print("  ✓ Temporary network glitches")
    print("  ✓ Server overload (rate limiting)")
    print("  ✓ Brief service outages")
    print("  ✓ Transient errors")


def example_context_manager_logging():
    """Example 6: Context manager lifecycle logging."""
    print("\n" + "="*60)
    print("Example 6: Context Manager Lifecycle")
    print("="*60)

    # Clear existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)-8s - %(message)s'
    )

    print("\nContext manager logs lifecycle events:")
    print("DEBUG: Entering VaultClient context manager")
    print("INFO: Authenticating with Vault at https://vault.example.com")
    print("... operations ...")
    print("DEBUG: Exiting VaultClient context manager")
    print("INFO: Cleared cache (removed N secrets)")
    print("\nThis helps track resource lifecycle in production")


def example_production_best_practices():
    """Example 7: Production best practices summary."""
    print("\n" + "="*60)
    print("Example 7: Production Best Practices")
    print("="*60)

    print("\n1. LOG LEVELS BY ENVIRONMENT:")
    print("   Development:  DEBUG   (see everything)")
    print("   Staging:      INFO    (track operations)")
    print("   Production:   WARNING (only issues)")
    print("   Troubleshoot: DEBUG   (temporarily)")

    print("\n2. LOG ROTATION:")
    print("   Use RotatingFileHandler to prevent disk space issues")
    print("   Recommended: 10MB per file, keep 5 backups")

    print("\n3. STRUCTURED LOGGING:")
    print("   Use JSON format for log aggregation systems")
    print("   (Splunk, ELK, CloudWatch, Datadog)")

    print("\n4. SECURITY:")
    print("   ✓ gds_vault never logs token values")
    print("   ✓ gds_vault never logs secret contents")
    print("   ✓ Only logs operation outcomes and paths")

    print("\n5. MONITORING:")
    print("   Alert on: Multiple ERROR logs within time window")
    print("   Alert on: High retry attempt frequency")
    print("   Alert on: 'failed after 3 retries' messages")

    print("\n6. RETRY CUSTOMIZATION:")
    print("   Default settings work for most use cases")
    print("   Customize if you have specific requirements")
    print("   (See LOGGING_AND_RETRY_GUIDE.md)")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("GDS_VAULT: LOGGING AND RETRY LOGIC EXAMPLES")
    print("="*70)
    print("\nThese examples demonstrate the logging and retry features")
    print("added to gds_vault for production resilience and debugging.")

    # Run examples
    example_basic_logging()
    example_debug_logging()
    example_production_file_logging()
    example_cache_behavior()
    example_retry_behavior()
    example_context_manager_logging()
    example_production_best_practices()

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("\n✓ Logging provides visibility into all Vault operations")
    print("✓ Retry logic automatically handles transient failures")
    print("✓ Exponential backoff prevents overwhelming struggling services")
    print("✓ Production-ready with minimal configuration")
    print("\nFor more details, see:")
    print("  - LOGGING_AND_RETRY_GUIDE.md (comprehensive guide)")
    print("  - LOGGING_AND_RETRY_IMPLEMENTATION.md (implementation details)")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()

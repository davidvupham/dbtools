#!/usr/bin/env python3
"""
Example demonstrating both functional and class-based approaches to using gds-vault.

This example shows:
1. Simple functional approach for one-off secret retrieval
2. VaultClient class for fetching multiple secrets with token caching
3. Context manager usage for automatic cleanup
"""

import os

from gds_vault import VaultClient, VaultError, get_secret_from_vault


def example_functional_approach():
    """
    Example 1: Simple functional approach.
    
    Use this when you need to fetch a single secret.
    This is the simplest way to use gds-vault.
    """
    print("=" * 60)
    print("Example 1: Functional Approach (Single Secret)")
    print("=" * 60)

    try:
        # Fetch a single secret
        secret = get_secret_from_vault('secret/data/myapp')
        print(f"✓ Retrieved secret: {list(secret.keys())}")
    except VaultError as e:
        print(f"✗ Error: {e}")

    print()


def example_class_without_caching():
    """
    Example 2: VaultClient without caching.
    
    Demonstrates explicitly disabling cache for each request.
    """
    print("=" * 60)
    print("Example 2: VaultClient Without Caching")
    print("=" * 60)

    try:
        client = VaultClient()

        # Fetch secrets without caching (use_cache=False)
        secret1 = client.get_secret('secret/data/app1', use_cache=False)
        secret2 = client.get_secret('secret/data/app2', use_cache=False)

        print("✓ Retrieved 2 secrets without caching")
        print(f"  Cache info: {client.get_cache_info()}")
    except VaultError as e:
        print(f"✗ Error: {e}")

    print()


def example_class_with_caching():
    """
    Example 3: VaultClient with caching (default behavior).
    
    Use this when fetching multiple secrets to:
    - Reuse authentication token (more efficient)
    - Cache secret values (avoid redundant Vault calls)
    """
    print("=" * 60)
    print("Example 3: VaultClient With Caching (Recommended)")
    print("=" * 60)

    try:
        client = VaultClient(
            vault_addr="https://vault.example.com",
            timeout=15
        )

        # Authenticate once and reuse token
        print("→ Fetching multiple secrets...")
        secret1 = client.get_secret('secret/data/database')
        secret2 = client.get_secret('secret/data/api-keys')
        secret3 = client.get_secret('secret/data/smtp')

        # Fetching the same secret again uses cache
        cached_secret = client.get_secret('secret/data/database')

        print("✓ Retrieved 3 unique secrets")
        print("✓ Second fetch of database secret used cache")

        # Check cache statistics
        cache_info = client.get_cache_info()
        print("\nCache Statistics:")
        print(f"  - Token cached: {cache_info['has_token']}")
        print(f"  - Token valid: {cache_info['token_valid']}")
        print(f"  - Cached secrets: {cache_info['cached_secrets_count']}")
        print(f"  - Secret paths: {cache_info['cached_secret_paths']}")

    except VaultError as e:
        print(f"✗ Error: {e}")

    print()


def example_context_manager():
    """
    Example 4: Using VaultClient as context manager.
    
    The context manager automatically clears the cache when done.
    This is the recommended approach for scripts.
    """
    print("=" * 60)
    print("Example 4: Context Manager (Best Practice)")
    print("=" * 60)

    try:
        with VaultClient() as client:
            print("→ Inside context manager...")

            # Fetch multiple secrets
            db_secret = client.get_secret('secret/data/database')
            api_secret = client.get_secret('secret/data/api-keys')

            print(f"✓ Retrieved {len(client._secret_cache)} secrets")
            print(f"  Database fields: {list(db_secret.keys())}")
            print(f"  API key fields: {list(api_secret.keys())}")

        print("✓ Context exited, cache automatically cleared")

    except VaultError as e:
        print(f"✗ Error: {e}")

    print()


def example_list_secrets():
    """
    Example 5: Listing secrets in a path.
    
    VaultClient provides additional operations beyond get_secret.
    """
    print("=" * 60)
    print("Example 5: Listing Secrets")
    print("=" * 60)

    try:
        client = VaultClient()

        # List all secrets in a path
        secrets = client.list_secrets('secret/metadata/myapp')

        print(f"✓ Found {len(secrets)} secrets:")
        for secret_name in secrets:
            print(f"  - {secret_name}")

    except VaultError as e:
        print(f"✗ Error: {e}")

    print()


def example_version_retrieval():
    """
    Example 6: Retrieving specific versions (KV v2 only).
    
    KV v2 secret engines support versioning.
    """
    print("=" * 60)
    print("Example 6: Version-Specific Secret Retrieval")
    print("=" * 60)

    try:
        client = VaultClient()

        # Get current version
        current = client.get_secret('secret/data/myapp')
        print(f"✓ Current version: {current}")

        # Get specific version
        v2 = client.get_secret('secret/data/myapp', version=2)
        print(f"✓ Version 2: {v2}")

        # Note: Different versions are cached separately
        cache_info = client.get_cache_info()
        print(f"\nCached: {cache_info['cached_secret_paths']}")

    except VaultError as e:
        print(f"✗ Error: {e}")

    print()


def example_manual_cache_management():
    """
    Example 7: Manual cache management.
    
    You can manually clear cache when needed.
    """
    print("=" * 60)
    print("Example 7: Manual Cache Management")
    print("=" * 60)

    try:
        client = VaultClient()

        # Fetch some secrets
        client.get_secret('secret/data/app1')
        client.get_secret('secret/data/app2')

        print(f"✓ Cached secrets: {len(client._secret_cache)}")

        # Clear cache manually
        client.clear_cache()
        print(f"✓ After clear: {len(client._secret_cache)} cached")

        # Next fetch will re-authenticate
        client.get_secret('secret/data/app3')
        print(f"✓ After new fetch: {len(client._secret_cache)} cached")

    except VaultError as e:
        print(f"✗ Error: {e}")

    print()


def example_error_handling():
    """
    Example 8: Comprehensive error handling.
    
    Shows how to handle various error conditions.
    """
    print("=" * 60)
    print("Example 8: Error Handling")
    print("=" * 60)

    # Example 1: Missing credentials
    try:
        os.environ.pop('VAULT_ROLE_ID', None)
        client = VaultClient()
    except VaultError as e:
        print(f"✓ Caught missing credentials: {e}")

    # Example 2: Invalid secret path
    try:
        client = VaultClient(
            vault_addr="https://vault.example.com",
            role_id="test",
            secret_id="test"
        )
        secret = client.get_secret('invalid/path')
    except VaultError as e:
        print(f"✓ Caught invalid path error: {e}")

    print()


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "GDS-VAULT USAGE EXAMPLES" + " " * 24 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    # Check if environment variables are set
    required_vars = ['VAULT_ADDR', 'VAULT_ROLE_ID', 'VAULT_SECRET_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("⚠ Warning: Missing environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nSet these variables to run live examples:")
        print("  export VAULT_ADDR='https://vault.example.com'")
        print("  export VAULT_ROLE_ID='your-role-id'")
        print("  export VAULT_SECRET_ID='your-secret-id'")
        print("\nShowing example usage (will fail without real credentials):\n")

    # Run examples
    example_functional_approach()
    example_class_with_caching()
    example_context_manager()
    example_list_secrets()
    example_version_retrieval()
    example_manual_cache_management()
    example_error_handling()

    print("=" * 60)
    print("Summary:")
    print("=" * 60)
    print("• Use get_secret_from_vault() for single secrets")
    print("• Use VaultClient for multiple secrets (caches token)")
    print("• Use context manager for automatic cleanup")
    print("• Secrets are cached by default (use use_cache=False to disable)")
    print("• Check cache_info() for statistics")
    print()


if __name__ == "__main__":
    main()

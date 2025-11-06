"""
Example: Using Vault Mount Points

This example demonstrates how to use the mount_point parameter
to work with HashiCorp Vault secrets engines mounted at different paths.

HashiCorp Vault allows mounting multiple instances of secrets engines
at different paths. The mount_point parameter simplifies working with
non-default mounts by automatically prepending the mount point to all
secret paths.
"""

import logging
import os

from gds_vault import VaultClient

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def example_basic_mount_point():
    """Example 1: Basic mount point usage."""
    print("\n" + "=" * 60)
    print("Example 1: Basic Mount Point Usage")
    print("=" * 60)

    # Without mount point - must use full paths
    client_no_mount = VaultClient()

    # Fetch from default 'secret' mount
    secret1 = client_no_mount.get_secret("secret/data/myapp")
    print(f"Secret from secret/data/myapp: {list(secret1.keys())}")

    # With mount point - paths are automatically prefixed
    client_with_mount = VaultClient(mount_point="kv-v2")

    # This fetches from 'kv-v2/data/myapp'
    secret2 = client_with_mount.get_secret("data/myapp")
    print(f"Secret from kv-v2/data/myapp: {list(secret2.keys())}")


def example_environment_variable():
    """Example 2: Using VAULT_MOUNT_POINT environment variable."""
    print("\n" + "=" * 60)
    print("Example 2: Environment Variable")
    print("=" * 60)

    # Set mount point via environment
    os.environ["VAULT_MOUNT_POINT"] = "kv-v2"

    # Client automatically uses the environment variable
    client = VaultClient()
    print(f"Mount point from environment: {client.mount_point}")

    # All secret paths are automatically prefixed
    _secret = client.get_secret("data/myapp")
    print("Fetched secret from: kv-v2/data/myapp")

    # Clean up
    del os.environ["VAULT_MOUNT_POINT"]


def example_parameter_override():
    """Example 3: Parameter overrides environment variable."""
    print("\n" + "=" * 60)
    print("Example 3: Parameter Overrides Environment")
    print("=" * 60)

    # Set environment variable
    os.environ["VAULT_MOUNT_POINT"] = "secret"

    # Parameter takes precedence
    client = VaultClient(mount_point="kv-v2")
    print("Environment says: secret")
    print(f"Client uses: {client.mount_point}")

    # Clean up
    del os.environ["VAULT_MOUNT_POINT"]


def example_dynamic_mount_point():
    """Example 4: Dynamically changing mount point."""
    print("\n" + "=" * 60)
    print("Example 4: Dynamic Mount Point Changes")
    print("=" * 60)

    client = VaultClient()

    # Start with no mount point
    print(f"Initial mount point: {client.mount_point}")

    # Change to 'kv-v2'
    client.mount_point = "kv-v2"
    print(f"Changed to: {client.mount_point}")
    _secret1 = client.get_secret("data/app1")
    print("Fetched from: kv-v2/data/app1")

    # Change to 'secret'
    client.mount_point = "secret"
    print(f"Changed to: {client.mount_point}")
    _secret2 = client.get_secret("data/app2")
    print("Fetched from: secret/data/app2")


def example_multi_environment():
    """Example 5: Different mount points for different environments."""
    print("\n" + "=" * 60)
    print("Example 5: Environment-Specific Mount Points")
    print("=" * 60)

    def get_client_for_environment(env: str) -> VaultClient:
        """Get Vault client configured for specific environment."""
        mount_points = {"dev": "secret", "staging": "kv-v2", "production": "kv-prod"}
        mount_point = mount_points.get(env, "secret")
        print(f"Environment: {env} -> Mount point: {mount_point}")
        return VaultClient(mount_point=mount_point)

    # Different environments use different mounts
    dev_client = get_client_for_environment("dev")
    staging_client = get_client_for_environment("staging")
    prod_client = get_client_for_environment("production")

    # All use the same relative path
    secret_path = "data/database/credentials"

    # But fetch from different mounts
    _dev_secret = dev_client.get_secret(secret_path)
    print(f"Dev fetches from: secret/{secret_path}")

    _staging_secret = staging_client.get_secret(secret_path)
    print(f"Staging fetches from: kv-v2/{secret_path}")

    _prod_secret = prod_client.get_secret(secret_path)
    print(f"Prod fetches from: kv-prod/{secret_path}")


def example_smart_path_handling():
    """Example 6: Smart path handling (no duplication)."""
    print("\n" + "=" * 60)
    print("Example 6: Smart Path Handling")
    print("=" * 60)

    client = VaultClient(mount_point="kv-v2")

    # Both of these work correctly
    path1 = "data/myapp"
    path2 = "kv-v2/data/myapp"

    print(f"Path 1: {path1}")
    print("Resolves to: kv-v2/data/myapp")

    print(f"\nPath 2: {path2}")
    print("Resolves to: kv-v2/data/myapp (no duplication)")

    # The client is smart enough not to duplicate the mount point
    _secret1 = client.get_secret(path1)
    _secret2 = client.get_secret(path2)

    print("\nBoth paths fetch the same secret successfully!")


def example_list_secrets_with_mount():
    """Example 7: Listing secrets with mount point."""
    print("\n" + "=" * 60)
    print("Example 7: List Secrets with Mount Point")
    print("=" * 60)

    client = VaultClient(mount_point="kv-v2")

    # List all secrets under a path
    # Without mount point, you'd need to use: kv-v2/metadata/myapp
    # With mount point, just use: metadata/myapp
    secrets = client.list_secrets("metadata/myapp")

    print("Secrets in kv-v2/metadata/myapp:")
    for secret_name in secrets:
        print(f"  - {secret_name}")


def example_configuration():
    """Example 8: Mount point in configuration."""
    print("\n" + "=" * 60)
    print("Example 8: Mount Point in Configuration")
    print("=" * 60)

    # Using from_config class method
    config = {
        "vault_addr": "https://vault.example.com",
        "mount_point": "kv-v2",
        "timeout": 15,
        "max_retries": 5,
    }

    client = VaultClient.from_config(config)
    print(f"Client created with mount point: {client.mount_point}")

    # Mount point is included in config
    all_config = client.get_all_config()
    print("\nAll configuration:")
    for key, value in all_config.items():
        print(f"  {key}: {value}")


def example_convenience_function():
    """Example 9: Mount point with convenience function."""
    print("\n" + "=" * 60)
    print("Example 9: Convenience Function")
    print("=" * 60)

    from gds_vault import get_secret_from_vault

    # Quick one-off secret fetch with mount point
    secret = get_secret_from_vault("data/myapp", mount_point="kv-v2")
    print("Fetched secret from kv-v2/data/myapp")
    print(f"Secret keys: {list(secret.keys())}")


def example_context_manager():
    """Example 10: Mount point with context manager."""
    print("\n" + "=" * 60)
    print("Example 10: Context Manager with Mount Point")
    print("=" * 60)

    with VaultClient(mount_point="kv-v2") as client:
        # Fetch multiple secrets
        _secret1 = client.get_secret("data/app1")
        _secret2 = client.get_secret("data/app2")
        _secret3 = client.get_secret("data/app3")

        print(f"Fetched {len(client)} secrets from kv-v2 mount")
        print(f"Cache statistics: {client.cache_stats}")

    print("Context manager automatically cleaned up resources")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("HashiCorp Vault Mount Point Examples")
    print("=" * 60)
    print("\nNote: These examples require a running Vault instance")
    print("with appropriate secrets and authentication configured.")
    print("Set VAULT_ADDR, VAULT_ROLE_ID, and VAULT_SECRET_ID")
    print("environment variables before running.")
    print("=" * 60)

    # Check if Vault is configured
    if not all(
        [
            os.getenv("VAULT_ADDR"),
            os.getenv("VAULT_ROLE_ID"),
            os.getenv("VAULT_SECRET_ID"),
        ]
    ):
        print("\n⚠️  WARNING: Vault environment variables not set!")
        print("Please set:")
        print("  - VAULT_ADDR")
        print("  - VAULT_ROLE_ID")
        print("  - VAULT_SECRET_ID")
        print("\nExamples will demonstrate the concepts but may fail without")
        print("a properly configured Vault instance.")

    try:
        # Run all examples (comment out any that require specific Vault setup)
        example_basic_mount_point()
        example_environment_variable()
        example_parameter_override()
        example_dynamic_mount_point()
        example_multi_environment()
        example_smart_path_handling()
        example_list_secrets_with_mount()
        example_configuration()
        example_convenience_function()
        example_context_manager()

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("\nThis is expected if Vault is not properly configured.")
        print("The examples demonstrate the API - actual usage requires")
        print("a running Vault instance with appropriate setup.")

    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)

# gds_vault API Reference

**[← Back to Reference Index](./README.md)**

> **Package:** gds_vault
> **Version:** Latest

> [!NOTE]
> **Naming Convention:** This file is named `gds-vault-api.md` because it strictly documents the API for the internal `gds_vault` Python package. It is distinct from the upstream [HashiCorp Vault HTTP API](https://developer.hashicorp.com/vault/api) and the [Vault CLI](./vault-cli.md).

## Table of Contents

- [VaultClient](#vaultclient)
- [Authentication Strategies](#authentication-strategies)
- [Cache Classes](#cache-classes)
- [Retry Policy](#retry-policy)
- [Environment Variables](#environment-variables)
- [Configuration Options](#configuration-options)
- [Exception Types](#exception-types)

## VaultClient

The main client class for interacting with HashiCorp Vault.

**Import:**

```python
from gds_vault import VaultClient
```

**Constructor:**

```python
VaultClient(
    vault_addr: str = None,        # Vault server address
    auth: AuthStrategy = None,     # Authentication strategy
    cache: CacheProtocol = None,   # Cache implementation
    retry_policy: RetryPolicy = None,  # Retry configuration
    timeout: int = 10,             # Request timeout in seconds
    verify_ssl: bool = True,       # Verify TLS certificates
    ssl_cert_path: str = None,     # Path to CA certificate
    namespace: str = None,         # Vault namespace (Enterprise)
    mount_point: str = None        # Default secrets engine mount
)
```

**Class Methods:**

| Method | Description | Returns |
|:---|:---|:---|
| `from_environment(**kwargs)` | Create client from environment variables | `VaultClient` |
| `from_config(config: dict)` | Create client from configuration dict | `VaultClient` |
| `from_token(token: str, **kwargs)` | Create client with direct token auth | `VaultClient` |

**Instance Methods:**

| Method | Description | Returns |
|:---|:---|:---|
| `get_secret(path: str, **kwargs)` | Retrieve a secret from Vault | `dict[str, Any]` |
| `list_secrets(path: str)` | List secrets at a path | `list[str]` |
| `authenticate()` | Authenticate with Vault | `bool` |
| `is_authenticated()` | Check if currently authenticated | `bool` |
| `clear_cache()` | Clear all cached secrets | `None` |
| `remove_from_cache(key: str)` | Remove specific secret from cache | `None` |
| `initialize()` | Initialize client resources | `None` |
| `cleanup()` | Clean up client resources | `None` |

**Properties:**

| Property | Type | Description |
|:---|:---|:---|
| `vault_addr` | `str` | Vault server address |
| `timeout` | `int` | Request timeout |
| `is_authenticated` | `bool` | Authentication status |
| `cache_stats` | `dict` | Cache statistics |

**Usage Examples:**

```python
# Basic usage
from gds_vault import VaultClient

client = VaultClient()
secret = client.get_secret("secret/data/myapp")

# Context manager (recommended)
with VaultClient() as client:
    secret = client.get_secret("secret/data/myapp")
    password = secret["password"]

# From configuration
config = {
    "vault_addr": "https://vault.example.com:8200",
    "timeout": 30,
    "mount_point": "kv-v2"
}
client = VaultClient.from_config(config)

# With custom components
from gds_vault import VaultClient, AppRoleAuth, TTLCache, RetryPolicy

client = VaultClient(
    auth=AppRoleAuth(role_id="...", secret_id="..."),
    cache=TTLCache(default_ttl=600),
    retry_policy=RetryPolicy(max_retries=5)
)
```

## Authentication Strategies

### AppRoleAuth

Machine authentication using Role ID and Secret ID.

```python
from gds_vault.auth import AppRoleAuth

auth = AppRoleAuth(
    role_id: str = None,     # Role ID (or VAULT_ROLE_ID env var)
    secret_id: str = None,   # Secret ID (or VAULT_SECRET_ID env var)
    namespace: str = None    # Optional namespace
)
```

### TokenAuth

Direct token authentication.

```python
from gds_vault.auth import TokenAuth

auth = TokenAuth(
    token: str,          # Vault token
    ttl: int = 3600      # Token TTL in seconds
)
```

### EnvironmentAuth

Auto-detect authentication from environment.

```python
from gds_vault.auth import EnvironmentAuth

auth = EnvironmentAuth()  # Tries VAULT_TOKEN, then AppRole
```

## Cache Classes

### SecretCache

Simple in-memory cache without TTL.

```python
from gds_vault.cache import SecretCache

cache = SecretCache(max_size: int = 100)
```

### TTLCache

Time-based cache with automatic expiration.

```python
from gds_vault.cache import TTLCache

cache = TTLCache(
    max_size: int = 100,      # Maximum cached items
    default_ttl: int = 300    # Default TTL in seconds
)
```

### RotationAwareCache

Cache that respects secret rotation schedules.

```python
from gds_vault.cache import RotationAwareCache

cache = RotationAwareCache(
    max_size: int = 100,       # Maximum cached items
    buffer_minutes: int = 10,  # Refresh before rotation
    fallback_ttl: int = 300    # TTL for non-rotating secrets
)
```

### NoOpCache

Disable caching (always fetch from Vault).

```python
from gds_vault.cache import NoOpCache

cache = NoOpCache()
```

## Retry Policy

Configure retry behavior for failed requests.

```python
from gds_vault import RetryPolicy

policy = RetryPolicy(
    max_retries: int = 3,           # Maximum retry attempts
    initial_delay: float = 1.0,     # Initial delay in seconds
    max_delay: float = 16.0,        # Maximum delay in seconds
    backoff_factor: float = 2.0     # Exponential backoff multiplier
)
```

## Environment Variables

| Variable | Description | Default |
|:---|:---|:---|
| `VAULT_ADDR` | Vault server URL | Required |
| `VAULT_TOKEN` | Direct authentication token | - |
| `VAULT_ROLE_ID` | AppRole role ID | - |
| `VAULT_SECRET_ID` | AppRole secret ID | - |
| `VAULT_NAMESPACE` | Vault namespace (Enterprise) | - |
| `VAULT_MOUNT_POINT` | Default secrets engine mount | `secret` |
| `VAULT_SSL_CERT` | Path to CA certificate | System default |
| `VAULT_SKIP_VERIFY` | Skip TLS verification (dev only) | `false` |

**Priority:**

1. Constructor parameters (highest)
2. Environment variables
3. Default values (lowest)

**Example Setup:**

```bash
# Production
export VAULT_ADDR="https://vault.example.com:8200"
export VAULT_ROLE_ID="12345-abcde-67890"
export VAULT_SECRET_ID="secret-id-value"
export VAULT_SSL_CERT="/etc/ssl/certs/ca-certificates.crt"

# Development
export VAULT_ADDR="http://localhost:8200"
export VAULT_TOKEN="hvs.dev-token"
```

## Configuration Options

### VaultClient Configuration Dict

```python
config = {
    # Connection
    "vault_addr": "https://vault.example.com:8200",
    "timeout": 30,
    "verify_ssl": True,
    "ssl_cert_path": "/path/to/ca.crt",

    # Authentication
    "role_id": "...",
    "secret_id": "...",

    # Secrets Engine
    "mount_point": "kv-v2",
    "namespace": "my-namespace",

    # Retry
    "max_retries": 5,
    "initial_delay": 1.0,
    "max_delay": 16.0,

    # Cache
    "cache_ttl": 600,
    "cache_max_size": 100
}

client = VaultClient.from_config(config)
```

## Exception Types

All exceptions inherit from `VaultError`.

| Exception | When Raised | HTTP Code |
|:---|:---|:---:|
| `VaultError` | Base exception (catch-all) | Various |
| `VaultAuthError` | Authentication failed | 401 |
| `VaultConnectionError` | Network/connection error | - |
| `VaultSecretNotFoundError` | Secret path not found | 404 |
| `VaultPermissionError` | Access denied | 403 |
| `VaultConfigurationError` | Invalid configuration | - |
| `VaultCacheError` | Cache operation failed | - |

**Exception Handling Pattern:**

```python
from gds_vault import (
    VaultClient,
    VaultError,
    VaultAuthError,
    VaultConnectionError,
    VaultSecretNotFoundError,
    VaultPermissionError,
    VaultConfigurationError
)

try:
    with VaultClient() as client:
        secret = client.get_secret("secret/data/myapp")
except VaultSecretNotFoundError:
    # Secret doesn't exist - use defaults
    secret = {"password": "default"}
except VaultPermissionError:
    # Access denied - log and escalate
    logger.error("Permission denied for secret")
    raise
except VaultAuthError:
    # Authentication failed - check credentials
    logger.error("Authentication failed")
    raise
except VaultConnectionError:
    # Network issue - retry or fallback
    logger.error("Cannot connect to Vault")
    raise
except VaultConfigurationError:
    # Bad config - check environment
    logger.error("Invalid Vault configuration")
    raise
except VaultError as e:
    # Catch-all for other Vault errors
    logger.error(f"Vault error: {e}")
    raise
```

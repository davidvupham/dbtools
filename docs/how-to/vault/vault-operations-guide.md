# Vault Operations Guide

**[← Back to Vault Documentation Index](../../explanation/vault/README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 15, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![gds_vault](https://img.shields.io/badge/gds__vault-Latest-blue)
![Document Status](https://img.shields.io/badge/Status-Production-green)

> [!IMPORTANT]
> **Related Docs:** [Concepts](../../explanation/vault/vault-concepts.md) | [Architecture](../../explanation/vault/vault-architecture.md) | [Reference](../../reference/vault/vault-reference.md)

## Table of Contents

- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
- [Using gds_vault](#using-gds_vault)
  - [Basic Usage](#basic-usage)
  - [Context Manager Pattern](#context-manager-pattern)
  - [Configuration Options](#configuration-options)
- [Authentication Patterns](#authentication-patterns)
  - [AppRole Authentication](#approle-authentication)
  - [Token Authentication](#token-authentication)
  - [Environment-Based Authentication](#environment-based-authentication)
  - [Choosing an Auth Method](#choosing-an-auth-method)
- [Retrieving Secrets](#retrieving-secrets)
  - [KV Secrets](#kv-secrets)
  - [Secret Paths](#secret-paths)
  - [Listing Secrets](#listing-secrets)
- [Caching Strategies](#caching-strategies)
  - [No Caching](#no-caching)
  - [TTL-Based Caching](#ttl-based-caching)
  - [Rotation-Aware Caching](#rotation-aware-caching)
  - [Choosing a Cache Strategy](#choosing-a-cache-strategy)
- [Error Handling](#error-handling)
  - [Exception Hierarchy](#exception-hierarchy)
  - [Retry Patterns](#retry-patterns)
  - [Graceful Degradation](#graceful-degradation)
- [Best Practices](#best-practices)
  - [Security](#security)
  - [Performance](#performance)
  - [Resilience](#resilience)
- [Integration Patterns](#integration-patterns)
  - [FastAPI Integration](#fastapi-integration)
  - [Background Workers](#background-workers)
  - [Configuration Management](#configuration-management)

## Getting Started

### Installation

Install the `gds_vault` package:

```bash
# From the monorepo root
pip install -e gds_vault/

# Or if packaged
pip install gds-vault
```

### Quick Start

```python
from gds_vault import VaultClient

# Set environment variables
# export VAULT_ADDR="https://vault.example.com:8200"
# export VAULT_ROLE_ID="your-role-id"
# export VAULT_SECRET_ID="your-secret-id"

# Get a secret
with VaultClient() as client:
    secret = client.get_secret("secret/data/myapp/database")
    password = secret["password"]
    print(f"Connected with password: {password[:3]}***")
```

[↑ Back to Table of Contents](#table-of-contents)

## Using gds_vault

### Basic Usage

The simplest way to use `gds_vault`:

```python
from gds_vault import VaultClient

# Create client (reads from environment variables)
client = VaultClient()

# Get a secret
secret = client.get_secret("secret/data/myapp/database")

# Access secret values
username = secret["username"]
password = secret["password"]
host = secret["host"]

# Use the credentials
connection_string = f"postgresql://{username}:{password}@{host}:5432/mydb"
```

### Context Manager Pattern

The recommended pattern for resource management:

```python
from gds_vault import VaultClient

# Resources automatically cleaned up
with VaultClient() as client:
    db_creds = client.get_secret("secret/data/myapp/database")
    api_key = client.get_secret("secret/data/myapp/api-keys")

    # Use secrets within the context
    configure_database(db_creds)
    configure_api(api_key)

# After 'with' block: cache cleared, resources released
```

**Benefits:**
- Automatic initialization
- Automatic cleanup on exit
- Exception-safe resource management

### Configuration Options

Configure the client for your environment:

```python
from gds_vault import VaultClient, TTLCache, RetryPolicy

# Full configuration
client = VaultClient(
    # Connection
    vault_addr="https://vault.example.com:8200",
    timeout=30,

    # TLS
    verify_ssl=True,
    ssl_cert_path="/etc/ssl/certs/ca-certificates.crt",

    # Vault options
    namespace="my-namespace",  # Enterprise only
    mount_point="kv-v2",

    # Components
    cache=TTLCache(default_ttl=600),
    retry_policy=RetryPolicy(max_retries=5)
)
```

**From Configuration Dict:**

```python
config = {
    "vault_addr": "https://vault.example.com:8200",
    "timeout": 30,
    "mount_point": "kv-v2",
    "max_retries": 5
}

client = VaultClient.from_config(config)
```

[↑ Back to Table of Contents](#table-of-contents)

## Authentication Patterns

### AppRole Authentication

AppRole is the recommended method for applications:

```python
from gds_vault import VaultClient
from gds_vault.auth import AppRoleAuth

# Explicit credentials
auth = AppRoleAuth(
    role_id="12345-abcde-67890",
    secret_id="secret-id-from-vault"
)
client = VaultClient(auth=auth)

# From environment (recommended)
# export VAULT_ROLE_ID="12345-abcde-67890"
# export VAULT_SECRET_ID="secret-id-from-vault"
auth = AppRoleAuth()  # Reads from env vars
client = VaultClient(auth=auth)
```

**How to Get AppRole Credentials:**

```bash
# Admin: Create AppRole
vault write auth/approle/role/myapp \
    token_policies="myapp-policy" \
    token_ttl=1h \
    secret_id_ttl=24h

# Admin: Get Role ID (static, safe to embed)
vault read -field=role_id auth/approle/role/myapp/role-id

# Admin: Generate Secret ID (dynamic, deliver securely)
vault write -f -field=secret_id auth/approle/role/myapp/secret-id
```

### Token Authentication

For development or when you have an existing token:

```python
from gds_vault import VaultClient
from gds_vault.auth import TokenAuth

# Direct token
auth = TokenAuth(token="hvs.CAESIF...")
client = VaultClient(auth=auth)

# Shortcut
client = VaultClient.from_token(token="hvs.CAESIF...")
```

> [!WARNING]
> Tokens are sensitive. Never commit tokens to version control. Use environment variables or secure secret delivery.

### Environment-Based Authentication

Let the client auto-detect from environment:

```python
from gds_vault import VaultClient
from gds_vault.auth import EnvironmentAuth

# Tries VAULT_TOKEN first, then AppRole credentials
auth = EnvironmentAuth()
client = VaultClient(auth=auth)

# Or simply (default behavior)
client = VaultClient()
```

**Detection Order:**
1. `VAULT_TOKEN` - Use direct token auth
2. `VAULT_ROLE_ID` + `VAULT_SECRET_ID` - Use AppRole auth
3. Error if neither found

### Choosing an Auth Method

| Scenario | Recommended Method |
|:---|:---|
| Production applications | AppRole |
| CI/CD pipelines | AppRole or Token |
| Local development | Token |
| Quick testing | Environment (Token) |
| Kubernetes workloads | Kubernetes auth (if available) |

[↑ Back to Table of Contents](#table-of-contents)

## Retrieving Secrets

### KV Secrets

For KV v2 secrets engine (default):

```python
from gds_vault import VaultClient

with VaultClient() as client:
    # Full path (including data/)
    secret = client.get_secret("secret/data/myapp/database")

    # If mount_point is set, you can use shorter paths
    # client = VaultClient(mount_point="secret")
    # secret = client.get_secret("data/myapp/database")

    # Access values
    username = secret["username"]
    password = secret["password"]
```

### Secret Paths

Understanding KV v2 path structure:

```
Mount Point: secret/
                │
                ├── data/          ← Read/write secret data
                │   └── myapp/
                │       └── database    → {"username": "app", "password": "..."}
                │
                ├── metadata/      ← Secret metadata
                │   └── myapp/
                │       └── database    → {versions, created_time, ...}
                │
                └── delete/        ← Soft delete operations
```

**Common Path Patterns:**

```python
# Team/app organized
"secret/data/platform/myapp/database"
"secret/data/platform/myapp/api-keys"
"secret/data/analytics/dashboard/credentials"

# Environment organized
"secret/data/prod/database"
"secret/data/staging/database"
"secret/data/dev/database"
```

### Listing Secrets

List secrets at a path:

```python
from gds_vault import VaultClient

with VaultClient() as client:
    # List paths under myapp/
    secrets = client.list_secrets("secret/metadata/myapp/")

    for secret_name in secrets:
        print(f"Found: {secret_name}")
        # Output: database, api-keys, certificates, etc.
```

> [!NOTE]
> Listing requires the `list` capability on the `metadata/` path in your policy.

[↑ Back to Table of Contents](#table-of-contents)

## Caching Strategies

### No Caching

Always fetch fresh secrets from Vault:

```python
from gds_vault import VaultClient
from gds_vault.cache import NoOpCache

client = VaultClient(cache=NoOpCache())

# Every call hits Vault
secret = client.get_secret("secret/data/myapp")  # Network request
secret = client.get_secret("secret/data/myapp")  # Another network request
```

**Use when:**
- Secrets change frequently
- Low latency to Vault server
- Debugging cache issues

### TTL-Based Caching

Cache secrets with time-based expiration:

```python
from gds_vault import VaultClient
from gds_vault.cache import TTLCache

# Cache secrets for 10 minutes
cache = TTLCache(max_size=100, default_ttl=600)
client = VaultClient(cache=cache)

# First call: network request, cached
secret = client.get_secret("secret/data/myapp")

# Subsequent calls within TTL: from cache
secret = client.get_secret("secret/data/myapp")  # Instant, no network

# After 10 minutes: cache expired, new network request
```

**Configuration Options:**

```python
cache = TTLCache(
    max_size=100,      # Max items in cache (LRU eviction)
    default_ttl=300    # Default TTL in seconds
)
```

**Cache Management:**

```python
# Check cache statistics
stats = client.cache_stats
print(f"Cache hits: {stats['hits']}")
print(f"Cache misses: {stats['misses']}")

# Clear entire cache
client.clear_cache()

# Remove specific secret
client.remove_from_cache("secret/data/myapp")
```

### Rotation-Aware Caching

Cache secrets with awareness of rotation schedules:

```python
from gds_vault import VaultClient
from gds_vault.cache import RotationAwareCache

# Automatically refresh before rotation
cache = RotationAwareCache(
    max_size=100,
    buffer_minutes=10,  # Refresh 10 min before rotation
    fallback_ttl=300    # TTL for secrets without rotation info
)
client = VaultClient(cache=cache)

# Cache respects rotation schedules from Vault metadata
secret = client.get_secret("secret/data/myapp/rotating-creds")
```

**How It Works:**
1. Fetches secret from Vault
2. Extracts rotation metadata (if available)
3. Calculates TTL based on next rotation time
4. Refreshes before rotation with configurable buffer

**Use when:**
- Using secrets with known rotation schedules
- Need maximum cache efficiency
- Rotation schedules are configured in Vault

### Choosing a Cache Strategy

| Strategy | When to Use | Pros | Cons |
|:---|:---|:---|:---|
| **NoOpCache** | Debugging, very dynamic secrets | Always fresh | High latency, load on Vault |
| **TTLCache** | Most applications | Simple, effective | May serve stale if rotated |
| **RotationAwareCache** | Rotating credentials | Optimal freshness | Requires rotation metadata |

**Recommended Defaults:**

| Environment | Strategy | TTL |
|:---|:---|:---|
| Development | NoOpCache | N/A |
| Testing | TTLCache | 60 seconds |
| Production | RotationAwareCache | Based on rotation |

[↑ Back to Table of Contents](#table-of-contents)

## Error Handling

### Exception Hierarchy

```python
from gds_vault import (
    VaultError,                 # Base exception
    VaultAuthError,             # Authentication failed
    VaultConnectionError,       # Network issues
    VaultSecretNotFoundError,   # Secret not found (404)
    VaultPermissionError,       # Access denied (403)
    VaultConfigurationError     # Bad configuration
)
```

**Comprehensive Error Handling:**

```python
from gds_vault import (
    VaultClient,
    VaultError,
    VaultAuthError,
    VaultConnectionError,
    VaultSecretNotFoundError,
    VaultPermissionError
)

def get_database_credentials():
    try:
        with VaultClient() as client:
            return client.get_secret("secret/data/myapp/database")

    except VaultSecretNotFoundError:
        # Secret doesn't exist - maybe use defaults
        logger.warning("Database secret not found, using defaults")
        return {"host": "localhost", "username": "dev", "password": "dev"}

    except VaultPermissionError:
        # Access denied - escalate
        logger.error("Permission denied for database secret")
        raise

    except VaultAuthError:
        # Auth failed - check credentials
        logger.error("Vault authentication failed")
        raise

    except VaultConnectionError:
        # Network issue - maybe retry or fail gracefully
        logger.error("Cannot connect to Vault")
        raise

    except VaultError as e:
        # Catch-all for other Vault errors
        logger.error(f"Vault error: {e}")
        raise
```

### Retry Patterns

Configure automatic retries for transient failures:

```python
from gds_vault import VaultClient, RetryPolicy

# Configure retry behavior
retry = RetryPolicy(
    max_retries=5,           # Try up to 5 times
    initial_delay=1.0,       # Start with 1 second delay
    max_delay=16.0,          # Cap delay at 16 seconds
    backoff_factor=2.0       # Double delay each retry
)

client = VaultClient(retry_policy=retry)

# Retries automatically on connection errors
# Delays: 1s → 2s → 4s → 8s → 16s
secret = client.get_secret("secret/data/myapp")
```

**Manual Retry with Decorator:**

```python
from gds_vault import retry_with_backoff

@retry_with_backoff(max_retries=3, initial_delay=0.5)
def fetch_config():
    with VaultClient() as client:
        return client.get_secret("secret/data/config")
```

### Graceful Degradation

Handle failures gracefully in production:

```python
import os
from gds_vault import VaultClient, VaultError

def get_secret_with_fallback(path: str, fallback: dict = None):
    """Get secret from Vault with fallback to environment or defaults."""
    try:
        with VaultClient() as client:
            return client.get_secret(path)
    except VaultError as e:
        logger.warning(f"Vault unavailable: {e}, using fallback")

        # Try environment variables
        if os.getenv("DB_PASSWORD"):
            return {
                "username": os.getenv("DB_USERNAME", "app"),
                "password": os.getenv("DB_PASSWORD"),
                "host": os.getenv("DB_HOST", "localhost")
            }

        # Use provided fallback
        if fallback:
            return fallback

        # No fallback available
        raise

# Usage
creds = get_secret_with_fallback(
    "secret/data/myapp/database",
    fallback={"username": "dev", "password": "dev123", "host": "localhost"}
)
```

[↑ Back to Table of Contents](#table-of-contents)

## Best Practices

### Security

1. **Never log secrets:**

```python
# Bad
logger.info(f"Got password: {secret['password']}")

# Good
logger.info("Successfully retrieved database credentials")
```

2. **Use environment variables for sensitive config:**

```bash
export VAULT_ROLE_ID="..."
export VAULT_SECRET_ID="..."
```

3. **Validate TLS in production:**

```python
# Always in production
client = VaultClient(verify_ssl=True)

# Only in development
if os.getenv("ENV") == "development":
    client = VaultClient(verify_ssl=False)
```

4. **Use least-privilege policies:**

```hcl
# Only read access to specific paths
path "secret/data/myapp/*" {
  capabilities = ["read"]
}
```

### Performance

1. **Use appropriate caching:**

```python
# Production: rotation-aware for best efficiency
cache = RotationAwareCache(buffer_minutes=10)
client = VaultClient(cache=cache)
```

2. **Reuse client instances:**

```python
# Good: Single client instance
client = VaultClient()

def get_config():
    return client.get_secret("secret/data/config")

def get_database():
    return client.get_secret("secret/data/database")
```

3. **Batch secret retrieval if possible:**

```python
# If you need multiple secrets, consider organizing them together
secrets = client.get_secret("secret/data/myapp/all-credentials")
# Contains: database, api_key, smtp, etc.
```

### Resilience

1. **Always use retry policies:**

```python
from gds_vault import VaultClient, RetryPolicy

client = VaultClient(
    retry_policy=RetryPolicy(max_retries=3)
)
```

2. **Handle errors explicitly:**

```python
try:
    secret = client.get_secret(path)
except VaultSecretNotFoundError:
    # Handle missing secret
except VaultError:
    # Handle other errors
```

3. **Have fallback strategies:**

```python
def get_config():
    try:
        return client.get_secret("secret/data/config")
    except VaultError:
        return load_config_from_file()  # Fallback
```

[↑ Back to Table of Contents](#table-of-contents)

## Integration Patterns

### FastAPI Integration

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from gds_vault import VaultClient
from gds_vault.cache import RotationAwareCache

# Global client
vault_client: VaultClient = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global vault_client
    vault_client = VaultClient(
        cache=RotationAwareCache(buffer_minutes=10)
    )
    vault_client.initialize()

    yield

    # Shutdown
    vault_client.cleanup()

app = FastAPI(lifespan=lifespan)

def get_vault_client() -> VaultClient:
    return vault_client

@app.get("/data")
async def get_data(client: VaultClient = Depends(get_vault_client)):
    db_creds = client.get_secret("secret/data/myapp/database")
    # Use credentials
    return {"status": "ok"}
```

### Background Workers

```python
from gds_vault import VaultClient
from gds_vault.cache import TTLCache

class Worker:
    def __init__(self):
        self.vault = VaultClient(
            cache=TTLCache(default_ttl=300)
        )
        self.vault.initialize()

    def process(self):
        creds = self.vault.get_secret("secret/data/worker/credentials")
        # Do work with credentials

    def shutdown(self):
        self.vault.cleanup()

# Usage
worker = Worker()
try:
    while running:
        worker.process()
finally:
    worker.shutdown()
```

### Configuration Management

```python
from dataclasses import dataclass
from gds_vault import VaultClient

@dataclass
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str
    database: str

    @classmethod
    def from_vault(cls, client: VaultClient, path: str) -> "DatabaseConfig":
        secret = client.get_secret(path)
        return cls(
            host=secret["host"],
            port=int(secret.get("port", 5432)),
            username=secret["username"],
            password=secret["password"],
            database=secret["database"]
        )

# Usage
with VaultClient() as client:
    db_config = DatabaseConfig.from_vault(
        client,
        "secret/data/myapp/database"
    )
    print(f"Connecting to {db_config.host}:{db_config.port}")
```

[↑ Back to Table of Contents](#table-of-contents)

## Related Documentation

- **[Vault Concepts Guide](../../explanation/vault/vault-concepts.md)** - Core concepts and fundamentals
- **[Vault Architecture Guide](../../explanation/vault/vault-architecture.md)** - Deployment and security
- **[Vault Reference](../../reference/vault/vault-reference.md)** - API reference and troubleshooting
- **[Rotate AD Passwords](./rotate-ad-passwords.md)** - AD password rotation how-to
- **[gds_vault Developer's Guide](../../../gds_vault/docs/DEVELOPERS_GUIDE.md)** - Complete package documentation

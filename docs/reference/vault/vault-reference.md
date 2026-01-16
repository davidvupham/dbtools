# Vault Reference Guide

**[← Back to Vault Documentation Index](../../explanation/vault/README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 15, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![gds_vault](https://img.shields.io/badge/gds__vault-Latest-blue)
![Document Status](https://img.shields.io/badge/Status-Production-green)

> [!IMPORTANT]
> **Related Docs:** [Concepts](../../explanation/vault/vault-concepts.md) | [Architecture](../../explanation/vault/vault-architecture.md) | [Operations](../../how-to/vault/vault-operations-guide.md)

## Table of Contents

- [gds_vault API Reference](#gds_vault-api-reference)
  - [VaultClient](#vaultclient)
  - [Authentication Strategies](#authentication-strategies)
  - [Cache Classes](#cache-classes)
  - [Retry Policy](#retry-policy)
- [Environment Variables](#environment-variables)
- [Configuration Options](#configuration-options)
- [Exception Types](#exception-types)
- [Troubleshooting](#troubleshooting)
  - [Common Errors](#common-errors)
  - [Connection Issues](#connection-issues)
  - [Authentication Issues](#authentication-issues)
  - [Permission Issues](#permission-issues)
  - [Cache Issues](#cache-issues)
- [Vault CLI Quick Reference](#vault-cli-quick-reference)
- [Glossary](#glossary)
- [External Resources](#external-resources)

## gds_vault API Reference

### VaultClient

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

### Authentication Strategies

#### AppRoleAuth

Machine authentication using Role ID and Secret ID.

```python
from gds_vault.auth import AppRoleAuth

auth = AppRoleAuth(
    role_id: str = None,     # Role ID (or VAULT_ROLE_ID env var)
    secret_id: str = None,   # Secret ID (or VAULT_SECRET_ID env var)
    namespace: str = None    # Optional namespace
)
```

#### TokenAuth

Direct token authentication.

```python
from gds_vault.auth import TokenAuth

auth = TokenAuth(
    token: str,          # Vault token
    ttl: int = 3600      # Token TTL in seconds
)
```

#### EnvironmentAuth

Auto-detect authentication from environment.

```python
from gds_vault.auth import EnvironmentAuth

auth = EnvironmentAuth()  # Tries VAULT_TOKEN, then AppRole
```

### Cache Classes

#### SecretCache

Simple in-memory cache without TTL.

```python
from gds_vault.cache import SecretCache

cache = SecretCache(max_size: int = 100)
```

#### TTLCache

Time-based cache with automatic expiration.

```python
from gds_vault.cache import TTLCache

cache = TTLCache(
    max_size: int = 100,      # Maximum cached items
    default_ttl: int = 300    # Default TTL in seconds
)
```

#### RotationAwareCache

Cache that respects secret rotation schedules.

```python
from gds_vault.cache import RotationAwareCache

cache = RotationAwareCache(
    max_size: int = 100,       # Maximum cached items
    buffer_minutes: int = 10,  # Refresh before rotation
    fallback_ttl: int = 300    # TTL for non-rotating secrets
)
```

#### NoOpCache

Disable caching (always fetch from Vault).

```python
from gds_vault.cache import NoOpCache

cache = NoOpCache()
```

### Retry Policy

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

[↑ Back to Table of Contents](#table-of-contents)

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

[↑ Back to Table of Contents](#table-of-contents)

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

[↑ Back to Table of Contents](#table-of-contents)

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

[↑ Back to Table of Contents](#table-of-contents)

## Troubleshooting

### Common Errors

#### "VAULT_ADDR is required"

**Cause:** Vault address not configured.

**Solution:**

```bash
export VAULT_ADDR="https://vault.example.com:8200"
```

Or provide in code:

```python
client = VaultClient(vault_addr="https://vault.example.com:8200")
```

#### "AppRole credentials must be provided"

**Cause:** Missing Role ID or Secret ID.

**Solution:**

```bash
export VAULT_ROLE_ID="your-role-id"
export VAULT_SECRET_ID="your-secret-id"
```

Or use a different auth method:

```python
from gds_vault import VaultClient, TokenAuth
client = VaultClient(auth=TokenAuth(token="hvs.your-token"))
```

### Connection Issues

#### "Failed to connect to Vault"

**Causes:**
- Vault server not running
- Wrong address/port
- Firewall blocking connection
- Network issues

**Diagnosis:**

```bash
# Test connectivity
curl -v https://vault.example.com:8200/v1/sys/health

# Check DNS
nslookup vault.example.com

# Check port
nc -zv vault.example.com 8200
```

**Solutions:**

1. Verify `VAULT_ADDR` is correct
2. Check firewall rules
3. Verify Vault server is running and unsealed
4. Check network connectivity

#### "SSL: CERTIFICATE_VERIFY_FAILED"

**Cause:** TLS certificate validation failed.

**Solutions:**

1. **Provide CA certificate:**

```python
client = VaultClient(ssl_cert_path="/path/to/ca.crt")
```

2. **Set environment variable:**

```bash
export VAULT_SSL_CERT="/path/to/ca.crt"
# Or for Python requests
export REQUESTS_CA_BUNDLE="/path/to/ca.crt"
```

3. **Development only (not recommended):**

```python
client = VaultClient(verify_ssl=False)  # Never in production!
```

### Authentication Issues

#### "Vault AppRole login failed: permission denied"

**Causes:**
- Invalid Role ID or Secret ID
- AppRole not enabled
- Wrong mount path
- Secret ID expired or used

**Diagnosis:**

```bash
# Check if AppRole is enabled
vault auth list

# Verify role exists
vault read auth/approle/role/your-role

# Test authentication manually
vault write auth/approle/login \
    role_id="your-role-id" \
    secret_id="your-secret-id"
```

**Solutions:**

1. Verify Role ID and Secret ID are correct
2. Generate new Secret ID if expired
3. Check AppRole configuration

#### "token not valid"

**Causes:**
- Token expired
- Token revoked
- Token from different Vault cluster

**Solutions:**

1. Re-authenticate to get new token
2. Check token TTL and renewal
3. Verify using correct Vault cluster

### Permission Issues

#### "permission denied" (403)

**Cause:** Token lacks required policy permissions.

**Diagnosis:**

```bash
# Check token policies
vault token lookup

# Check what policies allow
vault policy read your-policy

# Test specific path
vault kv get secret/data/myapp
```

**Solutions:**

1. Verify path is correct (KV v2 uses `secret/data/` prefix)
2. Check policy has required capabilities (`read`, `list`, etc.)
3. Request policy update from Vault admin

**Common Policy Mistakes:**

```hcl
# Wrong - missing "data" for KV v2
path "secret/myapp/*" {
  capabilities = ["read"]
}

# Correct for KV v2
path "secret/data/myapp/*" {
  capabilities = ["read"]
}

# Also need metadata for list operations
path "secret/metadata/myapp/*" {
  capabilities = ["list"]
}
```

### Cache Issues

#### Stale secrets after rotation

**Cause:** Cache TTL longer than rotation period.

**Solutions:**

1. **Use RotationAwareCache:**

```python
from gds_vault.cache import RotationAwareCache
client = VaultClient(cache=RotationAwareCache(buffer_minutes=10))
```

2. **Reduce TTL:**

```python
from gds_vault.cache import TTLCache
client = VaultClient(cache=TTLCache(default_ttl=60))  # 1 minute
```

3. **Clear cache manually:**

```python
client.clear_cache()
# or for specific secret
client.remove_from_cache("secret/data/myapp")
```

4. **Disable caching:**

```python
from gds_vault.cache import NoOpCache
client = VaultClient(cache=NoOpCache())
```

[↑ Back to Table of Contents](#table-of-contents)

## Vault CLI Quick Reference

### Authentication

```bash
# Login with token
vault login hvs.your-token

# Login with AppRole
vault write auth/approle/login \
    role_id="..." \
    secret_id="..."

# Check current token
vault token lookup
```

### KV Secrets (v2)

```bash
# Write secret
vault kv put secret/myapp password="secret123"

# Read secret
vault kv get secret/myapp

# Read specific version
vault kv get -version=2 secret/myapp

# List secrets
vault kv list secret/

# Delete secret (soft delete)
vault kv delete secret/myapp

# Undelete
vault kv undelete -versions=1 secret/myapp

# Permanently delete
vault kv destroy -versions=1 secret/myapp
```

### Policies

```bash
# List policies
vault policy list

# Read policy
vault policy read myapp-policy

# Write policy
vault policy write myapp-policy policy.hcl
```

### AppRole Management

```bash
# Enable AppRole
vault auth enable approle

# Create role
vault write auth/approle/role/myapp \
    token_policies="myapp-policy" \
    token_ttl=1h

# Get Role ID
vault read auth/approle/role/myapp/role-id

# Generate Secret ID
vault write -f auth/approle/role/myapp/secret-id
```

### Status and Health

```bash
# Server status
vault status

# Seal status
vault operator seal-status

# Health check
curl https://vault.example.com:8200/v1/sys/health
```

[↑ Back to Table of Contents](#table-of-contents)

## Glossary

| Term | Definition |
|:---|:---|
| **AppRole** | Auth method for machine authentication using Role ID and Secret ID |
| **Auth Method** | Plugin that verifies client identity (AppRole, Token, LDAP, etc.) |
| **Barrier** | Encryption layer protecting all Vault data |
| **Capability** | Permission type (create, read, update, delete, list, deny) |
| **Dynamic Secret** | Credential generated on-demand with automatic expiration |
| **Lease** | Time-limited grant of access to a secret |
| **Mount** | Path where a secrets engine or auth method is enabled |
| **Namespace** | Isolated tenant within Vault (Enterprise feature) |
| **Policy** | Rules defining what paths a token can access |
| **Role ID** | Static identifier for an AppRole (like a username) |
| **Seal** | State where Vault cannot access encrypted data |
| **Secret ID** | Dynamic credential for AppRole (like a password) |
| **Secrets Engine** | Plugin that stores or generates secrets (KV, Database, etc.) |
| **Static Secret** | Long-lived secret stored in KV engine |
| **Token** | Primary authentication credential in Vault |
| **TTL** | Time-To-Live, duration before expiration |
| **Unseal** | Process of decrypting Vault's master key |

[↑ Back to Table of Contents](#table-of-contents)

## External Resources

### Official HashiCorp Documentation

- [HashiCorp Vault Documentation](https://developer.hashicorp.com/vault/docs) - Comprehensive official docs
- [Vault API Reference](https://developer.hashicorp.com/vault/api-docs) - REST API documentation
- [Vault Tutorials](https://developer.hashicorp.com/vault/tutorials) - Hands-on tutorials
- [Production Hardening Guide](https://developer.hashicorp.com/vault/docs/concepts/production-hardening) - Security hardening

### Best Practices and Patterns

- [AppRole Best Practices](https://developer.hashicorp.com/vault/docs/auth/approle/approle-pattern) - Authentication patterns
- [Recommended Pattern for AppRole](https://developer.hashicorp.com/vault/tutorials/recommended-patterns/pattern-approle) - AppRole tutorial
- [Audit Logging Best Practices](https://developer.hashicorp.com/vault/docs/audit/best-practices) - Audit configuration
- [Recommended Patterns](https://developer.hashicorp.com/vault/docs/internals/recommended-patterns) - Architecture patterns
- [Programmatic Best Practices](https://developer.hashicorp.com/vault/docs/configuration/programmatic-best-practices) - Automation

### Secrets Engines

- [KV Secrets Engine v2](https://developer.hashicorp.com/vault/docs/secrets/kv/kv-v2) - KV engine reference
- [KV v2 API Reference](https://developer.hashicorp.com/vault/api-docs/secret/kv/kv-v2) - KV API docs
- [Store Versioned KV Secrets](https://developer.hashicorp.com/vault/tutorials/secrets-management/versioned-kv) - KV tutorial
- [Upgrading KV v1 to v2](https://support.hashicorp.com/hc/en-us/articles/44684220257555-Upgrading-Vault-KV-Secrets-Engine-from-Version-1-to-Version-2) - Migration guide

### Troubleshooting Resources

- [Troubleshoot Vault](https://developer.hashicorp.com/vault/tutorials/monitoring/troubleshooting-vault) - Troubleshooting guide
- [Query Audit Device Logs](https://developer.hashicorp.com/vault/tutorials/monitoring/query-audit-device-logs) - Audit analysis
- [Monitor and Understand Audit Logs](https://notes.kodekloud.com/docs/HashiCorp-Certified-Vault-Operations-Professional-2022/Monitor-a-Vault-Environment/Monitor-and-Understand-Audit-Logs) - KodeKloud guide

### Python and Caching

- [Vault Agent Caching](https://developer.hashicorp.com/vault/docs/agent-and-proxy/agent/caching) - Agent caching docs
- [Python Secrets Management Best Practices](https://blog.gitguardian.com/how-to-handle-secrets-in-python/) - GitGuardian guide
- [AWS Secrets Manager Python Caching](https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_cache-python.html) - Alternative caching pattern

### Package Documentation

- [gds_vault Developer's Guide](../../../python/gds_vault/docs/DEVELOPERS_GUIDE.md) - Complete API usage
- [gds_vault Beginner's Guide](../../../python/gds_vault/docs/BEGINNERS_GUIDE.md) - Python concepts explained
- [Rotation-Aware TTL Guide](../../../python/gds_vault/docs/ROTATION_AWARE_TTL_GUIDE.md) - Rotation-aware caching

[↑ Back to Table of Contents](#table-of-contents)

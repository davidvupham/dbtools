## gds_vault Developer's Guide

This guide explains how to use all functionality in `gds_vault`, from basic secret retrieval to advanced, production-ready configurations. It covers the modern client, legacy client (for backward compatibility), authentication strategies, caching (TTL and rotation-aware), retry policies, SSL and namespaces, mount points, the optional HTTP transport, exceptions, logging, and best practices.

### Table of Contents
- Overview and Installation
- Quick Start (Modern Client)
- Authentication Strategies
- Caching Options (SecretCache, TTLCache, RotationAwareCache, NoOpCache)
- Retry Policies
- SSL and Namespace Configuration
- Mount Points
- Optional HTTP Transport (Session, centralized SSL/namespace)
- Error Handling and Exceptions
- Context Manager Usage and Resource Lifecycle
- Configuration Patterns and Class Constructors
- Logging Guidance
- Legacy Client (vault.py) — Compatibility Notes
- Advanced Topics (Thread-safety, Testing, Performance)

---

### Overview and Installation

`gds_vault` provides a production-ready, OOP-designed client for HashiCorp Vault with:
- Strategy-based authentication (AppRole, Token, Environment)
- Pluggable caching (simple, TTL, rotation-aware, or disabled)
- Configurable retry policy with exponential backoff
- Strong exception hierarchy and comprehensive logging

Install:

```bash
pip install -e gds_vault/

# Or from within the project root (if packaged):
pip install gds-vault
```

Environment variables commonly used:
- `VAULT_ADDR`: Vault URL
- `VAULT_ROLE_ID`: For AppRole
- `VAULT_SECRET_ID`: For AppRole
- `VAULT_TOKEN`: For EnvironmentAuth
- `VAULT_MOUNT_POINT`: Optional default mount
- `VAULT_NAMESPACE`: Optional namespace (Vault Enterprise)
- `VAULT_SSL_CERT`: Optional path to CA bundle

---

### Quick Start (Modern Client)

```python
from gds_vault import VaultClient

# Uses VAULT_ADDR, VAULT_ROLE_ID, VAULT_SECRET_ID from environment
client = VaultClient()
secret = client.get_secret('secret/data/myapp')
print(secret['password'])

# Context manager (auto-init, auto-cleanup)
with VaultClient() as c:
    s = c.get_secret('secret/data/myapp')
```

Alternative constructors:

```python
from gds_vault import VaultClient, TokenAuth, TTLCache, RetryPolicy

# From configuration dict
cfg = {
    'vault_addr': 'https://vault.example.com',
    'timeout': 15,
    'max_retries': 5,
    'mount_point': 'kv-v2',
}
client = VaultClient.from_config(cfg)

# From token (bypasses AppRole)
client = VaultClient.from_token(token='hvs.CAESIF...', vault_addr='https://vault.example.com')

# Custom cache and retry policy
client = VaultClient(cache=TTLCache(max_size=50, default_ttl=600), retry_policy=RetryPolicy(max_retries=5))
```

---

### Authentication Strategies

`VaultClient` composes an `AuthStrategy`:
- `AppRoleAuth(role_id=None, secret_id=None, namespace=None)`
- `TokenAuth(token, ttl=3600)`
- `EnvironmentAuth(ttl=3600)` (reads `VAULT_TOKEN`)

```python
from gds_vault import VaultClient
from gds_vault.auth import AppRoleAuth, TokenAuth, EnvironmentAuth

# Explicit AppRole
client = VaultClient(auth=AppRoleAuth(role_id='role', secret_id='secret'))

# Direct token
client = VaultClient(auth=TokenAuth(token='hvs.CAESIF...'))

# Token from environment
client = VaultClient(auth=EnvironmentAuth())
```

---

### Caching Options

Available caches implement a simple interface (`CacheProtocol`) and are drop-in:
- `SecretCache(max_size=100)`: in-memory, no TTL
- `TTLCache(max_size=100, default_ttl=300)`: per-key TTL, supports optional rotation metadata
- `RotationAwareCache(max_size=100, buffer_minutes=10, fallback_ttl=300)`: rotation schedule-aware TTL
- `NoOpCache()`: disables caching entirely

```python
from gds_vault import VaultClient
from gds_vault.cache import SecretCache, TTLCache, RotationAwareCache, NoOpCache

# Simple cache
client = VaultClient(cache=SecretCache(max_size=200))

# TTL cache
client = VaultClient(cache=TTLCache(default_ttl=600))

# Rotation-aware cache
client = VaultClient(cache=RotationAwareCache(buffer_minutes=15, fallback_ttl=300))

# No cache
client = VaultClient(cache=NoOpCache())
```

Rotation-aware flow (automatic when Vault returns rotation metadata):
- Client extracts rotation metadata and supplies it to caches that accept it.
- `TTLCache` and `RotationAwareCache` will respect provided rotation schedules (when available) to compute TTL/refresh windows.

Cache management:

```python
client.clear_cache()             # clear all entries
client.remove_from_cache(key)    # remove one
len(client)                      # number of cached entries
client.cache_stats               # detailed statistics
```

Thread-safety: caches use internal locks for `get/set/remove/clear` and stats; safe for multi-threaded use.

---

### Retry Policies

Use `RetryPolicy` to wrap network operations with exponential backoff.

```python
from gds_vault import RetryPolicy, VaultClient

retry = RetryPolicy(max_retries=5, initial_delay=1.0, max_delay=16.0, backoff_factor=2.0)
client = VaultClient(retry_policy=retry)
```

Decorator variant (for your own functions):

```python
from gds_vault import retry_with_backoff

@retry_with_backoff(max_retries=3, initial_delay=0.5)
def do_io():
    ...
```

---

### SSL and Namespace Configuration

Modern client options:
- `verify_ssl=True|False`
- `ssl_cert_path='/path/to/ca-bundle.crt'`
- `namespace='team-space'` (adds `X-Vault-Namespace` header)

```python
client = VaultClient(
    verify_ssl=True,
    ssl_cert_path='/etc/ssl/my-ca.pem',
    namespace='my-ns',
)
```

Behavior:
- If `ssl_cert_path` is set, it is used for `requests` `verify=`.
- If not set, `verify_ssl` is used.

---

### Mount Points

Mount points can be provided via `mount_point` or `VAULT_MOUNT_POINT`. If set, it’s prepended when the path doesn’t already start with it.

```python
client = VaultClient(mount_point='kv-v2')

# Will request /v1/kv-v2/data/myapp
secret = client.get_secret('data/myapp')

# Path that already starts with mount point is not modified
secret = client.get_secret('kv-v2/data/myapp')
```

---

### Optional HTTP Transport (Session, centralized SSL/namespace)

For advanced scenarios, inject a `VaultTransport` to centralize SSL/namespace behavior and reuse a `requests.Session`:

```python
from gds_vault.gds_vault.transport import VaultTransport
from gds_vault import VaultClient

transport = VaultTransport(
    verify_ssl=True,
    ssl_cert_path='/etc/ssl/my-ca.pem',
    namespace='my-ns',
)

client = VaultClient(transport=transport)
```

Notes:
- The transport is optional; if not supplied, the client uses `requests` directly.
- The transport currently covers read/list requests; authentication is handled by the auth strategy (which already supports namespace and SSL options).

---

### Error Handling and Exceptions

Catch specific exceptions when possible:

```python
from gds_vault import (
    VaultError,
    VaultAuthError,
    VaultConnectionError,
    VaultSecretNotFoundError,
    VaultPermissionError,
    VaultConfigurationError,
)

try:
    secret = client.get_secret('secret/data/myapp')
except VaultSecretNotFoundError:
    ...  # handle 404
except VaultPermissionError:
    ...  # handle 403
except VaultConnectionError:
    ...  # network/connection
except VaultConfigurationError:
    ...  # invalid VAULT_ADDR, etc.
except VaultAuthError:
    ...  # auth failures
except VaultError:
    ...  # catch-all for gds_vault errors
```

---

### Context Manager Usage and Resource Lifecycle

`VaultClient` implements a resource manager lifecycle:

```python
with VaultClient() as c:
    data = c.get_secret('secret/data/myapp')
# Resources cleaned up; cache cleared
```

Outside a context, you can also manage lifecycle explicitly:

```python
c = VaultClient()
c.initialize()
# ... use c ...
c.cleanup()
```

---

### Configuration Patterns and Class Constructors

Options:
- Environment-driven: simply call `VaultClient()` and rely on env vars.
- `from_environment(**kwargs)`: identical to constructor but conveys intent.
- `from_config(config_dict)`: centralized config (addr, timeout, retries, mount)
- `from_token(token, vault_addr=None, **kwargs)`: direct token flows

You can also set and get arbitrary configuration data:

```python
client.set_config('feature_x_enabled', True)
flag = client.get_config('feature_x_enabled', False)
all_cfg = client.get_all_config()
```

---

### Logging Guidance

Configure logging in your application to control verbosity:

```python
import logging
logging.basicConfig(level=logging.INFO)

# To debug
logging.getLogger('gds_vault').setLevel(logging.DEBUG)
```

The client logs:
- Authentication start/success/failure (without secrets)
- Secret fetch/list operations
- Cache hits/misses, TTL expirations, rotation-derived TTLs
- Retry attempts and backoff timings

---

### Legacy Client (vault.py) — Compatibility Notes

`gds_vault/gds_vault/vault.py` provides a legacy `VaultClient` and `get_secret_from_vault` function for backward compatibility. Behavior is aligned to the modern exception hierarchy (e.g., connection → `VaultConnectionError`, 404 → `VaultSecretNotFoundError`). Prefer the modern client for new development.

Example (legacy):

```python
from gds_vault.vault import VaultClient as LegacyVaultClient, get_secret_from_vault

with LegacyVaultClient() as c:
    s = c.get_secret('secret/data/myapp')

d = get_secret_from_vault('secret/data/myapp')
```

---

### Advanced Topics (Thread-safety, Testing, Performance)

- Thread-safety: caches are guarded by internal locks and safe for concurrent use. If multiple threads share a client, consider the lifecycle carefully (e.g., context usage or explicit initialization/cleanup).
- Testing: the repository includes extensive unit tests with mocking for auth, secret retrieval, caches, retry, and exception mapping. For integration, run a Vault dev server and the provided integration tests.
- Performance: use `TTLCache` or `RotationAwareCache` to reduce round-trips; inject a `VaultTransport` to reuse a session; tune `RetryPolicy` for your environment.

---

### Common Recipes

1) KV v2 with mount point and TTL cache:
```python
from gds_vault import VaultClient
from gds_vault.cache import TTLCache

client = VaultClient(mount_point='kv-v2', cache=TTLCache(default_ttl=900))
db = client.get_secret('data/myapp')
```

2) Use direct token with custom retry and CA bundle:
```python
from gds_vault import VaultClient, RetryPolicy
from gds_vault.auth import TokenAuth

client = VaultClient(
    auth=TokenAuth(token='hvs.CAESIF...'),
    retry_policy=RetryPolicy(max_retries=4, initial_delay=0.5),
    ssl_cert_path='/etc/ssl/my-ca.pem',
)
secret = client.get_secret('secret/data/myapp')
```

3) Rotation-aware cache (auto-refresh near rotation window):
```python
from gds_vault import VaultClient
from gds_vault.cache import RotationAwareCache

client = VaultClient(cache=RotationAwareCache(buffer_minutes=10))
pwd = client.get_secret('secret/data/rotating-credential')['password']
```

4) Modern exception handling pattern:
```python
from gds_vault import VaultClient, VaultError, VaultSecretNotFoundError

try:
    with VaultClient() as c:
        s = c.get_secret('secret/data/myapp')
except VaultSecretNotFoundError:
    # handle missing secret
except VaultError as e:
    # generic fallback
    raise
```

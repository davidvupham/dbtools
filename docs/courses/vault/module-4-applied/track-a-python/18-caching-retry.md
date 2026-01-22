# Caching and retry

**[← Back to Track A: Python Integration](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-4_Applied-blue)
![Lesson](https://img.shields.io/badge/Lesson-18-purple)

## Learning objectives

By the end of this lesson, you will be able to:

- Implement client-side caching for Vault secrets
- Configure retry logic with exponential backoff
- Handle transient errors gracefully
- Build resilient applications that tolerate Vault unavailability

## Table of contents

- [Why caching and retry matter](#why-caching-and-retry-matter)
- [Client-side caching](#client-side-caching)
- [Retry strategies](#retry-strategies)
- [Error handling patterns](#error-handling-patterns)
- [Building a resilient client](#building-a-resilient-client)
- [Hands-on lab](#hands-on-lab)
- [Key takeaways](#key-takeaways)

---

## Why caching and retry matter

Network calls to Vault can fail for many reasons. A resilient application must handle these gracefully.

### Common failure scenarios

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Failure Scenarios and Mitigations                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Scenario                 │ Impact              │ Mitigation               │
│   ─────────────────────────┼─────────────────────┼────────────────────────  │
│   Network timeout          │ Request hangs       │ Timeout + retry          │
│   Vault restart            │ Brief unavailability│ Retry with backoff       │
│   Vault sealed             │ All requests fail   │ Cache + alerts           │
│   Rate limiting            │ 429 responses       │ Backoff + cache          │
│   Token expired            │ 403 responses       │ Re-authentication        │
│   Network partition        │ Connection refused  │ Cache + retry            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The cost of Vault calls

| Operation | Typical Latency | Impact at Scale |
|-----------|----------------|-----------------|
| Secret read | 5-20ms | 1000 req/s = 5-20s of latency/s |
| Token lookup | 2-10ms | Authentication overhead |
| Dynamic secret | 50-200ms | Database credential generation |

**Caching reduces:**
- Network round-trips
- Vault load
- Application latency
- Failure impact

[↑ Back to Table of Contents](#table-of-contents)

---

## Client-side caching

Implement intelligent caching to reduce Vault calls while maintaining security.

### Simple TTL-based cache

```python
import time
from typing import Any, Optional
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class CacheEntry:
    """A single cached value with expiration."""
    value: Any
    expires_at: float

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class SecretCache:
    """Thread-safe secret cache with TTL expiration."""

    def __init__(self, default_ttl_seconds: int = 300):
        self.default_ttl = default_ttl_seconds
        self._cache: dict[str, CacheEntry] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get a cached value if it exists and hasn't expired."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            if entry.is_expired():
                del self._cache[key]
                return None
            return entry.value

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Store a value in the cache."""
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expires_at = time.time() + ttl

        with self._lock:
            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)

    def delete(self, key: str) -> None:
        """Remove a value from the cache."""
        with self._lock:
            self._cache.pop(key, None)

    def clear(self) -> None:
        """Clear all cached values."""
        with self._lock:
            self._cache.clear()


# Usage
cache = SecretCache(default_ttl_seconds=300)

# Cache a secret
cache.set("secret/myapp/config", {"db_pass": "secret123"})

# Retrieve from cache
cached = cache.get("secret/myapp/config")
if cached:
    print(f"Cache hit: {cached}")
```

### Cached Vault client

```python
from typing import Optional, Any
from gds_vault import VaultClient


class CachedVaultClient:
    """Vault client with built-in caching."""

    def __init__(
        self,
        client: VaultClient,
        cache_ttl_seconds: int = 300,
    ):
        self._client = client
        self._cache = SecretCache(default_ttl_seconds=cache_ttl_seconds)

    def get_secret(
        self,
        path: str,
        bypass_cache: bool = False,
        cache_ttl: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Get a secret, using cache if available.

        Args:
            path: Secret path
            bypass_cache: If True, always fetch from Vault
            cache_ttl: Optional override for cache TTL
        """
        # Check cache first (unless bypassing)
        if not bypass_cache:
            cached = self._cache.get(path)
            if cached is not None:
                return cached

        # Fetch from Vault
        secret = self._client.get_secret(path)

        # Cache the result
        self._cache.set(path, secret, ttl_seconds=cache_ttl)

        return secret

    def invalidate(self, path: str) -> None:
        """Invalidate a cached secret."""
        self._cache.delete(path)

    def clear_cache(self) -> None:
        """Clear all cached secrets."""
        self._cache.clear()

    def close(self) -> None:
        """Close the underlying client."""
        self._client.close()

    def __enter__(self) -> "CachedVaultClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()


# Usage
with VaultClient(vault_addr="http://127.0.0.1:8200", token="root") as client:
    cached_client = CachedVaultClient(client, cache_ttl_seconds=300)

    # First call fetches from Vault
    secret1 = cached_client.get_secret("secret/data/myapp/config")

    # Second call uses cache
    secret2 = cached_client.get_secret("secret/data/myapp/config")

    # Force refresh
    secret3 = cached_client.get_secret("secret/data/myapp/config", bypass_cache=True)
```

### Lease-aware caching

For dynamic secrets, cache based on lease duration:

```python
from dataclasses import dataclass
from typing import Optional


@dataclass
class LeaseInfo:
    """Information about a Vault lease."""
    lease_id: str
    lease_duration: int
    renewable: bool


class LeaseAwareCache(SecretCache):
    """Cache that respects Vault lease durations."""

    def set_with_lease(
        self,
        key: str,
        value: Any,
        lease_info: Optional[LeaseInfo] = None,
        safety_margin_seconds: int = 60,
    ) -> None:
        """
        Cache a value respecting its lease duration.

        Args:
            key: Cache key
            value: Value to cache
            lease_info: Vault lease information
            safety_margin_seconds: Time before expiry to invalidate
        """
        if lease_info and lease_info.lease_duration > 0:
            # Cache for slightly less than lease duration
            ttl = max(lease_info.lease_duration - safety_margin_seconds, 10)
        else:
            ttl = self.default_ttl

        self.set(key, value, ttl_seconds=ttl)


# Usage with dynamic secrets
def get_database_credentials(client: VaultClient, cache: LeaseAwareCache) -> dict:
    """Get database credentials with lease-aware caching."""
    cache_key = "database/creds/myapp"

    # Check cache
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Fetch from Vault
    response = client.get_secret("database/creds/myapp-role")

    # Extract lease info
    lease_info = LeaseInfo(
        lease_id=response.get("lease_id", ""),
        lease_duration=response.get("lease_duration", 3600),
        renewable=response.get("renewable", False),
    )

    # Cache with lease awareness
    cache.set_with_lease(cache_key, response["data"], lease_info)

    return response["data"]
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Retry strategies

Implement intelligent retry logic to handle transient failures.

### Exponential backoff

```python
import time
import random
from typing import TypeVar, Callable, Optional
from functools import wraps

T = TypeVar("T")


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay_seconds: float = 0.5,
        max_delay_seconds: float = 30.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay_seconds
        self.max_delay = max_delay_seconds
        self.exponential_base = exponential_base
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for a given attempt number."""
        delay = self.initial_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)

        if self.jitter:
            # Add random jitter (±25%)
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)

        return max(delay, 0)


def retry_with_backoff(
    config: Optional[RetryConfig] = None,
    retryable_exceptions: tuple = (Exception,),
):
    """
    Decorator that retries a function with exponential backoff.

    Args:
        config: Retry configuration
        retryable_exceptions: Tuple of exceptions that trigger retry
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e

                    if attempt < config.max_attempts - 1:
                        delay = config.get_delay(attempt)
                        time.sleep(delay)

            raise last_exception

        return wrapper
    return decorator


# Usage
@retry_with_backoff(
    config=RetryConfig(max_attempts=3, initial_delay_seconds=0.5),
    retryable_exceptions=(ConnectionError, TimeoutError),
)
def fetch_secret(client: VaultClient, path: str) -> dict:
    """Fetch a secret with automatic retry."""
    return client.get_secret(path)
```

### Retry with circuit breaker

```python
import time
from enum import Enum
from threading import Lock
from typing import Callable, TypeVar

T = TypeVar("T")


class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    Prevents cascading failures by stopping calls to a failing service.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout_seconds: float = 30.0,
        success_threshold: int = 2,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout_seconds
        self.success_threshold = success_threshold

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float = 0
        self._lock = Lock()

    @property
    def state(self) -> CircuitState:
        with self._lock:
            if self._state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if time.time() - self._last_failure_time > self.recovery_timeout:
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
            return self._state

    def record_success(self) -> None:
        """Record a successful call."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0

    def record_failure(self) -> None:
        """Record a failed call."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
            elif self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN

    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute a function through the circuit breaker."""
        if self.state == CircuitState.OPEN:
            raise CircuitBreakerOpenError("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


# Usage
circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout_seconds=30,
)


def get_secret_with_circuit_breaker(client: VaultClient, path: str) -> dict:
    """Get a secret with circuit breaker protection."""
    return circuit_breaker.call(client.get_secret, path)
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Error handling patterns

Handle Vault-specific errors appropriately.

### Error classification

```python
from enum import Enum
from typing import Optional
import requests


class VaultErrorType(Enum):
    """Classification of Vault errors."""
    TRANSIENT = "transient"        # Retry may succeed
    AUTHENTICATION = "authentication"  # Re-auth needed
    AUTHORIZATION = "authorization"    # Permission issue
    NOT_FOUND = "not_found"        # Secret doesn't exist
    PERMANENT = "permanent"        # Don't retry


def classify_vault_error(error: Exception) -> VaultErrorType:
    """Classify a Vault error for appropriate handling."""
    error_str = str(error).lower()

    # Check HTTP status codes if available
    if isinstance(error, requests.HTTPError):
        status = error.response.status_code
        if status == 429:  # Rate limited
            return VaultErrorType.TRANSIENT
        if status == 401:  # Unauthorized
            return VaultErrorType.AUTHENTICATION
        if status == 403:  # Forbidden
            return VaultErrorType.AUTHORIZATION
        if status == 404:  # Not found
            return VaultErrorType.NOT_FOUND
        if status >= 500:  # Server error
            return VaultErrorType.TRANSIENT

    # Check error messages
    if "connection" in error_str or "timeout" in error_str:
        return VaultErrorType.TRANSIENT
    if "permission denied" in error_str:
        return VaultErrorType.AUTHORIZATION
    if "invalid token" in error_str or "token expired" in error_str:
        return VaultErrorType.AUTHENTICATION
    if "no secrets" in error_str or "not found" in error_str:
        return VaultErrorType.NOT_FOUND

    return VaultErrorType.PERMANENT
```

### Comprehensive error handler

```python
import logging
from typing import Callable, TypeVar, Optional

T = TypeVar("T")
logger = logging.getLogger(__name__)


class VaultErrorHandler:
    """Handles Vault errors with appropriate strategies."""

    def __init__(
        self,
        retry_config: RetryConfig,
        on_auth_failure: Optional[Callable[[], None]] = None,
        fallback_value: Optional[T] = None,
    ):
        self.retry_config = retry_config
        self.on_auth_failure = on_auth_failure
        self.fallback_value = fallback_value

    def execute(
        self,
        operation: Callable[[], T],
        operation_name: str = "vault_operation",
    ) -> T:
        """Execute an operation with comprehensive error handling."""
        last_exception = None

        for attempt in range(self.retry_config.max_attempts):
            try:
                return operation()

            except Exception as e:
                last_exception = e
                error_type = classify_vault_error(e)

                logger.warning(
                    f"{operation_name} failed (attempt {attempt + 1}): "
                    f"{error_type.value} - {e}"
                )

                if error_type == VaultErrorType.TRANSIENT:
                    # Retry with backoff
                    if attempt < self.retry_config.max_attempts - 1:
                        delay = self.retry_config.get_delay(attempt)
                        time.sleep(delay)
                        continue

                elif error_type == VaultErrorType.AUTHENTICATION:
                    # Try re-authentication
                    if self.on_auth_failure:
                        self.on_auth_failure()
                        continue
                    break

                elif error_type == VaultErrorType.NOT_FOUND:
                    # Don't retry, secret doesn't exist
                    if self.fallback_value is not None:
                        return self.fallback_value
                    break

                else:
                    # Permanent error, don't retry
                    break

        # All attempts failed
        if self.fallback_value is not None:
            logger.error(
                f"{operation_name} failed after all attempts, using fallback"
            )
            return self.fallback_value

        raise last_exception


# Usage
handler = VaultErrorHandler(
    retry_config=RetryConfig(max_attempts=3),
    on_auth_failure=lambda: reauthenticate(),
    fallback_value={"default": "value"},
)

result = handler.execute(
    operation=lambda: client.get_secret("secret/data/myapp/config"),
    operation_name="get_app_config",
)
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Building a resilient client

Combine caching, retry, and error handling into a production-ready client.

### Resilient Vault client

```python
import logging
from typing import Optional, Any, Callable
from dataclasses import dataclass
from gds_vault import VaultClient

logger = logging.getLogger(__name__)


@dataclass
class ResilienceConfig:
    """Configuration for resilient Vault client."""
    cache_ttl_seconds: int = 300
    retry_max_attempts: int = 3
    retry_initial_delay: float = 0.5
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 30.0


class ResilientVaultClient:
    """
    Production-ready Vault client with:
    - Caching
    - Retry with exponential backoff
    - Circuit breaker
    - Comprehensive error handling
    """

    def __init__(
        self,
        client: VaultClient,
        config: Optional[ResilienceConfig] = None,
        create_client: Optional[Callable[[], VaultClient]] = None,
    ):
        self._client = client
        self._config = config or ResilienceConfig()
        self._create_client = create_client

        # Initialize components
        self._cache = SecretCache(self._config.cache_ttl_seconds)
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=self._config.circuit_breaker_threshold,
            recovery_timeout_seconds=self._config.circuit_breaker_timeout,
        )
        self._retry_config = RetryConfig(
            max_attempts=self._config.retry_max_attempts,
            initial_delay_seconds=self._config.retry_initial_delay,
        )

    def get_secret(
        self,
        path: str,
        bypass_cache: bool = False,
        cache_ttl: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Get a secret with full resilience.

        Args:
            path: Secret path
            bypass_cache: Skip cache lookup
            cache_ttl: Override cache TTL

        Returns:
            Secret data
        """
        # 1. Check cache
        if not bypass_cache:
            cached = self._cache.get(path)
            if cached is not None:
                logger.debug(f"Cache hit for {path}")
                return cached

        # 2. Check circuit breaker
        if self._circuit_breaker.state == CircuitState.OPEN:
            # Try to return stale cache if available
            stale = self._cache.get(path)
            if stale:
                logger.warning(f"Circuit open, using stale cache for {path}")
                return stale
            raise CircuitBreakerOpenError("Vault circuit breaker is open")

        # 3. Fetch with retry
        handler = VaultErrorHandler(
            retry_config=self._retry_config,
            on_auth_failure=self._reauthenticate,
        )

        try:
            secret = handler.execute(
                operation=lambda: self._circuit_breaker.call(
                    self._client.get_secret, path
                ),
                operation_name=f"get_secret({path})",
            )

            # 4. Cache the result
            self._cache.set(path, secret, ttl_seconds=cache_ttl)

            return secret

        except Exception as e:
            # Last resort: return stale cache
            stale = self._cache.get(path)
            if stale:
                logger.error(f"All attempts failed, using stale cache for {path}")
                return stale
            raise

    def _reauthenticate(self) -> None:
        """Re-authenticate to Vault."""
        if self._create_client:
            logger.info("Re-authenticating to Vault")
            self._client = self._create_client()

    def invalidate(self, path: str) -> None:
        """Invalidate a cached secret."""
        self._cache.delete(path)

    def close(self) -> None:
        """Close the client."""
        self._client.close()

    def __enter__(self) -> "ResilientVaultClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()


# Usage
def create_vault_client() -> VaultClient:
    return VaultClient(
        vault_addr=os.environ["VAULT_ADDR"],
        role_id=os.environ["VAULT_ROLE_ID"],
        secret_id=os.environ["VAULT_SECRET_ID"],
    )


config = ResilienceConfig(
    cache_ttl_seconds=300,
    retry_max_attempts=3,
    circuit_breaker_threshold=5,
)

with ResilientVaultClient(
    client=create_vault_client(),
    config=config,
    create_client=create_vault_client,
) as vault:
    # This call has caching, retry, and circuit breaker
    secret = vault.get_secret("secret/data/myapp/config")
    print(f"Database: {secret['data']['db_host']}")
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Hands-on lab

### Prerequisites

- Python 3.9+
- Vault dev server

### Setup

```bash
# Start Vault
docker run -d --name vault-resilience \
    -p 8200:8200 \
    -e 'VAULT_DEV_ROOT_TOKEN_ID=root' \
    hashicorp/vault:1.15

export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'

# Create test secret
vault kv put secret/myapp/config db_host="postgres" db_pass="secret"
```

### Exercise 1: Implement simple caching

1. Create the cache module:

   ```python
   # cache_demo.py
   import time

   class SimpleCache:
       def __init__(self, ttl_seconds=60):
           self._cache = {}
           self._ttl = ttl_seconds

       def get(self, key):
           entry = self._cache.get(key)
           if entry and time.time() < entry["expires"]:
               print(f"[CACHE HIT] {key}")
               return entry["value"]
           print(f"[CACHE MISS] {key}")
           return None

       def set(self, key, value):
           self._cache[key] = {
               "value": value,
               "expires": time.time() + self._ttl
           }
           print(f"[CACHE SET] {key}")


   # Test the cache
   cache = SimpleCache(ttl_seconds=5)

   cache.set("test", {"data": "value"})
   print(cache.get("test"))  # Hit
   print(cache.get("test"))  # Hit

   print("Waiting for expiry...")
   time.sleep(6)

   print(cache.get("test"))  # Miss
   ```

2. Run the demo:

   ```bash
   python cache_demo.py
   ```

**Observation:** The cache returns hits until TTL expires.

### Exercise 2: Implement retry with backoff

1. Create retry demo:

   ```python
   # retry_demo.py
   import time
   import random

   def retry_with_backoff(func, max_attempts=3):
       for attempt in range(max_attempts):
           try:
               return func()
           except Exception as e:
               if attempt < max_attempts - 1:
                   delay = (2 ** attempt) + random.uniform(0, 1)
                   print(f"Attempt {attempt + 1} failed: {e}")
                   print(f"Retrying in {delay:.2f}s...")
                   time.sleep(delay)
               else:
                   raise

   # Simulate flaky service
   attempt_count = 0

   def flaky_operation():
       global attempt_count
       attempt_count += 1
       if attempt_count < 3:
           raise ConnectionError("Service unavailable")
       return {"status": "success"}

   result = retry_with_backoff(flaky_operation)
   print(f"Result: {result}")
   ```

2. Run the demo:

   ```bash
   python retry_demo.py
   ```

**Observation:** The operation succeeds after retries with increasing delays.

### Exercise 3: Combine caching and retry

1. Create combined resilient client:

   ```python
   # resilient_demo.py
   import os
   from gds_vault import VaultClient

   # Simple cache from Exercise 1
   class SecretCache:
       def __init__(self, ttl=60):
           self._cache = {}
           self._ttl = ttl
           import time
           self._time = time

       def get(self, key):
           entry = self._cache.get(key)
           if entry and self._time.time() < entry["expires"]:
               return entry["value"]
           return None

       def set(self, key, value):
           self._cache[key] = {
               "value": value,
               "expires": self._time.time() + self._ttl
           }

   # Resilient client
   class ResilientClient:
       def __init__(self, vault_client, cache_ttl=60, max_retries=3):
           self._client = vault_client
           self._cache = SecretCache(cache_ttl)
           self._max_retries = max_retries

       def get_secret(self, path):
           # Check cache
           cached = self._cache.get(path)
           if cached:
               print(f"[CACHE] Returning cached value for {path}")
               return cached

           # Fetch with retry
           for attempt in range(self._max_retries):
               try:
                   print(f"[VAULT] Fetching {path} (attempt {attempt + 1})")
                   secret = self._client.get_secret(path)
                   self._cache.set(path, secret)
                   return secret
               except Exception as e:
                   if attempt < self._max_retries - 1:
                       print(f"[RETRY] Failed: {e}")
                       import time
                       time.sleep(2 ** attempt)
                   else:
                       raise

   # Test
   os.environ["VAULT_ADDR"] = "http://127.0.0.1:8200"
   os.environ["VAULT_TOKEN"] = "root"

   with VaultClient() as client:
       resilient = ResilientClient(client, cache_ttl=30, max_retries=3)

       # First call - fetches from Vault
       print("\n--- First call ---")
       secret = resilient.get_secret("secret/data/myapp/config")
       print(f"Result: {secret['data']}")

       # Second call - uses cache
       print("\n--- Second call ---")
       secret = resilient.get_secret("secret/data/myapp/config")
       print(f"Result: {secret['data']}")

       # Third call - uses cache
       print("\n--- Third call ---")
       secret = resilient.get_secret("secret/data/myapp/config")
       print(f"Result: {secret['data']}")
   ```

2. Run the demo:

   ```bash
   python resilient_demo.py
   ```

**Observation:** Only the first call hits Vault; subsequent calls use the cache.

### Cleanup

```bash
docker stop vault-resilience && docker rm vault-resilience
rm -f cache_demo.py retry_demo.py resilient_demo.py
```

---

## Key takeaways

1. **Cache aggressively** - Most secrets don't change frequently
2. **Respect lease duration** - For dynamic secrets, cache based on TTL
3. **Use exponential backoff** - Prevents thundering herd on recovery
4. **Add jitter to delays** - Spreads out retry attempts
5. **Implement circuit breaker** - Fail fast when Vault is down
6. **Classify errors** - Not all errors should be retried
7. **Fall back to stale cache** - Better than failing completely

---

[← Previous: Authentication Patterns](./17-authentication-patterns.md) | [Back to Track A: Python Integration](./README.md)

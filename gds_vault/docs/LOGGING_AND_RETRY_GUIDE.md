# Logging and Retry Logic Guide

## Overview

The `gds_vault` package now includes production-ready logging and automatic retry logic with exponential backoff for enhanced resilience and debuggability.

## Table of Contents

1. [Logging](#logging)
2. [Retry Logic with Exponential Backoff](#retry-logic-with-exponential-backoff)
3. [Configuration Examples](#configuration-examples)
4. [Production Best Practices](#production-best-practices)

---

## Logging

### What is Logging?

Logging allows you to track what your application is doing, which is essential for:
- **Debugging**: Understand why something went wrong
- **Monitoring**: Track application health in production
- **Auditing**: Keep records of operations for compliance
- **Performance**: Identify bottlenecks and slow operations

### Log Levels

The package uses Python's standard logging library with these levels:

| Level | When to Use | Example |
|-------|-------------|---------|
| `DEBUG` | Detailed diagnostic information | "Token will be refreshed at 1234567890" |
| `INFO` | General informational messages | "Authenticating with Vault at https://vault.example.com" |
| `WARNING` | Retry attempts and recoverable issues | "authenticate attempt 1 failed: Connection timeout. Retrying in 1.0s..." |
| `ERROR` | Serious problems that need attention | "Failed to fetch secret secret/data/app1 (status 404): path not found" |

### What Gets Logged?

#### Authentication Operations
```
INFO: Authenticating with Vault at https://vault.example.com
INFO: Successfully authenticated with Vault. Token valid for 3600s
DEBUG: Token will be refreshed at 1698765432
```

#### Secret Retrieval
```
INFO: Fetching secret from Vault: secret/data/myapp
DEBUG: Requesting specific version: 3
DEBUG: Successfully fetched KV v2 secret: secret/data/myapp
DEBUG: Cached secret: secret/data/myapp:v3
```

#### Cache Operations
```
DEBUG: Cache hit for secret: secret/data/myapp
INFO: Cleared cache (removed 5 secrets)
```

#### Errors
```
ERROR: Network error connecting to Vault: Connection timeout
ERROR: Failed to fetch secret secret/data/app1 (status 404): path not found
```

#### Retry Attempts
```
WARNING: authenticate attempt 1 failed: Connection timeout. Retrying in 1.0s...
WARNING: authenticate attempt 2 failed: Connection timeout. Retrying in 2.0s...
INFO: Successfully authenticated with Vault. Token valid for 3600s
```

### Configuring Logging

#### Basic Setup (Console Output)

```python
import logging
from gds_vault import VaultClient

# Configure logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Use VaultClient - all operations will be logged
client = VaultClient()
secret = client.get_secret('secret/data/myapp')
```

**Output:**
```
2025-10-03 10:15:23 - gds_vault.vault - INFO - Authenticating with Vault at https://vault.example.com
2025-10-03 10:15:24 - gds_vault.vault - INFO - Successfully authenticated with Vault. Token valid for 3600s
2025-10-03 10:15:24 - gds_vault.vault - INFO - Fetching secret from Vault: secret/data/myapp
2025-10-03 10:15:24 - gds_vault.vault - DEBUG - Successfully fetched KV v2 secret: secret/data/myapp
```

#### Production Setup (File Output with Rotation)

```python
import logging
from logging.handlers import RotatingFileHandler
from gds_vault import VaultClient

# Create logger
logger = logging.getLogger('gds_vault.vault')
logger.setLevel(logging.INFO)

# File handler with rotation (10MB max, keep 5 backups)
handler = RotatingFileHandler(
    '/var/log/myapp/vault.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# Use VaultClient - all operations logged to file
client = VaultClient()
secret = client.get_secret('secret/data/myapp')
```

#### Debug Mode (Verbose Logging)

```python
import logging
from gds_vault import VaultClient

# Enable DEBUG level for detailed diagnostics
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

client = VaultClient()
secret = client.get_secret('secret/data/myapp')
```

**Output includes cache details:**
```
2025-10-03 10:15:24 - gds_vault.vault - DEBUG - Token will be refreshed at 1698765432
2025-10-03 10:15:24 - gds_vault.vault - DEBUG - Successfully fetched KV v2 secret: secret/data/myapp
2025-10-03 10:15:24 - gds_vault.vault - DEBUG - Cached secret: secret/data/myapp
```

#### JSON Logging (for Log Aggregation Systems)

```python
import logging
import json
from gds_vault import VaultClient

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
        }
        return json.dumps(log_data)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())

logger = logging.getLogger('gds_vault.vault')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

client = VaultClient()
secret = client.get_secret('secret/data/myapp')
```

**Output:**
```json
{"timestamp": "2025-10-03 10:15:23", "level": "INFO", "logger": "gds_vault.vault", "message": "Authenticating with Vault at https://vault.example.com", "module": "vault", "function": "authenticate"}
```

---

## Retry Logic with Exponential Backoff

### What is Retry Logic?

Retry logic automatically retries failed operations, which is essential for handling:
- Temporary network glitches
- Server overload (rate limiting)
- Brief service outages
- Transient errors

**Without retry logic:** One transient failure = your application crashes
**With retry logic:** Transient failures are automatically recovered

### What is Exponential Backoff?

Exponential backoff increases the delay between retries exponentially:

```
Attempt 1: Fails → Wait 1 second
Attempt 2: Fails → Wait 2 seconds (2^1)
Attempt 3: Fails → Wait 4 seconds (2^2)
Attempt 4: Fails → Wait 8 seconds (2^3)
Attempt 5: Success! ✅
```

#### Why Exponential?

1. **Gives services time to recover** - A server under load needs breathing room
2. **Prevents overwhelming struggling services** - Linear retries can make problems worse
3. **Reduces "thundering herd"** - Prevents all clients from retrying simultaneously
4. **Industry standard** - Used by AWS, Google Cloud, Azure, and all major cloud providers

### Default Retry Configuration

All network operations in `gds_vault` use the following defaults:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `max_retries` | 3 | Maximum number of retry attempts |
| `initial_delay` | 1.0s | Initial delay before first retry |
| `max_delay` | 32.0s | Maximum delay between retries |
| `backoff_factor` | 2.0 | Exponential multiplier |
| `retriable_exceptions` | `requests.RequestException` | Network errors only |

### Operations with Automatic Retry

All these operations automatically retry on network failures:

1. **Authentication** (`authenticate()`)
2. **Secret retrieval** (`get_secret()`)
3. **Secret listing** (`list_secrets()`)
4. **Functional API** (`get_secret_from_vault()`)

### Retry Behavior Example

#### Scenario: Network is temporarily down

```python
from gds_vault import VaultClient
import logging

logging.basicConfig(level=logging.WARNING)

client = VaultClient()
secret = client.get_secret('secret/data/myapp')
```

**Logs show automatic recovery:**
```
WARNING: get_secret attempt 1 failed: Connection timeout. Retrying in 1.0s...
WARNING: get_secret attempt 2 failed: Connection timeout. Retrying in 2.0s...
INFO: Fetching secret from Vault: secret/data/myapp
INFO: Successfully fetched KV v2 secret: secret/data/myapp
```

**Result:** Operation succeeds after 2 retries, total delay = 3 seconds

#### Scenario: Vault server rate limiting (429 errors)

```
WARNING: authenticate attempt 1 failed: 429 Too Many Requests. Retrying in 1.0s...
WARNING: authenticate attempt 2 failed: 429 Too Many Requests. Retrying in 2.0s...
INFO: Successfully authenticated with Vault. Token valid for 3600s
```

**Result:** Exponential backoff gives the server time to recover

### What Errors Trigger Retry?

Only **retriable network errors** trigger retry:

✅ **Retried automatically:**
- Connection timeout
- Connection refused
- Network unreachable
- DNS resolution failures
- SSL/TLS handshake errors
- HTTP 429 (Rate Limit)
- HTTP 5xx (Server Errors)

❌ **Not retried (fail immediately):**
- HTTP 404 (Not Found) - secret doesn't exist
- HTTP 403 (Forbidden) - permission denied
- HTTP 400 (Bad Request) - invalid input
- Invalid secret path format
- Missing environment variables

### Customizing Retry Behavior

The retry decorator is configurable. Here's how to customize:

#### Example: More aggressive retries

```python
from gds_vault.vault import retry_with_backoff
import requests

@retry_with_backoff(
    max_retries=5,           # Try 5 times instead of 3
    initial_delay=0.5,       # Start with 0.5s delay
    max_delay=60.0,          # Allow up to 60s between retries
    backoff_factor=2.0       # Double the delay each time
)
def my_vault_operation():
    # Your custom Vault operation
    response = requests.get('https://vault.example.com/v1/secret/data/myapp')
    return response.json()
```

#### Example: Custom retriable exceptions

```python
@retry_with_backoff(
    max_retries=3,
    retriable_exceptions=(
        requests.RequestException,
        ConnectionError,
        TimeoutError
    )
)
def fetch_data():
    # This will retry on any of the specified exceptions
    pass
```

### Calculating Total Retry Time

With default settings (3 retries, initial_delay=1s, backoff_factor=2):

```
Attempt 1: Immediate
Attempt 2: Wait 1s  → Total: 1s
Attempt 3: Wait 2s  → Total: 3s
Attempt 4: Wait 4s  → Total: 7s
```

**Maximum total time:** ~7 seconds (plus actual operation time)

---

## Configuration Examples

### Example 1: Development Environment

```python
import logging
from gds_vault import VaultClient

# Simple console logging with INFO level
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

client = VaultClient()
secret = client.get_secret('secret/data/dev-app')
print(f"Retrieved {len(secret)} keys")
```

### Example 2: Production Environment with File Logging

```python
import logging
from logging.handlers import RotatingFileHandler
from gds_vault import VaultClient

# Configure root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Console handler (errors only)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_formatter = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_formatter)

# File handler (all INFO and above)
file_handler = RotatingFileHandler(
    '/var/log/myapp/vault.log',
    maxBytes=10*1024*1024,
    backupCount=5
)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(file_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Use VaultClient
with VaultClient() as client:
    secret1 = client.get_secret('secret/data/app1')
    secret2 = client.get_secret('secret/data/app2')
    secret3 = client.get_secret('secret/data/app3')
```

### Example 3: Kubernetes/Cloud with JSON Logging

```python
import logging
import json
import sys
from gds_vault import VaultClient

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': self.formatTime(record, '%Y-%m-%dT%H:%M:%S'),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_entry)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())

logger = logging.getLogger('gds_vault')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Use VaultClient
client = VaultClient()
secret = client.get_secret('secret/data/myapp')
```

### Example 4: Debug Mode for Troubleshooting

```python
import logging
from gds_vault import VaultClient

# Enable DEBUG logging for gds_vault only
logging.basicConfig(
    level=logging.WARNING  # Other libraries stay at WARNING
)
vault_logger = logging.getLogger('gds_vault.vault')
vault_logger.setLevel(logging.DEBUG)

# Now you'll see all debug messages
client = VaultClient()
print(f"Cache info before: {client.get_cache_info()}")

secret = client.get_secret('secret/data/myapp')
print(f"Cache info after: {client.get_cache_info()}")

# Fetch again (should hit cache)
secret = client.get_secret('secret/data/myapp')
```

**Output:**
```
INFO: Authenticating with Vault at https://vault.example.com
INFO: Successfully authenticated with Vault. Token valid for 3600s
DEBUG: Token will be refreshed at 1698765432
Cache info before: {'has_token': True, 'token_valid': True, 'cached_secrets_count': 0, 'cached_secret_paths': []}
INFO: Fetching secret from Vault: secret/data/myapp
DEBUG: Successfully fetched KV v2 secret: secret/data/myapp
DEBUG: Cached secret: secret/data/myapp
Cache info after: {'has_token': True, 'token_valid': True, 'cached_secrets_count': 1, 'cached_secret_paths': ['secret/data/myapp']}
DEBUG: Cache hit for secret: secret/data/myapp
```

---

## Production Best Practices

### 1. Log Levels by Environment

| Environment | Recommended Level | Rationale |
|-------------|------------------|-----------|
| Development | `DEBUG` | See all operations for debugging |
| Staging | `INFO` | Track operations without noise |
| Production | `INFO` or `WARNING` | Balance observability vs. volume |
| Troubleshooting | `DEBUG` | Temporarily enable for investigation |

### 2. Log Rotation

Always use log rotation in production to prevent disk space issues:

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    '/var/log/myapp/vault.log',
    maxBytes=10*1024*1024,  # 10MB per file
    backupCount=5            # Keep 5 backup files
)
```

This creates: `vault.log`, `vault.log.1`, `vault.log.2`, etc.

### 3. Structured Logging (JSON)

Use JSON format for easy parsing by log aggregation tools (Splunk, ELK, CloudWatch):

```python
import json
import logging

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
        })

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.getLogger('gds_vault').addHandler(handler)
```

### 4. Sensitive Data Protection

**Never log sensitive data like tokens or secret values!**

The package already follows this practice:
- ✅ Logs operation success/failure
- ✅ Logs secret paths
- ❌ Never logs token values
- ❌ Never logs secret contents

### 5. Monitoring Retry Patterns

Watch for excessive retry warnings in production:

```python
# If you see many of these, investigate root cause:
WARNING: authenticate attempt 1 failed: Connection timeout. Retrying in 1.0s...
WARNING: authenticate attempt 2 failed: Connection timeout. Retrying in 2.0s...
```

Possible causes:
- Network issues between app and Vault
- Vault server overload
- Firewall/routing problems
- DNS resolution issues

### 6. Alerting on Failures

Set up alerts for persistent failures:

```python
# After 3 retries, operation fails with ERROR log:
ERROR: authenticate failed after 3 retries: Connection timeout
```

Configure your monitoring system (e.g., CloudWatch, Datadog) to alert on:
- Multiple ERROR logs within a time window
- Specific error patterns (e.g., "failed after 3 retries")
- High retry attempt frequency

### 7. Log Sampling (High-Volume Applications)

For applications making thousands of Vault requests, consider log sampling:

```python
import logging
import random

class SamplingFilter(logging.Filter):
    def __init__(self, rate=0.1):
        super().__init__()
        self.rate = rate  # 10% sampling

    def filter(self, record):
        # Always log warnings and errors
        if record.levelno >= logging.WARNING:
            return True
        # Sample INFO and DEBUG
        return random.random() < self.rate

logger = logging.getLogger('gds_vault.vault')
logger.addFilter(SamplingFilter(rate=0.1))  # Log 10% of INFO/DEBUG
```

### 8. Context Manager for Clean Logging

Use context managers to group related operations:

```python
import logging
from gds_vault import VaultClient

logging.basicConfig(level=logging.INFO)

with VaultClient() as client:
    # All operations logged with automatic cleanup
    secret1 = client.get_secret('secret/data/app1')
    secret2 = client.get_secret('secret/data/app2')
    secret3 = client.get_secret('secret/data/app3')
# Cache cleared and logged on exit
```

**Logs:**
```
DEBUG: Entering VaultClient context manager
INFO: Authenticating with Vault at https://vault.example.com
INFO: Successfully authenticated with Vault. Token valid for 3600s
INFO: Fetching secret from Vault: secret/data/app1
INFO: Fetching secret from Vault: secret/data/app2
INFO: Fetching secret from Vault: secret/data/app3
DEBUG: Exiting VaultClient context manager
INFO: Cleared cache (removed 3 secrets)
```

---

## Summary

### Logging Benefits
✅ **Observability** - Know what's happening in production
✅ **Debugging** - Quickly identify issues
✅ **Auditing** - Track all Vault operations
✅ **Performance** - Identify slow operations and cache hits

### Retry Logic Benefits
✅ **Resilience** - Automatically recover from transient failures
✅ **Reliability** - Reduce false positives from network glitches
✅ **Production-ready** - Handle real-world network conditions
✅ **Rate limit handling** - Work with Vault's rate limiting

### Quick Start

```python
import logging
from gds_vault import VaultClient

# Enable logging
logging.basicConfig(level=logging.INFO)

# Use VaultClient - automatic retry and logging built-in
client = VaultClient()
secret = client.get_secret('secret/data/myapp')

# That's it! Retry and logging work automatically.
```

---

## Additional Resources

- **Python Logging Documentation**: https://docs.python.org/3/library/logging.html
- **Retry Patterns**: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
- **HashiCorp Vault**: https://www.vaultproject.io/docs
- **Package Documentation**: See `README.md` for basic usage

---

**Version:** 0.1.0
**Last Updated:** October 3, 2025

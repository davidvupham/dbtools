# Track A project: Secrets-enabled Python service

**[← Back to Track A: Python Integration](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-4_Applied-blue)
![Project](https://img.shields.io/badge/Project-Track_A-purple)

## Project overview

Build a production-ready Python service that integrates with HashiCorp Vault for secrets management using the `gds_vault` library.

### Scenario

You are developing a backend service that needs to:
- Connect to a PostgreSQL database using dynamic credentials
- Store and retrieve API keys from Vault
- Handle authentication securely in different environments
- Remain resilient when Vault is temporarily unavailable

### Learning outcomes

By completing this project, you will demonstrate:
- Proper use of the gds_vault library
- Environment-based authentication configuration
- Client-side caching implementation
- Retry and error handling patterns
- Secure credential management

---

## Requirements

### Functional requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Service authenticates to Vault using AppRole in production | Must |
| FR-2 | Service retrieves database credentials from Vault | Must |
| FR-3 | Service caches secrets with configurable TTL | Must |
| FR-4 | Service retries failed Vault operations with backoff | Must |
| FR-5 | Service falls back to cached secrets when Vault unavailable | Should |
| FR-6 | Service supports token auth for development | Should |
| FR-7 | Service logs Vault operations (without exposing secrets) | Should |

### Non-functional requirements

| ID | Requirement | Criteria |
|----|-------------|----------|
| NFR-1 | Code follows Python coding standards | Passes ruff lint |
| NFR-2 | Unit tests cover core functionality | >80% coverage |
| NFR-3 | No secrets in source code | No hardcoded credentials |
| NFR-4 | Configuration via environment variables | 12-factor compliant |

---

## Project structure

```
project-track-a/
├── src/
│   └── secrets_service/
│       ├── __init__.py
│       ├── config.py          # Configuration management
│       ├── vault_client.py    # Vault client wrapper
│       ├── cache.py           # Caching implementation
│       ├── retry.py           # Retry logic
│       └── service.py         # Main service
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_vault_client.py
│   ├── test_cache.py
│   └── test_retry.py
├── docker-compose.yml         # Local development environment
├── pyproject.toml             # Project configuration
├── README.md                  # Project documentation
└── .env.example               # Example environment variables
```

---

## Implementation guide

### Phase 1: Configuration module

Create `config.py` to manage environment-based configuration:

```python
# src/secrets_service/config.py
from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class VaultConfig:
    """Vault connection configuration."""
    addr: str
    auth_method: str  # "token" or "approle"
    token: Optional[str] = None
    role_id: Optional[str] = None
    secret_id: Optional[str] = None
    namespace: Optional[str] = None
    cache_ttl_seconds: int = 300
    retry_max_attempts: int = 3

    @classmethod
    def from_environment(cls) -> "VaultConfig":
        """Load configuration from environment variables."""
        # Implement this method
        pass
```

**Requirements:**
- Load all values from environment variables
- Support both token and AppRole authentication
- Provide sensible defaults
- Validate required fields based on auth method

### Phase 2: Caching implementation

Create `cache.py` with TTL-based caching:

```python
# src/secrets_service/cache.py
from typing import Any, Optional


class SecretCache:
    """Thread-safe secret cache with TTL expiration."""

    def __init__(self, default_ttl_seconds: int = 300):
        # Implement initialization
        pass

    def get(self, key: str) -> Optional[Any]:
        """Get a cached value if not expired."""
        pass

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Store a value with TTL."""
        pass

    def delete(self, key: str) -> None:
        """Remove a cached value."""
        pass
```

**Requirements:**
- Thread-safe operations
- TTL-based expiration
- Support per-key TTL override

### Phase 3: Retry logic

Create `retry.py` with exponential backoff:

```python
# src/secrets_service/retry.py
from typing import Callable, TypeVar

T = TypeVar("T")


def retry_with_backoff(
    func: Callable[[], T],
    max_attempts: int = 3,
    initial_delay: float = 0.5,
) -> T:
    """Execute a function with retry and exponential backoff."""
    pass
```

**Requirements:**
- Exponential backoff between retries
- Random jitter to prevent thundering herd
- Configurable max attempts and initial delay

### Phase 4: Vault client wrapper

Create `vault_client.py` combining all components:

```python
# src/secrets_service/vault_client.py
from typing import Optional, Any
from gds_vault import VaultClient
from .config import VaultConfig
from .cache import SecretCache


class ResilientVaultClient:
    """Production-ready Vault client with caching and retry."""

    def __init__(self, config: VaultConfig):
        # Implement initialization
        pass

    def get_secret(self, path: str, bypass_cache: bool = False) -> dict[str, Any]:
        """Get a secret with caching and retry."""
        pass

    def get_database_credentials(self, role: str) -> dict[str, str]:
        """Get dynamic database credentials."""
        pass

    def close(self) -> None:
        """Close the client."""
        pass
```

**Requirements:**
- Use gds_vault for Vault communication
- Integrate caching from Phase 2
- Integrate retry from Phase 3
- Support both static and dynamic secrets

### Phase 5: Main service

Create `service.py` demonstrating the complete integration:

```python
# src/secrets_service/service.py
import logging
from .config import VaultConfig
from .vault_client import ResilientVaultClient

logger = logging.getLogger(__name__)


class SecretsService:
    """Example service using Vault for secrets."""

    def __init__(self):
        config = VaultConfig.from_environment()
        self._vault = ResilientVaultClient(config)

    def get_database_connection_string(self) -> str:
        """Get database connection string with dynamic credentials."""
        pass

    def get_api_key(self, service_name: str) -> str:
        """Get an API key for an external service."""
        pass
```

---

## Testing requirements

### Unit tests

Create tests for each module:

```python
# tests/test_cache.py
import pytest
from secrets_service.cache import SecretCache


def test_cache_set_and_get():
    """Test basic cache operations."""
    cache = SecretCache(default_ttl_seconds=60)
    cache.set("key", {"value": "test"})
    assert cache.get("key") == {"value": "test"}


def test_cache_expiration():
    """Test that cached values expire."""
    # Implement test
    pass


def test_cache_thread_safety():
    """Test concurrent cache access."""
    # Implement test
    pass
```

### Integration tests

Test against a real Vault dev server:

```python
# tests/test_integration.py
import pytest
from secrets_service.vault_client import ResilientVaultClient
from secrets_service.config import VaultConfig


@pytest.fixture
def vault_config():
    """Provide test Vault configuration."""
    return VaultConfig(
        addr="http://127.0.0.1:8200",
        auth_method="token",
        token="root",
        cache_ttl_seconds=60,
    )


def test_get_secret(vault_config):
    """Test retrieving a secret from Vault."""
    client = ResilientVaultClient(vault_config)
    # Implement test
    pass
```

---

## Evaluation rubric

| Criteria | Points | Description |
|----------|--------|-------------|
| **Configuration (15)** | | |
| Environment loading | 5 | Correctly loads from environment |
| Auth method support | 5 | Supports both token and AppRole |
| Validation | 5 | Validates required fields |
| **Caching (20)** | | |
| TTL expiration | 8 | Values expire correctly |
| Thread safety | 7 | Safe concurrent access |
| Per-key TTL | 5 | Supports TTL override |
| **Retry Logic (20)** | | |
| Exponential backoff | 8 | Delays increase exponentially |
| Jitter | 5 | Random jitter applied |
| Max attempts | 7 | Respects attempt limit |
| **Vault Client (25)** | | |
| gds_vault integration | 10 | Correctly uses library |
| Caching integration | 8 | Uses cache appropriately |
| Error handling | 7 | Handles failures gracefully |
| **Testing (10)** | | |
| Unit test coverage | 5 | >80% coverage |
| Integration tests | 5 | Tests against Vault |
| **Code Quality (10)** | | |
| Linting | 5 | Passes ruff |
| Documentation | 5 | Clear docstrings and README |

**Total: 100 points**

### Grading scale

| Score | Grade |
|-------|-------|
| 90-100 | Excellent |
| 80-89 | Good |
| 70-79 | Satisfactory |
| <70 | Needs Improvement |

---

## Deliverables

Submit the following:

- [ ] Complete source code in `src/secrets_service/`
- [ ] Unit tests in `tests/`
- [ ] `docker-compose.yml` for local development
- [ ] `README.md` with setup instructions
- [ ] `.env.example` with required environment variables

---

## Getting started

1. Set up local environment:

   ```bash
   # Start Vault dev server
   docker run -d --name vault-dev \
       -p 8200:8200 \
       -e 'VAULT_DEV_ROOT_TOKEN_ID=root' \
       hashicorp/vault:1.15

   # Configure test secrets
   export VAULT_ADDR='http://127.0.0.1:8200'
   export VAULT_TOKEN='root'

   vault secrets enable -path=secret kv-v2
   vault kv put secret/myapp/config db_host="localhost" db_name="mydb"
   vault kv put secret/myapp/api-keys stripe="sk_test_xxx" sendgrid="SG.xxx"
   ```

2. Create project structure:

   ```bash
   mkdir -p project-track-a/src/secrets_service project-track-a/tests
   cd project-track-a
   ```

3. Initialize Python project:

   ```bash
   # Create pyproject.toml
   cat > pyproject.toml <<EOF
   [project]
   name = "secrets-service"
   version = "0.1.0"
   requires-python = ">=3.9"
   dependencies = [
       "gds-vault",
   ]

   [project.optional-dependencies]
   dev = [
       "pytest",
       "pytest-cov",
       "ruff",
   ]
   EOF
   ```

4. Start implementing!

---

## Tips for success

1. **Start with configuration** - Get environment loading working first
2. **Test incrementally** - Write tests as you implement each module
3. **Use type hints** - They help catch errors early
4. **Don't expose secrets** - Never log or print secret values
5. **Handle edge cases** - What if Vault is down? What if secret doesn't exist?

---

[← Back to Track A: Python Integration](./README.md)

# Authentication patterns

**[← Back to Track A: Python Integration](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-4_Applied-blue)
![Lesson](https://img.shields.io/badge/Lesson-17-purple)

## Learning objectives

By the end of this lesson, you will be able to:

- Implement token-based authentication in Python applications
- Configure AppRole authentication for production workloads
- Use environment-based configuration for flexible deployments
- Handle authentication failures and token renewal gracefully

## Table of contents

- [Authentication overview](#authentication-overview)
- [Token authentication](#token-authentication)
- [AppRole authentication](#approle-authentication)
- [Environment-based configuration](#environment-based-configuration)
- [Token lifecycle management](#token-lifecycle-management)
- [Hands-on lab](#hands-on-lab)
- [Key takeaways](#key-takeaways)

---

## Authentication overview

Python applications can authenticate to Vault using various methods. Choosing the right method depends on your deployment environment and security requirements.

### Authentication method comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Python Authentication Decision Tree                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                         ┌─────────────────┐                                 │
│                         │ Where is your   │                                 │
│                         │ app running?    │                                 │
│                         └────────┬────────┘                                 │
│                                  │                                          │
│              ┌───────────────────┼───────────────────┐                     │
│              │                   │                   │                     │
│              ▼                   ▼                   ▼                     │
│     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐               │
│     │ Kubernetes  │     │    Cloud    │     │   Other     │               │
│     │             │     │ (AWS/GCP/   │     │ (VMs, bare  │               │
│     │             │     │  Azure)     │     │  metal)     │               │
│     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘               │
│            │                   │                   │                       │
│            ▼                   ▼                   ▼                       │
│     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐               │
│     │ Kubernetes  │     │  Cloud IAM  │     │   AppRole   │               │
│     │    Auth     │     │    Auth     │     │             │               │
│     └─────────────┘     └─────────────┘     └─────────────┘               │
│                                                                              │
│   Development: Token auth is acceptable for local testing                   │
│   Production: Always use platform-native auth methods                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### gds_vault authentication support

The `gds_vault` library supports multiple authentication methods:

| Method | Configuration | Use Case |
|--------|--------------|----------|
| Token | `VAULT_TOKEN` | Development, short-lived operations |
| AppRole | `VAULT_ROLE_ID` + `VAULT_SECRET_ID` | Production applications |
| Kubernetes | Auto-detected in K8s | Kubernetes workloads |

[↑ Back to Table of Contents](#table-of-contents)

---

## Token authentication

Token authentication is the simplest method, suitable for development and testing.

### Basic token authentication

```python
from gds_vault import VaultClient

# Direct token configuration
with VaultClient(
    vault_addr="http://127.0.0.1:8200",
    token="hvs.xxxxxxxxxxxxx"
) as client:
    secret = client.get_secret("secret/data/myapp/config")
    print(secret["data"]["username"])
```

### Using environment variables

```python
import os
from gds_vault import VaultClient

# Set environment variables
os.environ["VAULT_ADDR"] = "http://127.0.0.1:8200"
os.environ["VAULT_TOKEN"] = "hvs.xxxxxxxxxxxxx"

# Client reads from environment automatically
with VaultClient() as client:
    secret = client.get_secret("secret/data/myapp/config")
```

### Token authentication wrapper

```python
from gds_vault import VaultClient
from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class VaultConfig:
    """Configuration for Vault connection."""
    addr: str
    token: Optional[str] = None
    namespace: Optional[str] = None

    @classmethod
    def from_environment(cls) -> "VaultConfig":
        """Create config from environment variables."""
        return cls(
            addr=os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200"),
            token=os.environ.get("VAULT_TOKEN"),
            namespace=os.environ.get("VAULT_NAMESPACE"),
        )


def get_vault_client(config: Optional[VaultConfig] = None) -> VaultClient:
    """Create a Vault client with the given configuration."""
    if config is None:
        config = VaultConfig.from_environment()

    return VaultClient(
        vault_addr=config.addr,
        token=config.token,
        namespace=config.namespace,
    )


# Usage
config = VaultConfig.from_environment()
with get_vault_client(config) as client:
    secret = client.get_secret("secret/data/myapp/config")
```

### Security considerations for tokens

```python
# NEVER do this - token in code
client = VaultClient(token="hvs.actual-token-value")  # BAD!

# NEVER log tokens
import logging
logging.info(f"Using token: {token}")  # BAD!

# DO this - load from secure source
import os
token = os.environ.get("VAULT_TOKEN")
if not token:
    raise ValueError("VAULT_TOKEN environment variable required")
```

[↑ Back to Table of Contents](#table-of-contents)

---

## AppRole authentication

AppRole is the recommended method for production applications.

### AppRole workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AppRole Authentication Flow                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   1. Deployment               2. Runtime                3. Operations        │
│   ┌─────────────────┐        ┌─────────────────┐       ┌─────────────────┐  │
│   │ CI/CD injects   │        │ App presents    │       │ App uses token  │  │
│   │ Role ID +       │ ─────▶ │ credentials to  │ ────▶ │ to access       │  │
│   │ Secret ID       │        │ Vault           │       │ secrets         │  │
│   └─────────────────┘        └─────────────────┘       └─────────────────┘  │
│                                      │                                       │
│                                      ▼                                       │
│                              ┌─────────────────┐                            │
│                              │ Vault validates │                            │
│                              │ and returns     │                            │
│                              │ client token    │                            │
│                              └─────────────────┘                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Basic AppRole authentication

```python
import os
from gds_vault import VaultClient


def authenticate_with_approle() -> VaultClient:
    """Authenticate using AppRole credentials."""
    vault_addr = os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200")
    role_id = os.environ["VAULT_ROLE_ID"]
    secret_id = os.environ["VAULT_SECRET_ID"]

    client = VaultClient(
        vault_addr=vault_addr,
        role_id=role_id,
        secret_id=secret_id,
    )
    return client


# Usage
with authenticate_with_approle() as client:
    secret = client.get_secret("secret/data/myapp/config")
    print(f"Database host: {secret['data']['db_host']}")
```

### AppRole with custom login path

```python
from gds_vault import VaultClient
import os


class AppRoleAuth:
    """AppRole authentication handler."""

    def __init__(
        self,
        vault_addr: str,
        role_id: str,
        secret_id: str,
        mount_path: str = "approle",
    ):
        self.vault_addr = vault_addr
        self.role_id = role_id
        self.secret_id = secret_id
        self.mount_path = mount_path
        self._client: VaultClient | None = None

    def get_client(self) -> VaultClient:
        """Get or create an authenticated Vault client."""
        if self._client is None:
            self._client = VaultClient(
                vault_addr=self.vault_addr,
                role_id=self.role_id,
                secret_id=self.secret_id,
                auth_mount_path=self.mount_path,
            )
        return self._client

    def close(self) -> None:
        """Close the client connection."""
        if self._client:
            self._client.close()
            self._client = None


# Usage
auth = AppRoleAuth(
    vault_addr=os.environ["VAULT_ADDR"],
    role_id=os.environ["VAULT_ROLE_ID"],
    secret_id=os.environ["VAULT_SECRET_ID"],
    mount_path="approle",  # Custom mount path if needed
)

try:
    client = auth.get_client()
    secret = client.get_secret("secret/data/myapp/config")
finally:
    auth.close()
```

### Secure Secret ID delivery

```python
import os
import requests
from typing import Optional


def get_secret_id_from_wrapped_token(
    vault_addr: str,
    wrapped_token: str,
) -> str:
    """
    Unwrap a response-wrapped Secret ID.

    This is the secure way to deliver Secret IDs:
    1. Orchestrator wraps the Secret ID
    2. Application receives wrapped token
    3. Application unwraps to get actual Secret ID
    """
    response = requests.post(
        f"{vault_addr}/v1/sys/wrapping/unwrap",
        headers={"X-Vault-Token": wrapped_token},
    )
    response.raise_for_status()
    return response.json()["data"]["secret_id"]


def authenticate_with_wrapped_secret_id(
    vault_addr: str,
    role_id: str,
    wrapped_token: str,
) -> VaultClient:
    """Authenticate using a wrapped Secret ID."""
    # Unwrap the Secret ID
    secret_id = get_secret_id_from_wrapped_token(vault_addr, wrapped_token)

    # Authenticate with unwrapped credentials
    return VaultClient(
        vault_addr=vault_addr,
        role_id=role_id,
        secret_id=secret_id,
    )


# Usage in deployment script
wrapped_token = os.environ.get("VAULT_WRAPPED_SECRET_ID")
if wrapped_token:
    client = authenticate_with_wrapped_secret_id(
        vault_addr=os.environ["VAULT_ADDR"],
        role_id=os.environ["VAULT_ROLE_ID"],
        wrapped_token=wrapped_token,
    )
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Environment-based configuration

Configure authentication dynamically based on the deployment environment.

### Multi-environment configuration

```python
import os
from enum import Enum
from dataclasses import dataclass
from typing import Optional
from gds_vault import VaultClient


class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class VaultSettings:
    """Vault configuration settings."""
    addr: str
    auth_method: str
    token: Optional[str] = None
    role_id: Optional[str] = None
    secret_id: Optional[str] = None
    namespace: Optional[str] = None

    @classmethod
    def from_environment(cls) -> "VaultSettings":
        """Load settings from environment variables."""
        env = os.environ.get("ENVIRONMENT", "development")
        auth_method = os.environ.get("VAULT_AUTH_METHOD", "token")

        return cls(
            addr=os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200"),
            auth_method=auth_method,
            token=os.environ.get("VAULT_TOKEN"),
            role_id=os.environ.get("VAULT_ROLE_ID"),
            secret_id=os.environ.get("VAULT_SECRET_ID"),
            namespace=os.environ.get("VAULT_NAMESPACE"),
        )


def create_vault_client(settings: VaultSettings) -> VaultClient:
    """Create a Vault client based on settings."""
    if settings.auth_method == "token":
        if not settings.token:
            raise ValueError("VAULT_TOKEN required for token auth")
        return VaultClient(
            vault_addr=settings.addr,
            token=settings.token,
            namespace=settings.namespace,
        )

    elif settings.auth_method == "approle":
        if not settings.role_id or not settings.secret_id:
            raise ValueError("VAULT_ROLE_ID and VAULT_SECRET_ID required")
        return VaultClient(
            vault_addr=settings.addr,
            role_id=settings.role_id,
            secret_id=settings.secret_id,
            namespace=settings.namespace,
        )

    else:
        raise ValueError(f"Unsupported auth method: {settings.auth_method}")


# Usage
settings = VaultSettings.from_environment()
with create_vault_client(settings) as client:
    secret = client.get_secret("secret/data/myapp/config")
```

### YAML configuration file

```yaml
# config/vault.yaml
development:
  vault_addr: "http://127.0.0.1:8200"
  auth_method: "token"
  secret_path_prefix: "secret/data/dev"

staging:
  vault_addr: "https://vault.staging.example.com:8200"
  auth_method: "approle"
  secret_path_prefix: "secret/data/staging"

production:
  vault_addr: "https://vault.example.com:8200"
  auth_method: "approle"
  namespace: "production"
  secret_path_prefix: "secret/data/prod"
```

```python
import os
import yaml
from pathlib import Path
from gds_vault import VaultClient


def load_vault_config(env: str, config_path: str = "config/vault.yaml") -> dict:
    """Load Vault configuration for the specified environment."""
    with open(config_path) as f:
        config = yaml.safe_load(f)

    if env not in config:
        raise ValueError(f"No configuration for environment: {env}")

    return config[env]


def create_client_from_config(config: dict) -> VaultClient:
    """Create Vault client from configuration dictionary."""
    auth_method = config.get("auth_method", "token")

    if auth_method == "token":
        return VaultClient(
            vault_addr=config["vault_addr"],
            token=os.environ["VAULT_TOKEN"],
            namespace=config.get("namespace"),
        )
    elif auth_method == "approle":
        return VaultClient(
            vault_addr=config["vault_addr"],
            role_id=os.environ["VAULT_ROLE_ID"],
            secret_id=os.environ["VAULT_SECRET_ID"],
            namespace=config.get("namespace"),
        )


# Usage
env = os.environ.get("ENVIRONMENT", "development")
config = load_vault_config(env)

with create_client_from_config(config) as client:
    path = f"{config['secret_path_prefix']}/myapp/config"
    secret = client.get_secret(path)
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Token lifecycle management

Handle token expiration and renewal for long-running applications.

### Token renewal strategy

```python
import threading
import time
from typing import Callable, Optional
from gds_vault import VaultClient


class TokenRenewalManager:
    """Manages automatic token renewal for long-running applications."""

    def __init__(
        self,
        client: VaultClient,
        renewal_interval_seconds: int = 300,  # 5 minutes
        on_renewal_failure: Optional[Callable[[Exception], None]] = None,
    ):
        self.client = client
        self.renewal_interval = renewal_interval_seconds
        self.on_failure = on_renewal_failure
        self._stop_event = threading.Event()
        self._renewal_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the background token renewal thread."""
        if self._renewal_thread is not None:
            return

        self._stop_event.clear()
        self._renewal_thread = threading.Thread(
            target=self._renewal_loop,
            daemon=True,
        )
        self._renewal_thread.start()

    def stop(self) -> None:
        """Stop the background token renewal thread."""
        self._stop_event.set()
        if self._renewal_thread:
            self._renewal_thread.join(timeout=5)
            self._renewal_thread = None

    def _renewal_loop(self) -> None:
        """Background loop that renews the token periodically."""
        while not self._stop_event.is_set():
            try:
                self.client.renew_token()
            except Exception as e:
                if self.on_failure:
                    self.on_failure(e)

            self._stop_event.wait(self.renewal_interval)


# Usage
def handle_renewal_failure(error: Exception) -> None:
    """Handle token renewal failures."""
    print(f"Token renewal failed: {error}")
    # Could trigger re-authentication or alerting


client = VaultClient(
    vault_addr="http://127.0.0.1:8200",
    role_id=os.environ["VAULT_ROLE_ID"],
    secret_id=os.environ["VAULT_SECRET_ID"],
)

renewal_manager = TokenRenewalManager(
    client=client,
    renewal_interval_seconds=300,
    on_renewal_failure=handle_renewal_failure,
)

try:
    renewal_manager.start()

    # Application runs...
    while True:
        secret = client.get_secret("secret/data/myapp/config")
        time.sleep(60)

finally:
    renewal_manager.stop()
    client.close()
```

### Re-authentication on failure

```python
import logging
from typing import TypeVar, Callable
from functools import wraps
from gds_vault import VaultClient

T = TypeVar("T")
logger = logging.getLogger(__name__)


class VaultAuthenticationError(Exception):
    """Raised when Vault authentication fails."""
    pass


def with_reauth(
    create_client: Callable[[], VaultClient],
    max_retries: int = 3,
):
    """
    Decorator that re-authenticates on authentication failures.

    Usage:
        @with_reauth(create_client=my_client_factory)
        def get_database_password(client: VaultClient) -> str:
            return client.get_secret("secret/data/db")["password"]
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            client = kwargs.get("client") or create_client()
            retries = 0

            while retries < max_retries:
                try:
                    kwargs["client"] = client
                    return func(*args, **kwargs)
                except Exception as e:
                    if "permission denied" in str(e).lower():
                        retries += 1
                        logger.warning(
                            f"Auth failure, re-authenticating (attempt {retries}/{max_retries})"
                        )
                        client = create_client()
                    else:
                        raise

            raise VaultAuthenticationError(
                f"Failed to authenticate after {max_retries} attempts"
            )

        return wrapper
    return decorator


# Usage
def create_client() -> VaultClient:
    return VaultClient(
        vault_addr=os.environ["VAULT_ADDR"],
        role_id=os.environ["VAULT_ROLE_ID"],
        secret_id=os.environ["VAULT_SECRET_ID"],
    )


@with_reauth(create_client=create_client)
def get_database_config(client: VaultClient) -> dict:
    """Get database configuration with automatic re-authentication."""
    return client.get_secret("secret/data/myapp/database")
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Hands-on lab

### Prerequisites

- Python 3.9+
- gds_vault library installed
- Vault dev server running

### Setup

```bash
# Start Vault dev server
docker run -d --name vault-python-auth \
    -p 8200:8200 \
    -e 'VAULT_DEV_ROOT_TOKEN_ID=root' \
    hashicorp/vault:1.15

export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'

# Create test secrets
vault secrets enable -path=secret kv-v2
vault kv put secret/myapp/config \
    db_host="postgres.example.com" \
    db_user="myapp" \
    db_pass="secret123"
```

### Exercise 1: Token authentication

1. Create a simple token auth script:

   ```python
   # token_auth.py
   import os
   from gds_vault import VaultClient

   os.environ["VAULT_ADDR"] = "http://127.0.0.1:8200"
   os.environ["VAULT_TOKEN"] = "root"

   with VaultClient() as client:
       secret = client.get_secret("secret/data/myapp/config")
       print(f"Database: {secret['data']['db_host']}")
       print(f"Username: {secret['data']['db_user']}")
   ```

2. Run the script:

   ```bash
   python token_auth.py
   ```

**Observation:** The script authenticates using the token and retrieves the secret.

### Exercise 2: Set up AppRole authentication

1. Configure AppRole in Vault:

   ```bash
   # Create policy
   vault policy write myapp-policy - <<EOF
   path "secret/data/myapp/*" {
     capabilities = ["read"]
   }
   EOF

   # Enable AppRole
   vault auth enable approle

   # Create role
   vault write auth/approle/role/myapp \
       token_policies="myapp-policy" \
       token_ttl=1h \
       token_max_ttl=4h

   # Get credentials
   export ROLE_ID=$(vault read -field=role_id auth/approle/role/myapp/role-id)
   export SECRET_ID=$(vault write -f -field=secret_id auth/approle/role/myapp/secret-id)

   echo "Role ID: $ROLE_ID"
   echo "Secret ID: $SECRET_ID"
   ```

2. Create AppRole auth script:

   ```python
   # approle_auth.py
   import os
   from gds_vault import VaultClient

   vault_addr = os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200")
   role_id = os.environ["ROLE_ID"]
   secret_id = os.environ["SECRET_ID"]

   with VaultClient(
       vault_addr=vault_addr,
       role_id=role_id,
       secret_id=secret_id,
   ) as client:
       secret = client.get_secret("secret/data/myapp/config")
       print(f"Database: {secret['data']['db_host']}")
   ```

3. Run with AppRole credentials:

   ```bash
   python approle_auth.py
   ```

**Observation:** AppRole authentication works without a static token.

### Exercise 3: Environment-based configuration

1. Create configuration module:

   ```python
   # vault_config.py
   import os
   from dataclasses import dataclass
   from typing import Optional
   from gds_vault import VaultClient


   @dataclass
   class VaultConfig:
       addr: str
       auth_method: str
       token: Optional[str] = None
       role_id: Optional[str] = None
       secret_id: Optional[str] = None

       @classmethod
       def from_env(cls) -> "VaultConfig":
           auth_method = os.environ.get("VAULT_AUTH_METHOD", "token")
           return cls(
               addr=os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200"),
               auth_method=auth_method,
               token=os.environ.get("VAULT_TOKEN"),
               role_id=os.environ.get("ROLE_ID"),
               secret_id=os.environ.get("SECRET_ID"),
           )


   def get_client(config: Optional[VaultConfig] = None) -> VaultClient:
       if config is None:
           config = VaultConfig.from_env()

       if config.auth_method == "token":
           return VaultClient(vault_addr=config.addr, token=config.token)
       elif config.auth_method == "approle":
           return VaultClient(
               vault_addr=config.addr,
               role_id=config.role_id,
               secret_id=config.secret_id,
           )
       raise ValueError(f"Unknown auth method: {config.auth_method}")


   if __name__ == "__main__":
       with get_client() as client:
           secret = client.get_secret("secret/data/myapp/config")
           print(f"Auth method: {VaultConfig.from_env().auth_method}")
           print(f"Database: {secret['data']['db_host']}")
   ```

2. Test with different auth methods:

   ```bash
   # Token auth
   VAULT_AUTH_METHOD=token VAULT_TOKEN=root python vault_config.py

   # AppRole auth
   VAULT_AUTH_METHOD=approle python vault_config.py
   ```

**Observation:** The same code works with different auth methods based on environment.

### Cleanup

```bash
docker stop vault-python-auth && docker rm vault-python-auth
rm -f token_auth.py approle_auth.py vault_config.py
```

---

## Key takeaways

1. **Use AppRole for production** - Token auth is only for development
2. **Environment-based config** - Make authentication method configurable
3. **Never hardcode credentials** - Always load from environment or secure storage
4. **Handle token expiration** - Implement renewal or re-authentication
5. **Secure Secret ID delivery** - Use response wrapping in production
6. **Log carefully** - Never log tokens or credentials
7. **Use context managers** - Ensure proper cleanup with `with` statements

---

[← Previous: gds_vault Library](./16-gds-vault-library.md) | [Back to Track A: Python Integration](./README.md) | [Next: Caching and Retry →](./18-caching-retry.md)

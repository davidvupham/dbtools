# gds_vault Library

**[← Back to Track A](./README.md)**

## Learning objectives

- Install and configure the gds_vault library
- Use VaultClient for secret retrieval
- Handle different authentication methods

## Installation

```bash
pip install gds_vault

# Or development install
cd python/gds_vault
pip install -e .
```

## Basic usage

```python
from gds_vault import VaultClient

# Simple usage with environment variables
with VaultClient() as vault:
    secret = vault.get_secret("secret/data/myapp/config")
    print(secret["password"])

# Explicit configuration
from gds_vault import VaultConfig

config = VaultConfig(
    addr="https://vault.example.com:8200",
    token="hvs.xxx",  # Or use other auth methods
)

with VaultClient(config) as vault:
    secret = vault.get_secret("database/creds/app")
```

## Configuration

### Environment variables

```bash
export VAULT_ADDR="https://vault.example.com:8200"
export VAULT_TOKEN="hvs.xxx"
# Or for AppRole
export VAULT_ROLE_ID="xxx"
export VAULT_SECRET_ID="yyy"
```

### Configuration file

```yaml
# vault.yaml
vault:
  addr: https://vault.example.com:8200
  auth:
    method: approle
    role_id: xxx
    secret_id_file: /run/secrets/vault-secret-id
```

## Key takeaways

1. Use context manager (`with`) for automatic cleanup
2. Configure via environment or config file
3. VaultClient handles auth and caching

---

[← Back to Track A](./README.md) | [Next: Authentication Patterns →](./17-authentication-patterns.md)

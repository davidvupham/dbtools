# Vault Mount Point - Quick Reference

## Environment Variable

```bash
export VAULT_MOUNT_POINT=kv-v2
```

## Basic Usage

```python
from gds_vault import VaultClient

# With parameter
client = VaultClient(mount_point='kv-v2')
secret = client.get_secret('data/myapp')  # Fetches kv-v2/data/myapp

# With environment variable
client = VaultClient()  # Uses VAULT_MOUNT_POINT
secret = client.get_secret('data/myapp')

# Convenience function
from gds_vault import get_secret_from_vault
secret = get_secret_from_vault('data/myapp', mount_point='kv-v2')
```

## Property Access

```python
client = VaultClient()

# Get current mount point
print(client.mount_point)  # None or value from env

# Set mount point
client.mount_point = 'kv-v2'

# Change mount point dynamically
client.mount_point = 'secret'
```

## Configuration

```python
# From config dict
config = {'mount_point': 'kv-v2', 'timeout': 15}
client = VaultClient.from_config(config)

# In configuration
all_config = client.get_all_config()
print(all_config['mount_point'])
```

## Smart Path Handling

```python
client = VaultClient(mount_point='kv-v2')

# All these work correctly (no duplication):
secret = client.get_secret('data/myapp')          # → kv-v2/data/myapp
secret = client.get_secret('kv-v2/data/myapp')    # → kv-v2/data/myapp
```

## Multi-Environment Pattern

```python
import os

ENV = os.getenv('ENV', 'dev')
MOUNT_POINTS = {
    'dev': 'secret',
    'staging': 'kv-v2',
    'production': 'kv-prod'
}

client = VaultClient(mount_point=MOUNT_POINTS[ENV])
```

## List Secrets

```python
client = VaultClient(mount_point='kv-v2')

# Lists secrets at kv-v2/metadata/myapp
secrets = client.list_secrets('metadata/myapp')
```

## Without Mount Point (Traditional)

```python
# Still works - full backward compatibility
client = VaultClient()
secret = client.get_secret('kv-v2/data/myapp')  # Full path
```

## Priority Order

1. Parameter: `VaultClient(mount_point='kv-v2')`
2. Environment: `VAULT_MOUNT_POINT=kv-v2`
3. Default: `None` (no mount point)

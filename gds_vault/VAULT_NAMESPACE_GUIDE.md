# Vault Namespace Support Guide

## Overview

As of this update, all `gds_vault` client implementations now support **Vault Enterprise namespaces** via the `X-Vault-Namespace` header. This is required for multi-tenant Vault Enterprise deployments where resources are isolated by namespace.

## What Changed

### Added Namespace Support To:
- ✅ `vault.py` - `VaultClient` class
- ✅ `vault.py` - `get_secret_from_vault()` function
- ✅ `client.py` - `VaultClient` class (modern OOP)
- ✅ `enhanced_vault.py` - `EnhancedVaultClient` class
- ✅ `auth.py` - `AppRoleAuth` strategy

### Why This Was Needed

When using Vault Enterprise with namespaces, **all API calls** (including AppRole authentication) must include the `X-Vault-Namespace` header. Without this header:
- Authentication returns **403 Forbidden**
- Secret retrieval fails even with valid tokens
- List operations fail

## Configuration

### Environment Variable (Recommended)

```bash
export VAULT_NAMESPACE="your_namespace"
```

All client implementations will automatically read from this environment variable.

### Programmatic Configuration

#### Simple Client (vault.py)

```python
from gds_vault.vault import VaultClient

# Via constructor parameter
client = VaultClient(
    vault_addr="https://vault.example.com:8200",
    namespace="your_namespace"
)

# Via standalone function
from gds_vault.vault import get_secret_from_vault

secret = get_secret_from_vault(
    secret_path="data/myapp",
    namespace="your_namespace"
)
```

#### Modern Client (client.py)

```python
from gds_vault import VaultClient

# Via constructor parameter
client = VaultClient(
    vault_addr="https://vault.example.com:8200",
    namespace="your_namespace"
)

# Or from environment
import os
os.environ["VAULT_NAMESPACE"] = "your_namespace"
client = VaultClient()  # Automatically picks up namespace
```

#### With Authentication Strategy

```python
from gds_vault import VaultClient, AppRoleAuth

# AppRoleAuth now supports namespace
auth = AppRoleAuth(
    role_id="your-role-id",
    secret_id="your-secret-id",
    namespace="your_namespace"
)

client = VaultClient(
    vault_addr="https://vault.example.com:8200",
    auth=auth
)
```

## Complete Example

### Using Environment Variables (.env file)

```bash
# Vault Configuration
VAULT_ADDR=https://vault.example.com:8200
VAULT_NAMESPACE=your_namespace
VAULT_SECRET_PATH=data/snowflake
VAULT_MOUNT_POINT=secret
VAULT_ROLE_ID=your_role_id
VAULT_SECRET_ID=your_secret_id
```

### Python Code

```python
from gds_vault import VaultClient

# All configuration from environment
with VaultClient() as client:
    # Namespace header automatically included in all requests
    secret = client.get_secret('secret/data/myapp')
    print(secret)
```

## Testing Namespace Configuration

Use the provided test script to verify namespace configuration:

```bash
./test_vault_approle_login.sh
```

This script tests multiple scenarios:
1. Basic authentication (no namespace)
2. With namespace header
3. Custom mount points
4. Full configuration (namespace + custom mount)

Look for **HTTP 200** responses to confirm success.

## Troubleshooting

### 403 Forbidden Errors

**Symptom:** Authentication or secret retrieval returns 403

**Cause:** Missing or incorrect namespace

**Solution:**
1. Verify `VAULT_NAMESPACE` is set correctly
2. Run the test script: `./test_vault_approle_login.sh`
3. Confirm your AppRole exists in the specified namespace
4. Check with Vault admin that your credentials are valid for that namespace

### Namespace Not Applied

**Symptom:** Code works without namespace but fails with namespace set

**Cause:** Using older version of gds_vault without namespace support

**Solution:**
- Ensure you have the latest version with namespace support
- All client implementations should now support the `namespace` parameter

## Technical Details

### How It Works

When a namespace is configured (via parameter or environment variable), the client adds the `X-Vault-Namespace` header to **all Vault API requests**:

```python
headers = {"X-Vault-Token": token}
if namespace:
    headers["X-Vault-Namespace"] = namespace
```

This applies to:
- AppRole authentication (`/v1/auth/approle/login`)
- Secret retrieval (`/v1/{path}`)
- List operations (`LIST /v1/{path}`)

### Backward Compatibility

✅ **Fully backward compatible**

- If `VAULT_NAMESPACE` is not set, behavior is unchanged
- Existing code continues to work without modification
- Namespace is optional and only applied when configured

## See Also

- `.env.example` - Example environment configuration
- `test_vault_approle_login.sh` - Namespace testing script
- `VAULT_APPROLE_403_TROUBLESHOOTING.md` - Troubleshooting guide
- Vault Enterprise documentation on namespaces

## Version History

- **2025-10-07**: Added namespace support to all client implementations
  - Added `namespace` parameter to all VaultClient classes
  - Added `X-Vault-Namespace` header to all API calls
  - Updated tests to verify namespace functionality
  - Added test script for namespace validation

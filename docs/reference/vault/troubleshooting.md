# Vault Troubleshooting Guide

**[← Back to Reference Index](./README.md)**

## Table of Contents

- [Common Errors](#common-errors)
- [Connection Issues](#connection-issues)
- [Authentication Issues](#authentication-issues)
- [Permission Issues](#permission-issues)
- [Cache Issues](#cache-issues)

## Common Errors

### "VAULT_ADDR is required"

**Cause:** Vault address not configured.

**Solution:**

```bash
export VAULT_ADDR="https://vault.example.com:8200"
```

Or provide in code:

```python
client = VaultClient(vault_addr="https://vault.example.com:8200")
```

### "AppRole credentials must be provided"

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

## Connection Issues

### "Failed to connect to Vault"

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

### "SSL: CERTIFICATE_VERIFY_FAILED"

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

## Authentication Issues

### "Vault AppRole login failed: permission denied"

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

### "token not valid"

**Causes:**
- Token expired
- Token revoked
- Token from different Vault cluster

**Solutions:**

1. Re-authenticate to get new token
2. Check token TTL and renewal
3. Verify using correct Vault cluster

## Permission Issues

### "permission denied" (403)

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

## Cache Issues

### Stale secrets after rotation

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

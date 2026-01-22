# Vault Troubleshooting Guide

**[← Back to Course Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Vault-blue)

> [!IMPORTANT]
> **Related Docs:** [Quick Reference](./quick-reference.md) | [Glossary](./glossary.md)

## Table of contents

- [Connection issues](#connection-issues)
- [Authentication issues](#authentication-issues)
- [Permission issues](#permission-issues)
- [Seal/unseal issues](#sealunseal-issues)
- [Secrets engine issues](#secrets-engine-issues)
- [Token issues](#token-issues)
- [Docker/container issues](#dockercontainer-issues)
- [Performance issues](#performance-issues)

---

## Connection issues

### Cannot connect to Vault server

**Symptoms:**
- `Error checking seal status: Get "http://127.0.0.1:8200/v1/sys/seal-status": dial tcp 127.0.0.1:8200: connect: connection refused`

**Solutions:**

1. **Verify Vault is running:**
   ```bash
   # Check if Vault process is running
   ps aux | grep vault

   # Check container status
   docker ps | grep vault
   ```

2. **Check VAULT_ADDR:**
   ```bash
   # Verify environment variable
   echo $VAULT_ADDR

   # Set if missing
   export VAULT_ADDR='http://127.0.0.1:8200'
   ```

3. **Check network connectivity:**
   ```bash
   # Test connection
   curl -s http://127.0.0.1:8200/v1/sys/health

   # Check if port is listening
   netstat -tlnp | grep 8200
   ```

4. **Check Vault logs:**
   ```bash
   # Docker
   docker logs vault-dev

   # Systemd
   journalctl -u vault
   ```

### TLS certificate errors

**Symptoms:**
- `x509: certificate signed by unknown authority`
- `tls: failed to verify certificate`

**Solutions:**

1. **For development (not production!):**
   ```bash
   export VAULT_SKIP_VERIFY=true
   ```

2. **Provide CA certificate:**
   ```bash
   export VAULT_CACERT=/path/to/ca-cert.pem
   ```

3. **For self-signed certificates:**
   ```bash
   # Add to system trust store (Linux)
   sudo cp ca-cert.pem /usr/local/share/ca-certificates/
   sudo update-ca-certificates
   ```

[↑ Back to Table of Contents](#table-of-contents)

---

## Authentication issues

### Permission denied

**Symptoms:**
- `Error making API request: permission denied`
- `403 Forbidden`

**Solutions:**

1. **Verify token is valid:**
   ```bash
   vault token lookup
   ```

2. **Check token policies:**
   ```bash
   vault token lookup -format=json | jq '.data.policies'
   ```

3. **Verify policy allows the operation:**
   ```bash
   vault token capabilities <path>
   # Example: vault token capabilities secret/data/myapp
   ```

4. **Re-authenticate:**
   ```bash
   vault login
   ```

### Token expired

**Symptoms:**
- `permission denied` after working previously
- `token has expired`

**Solutions:**

1. **Check token TTL:**
   ```bash
   vault token lookup -format=json | jq '.data.ttl'
   ```

2. **Renew token (if renewable):**
   ```bash
   vault token renew
   ```

3. **Re-authenticate:**
   ```bash
   # Token auth
   vault login <new-token>

   # Userpass auth
   vault login -method=userpass username=<user>

   # AppRole auth
   vault write auth/approle/login role_id=<role-id> secret_id=<secret-id>
   ```

### AppRole authentication fails

**Symptoms:**
- `invalid role or secret ID`
- `role_id or secret_id not found`

**Solutions:**

1. **Verify role exists:**
   ```bash
   vault read auth/approle/role/<role-name>
   ```

2. **Get fresh role ID:**
   ```bash
   vault read auth/approle/role/<role-name>/role-id
   ```

3. **Generate new secret ID:**
   ```bash
   vault write -f auth/approle/role/<role-name>/secret-id
   ```

4. **Check secret ID usage limits:**
   ```bash
   # Secret IDs may have usage limits
   vault read auth/approle/role/<role-name> | grep secret_id
   ```

[↑ Back to Table of Contents](#table-of-contents)

---

## Permission issues

### Policy not allowing access

**Symptoms:**
- `1 error occurred: * permission denied`
- Can't read/write secrets despite being authenticated

**Diagnosis:**

```bash
# Check what paths your token can access
vault token capabilities secret/data/myapp/config

# List your policies
vault token lookup -format=json | jq '.data.policies'

# Read a specific policy
vault policy read <policy-name>
```

**Common mistakes:**

1. **KV v2 path mismatch:**
   ```hcl
   # Wrong - won't work with KV v2
   path "secret/myapp/*" {
     capabilities = ["read"]
   }

   # Correct - KV v2 requires data/ in path
   path "secret/data/myapp/*" {
     capabilities = ["read"]
   }
   ```

2. **Missing list capability:**
   ```hcl
   # Need list to see available secrets
   path "secret/metadata/myapp/*" {
     capabilities = ["list"]
   }
   ```

3. **Glob pattern issues:**
   ```hcl
   # This won't match secret/data/myapp
   path "secret/data/myapp/*" { }

   # Need both patterns
   path "secret/data/myapp" { }
   path "secret/data/myapp/*" { }
   ```

**Solution:**

Update the policy:
```bash
vault policy write my-policy - <<EOF
# Full KV v2 access
path "secret/data/myapp/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
path "secret/metadata/myapp/*" {
  capabilities = ["list", "read", "delete"]
}
EOF
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Seal/unseal issues

### Vault is sealed

**Symptoms:**
- `Vault is sealed`
- `error: sealed`

**Solutions:**

1. **Check seal status:**
   ```bash
   vault status
   ```

2. **Unseal Vault:**
   ```bash
   # Need to run this 3 times (by default) with different keys
   vault operator unseal <unseal-key-1>
   vault operator unseal <unseal-key-2>
   vault operator unseal <unseal-key-3>
   ```

3. **For dev server (auto-unsealed):**
   ```bash
   # Restart dev server
   vault server -dev
   ```

### Lost unseal keys

**Symptoms:**
- Cannot unseal after restart
- No access to unseal keys

**Solutions:**

> [!WARNING]
> If you lose all unseal keys and the root token, the Vault data is unrecoverable.

1. **Check for backed-up keys:**
   - Initial keys from `vault operator init`
   - Stored in password manager
   - Distributed to key custodians

2. **For development/testing:**
   ```bash
   # Destroy and reinitialize (data loss!)
   rm -rf /path/to/vault/data
   vault operator init
   ```

3. **Prevention - use auto-unseal:**
   ```hcl
   # vault.hcl configuration
   seal "awskms" {
     kms_key_id = "alias/vault-unseal-key"
   }
   ```

[↑ Back to Table of Contents](#table-of-contents)

---

## Secrets engine issues

### Secrets engine not enabled

**Symptoms:**
- `no handler for route`
- `path is not authorized`

**Solutions:**

1. **List enabled engines:**
   ```bash
   vault secrets list
   ```

2. **Enable the engine:**
   ```bash
   # KV v2
   vault secrets enable -path=secret kv-v2

   # Database
   vault secrets enable database

   # Transit
   vault secrets enable transit
   ```

### Database connection errors

**Symptoms:**
- `error creating database object`
- `connection refused`

**Diagnosis:**

```bash
# Check database config
vault read database/config/<config-name>

# Test database connectivity (from Vault's perspective)
vault write database/rotate-root/<config-name>
```

**Common issues:**

1. **Network connectivity:**
   ```bash
   # Can Vault reach the database?
   docker exec vault-dev nc -zv postgres 5432
   ```

2. **Credentials:**
   ```bash
   # Verify connection URL
   vault read database/config/<config-name> -format=json | jq '.data.connection_details'
   ```

3. **SSL/TLS:**
   ```bash
   # Add sslmode if needed
   connection_url="postgresql://{{username}}:{{password}}@host:5432/db?sslmode=disable"
   ```

### KV version mismatch

**Symptoms:**
- `invalid path for a versioned K/V secrets engine`
- Different behavior than expected

**Solutions:**

1. **Check KV version:**
   ```bash
   vault secrets list -format=json | jq '.["secret/"]'
   # Look for "options.version"
   ```

2. **Use correct commands:**
   ```bash
   # KV v1
   vault kv put kv/myapp password=secret
   vault read kv/myapp

   # KV v2
   vault kv put secret/myapp password=secret
   vault kv get secret/myapp
   ```

[↑ Back to Table of Contents](#table-of-contents)

---

## Token issues

### Token not renewable

**Symptoms:**
- `lease is not renewable`

**Solutions:**

1. **Check if token is renewable:**
   ```bash
   vault token lookup -format=json | jq '.data.renewable'
   ```

2. **Create a renewable token:**
   ```bash
   vault token create -policy=my-policy -renewable=true
   ```

### Token hierarchy revocation

**Symptoms:**
- Token suddenly stops working
- Child tokens invalidated

**Explanation:**
When a parent token is revoked, all child tokens are also revoked.

**Solutions:**

1. **Create orphan token:**
   ```bash
   vault token create -orphan -policy=my-policy
   ```

2. **Use batch tokens for short-lived operations:**
   ```bash
   vault token create -type=batch -policy=my-policy
   ```

[↑ Back to Table of Contents](#table-of-contents)

---

## Docker/container issues

### Container won't start

**Symptoms:**
- Container exits immediately
- No logs

**Solutions:**

1. **Check for port conflicts:**
   ```bash
   lsof -i :8200
   ```

2. **Verify Docker network:**
   ```bash
   docker network ls
   docker network inspect vault-network
   ```

3. **Check volume permissions:**
   ```bash
   ls -la /path/to/vault/data
   # Should be writable by container user
   ```

### IPC_LOCK capability

**Symptoms:**
- `Error initializing: Failed to lock memory`
- Memory locking warnings

**Solutions:**

```yaml
# docker-compose.yml
services:
  vault:
    cap_add:
      - IPC_LOCK
```

Or disable mlock:
```hcl
# vault.hcl
disable_mlock = true
```

### Container networking

**Symptoms:**
- Services can't reach Vault
- `connection refused` from other containers

**Solutions:**

1. **Use Docker network:**
   ```yaml
   services:
     vault:
       networks:
         - vault-network
     app:
       networks:
         - vault-network
       environment:
         VAULT_ADDR: http://vault:8200
   ```

2. **Check DNS resolution:**
   ```bash
   docker exec app-container ping vault
   ```

[↑ Back to Table of Contents](#table-of-contents)

---

## Performance issues

### Slow responses

**Diagnosis:**

```bash
# Check Vault metrics
curl -s http://localhost:8200/v1/sys/metrics | jq
```

**Solutions:**

1. **Enable caching in clients**
2. **Use batch tokens for high-volume operations**
3. **Tune storage backend**
4. **Consider Vault Agent for secret caching**

### High memory usage

**Solutions:**

1. **Limit lease count:**
   ```bash
   vault write sys/quotas/rate-limit/global rate=100
   ```

2. **Reduce token TTLs:**
   ```bash
   vault write auth/approle/role/my-role token_ttl=1h token_max_ttl=4h
   ```

3. **Revoke unused leases:**
   ```bash
   vault lease revoke -prefix database/creds/
   ```

[↑ Back to Table of Contents](#table-of-contents)

---

## Getting more help

### Diagnostic commands

```bash
# Full status
vault status

# Check storage health
vault operator raft list-peers

# Debug info
vault debug

# Audit log analysis
cat /var/log/vault/audit.log | jq
```

### Community resources

- [HashiCorp Discuss](https://discuss.hashicorp.com/c/vault/)
- [Vault GitHub Issues](https://github.com/hashicorp/vault/issues)
- [Vault Documentation](https://developer.hashicorp.com/vault/docs)

---

[← Back to Course Index](./README.md)

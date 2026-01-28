# Vault CLI reference

**🔗 [← Back to Reference Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 27, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Vault-blue)

## Table of Contents

- [CLI Quick Reference](#cli-quick-reference)
  - [Authentication](#authentication)
  - [KV Secrets (v2)](#kv-secrets-v2)
  - [Policies](#policies)
  - [AppRole Management](#approle-management)
  - [Status and Health](#status-and-health)
- [Glossary](#glossary)
- [External Resources](#external-resources)

## CLI Quick Reference

### Authentication

```bash
# Login with token
vault login hvs.your-token

# Login with AppRole
vault write auth/approle/login \
    role_id="..." \
    secret_id="..."

# Check current token
vault token lookup
```

### KV Secrets (v2)

```bash
# Write secret
vault kv put secret/myapp password="secret123"

# Read secret
vault kv get secret/myapp

# Read specific version
vault kv get -version=2 secret/myapp

# List secrets
vault kv list secret/

# Delete secret (soft delete)
vault kv delete secret/myapp

# Undelete
vault kv undelete -versions=1 secret/myapp

# Permanently delete
vault kv destroy -versions=1 secret/myapp
```

### Policies

```bash
# List policies
vault policy list

# Read policy
vault policy read myapp-policy

# Write policy
vault policy write myapp-policy policy.hcl
```

### AppRole Management

```bash
# Enable AppRole
vault auth enable approle

# Create role
vault write auth/approle/role/myapp \
    token_policies="myapp-policy" \
    token_ttl=1h

# Get Role ID
vault read auth/approle/role/myapp/role-id

# Generate Secret ID
vault write -f auth/approle/role/myapp/secret-id
```

### Status and Health

```bash
# Server status
vault status

# Seal status
vault operator seal-status

# Health check
curl https://vault.example.com:8200/v1/sys/health
```

## Glossary

| Term | Definition |
|:---|:---|
| **AppRole** | Auth method for machine authentication using Role ID and Secret ID |
| **Auth Method** | Plugin that verifies client identity (AppRole, Token, LDAP, etc.) |
| **Barrier** | Encryption layer protecting all Vault data |
| **Capability** | Permission type (create, read, update, delete, list, deny) |
| **Dynamic Secret** | Credential generated on-demand with automatic expiration |
| **Lease** | Time-limited grant of access to a secret |
| **Mount** | Path where a secrets engine or auth method is enabled |
| **Namespace** | Isolated tenant within Vault (Enterprise feature) |
| **Policy** | Rules defining what paths a token can access |
| **Role ID** | Static identifier for an AppRole (like a username) |
| **Seal** | State where Vault cannot access encrypted data |
| **Secret ID** | Dynamic credential for AppRole (like a password) |
| **Secrets Engine** | Plugin that stores or generates secrets (KV, Database, etc.) |
| **Static Secret** | Long-lived secret stored in KV engine |
| **Token** | Primary authentication credential in Vault |
| **TTL** | Time-To-Live, duration before expiration |
| **Unseal** | Process of decrypting Vault's master key |

## External Resources

### Official HashiCorp Documentation

- [HashiCorp Vault Documentation](https://developer.hashicorp.com/vault/docs) - Comprehensive official docs
- [Vault API Reference](https://developer.hashicorp.com/vault/api-docs) - REST API documentation
- [Vault Tutorials](https://developer.hashicorp.com/vault/tutorials) - Hands-on tutorials
- [Production Hardening Guide](https://developer.hashicorp.com/vault/docs/concepts/production-hardening) - Security hardening

### Best Practices and Patterns

- [AppRole Best Practices](https://developer.hashicorp.com/vault/docs/auth/approle/approle-pattern) - Authentication patterns
- [Recommended Pattern for AppRole](https://developer.hashicorp.com/vault/tutorials/recommended-patterns/pattern-approle) - AppRole tutorial
- [Audit Logging Best Practices](https://developer.hashicorp.com/vault/docs/audit/best-practices) - Audit configuration
- [Recommended Patterns](https://developer.hashicorp.com/vault/docs/internals/recommended-patterns) - Architecture patterns
- [Programmatic Best Practices](https://developer.hashicorp.com/vault/docs/configuration/programmatic-best-practices) - Automation

### Secrets Engines

- [KV Secrets Engine v2](https://developer.hashicorp.com/vault/docs/secrets/kv/kv-v2) - KV engine reference
- [KV v2 API Reference](https://developer.hashicorp.com/vault/api-docs/secret/kv/kv-v2) - KV API docs
- [Store Versioned KV Secrets](https://developer.hashicorp.com/vault/tutorials/secrets-management/versioned-kv) - KV tutorial
- [Upgrading KV v1 to v2](https://support.hashicorp.com/hc/en-us/articles/44684220257555-Upgrading-Vault-KV-Secrets-Engine-from-Version-1-to-Version-2) - Migration guide

### Troubleshooting Resources

- [Troubleshoot Vault](https://developer.hashicorp.com/vault/tutorials/monitoring/troubleshooting-vault) - Troubleshooting guide
- [Query Audit Device Logs](https://developer.hashicorp.com/vault/tutorials/monitoring/query-audit-device-logs) - Audit analysis
- [Monitor and Understand Audit Logs](https://notes.kodekloud.com/docs/HashiCorp-Certified-Vault-Operations-Professional-2022/Monitor-a-Vault-Environment/Monitor-and-Understand-Audit-Logs) - KodeKloud guide

### Python and Caching

- [Vault Agent Caching](https://developer.hashicorp.com/vault/docs/agent-and-proxy/agent/caching) - Agent caching docs
- [Python Secrets Management Best Practices](https://blog.gitguardian.com/how-to-handle-secrets-in-python/) - GitGuardian guide
- [AWS Secrets Manager Python Caching](https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_cache-python.html) - Alternative caching pattern

### Package Documentation

- [gds_vault Developer's Guide](../../../python/gds_vault/docs/DEVELOPERS_GUIDE.md) - Complete API usage
- [gds_vault Beginner's Guide](../../../python/gds_vault/docs/BEGINNERS_GUIDE.md) - Python concepts explained
- [Rotation-Aware TTL Guide](../../../python/gds_vault/docs/ROTATION_AWARE_TTL_GUIDE.md) - Rotation-aware caching

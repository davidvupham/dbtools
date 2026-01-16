# Vault Concepts Guide

**[← Back to Vault Documentation Index](./README.md)** — Navigation guide for all Vault docs

> **Document Version:** 1.0
> **Last Updated:** January 15, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Vault Version](https://img.shields.io/badge/Vault-1.15%2B-blue)
![Document Status](https://img.shields.io/badge/Status-Production-green)

> [!IMPORTANT]
> **Related Docs:** [Architecture](./vault-architecture.md) | [Operations](../../how-to/vault/vault-operations-guide.md) | [Reference](../../reference/vault/vault-reference.md) | [gds_vault Guide](../../../python/gds_vault/docs/DEVELOPERS_GUIDE.md)

## Table of Contents

- [What is HashiCorp Vault?](#what-is-hashicorp-vault)
- [Why Use Vault?](#why-use-vault)
- [Core Concepts](#core-concepts)
  - [Secrets](#secrets)
  - [Secrets Engines](#secrets-engines)
  - [Authentication Methods](#authentication-methods)
  - [Policies](#policies)
  - [Tokens](#tokens)
  - [Leases and TTLs](#leases-and-ttls)
- [How Vault Works](#how-vault-works)
  - [Security Model](#security-model)
  - [Request Flow](#request-flow)
  - [Seal and Unseal](#seal-and-unseal)
- [Secrets Engines Deep Dive](#secrets-engines-deep-dive)
  - [KV Secrets Engine](#kv-secrets-engine)
  - [Database Secrets Engine](#database-secrets-engine)
  - [Active Directory Secrets Engine](#active-directory-secrets-engine)
- [Authentication Methods Deep Dive](#authentication-methods-deep-dive)
  - [AppRole](#approle)
  - [Token Auth](#token-auth)
  - [Other Methods](#other-methods)
- [Key Decisions to Make](#key-decisions-to-make)
- [Best Practices](#best-practices)
- [Next Steps](#next-steps)

## What is HashiCorp Vault?

**HashiCorp Vault is a secrets management and data protection platform** that provides a unified interface to store, access, and distribute secrets like API keys, passwords, certificates, and encryption keys.

Think of it as a **secure vault (safe) for your application secrets** with advanced access control, audit logging, and automatic secret rotation capabilities.

### The Problem Vault Solves

Without a secrets manager:
- Secrets hardcoded in application code or config files
- Passwords stored in version control history
- No audit trail of who accessed what secrets
- Manual, error-prone secret rotation
- Shared credentials across teams and environments
- No encryption at rest for sensitive data

With Vault:
- **Centralized** - Single source of truth for all secrets
- **Dynamic** - Generate short-lived credentials on demand
- **Encrypted** - All secrets encrypted at rest and in transit
- **Auditable** - Complete log of all secret access
- **Automated** - Automatic rotation and lease management
- **Access Controlled** - Fine-grained policies per application

[↑ Back to Table of Contents](#table-of-contents)

## Why Use Vault?

| Benefit | Description |
|:---|:---|
| **Centralized Secrets Management** | Store all secrets in one secure location instead of scattered across configs |
| **Dynamic Secrets** | Generate short-lived credentials on demand, reducing exposure risk |
| **Encryption as a Service** | Encrypt data without managing encryption keys directly |
| **Identity-Based Access** | Applications authenticate to get only the secrets they need |
| **Comprehensive Audit** | Every secret access is logged for compliance and security |
| **Automatic Rotation** | Rotate secrets automatically without application changes |
| **Multi-Cloud Support** | Works across AWS, Azure, GCP, and on-premises |

### Vault vs. Alternatives

| Feature | Vault | Environment Variables | Config Files | Cloud KMS |
|:---|:---:|:---:|:---:|:---:|
| Centralized Management | Yes | No | No | Partial |
| Dynamic Secrets | Yes | No | No | No |
| Fine-Grained ACLs | Yes | No | No | Yes |
| Audit Logging | Yes | No | No | Yes |
| Secret Rotation | Yes | Manual | Manual | Partial |
| Multi-Cloud | Yes | N/A | N/A | No |

[↑ Back to Table of Contents](#table-of-contents)

## Core Concepts

### Secrets

A **secret** is any sensitive data you want to control access to:

- Database credentials (username/password)
- API keys and tokens
- TLS certificates and private keys
- SSH keys
- Encryption keys
- Service account credentials

**In Vault, secrets are stored at paths:**

```
secret/data/myapp/database     → Database credentials
secret/data/myapp/api-keys     → API keys
secret/data/shared/certificates → TLS certificates
```

### Secrets Engines

A **Secrets Engine** is a component that stores, generates, or encrypts secrets. Each engine is mounted at a path and provides specific functionality.

**Think of it as:** Different types of safes in your vault, each designed for a specific purpose.

| Engine | Purpose | Example Use Case |
|:---|:---|:---|
| **KV (Key-Value)** | Store static secrets | API keys, passwords, configs |
| **Database** | Generate dynamic database credentials | PostgreSQL, MySQL, MongoDB |
| **Active Directory** | Manage/rotate AD passwords | Service account rotation |
| **PKI** | Generate TLS certificates | Internal CA, mTLS |
| **Transit** | Encryption as a service | Encrypt data without storing keys |
| **AWS/Azure/GCP** | Generate cloud credentials | Dynamic IAM credentials |

**Mounting Example:**

```bash
# Enable KV v2 at path "secret"
vault secrets enable -path=secret kv-v2

# Enable database engine at path "database"
vault secrets enable -path=database database
```

### Authentication Methods

**Auth Methods** verify the identity of users or applications before granting access to secrets.

**Think of it as:** The front door security check - proving who you are before entering the vault.

| Method | Best For | How It Works |
|:---|:---|:---|
| **AppRole** | Applications/Services | Role ID + Secret ID (like username + password) |
| **Token** | Direct access | Pre-existing Vault token |
| **Kubernetes** | K8s workloads | Service account JWT validation |
| **LDAP/AD** | Human users | Directory authentication |
| **AWS/Azure/GCP** | Cloud workloads | Cloud IAM identity validation |
| **OIDC** | SSO integration | OpenID Connect tokens |

### Policies

**Policies** define what secrets a token can access and what operations it can perform.

**Think of it as:** The permission slip that says which safes you can open and what you can do with the contents.

**Policy Example:**

```hcl
# Allow read access to database secrets
path "secret/data/myapp/database" {
  capabilities = ["read"]
}

# Allow list access to see what secrets exist
path "secret/metadata/myapp/*" {
  capabilities = ["list"]
}

# Deny access to admin secrets
path "secret/data/admin/*" {
  capabilities = ["deny"]
}
```

**Capabilities:**
- `create` - Create new secrets
- `read` - Read existing secrets
- `update` - Modify existing secrets
- `delete` - Delete secrets
- `list` - List secret paths
- `deny` - Explicitly deny access

### Tokens

A **Token** is the primary authentication mechanism in Vault. After authenticating, you receive a token that grants access based on attached policies.

**Think of it as:** Your access badge after passing security - it determines where you can go.

**Token Properties:**
- **TTL (Time-To-Live)** - How long the token is valid
- **Policies** - What the token can access
- **Renewable** - Whether the TTL can be extended
- **Orphan** - Whether it has a parent token

**Token Types:**

| Type | Persistence | Use Case |
|:---|:---|:---|
| **Service Token** | Stored in Vault | Long-running applications |
| **Batch Token** | Not stored | Short-lived, high-volume operations |

### Leases and TTLs

A **Lease** is a time-limited grant of access to a secret. When the lease expires, the secret may be revoked or rotated.

**Think of it as:** A library loan - you have the book for a limited time, then it must be returned.

**Key Concepts:**

- **TTL (Time-To-Live)** - Initial validity period
- **Max TTL** - Maximum possible extension
- **Renewal** - Extending the lease before expiration
- **Revocation** - Invalidating the secret before expiration

**Why Leases Matter:**

```python
# Without leases - static credentials forever
password = "super_secret_123"  # Never changes, high risk if leaked

# With leases - dynamic, short-lived credentials
creds = vault_client.get_secret("database/creds/myapp")
# creds valid for 1 hour, then automatically rotated
```

[↑ Back to Table of Contents](#table-of-contents)

## How Vault Works

### Security Model

Vault's security model is based on **defense in depth**:

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT REQUEST                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  1. AUTHENTICATION                                          │
│     - Verify identity (AppRole, Token, etc.)                │
│     - Generate or validate token                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  2. AUTHORIZATION                                           │
│     - Check token's attached policies                       │
│     - Verify path and capability permissions                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  3. AUDIT                                                   │
│     - Log request details (who, what, when)                 │
│     - Must succeed before proceeding                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  4. SECRETS ENGINE                                          │
│     - Process request (read, write, generate)               │
│     - Return secret data                                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  5. STORAGE                                                 │
│     - All data encrypted with barrier key                   │
│     - Written to storage backend                            │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow

When your application requests a secret:

1. **Application authenticates** with Vault (e.g., AppRole)
2. **Vault validates identity** and returns a token
3. **Application requests secret** using the token
4. **Vault checks policies** attached to the token
5. **Audit device logs** the request
6. **Secrets engine** retrieves or generates the secret
7. **Secret returned** to the application

### Seal and Unseal

Vault starts in a **sealed** state where it cannot access any secrets. Unsealing requires a quorum of key shares.

**Why Sealing?**

- **Protection at rest** - Even with storage access, secrets are encrypted
- **Key splitting** - No single person can unseal alone (Shamir's Secret Sharing)
- **Emergency lockdown** - Seal Vault instantly if compromised

**Unseal Process:**

```
┌─────────────────────────────────────────────────────────────┐
│                    SEALED VAULT                             │
│     - Cannot read/write secrets                             │
│     - Master key encrypted                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │  Provide key shares (3 of 5)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   UNSEALED VAULT                            │
│     - Master key reconstructed in memory                    │
│     - Can process requests                                  │
│     - Key never written to disk                             │
└─────────────────────────────────────────────────────────────┘
```

**Auto-Unseal:**

Production deployments typically use **auto-unseal** with a cloud KMS:
- AWS KMS
- Azure Key Vault
- Google Cloud KMS
- HashiCorp Vault (another instance)

[↑ Back to Table of Contents](#table-of-contents)

## Secrets Engines Deep Dive

### KV Secrets Engine

The **Key-Value (KV) Secrets Engine** stores arbitrary secrets as key-value pairs.

**Versions:**
- **KV v1** - Simple storage, no versioning
- **KV v2** - Versioning, soft deletes, metadata (recommended)

**KV v2 Features:**

| Feature | Description |
|:---|:---|
| **Versioning** | Keep history of secret changes (default: 10 versions) |
| **Soft Delete** | Mark as deleted but recoverable |
| **Metadata** | Store custom metadata with secrets |
| **Check-and-Set** | Prevent blind overwrites |

**Path Structure (KV v2):**

```
secret/                    ← Mount point
├── data/                  ← Read/write secret data
│   └── myapp/database     ← Actual secret
├── metadata/              ← Secret metadata
│   └── myapp/database     ← Metadata for secret
└── delete/                ← Soft delete operations
```

**Example:**

```bash
# Write a secret
vault kv put secret/myapp/database username="app" password="secret123"

# Read a secret
vault kv get secret/myapp/database

# Get specific version
vault kv get -version=2 secret/myapp/database

# List secrets
vault kv list secret/myapp/
```

### Database Secrets Engine

The **Database Secrets Engine** generates dynamic, short-lived database credentials.

**How It Works:**

1. Configure Vault with database admin credentials
2. Define roles with SQL statements for user creation
3. Applications request credentials from Vault
4. Vault creates a new database user with limited TTL
5. Credentials automatically revoked when lease expires

**Supported Databases:**
- PostgreSQL
- MySQL/MariaDB
- MongoDB
- Microsoft SQL Server
- Oracle
- And many more...

**Example Configuration:**

```bash
# Configure PostgreSQL connection
vault write database/config/mydb \
    plugin_name=postgresql-database-plugin \
    connection_url="postgresql://{{username}}:{{password}}@db.example.com:5432/mydb" \
    allowed_roles="readonly" \
    username="vault_admin" \
    password="admin_password"

# Create a role
vault write database/roles/readonly \
    db_name=mydb \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
    default_ttl="1h" \
    max_ttl="24h"

# Get credentials
vault read database/creds/readonly
```

### Active Directory Secrets Engine

The **AD Secrets Engine** manages and rotates Active Directory service account passwords.

**Use Cases:**
- Rotate service account passwords automatically
- Retrieve current passwords for applications
- Audit all password access

**Key Concept - Lazy Rotation:**

Passwords are NOT rotated immediately at TTL expiration. Instead, rotation occurs on the **next credential request** after TTL expires.

See [How-to: Rotate AD Passwords](../../how-to/vault/rotate-ad-passwords.md) for detailed configuration.

[↑ Back to Table of Contents](#table-of-contents)

## Authentication Methods Deep Dive

### AppRole

**AppRole** is the recommended authentication method for applications and services.

**How It Works:**

```
┌─────────────────────────────────────────────────────────────┐
│  1. SETUP (One-time by admin)                               │
│     - Create AppRole with policies                          │
│     - Generate Role ID (like username)                      │
│     - Generate Secret ID (like password)                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  2. AUTHENTICATION (At runtime)                             │
│     - Application sends Role ID + Secret ID                 │
│     - Vault validates and returns token                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  3. ACCESS SECRETS                                          │
│     - Use token to read secrets                             │
│     - Token has policies attached                           │
└─────────────────────────────────────────────────────────────┘
```

**Best Practices:**

| Practice | Reason |
|:---|:---|
| **Separate delivery channels** | Role ID and Secret ID should come from different sources |
| **Short Secret ID TTL** | Limit exposure window if Secret ID is compromised |
| **Use CIDR binding** | Restrict which IPs can use the AppRole |
| **Response wrapping** | Deliver Secret ID wrapped for single-use |

**Configuration Example:**

```bash
# Enable AppRole
vault auth enable approle

# Create role
vault write auth/approle/role/myapp \
    token_policies="myapp-policy" \
    token_ttl=1h \
    token_max_ttl=4h \
    secret_id_ttl=10m \
    secret_id_num_uses=1

# Get Role ID
vault read auth/approle/role/myapp/role-id

# Generate Secret ID
vault write -f auth/approle/role/myapp/secret-id
```

### Token Auth

**Token Authentication** uses an existing Vault token directly.

**Use Cases:**
- Development and testing
- CI/CD pipelines with pre-generated tokens
- Service accounts with long-lived tokens

**Token Creation:**

```bash
# Create a token with specific policies
vault token create -policy=myapp-policy -ttl=24h

# Create an orphan token (no parent)
vault token create -policy=myapp-policy -orphan

# Create a periodic token (renewable indefinitely)
vault token create -policy=myapp-policy -period=24h
```

### Other Methods

| Method | Use Case | How It Works |
|:---|:---|:---|
| **Kubernetes** | K8s pods | JWT from service account |
| **AWS IAM** | EC2/Lambda | AWS STS credentials |
| **Azure** | Azure VMs | Managed identity |
| **LDAP** | Human users | Directory authentication |
| **OIDC** | SSO | OpenID Connect flow |

[↑ Back to Table of Contents](#table-of-contents)

## Key Decisions to Make

### 1. Which Secrets Engine?

| Scenario | Recommended Engine |
|:---|:---|
| Static secrets (API keys, passwords) | KV v2 |
| Database credentials | Database (dynamic) |
| Active Directory accounts | AD Secrets Engine |
| TLS certificates | PKI |
| Encryption without storing keys | Transit |

### 2. Which Auth Method?

| Scenario | Recommended Method |
|:---|:---|
| Applications/Services | AppRole |
| Kubernetes workloads | Kubernetes |
| AWS workloads | AWS IAM |
| Human users | LDAP/OIDC |
| CI/CD pipelines | AppRole or Token |
| Development | Token |

### 3. Static vs. Dynamic Secrets?

| Approach | Pros | Cons |
|:---|:---|:---|
| **Static (KV)** | Simple, familiar | Long-lived, manual rotation |
| **Dynamic** | Short-lived, auto-revoked | More complex setup |

**Recommendation:** Use dynamic secrets when possible, especially for databases.

### 4. Caching Strategy?

| Strategy | When to Use |
|:---|:---|
| **No caching** | Secrets change frequently, low latency to Vault |
| **TTL-based** | Balance between freshness and performance |
| **Rotation-aware** | Secrets have known rotation schedules |

See [Operations Guide - Caching](../../how-to/vault/vault-operations-guide.md#caching-strategies) for implementation details.

[↑ Back to Table of Contents](#table-of-contents)

## Best Practices

### Security Best Practices

1. **Use Dynamic Secrets** - Generate short-lived credentials instead of static passwords
2. **Implement Least Privilege** - Grant only the minimum required permissions
3. **Enable Audit Logging** - Log all secret access for compliance
4. **Rotate Secrets Regularly** - Even static secrets should be rotated
5. **Never Store Root Tokens** - Revoke root tokens after initial setup
6. **Use TLS Everywhere** - Encrypt all communication with Vault

### Application Best Practices

1. **Cache Appropriately** - Don't hit Vault for every request
2. **Handle Lease Renewal** - Renew tokens before expiration
3. **Implement Retry Logic** - Network failures happen
4. **Use Specific Exceptions** - Handle different errors differently
5. **Log (Not Secrets)** - Log operations but never secret values

### Operational Best Practices

1. **Deploy Multiple Nodes** - High availability prevents outages
2. **Backup Regularly** - Use Vault's snapshot functionality
3. **Monitor Health** - Set up alerts for Vault health
4. **Test DR Procedures** - Regularly test disaster recovery
5. **Document Policies** - Keep policy documentation up to date

[↑ Back to Table of Contents](#table-of-contents)

## Next Steps

Now that you understand the core concepts, proceed to:

1. **[Vault Architecture Guide](./vault-architecture.md)** - Learn about deployment and security
2. **[Vault Operations Guide](../../how-to/vault/vault-operations-guide.md)** - Hands-on usage with gds_vault
3. **[Vault Reference](../../reference/vault/vault-reference.md)** - API reference and troubleshooting

**Quick Start with gds_vault:**

```python
from gds_vault import VaultClient

# Authenticate and get a secret
with VaultClient() as client:
    secret = client.get_secret("secret/data/myapp")
    password = secret["password"]
```

[↑ Back to Table of Contents](#table-of-contents)

## Related Documentation

- **[Vault Architecture Guide](./vault-architecture.md)** - Deployment, security, and production hardening
- **[Vault Operations Guide](../../how-to/vault/vault-operations-guide.md)** - Using gds_vault in applications
- **[Vault Reference](../../reference/vault/vault-reference.md)** - API reference, troubleshooting, glossary

## Sources and Further Reading

### Official HashiCorp Documentation

- [HashiCorp Vault Documentation](https://developer.hashicorp.com/vault/docs) - Comprehensive official docs
- [Vault Production Hardening](https://developer.hashicorp.com/vault/docs/concepts/production-hardening) - Security hardening guide
- [Programmatic Best Practices](https://developer.hashicorp.com/vault/docs/configuration/programmatic-best-practices) - Terraform and automation
- [Recommended Patterns](https://developer.hashicorp.com/vault/docs/internals/recommended-patterns) - Architecture patterns
- [AppRole Best Practices](https://developer.hashicorp.com/vault/docs/auth/approle/approle-pattern) - Authentication patterns
- [KV Secrets Engine v2](https://developer.hashicorp.com/vault/docs/secrets/kv/kv-v2) - KV engine reference

### Tutorials and Guides

- [Vault Developer Quick Start](https://developer.hashicorp.com/vault/docs/get-started/developer-qs) - Getting started
- [Store Versioned KV Secrets](https://developer.hashicorp.com/vault/tutorials/secrets-management/versioned-kv) - KV v2 tutorial
- [Generate Tokens with AppRole](https://developer.hashicorp.com/vault/tutorials/auth-methods/approle) - AppRole tutorial
- [Vault on Kubernetes Security](https://developer.hashicorp.com/vault/tutorials/kubernetes/kubernetes-security-concerns) - K8s considerations

### Community Resources

- [Secure Your Secrets: Best Practices for Hardening HashiCorp Vault](https://sjramblings.io/secure-your-secrets-best-practices-for-hardening-hashicorp-vault-in-production/) - Production hardening guide
- [How to Successfully Manage Secrets with HashiCorp Vault](https://spr.com/how-to-successfully-manage-secrets-with-hashicorp-vault/) - Secrets management patterns
- [HashiCorp Vault Kubernetes: The Definitive Guide](https://www.plural.sh/blog/hashicorp-vault-kubernetes-guide/) - K8s integration

# Vault Architecture

**[← Back to Module 1](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-1_Foundations-blue)
![Lesson](https://img.shields.io/badge/Lesson-02-purple)

## Learning objectives

By the end of this lesson, you will be able to:

- Describe Vault's core architectural components
- Explain the seal/unseal mechanism and why it exists
- Identify different storage backends and their trade-offs
- Understand how secrets engines and auth methods work together

## Table of contents

- [High-level architecture](#high-level-architecture)
- [Core components](#core-components)
- [The seal/unseal mechanism](#the-sealunseal-mechanism)
- [Storage backends](#storage-backends)
- [Secrets engines](#secrets-engines)
- [Authentication methods](#authentication-methods)
- [Policies and tokens](#policies-and-tokens)
- [Hands-on lab](#hands-on-lab)
- [Key takeaways](#key-takeaways)

---

## High-level architecture

Vault follows a client-server architecture where all interactions happen through a secure HTTP API.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        VAULT ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  CLIENTS                           VAULT SERVER                          │
│  ───────                           ────────────                          │
│  ┌─────────┐                                                            │
│  │   CLI   │ ──┐                   ┌────────────────────────────────┐   │
│  └─────────┘   │                   │           HTTP API             │   │
│  ┌─────────┐   │    HTTPS/TLS      │  (All operations go through    │   │
│  │   SDK   │ ──┼─────────────────▶ │   this single interface)       │   │
│  └─────────┘   │                   └──────────────┬─────────────────┘   │
│  ┌─────────┐   │                                  │                      │
│  │   UI    │ ──┘                                  ▼                      │
│  └─────────┘                       ┌────────────────────────────────┐   │
│                                    │         VAULT CORE              │   │
│                                    │  ┌──────────────────────────┐  │   │
│                                    │  │     Auth Methods         │  │   │
│                                    │  │  (Token, AppRole, LDAP)  │  │   │
│                                    │  └──────────────────────────┘  │   │
│                                    │  ┌──────────────────────────┐  │   │
│                                    │  │    Secrets Engines       │  │   │
│                                    │  │  (KV, Database, Transit) │  │   │
│                                    │  └──────────────────────────┘  │   │
│                                    │  ┌──────────────────────────┐  │   │
│                                    │  │   System Backend         │  │   │
│                                    │  │  (Policies, Audit, ACL)  │  │   │
│                                    │  └──────────────────────────┘  │   │
│                                    └──────────────┬─────────────────┘   │
│                                                   │                      │
│                                                   ▼                      │
│                                    ┌────────────────────────────────┐   │
│                                    │       BARRIER (Encryption)     │   │
│                                    │  All data encrypted before     │   │
│                                    │  leaving this layer            │   │
│                                    └──────────────┬─────────────────┘   │
│                                                   │                      │
│                                                   ▼                      │
│                                    ┌────────────────────────────────┐   │
│                                    │      STORAGE BACKEND           │   │
│                                    │  (Raft, Consul, PostgreSQL)    │   │
│                                    └────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Core components

### HTTP API

All Vault operations—whether from CLI, SDK, or UI—go through the HTTP API:

```bash
# CLI command
vault kv get secret/myapp

# Translates to API call
GET /v1/secret/data/myapp
Header: X-Vault-Token: <token>
```

**Key properties:**
- RESTful design
- JSON request/response format
- Token-based authentication
- TLS encryption in transit

### Vault core

The core handles the business logic:

| Component | Responsibility |
|-----------|---------------|
| **Request routing** | Directs requests to appropriate handlers |
| **Token management** | Creates, validates, revokes tokens |
| **Policy enforcement** | Checks permissions before operations |
| **Audit logging** | Records all requests and responses |
| **Lease management** | Tracks and revokes dynamic secrets |

### Barrier (encryption layer)

The barrier encrypts **all** data before it leaves Vault:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         BARRIER OPERATION                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   WRITE OPERATION                                                        │
│   ───────────────                                                        │
│   ┌───────────────┐     ┌───────────────┐     ┌───────────────┐        │
│   │  Plaintext    │ ──▶ │   Barrier     │ ──▶ │  Ciphertext   │        │
│   │  Secret Data  │     │  (Encrypt)    │     │  (To Storage) │        │
│   └───────────────┘     └───────────────┘     └───────────────┘        │
│                                                                          │
│   READ OPERATION                                                         │
│   ──────────────                                                         │
│   ┌───────────────┐     ┌───────────────┐     ┌───────────────┐        │
│   │  Ciphertext   │ ──▶ │   Barrier     │ ──▶ │  Plaintext    │        │
│   │  (From Store) │     │  (Decrypt)    │     │  Secret Data  │        │
│   └───────────────┘     └───────────────┘     └───────────────┘        │
│                                                                          │
│   Encryption Key: AES-256-GCM                                           │
│   Key protected by: Unseal keys (Shamir's Secret Sharing)               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Implications:**
- Storage backend never sees plaintext data
- Compromised storage = encrypted data only
- Must unseal Vault to decrypt anything

[↑ Back to Table of Contents](#table-of-contents)

---

## The seal/unseal mechanism

Vault uses a sophisticated sealing mechanism to protect the master encryption key.

### Why sealing matters

When Vault starts, it's **sealed**:
- The encryption key is encrypted
- Vault cannot read its own data
- No secrets can be accessed

To operate, Vault must be **unsealed**:
- Provide unseal keys to decrypt the master key
- Master key loaded into memory (never written to disk)
- Vault can now decrypt/encrypt secrets

### Shamir's Secret Sharing

Vault uses Shamir's Secret Sharing algorithm to split the master key:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SHAMIR'S SECRET SHARING                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   INITIALIZATION (vault operator init)                                   │
│   ────────────────────────────────────                                   │
│                                                                          │
│       Master Key                                                         │
│          │                                                               │
│          ▼                                                               │
│   ┌─────────────────────────────────────────────────────────────┐       │
│   │              SPLIT (default: 5 shares)                       │       │
│   └─────────────────────────────────────────────────────────────┘       │
│          │                                                               │
│          ├────────┬────────┬────────┬────────┐                          │
│          ▼        ▼        ▼        ▼        ▼                          │
│       ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐                       │
│       │Key 1│  │Key 2│  │Key 3│  │Key 4│  │Key 5│                       │
│       └─────┘  └─────┘  └─────┘  └─────┘  └─────┘                       │
│          │        │        │        │        │                          │
│          ▼        ▼        ▼        ▼        ▼                          │
│       Alice    Bob     Carol    Dave     Eve                            │
│       (Admin)  (Admin) (Admin)  (DBA)   (Security)                      │
│                                                                          │
│   UNSEAL (default: 3 of 5 required)                                     │
│   ─────────────────────────────────                                      │
│                                                                          │
│       ┌─────┐  ┌─────┐  ┌─────┐                                         │
│       │Key 1│  │Key 3│  │Key 5│    Any 3 keys                          │
│       └─────┘  └─────┘  └─────┘                                         │
│          │        │        │                                             │
│          └────────┼────────┘                                             │
│                   ▼                                                      │
│   ┌─────────────────────────────────────────────────────────────┐       │
│   │            RECONSTRUCT MASTER KEY                            │       │
│   └─────────────────────────────────────────────────────────────┘       │
│                   │                                                      │
│                   ▼                                                      │
│              Master Key                                                  │
│           (in memory only)                                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Security benefits:**
- No single person has the full key
- Requires collaboration to unseal
- Lost keys can be tolerated (if below threshold)
- Compromising 1-2 keys doesn't break security

### Seal states

```bash
# Check seal status
$ vault status
Key                Value
---                -----
Seal Type          shamir
Initialized        true
Sealed             false     # <-- Currently unsealed
Total Shares       5
Threshold          3
Version            1.15.0
Storage Type       raft
```

| State | Description | Operations allowed |
|-------|-------------|-------------------|
| **Sealed** | Master key encrypted | Status check only |
| **Unsealed** | Master key in memory | All operations |

### Auto-unseal

For production, manual unsealing can be replaced with **auto-unseal**:

```hcl
# vault.hcl configuration
seal "awskms" {
  region     = "us-west-2"
  kms_key_id = "alias/vault-unseal-key"
}
```

The master key is encrypted with a cloud KMS key instead of Shamir shares.

[↑ Back to Table of Contents](#table-of-contents)

---

## Storage backends

The storage backend persists all encrypted data. Vault supports multiple backends:

### Integrated storage (Raft)

**Recommended for most deployments:**

```hcl
storage "raft" {
  path    = "/vault/data"
  node_id = "vault_1"
}
```

| Pros | Cons |
|------|------|
| No external dependencies | Requires Vault Enterprise for auto-pilot |
| Built-in HA | More complex backup/restore |
| Simple to deploy | Cluster management overhead |

### Consul

**Good for HashiCorp stack integration:**

```hcl
storage "consul" {
  address = "127.0.0.1:8500"
  path    = "vault/"
}
```

| Pros | Cons |
|------|------|
| Battle-tested | Another system to manage |
| Automatic HA | Network complexity |
| Health checking | Consul expertise required |

### Other backends

| Backend | Use case |
|---------|----------|
| **PostgreSQL** | When Postgres is already available |
| **MySQL** | When MySQL is already available |
| **S3** | Simple storage, no HA |
| **In-memory** | Development only (data lost on restart) |

### Development mode

Dev mode uses in-memory storage with auto-unseal:

```bash
# Start dev server
vault server -dev

# Characteristics:
# - In-memory storage (data lost on restart)
# - Auto-unsealed
# - Root token printed to console
# - Listens on localhost only
# - TLS disabled
```

> [!WARNING]
> Never use dev mode in production!

[↑ Back to Table of Contents](#table-of-contents)

---

## Secrets engines

Secrets engines are components that store, generate, or encrypt data.

### Enabled at paths

Each engine is mounted at a path:

```bash
# List enabled engines
$ vault secrets list
Path          Type         Description
----          ----         -----------
cubbyhole/    cubbyhole    per-token private storage
secret/       kv           key-value secret storage
sys/          system       system endpoints
```

### Common engines

| Engine | Purpose | Example use |
|--------|---------|-------------|
| **KV** | Store arbitrary secrets | Passwords, API keys |
| **Database** | Generate database credentials | PostgreSQL, MySQL users |
| **Transit** | Encryption as a service | Encrypt application data |
| **PKI** | Certificate authority | TLS certificates |
| **AWS** | Generate AWS credentials | IAM users, STS tokens |
| **SSH** | SSH key management | SSH certificates |

### Engine lifecycle

```bash
# Enable a new engine
vault secrets enable -path=myapp kv-v2

# Use the engine
vault kv put myapp/config password=secret

# Disable the engine (removes all data!)
vault secrets disable myapp/
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Authentication methods

Auth methods verify the identity of users and applications.

### How auth works

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION FLOW                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   1. CLIENT PRESENTS CREDENTIALS                                         │
│   ┌──────────────┐                                                       │
│   │   Client     │                                                       │
│   │              │  Username: alice                                      │
│   │              │  Password: ******                                     │
│   └──────┬───────┘                                                       │
│          │                                                               │
│          ▼                                                               │
│   2. VAULT VERIFIES WITH AUTH METHOD                                     │
│   ┌──────────────┐     ┌──────────────┐                                 │
│   │    Vault     │ ──▶ │  Auth Method │  Userpass: check password       │
│   │              │ ◀── │  (Userpass)  │  LDAP: query AD                 │
│   └──────┬───────┘     └──────────────┘  AppRole: verify role/secret    │
│          │                                                               │
│          ▼                                                               │
│   3. VAULT ISSUES TOKEN WITH POLICIES                                    │
│   ┌──────────────────────────────────────────────────────────────┐      │
│   │  Token: s.Xt6p8R2d9Yq3Kl7mN1o4Pj5wW8                         │      │
│   │  Policies: ["default", "app-read"]                           │      │
│   │  TTL: 768h                                                   │      │
│   └──────────────────────────────────────────────────────────────┘      │
│          │                                                               │
│          ▼                                                               │
│   4. CLIENT USES TOKEN FOR SUBSEQUENT REQUESTS                           │
│   ┌──────────────┐                                                       │
│   │   Client     │  Header: X-Vault-Token: s.Xt6p8R2d9Yq3...            │
│   │  (has token) │  GET /v1/secret/data/myapp                           │
│   └──────────────┘                                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Common auth methods

| Method | Use case | Identity source |
|--------|----------|-----------------|
| **Token** | Direct token usage | Pre-existing token |
| **Userpass** | Human users | Username/password |
| **LDAP** | Enterprise users | Active Directory |
| **AppRole** | Applications/automation | Role ID + Secret ID |
| **Kubernetes** | K8s workloads | Service account |
| **AWS IAM** | AWS workloads | IAM role |
| **OIDC** | SSO integration | Identity provider |

### Enable and configure

```bash
# Enable userpass auth
vault auth enable userpass

# Create a user
vault write auth/userpass/users/alice \
    password="password123" \
    policies="app-read"

# Login
vault login -method=userpass username=alice
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Policies and tokens

### Policies

Policies define what a token can do:

```hcl
# app-read.hcl
path "secret/data/myapp/*" {
  capabilities = ["read", "list"]
}

path "secret/metadata/myapp/*" {
  capabilities = ["list"]
}
```

**Capabilities:**
- `create` - Create new data
- `read` - Read existing data
- `update` - Modify existing data
- `delete` - Delete data
- `list` - List keys at a path
- `sudo` - Access protected paths
- `deny` - Explicitly deny access

### Tokens

Tokens are the core authentication mechanism:

```bash
# View current token
$ vault token lookup
Key                 Value
---                 -----
accessor            aRgWJP5K4sKHQ8wy
creation_time       1705851600
creation_ttl        768h
display_name        userpass-alice
entity_id           abc123-def456
expire_time         2026-02-22T10:00:00Z
policies            [default app-read]
renewable           true
ttl                 767h59m
```

**Token properties:**
- **TTL** - How long until expiration
- **Policies** - What the token can access
- **Renewable** - Can the TTL be extended
- **Accessor** - Reference without exposing the token

[↑ Back to Table of Contents](#table-of-contents)

---

## Hands-on lab

### Exercise 1: Examine Vault architecture with the CLI

1. Start a dev server (if not running):
   ```bash
   vault server -dev -dev-root-token-id="root" &
   export VAULT_ADDR='http://127.0.0.1:8200'
   export VAULT_TOKEN='root'
   ```

2. Check the server status:
   ```bash
   vault status
   ```
   Note the Seal Type, Initialized, and Sealed fields.

3. List enabled secrets engines:
   ```bash
   vault secrets list
   ```

4. List enabled auth methods:
   ```bash
   vault auth list
   ```

### Exercise 2: Understand the seal mechanism

1. Check current seal status:
   ```bash
   vault status | grep -E "Sealed|Seal Type"
   ```

2. In dev mode, Vault is auto-unsealed. The unseal key is printed on startup:
   ```
   Unseal Key: <base64-encoded-key>
   ```

3. (Optional) Seal the vault:
   ```bash
   vault operator seal
   ```

4. (Optional) Unseal:
   ```bash
   vault operator unseal <unseal-key>
   ```

### Exercise 3: Enable a new secrets engine

1. Enable a new KV engine at a custom path:
   ```bash
   vault secrets enable -path=team-secrets kv-v2
   ```

2. Verify it's enabled:
   ```bash
   vault secrets list
   ```

3. Write a test secret:
   ```bash
   vault kv put team-secrets/test message="Hello from custom path"
   ```

4. Read it back:
   ```bash
   vault kv get team-secrets/test
   ```

---

## Key takeaways

1. **Everything goes through the HTTP API** - CLI, SDK, and UI all use the same interface

2. **The barrier encrypts all data** - Storage backends only see ciphertext

3. **Seal/unseal protects the master key**:
   - Sealed: Vault cannot decrypt anything
   - Unsealed: Master key in memory for operations
   - Shamir shares prevent single points of failure

4. **Storage backends are pluggable** - Raft (integrated) is recommended for most use cases

5. **Secrets engines generate/store secrets** - Different engines for different use cases

6. **Auth methods verify identity** - Result is always a token with policies

7. **Policies control access** - Fine-grained path-based permissions

---

## Next steps

In the next lesson, you'll set up a Vault development environment using Docker.

---

[← Previous: Introduction](./01-introduction-to-secrets-management.md) | [Back to Module 1](./README.md) | [Next: Dev Environment →](./03-vault-dev-environment.md)

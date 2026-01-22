# Introduction to Secrets Management

**[← Back to Module 1](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-1_Foundations-blue)
![Lesson](https://img.shields.io/badge/Lesson-01-purple)

## Learning objectives

By the end of this lesson, you will be able to:

- Define what constitutes a "secret" in software systems
- Identify common security risks with traditional secret handling
- Explain the benefits of centralized secrets management
- Describe HashiCorp Vault's value proposition

## Table of contents

- [What are secrets?](#what-are-secrets)
- [The secrets problem](#the-secrets-problem)
- [Why secrets management?](#why-secrets-management)
- [Introduction to HashiCorp Vault](#introduction-to-hashicorp-vault)
- [Common use cases](#common-use-cases)
- [Hands-on lab](#hands-on-lab)
- [Key takeaways](#key-takeaways)

---

## What are secrets?

A **secret** is any piece of sensitive information that grants access to systems, data, or services. If exposed, secrets can lead to unauthorized access, data breaches, or system compromise.

### Types of secrets

| Category | Examples | Risk if exposed |
|----------|----------|-----------------|
| **Credentials** | Database passwords, service account passwords | Unauthorized data access |
| **API keys** | Cloud provider keys, third-party service tokens | Account takeover, billing fraud |
| **Certificates** | TLS/SSL certificates, SSH keys | Man-in-the-middle attacks |
| **Encryption keys** | AES keys, RSA private keys | Data decryption, forgery |
| **Tokens** | OAuth tokens, JWTs, session tokens | Identity impersonation |

### Secrets are everywhere

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     WHERE SECRETS LIVE                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │
│   │   Source Code   │    │   Config Files  │    │   Environment   │    │
│   │   ────────────  │    │   ────────────  │    │   ────────────  │    │
│   │ DB_PASS="..."   │    │ password: ...   │    │ export KEY=...  │    │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘    │
│                                                                          │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │
│   │   CI/CD Logs    │    │   Containers    │    │   Cloud Consoles│    │
│   │   ────────────  │    │   ────────────  │    │   ────────────  │    │
│   │ build output    │    │ docker inspect  │    │ IAM, Key Vault  │    │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

## The secrets problem

### Anti-pattern 1: Hardcoded secrets

The most dangerous pattern is embedding secrets directly in code:

```python
# NEVER DO THIS - Hardcoded secrets
DATABASE_URL = "postgresql://admin:SuperSecret123@prod-db.example.com/mydb"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY"
STRIPE_API_KEY = "sk_live_abc123xyz789"
```

**Why this is dangerous:**

1. **Git history is forever** - Even after removing the secret, it remains in commit history
2. **Shared with everyone** - Anyone with repo access sees production credentials
3. **Same everywhere** - Dev, staging, and production use the same secret
4. **No rotation** - Changing secrets requires code deployments

### Anti-pattern 2: Environment variables alone

Better than hardcoding, but still problematic:

```bash
# Slightly better, but still risky
export DATABASE_PASSWORD="SuperSecret123"
```

**Remaining risks:**

- Secrets visible in shell history (`~/.bash_history`)
- Exposed in process listings (`ps aux -e`)
- Logged by orchestration tools
- No access control or audit trail
- No automatic rotation

### Anti-pattern 3: Configuration files

```yaml
# config.yaml - DANGEROUS if committed to version control
database:
  host: prod-db.example.com
  username: admin
  password: SuperSecret123  # <-- Security risk!
```

**Problems:**

- Often accidentally committed to version control
- Shared across environments
- No encryption at rest
- No access logging

### Real-world breaches

| Year | Company | Cause | Impact |
|------|---------|-------|--------|
| 2021 | Codecov | Secrets in CI logs | Supply chain attack |
| 2019 | Capital One | AWS credentials exposed | 100M+ records |
| 2018 | GitHub | Secrets in public repos | Thousands of keys exposed daily |

[↑ Back to Table of Contents](#table-of-contents)

---

## Why secrets management?

A proper secrets management solution addresses all these problems:

### Core capabilities

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   SECRETS MANAGEMENT CAPABILITIES                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 1. CENTRALIZED STORAGE                                           │   │
│  │    • Single source of truth for all secrets                      │   │
│  │    • No secrets in code, configs, or environment                 │   │
│  │    • Fetch secrets at runtime                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 2. ACCESS CONTROL                                                │   │
│  │    • Fine-grained permissions (who can access what)              │   │
│  │    • Application-specific credentials                            │   │
│  │    • Role-based access                                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 3. ENCRYPTION                                                    │   │
│  │    • Secrets encrypted at rest                                   │   │
│  │    • Encrypted in transit (TLS)                                  │   │
│  │    • Only authorized parties can decrypt                         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 4. AUDIT LOGGING                                                 │   │
│  │    • Track every secret access                                   │   │
│  │    • Who accessed what, when                                     │   │
│  │    • Compliance and forensics                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 5. DYNAMIC SECRETS                                               │   │
│  │    • Generate credentials on demand                              │   │
│  │    • Short-lived, unique per application                         │   │
│  │    • Automatic expiration                                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 6. ROTATION                                                      │   │
│  │    • Automatic credential rotation                               │   │
│  │    • Zero-downtime updates                                       │   │
│  │    • Reduce blast radius of leaks                                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Before and after

**Without secrets management:**

```python
# Secrets scattered everywhere
import os

DB_PASSWORD = os.getenv("DB_PASSWORD")  # Where does this come from?
# No audit trail
# No access control
# Manual rotation = downtime
```

**With secrets management (Vault):**

```python
# Secrets centralized and secured
from gds_vault import VaultClient

with VaultClient() as vault:
    secret = vault.get_secret("database/prod/credentials")
    # Audited access
    # Policy-controlled
    # Auto-rotated
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Introduction to HashiCorp Vault

HashiCorp Vault is an identity-based secrets management system. It provides a unified interface to secrets while providing tight access control and recording a detailed audit log.

### Key features

| Feature | Description |
|---------|-------------|
| **Secrets Storage** | Securely store and manage arbitrary secrets |
| **Dynamic Secrets** | Generate credentials on-demand with automatic expiration |
| **Data Encryption** | Encrypt/decrypt data without storing it (Transit engine) |
| **Identity Management** | Tie secrets access to machine and user identities |
| **Leasing & Renewal** | All secrets have a lease with automatic revocation |
| **Revocation** | Revoke single secrets or entire trees of secrets |

### How Vault works (high-level)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         VAULT WORKFLOW                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────┐         1. Authenticate                              │
│   │ Application  │ ─────────────────────────────────────────▶           │
│   │              │                                           │          │
│   │              │ ◀─────────────────────────────────────────│          │
│   │              │         2. Receive Token                  │          │
│   └──────┬───────┘                                           │          │
│          │                                                   │          │
│          │               3. Request Secret                   │          │
│          │            (with token attached)      ┌───────────┴────────┐ │
│          │ ──────────────────────────────────▶   │                    │ │
│          │                                       │       VAULT        │ │
│          │ ◀──────────────────────────────────   │                    │ │
│          │               4. Return Secret        │  • Verify token    │ │
│          │            (if policy allows)         │  • Check policy    │ │
│          ▼                                       │  • Log access      │ │
│   ┌──────────────┐                               │  • Return secret   │ │
│   │ Application  │                               │                    │ │
│   │  (has secret)│                               └────────────────────┘ │
│   └──────────────┘                                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Vault vs alternatives

| Feature | Vault | AWS Secrets Manager | Azure Key Vault | K8s Secrets |
|---------|-------|---------------------|-----------------|-------------|
| Multi-cloud | Yes | AWS only | Azure only | K8s only |
| Dynamic secrets | Yes | Limited | Limited | No |
| On-premise | Yes | No | No | Yes |
| PKI/Certificates | Yes | ACM | Yes | No |
| Transit encryption | Yes | No | Yes | No |
| Fine-grained policies | Yes | Yes | Yes | Limited |
| Open source | Yes | No | No | Yes |

[↑ Back to Table of Contents](#table-of-contents)

---

## Common use cases

### 1. Static secrets storage

Store and manage passwords, API keys, and configuration:

```bash
# Store application secrets
vault kv put secret/myapp/config \
    db_password="SuperSecret123" \
    api_key="sk-abc123"

# Retrieve at runtime
vault kv get secret/myapp/config
```

### 2. Dynamic database credentials

Generate unique, short-lived database credentials:

```bash
# Application requests credentials
vault read database/creds/my-role

# Output: unique, temporary credentials
# username: v-approle-my-role-xyz123
# password: A1B2C3-randomly-generated
# TTL: 1 hour (then auto-revoked)
```

**Benefits:**
- Each application instance gets unique credentials
- Compromised credentials expire quickly
- No shared passwords across environments

### 3. Encryption as a service

Encrypt sensitive data without managing keys:

```bash
# Encrypt data (application never sees the key)
vault write transit/encrypt/my-key \
    plaintext=$(echo "sensitive data" | base64)

# Decrypt data
vault write transit/decrypt/my-key \
    ciphertext="vault:v1:abc123..."
```

### 4. PKI certificate management

Issue TLS certificates from an internal CA:

```bash
# Request a certificate
vault write pki/issue/web-servers \
    common_name="app.example.com" \
    ttl="720h"

# Output: certificate, private_key, ca_chain
```

### 5. Kubernetes secrets injection

Automatically inject secrets into pods:

```yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/agent-inject-secret-db: "secret/data/myapp/db"
spec:
  containers:
    - name: app
      # Secret automatically available at /vault/secrets/db
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Hands-on lab

In this lab, you will observe the security risks of hardcoded secrets.

### Setup

No Vault needed for this lab - we're demonstrating the problem.

### Exercise 1: Find secrets in Git history

1. Create a sample project:
   ```bash
   mkdir secrets-lab && cd secrets-lab
   git init
   ```

2. Add a file with a "secret":
   ```bash
   cat > config.py << 'EOF'
   DATABASE_PASSWORD = "SuperSecret123"
   API_KEY = "sk-test-abc123"
   EOF
   git add . && git commit -m "Initial commit"
   ```

3. "Fix" by removing the secret:
   ```bash
   cat > config.py << 'EOF'
   DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
   API_KEY = os.getenv("API_KEY")
   EOF
   git add . && git commit -m "Remove hardcoded secrets"
   ```

4. Attempt to find the secret in history:
   ```bash
   git log -p | grep -i "password\|secret\|key"
   ```

**Observation:** The secret is still visible in Git history!

### Exercise 2: Secrets in environment

1. Set a secret in the environment:
   ```bash
   export MY_SECRET="SuperSecret123"
   ```

2. Check where it's visible:
   ```bash
   # In process list (on some systems)
   ps eww $$ | grep MY_SECRET

   # In /proc filesystem
   cat /proc/$$/environ | tr '\0' '\n' | grep MY_SECRET
   ```

**Observation:** Environment variables aren't truly "secret."

### Exercise 3: Plan your secrets inventory

List all secrets your team currently manages:

| Secret | Current Location | Access Control | Rotation Frequency |
|--------|------------------|----------------|-------------------|
| DB password | .env file | Anyone with repo | Never |
| API key | CI/CD secrets | CI admins | Never |
| ... | ... | ... | ... |

---

## Key takeaways

1. **Secrets are everywhere** - Credentials, keys, tokens, certificates
2. **Hardcoded secrets are dangerous** - Git history, shared access, no rotation
3. **Environment variables aren't enough** - Still visible, no audit, no access control
4. **Secrets management solves these problems**:
   - Centralized storage with encryption
   - Fine-grained access control
   - Comprehensive audit logging
   - Dynamic secrets and automatic rotation
5. **Vault is a leading solution** - Open source, multi-cloud, feature-rich

---

## Next steps

In the next lesson, you'll learn about Vault's architecture and how it securely manages secrets.

---

[← Back to Module 1](./README.md) | [Next: Vault Architecture →](./02-vault-architecture.md)

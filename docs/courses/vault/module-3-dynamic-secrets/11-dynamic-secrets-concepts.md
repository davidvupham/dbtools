# Dynamic Secrets Concepts

**[← Back to Module 3](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-3_Dynamic_Secrets-blue)
![Lesson](https://img.shields.io/badge/Lesson-11-purple)

## Learning objectives

By the end of this lesson, you will be able to:

- Explain the concept and benefits of dynamic secrets
- Understand leases and their lifecycle
- Describe common dynamic secret patterns
- Implement lease renewal and revocation

## Table of contents

- [What are dynamic secrets?](#what-are-dynamic-secrets)
- [Benefits of dynamic secrets](#benefits-of-dynamic-secrets)
- [Leases](#leases)
- [Lease management](#lease-management)
- [Common patterns](#common-patterns)
- [Hands-on lab](#hands-on-lab)
- [Key takeaways](#key-takeaways)

---

## What are dynamic secrets?

Dynamic secrets are credentials generated on-demand by Vault when requested. Unlike static secrets (stored values), dynamic secrets are created fresh for each request.

### Dynamic secret lifecycle

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   DYNAMIC SECRET LIFECYCLE                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   1. REQUEST                                                            │
│   ┌──────────────┐         vault read database/creds/app                │
│   │ Application  │ ──────────────────────────────────────▶              │
│   └──────────────┘                                                       │
│                                                                          │
│   2. GENERATION                                                         │
│                              ┌─────────────────────────────────────┐    │
│                              │           VAULT                      │    │
│                              │                                      │    │
│                              │  • Generate unique credentials       │    │
│                              │  • Create user in target system      │    │
│                              │  • Track with lease                  │    │
│                              │  • Return to client                  │    │
│                              └─────────────────────────────────────┘    │
│                                                                          │
│   3. USAGE                                                              │
│   ┌──────────────┐    ┌──────────────────────────────────────┐         │
│   │ Application  │───▶│ username: v-approle-app-abc123       │         │
│   │              │    │ password: A1B2C3-random-xyz          │         │
│   │              │    │ lease_id: database/creds/app/xyz789  │         │
│   │              │    │ lease_duration: 1h                   │         │
│   └──────────────┘    └──────────────────────────────────────┘         │
│         │                                                                │
│         │ Connect to database                                           │
│         ▼                                                                │
│   ┌──────────────┐                                                      │
│   │   Database   │                                                      │
│   └──────────────┘                                                      │
│                                                                          │
│   4. EXPIRATION (after TTL)                                             │
│                              ┌─────────────────────────────────────┐    │
│                              │           VAULT                      │    │
│                              │                                      │    │
│                              │  • Lease expires                     │    │
│                              │  • Delete user from database         │    │
│                              │  • Credentials no longer valid       │    │
│                              └─────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Benefits of dynamic secrets

### 1. Reduced blast radius

If credentials are compromised, the exposure window is limited to the TTL:

| Secret Type | Exposure Window |
|-------------|-----------------|
| Static password | Forever (until manually rotated) |
| Dynamic credential (1h TTL) | Maximum 1 hour |

### 2. Unique credentials per client

Each application instance gets unique credentials:

```bash
# App instance 1
vault read database/creds/readonly
# username: v-approle-readonly-1234-abc

# App instance 2
vault read database/creds/readonly
# username: v-approle-readonly-5678-def
```

### 3. Automatic rotation

No manual credential rotation needed:

- Old credentials expire automatically
- New credentials generated on request
- No deployment required for rotation

### 4. Audit trail

Know exactly which credential accessed what:

```json
{
  "auth": {"accessor": "abc123"},
  "request": {"path": "database/creds/readonly"},
  "response": {"data": {"username": "v-approle-readonly-xyz"}}
}
```

### 5. Revocation

Instantly revoke access when needed:

```bash
# Revoke specific credential
vault lease revoke database/creds/app/lease-id

# Revoke all credentials for a role
vault lease revoke -prefix database/creds/app/
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Leases

Every dynamic secret comes with a lease - metadata tracking its lifecycle.

### Lease components

| Component | Description |
|-----------|-------------|
| `lease_id` | Unique identifier for this lease |
| `lease_duration` | How long until expiration (seconds) |
| `renewable` | Whether the lease can be renewed |

### Lease example

```bash
$ vault read database/creds/readonly

Key                Value
---                -----
lease_id           database/creds/readonly/abcd1234efgh5678
lease_duration     1h
lease_renewable    true
password           A1B2C3D4E5F6
username           v-approle-readonly-xyz123
```

### Lease hierarchy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      LEASE HIERARCHY                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Token (parent)                                                        │
│   └── database/creds/app/lease1                                         │
│   └── database/creds/app/lease2                                         │
│   └── pki/issue/web/lease3                                              │
│                                                                          │
│   When token is revoked → All child leases are revoked                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Lease management

### View leases

```bash
# List leases for a path
vault list sys/leases/lookup/database/creds/readonly

# Look up specific lease
vault lease lookup database/creds/readonly/abcd1234
```

### Renew leases

```bash
# Renew with default increment
vault lease renew database/creds/readonly/abcd1234

# Renew with specific increment
vault lease renew -increment=30m database/creds/readonly/abcd1234
```

### Revoke leases

```bash
# Revoke specific lease
vault lease revoke database/creds/readonly/abcd1234

# Revoke all leases under a prefix
vault lease revoke -prefix database/creds/readonly/

# Force revoke (no grace period)
vault lease revoke -force database/creds/readonly/abcd1234
```

### Max TTL behavior

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TTL AND MAX TTL                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Role configuration:                                                   │
│   • default_ttl: 1h                                                     │
│   • max_ttl: 24h                                                        │
│                                                                          │
│   Timeline:                                                             │
│   ├─────────┼─────────┼─────────┼─────────┼─────────────────────────┤   │
│   0h        1h        2h        3h        ...                    24h    │
│   │         │                                                     │     │
│   │         │ Expires if not renewed                              │     │
│   │         │                                                     │     │
│   │         └──▶ Renewed to 2h ──▶ Renewed to 3h ──▶ ... ──▶ Max │     │
│   │                                                               │     │
│   Issue     Can keep renewing...              Cannot exceed max_ttl     │
│                                                                          │
│   After 24h: Lease MUST expire, cannot be renewed further               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Common patterns

### Pattern 1: Request-per-connection

Each database connection gets a new credential:

```python
def get_db_connection():
    # Get fresh credentials from Vault
    creds = vault.read("database/creds/app")

    # Connect with unique credentials
    return psycopg2.connect(
        user=creds["username"],
        password=creds["password"]
    )
```

### Pattern 2: Cached with renewal

Get once, renew before expiration:

```python
class VaultDBPool:
    def __init__(self):
        self.creds = None
        self.lease_id = None

    def get_credentials(self):
        if self.creds is None or self._is_expiring():
            self._refresh_credentials()
        return self.creds

    def _refresh_credentials(self):
        response = vault.read("database/creds/app")
        self.creds = response["data"]
        self.lease_id = response["lease_id"]

    def _is_expiring(self):
        # Refresh when less than 10 min remaining
        return self.remaining_ttl() < 600

    def renew(self):
        vault.renew_lease(self.lease_id)
```

### Pattern 3: Graceful credential rotation

Handle credential changes without downtime:

```python
class GracefulDBClient:
    def __init__(self):
        self.current_conn = None
        self.new_conn = None

    def rotate_credentials(self):
        # Get new credentials
        creds = vault.read("database/creds/app")
        self.new_conn = create_connection(creds)

        # Drain old connection
        self.current_conn.drain()

        # Switch
        old = self.current_conn
        self.current_conn = self.new_conn

        # Cleanup
        old.close()
        self.new_conn = None
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Hands-on lab

### Setup

```bash
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'
```

### Exercise 1: Understand leases with KV

Even static secrets can have leases:

```bash
# Enable KV v1 (has leases unlike v2)
vault secrets enable -path=kv kv

# Put a secret
vault kv put kv/test password=secret

# Read with lease info
vault read kv/test

# Note: KV v1 has lease_duration but it's informational
```

### Exercise 2: Explore lease commands

```bash
# Create a token with TTL (creates a lease)
TOKEN=$(vault token create -ttl=5m -format=json | jq -r '.auth.client_token')

# List active leases
vault list sys/leases/lookup/auth/token/create

# Look up the token's lease
vault token lookup $TOKEN | grep -E "ttl|expire"

# Renew the token
vault token renew $TOKEN

# Check TTL again
vault token lookup $TOKEN | grep ttl
```

### Exercise 3: Lease revocation

```bash
# Create multiple tokens
TOKEN1=$(vault token create -ttl=1h -format=json | jq -r '.auth.client_token')
TOKEN2=$(vault token create -ttl=1h -format=json | jq -r '.auth.client_token')

# List leases
vault list sys/leases/lookup/auth/token/create

# Revoke all token leases (careful!)
# vault lease revoke -prefix auth/token/create/

# Revoke specific token
vault token revoke $TOKEN1

# Verify TOKEN1 is invalid
vault token lookup $TOKEN1
# Error: bad token
```

---

## Key takeaways

1. **Dynamic secrets are generated on-demand** - Not stored, but created per request

2. **Each request gets unique credentials** - Improves audit and limits blast radius

3. **Leases track secret lifecycle**:
   - `lease_id`: Unique identifier
   - `lease_duration`: Time until expiration
   - `renewable`: Can TTL be extended

4. **TTL vs Max TTL**:
   - TTL: Initial duration
   - Max TTL: Absolute maximum lifetime

5. **Lease management**:
   - Renew: Extend lifetime
   - Revoke: Immediately invalidate

6. **Revocation cascades** - Revoking a token revokes all its leases

---

## Next steps

In the next lesson, you'll configure the database secrets engine for PostgreSQL.

---

[← Back to Module 3](./README.md) | [Next: Database Secrets →](./12-database-secrets-engine.md)

# Token Authentication

**[← Back to Module 2](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-2_Authentication-blue)
![Lesson](https://img.shields.io/badge/Lesson-06-purple)

## Learning objectives

By the end of this lesson, you will be able to:

- Explain the role of tokens in Vault authentication
- Differentiate between token types (service, batch, periodic)
- Understand token hierarchy and orphan tokens
- Manage token lifecycle (create, renew, revoke)

## Table of contents

- [Tokens overview](#tokens-overview)
- [Token types](#token-types)
- [Token properties](#token-properties)
- [Token hierarchy](#token-hierarchy)
- [Creating and managing tokens](#creating-and-managing-tokens)
- [Hands-on lab](#hands-on-lab)
- [Key takeaways](#key-takeaways)

---

## Tokens overview

Tokens are the core of Vault authentication. After authenticating via any method, Vault issues a token that the client uses for subsequent requests.

### Token anatomy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TOKEN STRUCTURE                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Token ID: hvs.CAESIG...                                               │
│   ─────────────────────────────────────────────                         │
│   │                                                                      │
│   │  ┌─────────────────────────────────────────────────────────┐       │
│   │  │ Prefix: hvs. (Vault service token)                      │       │
│   │  │         hvb. (Vault batch token)                        │       │
│   │  │         hvr. (Vault recovery token)                     │       │
│   │  └─────────────────────────────────────────────────────────┘       │
│   │                                                                      │
│   │  ┌─────────────────────────────────────────────────────────┐       │
│   │  │ Encoded payload:                                        │       │
│   │  │   • Namespace (if applicable)                           │       │
│   │  │   • Random identifier                                   │       │
│   │  │   • Accessor (for batch tokens)                         │       │
│   │  └─────────────────────────────────────────────────────────┘       │
│   │                                                                      │
│   Token Accessor: abc123...                                             │
│   ──────────────────────────                                            │
│   • Reference token without exposing it                                 │
│   • Use for audit logs, revocation                                      │
│   • Cannot be used to authenticate                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### What tokens contain

Every token has associated metadata:

| Property | Description |
|----------|-------------|
| `id` | The actual token string (secret) |
| `accessor` | Non-sensitive reference to the token |
| `policies` | List of policies attached |
| `ttl` | Time until expiration |
| `creation_time` | When the token was created |
| `renewable` | Whether TTL can be extended |
| `orphan` | Whether token has a parent |
| `entity_id` | Associated identity entity |

[↑ Back to Table of Contents](#table-of-contents)

---

## Token types

### Service tokens

The default and most common token type:

```bash
# Create a service token
vault token create -policy=my-policy
```

**Characteristics:**
- Persisted in storage
- Can be renewed
- Have a parent (unless orphan)
- Revocation cascades to children

### Batch tokens

Lightweight, high-performance tokens:

```bash
# Create a batch token
vault token create -type=batch -policy=my-policy
```

**Characteristics:**
- Not persisted (encrypted in token itself)
- Cannot be renewed
- No parent-child relationships
- No accessor
- More efficient for high-volume operations

### Periodic tokens

Tokens that never expire if renewed:

```bash
# Create a periodic token
vault token create -policy=my-policy -period=24h
```

**Characteristics:**
- Can be renewed indefinitely
- Each renewal resets TTL to the period
- Useful for long-running services
- Must be renewed before expiration

### Comparison

| Feature | Service | Batch | Periodic |
|---------|---------|-------|----------|
| Persisted | Yes | No | Yes |
| Renewable | Yes | No | Yes (forever) |
| Has accessor | Yes | No | Yes |
| Parent tracking | Yes | No | Yes |
| Performance | Normal | High | Normal |
| Use case | General | High volume | Long-running |

[↑ Back to Table of Contents](#table-of-contents)

---

## Token properties

### TTL (Time To Live)

```bash
# Create token with specific TTL
vault token create -ttl=1h -policy=my-policy

# Create with max TTL
vault token create -ttl=1h -explicit-max-ttl=24h -policy=my-policy
```

**TTL rules:**
- `ttl`: Initial lifetime
- `explicit-max-ttl`: Maximum possible lifetime (cannot be exceeded by renewal)
- `0` TTL: Never expires (only root tokens)

### Policies

```bash
# Token with multiple policies
vault token create -policy=policy-a -policy=policy-b

# Policies are additive
# Token gets UNION of all policy capabilities
```

### Number of uses

```bash
# Token valid for only 5 operations
vault token create -use-limit=5 -policy=my-policy
```

After 5 uses, the token is automatically revoked.

### Display name

```bash
# Add descriptive name for audit logs
vault token create -display-name="ci-pipeline-main" -policy=deploy
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Token hierarchy

Service tokens form a parent-child hierarchy:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TOKEN HIERARCHY                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                    ┌──────────────┐                                      │
│                    │  Root Token  │                                      │
│                    │   (parent)   │                                      │
│                    └──────┬───────┘                                      │
│                           │                                              │
│            ┌──────────────┼──────────────┐                              │
│            ▼              ▼              ▼                              │
│     ┌──────────┐   ┌──────────┐   ┌──────────┐                         │
│     │ Token A  │   │ Token B  │   │ Token C  │                         │
│     │ (child)  │   │ (child)  │   │ (orphan) │ ← No parent             │
│     └────┬─────┘   └──────────┘   └──────────┘                         │
│          │                                                              │
│          ▼                                                              │
│     ┌──────────┐                                                        │
│     │ Token D  │                                                        │
│     │(grandchild)                                                       │
│     └──────────┘                                                        │
│                                                                          │
│   REVOCATION:                                                           │
│   • Revoke Token A → Token D also revoked                               │
│   • Revoke Root   → All children (A, B, D) revoked                     │
│   • Revoke Token C → Only C revoked (orphan)                           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Orphan tokens

Tokens without a parent:

```bash
# Create orphan token
vault token create -orphan -policy=my-policy
```

**Benefits:**
- Survive parent revocation
- Independent lifecycle
- Useful for long-running processes

**Requirements:**
- Creating orphan tokens requires special permission (`auth/token/create-orphan`)
- Or root/sudo access

[↑ Back to Table of Contents](#table-of-contents)

---

## Creating and managing tokens

### Create tokens

```bash
# Basic token
vault token create

# With policies and TTL
vault token create -policy=reader -policy=writer -ttl=2h

# Orphan token
vault token create -orphan -policy=app-policy

# Periodic token
vault token create -period=24h -policy=service-policy

# Batch token
vault token create -type=batch -policy=ephemeral-policy

# With metadata
vault token create -metadata=app=myapp -metadata=env=prod
```

### Lookup tokens

```bash
# Current token
vault token lookup

# Specific token
vault token lookup <token>

# By accessor (doesn't need the actual token)
vault token lookup -accessor <accessor>
```

### Renew tokens

```bash
# Renew current token
vault token renew

# Renew specific token
vault token renew <token>

# Renew with increment
vault token renew -increment=2h <token>
```

### Revoke tokens

```bash
# Revoke specific token
vault token revoke <token>

# Revoke by accessor
vault token revoke -accessor <accessor>

# Revoke current token (and all children!)
vault token revoke -self

# Revoke orphan (don't revoke children)
vault token revoke -mode=orphan <token>
```

### Token role

Pre-define token parameters:

```bash
# Create a token role
vault write auth/token/roles/ci-runner \
    allowed_policies="deploy,read-secrets" \
    orphan=true \
    period=24h \
    renewable=true

# Create token from role
vault token create -role=ci-runner
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Hands-on lab

### Setup

```bash
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'
```

### Exercise 1: Token properties

1. Create a token and examine its properties:
   ```bash
   TOKEN=$(vault token create -policy=default -format=json | jq -r '.auth.client_token')
   vault token lookup $TOKEN
   ```

2. Note the accessor, policies, and TTL.

### Exercise 2: Token hierarchy

1. Create a parent token:
   ```bash
   PARENT=$(vault token create -policy=default -ttl=1h -format=json | jq -r '.auth.client_token')
   ```

2. Use parent to create child:
   ```bash
   VAULT_TOKEN=$PARENT vault token create -policy=default -ttl=30m
   ```

3. Revoke parent and observe child:
   ```bash
   vault token revoke $PARENT
   # Child is also revoked
   ```

### Exercise 3: Orphan tokens

1. Create an orphan:
   ```bash
   ORPHAN=$(vault token create -orphan -policy=default -format=json | jq -r '.auth.client_token')
   ```

2. Verify it's orphan:
   ```bash
   vault token lookup $ORPHAN | grep orphan
   ```

### Exercise 4: Token renewal

1. Create renewable token:
   ```bash
   TOKEN=$(vault token create -ttl=5m -policy=default -format=json | jq -r '.auth.client_token')
   ```

2. Check TTL:
   ```bash
   vault token lookup $TOKEN | grep ttl
   ```

3. Renew and check again:
   ```bash
   vault token renew $TOKEN
   vault token lookup $TOKEN | grep ttl
   ```

### Exercise 5: Batch vs service tokens

1. Create both types:
   ```bash
   SERVICE=$(vault token create -policy=default -format=json | jq -r '.auth.client_token')
   BATCH=$(vault token create -type=batch -policy=default -format=json | jq -r '.auth.client_token')
   ```

2. Compare:
   ```bash
   echo "Service: $SERVICE"
   echo "Batch: $BATCH"
   # Note the different prefixes: hvs. vs hvb.
   ```

3. Try to renew batch (fails):
   ```bash
   vault token renew $BATCH
   # Error: batch tokens cannot be renewed
   ```

---

## Key takeaways

1. **Tokens are Vault's authentication mechanism** - All auth methods result in tokens

2. **Three token types**:
   - Service: Default, persisted, renewable
   - Batch: Lightweight, not persisted, high performance
   - Periodic: Can be renewed forever

3. **Token hierarchy** - Parent revocation cascades to children (except orphans)

4. **Accessors** - Safe way to reference tokens without exposing them

5. **TTL management** - Control token lifetime with ttl and max-ttl

6. **Token roles** - Pre-configure token parameters for consistency

---

## Next steps

In the next lesson, you'll learn about AppRole authentication for machine-to-machine authentication.

---

[← Back to Module 2](./README.md) | [Next: AppRole Authentication →](./07-approle-authentication.md)

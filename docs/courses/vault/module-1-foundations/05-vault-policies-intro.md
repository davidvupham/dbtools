# Vault Policies Introduction

**[← Back to Module 1](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-1_Foundations-blue)
![Lesson](https://img.shields.io/badge/Lesson-05-purple)

## Learning objectives

By the end of this lesson, you will be able to:

- Explain how Vault's policy system works
- Write basic policies using HCL syntax
- Understand capabilities and path patterns
- Apply policies to tokens and users

## Table of contents

- [What are policies?](#what-are-policies)
- [Policy syntax](#policy-syntax)
- [Capabilities](#capabilities)
- [Path patterns](#path-patterns)
- [Managing policies](#managing-policies)
- [Attaching policies](#attaching-policies)
- [Hands-on lab](#hands-on-lab)
- [Key takeaways](#key-takeaways)

---

## What are policies?

Policies are the primary mechanism for controlling access in Vault. They define **what** actions can be performed on **which** paths.

### Default behavior

Vault follows a **deny by default** model:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    VAULT AUTHORIZATION MODEL                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   DEFAULT: DENY EVERYTHING                                              │
│   ────────────────────────                                               │
│                                                                          │
│   Token without policies:                                               │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ secret/app1/* → DENIED                                          │   │
│   │ secret/app2/* → DENIED                                          │   │
│   │ database/*    → DENIED                                          │   │
│   │ sys/*         → DENIED (except some paths)                      │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   Token with "app1-read" policy:                                        │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ secret/data/app1/* → ALLOWED (read, list)                       │   │
│   │ secret/data/app2/* → DENIED                                     │   │
│   │ database/*         → DENIED                                     │   │
│   │ sys/*              → DENIED (except some paths)                 │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   Policies are ADDITIVE (union of all attached policies)                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Built-in policies

Vault has two built-in policies:

| Policy | Description |
|--------|-------------|
| `default` | Attached to all tokens; provides basic self-management |
| `root` | Superuser access; all capabilities on all paths |

```bash
# View default policy
vault policy read default

# The root policy is implicit - there's no HCL file
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Policy syntax

Policies are written in HCL (HashiCorp Configuration Language):

### Basic structure

```hcl
# policy-name.hcl

# Allow read access to a specific path
path "secret/data/myapp/config" {
  capabilities = ["read"]
}

# Allow full access to a path prefix
path "secret/data/myapp/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
```

### Policy components

```hcl
path "<path-pattern>" {
  capabilities = [<list-of-capabilities>]

  # Optional constraints
  required_parameters = ["param1", "param2"]
  allowed_parameters = {
    "key" = ["value1", "value2"]
  }
  denied_parameters = {
    "key" = ["*"]
  }
}
```

### Real-world example

```hcl
# web-app-policy.hcl - Policy for a web application

# Read application configuration
path "secret/data/webapp/config" {
  capabilities = ["read"]
}

# Full access to application secrets
path "secret/data/webapp/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Allow listing to navigate
path "secret/metadata/webapp/*" {
  capabilities = ["list", "read"]
}

# Generate database credentials
path "database/creds/webapp-role" {
  capabilities = ["read"]
}

# Renew own token
path "auth/token/renew-self" {
  capabilities = ["update"]
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Capabilities

Capabilities define what operations are allowed on a path:

### Available capabilities

| Capability | HTTP Verb | Description |
|------------|-----------|-------------|
| `create` | POST/PUT | Create new data at a path |
| `read` | GET | Read data from a path |
| `update` | POST/PUT | Modify existing data |
| `delete` | DELETE | Delete data |
| `list` | LIST | List keys at a path |
| `sudo` | - | Access root-protected endpoints |
| `deny` | - | Explicitly deny access |

### Capability mapping

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CAPABILITIES TO OPERATIONS                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   KV v2 Operations:                                                     │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ vault kv put    → requires: create OR update                    │   │
│   │ vault kv get    → requires: read                                │   │
│   │ vault kv delete → requires: delete                              │   │
│   │ vault kv list   → requires: list (on metadata path!)            │   │
│   │ vault kv patch  → requires: read + update                       │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   Important: KV v2 has separate data and metadata paths!                │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ Data operations:     secret/data/myapp/*                        │   │
│   │ List operations:     secret/metadata/myapp/*                    │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Deny capability

`deny` is special - it takes precedence over all other capabilities:

```hcl
# Allow access to everything under secret/
path "secret/data/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# But explicitly deny access to admin secrets
path "secret/data/admin/*" {
  capabilities = ["deny"]
}
```

### Sudo capability

Some system paths require `sudo`:

```hcl
# Required for administrative operations
path "sys/policy/*" {
  capabilities = ["sudo", "create", "read", "update", "delete", "list"]
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Path patterns

Paths in policies support glob patterns for flexible matching.

### Glob patterns

| Pattern | Matches |
|---------|---------|
| `secret/data/myapp` | Exactly `secret/data/myapp` |
| `secret/data/myapp/*` | Any path under `myapp/` (one level) |
| `secret/data/myapp/+` | Exactly one segment under `myapp/` |
| `secret/data/+/config` | Any path like `secret/data/X/config` |

### Pattern examples

```hcl
# Exact path match
path "secret/data/myapp/database" {
  capabilities = ["read"]
}

# Glob: matches secret/data/myapp/anything/here/too
path "secret/data/myapp/*" {
  capabilities = ["read"]
}

# Single segment: matches secret/data/myapp/X but not secret/data/myapp/X/Y
path "secret/data/myapp/+" {
  capabilities = ["read"]
}

# Mixed: matches secret/data/team1/config, secret/data/team2/config, etc.
path "secret/data/+/config" {
  capabilities = ["read"]
}
```

### KV v2 path structure

Remember the KV v2 path structure:

```hcl
# WRONG - This won't work for KV v2!
path "secret/myapp/*" {
  capabilities = ["read"]
}

# CORRECT - Include data/ prefix
path "secret/data/myapp/*" {
  capabilities = ["read"]
}

# For listing secrets
path "secret/metadata/myapp/*" {
  capabilities = ["list"]
}
```

### Common patterns

```hcl
# Full access to application secrets
path "secret/data/myapp/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
path "secret/metadata/myapp/*" {
  capabilities = ["list", "read", "delete"]
}

# Read-only access
path "secret/data/shared/*" {
  capabilities = ["read", "list"]
}
path "secret/metadata/shared/*" {
  capabilities = ["list", "read"]
}

# Environment-specific access
path "secret/data/myapp/+/database" {
  capabilities = ["read"]
}
# Matches: secret/data/myapp/dev/database
#          secret/data/myapp/prod/database
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Managing policies

### Create a policy

```bash
# From a file
vault policy write myapp-read myapp-read.hcl

# Inline (heredoc)
vault policy write myapp-read - <<EOF
path "secret/data/myapp/*" {
  capabilities = ["read", "list"]
}
path "secret/metadata/myapp/*" {
  capabilities = ["list"]
}
EOF
```

### Read a policy

```bash
# View policy content
vault policy read myapp-read

# List all policies
vault policy list
```

### Update a policy

```bash
# Same command as create - overwrites existing
vault policy write myapp-read updated-policy.hcl
```

### Delete a policy

```bash
vault policy delete myapp-read
```

### Format and validate

```bash
# Format HCL file
vault policy fmt policy.hcl

# Validate (implicit during write)
vault policy write test - <<EOF
invalid hcl content
EOF
# Error: failed to parse policy
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Attaching policies

Policies are attached to tokens, and tokens are obtained through authentication.

### At token creation

```bash
# Create token with policies
vault token create -policy="myapp-read" -policy="database-access"

# Token inherits policies from creating token (unless orphan)
vault token create -orphan -policy="limited-policy"
```

### With auth methods

```bash
# Userpass: attach policies to user
vault write auth/userpass/users/alice \
    password="password123" \
    policies="myapp-read,database-access"

# AppRole: attach policies to role
vault write auth/approle/role/myapp \
    token_policies="myapp-read,database-access" \
    token_ttl=1h
```

### View token policies

```bash
# Current token
vault token lookup

# Specific token
vault token lookup <token>

# Check capabilities for a path
vault token capabilities <token> secret/data/myapp/config
# Output: read

# Current token capabilities
vault token capabilities secret/data/myapp/config
```

### Policy precedence

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      POLICY PRECEDENCE                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Token has policies: [policy-a, policy-b, policy-c]                    │
│                                                                          │
│   For each request:                                                     │
│   1. Check all policies for matching paths                              │
│   2. If ANY policy has "deny" → DENIED                                  │
│   3. Otherwise, UNION of all capabilities                               │
│                                                                          │
│   Example:                                                              │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ policy-a: secret/data/myapp/* → [read]                          │   │
│   │ policy-b: secret/data/myapp/* → [update]                        │   │
│   │ policy-c: secret/data/admin/* → [deny]                          │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   Result:                                                               │
│   • secret/data/myapp/* → [read, update] (union)                        │
│   • secret/data/admin/* → DENIED (deny overrides)                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Hands-on lab

### Setup

```bash
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'
vault status
```

### Exercise 1: Create a read-only policy

1. Create the policy:
   ```bash
   vault policy write app-readonly - <<EOF
   # Read-only access to app secrets
   path "secret/data/app/*" {
     capabilities = ["read"]
   }
   path "secret/metadata/app/*" {
     capabilities = ["list", "read"]
   }
   EOF
   ```

2. Verify the policy:
   ```bash
   vault policy read app-readonly
   ```

3. Create test secrets:
   ```bash
   vault kv put secret/app/config setting1="value1" setting2="value2"
   vault kv put secret/app/database password="dbpass"
   ```

4. Create a token with the policy:
   ```bash
   APP_TOKEN=$(vault token create -policy="app-readonly" -format=json | jq -r '.auth.client_token')
   echo "Token: $APP_TOKEN"
   ```

5. Test read access:
   ```bash
   VAULT_TOKEN=$APP_TOKEN vault kv get secret/app/config
   ```

6. Test write access (should fail):
   ```bash
   VAULT_TOKEN=$APP_TOKEN vault kv put secret/app/config setting1="newvalue"
   # Error: permission denied
   ```

### Exercise 2: Create a full-access policy

1. Create the policy:
   ```bash
   vault policy write app-admin - <<EOF
   # Full access to app secrets
   path "secret/data/app/*" {
     capabilities = ["create", "read", "update", "delete", "list"]
   }
   path "secret/metadata/app/*" {
     capabilities = ["list", "read", "delete"]
   }
   EOF
   ```

2. Create a token with both policies:
   ```bash
   ADMIN_TOKEN=$(vault token create -policy="app-admin" -format=json | jq -r '.auth.client_token')
   ```

3. Test full access:
   ```bash
   VAULT_TOKEN=$ADMIN_TOKEN vault kv put secret/app/new-secret key="value"
   VAULT_TOKEN=$ADMIN_TOKEN vault kv get secret/app/new-secret
   VAULT_TOKEN=$ADMIN_TOKEN vault kv delete secret/app/new-secret
   ```

### Exercise 3: Test capability checking

1. Check capabilities for different tokens:
   ```bash
   # Root token
   vault token capabilities secret/data/app/config
   # Output: create, delete, list, read, update

   # Read-only token
   vault token capabilities $APP_TOKEN secret/data/app/config
   # Output: read

   # Admin token
   vault token capabilities $ADMIN_TOKEN secret/data/app/config
   # Output: create, delete, list, read, update
   ```

### Exercise 4: Create a deny policy

1. Create secrets in different paths:
   ```bash
   vault kv put secret/public/info message="public data"
   vault kv put secret/private/sensitive password="secret"
   ```

2. Create a policy with deny:
   ```bash
   vault policy write public-only - <<EOF
   # Allow access to public secrets
   path "secret/data/public/*" {
     capabilities = ["read", "list"]
   }
   path "secret/metadata/public/*" {
     capabilities = ["list"]
   }

   # Explicitly deny private secrets
   path "secret/data/private/*" {
     capabilities = ["deny"]
   }
   EOF
   ```

3. Test the deny:
   ```bash
   PUBLIC_TOKEN=$(vault token create -policy="public-only" -format=json | jq -r '.auth.client_token')

   # This works
   VAULT_TOKEN=$PUBLIC_TOKEN vault kv get secret/public/info

   # This fails
   VAULT_TOKEN=$PUBLIC_TOKEN vault kv get secret/private/sensitive
   # Error: permission denied
   ```

### Exercise 5: Create a userpass user with policies

1. Enable userpass auth:
   ```bash
   vault auth enable userpass 2>/dev/null || true
   ```

2. Create a user with policies:
   ```bash
   vault write auth/userpass/users/developer \
       password="devpass123" \
       policies="app-readonly"
   ```

3. Login as the user:
   ```bash
   vault login -method=userpass username=developer password=devpass123
   ```

4. Test access:
   ```bash
   vault kv get secret/app/config     # Works
   vault kv put secret/app/test x=y   # Fails
   ```

5. Reset to root token:
   ```bash
   vault login root
   ```

### Cleanup

```bash
vault policy delete app-readonly
vault policy delete app-admin
vault policy delete public-only
vault delete auth/userpass/users/developer
vault kv metadata delete secret/app/config
vault kv metadata delete secret/app/database
vault kv metadata delete secret/public/info
vault kv metadata delete secret/private/sensitive
```

---

## Key takeaways

1. **Deny by default** - No access unless explicitly granted

2. **Policies are HCL files** - Define paths and capabilities

3. **Capabilities map to operations**:
   - `create`, `read`, `update`, `delete`, `list`
   - `sudo` for protected paths
   - `deny` to explicitly block

4. **KV v2 requires data/ and metadata/ prefixes** - Common mistake!

5. **Policies are additive** - Multiple policies = union of capabilities

6. **Deny takes precedence** - Overrides all other capabilities

7. **Test with capability checking** - `vault token capabilities`

---

## Module 1 complete!

Congratulations! You've completed all lessons in Module 1. Next steps:

1. Complete the [Module 1 Exercises](./exercises/)
2. Build [Project 1: Password Manager](./project-1-password-manager.md)
3. Take the [Module 1 Quiz](./quiz-module-1.md)

---

[← Previous: Secrets Engines](./04-secrets-engines-basics.md) | [Back to Module 1](./README.md) | [Project 1 →](./project-1-password-manager.md)

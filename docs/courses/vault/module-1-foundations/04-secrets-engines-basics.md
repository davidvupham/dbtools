# Secrets Engines Basics

**[← Back to Module 1](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-1_Foundations-blue)
![Lesson](https://img.shields.io/badge/Lesson-04-purple)

## Learning objectives

By the end of this lesson, you will be able to:

- Explain the difference between KV v1 and KV v2 secrets engines
- Perform CRUD operations on secrets
- Use versioning to manage secret history
- Understand metadata and soft delete vs permanent delete

## Table of contents

- [What are secrets engines?](#what-are-secrets-engines)
- [KV v1 vs KV v2](#kv-v1-vs-kv-v2)
- [KV v2 operations](#kv-v2-operations)
- [Versioning and history](#versioning-and-history)
- [Metadata operations](#metadata-operations)
- [Hands-on lab](#hands-on-lab)
- [Key takeaways](#key-takeaways)

---

## What are secrets engines?

Secrets engines are plugins that store, generate, or encrypt data. Each engine is mounted at a specific path and handles requests to that path.

### Engine types

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      SECRETS ENGINE TYPES                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   STORAGE ENGINES (store secrets you provide)                           │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ • KV (Key-Value) - Store arbitrary secrets                      │   │
│   │ • Cubbyhole - Per-token private storage                         │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   DYNAMIC ENGINES (generate secrets on demand)                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ • Database - Generate database credentials                      │   │
│   │ • AWS - Generate AWS IAM credentials                            │   │
│   │ • SSH - Generate SSH credentials/certificates                   │   │
│   │ • Consul - Generate Consul ACL tokens                           │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   ENCRYPTION ENGINES (encrypt/decrypt without storing)                  │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ • Transit - Encryption as a service                             │   │
│   │ • Transform - Data masking/tokenization                         │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   CERTIFICATE ENGINES                                                   │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ • PKI - Certificate authority                                   │   │
│   │ • SSH - SSH certificate authority                               │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Managing secrets engines

```bash
# List enabled engines
vault secrets list

# Enable a new engine
vault secrets enable -path=myapp kv-v2

# Disable an engine (WARNING: deletes all data!)
vault secrets disable myapp/

# Move an engine
vault secrets move source/ destination/

# Tune engine settings
vault secrets tune -default-lease-ttl=72h secret/
```

[↑ Back to Table of Contents](#table-of-contents)

---

## KV v1 vs KV v2

The KV (Key-Value) secrets engine is the most commonly used engine for storing static secrets.

### Comparison

| Feature | KV v1 | KV v2 |
|---------|-------|-------|
| Versioning | No | Yes (configurable) |
| Soft delete | No | Yes |
| Metadata | No | Yes |
| Check-and-set | No | Yes |
| Undelete | No | Yes |
| API path | `<mount>/key` | `<mount>/data/key` |

### API path differences

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         KV V1 vs V2 PATHS                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   KV V1 (simple paths)                                                  │
│   ────────────────────                                                   │
│   vault kv put kv/myapp password=secret                                 │
│   API: POST /v1/kv/myapp                                                │
│                                                                          │
│   vault kv get kv/myapp                                                 │
│   API: GET /v1/kv/myapp                                                 │
│                                                                          │
│   KV V2 (versioned paths)                                               │
│   ───────────────────────                                                │
│   vault kv put secret/myapp password=secret                             │
│   API: POST /v1/secret/data/myapp                                       │
│                         ^^^^                                            │
│   vault kv get secret/myapp                                             │
│   API: GET /v1/secret/data/myapp                                        │
│                                                                          │
│   Metadata operations:                                                  │
│   API: GET /v1/secret/metadata/myapp                                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### When to use which

**Use KV v1 when:**
- You need simple key-value storage
- Versioning overhead is not acceptable
- Migrating from very old Vault versions

**Use KV v2 when (recommended):**
- You want secret history
- You need soft delete and recovery
- You want metadata tracking
- You need check-and-set for concurrent writes

### Enable KV engines

```bash
# Enable KV v1
vault secrets enable -path=kv-v1 kv

# Enable KV v2
vault secrets enable -path=kv-v2 kv-v2

# Default 'secret/' in dev mode is KV v2
vault secrets list -format=json | jq '."secret/".options'
# Output: {"version": "2"}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## KV v2 operations

### Create (Put)

```bash
# Create a new secret
vault kv put secret/myapp/database \
    username="dbadmin" \
    password="SuperSecret123" \
    host="db.example.com" \
    port="5432"

# Output:
# === Secret Path ===
# secret/data/myapp/database
#
# ======= Metadata =======
# Key                Value
# ---                -----
# created_time       2026-01-21T10:00:00.000000Z
# custom_metadata    <nil>
# deletion_time      n/a
# destroyed          false
# version            1
```

### Read (Get)

```bash
# Read current version
vault kv get secret/myapp/database

# Output:
# === Secret Path ===
# secret/data/myapp/database
#
# ======= Metadata =======
# Key                Value
# ---                -----
# created_time       2026-01-21T10:00:00.000000Z
# version            1
#
# ====== Data ======
# Key         Value
# ---         -----
# host        db.example.com
# password    SuperSecret123
# port        5432
# username    dbadmin

# Read specific field
vault kv get -field=password secret/myapp/database
# Output: SuperSecret123

# Read as JSON
vault kv get -format=json secret/myapp/database | jq '.data.data'

# Read specific version
vault kv get -version=1 secret/myapp/database
```

### Update

```bash
# Update replaces ALL fields (not a merge!)
vault kv put secret/myapp/database \
    username="dbadmin" \
    password="NewPassword456" \
    host="db.example.com" \
    port="5432"

# To merge with existing data, use patch
vault kv patch secret/myapp/database \
    password="UpdatedPassword789"
```

### Delete

```bash
# Soft delete (can be recovered)
vault kv delete secret/myapp/database

# Soft delete specific versions
vault kv delete -versions=1,2 secret/myapp/database

# Undelete (recover soft-deleted)
vault kv undelete -versions=1 secret/myapp/database

# Permanent destroy (cannot be recovered!)
vault kv destroy -versions=1,2 secret/myapp/database

# Delete all versions and metadata
vault kv metadata delete secret/myapp/database
```

### List

```bash
# List keys at a path
vault kv list secret/
vault kv list secret/myapp/
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Versioning and history

KV v2 automatically tracks version history.

### Version behavior

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      VERSION HISTORY                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   secret/myapp/database                                                 │
│                                                                          │
│   Version 1 (created 2026-01-21)                                        │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ password: "InitialPassword"                                     │   │
│   │ username: "admin"                                               │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                     │                                                    │
│                     ▼ vault kv put ...                                  │
│   Version 2 (created 2026-01-22)                                        │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ password: "UpdatedPassword"                                     │   │
│   │ username: "admin"                                               │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                     │                                                    │
│                     ▼ vault kv delete (soft)                            │
│   Version 2 (soft deleted 2026-01-23)                                   │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ [SOFT DELETED - can be undeleted]                               │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                     │                                                    │
│                     ▼ vault kv put ... (creates new version)            │
│   Version 3 (created 2026-01-24) ← Current                              │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ password: "LatestPassword"                                      │   │
│   │ username: "admin"                                               │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Working with versions

```bash
# Read current (latest) version
vault kv get secret/myapp/database

# Read specific version
vault kv get -version=2 secret/myapp/database

# Rollback to old version (creates new version with old data)
# First, get old data
OLD_DATA=$(vault kv get -format=json -version=1 secret/myapp/database | jq '.data.data')

# Then write it as new version
echo $OLD_DATA | vault kv put secret/myapp/database -
```

### Configure version history

```bash
# Set max versions to keep (0 = unlimited)
vault kv metadata put -max-versions=10 secret/myapp/database

# Check current settings
vault kv metadata get secret/myapp/database
```

### Check-and-set (CAS)

Prevent accidental overwrites with check-and-set:

```bash
# Require CAS for all writes to this secret
vault kv metadata put -cas-required=true secret/myapp/database

# Must specify current version when writing
vault kv put -cas=3 secret/myapp/database password=new

# Fails if version doesn't match
# Error: check-and-set parameter did not match the current version
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Metadata operations

KV v2 stores metadata separately from secret data.

### Read metadata

```bash
vault kv metadata get secret/myapp/database

# Output:
# ========== Metadata ==========
# Key                     Value
# ---                     -----
# cas_required            false
# created_time            2026-01-21T10:00:00.000000Z
# current_version         3
# custom_metadata         <nil>
# delete_version_after    0s
# max_versions            0
# oldest_version          1
# updated_time            2026-01-24T10:00:00.000000Z
#
# ====== Version 1 ======
# Key              Value
# ---              -----
# created_time     2026-01-21T10:00:00.000000Z
# deletion_time    n/a
# destroyed        false
#
# ====== Version 2 ======
# ...
```

### Custom metadata

Add non-secret metadata to help organize secrets:

```bash
# Add custom metadata
vault kv metadata put \
    -custom-metadata=owner="platform-team" \
    -custom-metadata=environment="production" \
    -custom-metadata=last-rotated="2026-01-21" \
    secret/myapp/database

# Read custom metadata
vault kv metadata get -format=json secret/myapp/database | jq '.data.custom_metadata'
```

### Configure auto-delete

```bash
# Auto-delete versions after 30 days
vault kv metadata put -delete-version-after=720h secret/myapp/database
```

### Delete all metadata and versions

```bash
# Permanently delete secret and all history
vault kv metadata delete secret/myapp/database
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Hands-on lab

### Setup

Ensure your dev server is running:
```bash
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'
vault status
```

### Exercise 1: Basic CRUD operations

1. **Create** a secret:
   ```bash
   vault kv put secret/lab/webapp \
       db_host="localhost" \
       db_user="webapp" \
       db_pass="s3cr3t" \
       api_key="key-12345"
   ```

2. **Read** the secret:
   ```bash
   vault kv get secret/lab/webapp
   ```

3. **Read** a specific field:
   ```bash
   vault kv get -field=api_key secret/lab/webapp
   ```

4. **Update** (replace all fields):
   ```bash
   vault kv put secret/lab/webapp \
       db_host="prod-db.example.com" \
       db_user="webapp" \
       db_pass="n3w-s3cr3t" \
       api_key="key-12345"
   ```

5. **Patch** (update single field):
   ```bash
   vault kv patch secret/lab/webapp \
       api_key="key-67890"
   ```

6. **List** secrets:
   ```bash
   vault kv list secret/lab/
   ```

### Exercise 2: Versioning

1. Check the current version:
   ```bash
   vault kv metadata get secret/lab/webapp
   ```
   Note the `current_version` and version history.

2. Read an older version:
   ```bash
   vault kv get -version=1 secret/lab/webapp
   ```

3. Compare versions:
   ```bash
   echo "=== Version 1 ==="
   vault kv get -version=1 -field=db_pass secret/lab/webapp

   echo "=== Current ==="
   vault kv get -field=db_pass secret/lab/webapp
   ```

### Exercise 3: Soft delete and recovery

1. Soft delete the secret:
   ```bash
   vault kv delete secret/lab/webapp
   ```

2. Try to read it:
   ```bash
   vault kv get secret/lab/webapp
   # No data found at secret/data/lab/webapp
   ```

3. Check metadata (still exists):
   ```bash
   vault kv metadata get secret/lab/webapp
   ```

4. Undelete:
   ```bash
   vault kv undelete -versions=3 secret/lab/webapp
   ```

5. Verify recovery:
   ```bash
   vault kv get secret/lab/webapp
   ```

### Exercise 4: Custom metadata

1. Add custom metadata:
   ```bash
   vault kv metadata put \
       -custom-metadata=owner="web-team" \
       -custom-metadata=sensitivity="high" \
       -custom-metadata=rotation-policy="30-days" \
       secret/lab/webapp
   ```

2. Read custom metadata:
   ```bash
   vault kv metadata get -format=json secret/lab/webapp | jq '.data.custom_metadata'
   ```

### Exercise 5: Check-and-set

1. Enable CAS requirement:
   ```bash
   vault kv metadata put -cas-required=true secret/lab/webapp
   ```

2. Try to write without CAS:
   ```bash
   vault kv put secret/lab/webapp db_pass="test"
   # Error: check-and-set parameter required
   ```

3. Get current version:
   ```bash
   VERSION=$(vault kv metadata get -format=json secret/lab/webapp | jq -r '.data.current_version')
   echo "Current version: $VERSION"
   ```

4. Write with correct CAS:
   ```bash
   vault kv put -cas=$VERSION secret/lab/webapp \
       db_host="prod-db.example.com" \
       db_user="webapp" \
       db_pass="cas-protected-secret" \
       api_key="key-67890"
   ```

### Cleanup

```bash
vault kv metadata delete secret/lab/webapp
```

---

## Key takeaways

1. **Secrets engines are mounted at paths** - Different engines serve different purposes

2. **KV v2 is recommended** - Versioning, soft delete, and metadata

3. **KV v2 path structure**:
   - Data: `/secret/data/<path>`
   - Metadata: `/secret/metadata/<path>`

4. **Version management**:
   - Automatic version history
   - Configurable retention
   - Soft delete with recovery

5. **Check-and-set prevents race conditions** - Use CAS for concurrent access

6. **Custom metadata helps organization** - Add owner, environment, rotation info

7. **Understand the difference**:
   - `delete` = soft delete (recoverable)
   - `destroy` = permanent delete
   - `metadata delete` = remove everything

---

## Next steps

In the next lesson, you'll learn about Vault policies to control who can access what secrets.

---

[← Previous: Dev Environment](./03-vault-dev-environment.md) | [Back to Module 1](./README.md) | [Next: Policies →](./05-vault-policies-intro.md)

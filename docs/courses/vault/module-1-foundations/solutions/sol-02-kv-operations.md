# Solution 02: KV Operations

**[← Back to Exercises](../exercises/ex-02-kv-operations.md)**

## What this solution demonstrates

- CRUD operations with KV v2
- Versioning behavior
- Soft delete and recovery

## Exercise 2.1: Create secrets

```bash
# Create app1 secret
$ vault kv put secret/exercise/app1 \
    db_host="localhost" \
    db_port="5432" \
    db_user="admin" \
    db_pass="secretpassword"
=== Secret Path ===
secret/data/exercise/app1

======= Metadata =======
Key                Value
---                -----
created_time       2026-01-21T10:00:00.000000Z
custom_metadata    <nil>
deletion_time      n/a
destroyed          false
version            1

# Create app2 secret
$ vault kv put secret/exercise/app2 \
    api_key="sk-test-123456" \
    api_secret="shh-this-is-secret"
```

## Exercise 2.2: Read secrets

```bash
# Full secret
$ vault kv get secret/exercise/app1
====== Data ======
Key         Value
---         -----
db_host     localhost
db_pass     secretpassword
db_port     5432
db_user     admin

# Single field
$ vault kv get -field=db_pass secret/exercise/app1
secretpassword

# JSON output
$ vault kv get -format=json secret/exercise/app1 | jq '.data.data'
{
  "db_host": "localhost",
  "db_pass": "secretpassword",
  "db_port": "5432",
  "db_user": "admin"
}

# List secrets
$ vault kv list secret/exercise/
Keys
----
app1
app2
```

## Exercise 2.3: Update secrets

```bash
# Full update (replaces all fields!)
$ vault kv put secret/exercise/app1 \
    db_host="localhost" \
    db_port="5432" \
    db_user="admin" \
    db_pass="newpassword123"
# Version: 2

# Patch (update single field)
$ vault kv patch secret/exercise/app1 \
    db_pass="patchedpassword"
# Version: 3

# Check version
$ vault kv metadata get secret/exercise/app1 | grep current_version
current_version    3
```

## Exercise 2.4: Versioning

```bash
# Read version 1
$ vault kv get -version=1 secret/exercise/app1
====== Data ======
Key         Value
---         -----
db_pass     secretpassword

# Read version 2
$ vault kv get -version=2 secret/exercise/app1
====== Data ======
Key         Value
---         -----
db_pass     newpassword123

# Compare
$ echo "V1: $(vault kv get -version=1 -field=db_pass secret/exercise/app1)"
V1: secretpassword
$ echo "V2: $(vault kv get -version=2 -field=db_pass secret/exercise/app1)"
V2: newpassword123

# Metadata shows all versions
$ vault kv metadata get secret/exercise/app1
======= Metadata =======
current_version         3
...
====== Version 1 ======
created_time     2026-01-21T10:00:00.000000Z
====== Version 2 ======
created_time     2026-01-21T10:01:00.000000Z
====== Version 3 ======
created_time     2026-01-21T10:02:00.000000Z
```

## Exercise 2.5: Delete and recover

```bash
# Soft delete
$ vault kv delete secret/exercise/app2
Success! Data deleted (if it existed) at: secret/data/exercise/app2

# Try to read (fails)
$ vault kv get secret/exercise/app2
No data found at secret/data/exercise/app2

# Check metadata (still exists)
$ vault kv metadata get secret/exercise/app2
======= Metadata =======
current_version    1
====== Version 1 ======
deletion_time    2026-01-21T10:03:00.000000Z
destroyed        false

# Undelete
$ vault kv undelete -versions=1 secret/exercise/app2
Success! Data written to: secret/undelete/exercise/app2

# Verify recovery
$ vault kv get secret/exercise/app2
====== Data ======
Key          Value
---          -----
api_key      sk-test-123456
api_secret   shh-this-is-secret

# Permanently destroy version 1
$ vault kv destroy -versions=1 secret/exercise/app1
Success! Data written to: secret/destroy/exercise/app1

# Check metadata - version 1 is destroyed
$ vault kv metadata get secret/exercise/app1
====== Version 1 ======
destroyed    true
```

## Common pitfalls

1. Using `put` instead of `patch` - `put` replaces ALL fields
2. Forgetting `data/` prefix in API paths
3. Confusing `delete` (soft) with `destroy` (permanent)

---

[← Back to Exercises](../exercises/ex-02-kv-operations.md)

# Solution 03: Policies

**[← Back to Exercises](../exercises/ex-03-policies.md)**

## What this solution demonstrates

- Policy creation and management
- Path patterns with KV v2
- Testing access control

## Exercise 3.1: View built-in policies

```bash
# List policies
$ vault policy list
default
root

# Read default policy
$ vault policy read default
# Allow tokens to look up their own properties
path "auth/token/lookup-self" {
    capabilities = ["read"]
}

# Allow tokens to renew themselves
path "auth/token/renew-self" {
    capabilities = ["update"]
}

# Allow tokens to revoke themselves
path "auth/token/revoke-self" {
    capabilities = ["update"]
}

# Allow a token to look up its own capabilities on a path
path "sys/capabilities-self" {
    capabilities = ["update"]
}
...
```

**The default policy grants:**
- Token self-management (lookup, renew, revoke)
- Capability checking
- Cubbyhole access (private per-token storage)
- Limited system path access

## Exercise 3.2: Create read-only policy

```bash
$ vault policy write readonly - <<EOF
# Read-only policy for public secrets
path "secret/data/public/*" {
  capabilities = ["read"]
}

path "secret/metadata/public/*" {
  capabilities = ["list", "read"]
}
EOF
Success! Uploaded policy: readonly
```

## Exercise 3.3: Create writer policy

```bash
$ vault policy write writer - <<EOF
# Writer policy for team secrets
path "secret/data/team/*" {
  capabilities = ["create", "read", "update", "delete"]
}

path "secret/metadata/team/*" {
  capabilities = ["list", "read"]
}

# Explicitly deny admin secrets
path "secret/data/team/admin/*" {
  capabilities = ["deny"]
}
EOF
Success! Uploaded policy: writer
```

## Exercise 3.4: Test policies

```bash
# Create test secrets
$ vault kv put secret/public/info message="hello"
$ vault kv put secret/team/config setting="value"
$ vault kv put secret/team/admin/creds password="secret"

# Create tokens
$ READONLY_TOKEN=$(vault token create -policy=readonly -format=json | jq -r '.auth.client_token')
$ WRITER_TOKEN=$(vault token create -policy=writer -format=json | jq -r '.auth.client_token')

# Test readonly token
$ VAULT_TOKEN=$READONLY_TOKEN vault kv get secret/public/info
====== Data ======
Key        Value
---        -----
message    hello
# SUCCESS - can read public

$ VAULT_TOKEN=$READONLY_TOKEN vault kv put secret/public/info message="changed"
Error writing data to secret/data/public/info: permission denied
# DENIED - cannot write

# Test writer token
$ VAULT_TOKEN=$WRITER_TOKEN vault kv get secret/team/config
====== Data ======
Key       Value
---       -----
setting   value
# SUCCESS - can read team

$ VAULT_TOKEN=$WRITER_TOKEN vault kv put secret/team/config setting="new"
Success! Data written to: secret/data/team/config
# SUCCESS - can write team

$ VAULT_TOKEN=$WRITER_TOKEN vault kv get secret/team/admin/creds
Error reading secret/data/team/admin/creds: permission denied
# DENIED - deny rule blocks admin access
```

## Exercise 3.5: Check capabilities

```bash
# Readonly token capabilities
$ vault token capabilities $READONLY_TOKEN secret/data/public/info
read

$ vault token capabilities $READONLY_TOKEN secret/data/public/anything
read

$ vault token capabilities $READONLY_TOKEN secret/data/team/config
deny

# Writer token capabilities
$ vault token capabilities $WRITER_TOKEN secret/data/team/config
create, delete, read, update

$ vault token capabilities $WRITER_TOKEN secret/data/team/admin/creds
deny

$ vault token capabilities $WRITER_TOKEN secret/data/public/info
deny
```

## Summary table

| Token | Path | Expected | Actual |
|-------|------|----------|--------|
| readonly | secret/data/public/info | read | read |
| readonly | secret/data/public/info (write) | deny | deny |
| readonly | secret/data/team/config | deny | deny |
| writer | secret/data/team/config | create,read,update,delete | create,read,update,delete |
| writer | secret/data/team/admin/creds | deny | deny |
| writer | secret/data/public/info | deny | deny |

## Common pitfalls

1. **Forgetting `data/` prefix** - KV v2 requires `secret/data/` not `secret/`
2. **Missing metadata path** - Need separate policy for listing
3. **Deny not taking effect** - Ensure path pattern matches exactly
4. **Glob vs specific path** - `/*` vs `/+` behavior

---

[← Back to Exercises](../exercises/ex-03-policies.md)

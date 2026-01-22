# Solution 01: CLI Basics

**[← Back to Exercises](../exercises/ex-01-cli-basics.md)**

## What this solution demonstrates

- Basic Vault CLI commands
- JSON output parsing
- Environment variable configuration

## Exercise 1.1: Server status

```bash
# Full status
$ vault status
Key             Value
---             -----
Seal Type       shamir
Initialized     true
Sealed          false
Total Shares    1
Threshold       1
Version         1.15.0
Build Date      2023-09-22T16:57:08Z
Storage Type    inmem
Cluster Name    vault-cluster-abc123
Cluster ID      abc123-def456
HA Enabled      false

# Extract sealed value
$ vault status -format=json | jq '.sealed'
false
```

**Field meanings:**
- `Seal Type`: Algorithm for unsealing (shamir or auto-unseal)
- `Initialized`: Whether Vault has been initialized
- `Sealed`: Whether master key is accessible
- `Total Shares`: Shamir shares created
- `Threshold`: Shares needed to unseal
- `Storage Type`: Backend storage (inmem = development)
- `HA Enabled`: High availability mode

## Exercise 1.2: Token information

```bash
$ vault token lookup
Key                 Value
---                 -----
accessor            abc123
creation_time       1705851600
creation_ttl        0
display_name        root
entity_id           n/a
expire_time         <nil>
explicit_max_ttl    0
id                  root
meta                <nil>
num_uses            0
orphan              true
path                auth/token/root
policies            [root]
ttl                 0
type                service
```

**Answers:**
- Policies: `[root]` (superuser access)
- TTL: `0` (never expires - only root tokens have this)

## Exercise 1.3: Secrets engines

```bash
# List engines
$ vault secrets list
Path          Type         Accessor              Description
----          ----         --------              -----------
cubbyhole/    cubbyhole    cubbyhole_abc123     per-token private secret storage
secret/       kv           kv_def456            key-value secret storage
sys/          system       system_ghi789        system endpoints

# KV v2 is at: secret/

# Enable new engine
$ vault secrets enable -path=myengine kv-v2
Success! Enabled the kv-v2 secrets engine at: myengine/

# Verify
$ vault secrets list | grep myengine
myengine/     kv           kv_xyz789            n/a

# Disable
$ vault secrets disable myengine/
Success! Disabled the secrets engine (if it existed) at: myengine/
```

## Exercise 1.4: Auth methods

```bash
# List auth methods
$ vault auth list
Path      Type     Accessor               Description
----      ----     --------               -----------
token/    token    auth_token_abc123      token based credentials

# Default is: token

# Enable userpass
$ vault auth enable userpass
Success! Enabled userpass auth method at: userpass/

# Verify
$ vault auth list | grep userpass
userpass/    userpass    auth_userpass_xyz789    n/a
```

## Exercise 1.5: Environment variables

```bash
# Unset token
$ unset VAULT_TOKEN

# Status still works (no auth needed)
$ vault status
Key             Value
---             -----
Sealed          false
...

# Secret access fails
$ vault kv get secret/test
Error reading secret/data/test: Error making API request.
URL: GET http://127.0.0.1:8200/v1/secret/data/test
Code: 403. Errors:
* permission denied

# Set token back
$ export VAULT_TOKEN='root'
$ vault token lookup
# Works again
```

## Common pitfalls

1. Forgetting to set `VAULT_ADDR` - defaults to https which fails without TLS
2. Using wrong token format - tokens start with `hvs.` or `s.`
3. Not quoting values with special characters

---

[← Back to Exercises](../exercises/ex-01-cli-basics.md)

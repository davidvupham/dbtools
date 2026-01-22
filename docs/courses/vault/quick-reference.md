# Vault Quick Reference

**[← Back to Course Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Vault-blue)

> [!IMPORTANT]
> **Related Docs:** [Glossary](./glossary.md) | [Troubleshooting](./troubleshooting.md)

## Table of contents

- [Server management](#server-management)
- [Authentication](#authentication)
- [KV secrets engine](#kv-secrets-engine)
- [Database secrets engine](#database-secrets-engine)
- [Transit secrets engine](#transit-secrets-engine)
- [PKI secrets engine](#pki-secrets-engine)
- [Policies](#policies)
- [Tokens](#tokens)
- [Audit](#audit)
- [Environment variables](#environment-variables)

---

## Server management

### Start dev server

```bash
# Start in dev mode (in-memory, auto-unsealed)
vault server -dev

# Start with specific address
vault server -dev -dev-listen-address="0.0.0.0:8200"

# Start with specific root token
vault server -dev -dev-root-token-id="root"
```

### Check server status

```bash
# Check if Vault is running and sealed/unsealed
vault status

# Check health via API
curl http://localhost:8200/v1/sys/health
```

### Seal and unseal

```bash
# Seal Vault (requires root token)
vault operator seal

# Unseal Vault (requires unseal key)
vault operator unseal <unseal-key>

# Check seal status
vault status | grep Sealed
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Authentication

### Login methods

```bash
# Token login
vault login <token>

# Userpass login
vault login -method=userpass username=<user>

# AppRole login
vault write auth/approle/login \
    role_id=<role-id> \
    secret_id=<secret-id>

# LDAP login
vault login -method=ldap username=<user>
```

### Enable auth methods

```bash
# Enable userpass
vault auth enable userpass

# Enable AppRole
vault auth enable approle

# Enable LDAP
vault auth enable ldap

# List enabled auth methods
vault auth list
```

### Manage userpass

```bash
# Create user
vault write auth/userpass/users/<username> \
    password=<password> \
    policies=<policy1,policy2>

# Update password
vault write auth/userpass/users/<username> \
    password=<new-password>

# Delete user
vault delete auth/userpass/users/<username>
```

### Manage AppRole

```bash
# Create role
vault write auth/approle/role/<role-name> \
    token_policies="<policy>" \
    token_ttl=1h \
    token_max_ttl=4h

# Get role ID
vault read auth/approle/role/<role-name>/role-id

# Generate secret ID
vault write -f auth/approle/role/<role-name>/secret-id
```

[↑ Back to Table of Contents](#table-of-contents)

---

## KV secrets engine

### KV version 2 (default)

```bash
# Enable KV v2
vault secrets enable -path=secret kv-v2

# Write secret
vault kv put secret/myapp/config \
    username="admin" \
    password="secret123"

# Read secret
vault kv get secret/myapp/config

# Read specific field
vault kv get -field=password secret/myapp/config

# Read specific version
vault kv get -version=2 secret/myapp/config

# List secrets
vault kv list secret/myapp

# Delete secret (soft delete)
vault kv delete secret/myapp/config

# Undelete secret
vault kv undelete -versions=1 secret/myapp/config

# Permanently delete
vault kv destroy -versions=1,2 secret/myapp/config

# Get metadata
vault kv metadata get secret/myapp/config

# Delete all versions
vault kv metadata delete secret/myapp/config
```

### KV version 1

```bash
# Enable KV v1
vault secrets enable -path=kv kv

# Write secret
vault kv put kv/myapp/config password="secret"

# Read secret
vault kv get kv/myapp/config
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Database secrets engine

### Enable and configure

```bash
# Enable database secrets engine
vault secrets enable database

# Configure PostgreSQL connection
vault write database/config/my-postgresql-database \
    plugin_name=postgresql-database-plugin \
    allowed_roles="my-role" \
    connection_url="postgresql://{{username}}:{{password}}@localhost:5432/mydb" \
    username="vault" \
    password="vault-password"
```

### Create roles

```bash
# Create role for dynamic credentials
vault write database/roles/my-role \
    db_name=my-postgresql-database \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
    default_ttl="1h" \
    max_ttl="24h"
```

### Generate credentials

```bash
# Generate dynamic credentials
vault read database/creds/my-role

# Output:
# username: v-approle-my-role-abc123
# password: A1B2C3-random-password
# lease_id: database/creds/my-role/xyz789
# lease_duration: 1h
```

### Manage leases

```bash
# List leases
vault list sys/leases/lookup/database/creds/my-role

# Renew lease
vault lease renew database/creds/my-role/<lease-id>

# Revoke lease
vault lease revoke database/creds/my-role/<lease-id>

# Revoke all leases for role
vault lease revoke -prefix database/creds/my-role
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Transit secrets engine

### Enable and create keys

```bash
# Enable transit
vault secrets enable transit

# Create encryption key
vault write -f transit/keys/my-key

# Create key with specific type
vault write transit/keys/my-key type=aes256-gcm96

# List keys
vault list transit/keys
```

### Encrypt and decrypt

```bash
# Encrypt data (plaintext must be base64 encoded)
vault write transit/encrypt/my-key \
    plaintext=$(echo -n "my secret data" | base64)

# Decrypt data
vault write transit/decrypt/my-key \
    ciphertext="vault:v1:abc123..."

# Decode the result
echo "<base64-plaintext>" | base64 -d
```

### Key rotation

```bash
# Rotate encryption key
vault write -f transit/keys/my-key/rotate

# Set minimum decryption version
vault write transit/keys/my-key/config \
    min_decryption_version=2

# Rewrap ciphertext with latest key
vault write transit/rewrap/my-key \
    ciphertext="vault:v1:abc123..."
```

[↑ Back to Table of Contents](#table-of-contents)

---

## PKI secrets engine

### Enable and configure root CA

```bash
# Enable PKI
vault secrets enable pki

# Set max lease
vault secrets tune -max-lease-ttl=87600h pki

# Generate root CA
vault write pki/root/generate/internal \
    common_name="example.com" \
    ttl=87600h

# Configure URLs
vault write pki/config/urls \
    issuing_certificates="http://vault:8200/v1/pki/ca" \
    crl_distribution_points="http://vault:8200/v1/pki/crl"
```

### Create intermediate CA

```bash
# Enable intermediate PKI
vault secrets enable -path=pki_int pki

# Generate CSR
vault write pki_int/intermediate/generate/internal \
    common_name="example.com Intermediate Authority"

# Sign with root
vault write pki/root/sign-intermediate \
    csr=@csr.pem \
    format=pem_bundle \
    ttl=43800h

# Set signed certificate
vault write pki_int/intermediate/set-signed \
    certificate=@signed_certificate.pem
```

### Issue certificates

```bash
# Create role
vault write pki_int/roles/example-dot-com \
    allowed_domains="example.com" \
    allow_subdomains=true \
    max_ttl="720h"

# Issue certificate
vault write pki_int/issue/example-dot-com \
    common_name="app.example.com" \
    ttl="24h"
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Policies

### Write and manage policies

```bash
# Write policy from file
vault policy write my-policy policy.hcl

# Write policy inline
vault policy write my-policy - <<EOF
path "secret/data/myapp/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
EOF

# Read policy
vault policy read my-policy

# List policies
vault policy list

# Delete policy
vault policy delete my-policy
```

### Common policy patterns

```hcl
# Read-only access
path "secret/data/myapp/*" {
  capabilities = ["read", "list"]
}

# Full access
path "secret/data/myapp/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Deny access
path "secret/data/admin/*" {
  capabilities = ["deny"]
}

# Generate database credentials
path "database/creds/my-role" {
  capabilities = ["read"]
}

# Encrypt/decrypt with transit
path "transit/encrypt/my-key" {
  capabilities = ["update"]
}
path "transit/decrypt/my-key" {
  capabilities = ["update"]
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Tokens

### Create and manage tokens

```bash
# Create token
vault token create

# Create token with policy
vault token create -policy="my-policy"

# Create token with TTL
vault token create -ttl=1h -policy="my-policy"

# Create orphan token
vault token create -orphan -policy="my-policy"

# Lookup current token
vault token lookup

# Lookup specific token
vault token lookup <token>

# Renew token
vault token renew <token>

# Revoke token
vault token revoke <token>
```

### Token capabilities

```bash
# Check what paths a token can access
vault token capabilities <token> secret/data/myapp/config

# Check current token capabilities
vault token capabilities secret/data/myapp/config
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Audit

### Enable audit devices

```bash
# Enable file audit
vault audit enable file file_path=/var/log/vault/audit.log

# Enable syslog audit
vault audit enable syslog

# List audit devices
vault audit list

# Disable audit device
vault audit disable file/
```

### Audit log format (JSON)

```json
{
  "time": "2026-01-21T10:00:00.000000Z",
  "type": "request",
  "auth": {
    "token_type": "service",
    "policies": ["default", "my-policy"]
  },
  "request": {
    "operation": "read",
    "path": "secret/data/myapp/config"
  }
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Environment variables

### Common variables

```bash
# Vault address
export VAULT_ADDR='http://127.0.0.1:8200'

# Vault token (use sparingly - prefer vault login)
export VAULT_TOKEN='s.xxxxxx'

# Skip TLS verification (dev only!)
export VAULT_SKIP_VERIFY=true

# CA certificate path
export VAULT_CACERT='/path/to/ca.pem'

# Client certificate (mTLS)
export VAULT_CLIENT_CERT='/path/to/client.pem'
export VAULT_CLIENT_KEY='/path/to/client-key.pem'

# Namespace (Enterprise)
export VAULT_NAMESPACE='my-namespace'
```

### Configuration file (~/.vault)

```bash
# Default vault configuration
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_FORMAT='json'
```

[↑ Back to Table of Contents](#table-of-contents)

---

## API examples with curl

### Read secret

```bash
curl -s \
    -H "X-Vault-Token: $VAULT_TOKEN" \
    "$VAULT_ADDR/v1/secret/data/myapp/config" | jq
```

### Write secret

```bash
curl -s \
    -H "X-Vault-Token: $VAULT_TOKEN" \
    -X POST \
    -d '{"data": {"password": "secret123"}}' \
    "$VAULT_ADDR/v1/secret/data/myapp/config"
```

### AppRole login

```bash
curl -s \
    -X POST \
    -d '{"role_id": "xxx", "secret_id": "yyy"}' \
    "$VAULT_ADDR/v1/auth/approle/login" | jq -r '.auth.client_token'
```

---

[← Back to Course Index](./README.md)

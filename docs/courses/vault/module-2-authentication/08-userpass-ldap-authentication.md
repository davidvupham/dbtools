# Userpass and LDAP Authentication

**[← Back to Module 2](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-2_Authentication-blue)
![Lesson](https://img.shields.io/badge/Lesson-08-purple)

## Learning objectives

By the end of this lesson, you will be able to:

- Configure userpass authentication for simple user management
- Integrate Vault with LDAP/Active Directory
- Map LDAP groups to Vault policies
- Choose the right auth method for your organization

## Table of contents

- [Human authentication overview](#human-authentication-overview)
- [Userpass authentication](#userpass-authentication)
- [LDAP authentication](#ldap-authentication)
- [Choosing between methods](#choosing-between-methods)
- [Hands-on lab](#hands-on-lab)
- [Key takeaways](#key-takeaways)

---

## Human authentication overview

While AppRole is for machines, humans need different authentication methods:

| Method | Use case | Complexity |
|--------|----------|------------|
| **Userpass** | Small teams, testing | Simple |
| **LDAP** | Enterprise with AD/LDAP | Medium |
| **OIDC** | SSO with identity providers | Medium |
| **GitHub** | Teams using GitHub | Simple |

[↑ Back to Table of Contents](#table-of-contents)

---

## Userpass authentication

### Enable and configure

```bash
# Enable userpass auth
vault auth enable userpass

# Create a user
vault write auth/userpass/users/alice \
    password="alicepassword123" \
    policies="developer"

# Create another user with multiple policies
vault write auth/userpass/users/bob \
    password="bobpassword456" \
    policies="developer,team-lead"
```

### User management

```bash
# List users
vault list auth/userpass/users

# Read user config (password not shown)
vault read auth/userpass/users/alice

# Update password
vault write auth/userpass/users/alice \
    password="newpassword789"

# Update policies
vault write auth/userpass/users/alice \
    policies="developer,senior-dev"

# Delete user
vault delete auth/userpass/users/alice
```

### Login

```bash
# CLI login
vault login -method=userpass username=alice

# API login
curl -s \
    -X POST \
    -d '{"password": "alicepassword123"}' \
    $VAULT_ADDR/v1/auth/userpass/login/alice | jq
```

[↑ Back to Table of Contents](#table-of-contents)

---

## LDAP authentication

### LDAP concepts

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        LDAP INTEGRATION                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   LDAP/Active Directory                      Vault                       │
│   ─────────────────────                      ─────                       │
│                                                                          │
│   ┌─────────────────────┐                   ┌─────────────────────┐    │
│   │ Users               │                   │ Auth Method         │    │
│   │ • alice@corp.com    │  ────────────▶    │ • Verify password   │    │
│   │ • bob@corp.com      │                   │ • Lookup groups     │    │
│   └─────────────────────┘                   └─────────────────────┘    │
│                                                      │                   │
│   ┌─────────────────────┐                           │                   │
│   │ Groups              │                           ▼                   │
│   │ • developers        │                   ┌─────────────────────┐    │
│   │ • ops-team          │  ────────────▶    │ Group-to-Policy     │    │
│   │ • dba-team          │                   │ Mapping             │    │
│   └─────────────────────┘                   │ • developers→dev    │    │
│                                             │ • ops-team→ops      │    │
│                                             │ • dba-team→dba      │    │
│                                             └─────────────────────┘    │
│                                                      │                   │
│                                                      ▼                   │
│                                             ┌─────────────────────┐    │
│                                             │ Token issued with   │    │
│                                             │ mapped policies     │    │
│                                             └─────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Enable LDAP

```bash
vault auth enable ldap
```

### Configure LDAP connection

```bash
# Basic LDAP configuration
vault write auth/ldap/config \
    url="ldaps://ldap.example.com:636" \
    userdn="ou=Users,dc=example,dc=com" \
    userattr="sAMAccountName" \
    groupdn="ou=Groups,dc=example,dc=com" \
    groupattr="cn" \
    binddn="cn=vault-bind,ou=ServiceAccounts,dc=example,dc=com" \
    bindpass="bindpassword" \
    insecure_tls=false \
    certificate=@/path/to/ldap-ca.pem
```

### Active Directory configuration

```bash
vault write auth/ldap/config \
    url="ldaps://dc.corp.example.com:636" \
    userdn="CN=Users,DC=corp,DC=example,DC=com" \
    userattr="sAMAccountName" \
    groupdn="OU=Groups,DC=corp,DC=example,DC=com" \
    groupfilter="(&(objectClass=group)(member:1.2.840.113556.1.4.1941:={{.UserDN}}))" \
    groupattr="cn" \
    upndomain="corp.example.com" \
    binddn="CN=vault-svc,OU=ServiceAccounts,DC=corp,DC=example,DC=com" \
    bindpass="serviceaccountpassword"
```

### Map groups to policies

```bash
# Map LDAP group "developers" to Vault policy "dev-policy"
vault write auth/ldap/groups/developers \
    policies="dev-policy"

# Map multiple policies
vault write auth/ldap/groups/ops-team \
    policies="ops-policy,monitoring-policy"

# Map user directly (overrides group)
vault write auth/ldap/users/alice \
    policies="admin-policy"
```

### LDAP login

```bash
# CLI login
vault login -method=ldap username=alice

# API login
curl -s \
    -X POST \
    -d '{"password": "alicepassword"}' \
    $VAULT_ADDR/v1/auth/ldap/login/alice | jq
```

### LDAP configuration options

| Option | Description |
|--------|-------------|
| `url` | LDAP server URL (ldap:// or ldaps://) |
| `userdn` | Base DN for user search |
| `userattr` | Attribute for username matching |
| `groupdn` | Base DN for group search |
| `groupattr` | Attribute for group name |
| `binddn` | DN for Vault to bind to LDAP |
| `bindpass` | Password for bind DN |
| `upndomain` | UPN domain for AD (user@domain) |
| `groupfilter` | LDAP filter for group membership |

[↑ Back to Table of Contents](#table-of-contents)

---

## Choosing between methods

### Decision matrix

| Criteria | Userpass | LDAP | OIDC |
|----------|----------|------|------|
| **Setup complexity** | Low | Medium | Medium |
| **User management** | In Vault | External | External |
| **MFA support** | No | Depends | Yes |
| **SSO** | No | No | Yes |
| **Scalability** | Small teams | Enterprise | Enterprise |
| **Password policy** | Manual | Centralized | Centralized |

### Recommendations

**Use Userpass when:**
- Small team (< 20 users)
- Development/testing environments
- No existing identity provider
- Quick setup needed

**Use LDAP when:**
- Existing AD/LDAP infrastructure
- Centralized user management required
- Group-based access control needed
- Compliance requires central identity

**Use OIDC when:**
- SSO is required
- MFA is mandatory
- Using identity providers (Okta, Azure AD, etc.)
- Modern authentication flows needed

[↑ Back to Table of Contents](#table-of-contents)

---

## Hands-on lab

### Exercise 1: Userpass setup

1. Enable userpass:
   ```bash
   vault auth enable userpass 2>/dev/null || true
   ```

2. Create policies:
   ```bash
   vault policy write developer - <<EOF
   path "secret/data/dev/*" {
     capabilities = ["create", "read", "update", "delete", "list"]
   }
   EOF

   vault policy write team-lead - <<EOF
   path "secret/data/team/*" {
     capabilities = ["create", "read", "update", "delete", "list"]
   }
   EOF
   ```

3. Create users:
   ```bash
   vault write auth/userpass/users/alice \
       password="alice123" \
       policies="developer"

   vault write auth/userpass/users/bob \
       password="bob456" \
       policies="developer,team-lead"
   ```

4. Test login:
   ```bash
   # Login as Alice
   vault login -method=userpass username=alice password=alice123

   # Check policies
   vault token lookup | grep policies

   # Reset to root
   vault login root
   ```

### Exercise 2: Test access control

1. Create test secrets:
   ```bash
   vault kv put secret/dev/config setting=devvalue
   vault kv put secret/team/config setting=teamvalue
   ```

2. Test as Alice (developer only):
   ```bash
   ALICE_TOKEN=$(vault login -method=userpass -format=json \
       username=alice password=alice123 | jq -r '.auth.client_token')

   # Should work
   VAULT_TOKEN=$ALICE_TOKEN vault kv get secret/dev/config

   # Should fail
   VAULT_TOKEN=$ALICE_TOKEN vault kv get secret/team/config
   ```

3. Test as Bob (developer + team-lead):
   ```bash
   BOB_TOKEN=$(vault login -method=userpass -format=json \
       username=bob password=bob456 | jq -r '.auth.client_token')

   # Should work
   VAULT_TOKEN=$BOB_TOKEN vault kv get secret/dev/config
   VAULT_TOKEN=$BOB_TOKEN vault kv get secret/team/config
   ```

### Exercise 3: Password management

1. Change password:
   ```bash
   vault login root
   vault write auth/userpass/users/alice \
       password="newpassword789"
   ```

2. Test new password:
   ```bash
   vault login -method=userpass username=alice password=newpassword789
   ```

---

## Key takeaways

1. **Userpass for simplicity** - Easy setup, good for small teams

2. **LDAP for enterprise** - Centralized management, group mapping

3. **Group-to-policy mapping** - Map LDAP groups to Vault policies

4. **User overrides** - Individual user mappings override groups

5. **OIDC for SSO** - Modern authentication with identity providers

6. **Choose based on needs** - Consider scale, existing infrastructure, compliance

---

## Next steps

In the next lesson, you'll learn about advanced policy features including templating and parameter constraints.

---

[← Previous: AppRole](./07-approle-authentication.md) | [Back to Module 2](./README.md) | [Next: Advanced Policies →](./09-advanced-policies.md)

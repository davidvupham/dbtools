# Entities and Groups

**[← Back to Module 2](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-2_Authentication-blue)
![Lesson](https://img.shields.io/badge/Lesson-10-purple)

## Learning objectives

By the end of this lesson, you will be able to:

- Explain Vault's identity system
- Create and manage entities
- Configure internal and external groups
- Use identity for unified access control

## Table of contents

- [Identity system overview](#identity-system-overview)
- [Entities](#entities)
- [Groups](#groups)
- [Identity in practice](#identity-in-practice)
- [Hands-on lab](#hands-on-lab)
- [Key takeaways](#key-takeaways)

---

## Identity system overview

Vault's identity system unifies users across multiple authentication methods.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      VAULT IDENTITY SYSTEM                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   AUTH METHODS                      IDENTITY                             │
│   ────────────                      ────────                             │
│                                                                          │
│   ┌──────────────┐                 ┌────────────────────────────────┐   │
│   │   Userpass   │ ──┐             │           ENTITY               │   │
│   │   "alice"    │   │             │   Name: alice                  │   │
│   └──────────────┘   │             │   ID: abc-123-xyz              │   │
│                      │             │   Metadata:                    │   │
│   ┌──────────────┐   ├──────────▶  │     department: engineering   │   │
│   │    LDAP      │   │             │     team: platform            │   │
│   │ "alice@corp" │ ──┤             │   Policies: [user-policy]     │   │
│   └──────────────┘   │             │                                │   │
│                      │             │   Aliases:                     │   │
│   ┌──────────────┐   │             │   ┌────────────────────────┐  │   │
│   │   GitHub     │ ──┘             │   │ userpass: alice        │  │   │
│   │   "alice"    │                 │   │ ldap: alice@corp       │  │   │
│   └──────────────┘                 │   │ github: alice          │  │   │
│                                    │   └────────────────────────┘  │   │
│                                    └────────────────────────────────┘   │
│                                                                          │
│   GROUPS                           GROUP MEMBERSHIP                      │
│   ──────                           ────────────────                      │
│                                                                          │
│   ┌──────────────┐                 ┌────────────────────────────────┐   │
│   │ Internal     │                 │ Entity "alice" is member of:  │   │
│   │  developers  │ ◀─────────────  │   • developers (internal)     │   │
│   └──────────────┘                 │   • eng-team (external/LDAP)  │   │
│                                    └────────────────────────────────┘   │
│   ┌──────────────┐                                                      │
│   │ External     │                                                      │
│   │  eng-team    │ ◀── From LDAP                                       │
│   └──────────────┘                                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Entities

An entity represents a single person or machine identity.

### Create entity

```bash
# Create entity with metadata
vault write identity/entity \
    name="alice" \
    metadata=department="engineering" \
    metadata=team="platform" \
    policies="user-base"
```

### Entity aliases

Aliases link auth method identities to the entity:

```bash
# Get auth method accessor
USERPASS_ACCESSOR=$(vault auth list -format=json | jq -r '.["userpass/"].accessor')

# Create alias
vault write identity/entity-alias \
    name="alice" \
    canonical_id="<entity-id>" \
    mount_accessor="$USERPASS_ACCESSOR"
```

### Manage entities

```bash
# List entities
vault list identity/entity/id

# Read entity
vault read identity/entity/id/<entity-id>

# Read by name
vault read identity/entity/name/alice

# Update entity
vault write identity/entity/id/<entity-id> \
    metadata=department="security"

# Delete entity
vault delete identity/entity/id/<entity-id>
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Groups

Groups organize entities and can have policies attached.

### Internal groups

Manually managed within Vault:

```bash
# Create internal group
vault write identity/group \
    name="developers" \
    policies="dev-secrets" \
    member_entity_ids="<entity-id-1>,<entity-id-2>"
```

### External groups

Synced from auth methods (like LDAP):

```bash
# Create external group (linked to LDAP group)
vault write identity/group \
    name="ldap-engineers" \
    type="external" \
    policies="engineer-policy"

# Get LDAP accessor
LDAP_ACCESSOR=$(vault auth list -format=json | jq -r '.["ldap/"].accessor')

# Create group alias to link to LDAP group
vault write identity/group-alias \
    name="cn=engineers,ou=groups,dc=example,dc=com" \
    mount_accessor="$LDAP_ACCESSOR" \
    canonical_id="<group-id>"
```

### Group hierarchy

Groups can contain other groups:

```bash
# Create parent group
vault write identity/group \
    name="all-engineering" \
    policies="eng-base" \
    member_group_ids="<developers-group-id>,<sre-group-id>"
```

### Manage groups

```bash
# List groups
vault list identity/group/id

# Read group
vault read identity/group/id/<group-id>
vault read identity/group/name/developers

# Add member to group
vault write identity/group/id/<group-id> \
    member_entity_ids="<existing>,<new-entity-id>"

# Delete group
vault delete identity/group/id/<group-id>
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Identity in practice

### Policy inheritance

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      POLICY INHERITANCE                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   When Alice authenticates, her token gets policies from:               │
│                                                                          │
│   1. Auth method (userpass user policies)                               │
│      └── policies: [userpass-base]                                      │
│                                                                          │
│   2. Entity direct policies                                             │
│      └── policies: [user-alice]                                         │
│                                                                          │
│   3. Group memberships                                                  │
│      ├── developers → policies: [dev-secrets]                          │
│      └── platform-team → policies: [platform-access]                   │
│                                                                          │
│   4. Parent group memberships                                           │
│      └── all-engineering → policies: [eng-base]                        │
│                                                                          │
│   RESULT: Token has ALL policies combined:                              │
│   [userpass-base, user-alice, dev-secrets, platform-access, eng-base]  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Use case: Multi-auth user

Alice uses both userpass and LDAP:

```bash
# Create entity
ALICE_ENTITY=$(vault write -format=json identity/entity \
    name="alice" \
    policies="user-base" | jq -r '.data.id')

# Link userpass
USERPASS_ACCESSOR=$(vault auth list -format=json | jq -r '.["userpass/"].accessor')
vault write identity/entity-alias \
    name="alice" \
    canonical_id="$ALICE_ENTITY" \
    mount_accessor="$USERPASS_ACCESSOR"

# Link LDAP
LDAP_ACCESSOR=$(vault auth list -format=json | jq -r '.["ldap/"].accessor')
vault write identity/entity-alias \
    name="alice@corp.example.com" \
    canonical_id="$ALICE_ENTITY" \
    mount_accessor="$LDAP_ACCESSOR"

# Now Alice gets same identity whether logging in via userpass or LDAP
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Hands-on lab

### Exercise 1: Create entities and groups

```bash
# Enable userpass
vault auth enable userpass 2>/dev/null || true

# Create users
vault write auth/userpass/users/alice password="alice123"
vault write auth/userpass/users/bob password="bob456"
vault write auth/userpass/users/carol password="carol789"

# Get accessor
ACCESSOR=$(vault auth list -format=json | jq -r '.["userpass/"].accessor')

# Create entities
ALICE_ID=$(vault write -format=json identity/entity name="alice" \
    metadata=department="engineering" | jq -r '.data.id')
BOB_ID=$(vault write -format=json identity/entity name="bob" \
    metadata=department="engineering" | jq -r '.data.id')
CAROL_ID=$(vault write -format=json identity/entity name="carol" \
    metadata=department="finance" | jq -r '.data.id')

# Create aliases
vault write identity/entity-alias name="alice" canonical_id="$ALICE_ID" mount_accessor="$ACCESSOR"
vault write identity/entity-alias name="bob" canonical_id="$BOB_ID" mount_accessor="$ACCESSOR"
vault write identity/entity-alias name="carol" canonical_id="$CAROL_ID" mount_accessor="$ACCESSOR"

# Create engineering group
ENG_GROUP=$(vault write -format=json identity/group \
    name="engineering" \
    policies="eng-policy" \
    member_entity_ids="$ALICE_ID,$BOB_ID" | jq -r '.data.id')

# Create finance group
FIN_GROUP=$(vault write -format=json identity/group \
    name="finance" \
    policies="finance-policy" \
    member_entity_ids="$CAROL_ID" | jq -r '.data.id')

echo "Alice Entity: $ALICE_ID"
echo "Engineering Group: $ENG_GROUP"
```

### Exercise 2: Create policies and test

```bash
# Create policies
vault policy write eng-policy - <<EOF
path "secret/data/engineering/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
EOF

vault policy write finance-policy - <<EOF
path "secret/data/finance/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
EOF

# Create test secrets
vault kv put secret/engineering/config env=dev
vault kv put secret/finance/budget year=2026

# Test as Alice (engineering)
ALICE_TOKEN=$(vault login -method=userpass -format=json username=alice password=alice123 | jq -r '.auth.client_token')

VAULT_TOKEN=$ALICE_TOKEN vault kv get secret/engineering/config  # Should work
VAULT_TOKEN=$ALICE_TOKEN vault kv get secret/finance/budget      # Should fail

# Test as Carol (finance)
CAROL_TOKEN=$(vault login -method=userpass -format=json username=carol password=carol789 | jq -r '.auth.client_token')

VAULT_TOKEN=$CAROL_TOKEN vault kv get secret/finance/budget       # Should work
VAULT_TOKEN=$CAROL_TOKEN vault kv get secret/engineering/config   # Should fail
```

### Exercise 3: Add member to group

```bash
vault login root

# Add Carol to engineering (dual membership)
vault write identity/group/name/engineering \
    member_entity_ids="$ALICE_ID,$BOB_ID,$CAROL_ID"

# Now Carol has both policies
CAROL_TOKEN=$(vault login -method=userpass -format=json username=carol password=carol789 | jq -r '.auth.client_token')

VAULT_TOKEN=$CAROL_TOKEN vault kv get secret/finance/budget       # Should work
VAULT_TOKEN=$CAROL_TOKEN vault kv get secret/engineering/config   # Should now work!
```

---

## Key takeaways

1. **Entities represent identities** - One entity per person/machine
2. **Aliases link auth methods** - Same entity across multiple auth methods
3. **Internal groups** - Manually managed in Vault
4. **External groups** - Synced from LDAP, OIDC, etc.
5. **Policies are inherited** - From entity, groups, and parent groups
6. **Metadata enables templating** - Use in templated policies

---

## Module 2 complete!

Congratulations! You've completed Module 2. Next steps:

1. Complete [Project 2: Multi-User Secret Store](./project-2-multi-user-store.md)
2. Take the [Module 2 Quiz](./quiz-module-2.md)
3. Start [Module 3: Dynamic Secrets](../module-3-dynamic-secrets/README.md)

---

[← Previous: Advanced Policies](./09-advanced-policies.md) | [Back to Module 2](./README.md) | [Project 2 →](./project-2-multi-user-store.md)

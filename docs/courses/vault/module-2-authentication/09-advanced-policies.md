# Advanced Policies

**[← Back to Module 2](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-2_Authentication-blue)
![Lesson](https://img.shields.io/badge/Lesson-09-purple)

## Learning objectives

By the end of this lesson, you will be able to:

- Use templated policies with identity attributes
- Configure parameter constraints
- Implement fine-grained time-based access
- Design multi-tenant policy architectures

## Table of contents

- [Policy templating](#policy-templating)
- [Parameter constraints](#parameter-constraints)
- [Sentinel policies](#sentinel-policies)
- [Multi-tenant patterns](#multi-tenant-patterns)
- [Hands-on lab](#hands-on-lab)
- [Key takeaways](#key-takeaways)

---

## Policy templating

Templated policies use identity information to dynamically construct paths.

### Available template parameters

| Parameter | Description |
|-----------|-------------|
| `{{identity.entity.id}}` | Entity UUID |
| `{{identity.entity.name}}` | Entity name |
| `{{identity.entity.aliases.auth_method.name}}` | Alias name |
| `{{identity.entity.metadata.key}}` | Entity metadata |
| `{{identity.groups.ids.group_id.name}}` | Group name by ID |
| `{{identity.groups.names.group_name.id}}` | Group ID by name |

### Example: Per-user secrets

```hcl
# Each user gets their own secret space
path "secret/data/users/{{identity.entity.name}}/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "secret/metadata/users/{{identity.entity.name}}/*" {
  capabilities = ["list", "read", "delete"]
}
```

### Example: Per-team secrets

```hcl
# Users can access secrets for their team
path "secret/data/teams/{{identity.groups.names.team.id}}/*" {
  capabilities = ["read", "list"]
}
```

### Example: Using metadata

```hcl
# Access based on department metadata
path "secret/data/departments/{{identity.entity.metadata.department}}/*" {
  capabilities = ["read"]
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Parameter constraints

Control what values can be written to secrets.

### Required parameters

```hcl
# Require specific keys to be present
path "secret/data/apps/*" {
  capabilities = ["create", "update"]
  required_parameters = ["owner", "environment"]
}
```

### Allowed parameters

```hcl
# Only allow specific key-value combinations
path "secret/data/config/*" {
  capabilities = ["create", "update"]
  allowed_parameters = {
    "environment" = ["dev", "staging", "prod"]
    "region" = ["us-east-1", "us-west-2", "eu-west-1"]
  }
}
```

### Denied parameters

```hcl
# Prevent certain keys from being set
path "secret/data/apps/*" {
  capabilities = ["create", "update"]
  denied_parameters = {
    "admin_password" = ["*"]
    "root_key" = ["*"]
  }
}
```

### Min/Max wrapping TTL

```hcl
# Control response wrapping
path "secret/data/sensitive/*" {
  capabilities = ["read"]
  min_wrapping_ttl = "100s"
  max_wrapping_ttl = "300s"
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Sentinel policies

> [!NOTE]
> Sentinel is a Vault Enterprise feature.

Sentinel provides fine-grained, logic-based policy control:

```python
# Example: Only allow access during business hours
import "time"

main = rule {
  time.hour >= 9 and time.hour < 17
}
```

```python
# Example: Require MFA for production secrets
import "mfa"
import "strings"

main = rule {
  strings.has_prefix(request.path, "secret/data/prod") implies mfa.validate()
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Multi-tenant patterns

### Pattern 1: Path-based isolation

```hcl
# Tenant A policy
path "secret/data/tenants/tenant-a/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Tenant B policy (separate)
path "secret/data/tenants/tenant-b/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
```

### Pattern 2: Template-based isolation

```hcl
# Single policy for all tenants
path "secret/data/tenants/{{identity.entity.metadata.tenant_id}}/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
```

### Pattern 3: Namespace isolation (Enterprise)

```hcl
# Each tenant gets a namespace
# Policies are scoped to namespace automatically
path "secret/data/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
```

### Pattern 4: Role-based access

```hcl
# Admin role - full access
path "secret/data/{{identity.entity.metadata.tenant}}/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Reader role - read only
path "secret/data/{{identity.entity.metadata.tenant}}/*" {
  capabilities = ["read", "list"]
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Hands-on lab

### Setup

```bash
export VAULT_ADDR='http://127.0.0.1:8200'
vault login root
```

### Exercise 1: Templated policy

1. Create an entity and alias:
   ```bash
   # Enable userpass if not already
   vault auth enable userpass 2>/dev/null || true

   # Create entity
   ENTITY_ID=$(vault write -format=json identity/entity \
       name="alice" \
       metadata=department="engineering" \
       metadata=team="platform" | jq -r '.data.id')

   # Get userpass accessor
   ACCESSOR=$(vault auth list -format=json | jq -r '.["userpass/"].accessor')

   # Create alias
   vault write identity/entity-alias \
       name="alice" \
       canonical_id="$ENTITY_ID" \
       mount_accessor="$ACCESSOR"

   # Create userpass user
   vault write auth/userpass/users/alice \
       password="alice123"
   ```

2. Create templated policy:
   ```bash
   vault policy write user-workspace - <<EOF
   # Access own workspace
   path "secret/data/users/{{identity.entity.name}}/*" {
     capabilities = ["create", "read", "update", "delete", "list"]
   }
   path "secret/metadata/users/{{identity.entity.name}}/*" {
     capabilities = ["list", "read"]
   }

   # Read team secrets
   path "secret/data/teams/{{identity.entity.metadata.team}}/*" {
     capabilities = ["read", "list"]
   }
   EOF
   ```

3. Assign policy to entity:
   ```bash
   vault write identity/entity/id/$ENTITY_ID \
       policies="user-workspace"
   ```

4. Test:
   ```bash
   # Login as alice
   ALICE_TOKEN=$(vault login -method=userpass -format=json \
       username=alice password=alice123 | jq -r '.auth.client_token')

   # Create user secret
   VAULT_TOKEN=$ALICE_TOKEN vault kv put secret/users/alice/myconfig key=value

   # Read it back
   VAULT_TOKEN=$ALICE_TOKEN vault kv get secret/users/alice/myconfig

   # Try to access another user's workspace (should fail)
   VAULT_TOKEN=$ALICE_TOKEN vault kv get secret/users/bob/config
   ```

### Exercise 2: Parameter constraints

1. Create policy with constraints:
   ```bash
   vault policy write constrained-write - <<EOF
   path "secret/data/constrained/*" {
     capabilities = ["create", "update", "read"]
     required_parameters = ["owner"]
     allowed_parameters = {
       "environment" = ["dev", "staging", "prod"]
       "owner" = []
       "value" = []
     }
     denied_parameters = {
       "password" = ["*"]
     }
   }
   EOF
   ```

2. Create test token:
   ```bash
   CONSTRAINED_TOKEN=$(vault token create -policy=constrained-write -format=json | jq -r '.auth.client_token')
   ```

3. Test constraints:
   ```bash
   # Missing required parameter (should fail)
   VAULT_TOKEN=$CONSTRAINED_TOKEN vault kv put secret/constrained/test1 value=x
   # Error: missing required parameters: [owner]

   # Invalid environment value (should fail)
   VAULT_TOKEN=$CONSTRAINED_TOKEN vault kv put secret/constrained/test2 owner=alice environment=invalid
   # Error: parameter "environment" cannot be "invalid"

   # Denied parameter (should fail)
   VAULT_TOKEN=$CONSTRAINED_TOKEN vault kv put secret/constrained/test3 owner=alice password=secret
   # Error: parameter "password" not allowed

   # Valid request (should succeed)
   VAULT_TOKEN=$CONSTRAINED_TOKEN vault kv put secret/constrained/test4 owner=alice environment=dev value=myvalue
   ```

---

## Key takeaways

1. **Templated policies** - Use identity attributes for dynamic paths
2. **Parameter constraints** - Control what can be written
3. **Required parameters** - Enforce metadata presence
4. **Allowed/denied values** - Restrict parameter values
5. **Multi-tenant patterns** - Path-based, template-based, or namespace isolation
6. **Sentinel** - Advanced logic-based policies (Enterprise)

---

[← Previous: Userpass & LDAP](./08-userpass-ldap-authentication.md) | [Back to Module 2](./README.md) | [Next: Entities & Groups →](./10-entity-groups.md)

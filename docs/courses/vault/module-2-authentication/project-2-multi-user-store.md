# Project 2: Multi-User Secret Store

**[← Back to Module 2](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-2_Authentication-blue)
![Type](https://img.shields.io/badge/Type-Project-orange)

## Overview

Build a multi-user secret store supporting multiple teams with different access levels. This project reinforces authentication methods, policies, and identity management.

## Scenario

You're setting up secrets management for a company with three teams:

- **Platform Team**: Manages infrastructure secrets, full access to platform secrets
- **Backend Team**: Develops applications, access to their app secrets
- **Data Team**: Manages data pipelines, access to database credentials

## Requirements

### Functional requirements

1. **User management**
   - Users authenticate via userpass
   - Each user belongs to one or more teams
   - Users have personal secret workspaces

2. **Team secrets**
   - Each team has a shared secret space
   - Team members can read/write team secrets
   - Teams cannot access other teams' secrets

3. **Personal workspaces**
   - Each user gets a personal secret space
   - Only the user can access their workspace

4. **Admin access**
   - Admins can access all secrets
   - Admins can manage users and policies

### Technical requirements

- Use entities and groups for identity management
- Use templated policies where appropriate
- Implement role-based access control
- Create at least 9 users (3 per team) + 1 admin

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      SECRET STORE ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   secret/                                                               │
│   ├── shared/                  # Cross-team shared secrets              │
│   │   └── company-wide/        # (admin write, all read)                │
│   │                                                                      │
│   ├── teams/                   # Team-specific secrets                  │
│   │   ├── platform/            # Platform team only                     │
│   │   ├── backend/             # Backend team only                      │
│   │   └── data/                # Data team only                         │
│   │                                                                      │
│   └── users/                   # Personal workspaces                    │
│       ├── alice/               # Alice's private secrets                │
│       ├── bob/                 # Bob's private secrets                  │
│       └── ...                                                           │
│                                                                          │
│   GROUPS                       POLICIES                                 │
│   ──────                       ────────                                  │
│   platform-team     ────────▶  platform-policy                          │
│   backend-team      ────────▶  backend-policy                           │
│   data-team         ────────▶  data-policy                              │
│   admins            ────────▶  admin-policy                             │
│   all-users         ────────▶  user-base-policy                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Implementation guide

### Step 1: Create base policies

```hcl
# policies/user-base.hcl - All users get this
path "secret/data/users/{{identity.entity.name}}/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
path "secret/metadata/users/{{identity.entity.name}}/*" {
  capabilities = ["list", "read", "delete"]
}
path "secret/data/shared/company-wide/*" {
  capabilities = ["read", "list"]
}
```

### Step 2: Create team policies

```hcl
# policies/platform-team.hcl
path "secret/data/teams/platform/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
path "secret/metadata/teams/platform/*" {
  capabilities = ["list", "read", "delete"]
}
```

### Step 3: Create setup script

```bash
#!/bin/bash
# setup-secret-store.sh

# Enable auth
vault auth enable userpass

# Create policies
vault policy write user-base policies/user-base.hcl
vault policy write platform-team policies/platform-team.hcl
vault policy write backend-team policies/backend-team.hcl
vault policy write data-team policies/data-team.hcl
vault policy write admin policies/admin.hcl

# Create groups
PLATFORM_GROUP=$(vault write -format=json identity/group \
    name="platform-team" policies="platform-team" | jq -r '.data.id')

# Create users and entities
for user in alice bob carol; do
    # Create userpass user
    vault write auth/userpass/users/$user password="${user}pass"

    # Create entity
    ENTITY_ID=$(vault write -format=json identity/entity \
        name="$user" policies="user-base" | jq -r '.data.id')

    # Link alias
    vault write identity/entity-alias \
        name="$user" \
        canonical_id="$ENTITY_ID" \
        mount_accessor="$ACCESSOR"
done
```

## Deliverables

1. **Policies** - All policy HCL files
2. **Setup script** - Automated setup
3. **Test script** - Verify access control
4. **Documentation** - User guide

## Evaluation criteria

| Criterion | Points |
|-----------|--------|
| Policies correctly restrict access | 30 |
| Identity (entities/groups) setup | 25 |
| Templated policies used | 20 |
| Testing demonstrates access control | 15 |
| Documentation | 10 |
| **Total** | 100 |

## Testing checklist

- [ ] Platform team member can access platform secrets
- [ ] Platform team member cannot access backend secrets
- [ ] Each user can access only their personal workspace
- [ ] Admin can access all secrets
- [ ] Shared company secrets readable by all
- [ ] Cross-team access is blocked

---

[← Back to Module 2](./README.md) | [Take Quiz →](./quiz-module-2.md)

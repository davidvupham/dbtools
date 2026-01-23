# gds-ad

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

Active Directory integration library for GDS services. Provides a Pythonic interface to Active Directory for common operations like querying user group memberships and managing group members.

## Requirements

- Python 3.9+
- `ldap3` library (installed automatically)
- Optional: `gssapi` for Kerberos authentication

## Installation

The package is part of the GDS monorepo and is installed with UV:

```bash
uv sync
```

For Kerberos support:

```bash
uv pip install gds-ad[kerberos]
```

## Quick start

```python
from gds_ad import ActiveDirectoryClient

# Connect with username/password
client = ActiveDirectoryClient(
    server="ldap://dc.example.com",
    base_dn="DC=example,DC=com",
    username="MYDOMAIN\\admin",
    password="secret123"
)

# Use context manager for automatic connection handling
with client:
    # Get all security groups for a user
    groups = client.get_user_group_membership("jdoe")
    for group in groups:
        print(f"{group.name}: {group.distinguished_name}")

    # Get only SQL-related groups (PowerShell-style wildcards)
    sql_groups = client.get_user_group_membership("jdoe", filter="SQL*")

    # Remove user from groups
    result = client.remove_user_group_membership("jdoe", ["SQL_Admin"])
```

## Public functions

### ActiveDirectoryClient

The main client class for AD operations.

**Constructor parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| server | str | Yes | - | LDAP server URL (e.g., `ldap://dc.example.com` or `ldaps://dc.example.com:636`) |
| base_dn | str | Yes | - | Base DN for searches (e.g., `DC=example,DC=com`) |
| auth | AuthStrategy | No | - | Authentication strategy object |
| username | str | No | - | Bind username (alternative to auth) |
| password | str | No | - | Bind password (alternative to auth) |
| use_ssl | bool | No | Auto | Use SSL/TLS (auto-detected from URL) |
| connect_timeout | int | No | 10 | Connection timeout in seconds |

### get_user_group_membership

Get the groups a user is a member of. Equivalent to PowerShell's `Get-GdsUserGroupMembership`.

```python
groups = client.get_user_group_membership(
    username="jdoe",
    filter="SQL*",        # Optional: PowerShell-style wildcard
    security_only=True    # Default: only Security groups, not Distribution
)
```

**Returns:** `list[ADGroup]`

### remove_user_group_membership

Remove a user from one or more groups. Equivalent to PowerShell's `Remove-GdsUserGroupMembership`.

```python
# Remove from single group
result = client.remove_user_group_membership("jdoe", "SQL_Admin")

# Remove from multiple groups
result = client.remove_user_group_membership("jdoe", ["SQL_Admin", "SQL_Reader"])

# Remove from ADGroup objects (e.g., from get_user_group_membership)
sql_groups = client.get_user_group_membership("jdoe", filter="SQL*")
result = client.remove_user_group_membership("jdoe", sql_groups)
```

**Returns:** `dict[str, bool]` - Dictionary mapping group names to success status.

### search_users

Search for users in Active Directory.

```python
users = client.search_users(filter="j*")  # All users starting with 'j'
```

### search_groups

Search for groups in Active Directory.

```python
groups = client.search_groups(filter="SQL*", security_only=True)
```

## Authentication strategies

### SimpleBindAuth

Standard username/password authentication.

```python
from gds_ad import ActiveDirectoryClient, SimpleBindAuth

auth = SimpleBindAuth(
    username="MYDOMAIN\\svc_account",
    password="secret123"
)
client = ActiveDirectoryClient(
    server="ldap://dc.example.com",
    base_dn="DC=example,DC=com",
    auth=auth
)
```

### EnvironmentAuth

Read credentials from environment variables.

```bash
export AD_USERNAME="MYDOMAIN\\svc_account"
export AD_PASSWORD="secret123"
```

```python
from gds_ad import ActiveDirectoryClient, EnvironmentAuth

client = ActiveDirectoryClient(
    server="ldap://dc.example.com",
    base_dn="DC=example,DC=com",
    auth=EnvironmentAuth()
)
```

### KerberosAuth

Windows integrated authentication using Kerberos.

```python
from gds_ad import ActiveDirectoryClient, KerberosAuth

client = ActiveDirectoryClient(
    server="ldap://dc.example.com",
    base_dn="DC=example,DC=com",
    auth=KerberosAuth()  # Uses current user's Kerberos ticket
)
```

## Data models

### ADGroup

Represents an Active Directory group.

| Attribute | Type | Description |
|-----------|------|-------------|
| name | str | Group's SAM account name |
| distinguished_name | str | Full LDAP DN |
| category | GroupCategory | SECURITY or DISTRIBUTION |
| scope | GroupScope | DOMAIN_LOCAL, GLOBAL, or UNIVERSAL |
| description | str | Group description |

### ADUser

Represents an Active Directory user.

| Attribute | Type | Description |
|-----------|------|-------------|
| username | str | User's SAM account name |
| distinguished_name | str | Full LDAP DN |
| display_name | str | User's display name |
| email | str | User's email address |
| enabled | bool | Whether account is enabled |

## Exception handling

```python
from gds_ad import (
    ActiveDirectoryClient,
    ActiveDirectoryError,      # Base exception
    ADConnectionError,         # Connection failures
    ADAuthenticationError,     # Authentication failures
    ADSearchError,             # Search failures
    ADModificationError,       # Modification failures
    ADObjectNotFoundError,     # Object not found
    ADConfigurationError,      # Configuration errors
)

try:
    with ActiveDirectoryClient(...) as client:
        groups = client.get_user_group_membership("jdoe")
except ADAuthenticationError as e:
    print(f"Authentication failed: {e}")
except ADObjectNotFoundError as e:
    print(f"User not found: {e}")
except ActiveDirectoryError as e:
    print(f"AD operation failed: {e}")
```

## Testing

Tests use pytest and mock the ldap3 library for unit testing without AD access.

```bash
# Run all tests
pytest python/gds_ad/tests/ -v

# Run with coverage
pytest python/gds_ad/tests/ -v --cov=gds_ad
```

## PowerShell equivalent

This package provides Python equivalents to the PowerShell `GDS.ActiveDirectory` module functions:

| PowerShell | Python |
|------------|--------|
| `Get-GdsUserGroupMembership -UserName "jdoe" -Filter "SQL*"` | `client.get_user_group_membership("jdoe", filter="SQL*")` |
| `Remove-GdsUserGroupMembership -UserName "jdoe" -Group "SQL_Admin"` | `client.remove_user_group_membership("jdoe", ["SQL_Admin"])` |
| Pipeline: `Get-GdsUserGroupMembership ... \| Remove-GdsUserGroupMembership ...` | `groups = client.get_user_group_membership(...); client.remove_user_group_membership("jdoe", groups)` |

## Related documentation

- [PowerShell GDS.ActiveDirectory module](../../PowerShell/Modules/GDS.ActiveDirectory/README.md)

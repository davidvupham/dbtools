# GDS.ActiveDirectory module

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

## Overview

PowerShell module for Active Directory management operations. Provides functions for exporting AD objects to databases and managing user group memberships.

## Requirements

- PowerShell 5.1+ (PowerShell 7+ recommended)
- Active Directory module (available on Windows with RSAT installed)
- GDS.Logging module

## Installation

The module is automatically loaded when imported from the repository:

```powershell
Import-Module /path/to/PowerShell/Modules/GDS.ActiveDirectory
```

## Public functions

### Get-GdsUserGroupMembership

Lists security groups a user is a member of, with optional name filtering.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| UserName | String | Yes | - | The SAM account name of the user |
| Filter | String | No | `*` | Wildcard filter for group names |

**Examples:**

```powershell
# List all security groups for a user
Get-GdsUserGroupMembership -UserName "jdoe"

# List only SQL-related groups
Get-GdsUserGroupMembership -UserName "jdoe" -Filter "SQL*"

# Pipe results to other commands
Get-GdsUserGroupMembership -UserName "jdoe" -Filter "SQL*" | Select-Object Name, DistinguishedName
```

### Remove-GdsUserGroupMembership

Removes a user from one or more Active Directory security groups. Supports `-WhatIf` and `-Confirm` for safe operations.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| UserName | String | Yes | - | The SAM account name of the user |
| Group | Object[] | Yes | - | Group name(s) or ADGroup objects (supports pipeline) |

**Examples:**

```powershell
# Remove user from a single group
Remove-GdsUserGroupMembership -UserName "jdoe" -Group "SQLdb_Readers"

# Remove user from multiple groups
Remove-GdsUserGroupMembership -UserName "jdoe" -Group "SQL_Admin", "SQL_Reader"

# Preview changes without executing
Remove-GdsUserGroupMembership -UserName "jdoe" -Group "SQL_Admin" -WhatIf

# Pipeline: Remove user from all SQL groups
Get-GdsUserGroupMembership -UserName "jdoe" -Filter "SQL*" | Remove-GdsUserGroupMembership -UserName "jdoe"
```

### Export-ADObjectsToDatabase

Exports Active Directory objects (users and groups) to a SQL Server database.

See [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) for detailed documentation.

## Testing

Tests use Pester 5.0+ and can run on Linux without the ActiveDirectory module by using stub functions for mocking.

```powershell
# Run all module tests
Invoke-Pester -Path ./tests/

# Run specific test file
Invoke-Pester -Path ./tests/UserGroupMembership.Tests.ps1 -Output Detailed
```

## Related documentation

- [Implementation plan](./IMPLEMENTATION_PLAN.md) - Architecture and design details
- [Bulk insert design](./BULK_INSERT_DESIGN.md) - Database bulk operations
- [Extended properties design](./EXTENDED_PROPERTIES_DESIGN.md) - AD extended attributes

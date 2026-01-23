# Active Directory to Database Export - Implementation Plan

## Overview
This document outlines the implementation plan for the `GDS.ActiveDirectory` module. It originally focused on exporting AD objects to a database but now includes direct AD group membership management functions for PowerShell 7/Linux environments.

## Module Location
**Module**: `GDS.ActiveDirectory`
**Location**: `/workspaces/dbtools/PowerShell/Modules/GDS.ActiveDirectory/`

## Recent Updates: Group Membership Functions (PowerShell 7 / Linux)

### Goal
Implement `Get-GdsUserGroupMembership` and `Remove-GdsUserGroupMembership` to manage security group memberships, supporting pipeline input and filtering. These must work in a PowerShell 7 environment on Linux, where the native `ActiveDirectory` module is not locally available during development/testing.

### Architecture Changes

#### Public Functions
- `Get-GdsUserGroupMembership.ps1`: Wraps `Get-ADPrincipalGroupMembership`.
- `Remove-GdsUserGroupMembership.ps1`: Wraps `Remove-ADGroupMember`.

#### Testing Strategy
- **Pester Mocks**: Since `ActiveDirectory` module cannot be loaded on Linux without RSAT, we mock the underlying calls (`Get-ADPrincipalGroupMembership`, `Remove-ADGroupMember`) to verify logic (filtering, pipeline handling, error catching).

### Implementation Steps

#### Step 1: `Get-GdsUserGroupMembership`
- **Parameters**: `UserName` (Mandatory), `Filter` (Optional, default `*`).
- **Logic**: 
    - Call `Get-ADPrincipalGroupMembership -Identity $UserName`.
    - Filter results where `GroupCategory -eq 'Security'` AND `Name -like $Filter`.
    - Output `ADGroup` objects.

#### Step 2: `Remove-GdsUserGroupMembership`
- **Parameters**: 
    - `UserName` (Mandatory).
    - `Group` (Mandatory, Pipeline-enabled).
- **Logic**:
    - Iterate through piped `Group` objects (or string names).
    - Support `ShouldProcess` (`-WhatIf`, `-Confirm`).
    - Call `Remove-ADGroupMember -Identity $Group -Members $UserName`.

#### Step 3: Unit Tests (`UserGroupMembership.Tests.ps1`)
- Mock `Get-ADPrincipalGroupMembership` to return custom PSObjects with `GroupCategory` and `Name`.
- Mock `Remove-ADGroupMember`.
- Verify pipeline logic (e.g., `Get... | Remove...`).
- Verify filtering logic.

#### Step 4: Documentation
- Create/Update `DOCUMENTATION.md` to explain usage and the testing approach (mocks).

## (Previous) Database Export Architecture 

### 1. Module Structure
```
GDS.ActiveDirectory/
├── GDS.ActiveDirectory.psm1          # Module manifest loader
├── GDS.ActiveDirectory.psd1          # Module manifest
├── Public/
│   ├── Export-ADObjectsToDatabase.ps1  # Main cmdlet
│   ├── Get-GdsUserGroupMembership.ps1  # [NEW] List groups
│   └── Remove-GdsUserGroupMembership.ps1 # [NEW] Remove groups
├── Private/
│   ├── New-ADDatabaseSchema.ps1        # Database schema creation
│   ├── Write-ADUserToDatabase.ps1      # ADUser database operations
│   ├── Write-ADGroupToDatabase.ps1     # ADGroup database operations
│   └── Get-DatabaseConnection.ps1      # Database connection helper
└── IMPLEMENTATION_PLAN.md              # This document
```

### 2. Database Schema (Unchanged)
[... see previous plan sections for DB schema details ...]

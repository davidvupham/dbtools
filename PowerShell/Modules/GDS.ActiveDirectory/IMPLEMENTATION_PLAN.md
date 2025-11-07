# Active Directory to Database Export - Implementation Plan

## Overview
This document outlines the implementation plan for a PowerShell cmdlet that retrieves Active Directory objects (ADUser and ADGroup) and stores them in a SQL Server database.

## Module Location
**Module**: `GDS.ActiveDirectory`
**Location**: `/workspaces/dbtools/PowerShell/Modules/GDS.ActiveDirectory/`

## Architecture

### 1. Module Structure
```
GDS.ActiveDirectory/
├── GDS.ActiveDirectory.psm1          # Module manifest loader
├── GDS.ActiveDirectory.psd1          # Module manifest
├── Public/
│   └── Export-ADObjectsToDatabase.ps1  # Main cmdlet
├── Private/
│   ├── New-ADDatabaseSchema.ps1        # Database schema creation
│   ├── Write-ADUserToDatabase.ps1      # ADUser database operations
│   ├── Write-ADGroupToDatabase.ps1     # ADGroup database operations
│   └── Get-DatabaseConnection.ps1      # Database connection helper
└── IMPLEMENTATION_PLAN.md              # This document
```

### 2. Database Schema

#### Table: ADUsers
Stores Active Directory user objects with key attributes.

**Columns:**
- `Id` (INT, IDENTITY, PRIMARY KEY) - Auto-incrementing ID
- `SamAccountName` (NVARCHAR(255), UNIQUE) - User's SAM account name
- `DistinguishedName` (NVARCHAR(500)) - Full DN
- `DisplayName` (NVARCHAR(500)) - Display name
- `GivenName` (NVARCHAR(255)) - First name
- `Surname` (NVARCHAR(255)) - Last name
- `EmailAddress` (NVARCHAR(255)) - Email address
- `UserPrincipalName` (NVARCHAR(255)) - UPN
- `Enabled` (BIT) - Account enabled status
- `LastLogonDate` (DATETIME2) - Last logon timestamp
- `PasswordLastSet` (DATETIME2) - Password last set date
- `Created` (DATETIME2) - AD object creation date
- `Modified` (DATETIME2) - AD object modification date
- `SID` (NVARCHAR(255)) - Security Identifier
- `Description` (NVARCHAR(MAX)) - User description
- `Department` (NVARCHAR(255)) - Department
- `Title` (NVARCHAR(255)) - Job title
- `Manager` (NVARCHAR(500)) - Manager's DN
- `Office` (NVARCHAR(255)) - Office location
- `PhoneNumber` (NVARCHAR(50)) - Phone number
- `MobilePhone` (NVARCHAR(50)) - Mobile phone
- `SyncDate` (DATETIME2, DEFAULT GETUTCDATE()) - When record was synced
- `SyncAction` (NVARCHAR(50)) - 'INSERT', 'UPDATE', or 'DELETE'

**Indexes:**
- Unique index on `SamAccountName`
- Index on `DistinguishedName`
- Index on `EmailAddress`
- Index on `SyncDate`

#### Table: ADGroups
Stores Active Directory group objects.

**Columns:**
- `Id` (INT, IDENTITY, PRIMARY KEY) - Auto-incrementing ID
- `SamAccountName` (NVARCHAR(255), UNIQUE) - Group's SAM account name
- `DistinguishedName` (NVARCHAR(500)) - Full DN
- `DisplayName` (NVARCHAR(500)) - Display name
- `Name` (NVARCHAR(255)) - Group name
- `Description` (NVARCHAR(MAX)) - Group description
- `GroupCategory` (NVARCHAR(50)) - Security/Distribution
- `GroupScope` (NVARCHAR(50)) - DomainLocal/Global/Universal
- `SID` (NVARCHAR(255)) - Security Identifier
- `Created` (DATETIME2) - AD object creation date
- `Modified` (DATETIME2) - AD object modification date
- `SyncDate` (DATETIME2, DEFAULT GETUTCDATE()) - When record was synced
- `SyncAction` (NVARCHAR(50)) - 'INSERT', 'UPDATE', or 'DELETE'

**Indexes:**
- Unique index on `SamAccountName`
- Index on `DistinguishedName`
- Index on `SyncDate`

#### Table: ADGroupMembers
Stores group membership relationships.

**Columns:**
- `GroupId` (INT, FOREIGN KEY -> ADGroups.Id) - Reference to group
- `MemberSamAccountName` (NVARCHAR(255)) - Member's SAM account name
- `MemberDistinguishedName` (NVARCHAR(500)) - Member's DN
- `MemberType` (NVARCHAR(50)) - 'User', 'Group', or 'Computer'
- `AddedDate` (DATETIME2, DEFAULT GETUTCDATE()) - When membership was recorded
- PRIMARY KEY (GroupId, MemberDistinguishedName)

**Indexes:**
- Index on `MemberSamAccountName`
- Index on `MemberDistinguishedName`

### 3. Cmdlet Design

#### Export-ADObjectsToDatabase
Main cmdlet that orchestrates the export process.

**Parameters:**
- `-Server` (String, Required) - SQL Server instance name
- `-Database` (String, Required) - Database name
- `-Credential` (PSCredential, Optional) - SQL Server credentials (if not using Windows Auth)
- `-ObjectType` (String[], Optional) - Types to export: 'User', 'Group', 'All' (default: 'All')
- `-Filter` (String, Optional) - LDAP filter for AD objects (e.g., "Department -eq 'IT'")
- `-SearchBase` (String, Optional) - OU to search from (default: domain root)
- `-CreateSchema` (Switch) - Create database schema if it doesn't exist
- `-UpdateMode` (String, Optional) - 'Full' (replace all) or 'Incremental' (update only) (default: 'Incremental')
- `-WhatIf` (Switch) - Preview changes without executing
- `-Verbose` (Switch) - Detailed output

**Output:**
- PSCustomObject with:
  - UsersProcessed (Int)
  - GroupsProcessed (Int)
  - UsersInserted (Int)
  - UsersUpdated (Int)
  - GroupsInserted (Int)
  - GroupsUpdated (Int)
  - Errors (Array)

**Example Usage:**
```powershell
# Export all AD objects
Export-ADObjectsToDatabase -Server "SQLSERVER01" -Database "ADInventory" -CreateSchema

# Export only users from specific OU
Export-ADObjectsToDatabase -Server "SQLSERVER01" -Database "ADInventory" `
    -ObjectType "User" -SearchBase "OU=Users,DC=contoso,DC=com"

# Export with filter
Export-ADObjectsToDatabase -Server "SQLSERVER01" -Database "ADInventory" `
    -Filter "Department -eq 'IT'" -UpdateMode "Full"
```

### 4. Implementation Steps

#### Step 1: Database Schema Creation
- Create `New-ADDatabaseSchema.ps1` private function
- Function creates tables, indexes, and constraints
- Handles schema existence checks
- Supports schema updates/migrations

#### Step 2: Database Connection Helper
- Create `Get-DatabaseConnection.ps1` private function
- Handles SQL Server connection using `System.Data.SqlClient`
- Supports both Windows Authentication and SQL Authentication
- Implements connection pooling and error handling

#### Step 3: ADUser Database Operations
- Create `Write-ADUserToDatabase.ps1` private function
- Retrieves ADUser objects using `Get-ADUser`
- Maps ADUser properties to database columns
- Implements INSERT/UPDATE logic based on UpdateMode
- Handles NULL values and data type conversions

#### Step 4: ADGroup Database Operations
- Create `Write-ADGroupToDatabase.ps1` private function
- Retrieves ADGroup objects using `Get-ADGroup`
- Maps ADGroup properties to database columns
- Handles group membership relationships
- Implements INSERT/UPDATE logic

#### Step 5: Main Cmdlet
- Create `Export-ADObjectsToDatabase.ps1` public function
- Orchestrates the export process
- Handles parameter validation
- Manages transactions
- Provides progress reporting
- Error handling and logging

#### Step 6: Module Manifest Update
- Update `GDS.ActiveDirectory.psd1` to export the new function
- Add required modules: `ActiveDirectory`, `SqlServer` (if needed)

### 5. Dependencies

**PowerShell Modules:**
- `ActiveDirectory` - For Get-ADUser, Get-ADGroup cmdlets
- `SqlServer` (optional) - For SQL Server cmdlets (we'll use .NET classes instead)

**.NET Assemblies:**
- `System.Data.SqlClient` - For SQL Server connectivity

**Prerequisites:**
- Windows OS (for Active Directory cmdlets)
- SQL Server database access
- Appropriate AD read permissions
- Appropriate database permissions (CREATE TABLE, INSERT, UPDATE)

### 6. Error Handling

- Validate AD connectivity before starting
- Validate database connectivity before starting
- Handle missing AD objects gracefully
- Handle database constraint violations
- Log all errors with context
- Continue processing on individual object errors
- Return comprehensive error summary

### 7. Performance Considerations

- Use batch inserts for large datasets
- Implement pagination for large AD queries
- Use transactions for data consistency
- Consider parallel processing for large exports
- Add progress indicators for long-running operations
- Implement connection reuse

### 8. Security Considerations

- Support secure credential handling
- Use parameterized queries to prevent SQL injection
- Encrypt database connections (if configured)
- Support Windows Authentication (preferred)
- Log access for audit purposes

### 9. Testing Strategy

- Unit tests for database operations
- Integration tests with test AD environment
- Test with various AD object configurations
- Test error scenarios (missing objects, DB errors)
- Test incremental vs full update modes
- Test with different filters and search bases

### 10. Future Enhancements

- Support for other AD object types (Computer, OU, etc.)
- Delta sync capabilities (only changed objects)
- Scheduled sync via scheduled tasks
- Support for multiple domains
- Export to other database types (PostgreSQL, MySQL)
- PowerShell DSC resource for configuration management
- REST API wrapper for remote execution

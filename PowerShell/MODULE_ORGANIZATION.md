# GDS PowerShell Module Organization

## Module Structure

GDS PowerShell modules are organized by purpose for clarity and maintainability.

### Core Modules

#### GDS.Common
**Purpose:** Common utilities shared across ALL GDS modules
**Contains:** Logging functions (PSFramework-based)
**Used By:** All GDS modules

**Functions:**
- `Write-Log` - Logging
- `Initialize-Logging` - Logging configuration
- `Set-GDSLogging` - Advanced logging settings

**Principle:** Only truly common utilities that every module needs

#### GDS.NuGet
**Purpose:** NuGet package building and publishing
**Contains:** Build and CI/CD functions
**Used By:** Developers and CI/CD pipelines

**Functions:**
- `Build-NuGetPackage` - Build single package
- `Build-AllNuGetPackages` - Build all packages
- `Publish-NuGetPackage` - Publish to repositories

**Principle:** Specialized for NuGet operations, not used by runtime modules

### Domain Modules

#### GDS.ActiveDirectory
**Purpose:** Active Directory management
**Contains:** AD object export, synchronization

#### GDS.MSSQL.*
**Purpose:** SQL Server operations
**Modules:**
- `GDS.MSSQL.Core` - Core SQL utilities
- `GDS.MSSQL.Build` - SQL Server instance building
- `GDS.MSSQL.AvailabilityGroups` - AG management
- `GDS.MSSQL.Monitor` - Monitoring and health

#### GDS.WindowsOS
**Purpose:** Windows OS operations
**Contains:** Windows-specific utilities

## Module Dependencies

```
GDS.ActiveDirectory
  └── GDS.Common (logging)

GDS.MSSQL.*
  └── GDS.Common (logging)

GDS.WindowsOS
  └── GDS.Common (logging)

GDS.NuGet
  └── GDS.Common (logging for build process)
```

## Design Principles

### 1. Single Responsibility
Each module has a clear, focused purpose:
- **GDS.Common** = Logging only
- **GDS.NuGet** = NuGet packaging only
- **GDS.ActiveDirectory** = AD operations only

### 2. Minimal Dependencies
- Runtime modules only depend on GDS.Common
- GDS.NuGet is only used during build/deployment, not runtime

### 3. Clear Naming
- **Common** = Used by everyone
- **NuGet** = Specific to NuGet operations
- **ActiveDirectory** = Domain-specific
- **MSSQL.{Function}** = SQL Server with specific function

### 4. Separation of Concerns
- **Runtime utilities** (GDS.Common) are separate from **build utilities** (GDS.NuGet)
- Developers building packages use GDS.NuGet
- Applications using the modules only need GDS.Common

## Usage Patterns

### For Module Development

```powershell
# In YourModule.psd1
@{
    RequiredModules = @(
        @{ ModuleName = 'GDS.Common'; ModuleVersion = '1.0.0' }
    )
}

# In YourModule.psm1
Initialize-Logging -ModuleName "YourModule"
Write-Log -Message "Module loaded" -Level Info
```

### For Building/Publishing

```powershell
# Developers and CI/CD only
Import-Module GDS.NuGet
Build-AllNuGetPackages -Parallel
Publish-NuGetPackage -ModuleName "YourModule" -Repository "JFrog" -NuGetApiKey $key
```

### For End Users

```powershell
# Users only install what they need
Install-Module -Name GDS.ActiveDirectory  # Automatically gets GDS.Common
# They never need GDS.NuGet
```

## When to Create a New Module

### Create a NEW module when:
- ✅ Functionality is domain-specific (e.g., GDS.Azure, GDS.Oracle)
- ✅ Functionality is used independently
- ✅ Functionality has unique dependencies
- ✅ Functionality serves a specific purpose

### Add to EXISTING module when:
- ❌ Function is truly common to all modules → GDS.Common
- ❌ Function is for NuGet operations → GDS.NuGet
- ❌ Function is domain-specific and fits existing module

## Module Naming Convention

Format: `GDS.{Purpose}[.{SubPurpose}]`

**Examples:**
- `GDS.Common` - Common utilities
- `GDS.NuGet` - NuGet operations
- `GDS.ActiveDirectory` - Active Directory
- `GDS.MSSQL.Core` - SQL Server core
- `GDS.MSSQL.Build` - SQL Server build operations

**Guidelines:**
- Use specific, descriptive names
- Avoid generic names (~~GDS.Build~~, ~~GDS.Utils~~)
- Use sub-names for related groups (MSSQL.*)

## Current Module Catalog

| Module | Purpose | Type | Dependencies |
|--------|---------|------|--------------|
| GDS.Common | Logging | Utility | PSFramework |
| GDS.NuGet | NuGet packaging | Build Tool | GDS.Common |
| GDS.ActiveDirectory | AD management | Domain | GDS.Common |
| GDS.MSSQL.Core | SQL utilities | Domain | GDS.Common |
| GDS.MSSQL.Build | SQL instance building | Domain | GDS.Common |
| GDS.MSSQL.AvailabilityGroups | SQL AG management | Domain | GDS.Common |
| GDS.MSSQL.Monitor | SQL monitoring | Domain | GDS.Common |
| GDS.WindowsOS | Windows operations | Domain | GDS.Common |

## Decision Tree

```
Does the functionality apply to ALL modules?
  ├─ YES: Add to GDS.Common
  └─ NO: Is it for NuGet packaging?
      ├─ YES: Add to GDS.NuGet
      └─ NO: Is it domain-specific?
          ├─ YES: Add to domain module or create new one
          └─ NO: Reconsider if it's needed
```

## Summary

**GDS.Common**: Logging only (truly common)
**GDS.NuGet**: NuGet packaging (specific purpose)
**Domain Modules**: Business functionality

This organization keeps modules focused, dependencies minimal, and purpose clear.

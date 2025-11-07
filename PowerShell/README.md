# PowerShell Modules for DBTools

This directory contains PowerShell modules for the DBTools project, providing functionality for interacting with Microsoft SQL Server, Windows operating systems, and Active Directory.

## Modules

- **GDS.Common**: Common utilities (logging) shared across all GDS modules.
- **GDS.NuGet**: NuGet package building and publishing for GDS modules.
- **GDS.ActiveDirectory**: Functions for Active Directory management.
- **GDS.MSSQL.Build**: Functions for building and configuring SQL Server instances.
- **GDS.MSSQL.AvailabilityGroups**: Functions for managing SQL Server Availability Groups.
- **GDS.MSSQL.Core**: Shared utilities and common functions for MSSQL modules.
- **GDS.MSSQL.Monitor**: Functions for monitoring SQL Server performance and health.
- **GDS.WindowsOS**: Functions for interacting with Windows operating system components.

## Getting Started

### For End Users - Installing Modules

```powershell
# Install from JFrog Artifactory
.\Install-GDSModulesFromJFrog.ps1 `
    -JFrogUrl "https://mycompany.jfrog.io" `
    -JFrogRepo "powershell-modules"

# Or install from PowerShell Gallery (if published)
Install-Module -Name GDS.Common, GDS.ActiveDirectory
```

### For Developers - Using Modules

```powershell
# Import a module
Import-Module GDS.ActiveDirectory

# Use module functions
Export-ADObjectsToDatabase -Server "SQLSERVER01" -Database "ADInventory" -CreateSchema
```

### For Developers - Building Packages

```powershell
# Quick build - Use convenience script
.\BuildAllModules.ps1

# Or build with options
.\BuildAllModules.ps1 -Parallel -SkipTests

# Or use GDS.NuGet module directly
Import-Module GDS.NuGet
Build-AllNuGetPackages -Parallel
```

## Key Scripts

### BuildAllModules.ps1
Convenience script to build all GDS module packages.

```powershell
.\BuildAllModules.ps1                    # Build all
.\BuildAllModules.ps1 -Parallel         # Build in parallel (faster)
.\BuildAllModules.ps1 -SkipTests        # Skip validation (faster)
```

### Install-GDSModulesFromJFrog.ps1
Install GDS modules from JFrog Artifactory.

```powershell
.\Install-GDSModulesFromJFrog.ps1 -JFrogUrl "https://company.jfrog.io" -JFrogRepo "repo"
```

## Requirements

- **Windows OS** for AD and Windows-specific modules
- **PowerShell 5.1 or later** (PowerShell 7+ recommended)
- **PSFramework module** for logging
- **SQL Server modules** require the `SqlServer` PowerShell module
- **ActiveDirectory module** requires RSAT-AD-PowerShell

## Development

### Setup

```powershell
# Install prerequisites
Install-Module -Name PSFramework -Scope CurrentUser -Force
Install-Module -Name Pester -Scope CurrentUser -Force
Install-Module -Name PSScriptAnalyzer -Scope CurrentUser -Force

# Add modules to PSModulePath
$modulesPath = "$PSScriptRoot/Modules"
$env:PSModulePath += [System.IO.Path]::PathSeparator + $modulesPath

# Import modules
Import-Module GDS.Common
Import-Module GDS.NuGet
```

### Testing

```powershell
# Run PSScriptAnalyzer
Invoke-ScriptAnalyzer -Path .\Modules\ -Recurse

# Run Pester tests
Invoke-Pester -Path .\Modules\ -Output Detailed
```

### Building

```powershell
# Build all modules
.\BuildAllModules.ps1 -Parallel

# Output: build/packages/*.nupkg
```

## CI/CD

GitHub Actions workflow: `.github/workflows/powershell-modules-jfrog.yml`

**Triggers:**
- Push to main/develop
- Pull requests
- Releases

**Actions:**
- Validates code (PSScriptAnalyzer)
- Runs tests (Pester)
- Builds packages
- Publishes to JFrog Artifactory (on main/release)

## Documentation

### Project Level
- [MODULE_ORGANIZATION.md](./MODULE_ORGANIZATION.md) - Module organization principles
- [FINAL_IMPLEMENTATION_SUMMARY.md](./FINAL_IMPLEMENTATION_SUMMARY.md) - Complete implementation summary

### Module Documentation
- [GDS.Common/README.md](./Modules/GDS.Common/README.md) - Logging module
- [GDS.NuGet/README.md](./Modules/GDS.NuGet/README.md) - NuGet build module
- [GDS.ActiveDirectory/IMPLEMENTATION_PLAN.md](./Modules/GDS.ActiveDirectory/IMPLEMENTATION_PLAN.md) - AD implementation

### Detailed Guides (in GDS.NuGet/)
- [GDS.NuGet/NUGET_QUICK_START.md](./Modules/GDS.NuGet/NUGET_QUICK_START.md) - Quick reference
- [GDS.NuGet/JFROG_QUICK_START.md](./Modules/GDS.NuGet/JFROG_QUICK_START.md) - JFrog quick reference
- [GDS.NuGet/NUGET_BUILD_HOWTO.md](./Modules/GDS.NuGet/NUGET_BUILD_HOWTO.md) - Step-by-step guide
- [GDS.NuGet/JFROG_CICD_GUIDE.md](./Modules/GDS.NuGet/JFROG_CICD_GUIDE.md) - Complete JFrog + GitHub Actions

### Logging Guides (in GDS.Common/)
- [GDS.Common/DEVELOPER_GUIDE_LOGGING.md](./Modules/GDS.Common/DEVELOPER_GUIDE_LOGGING.md) - Complete logging guide

## Package Output

Built packages go to: `PowerShell/build/packages/`

Format: `{ModuleName}.{Version}.nupkg`

For more details, see the individual module READMEs.

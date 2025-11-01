# PowerShell Modules for DBTools

This directory contains PowerShell modules for the DBTools project, providing functionality for interacting with Microsoft SQL Server, Windows operating systems, and Active Directory.

## Modules

- **GDS.MSSQL.Build**: Functions for building and configuring SQL Server instances.
- **GDS.MSSQL.AvailabilityGroups**: Functions for managing SQL Server Availability Groups.
- **GDS.MSSQL.Core**: Shared utilities and common functions for MSSQL modules.
- **GDS.MSSQL.Monitor**: Functions for monitoring SQL Server performance and health.
- **GDS.WindowsOS**: Functions for interacting with Windows operating system components.
- **GDS.ActiveDirectory**: Functions for Active Directory management.

## Getting Started

1. Ensure PowerShell 5.1 or later is installed.
2. Import a module: `Import-Module .\modules\GDS.MSSQL.Build\GDS.MSSQL.Build.psd1`
3. Run functions: `Get-Command -Module GDS.MSSQL.Build`

## Requirements

- Windows OS for AD and Windows-specific modules.
- SQL Server modules require the `SqlServer` PowerShell module.

## Development

- Use Pester for testing.
- Lint with PSScriptAnalyzer.
- Package modules as NuGet packages using the build script.

## Packaging

To create NuGet packages for distribution:

```powershell
# Build and package all modules
.\powershell\build\build.ps1 -PackageNuGet
```

See `docs/NuGetPackagingTutorial.md` for detailed instructions.

For more details, see the individual module READMEs.

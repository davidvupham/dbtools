# PowerShell Best Practices: Naming and Style

Consistent naming and style conventions make PowerShell scripts more readable, maintainable, and discoverable. This document covers the standards that align with Microsoft's cmdlet design guidelines.

## Function and Script Naming

### Use Verb-Noun Format

PowerShell commands follow a `Verb-Noun` naming pattern. Use only **approved verbs** from `Get-Verb`:

```powershell
# BEST PRACTICE
Get-ServiceStatus
Set-Configuration
New-BackupJob
Remove-TempFiles

# ANTI-PATTERN - unapproved verbs cause warnings
Fetch-Data        # Use Get-Data
Create-User       # Use New-User
Delete-Log        # Use Remove-Log
Execute-Script    # Use Invoke-Script
```

> [!TIP]
> Run `Get-Verb | Sort-Object Verb` to see all approved verbs grouped by category (Common, Data, Lifecycle, Security, etc.).

### Use Singular Nouns

Use singular nouns even when the command operates on multiple items:

```powershell
# BEST PRACTICE
Get-Process       # Not Get-Processes
Get-EventLog      # Not Get-EventLogs
Remove-Item       # Not Remove-Items
```

### Use Specific Nouns with Prefixes

Generic nouns should include a prefix to avoid conflicts and improve discoverability:

```powershell
# BEST PRACTICE - specific nouns
Get-ADUser              # Active Directory user
Get-AzStorageAccount    # Azure storage
Get-GDSServerConfig     # Your organization's tools

# ANTI-PATTERN - too generic
Get-User
Get-Server
Get-Config
```

### Use PascalCase

Capitalize the first letter of each word in function names, parameters, and variables:

```powershell
# BEST PRACTICE
function Get-ServerInfo {
    param(
        [string]$ComputerName,
        [switch]$IncludeDetails
    )
}

# ANTI-PATTERN
function get-serverinfo {
    param(
        [string]$computername,
        [switch]$includedetails
    )
}
```

## Script Style Conventions

### Use Full Command Names

Avoid aliases in scripts for clarity and cross-platform compatibility:

```powershell
# BEST PRACTICE
Get-Process -Name "explorer"
Get-ChildItem -Path "C:\Logs" -Filter "*.log"
Where-Object -Property Status -EQ "Running"

# ANTI-PATTERN - aliases are fine for interactive use, not scripts
gps -Name "explorer"
gci C:\Logs -Filter "*.log"
? { $_.Status -eq "Running" }
```

### Use Full Parameter Names

Explicit parameter names improve readability and protect against parameter set changes:

```powershell
# BEST PRACTICE
Get-Process -Name "explorer"
Copy-Item -Path "source.txt" -Destination "backup.txt"
Get-Content -Path "log.txt" -Tail 100

# ANTI-PATTERN - positional parameters can be ambiguous
Get-Process explorer
Copy-Item source.txt backup.txt
Get-Content log.txt -Tail 100
```

### Use Explicit Paths

Avoid relative paths (`.`, `..`, `~`) in scripts because:
- .NET methods use `[Environment]::CurrentDirectory`, not PowerShell's `$PWD`
- Relative paths are fragile and confusing when debugging

```powershell
# BEST PRACTICE - use $PSScriptRoot for script-relative paths
$configPath = Join-Path -Path $PSScriptRoot -ChildPath "config.json"
$dataPath = Join-Path -Path $PSScriptRoot -ChildPath "..\data\input.csv"

# BEST PRACTICE - use fully qualified paths
$logPath = "C:\Logs\Application\script.log"

# ANTI-PATTERN
$configPath = ".\config.json"
$homePath = "~\Documents\scripts"
```

## Parameter Naming Standards

### Use Standard Parameter Names

PowerShell has conventional names for common parameters. Use them consistently:

| Standard Name | Purpose | Aliases |
|---------------|---------|---------|
| `ComputerName` | Target computer(s) | `Server`, `CN` |
| `Credential` | PSCredential object | `Cred` |
| `Path` | File/folder path | `FilePath` |
| `Name` | Resource identifier | |
| `Force` | Override restrictions | |
| `Confirm` | Prompt for confirmation | |
| `WhatIf` | Preview mode | |

```powershell
# BEST PRACTICE - standard names with aliases
param(
    [Parameter(Mandatory)]
    [Alias('Server', 'CN')]
    [string[]]$ComputerName,

    [System.Management.Automation.PSCredential]
    [System.Management.Automation.Credential()]
    $Credential
)

# ANTI-PATTERN - non-standard names
param(
    [string[]]$ServerList,      # Use ComputerName
    [string]$FileName,          # Use Path
    [pscredential]$AdminCreds   # Use Credential
)
```

### Use Singular Parameter Names

Unless a parameter **always** requires multiple values, use singular names:

```powershell
# BEST PRACTICE
param(
    [string[]]$ComputerName,    # Singular but accepts arrays
    [string]$Path
)

# ANTI-PATTERN - plural suggests it's array-only
param(
    [string[]]$ComputerNames,
    [string[]]$Paths
)
```

## Naming Conventions Summary

| Element | Convention | Example |
|---------|------------|---------|
| Functions | PascalCase, Verb-Noun | `Get-ServerConfig` |
| Parameters | PascalCase | `$ComputerName` |
| Variables | PascalCase | `$ConfigPath` |
| Private Functions | Use module scoping, not prefixes | Internal functions in module |
| Nouns | Singular, specific with prefix | `GDSWindowsConfig` |
| Verbs | Approved PowerShell verbs | `Get`, `Set`, `New`, `Remove` |

## Related Documentation

- [Advanced Functions and Parameters](advanced-functions.md) - CmdletBinding, parameter validation
- [Output, Streams, and Logging](output-streams-and-logging.md) - Writing clean, pipelineable output

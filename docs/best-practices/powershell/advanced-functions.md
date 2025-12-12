# PowerShell Best Practices: Advanced Functions

Advanced functions provide built-in capabilities like parameter validation, verbose output, and common parameters. This document covers patterns for building robust, reusable PowerShell tools.

## CmdletBinding: The Foundation

Adding `[CmdletBinding()]` transforms a basic function into an advanced function with automatic support for common parameters:

```powershell
# Basic function - no common parameters
function Get-BasicInfo {
    param($Name)
    Write-Output $Name
}

# Advanced function - adds -Verbose, -Debug, -ErrorAction, etc.
function Get-AdvancedInfo {
    [CmdletBinding()]
    param(
        [string]$Name
    )

    Write-Verbose "Processing: $Name"
    Write-Output $Name
}
```

### Common Parameters Added by CmdletBinding

| Parameter | Purpose |
|-----------|---------|
| `-Verbose` | Display verbose messages |
| `-Debug` | Display debug messages |
| `-ErrorAction` | Control error behavior |
| `-WarningAction` | Control warning behavior |
| `-InformationAction` | Control information stream |
| `-ErrorVariable` | Store errors in a variable |
| `-OutVariable` | Store output in a variable |
| `-OutBuffer` | Buffer output before sending |
| `-PipelineVariable` | Store current pipeline object |

## Parameter Validation

### Mandatory Parameters

Use `[Parameter(Mandatory)]` to require a value. PowerShell prompts if not provided:

```powershell
function Get-UserInfo {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$UserName
    )

    # $UserName is guaranteed to have a value
    Get-ADUser -Identity $UserName
}
```

### Type Validation

Specify types to enforce correct data:

```powershell
param(
    [string]$Name,              # Single string
    [string[]]$ComputerName,    # Array of strings
    [int]$Count,                # Integer
    [datetime]$StartDate,       # DateTime
    [System.IO.FileInfo]$Path   # File object with validation
)
```

### Validation Attributes

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `ValidateNotNullOrEmpty` | Reject null or empty | `[ValidateNotNullOrEmpty()][string]$Name` |
| `ValidateSet` | Restrict to specific values | `[ValidateSet('Low','Medium','High')]` |
| `ValidateRange` | Numeric range | `[ValidateRange(1,100)]` |
| `ValidatePattern` | Regex match | `[ValidatePattern('^[A-Z]{3}\d{4}$')]` |
| `ValidateScript` | Custom validation | `[ValidateScript({Test-Path $_})]` |
| `ValidateLength` | String length | `[ValidateLength(1,50)]` |
| `ValidateCount` | Array element count | `[ValidateCount(1,10)]` |

```powershell
function Set-Priority {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [ValidateNotNullOrEmpty()]
        [string]$TaskName,

        [ValidateSet('Low', 'Medium', 'High', 'Critical')]
        [string]$Priority = 'Medium',

        [ValidateRange(1, 100)]
        [int]$Percentage = 50,

        [ValidateScript({ Test-Path $_ -PathType Leaf })]
        [string]$ConfigFile
    )

    Write-Verbose "Setting $TaskName to $Priority ($Percentage%)"
}
```

### Default Values with Validation

Use `ValidateNotNullOrEmpty` instead of `Mandatory` when you want a default value:

```powershell
param(
    # Prompts if not provided
    [Parameter(Mandatory)]
    [string]$RequiredValue,

    # Uses default if not provided, errors if explicitly set to null/empty
    [ValidateNotNullOrEmpty()]
    [string]$OptionalWithDefault = $env:COMPUTERNAME
)
```

## Pipeline Input

### ValueFromPipeline

Accept objects from the pipeline with the `process` block:

```powershell
function Get-ServiceStatus {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [string[]]$ComputerName
    )

    process {
        foreach ($Computer in $ComputerName) {
            Write-Verbose "Checking $Computer"
            Get-Service -ComputerName $Computer
        }
    }
}

# Usage
"Server01", "Server02" | Get-ServiceStatus
```

### ValueFromPipelineByPropertyName

Accept property values from pipeline objects:

```powershell
function Get-DetailedInfo {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory, ValueFromPipelineByPropertyName)]
        [Alias('CN', 'Server')]
        [string]$ComputerName
    )

    process {
        Write-Output "Processing: $ComputerName"
    }
}

# Works with objects that have ComputerName, CN, or Server properties
Get-ADComputer -Filter * | Get-DetailedInfo
```

## Verbose Output

Use `Write-Verbose` for detailed operational information, hidden by default:

```powershell
function Install-Application {
    [CmdletBinding()]
    param(
        [string]$AppName
    )

    Write-Verbose "Starting installation of $AppName"
    Write-Verbose "Downloading installer..."
    # Download logic

    Write-Verbose "Running installer..."
    # Install logic

    Write-Verbose "Installation complete"
}

# Usage
Install-Application -AppName "MyApp"           # Quiet
Install-Application -AppName "MyApp" -Verbose  # Detailed
```

## Tool Functions vs. Controller Scripts

### Tool Functions (Reusable)

- Accept input via parameters
- Output raw, unformatted objects to the pipeline
- Handle one logical operation
- Designed for maximum reusability

```powershell
function Get-DiskSpace {
    [CmdletBinding()]
    param(
        [Parameter(ValueFromPipeline)]
        [string[]]$ComputerName = $env:COMPUTERNAME
    )

    process {
        foreach ($Computer in $ComputerName) {
            Get-CimInstance -ClassName Win32_LogicalDisk -ComputerName $Computer |
                Where-Object DriveType -EQ 3 |
                Select-Object @{N='ComputerName';E={$Computer}}, DeviceID,
                    @{N='SizeBytes';E={$_.Size}},
                    @{N='FreeBytes';E={$_.FreeSpace}}
        }
    }
}
```

### Controller Scripts (Purpose-Built)

- Orchestrate multiple tools
- Format output for human consumption
- Contain business-specific logic
- Not designed for reuse

```powershell
# Controller script: Generate-DiskReport.ps1
$servers = Get-Content "$PSScriptRoot\servers.txt"

Write-Host "Disk Space Report - $(Get-Date)" -ForegroundColor Cyan

$servers | Get-DiskSpace | ForEach-Object {
    $freeGB = [math]::Round($_.FreeBytes / 1GB, 2)
    $totalGB = [math]::Round($_.SizeBytes / 1GB, 2)
    $pctFree = [math]::Round(($_.FreeBytes / $_.SizeBytes) * 100, 1)

    Write-Host "$($_.ComputerName) $($_.DeviceID): $freeGB GB free of $totalGB GB ($pctFree%)"
}
```

## Advanced Function Checklist

1. **Always use `[CmdletBinding()]`** to enable common parameters
2. **Use appropriate parameter validation** for required and constrained values
3. **Support pipeline input** with `ValueFromPipeline` where logical
4. **Use `Write-Verbose`** for operational details, not `Write-Host`
5. **Output raw objects** from tool functions, let callers format
6. **Document with comment-based help** (Synopsis, Description, Examples)
7. **Use standard parameter names** (`ComputerName`, `Path`, `Credential`)

## Related Documentation

- [WhatIf and ShouldProcess](whatif-and-shouldprocess.md) - Add preview support for destructive operations
- [Output, Streams, and Logging](output-streams-and-logging.md) - Proper use of output streams
- [Naming and Style](naming-and-style.md) - Naming conventions for functions and parameters
- [Error Handling](error-handling.md) - Robust error handling in advanced functions

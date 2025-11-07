# GDS.Common Module

Common utilities shared across all GDS PowerShell modules.

## Overview

GDS.Common provides **logging functionality** that is used by all GDS modules:
- **PSFramework Logging** - Industry-standard logging with multiple output targets
- **Cross-Platform Support** - Works on Windows, Linux, and macOS

## Purpose

This module contains **only truly common utilities** that all GDS modules need:
- ✅ Logging (Write-Log, Initialize-Logging, Set-GDSLogging)
- ✅ Cross-platform utilities (future)
- ✅ Shared helper functions (future)

**Note:** For NuGet package building and publishing, see the **GDS.NuGet** module.

## Features

### 🔍 PSFramework Logging
- Industry-standard logging using PSFramework (de facto standard)
- Multiple output targets (file, console, Event Log, Splunk, Azure)
- Structured logging with JSON format
- Automatic log rotation and retention
- Log levels: Debug, Verbose, Info, Warning, Error, Critical
- Context and exception support
- Asynchronous, non-blocking operations
- Cross-platform compatible (Windows, Linux, macOS)

## Installation

### Prerequisites

```powershell
# Install PSFramework (required)
Install-Module -Name PSFramework -Scope CurrentUser -Force
```

### Install GDS.Common

```powershell
# From PowerShell Gallery (once published)
Install-Module -Name GDS.Common -Scope CurrentUser

# Or import from PSModulePath
Import-Module GDS.Common
```

## Quick Start

```powershell
# Import module
Import-Module GDS.Common

# Initialize logging for your module
Initialize-Logging -ModuleName "MyModule"

# Write log messages
Write-Log -Message "Processing user" -Level Info
Write-Log -Message "Error occurred" -Level Error -Exception $_.Exception
Write-Log -Message "Operation completed" -Level Info -Context @{Count=100}

# Advanced configuration
Set-GDSLogging -ModuleName "MyModule" -EnableEventLog:$IsWindows -MinimumLevel "Debug"
```

## Functions

### Write-Log
Writes log entries using PSFramework logging.

```powershell
Write-Log -Message "Processing data" -Level Info -Context @{User="jdoe"} -Tag "Processing"
```

**Parameters:**
- `Message` (required) - Log message
- `Level` (optional) - Debug, Verbose, Info, Warning, Error, Critical (default: Info)
- `Exception` (optional) - Exception object to include
- `Context` (optional) - Hashtable with additional context
- `Tag` (optional) - Tags for categorization
- `ModuleName` (optional) - Module name (auto-detected)

### Initialize-Logging
Initializes PSFramework logging for a module.

```powershell
Initialize-Logging -ModuleName "MyModule" -LogLevel "Debug"
```

**Parameters:**
- `ModuleName` (optional) - Module name (auto-detected)
- `LogPath` (optional) - Custom log file path
- `LogLevel` (optional) - Minimum log level (default: Info)
- `MaxLogSizeMB` (optional) - Max log size before rotation (default: 10)
- `RetentionDays` (optional) - Days to retain logs (default: 30)

### Set-GDSLogging
Configures advanced PSFramework logging settings.

```powershell
Set-GDSLogging -ModuleName "MyModule" -EnableEventLog -MinimumLevel "Debug"
```

**Parameters:**
- `ModuleName` (required) - Module name
- `EnableEventLog` (optional) - Enable Windows Event Log (Windows only)
- `EnableFileLog` (optional) - Enable file logging (default: true)
- `EnableConsoleLog` (optional) - Enable console output (default: true)
- `LogPath` (optional) - Custom log file path
- `MinimumLevel` (optional) - Minimum log level (default: Info)
- `MaxLogSizeMB` (optional) - Max log size (default: 10MB)
- `RetentionDays` (optional) - Retention period (default: 30 days)

## Usage Examples

### Example 1: Basic Logging

```powershell
Import-Module GDS.Common

# Initialize once
Initialize-Logging -ModuleName "MyScript"

# Log various levels
Write-Log -Message "Script started" -Level Info
Write-Log -Message "Processing 100 items" -Level Verbose
Write-Log -Message "Warning: connection slow" -Level Warning

# Log with context
Write-Log -Message "User processed" -Level Info -Context @{
    UserName = "jdoe"
    ProcessingTime = 123
}

# Log errors
try {
    Get-Item "NonExistent.txt"
}
catch {
    Write-Log -Message "File not found" -Level Error -Exception $_.Exception
}
```

### Example 2: Module with Logging

```powershell
# MyModule.psm1

# Import GDS.Common
Import-Module GDS.Common

# Initialize logging at module load
Initialize-Logging -ModuleName "MyModule"

function Get-MyData {
    [CmdletBinding()]
    param([string]$Filter)

    Write-Log -Message "Getting data" -Level Info -Context @{Filter = $Filter}

    try {
        $data = Get-Data -Filter $Filter
        Write-Log -Message "Data retrieved" -Level Info -Context @{Count = $data.Count}
        return $data
    }
    catch {
        Write-Log -Message "Failed to get data" -Level Error -Exception $_.Exception
        throw
    }
}

Export-ModuleMember -Function Get-MyData
```

### Example 3: Advanced Configuration

```powershell
# Configure logging with custom settings
Set-GDSLogging -ModuleName "MyModule" `
    -EnableEventLog:$IsWindows `
    -EnableFileLog `
    -LogPath "C:\Logs\MyModule.log" `
    -MinimumLevel "Debug" `
    -MaxLogSizeMB 50 `
    -RetentionDays 60
```

## Log Locations

### Default Locations

**Windows:**
- `C:\Users\{Username}\AppData\Roaming\PSFramework\Logs\{ModuleName}_{Date}.log`

**Linux:**
- `~/.local/share/powershell/PSFramework/Logs/{ModuleName}_{Date}.log`

**macOS:**
- `~/Library/Application Support/PowerShell/PSFramework/Logs/{ModuleName}_{Date}.log`

### Custom Location

```powershell
Initialize-Logging -ModuleName "MyModule" -LogPath "C:\Logs\MyModule.log"
```

## Integration with Other Modules

### Add Dependency

```powershell
# In YourModule.psd1
@{
    RequiredModules = @(
        @{ ModuleName = 'GDS.Common'; ModuleVersion = '1.0.0' }
    )
}
```

### Use Logging

```powershell
# In YourModule.psm1
Initialize-Logging -ModuleName "YourModule"

function Get-Something {
    Write-Log -Message "Getting something" -Level Info
    # ... your code ...
}
```

### Real Example: GDS.ActiveDirectory

```powershell
# GDS.ActiveDirectory.psd1
@{
    RequiredModules = @(
        @{ ModuleName = 'GDS.Common'; ModuleVersion = '1.0.0' }
    )
}

# In Export-ADObjectsToDatabase.ps1
Initialize-Logging -ModuleName "ActiveDirectory"
Write-Log -Message "Starting AD export" -Level Info
```

## Dependencies

- **PSFramework** (v1.7.0 or later) - Required

## Cross-Platform Support

GDS.Common works on:
- ✅ Windows (PowerShell 5.1, PowerShell 7+)
- ✅ Linux (PowerShell 7+)
- ✅ macOS (PowerShell 7+)

**Note:** Windows Event Log is only available on Windows platforms (automatically detected).

## Documentation

### 📚 Logging Guides
- **[DEVELOPER_GUIDE_LOGGING.md](./DEVELOPER_GUIDE_LOGGING.md)** - Complete guide with examples
- [PSFramework Migration Guide](./PSFRAMEWORK_MIGRATION.md) - Migration from custom logging
- [Cross-Platform Support](./PSFRAMEWORK_CROSS_PLATFORM.md) - Platform details
- [PowerShell Logging Best Practices](./POWERSHELL_LOGGING_BEST_PRACTICES.md) - Best practices analysis
- [PSFramework Implementation Summary](./PSFRAMEWORK_IMPLEMENTATION_SUMMARY.md) - Implementation details

### 🔨 NuGet Package Building

**Looking for build functions?** See the **GDS.NuGet** module:
- [GDS.NuGet README](../GDS.NuGet/README.md)
- [NuGet Build How-To](../GDS.NuGet/NUGET_BUILD_HOWTO.md)
- [JFrog CI/CD Guide](../GDS.NuGet/JFROG_CICD_GUIDE.md)

## Troubleshooting

### Check PSFramework Installation

```powershell
Get-Module -ListAvailable -Name PSFramework
Import-Module PSFramework
Get-PSFLoggingProvider
```

### View Recent Logs

```powershell
# View in-memory logs
Get-PSFMessage -Last 20

# View by level
Get-PSFMessage -Level Error

# View by tag
Get-PSFMessage -Tag "MyModule"
```

### Check Log Files

```powershell
# Find log directory
$logPath = Join-Path $env:APPDATA "PSFramework\Logs"
Get-ChildItem $logPath | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```

### Enable Debug Logging

```powershell
Set-GDSLogging -ModuleName "MyModule" -MinimumLevel "Debug"
Get-PSFMessage -Level Debug
```

## Best Practices

1. ✅ Initialize logging once at module load
2. ✅ Use appropriate log levels
3. ✅ Include context in log messages
4. ✅ Log exceptions with `-Exception` parameter
5. ✅ Use tags for categorization
6. ❌ Don't log sensitive information (passwords, keys)
7. ❌ Don't over-log (performance impact)

## External Resources

- [PSFramework Documentation](https://psframework.org/documentation/documents/psframework/logging.html)
- [PSFramework GitHub](https://github.com/PowershellFrameworkCollective/psframework)
- [PowerShell Gallery](https://www.powershellgallery.com/)

---

**Module Type:** Common Utilities (Logging)
**Version:** 1.0.0
**Status:** Production Ready ✅
**Maintained By:** GDS Team

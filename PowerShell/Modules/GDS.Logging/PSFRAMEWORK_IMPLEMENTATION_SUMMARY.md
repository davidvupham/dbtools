# PSFramework Implementation Summary

## Overview

GDS modules have been successfully migrated to use **PSFramework** for logging, replacing the custom `Write-Log` implementation. PSFramework is the de facto standard for PowerShell logging and provides comprehensive, production-ready logging capabilities.

## What Changed

### Before

- Custom `Write-Log` function with JSON file logging
- Manual log rotation
- Single output target (file)
- Custom implementation to maintain

### After

- PSFramework-based logging with wrapper function
- Automatic log rotation and retention
- Multiple output targets (file, console, event log, Splunk, Azure)
- Industry-standard implementation

## Implementation Details

### 1. GDS.Common Module Updates

**Module Manifest (`GDS.Common.psd1`)**

- Added PSFramework as required module
- Version requirement: 1.7.0 or later

**Functions Updated:**

- `Write-Log.ps1`: Now wraps `Write-PSFMessage`
- `Initialize-Logging.ps1`: Configures PSFramework providers
- `Set-GDSLogging.ps1`: New function for advanced configuration

### 2. Backward Compatibility

**The `Write-Log` function signature remains the same**, so existing code continues to work without changes:

```powershell
# This still works exactly the same
Write-Log -Message "Processing" -Level Info -Context @{User="jdoe"}
```

### 3. New Features Available

**Multiple Output Targets:**

```powershell
Set-GDSLogging -ModuleName "ActiveDirectory" -EnableEventLog
```

**Advanced Configuration:**

```powershell
Set-GDSLogging -ModuleName "ActiveDirectory" `
    -MinimumLevel "Debug" `
    -LogPath "C:\Logs\AD.log"
```

**Direct PSFramework Access:**

```powershell
# Can also use PSFramework directly
Write-PSFMessage -Level Important -Message "Processing" -Tag "ActiveDirectory"
```

## Benefits

### 1. Industry Standard ✅

- Widely adopted in PowerShell community
- Well-documented and maintained
- Community support

### 2. Feature Rich ✅

- Multiple output targets
- Structured logging
- Rich metadata support
- Exception handling

### 3. Performance ✅

- Asynchronous logging (non-blocking)
- Runspace-safe (concurrent operations)
- Minimal performance impact

### 4. Integration ✅

- Windows Event Log
- Splunk
- Azure Log Analytics
- ELK Stack
- Custom providers

### 5. Maintenance ✅

- No custom code to maintain
- Active development
- Bug fixes and improvements from community

## Installation

### Prerequisites

```powershell
# Install PSFramework
Install-Module -Name PSFramework -Scope CurrentUser -Force
```

### Verify

```powershell
Get-Module -ListAvailable -Name PSFramework
Import-Module PSFramework
Get-Command -Module PSFramework | Where-Object { $_.Name -like '*Log*' }
```

## Usage Examples

### Basic Usage

```powershell
# Import module (automatically loads PSFramework)
Import-Module GDS.Common

# Initialize logging
Initialize-Logging -ModuleName "ActiveDirectory"

# Write logs
Write-Log -Message "Processing user" -Level Info
Write-Log -Message "Error occurred" -Level Error -Exception $_.Exception
```

### Advanced Configuration

```powershell
# Configure with Event Log support
Set-GDSLogging -ModuleName "ActiveDirectory" `
    -EnableEventLog `
    -MinimumLevel "Debug" `
    -LogPath "C:\Logs\AD.log"
```

### Query Logs

```powershell
# Get recent messages from memory
Get-PSFMessage

# Filter by tag
Get-PSFMessage -Tag "Error", "ActiveDirectory"

# Filter by level
Get-PSFMessage -Level Error
```

## Log Locations

### Default

- **Path**: `Join-Path $env:GDS_LOG_DIR "{ModuleName}_{yyyyMMdd}.log"`
- **Example (Windows)**: `M:\GDS\Logs\ActiveDirectory_20240115.log`
- **Example (Linux)**: `/var/log/gds/ActiveDirectory_20240115.log`

> When `ModuleName` is omitted, the log owner defaults to the calling script so downstream modules share the same log file.

### Custom

```powershell
$env:GDS_LOG_DIR = "/var/log/gds"
Initialize-Logging -ModuleName "ActiveDirectory" -LogPath (Join-Path $env:GDS_LOG_DIR "AD.log")
```

> If `GDS_LOG_DIR` is not defined the module chooses a platform-specific default in this order:
>
> - Windows: `M:\GDS\Logs`, then `%ALLUSERSPROFILE%\GDS\Logs`
> - Linux/macOS: `/gds/log`, then `/var/log/gds`
> Set the environment variable if you need a different location.

## Migration Checklist

- ✅ GDS.Common updated to use PSFramework
- ✅ Write-Log wrapper maintains backward compatibility
- ✅ Initialize-Logging configures PSFramework providers
- ✅ Set-GDSLogging provides advanced configuration
- ✅ Documentation updated
- ✅ Migration guide created

## Next Steps

1. **Install PSFramework** on systems using GDS modules
2. **Test logging** in development environment
3. **Configure output targets** as needed (Event Log, Splunk, etc.)
4. **Update documentation** for your specific use cases

## Support

### PSFramework Resources

- [Documentation](https://psframework.org/documentation/documents/psframework/logging.html)
- [GitHub](https://github.com/PowershellFrameworkCollective/psframework)
- [PowerShell Gallery](https://www.powershellgallery.com/packages/PSFramework)

### Troubleshooting

- Check PSFramework installation: `Get-Module -ListAvailable -Name PSFramework`
- View log configuration: `Get-PSFLoggingProvider`
- Check minimum log level: `Get-PSFConfig -FullName 'PSFramework.Logging.MinimumLevel'`
- View in-memory messages: `Get-PSFMessage`

## Conclusion

The migration to PSFramework provides:

- ✅ Industry-standard logging
- ✅ Better features and performance
- ✅ Multiple integration options
- ✅ Reduced maintenance burden
- ✅ Backward compatibility

**All existing code continues to work without changes**, while gaining access to PSFramework's comprehensive logging capabilities.

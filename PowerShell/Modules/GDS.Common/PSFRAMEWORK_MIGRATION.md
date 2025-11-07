# PSFramework Logging Migration Guide

## Overview

GDS modules have been migrated from custom `Write-Log` implementation to **PSFramework**, the de facto standard for PowerShell logging. This provides better features, performance, and industry alignment.

## Why PSFramework?

1. **De Facto Standard**: Widely adopted in PowerShell community
2. **Feature Rich**: Multiple output targets, structured logging, async operations
3. **Performance**: Asynchronous logging with minimal impact
4. **Integration**: Supports Splunk, Azure, Event Log, and more
5. **Maintained**: Active development and community support

## Installation

### Prerequisites
```powershell
# Install PSFramework from PowerShell Gallery
Install-Module -Name PSFramework -Scope CurrentUser -Force
```

### Verify Installation
```powershell
Get-Module -ListAvailable -Name PSFramework
Import-Module PSFramework
Get-Command -Module PSFramework | Where-Object { $_.Name -like '*Log*' }
```

## Usage

### Basic Logging

```powershell
# Import GDS.Common (automatically imports PSFramework)
Import-Module GDS.Common

# Initialize logging for your module
Initialize-Logging -ModuleName "ActiveDirectory"

# Write log entries
Write-Log -Message "Processing user" -Level Info
Write-Log -Message "Error occurred" -Level Error -Exception $_.Exception
Write-Log -Message "Operation completed" -Level Info -Context @{Count=100; Duration="2.5s"}
```

### Advanced Configuration

```powershell
# Configure logging with custom settings
Set-GDSLogging -ModuleName "ActiveDirectory" `
    -EnableEventLog `
    -MinimumLevel "Debug" `
    -LogPath "C:\Logs\AD.log" `
    -MaxLogSizeMB 50 `
    -RetentionDays 60
```

### Direct PSFramework Usage

You can also use PSFramework directly:

```powershell
# Direct PSFramework usage
Write-PSFMessage -Level Important -Message "Processing user" -Tag "ActiveDirectory", "Processing"
Write-PSFMessage -Level Error -Message "Error occurred" -Exception $_.Exception
```

## Migration from Custom Write-Log

### Before (Custom Implementation)
```powershell
Write-Log -Message "Processing user" -Level Info -Context @{User="jdoe"}
```

### After (PSFramework)
```powershell
# Same syntax - backward compatible!
Write-Log -Message "Processing user" -Level Info -Context @{User="jdoe"}
```

**The function signature is compatible**, so existing code continues to work.

## Log Levels

| Custom Level | PSFramework Level | Description |
|-------------|-------------------|-------------|
| Debug | Debug | Detailed debugging information |
| Verbose | Verbose | Verbose information |
| Info | Important | General informational messages |
| Warning | Warning | Warning messages |
| Error | Error | Error messages |
| Critical | Critical | Critical errors |

## Log Locations

### Default Location
- **Path**: `$env:APPDATA\PSFramework\Logs\`
- **Format**: `{ModuleName}_{yyyyMMdd}.log`
- **Example**: `C:\Users\Username\AppData\Roaming\PSFramework\Logs\ActiveDirectory_20240115.log`

### Custom Location
```powershell
Initialize-Logging -ModuleName "ActiveDirectory" -LogPath "C:\Logs\AD.log"
```

## Features

### 1. Automatic Log Rotation
- Rotates when file size exceeds limit (default: 10MB)
- Maintains retention policy (default: 30 days)
- Configurable via `MaxLogSizeMB` and `RetentionDays`

### 2. Multiple Output Targets
- **File**: Structured file logging
- **Console**: Console output
- **Event Log**: Windows Event Log integration
- **Splunk**: Splunk integration (via provider)
- **Azure**: Azure Log Analytics (via provider)

### 3. Structured Logging
- JSON format support
- Rich metadata (tags, function names, context)
- Exception details with stack traces

### 4. Performance
- Asynchronous logging (no blocking)
- Runspace-safe (concurrent operations)
- Minimal performance impact

### 5. Query and Analysis
```powershell
# Get recent log messages from memory
Get-PSFMessage

# Get messages with specific tags
Get-PSFMessage -Tag "Error", "ActiveDirectory"

# Get messages by level
Get-PSFMessage -Level Error
```

## Configuration

### Module-Level Configuration
```powershell
# In module manifest (GDS.Common.psd1)
RequiredModules = @(
    @{ ModuleName = 'PSFramework'; ModuleVersion = '1.7.0' }
)
```

### Runtime Configuration
```powershell
# Set minimum log level globally
Set-PSFConfig -FullName 'PSFramework.Logging.MinimumLevel' -Value 'Important'

# Configure specific provider
Set-PSFLoggingProvider -Name 'logfile' -InstanceName 'MyModule' -Enabled $true
```

## Benefits

1. **Industry Standard**: Aligns with PowerShell community best practices
2. **Feature Rich**: More capabilities than custom implementation
3. **Maintained**: Active development and support
4. **Performance**: Asynchronous, non-blocking operations
5. **Integration**: Supports multiple output targets
6. **Structured**: Rich metadata and context support

## Troubleshooting

### PSFramework Not Found
```powershell
# Install PSFramework
Install-Module -Name PSFramework -Scope CurrentUser -Force

# Verify installation
Get-Module -ListAvailable -Name PSFramework
```

### Logs Not Appearing
```powershell
# Check logging configuration
Get-PSFLoggingProvider

# Check minimum log level
Get-PSFConfig -FullName 'PSFramework.Logging.MinimumLevel'

# Enable debug logging
Set-PSFConfig -FullName 'PSFramework.Logging.MinimumLevel' -Value 'Debug'
```

### Performance Issues
- PSFramework uses asynchronous logging by default
- If issues persist, check log file size and rotation settings
- Consider adjusting `MaxLogSizeMB` and `RetentionDays`

## References

- [PSFramework Documentation](https://psframework.org/documentation/documents/psframework/logging.html)
- [PSFramework GitHub](https://github.com/PowershellFrameworkCollective/psframework)
- [PSFramework PowerShell Gallery](https://www.powershellgallery.com/packages/PSFramework)

## Support

For issues or questions:
1. Check PSFramework documentation
2. Review log files in `$env:APPDATA\PSFramework\Logs\`
3. Use `Get-PSFMessage` for in-memory debugging
4. Check PSFramework GitHub issues

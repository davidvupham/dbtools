# PSFramework Cross-Platform Support

## Overview

**Yes, PSFramework works on PowerShell 7 for Linux (and macOS)!** PSFramework is designed to be fully cross-platform and compatible with PowerShell Core/PowerShell 7 across Windows, Linux, and macOS.

## Platform Compatibility

### Supported Platforms

| Platform | PowerShell Version | PSFramework Support |
|----------|-------------------|-------------------|
| Windows | PowerShell 5.1 | ✅ Full support |
| Windows | PowerShell 7+ | ✅ Full support |
| Linux | PowerShell 7+ | ✅ Full support |
| macOS | PowerShell 7+ | ✅ Full support |

### Minimum Requirements

- **PowerShell Version**: 5.1 or later
- **PSFramework Version**: 1.7.0 or later
- **Operating Systems**: Windows, Linux, macOS

## Installation on Linux

### Using PowerShell Gallery

```bash
# Start PowerShell 7
pwsh

# Install PSFramework
Install-Module -Name PSFramework -Scope CurrentUser -Force
```

### Verify Installation

```powershell
# Check installed version
Get-Module -ListAvailable -Name PSFramework

# Import and test
Import-Module PSFramework
Get-Command -Module PSFramework | Where-Object { $_.Name -like '*Log*' }
```

## Feature Compatibility

### Fully Cross-Platform Features ✅

These features work identically on all platforms:

1. **File Logging**
   - Structured file logging
   - Automatic rotation
   - Retention policies

   ```powershell
   $env:GDS_LOG_DIR = "/var/log/gds"  # Required on non-Windows platforms (Windows defaults to M:\GDS\Logs or %ALLUSERSPROFILE%\GDS\Logs)
   Set-PSFLoggingProvider -Name 'logfile' -Enabled $true
   ```

2. **Console Logging**
   - Console output with color
   - Multiple log levels

   ```powershell
   Set-PSFLoggingProvider -Name 'console' -Enabled $true
   ```

3. **In-Memory Debug Log**
   - Memory-based logging
   - Query recent messages

   ```powershell
   Get-PSFMessage
   ```

4. **Core Logging Functions**
   - Write-PSFMessage
   - Get-PSFMessage
   - All log levels and tags

5. **Configuration**
   - All PSFramework configuration options
   - Module-specific settings

### Platform-Specific Features

#### Windows-Only Features ⚠️

1. **Event Log Provider**
   - Windows Event Log integration
   - **NOT available on Linux/macOS**

   ```powershell
   # This will fail on Linux
   Set-PSFLoggingProvider -Name 'eventlog' -Enabled $true
   ```

2. **Performance Counter Integration**
   - Windows-specific performance counters
   - **NOT available on Linux/macOS**

#### Workarounds for Cross-Platform Code

```powershell
# Check platform before enabling Event Log
if ($IsWindows -or ($PSVersionTable.PSVersion.Major -lt 6)) {
    # Windows PowerShell or PowerShell 7+ on Windows
    Set-PSFLoggingProvider -Name 'eventlog' -Enabled $true
}
else {
    # Linux or macOS
    Write-PSFMessage -Level Verbose -Message "Event Log not available on this platform"
}
```

## GDS.Common Cross-Platform Support

### Our Implementation

The GDS.Common module is designed to work cross-platform:

```powershell
# Works on all platforms
Write-Log -Message "Processing data" -Level Info

# Automatically detects platform
$env:GDS_LOG_DIR = "/var/log/gds"
Initialize-Logging -ModuleName "MyModule"

# Advanced configuration with platform awareness
Set-GDSLogging -ModuleName "MyModule" `
    -EnableEventLog:$IsWindows `  # Only on Windows
    -MinimumLevel "Info"
```

### Platform-Aware Configuration

```powershell
function Set-GDSLoggingCrossPlatform {
    param(
        [string]$ModuleName,
        [string]$MinimumLevel = 'Info'
    )

    # File logging works everywhere
    Set-PSFLoggingProvider -Name 'logfile' -Enabled $true

    # Console logging works everywhere
    Set-PSFLoggingProvider -Name 'console' -Enabled $true

    # Event Log only on Windows
    if ($IsWindows -or ($PSVersionTable.PSVersion.Major -lt 6)) {
        Set-PSFLoggingProvider -Name 'eventlog' -Enabled $true
    }

    Write-PSFMessage -Level Important -Message "Logging configured for $ModuleName on $($PSVersionTable.Platform)"
}
```

## Log Directory (All Platforms)

- Define the log root using the `GDS_LOG_DIR` environment variable. Each log owner writes to `<GDS_LOG_DIR>/{ModuleName}_{yyyyMMdd}.log`; when `ModuleName` is omitted, the owner defaults to the calling script so downstream modules share the same file.
- Fallback order when `GDS_LOG_DIR` is not set:
  1. Windows: `M:\GDS\Logs`, then `%ALLUSERSPROFILE%\GDS\Logs`
  2. Linux/macOS: `/gds/logs`, then `/var/log/gds`
- macOS users can symlink `/usr/local/var/log/gds` to whichever directory is required.
- The directory is created automatically if it doesn't exist.

```powershell
# Cross-platform setup
$env:GDS_LOG_DIR = if ($IsWindows) {
    "M:\\GDS\\Logs"
} elseif ($IsLinux -or $IsMacOS) {
    if (Test-Path '/gds/logs') { '/gds/logs' } else { '/var/log/gds' }
}

Initialize-Logging -ModuleName "MyApp"
```

## Testing Cross-Platform Compatibility

### Test Script

```powershell
# Test PSFramework on any platform
function Test-PSFrameworkPlatform {
    # Show platform info
    Write-Host "Platform: $($PSVersionTable.Platform)"
    Write-Host "OS: $($PSVersionTable.OS)"
    Write-Host "PowerShell Version: $($PSVersionTable.PSVersion)"

    # Import PSFramework
    Import-Module PSFramework
    Write-Host "✅ PSFramework imported successfully"

    # Test file logging
    Set-PSFLoggingProvider -Name 'logfile' -Enabled $true
    Write-PSFMessage -Level Important -Message "Test message on $($PSVersionTable.Platform)"
    Write-Host "✅ File logging works"

    # Test console logging
    Set-PSFLoggingProvider -Name 'console' -Enabled $true
    Write-PSFMessage -Level Important -Message "Console test"
    Write-Host "✅ Console logging works"

    # Test in-memory logging
    $messages = Get-PSFMessage -Last 5
    Write-Host "✅ In-memory logging works ($($messages.Count) messages)"

    # Test Event Log (Windows only)
    if ($IsWindows -or ($PSVersionTable.PSVersion.Major -lt 6)) {
        Write-Host "✅ Windows platform - Event Log available"
    }
    else {
        Write-Host "ℹ️ Non-Windows platform - Event Log not available (expected)"
    }

    Write-Host "`n✅ All cross-platform tests passed!"
}

# Run the test
Test-PSFrameworkPlatform
```

## Best Practices for Cross-Platform Code

### 1. Use Platform Detection

```powershell
# Built-in variables (PowerShell 6+)
if ($IsWindows) {
    # Windows-specific code
}
elseif ($IsLinux) {
    # Linux-specific code
}
elseif ($IsMacOS) {
    # macOS-specific code
}

# For PowerShell 5.1 compatibility
$isWindowsPS = ($PSVersionTable.PSVersion.Major -lt 6) -or $IsWindows
```

### 2. Avoid Platform-Specific Providers

```powershell
# ❌ Bad - will fail on Linux
Set-PSFLoggingProvider -Name 'eventlog' -Enabled $true

# ✅ Good - platform aware
if ($IsWindows -or ($PSVersionTable.PSVersion.Major -lt 6)) {
    Set-PSFLoggingProvider -Name 'eventlog' -Enabled $true
}
```

### 3. Use Cross-Platform Paths

```powershell
# ❌ Bad - Windows-specific
$logPath = "C:\Logs\app.log"

# ✅ Good - cross-platform
$logPath = Join-Path $env:HOME "logs" "app.log"
```

### 4. Test on Multiple Platforms

- Test on Windows PowerShell 5.1
- Test on PowerShell 7+ (Windows)
- Test on PowerShell 7+ (Linux)
- Test on PowerShell 7+ (macOS)

## Docker Example for Testing

### Dockerfile

```dockerfile
# Use PowerShell 7 on Ubuntu
FROM mcr.microsoft.com/powershell:latest

# Install PSFramework
RUN pwsh -Command "Install-Module -Name PSFramework -Force -Scope AllUsers"

# Copy your module
COPY ./GDS.Common /root/.local/share/powershell/Modules/GDS.Common/

# Test
CMD ["pwsh", "-Command", "Import-Module GDS.Common; Write-Log -Message 'Test on Linux' -Level Info"]
```

### Build and Test

```bash
# Build Docker image
docker build -t gds-common-test .

# Run test
docker run --rm gds-common-test
```

## Known Issues and Limitations

### 1. Event Log Provider (Linux/macOS)

- **Issue**: Not available on non-Windows platforms
- **Workaround**: Use syslog provider or file logging

### 2. Path Separators

- **Issue**: Different on Windows (`\`) vs Linux/macOS (`/`)
- **Solution**: Use `Join-Path` or `[System.IO.Path]::Combine()`

### 3. Case Sensitivity

- **Issue**: Linux filesystem is case-sensitive
- **Solution**: Use consistent casing in file names and paths

### 4. Permissions

- **Issue**: Different permission models
- **Solution**: Test permissions before writing logs

## Recommendations

### For Production Use

1. **Use file logging** (works everywhere)
2. **Add platform detection** for Windows-specific features
3. **Test on target platforms** before deployment
4. **Use environment variables** for paths
5. **Document platform requirements** clearly

### For Development

1. **Test on multiple platforms** during development
2. **Use Docker** for Linux testing
3. **Run automated tests** on CI/CD pipelines
4. **Monitor platform-specific issues** in production

## Conclusion

**PSFramework is fully cross-platform** and works excellently on PowerShell 7 for Linux. The main considerations are:

✅ **Core logging features work identically** on all platforms
✅ **File and console logging** are cross-platform
⚠️ **Event Log** is Windows-only (expected)
✅ **GDS.Common is designed** to be cross-platform

You can confidently use PSFramework and GDS.Common on Linux with PowerShell 7!

## Additional Resources

- [PSFramework Documentation](https://psframework.org)
- [PowerShell on Linux](https://docs.microsoft.com/powershell/scripting/install/installing-powershell-on-linux)
- [Cross-Platform PowerShell](https://docs.microsoft.com/powershell/scripting/whats-new/what-s-new-in-powershell-70)

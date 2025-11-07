# PSModulePath Setup Guide

## Overview

For GDS modules to be available system-wide, they should be placed in a directory that's part of the PowerShell module path (`$env:PSModulePath`). This allows you to use `Import-Module GDS.Common` instead of specifying full paths.

## Understanding PSModulePath

### What is PSModulePath?

`PSModulePath` is an environment variable that contains a list of directories where PowerShell looks for modules.

### View Current PSModulePath

```powershell
# View as list
$env:PSModulePath -split [System.IO.Path]::PathSeparator

# Or in PowerShell 7+
$env:PSModulePath -split ';' | Format-Table
```

### Default Locations

#### Windows (PowerShell 5.1)
1. `C:\Users\{Username}\Documents\WindowsPowerShell\Modules` (User scope)
2. `C:\Program Files\WindowsPowerShell\Modules` (AllUsers scope)
3. `C:\Windows\System32\WindowsPowerShell\v1.0\Modules` (System scope)

#### Windows (PowerShell 7+)
1. `C:\Users\{Username}\Documents\PowerShell\Modules` (User scope)
2. `C:\Program Files\PowerShell\Modules` (AllUsers scope)

#### Linux (PowerShell 7+)
1. `~/.local/share/powershell/Modules` (User scope)
2. `/usr/local/share/powershell/Modules` (AllUsers scope)

#### macOS (PowerShell 7+)
1. `~/.local/share/powershell/Modules` (User scope)
2. `/usr/local/share/powershell/Modules` (AllUsers scope)

## Installation Methods

### Method 1: Copy to User Module Directory (Recommended for Development)

#### Windows
```powershell
# Copy GDS modules to user module directory
$userModulePath = Join-Path ([Environment]::GetFolderPath('MyDocuments')) "PowerShell\Modules"
Copy-Item -Path ".\Modules\GDS.Common" -Destination "$userModulePath\GDS.Common" -Recurse -Force
Copy-Item -Path ".\Modules\GDS.ActiveDirectory" -Destination "$userModulePath\GDS.ActiveDirectory" -Recurse -Force

# Verify
Get-Module -ListAvailable -Name GDS.*
```

#### Linux/macOS
```bash
# Copy GDS modules to user module directory
mkdir -p ~/.local/share/powershell/Modules
cp -r ./Modules/GDS.Common ~/.local/share/powershell/Modules/
cp -r ./Modules/GDS.ActiveDirectory ~/.local/share/powershell/Modules/

# Verify
pwsh -Command "Get-Module -ListAvailable -Name GDS.*"
```

### Method 2: Add Custom Directory to PSModulePath (Recommended for Production)

#### Temporary (Current Session Only)

```powershell
# Add your modules directory
$customPath = "C:\Projects\dbtools\PowerShell\Modules"
$env:PSModulePath += [System.IO.Path]::PathSeparator + $customPath

# Verify
$env:PSModulePath -split [System.IO.Path]::PathSeparator
Get-Module -ListAvailable -Name GDS.*
```

#### Permanent (All Sessions)

**Windows:**
```powershell
# Add to user environment variable (persists across sessions)
$customPath = "C:\Projects\dbtools\PowerShell\Modules"
$currentPath = [Environment]::GetEnvironmentVariable('PSModulePath', 'User')
$newPath = $currentPath + [System.IO.Path]::PathSeparator + $customPath
[Environment]::SetEnvironmentVariable('PSModulePath', $newPath, 'User')

# Restart PowerShell and verify
$env:PSModulePath -split [System.IO.Path]::PathSeparator
```

**Linux/macOS:**
```bash
# Add to shell profile (~/.bashrc or ~/.zshrc)
echo 'export PSModulePath="$PSModulePath:/workspaces/dbtools/PowerShell/Modules"' >> ~/.bashrc

# Or for PowerShell profile
pwsh -Command "
Add-Content -Path \$PROFILE -Value \"`$env:PSModulePath += ':/workspaces/dbtools/PowerShell/Modules'\"
"

# Reload and verify
source ~/.bashrc
pwsh -Command '$env:PSModulePath -split ":"'
```

### Method 3: Install from NuGet Package (Recommended for Distribution)

```powershell
# Install from PowerShell Gallery (once published)
Install-Module -Name GDS.Common -Scope CurrentUser

# Or install from local package
Register-PSRepository -Name "Local" -SourceLocation ".\build\packages" -InstallationPolicy Trusted
Install-Module -Name GDS.Common -Repository "Local"
```

### Method 4: PowerShell Profile Setup

Add to your PowerShell profile for automatic loading:

```powershell
# Open profile
notepad $PROFILE  # Windows
# or
code $PROFILE     # VS Code
# or
nano $PROFILE     # Linux/macOS

# Add this line
$env:PSModulePath += [System.IO.Path]::PathSeparator + "C:\Projects\dbtools\PowerShell\Modules"

# Save and reload
. $PROFILE
```

## Verification

### Check Module is Available

```powershell
# List all GDS modules
Get-Module -ListAvailable -Name GDS.*

# Import and test
Import-Module GDS.Common
Get-Command -Module GDS.Common

# Test a function
Initialize-Logging -ModuleName "Test"
Write-Log -Message "Test" -Level Info
```

### Check Module Location

```powershell
# Find where module is loaded from
Get-Module GDS.Common | Format-List Name, Path, ModuleBase

# Should show path in PSModulePath
```

## Recommended Setup

### For Development

```powershell
# Add workspace to PSModulePath temporarily
$env:PSModulePath += [System.IO.Path]::PathSeparator + "/workspaces/dbtools/PowerShell/Modules"

# Or create symlink
New-Item -ItemType SymbolicLink `
    -Path (Join-Path ([Environment]::GetFolderPath('MyDocuments')) "PowerShell\Modules\GDS.Common") `
    -Target "C:\Projects\dbtools\PowerShell\Modules\GDS.Common"
```

### For Production

```powershell
# Install from published packages
Install-Module -Name GDS.Common -Scope AllUsers
Install-Module -Name GDS.ActiveDirectory -Scope AllUsers

# Verify
Get-Module -ListAvailable -Name GDS.*
```

### For CI/CD

```powershell
# In CI/CD pipeline, temporarily add to path
$env:PSModulePath = "./PowerShell/Modules" + [System.IO.Path]::PathSeparator + $env:PSModulePath

# Then import normally
Import-Module GDS.Common
Build-AllNuGetPackages
```

## Best Practices

1. **Development**: Add workspace modules to PSModulePath or use symlinks
2. **Testing**: Copy to user module directory
3. **Production**: Install from NuGet packages
4. **CI/CD**: Temporarily add to PSModulePath in build script

## Troubleshooting

### Module Not Found

```powershell
# Check PSModulePath
$env:PSModulePath -split [System.IO.Path]::PathSeparator

# Check if module exists in any path
Get-Module -ListAvailable -Name GDS.Common

# Force refresh module cache
Get-Module -ListAvailable -Refresh
```

### Multiple Versions

```powershell
# List all versions
Get-Module -ListAvailable -Name GDS.Common -All

# Import specific version
Import-Module GDS.Common -RequiredVersion "1.0.0"
```

### Permission Issues

```powershell
# Use CurrentUser scope instead of AllUsers
Install-Module -Name GDS.Common -Scope CurrentUser

# Or copy to user directory
Copy-Item -Path ".\Modules\GDS.Common" `
    -Destination (Join-Path ([Environment]::GetFolderPath('MyDocuments')) "PowerShell\Modules\GDS.Common") `
    -Recurse -Force
```

## Summary

**For all documentation and examples**, we now assume modules are in PSModulePath, so you can use:

```powershell
# Simple import (no paths needed)
Import-Module GDS.Common
Import-Module GDS.ActiveDirectory

# They just work!
Write-Log -Message "Hello" -Level Info
Export-ADObjectsToDatabase -Server "SQL01" -Database "AD"
```

This is cleaner and more standard PowerShell practice. ✅

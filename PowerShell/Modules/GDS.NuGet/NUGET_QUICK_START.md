# NuGet Package Build - Quick Start

## TL;DR

```powershell
# From PowerShell directory:

# Build all modules
.\BuildAllModules.ps1

# Or build with tests skipped (faster)
.\BuildAllModules.ps1 -SkipTests -Parallel

# Output: build/packages/*.nupkg
```

## Step-by-Step

### 1. Install Prerequisites

```powershell
# Install PSFramework (required by GDS.Common)
Install-Module -Name PSFramework -Scope CurrentUser -Force

# Install testing tools (optional, for validation)
Install-Module -Name Pester -Scope CurrentUser -Force
Install-Module -Name PSScriptAnalyzer -Scope CurrentUser -Force
```

### 2. Build Packages

#### Option A: Build All Modules (Recommended)

```powershell
# Navigate to PowerShell directory
cd /workspaces/dbtools/PowerShell

# Build all modules
.\BuildAllModules.ps1
```

#### Option B: Build Single Module

```powershell
# Import GDS.NuGet
Import-Module GDS.NuGet

# Build specific module
Build-NuGetPackage -ModuleName "GDS.ActiveDirectory"
```

### 3. Find Your Packages

```powershell
# Packages are in:
Get-ChildItem .\build\packages\*.nupkg

# Example output:
# GDS.Common.1.0.0.nupkg
# GDS.ActiveDirectory.1.0.0.nupkg
# GDS.MSSQL.Core.1.0.0.nupkg
```

### 4. Test Installation

```powershell
# Install from local package
$packagePath = ".\build\packages"
Install-Module -Name GDS.Common -Repository (
    Register-PSRepository -Name "Local" -SourceLocation $packagePath -InstallationPolicy Trusted -PassThru
).Name

# Test
Import-Module GDS.Common
Get-Command -Module GDS.Common
```

### 5. Publish (Optional)

```powershell
# To PowerShell Gallery
$apiKey = "your-api-key-from-powershellgallery.com"
Publish-NuGetPackage -ModuleName "GDS.Common" -NuGetApiKey $apiKey

# Or use the convenience script
.\BuildAllModules.ps1 -Publish -ApiKey $apiKey
```

## Common Commands

```powershell
# Build single module
Build-NuGetPackage -ModuleName "GDS.Common"

# Build all modules
Build-AllNuGetPackages

# Build in parallel (faster)
Build-AllNuGetPackages -Parallel

# Skip tests (faster development)
Build-AllNuGetPackages -SkipTests

# Force rebuild
Build-AllNuGetPackages -Force

# Build and publish
.\BuildAllModules.ps1 -Publish -ApiKey "your-key"
```

## Troubleshooting

### "Module manifest not found"
- Ensure you're in the PowerShell directory
- Check module has .psd1 file

### "PSFramework not found"
```powershell
Install-Module -Name PSFramework -Force
```

### "Tests failed"
```powershell
# Skip tests during build
Build-NuGetPackage -ModuleName "GDS.Common" -SkipTests
```

### "Package already exists"
```powershell
# Force rebuild
Build-NuGetPackage -ModuleName "GDS.Common" -Force
```

## More Information

- [NUGET_BUILD_HOWTO.md](./NUGET_BUILD_HOWTO.md) - Detailed how-to
- [NUGET_PACKAGING_GUIDE.md](./NUGET_PACKAGING_GUIDE.md) - Comprehensive guide
- [Build-Package-Examples.ps1](./Build-Package-Examples.ps1) - More examples

## Repository

Built packages go to: `PowerShell/build/packages/`

Format: `{ModuleName}.{Version}.nupkg`

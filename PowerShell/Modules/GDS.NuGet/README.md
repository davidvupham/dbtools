# GDS.NuGet Module

NuGet package building and publishing for GDS PowerShell modules.

## Overview

GDS.NuGet provides **NuGet package building and publishing** functionality for GDS modules:
- **Package Building** - Build NuGet packages (.nupkg) for PowerShell modules
- **Package Publishing** - Publish to PowerShell Gallery, JFrog Artifactory, Azure Artifacts
- **Validation** - PSScriptAnalyzer and Pester test integration
- **CI/CD Integration** - GitHub Actions workflows and scripts

## Purpose

This module is specifically for **build and deployment automation**:
- ✅ Building NuGet packages
- ✅ Publishing to repositories
- ✅ CI/CD pipeline integration
- ✅ Build validation and testing

**Note:** For logging functionality, see the **GDS.Common** module.

## Installation

### Prerequisites

```powershell
# Install PSFramework (via GDS.Common dependency)
Install-Module -Name PSFramework -Scope CurrentUser -Force

# Install GDS.Common (required dependency)
Install-Module -Name GDS.Common -Scope CurrentUser

# Install testing tools (optional, for validation)
Install-Module -Name Pester -Scope CurrentUser -MinimumVersion 5.0.0
Install-Module -Name PSScriptAnalyzer -Scope CurrentUser
```

### Install GDS.NuGet

```powershell
# From PowerShell Gallery (once published)
Install-Module -Name GDS.NuGet -Scope CurrentUser

# Or import from PSModulePath
Import-Module GDS.NuGet
```

## Quick Start

### Build a Package

```powershell
# Import module
Import-Module GDS.NuGet

# Build single module
Build-NuGetPackage -ModuleName "GDS.Common"

# Build all modules
Build-AllNuGetPackages -Parallel

# Output: build/packages/*.nupkg
```

### Publish to JFrog

```powershell
# Configure JFrog
$jfrogUrl = "https://mycompany.jfrog.io"
$jfrogRepo = "powershell-modules"
$sourceUrl = "$jfrogUrl/artifactory/api/nuget/v3/$jfrogRepo"
$publishUrl = "$jfrogUrl/artifactory/api/nuget/$jfrogRepo"

Register-PSRepository -Name 'JFrog' `
    -SourceLocation $sourceUrl `
    -PublishLocation $publishUrl `
    -InstallationPolicy Trusted

# Publish
Publish-NuGetPackage -ModuleName "GDS.Common" `
    -Repository "JFrog" `
    -NuGetApiKey "${user}:${token}"
```

## Functions

### Build-NuGetPackage
Builds a NuGet package for a PowerShell module.

```powershell
Build-NuGetPackage -ModuleName "GDS.Common" -Version "1.1.0" -Verbose
```

**Parameters:**
- `ModuleName` (required) - Module to build
- `ModulePath` (optional) - Module directory path
- `OutputPath` (optional) - Output directory
- `Version` (optional) - Version override
- `SkipTests` (optional) - Skip validation tests
- `SkipValidation` (optional) - Skip manifest validation
- `Force` (optional) - Force rebuild

### Build-AllNuGetPackages
Builds NuGet packages for all GDS modules.

```powershell
Build-AllNuGetPackages -Parallel -SkipTests
```

**Parameters:**
- `ModulesPath` (optional) - Modules directory path
- `OutputPath` (optional) - Output directory
- `ExcludeModules` (optional) - Modules to exclude
- `SkipTests` (optional) - Skip validation tests
- `Force` (optional) - Force rebuild
- `Parallel` (optional) - Build in parallel (faster)

### Publish-NuGetPackage
Publishes a NuGet package to a repository.

```powershell
Publish-NuGetPackage -ModuleName "GDS.Common" -Repository "JFrog" -NuGetApiKey $key
```

**Parameters:**
- `ModuleName` (required) - Module to publish
- `PackagePath` (optional) - Path to .nupkg file
- `Repository` (optional) - Target repository (default: PSGallery)
- `NuGetApiKey` (required) - API key for authentication
- `FeedUrl` (optional) - Feed URL for custom repositories

## Common Scenarios

### Scenario 1: Development Build

```powershell
# Quick build without tests
Import-Module GDS.NuGet
Build-NuGetPackage -ModuleName "GDS.Common" -SkipTests

# Or use convenience script
.\BuildAllModules.ps1 -SkipTests
```

### Scenario 2: Release Build

```powershell
Import-Module GDS.NuGet

# Update version
Update-ModuleManifest -Path .\Modules\GDS.Common\GDS.Common.psd1 -ModuleVersion "1.1.0"

# Build with full validation
Build-NuGetPackage -ModuleName "GDS.Common" -Verbose

# Publish to JFrog
Publish-NuGetPackage -ModuleName "GDS.Common" -Repository "JFrog" -NuGetApiKey $apiKey
```

### Scenario 3: Build All Modules

```powershell
Import-Module GDS.NuGet

# Build all in parallel
Build-AllNuGetPackages -Parallel -Verbose

# Or use convenience script
.\BuildAllModules.ps1 -Parallel
```

## CI/CD Integration

### GitHub Actions

Workflow already created: `.github/workflows/powershell-modules-jfrog.yml`

See [JFROG_CICD_GUIDE.md](./JFROG_CICD_GUIDE.md) for complete details.

### Manual CI/CD Script

```powershell
# build-pipeline.ps1
Import-Module GDS.NuGet

# Build all
$results = Build-AllNuGetPackages -Parallel
if ($results | Where-Object { -not $_.Success }) {
    exit 1
}

# Publish successful builds
$results | Where-Object Success | ForEach-Object {
    Publish-NuGetPackage -ModuleName $_.ModuleName -Repository "JFrog" -NuGetApiKey $apiKey
}
```

## Output

### Package Location
- **Default:** `PowerShell/build/packages/`
- **Format:** `{ModuleName}.{Version}.nupkg`
- **Example:** `GDS.Common.1.0.0.nupkg`

### Build Results

```powershell
$result = Build-NuGetPackage -ModuleName "GDS.Common"

# $result contains:
# - ModuleName
# - Version
# - PackagePath
# - Success (bool)
# - Errors (array)
# - Warnings (array)
```

## Dependencies

- **GDS.Common** (v1.0.0) - For logging
- **PSFramework** (v1.7.0+) - Via GDS.Common
- **PowerShellGet** - Built-in
- **Pester** (optional) - For testing
- **PSScriptAnalyzer** (optional) - For validation

## Documentation

### 📚 Tutorials (Learning-oriented)
- [nuget-tutorial.md](../../../docs/tutorials/powershell/nuget-tutorial.md) - Beginner-friendly NuGet packaging tutorial

### 📖 How-to Guides (Task-oriented)
- [github-actions-nuget-build.md](../../../docs/how-to/powershell/github-actions-nuget-build.md) - Build packages with GitHub Actions
- [nuget-quick-start.md](../../../docs/how-to/powershell/nuget-quick-start.md) - NuGet build quick reference
- [nuget-build-howto.md](../../../docs/how-to/powershell/nuget-build-howto.md) - Step-by-step build guide
- [jfrog-quick-start.md](../../../docs/how-to/powershell/jfrog-quick-start.md) - JFrog quick reference
- [jfrog-cicd-guide.md](../../../docs/how-to/powershell/jfrog-cicd-guide.md) - Complete JFrog + GitHub Actions guide

### 📋 Reference (Technical details)
- [nuget-packaging-guide.md](../../../docs/reference/powershell/nuget-packaging-guide.md) - Comprehensive packaging reference
- [package-build-summary.md](../../../docs/reference/powershell/package-build-summary.md) - Implementation details

### 💡 Examples
- [Build-Package-Examples.ps1](./Build-Package-Examples.ps1) - Runnable examples

### 🔧 Related Documentation
- [GDS.Common](../GDS.Common/README.md) - Logging module
- [PSModulePath Setup](../GDS.Common/PSMODULEPATH_SETUP.md) - Module path configuration
- [Module Organization](../../MODULE_ORGANIZATION.md) - Organization principles

## Troubleshooting

### Module Not Found

```powershell
# Check if GDS.NuGet is in PSModulePath
Get-Module -ListAvailable -Name GDS.NuGet

# Check GDS.Common is installed (dependency)
Get-Module -ListAvailable -Name GDS.Common
```

### Build Fails

```powershell
# Skip tests
Build-NuGetPackage -ModuleName "GDS.Common" -SkipTests

# Force rebuild
Build-NuGetPackage -ModuleName "GDS.Common" -Force

# Check manifest
Test-ModuleManifest .\Modules\GDS.Common\GDS.Common.psd1
```

### Publish Fails

```powershell
# Check repository registration
Get-PSRepository

# Re-register
Register-PSRepository -Name 'JFrog' -SourceLocation $url -InstallationPolicy Trusted

# Test credentials
# See JFROG_CICD_GUIDE.md for authentication troubleshooting
```

## Examples

See [Build-Package-Examples.ps1](./Build-Package-Examples.ps1) for complete runnable examples.

## External Resources

- [PowerShell Gallery](https://www.powershellgallery.com/)
- [JFrog Artifactory NuGet Repositories](https://www.jfrog.com/confluence/display/JFROG/NuGet+Repositories)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PowerShell Module Publishing](https://docs.microsoft.com/powershell/scripting/gallery/how-to/publishing-packages/)

---

**Module Name:** GDS.NuGet
**Purpose:** NuGet Package Building and Publishing
**Version:** 1.0.0
**Status:** Production Ready ✅
**Maintained By:** GDS Team

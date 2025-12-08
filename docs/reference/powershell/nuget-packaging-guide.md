# NuGet Package Build Guide for GDS PowerShell Modules

## Overview

This guide explains how to build NuGet packages for GDS PowerShell modules for distribution via PowerShell Gallery, Azure Artifacts, or private NuGet feeds.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Understanding NuGet Packages](#understanding-nuget-packages)
4. [Module Structure](#module-structure)
5. [Building Packages](#building-packages)
6. [Publishing Packages](#publishing-packages)
7. [Consuming Packages](#consuming-packages)
8. [CI/CD Integration](#cicd-integration)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

1. **PowerShell 5.1 or later** (PowerShell 7+ recommended)
2. **NuGet CLI** (optional, for advanced scenarios)
3. **Module Manifests** (.psd1 files) for each module

### Optional Tools

- **Azure DevOps CLI** (for Azure Artifacts)
- **Git** (for version control)
- **PSScriptAnalyzer** (for code quality)

### Installation

```powershell
# Install required PowerShell modules
Install-Module -Name PowerShellGet -Force -Scope CurrentUser
Install-Module -Name PSScriptAnalyzer -Scope CurrentUser

# Verify installation
Get-Command Publish-Module, Register-PSRepository
```

---

## Quick Start

### Build a Single Module

```powershell
# Navigate to the common module
cd PowerShell/Modules/GDS.Common

# Run the build script
.\Build-NuGetPackage.ps1 -ModuleName "GDS.Common"
```

### Build All Modules

```powershell
# From the PowerShell directory
.\Modules\GDS.Common\Build-AllNuGetPackages.ps1
```

### Output

Packages are created in: `PowerShell/build/packages/`

Example: `GDS.Common.1.0.0.nupkg`

---

## Understanding NuGet Packages

### What is a NuGet Package?

A NuGet package (`.nupkg`) is a ZIP archive containing:
- Module files (.psm1, .psd1, .ps1)
- Metadata (manifest)
- Dependencies
- Documentation

### PowerShell Module Package Structure

```
GDS.Common.1.0.0.nupkg
├── GDS.Common.nuspec          # Package metadata
├── tools/
│   └── (empty or install scripts)
└── content/
    └── GDS.Common/
        ├── GDS.Common.psd1    # Module manifest
        ├── GDS.Common.psm1    # Module file
        ├── Public/
        ├── Private/
        └── README.md
```

### Package Metadata (.nuspec)

The `.nuspec` file contains:
- Package ID
- Version
- Authors and owners
- Description
- Dependencies
- Tags
- Release notes

---

## Module Structure

### Required Files

Each module must have:

```
GDS.ModuleName/
├── GDS.ModuleName.psd1    # Module manifest (REQUIRED)
├── GDS.ModuleName.psm1    # Module file (REQUIRED)
├── README.md              # Documentation (RECOMMENDED)
├── Public/                # Public functions (OPTIONAL)
│   └── *.ps1
├── Private/               # Private functions (OPTIONAL)
│   └── *.ps1
└── tests/                 # Pester tests (RECOMMENDED)
    └── *.Tests.ps1
```

### Module Manifest (.psd1)

Ensure your manifest has:

```powershell
@{
    RootModule = 'GDS.Common.psm1'
    ModuleVersion = '1.0.0'                    # IMPORTANT: Semantic versioning
    GUID = '12345678-1234-1234-1234-123456789000'
    Author = 'GDS Team'
    CompanyName = 'GDS'
    Copyright = '(c) GDS Team. All rights reserved.'
    Description = 'Common utilities for GDS modules'  # IMPORTANT
    PowerShellVersion = '5.1'
    RequiredModules = @(                       # IMPORTANT: Dependencies
        @{ ModuleName = 'PSFramework'; ModuleVersion = '1.7.0' }
    )
    FunctionsToExport = @('Write-Log', 'Initialize-Logging')
    Tags = @('Common', 'Logging', 'GDS')      # IMPORTANT: For discovery
}
```

---

## Building Packages

### Using the Build Script

The `Build-NuGetPackage.ps1` script automates the build process:

```powershell
# Import GDS.Common
Import-Module GDS.Common

# Build a specific module
Build-NuGetPackage -ModuleName "GDS.Common" -OutputPath ".\build\packages"

# Build with version override
.\Build-NuGetPackage.ps1 -ModuleName "GDS.Common" -Version "1.1.0"

# Build with verbose output
.\Build-NuGetPackage.ps1 -ModuleName "GDS.Common" -Verbose

# Build without tests
.\Build-NuGetPackage.ps1 -ModuleName "GDS.Common" -SkipTests
```

### Build Process Steps

The script performs:

1. **Validation**
   - Verifies module manifest exists
   - Validates manifest structure
   - Checks dependencies

2. **Testing** (optional)
   - Runs PSScriptAnalyzer
   - Runs Pester tests

3. **Preparation**
   - Creates build directory
   - Copies module files
   - Excludes unnecessary files

4. **Packaging**
   - Generates .nuspec if needed
   - Creates .nupkg file
   - Validates package

5. **Output**
   - Displays package information
   - Shows file location

### Manual Build

```powershell
# 1. Ensure module manifest is valid
Test-ModuleManifest .\GDS.Common.psd1

# 2. Create output directory
New-Item -ItemType Directory -Path ".\build\packages" -Force

# 3. Build package using PowerShellGet
$modulePath = ".\Modules\GDS.Common"
$outputPath = ".\build\packages"

# Publish to local repository (creates .nupkg)
Register-PSRepository -Name "LocalTemp" -SourceLocation $outputPath -InstallationPolicy Trusted
Publish-Module -Path $modulePath -Repository "LocalTemp" -NuGetApiKey "temp"
Unregister-PSRepository -Name "LocalTemp"
```

### Versioning

Use **Semantic Versioning** (SemVer):

- **Major.Minor.Patch** (e.g., 1.0.0)
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes

```powershell
# Update version in manifest
Update-ModuleManifest -Path .\GDS.Common.psd1 -ModuleVersion "1.1.0"

# Then rebuild
.\Build-NuGetPackage.ps1 -ModuleName "GDS.Common"
```

---

## Publishing Packages

### To PowerShell Gallery

```powershell
# 1. Get API key from https://www.powershellgallery.com/
$apiKey = "your-api-key-here"

# 2. Publish module
Publish-Module -Path ".\Modules\GDS.Common" `
    -Repository "PSGallery" `
    -NuGetApiKey $apiKey

# Or publish the .nupkg directly
Publish-Module -Path ".\build\packages\GDS.Common.1.0.0.nupkg" `
    -Repository "PSGallery" `
    -NuGetApiKey $apiKey
```

### To Azure Artifacts

```powershell
# 1. Register Azure Artifacts feed
$feedUrl = "https://pkgs.dev.azure.com/{organization}/_packaging/{feed}/nuget/v2"
$pat = "your-personal-access-token"

Register-PSRepository -Name "AzureArtifacts" `
    -SourceLocation $feedUrl `
    -PublishLocation $feedUrl `
    -InstallationPolicy Trusted

# 2. Publish module
Publish-Module -Path ".\Modules\GDS.Common" `
    -Repository "AzureArtifacts" `
    -NuGetApiKey $pat
```

### To Private NuGet Feed

```powershell
# 1. Register private feed
$feedUrl = "https://your-nuget-server.com/nuget"
$apiKey = "your-api-key"

Register-PSRepository -Name "PrivateFeed" `
    -SourceLocation $feedUrl `
    -PublishLocation $feedUrl `
    -InstallationPolicy Trusted

# 2. Publish module
Publish-Module -Path ".\Modules\GDS.Common" `
    -Repository "PrivateFeed" `
    -NuGetApiKey $apiKey
```

### To Local File Share

```powershell
# 1. Set up file share as repository
$shareLocation = "\\server\share\PSModules"

Register-PSRepository -Name "FileShare" `
    -SourceLocation $shareLocation `
    -PublishLocation $shareLocation `
    -InstallationPolicy Trusted

# 2. Publish module (copies .nupkg to share)
Publish-Module -Path ".\Modules\GDS.Common" `
    -Repository "FileShare"
```

---

## Consuming Packages

### Install from PowerShell Gallery

```powershell
# Install latest version
Install-Module -Name GDS.Common -Scope CurrentUser

# Install specific version
Install-Module -Name GDS.Common -RequiredVersion "1.0.0"

# Update to latest
Update-Module -Name GDS.Common
```

### Install from Azure Artifacts

```powershell
# 1. Register feed (if not already)
$feedUrl = "https://pkgs.dev.azure.com/{organization}/_packaging/{feed}/nuget/v2"
Register-PSRepository -Name "AzureArtifacts" -SourceLocation $feedUrl

# 2. Install module
Install-Module -Name GDS.Common -Repository "AzureArtifacts"
```

### Install from Local Package

```powershell
# From local directory
Install-Module -Name GDS.Common -Repository "LocalRepo" `
    -Scope CurrentUser

# Or extract manually
Expand-Archive -Path ".\GDS.Common.1.0.0.nupkg" `
    -DestinationPath "$env:USERPROFILE\Documents\PowerShell\Modules\GDS.Common"
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/build-publish.yml
name: Build and Publish PowerShell Modules

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build NuGet Packages
        shell: pwsh
        run: |
          .\PowerShell\Modules\GDS.Common\Build-AllNuGetPackages.ps1

      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: nuget-packages
          path: PowerShell/build/packages/*.nupkg

      - name: Publish to PowerShell Gallery
        if: startsWith(github.ref, 'refs/tags/v')
        shell: pwsh
        env:
          PSGALLERY_API_KEY: ${{ secrets.PSGALLERY_API_KEY }}
        run: |
          Get-ChildItem ".\PowerShell\build\packages\*.nupkg" | ForEach-Object {
            Publish-Module -Path $_.FullName -Repository PSGallery -NuGetApiKey $env:PSGALLERY_API_KEY
          }
```

### Azure DevOps

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
  tags:
    include:
      - v*

pool:
  vmImage: 'windows-latest'

steps:
- task: PowerShell@2
  displayName: 'Build NuGet Packages'
  inputs:
    filePath: 'PowerShell/Modules/GDS.Common/Build-AllNuGetPackages.ps1'
    pwsh: true

- task: PublishBuildArtifacts@1
  displayName: 'Publish NuGet Packages'
  inputs:
    PathtoPublish: 'PowerShell/build/packages'
    ArtifactName: 'nuget-packages'

- task: PowerShell@2
  displayName: 'Publish to Azure Artifacts'
  condition: startsWith(variables['Build.SourceBranch'], 'refs/tags/v')
  inputs:
    targetType: 'inline'
    script: |
      $feedUrl = "$(AZURE_ARTIFACTS_FEED_URL)"
      $pat = "$(System.AccessToken)"
      Register-PSRepository -Name "AzureArtifacts" -SourceLocation $feedUrl
      Get-ChildItem ".\PowerShell\build\packages\*.nupkg" | ForEach-Object {
        Publish-Module -Path $_.FullName -Repository AzureArtifacts -NuGetApiKey $pat
      }
    pwsh: true
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - build
  - publish

build:
  stage: build
  script:
    - pwsh -File PowerShell/Modules/GDS.Common/Build-AllNuGetPackages.ps1
  artifacts:
    paths:
      - PowerShell/build/packages/*.nupkg
    expire_in: 1 week

publish:
  stage: publish
  only:
    - tags
  script:
    - |
      pwsh -Command "
      Get-ChildItem 'PowerShell/build/packages/*.nupkg' | ForEach-Object {
        Publish-Module -Path $_.FullName -Repository PSGallery -NuGetApiKey $env:PSGALLERY_API_KEY
      }"
```

---

## Troubleshooting

### Common Issues

#### 1. Module Manifest Invalid

**Error:** `Test-ModuleManifest : The specified module manifest is invalid`

**Solution:**
```powershell
# Validate manifest
Test-ModuleManifest .\GDS.Common.psd1

# Check for syntax errors
$manifest = Import-PowerShellDataFile .\GDS.Common.psd1
$manifest | Format-List
```

#### 2. Dependency Not Found

**Error:** `Cannot find dependency module 'PSFramework'`

**Solution:**
```powershell
# Install dependencies first
Install-Module -Name PSFramework -Scope CurrentUser

# Or update RequiredModules in manifest
Update-ModuleManifest -Path .\GDS.Common.psd1 `
    -RequiredModules @(@{ModuleName='PSFramework'; ModuleVersion='1.7.0'})
```

#### 3. Version Conflict

**Error:** `Module with version X.Y.Z already exists`

**Solution:**
```powershell
# Update version in manifest
Update-ModuleManifest -Path .\GDS.Common.psd1 -ModuleVersion "1.1.0"

# Or use -Force to overwrite
Publish-Module -Path .\GDS.Common -Force
```

#### 4. Permission Denied

**Error:** `Access denied to path 'build\packages'`

**Solution:**
```powershell
# Run as administrator or change output path
.\Build-NuGetPackage.ps1 -OutputPath "$env:USERPROFILE\Downloads\packages"
```

#### 5. Package Size Too Large

**Error:** `Package exceeds maximum size`

**Solution:**
```powershell
# Exclude unnecessary files in .nuspec
# Add to <files> section:
<file src="**\*.*" target="content" exclude="**\*.Tests.ps1;**\test\**" />
```

### Debug Build Issues

```powershell
# Enable verbose output
.\Build-NuGetPackage.ps1 -ModuleName "GDS.Common" -Verbose -Debug

# Check what files are included
Expand-Archive -Path ".\build\packages\GDS.Common.1.0.0.nupkg" -DestinationPath ".\temp"
Get-ChildItem ".\temp" -Recurse

# Validate package
Test-ModuleManifest ".\temp\GDS.Common\GDS.Common.psd1"
```

---

## Best Practices

### 1. Version Management

- Use semantic versioning (SemVer)
- Update version in manifest before building
- Tag releases in Git

```powershell
# Update version
Update-ModuleManifest -Path .\GDS.Common.psd1 -ModuleVersion "1.1.0"

# Tag in Git
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

### 2. Testing Before Publishing

```powershell
# Run tests
Invoke-Pester .\tests\

# Run script analyzer
Invoke-ScriptAnalyzer -Path .\

# Test import
Import-Module .\GDS.Common.psd1 -Force
Get-Command -Module GDS.Common
```

### 3. Documentation

- Keep README.md updated
- Include examples
- Document breaking changes

### 4. Dependencies

- Declare all dependencies in manifest
- Use minimum required versions
- Test with dependencies installed

### 5. Signing (Optional)

```powershell
# Sign module files
$cert = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert
Set-AuthenticodeSignature -FilePath .\GDS.Common.psm1 -Certificate $cert
```

---

## Reference

### Build Script Parameters

```powershell
.\Build-NuGetPackage.ps1 `
    -ModuleName "GDS.Common" `        # Module to build
    -OutputPath ".\build\packages" `  # Output directory
    -Version "1.0.0" `                # Override version
    -SkipTests `                      # Skip tests
    -Verbose                          # Verbose output
```

### Useful Commands

```powershell
# List installed modules
Get-Module -ListAvailable

# Find module in gallery
Find-Module -Name GDS.Common

# Get module info
Get-Module GDS.Common | Format-List

# Uninstall module
Uninstall-Module -Name GDS.Common

# Update all modules
Update-Module
```

---

## Additional Resources

- [PowerShell Gallery](https://www.powershellgallery.com/)
- [Publishing to PowerShell Gallery](https://docs.microsoft.com/powershell/scripting/gallery/how-to/publishing-packages/publishing-a-package)
- [Module Manifest Reference](https://docs.microsoft.com/powershell/module/microsoft.powershell.core/about/about_module_manifests)
- [Semantic Versioning](https://semver.org/)
- [Azure Artifacts](https://docs.microsoft.com/azure/devops/artifacts/)

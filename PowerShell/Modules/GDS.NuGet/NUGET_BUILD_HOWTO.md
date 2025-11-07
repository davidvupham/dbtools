# How To: Build NuGet Packages for GDS PowerShell Modules

## Quick Start

### 1. Build a Single Module

```powershell
# Import GDS.Common
Import-Module GDS.Common

# Build the package
Build-NuGetPackage -ModuleName "GDS.Common"

# Output: GDS.Common.1.0.0.nupkg in build/packages/
```

### 2. Build All Modules

```powershell
# Build all GDS modules at once
Build-AllNuGetPackages

# Or build in parallel for speed
Build-AllNuGetPackages -Parallel
```

### 3. Publish to PowerShell Gallery

```powershell
# Get your API key from https://www.powershellgallery.com/
$apiKey = "your-api-key-here"

# Publish
Publish-NuGetPackage -ModuleName "GDS.Common" -NuGetApiKey $apiKey
```

---

## Detailed Walkthrough

### Step 1: Prepare Your Module

#### Ensure Module Manifest is Valid

```powershell
# Navigate to your module
cd .\Modules\GDS.Common

# Test the manifest
Test-ModuleManifest .\GDS.Common.psd1

# Expected output: Module information (no errors)
```

#### Update Version (if needed)

```powershell
# Update to new version
Update-ModuleManifest -Path .\GDS.Common.psd1 -ModuleVersion "1.1.0"

# Verify
(Import-PowerShellDataFile .\GDS.Common.psd1).ModuleVersion
```

### Step 2: Run Tests (Recommended)

```powershell
# Run PSScriptAnalyzer
Invoke-ScriptAnalyzer -Path .\ -Recurse

# Run Pester tests (if available)
Invoke-Pester .\tests\

# Import and test manually
Import-Module .\GDS.Common.psd1 -Force
Get-Command -Module GDS.Common
```

### Step 3: Build the Package

```powershell
# Import GDS.Common
Import-Module GDS.Common

# Build with validation and tests
Build-NuGetPackage -ModuleName "GDS.Common" -Verbose

# Or skip tests for faster build
Build-NuGetPackage -ModuleName "GDS.Common" -SkipTests

# Build with custom output path
Build-NuGetPackage -ModuleName "GDS.Common" -OutputPath "C:\Packages"
```

### Step 4: Verify the Package

```powershell
# Find the package
$package = Get-ChildItem ".\build\packages\GDS.Common.*.nupkg" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

# Show package info
$package | Format-List Name, Length, LastWriteTime

# Extract and inspect contents
$tempDir = Join-Path $env:TEMP "PackageInspect"
Expand-Archive -Path $package.FullName -DestinationPath $tempDir -Force
explorer $tempDir  # Opens in File Explorer
```

### Step 5: Test Install Locally

```powershell
# Create a test location
$testPath = Join-Path $env:TEMP "TestModules"
New-Item -ItemType Directory -Path $testPath -Force

# Register as temporary repository
Register-PSRepository -Name "TestRepo" -SourceLocation $testPath -InstallationPolicy Trusted

# Copy package
Copy-Item $package.FullName -Destination $testPath

# Install from test repo
Install-Module -Name "GDS.Common" -Repository "TestRepo" -Scope CurrentUser -Force

# Test the module
Import-Module GDS.Common -Force
Get-Command -Module GDS.Common

# Clean up
Uninstall-Module -Name "GDS.Common" -Force
Unregister-PSRepository -Name "TestRepo"
```

### Step 6: Publish to Repository

#### Option A: PowerShell Gallery (Public)

```powershell
# Import GDS.Common
Import-Module GDS.Common

# Get API key from https://www.powershellgallery.com/
$apiKey = Read-Host "Enter PowerShell Gallery API Key" -AsSecureString
$apiKeyPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey)
)

# Publish
Publish-NuGetPackage -ModuleName "GDS.Common" -NuGetApiKey $apiKeyPlain

# Verify
Find-Module -Name "GDS.Common"
```

#### Option B: Azure Artifacts (Private)

```powershell
# Set up Azure Artifacts
$organization = "yourorg"
$feed = "yourfeed"
$feedUrl = "https://pkgs.dev.azure.com/$organization/_packaging/$feed/nuget/v2"
$pat = "your-personal-access-token"

# Publish
Publish-NuGetPackage -ModuleName "GDS.Common" `
    -Repository "AzureArtifacts" `
    -FeedUrl $feedUrl `
    -NuGetApiKey $pat

# Verify
Find-Module -Name "GDS.Common" -Repository "AzureArtifacts"
```

#### Option C: Local File Share

```powershell
# Set up file share
$shareLocation = "\\server\share\PSModules"

# Register repository
Register-PSRepository -Name "FileShare" `
    -SourceLocation $shareLocation `
    -PublishLocation $shareLocation `
    -InstallationPolicy Trusted

# Publish (just copies the file)
Copy-Item $package.FullName -Destination $shareLocation

# Verify
Find-Module -Name "GDS.Common" -Repository "FileShare"
```

---

## Common Scenarios

### Scenario 1: Initial Release

```powershell
# 1. Ensure version is set
Update-ModuleManifest -Path .\Modules\GDS.Common\GDS.Common.psd1 -ModuleVersion "1.0.0"

# 2. Run all tests
Invoke-ScriptAnalyzer -Path .\ -Recurse
Invoke-Pester .\tests\

# 3. Build package
Build-NuGetPackage -ModuleName "GDS.Common"

# 4. Test locally
# ... (see Step 5 above)

# 5. Publish to gallery
Publish-NuGetPackage -ModuleName "GDS.Common" -NuGetApiKey $apiKey
```

### Scenario 2: Bug Fix Release (Patch)

```powershell
# 1. Increment patch version (1.0.0 -> 1.0.1)
Update-ModuleManifest -Path .\GDS.Common.psd1 -ModuleVersion "1.0.1"

# 2. Build and publish quickly
Build-NuGetPackage -ModuleName "GDS.Common" -SkipTests
Publish-NuGetPackage -ModuleName "GDS.Common" -NuGetApiKey $apiKey
```

### Scenario 3: Feature Release (Minor)

```powershell
# 1. Increment minor version (1.0.1 -> 1.1.0)
Update-ModuleManifest -Path .\GDS.Common.psd1 -ModuleVersion "1.1.0"

# 2. Run full test suite
Invoke-Pester .\tests\ -CodeCoverage

# 3. Build with validation
Build-NuGetPackage -ModuleName "GDS.Common" -Verbose

# 4. Publish
Publish-NuGetPackage -ModuleName "GDS.Common" -NuGetApiKey $apiKey
```

### Scenario 4: Breaking Change Release (Major)

```powershell
# 1. Increment major version (1.1.0 -> 2.0.0)
Update-ModuleManifest -Path .\GDS.Common.psd1 -ModuleVersion "2.0.0"

# 2. Update release notes
Update-ModuleManifest -Path .\GDS.Common.psd1 -ReleaseNotes @"
Version 2.0.0
- BREAKING: Changed function signature for Write-Log
- Added new features X, Y, Z
"@

# 3. Full validation
Test-ModuleManifest .\GDS.Common.psd1
Invoke-ScriptAnalyzer -Path .\ -Recurse
Invoke-Pester .\tests\

# 4. Build and publish
Build-NuGetPackage -ModuleName "GDS.Common"
Publish-NuGetPackage -ModuleName "GDS.Common" -NuGetApiKey $apiKey
```

### Scenario 5: Build All Modules for Release

```powershell
# 1. Update versions for all modules (if needed)
$modules = Get-ChildItem .\Modules -Directory | Where-Object { $_.Name -like "GDS.*" }
foreach ($module in $modules) {
    $manifestPath = Join-Path $module.FullName "$($module.Name).psd1"
    if (Test-Path $manifestPath) {
        Update-ModuleManifest -Path $manifestPath -ModuleVersion "1.0.0"
    }
}

# 2. Build all in parallel
Build-AllNuGetPackages -Parallel -Verbose

# 3. Review results
$results = Build-AllNuGetPackages -Parallel
$results | Format-Table ModuleName, Version, Success, @{L='Errors';E={$_.Errors.Count}}

# 4. Publish successful builds
$results | Where-Object { $_.Success } | ForEach-Object {
    Publish-NuGetPackage -ModuleName $_.ModuleName -NuGetApiKey $apiKey
}
```

### Scenario 6: CI/CD Pipeline

```powershell
# Typical CI/CD workflow
param(
    [string]$ApiKey,
    [string]$Version
)

try {
    # 1. Update versions
    if ($Version) {
        $modules = Get-ChildItem .\Modules -Directory
        foreach ($module in $modules) {
            $manifest = Join-Path $module.FullName "$($module.Name).psd1"
            if (Test-Path $manifest) {
                Update-ModuleManifest -Path $manifest -ModuleVersion $Version
            }
        }
    }

    # 2. Build all
    $results = Build-AllNuGetPackages -Verbose

    # 3. Check for failures
    $failures = $results | Where-Object { -not $_.Success }
    if ($failures) {
        Write-Error "Build failed for: $($failures.ModuleName -join ', ')"
        exit 1
    }

    # 4. Publish (if API key provided)
    if ($ApiKey) {
        foreach ($result in $results) {
            if ($result.Success) {
                Publish-NuGetPackage -ModuleName $result.ModuleName -NuGetApiKey $ApiKey
            }
        }
    }

    Write-Host "✓ CI/CD pipeline completed successfully" -ForegroundColor Green
}
catch {
    Write-Error "CI/CD pipeline failed: $_"
    exit 1
}
```

---

## Tips and Tricks

### Tip 1: View Package Contents

```powershell
# Extract package to temp location
$package = ".\build\packages\GDS.Common.1.0.0.nupkg"
$tempDir = Join-Path $env:TEMP "PackageView"
Expand-Archive -Path $package -DestinationPath $tempDir -Force

# View structure
Get-ChildItem $tempDir -Recurse | Format-Table FullName

# Open in editor
code $tempDir
```

### Tip 2: Compare Versions

```powershell
# Extract two versions
Expand-Archive ".\build\packages\GDS.Common.1.0.0.nupkg" -Destination ".\temp\v1"
Expand-Archive ".\build\packages\GDS.Common.1.1.0.nupkg" -Destination ".\temp\v2"

# Compare
Compare-Object (Get-ChildItem .\temp\v1 -Recurse) (Get-ChildItem .\temp\v2 -Recurse)
```

### Tip 3: Batch Build Multiple Modules

```powershell
# Build specific modules
$modulesToBuild = @("GDS.Common", "GDS.ActiveDirectory", "GDS.MSSQL.Core")

foreach ($moduleName in $modulesToBuild) {
    Build-NuGetPackage -ModuleName $moduleName -SkipTests
}
```

### Tip 4: Automated Version Bumping

```powershell
function Update-ModuleVersion {
    param(
        [string]$ModulePath,
        [ValidateSet('Major', 'Minor', 'Patch')]
        [string]$BumpType
    )

    $manifestPath = Join-Path $ModulePath "$((Get-Item $ModulePath).Name).psd1"
    $manifest = Import-PowerShellDataFile $manifestPath
    $currentVersion = [version]$manifest.ModuleVersion

    $newVersion = switch ($BumpType) {
        'Major' { "$($currentVersion.Major + 1).0.0" }
        'Minor' { "$($currentVersion.Major).$($currentVersion.Minor + 1).0" }
        'Patch' { "$($currentVersion.Major).$($currentVersion.Minor).$($currentVersion.Build + 1)" }
    }

    Update-ModuleManifest -Path $manifestPath -ModuleVersion $newVersion
    Write-Host "Updated $((Get-Item $ModulePath).Name) from $currentVersion to $newVersion"
}

# Usage
Update-ModuleVersion -ModulePath .\Modules\GDS.Common -BumpType Patch
Build-NuGetPackage -ModuleName "GDS.Common"
```

### Tip 5: Build Script for Production

```powershell
# production-build.ps1
param(
    [Parameter(Mandatory)]
    [ValidateSet('Development', 'Staging', 'Production')]
    [string]$Environment,

    [string]$ApiKey
)

Write-Host "Building packages for: $Environment" -ForegroundColor Cyan

# Set version suffix based on environment
$versionSuffix = switch ($Environment) {
    'Development' { 'dev' }
    'Staging' { 'beta' }
    'Production' { $null }
}

# Build all modules
$results = Build-AllNuGetPackages -SkipTests:($Environment -eq 'Development')

# Display summary
$results | Format-Table ModuleName, Version, Success

# Publish if production
if ($Environment -eq 'Production' -and $ApiKey) {
    $results | Where-Object { $_.Success } | ForEach-Object {
        Publish-NuGetPackage -ModuleName $_.ModuleName -NuGetApiKey $ApiKey
    }
}
```

---

## Troubleshooting

### Issue: "Module manifest not found"

```powershell
# Check module structure
Get-ChildItem .\Modules\GDS.Common

# Should have:
# GDS.Common.psd1 (required)
# GDS.Common.psm1 (required)
```

### Issue: "Tests failed"

```powershell
# Run tests manually to see details
Invoke-Pester .\Modules\GDS.Common\tests\ -Output Detailed

# Or skip tests during build
Build-NuGetPackage -ModuleName "GDS.Common" -SkipTests
```

### Issue: "Package already exists"

```powershell
# Force rebuild
Build-NuGetPackage -ModuleName "GDS.Common" -Force

# Or increment version
Update-ModuleManifest -Path .\Modules\GDS.Common\GDS.Common.psd1 -ModuleVersion "1.0.1"
Build-NuGetPackage -ModuleName "GDS.Common"
```

### Issue: "Permission denied"

```powershell
# Run PowerShell as Administrator, or
# Use a different output path
Build-NuGetPackage -ModuleName "GDS.Common" -OutputPath "$env:USERPROFILE\Downloads\packages"
```

---

## Complete Example: End-to-End

```powershell
# Complete workflow from scratch

# 1. Navigate to PowerShell directory
cd C:\Projects\dbtools\PowerShell

# 2. Import GDS.Common
Import-Module .\Modules\GDS.Common\GDS.Common.psd1 -Force

# 3. Set version for new release
Update-ModuleManifest -Path .\Modules\GDS.Common\GDS.Common.psd1 -ModuleVersion "1.1.0"

# 4. Update release notes
Update-ModuleManifest -Path .\Modules\GDS.Common\GDS.Common.psd1 -ReleaseNotes @"
Version 1.1.0
- Added PSFramework logging support
- Added NuGet package build functions
- Improved cross-platform compatibility
"@

# 5. Run tests
Write-Host "Running tests..." -ForegroundColor Yellow
Invoke-ScriptAnalyzer -Path .\Modules\GDS.Common -Recurse
Invoke-Pester .\Modules\GDS.Common\tests\

# 6. Build package
Write-Host "`nBuilding package..." -ForegroundColor Yellow
$buildResult = Build-NuGetPackage -ModuleName "GDS.Common" -Verbose

# 7. Check build result
if ($buildResult.Success) {
    Write-Host "✓ Build successful!" -ForegroundColor Green
    Write-Host "Package: $($buildResult.PackagePath)" -ForegroundColor Gray
}
else {
    Write-Host "✗ Build failed!" -ForegroundColor Red
    $buildResult.Errors | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    exit 1
}

# 8. Test install locally
Write-Host "`nTesting local install..." -ForegroundColor Yellow
$testPath = Join-Path $env:TEMP "TestRepo"
New-Item -ItemType Directory -Path $testPath -Force | Out-Null
Register-PSRepository -Name "TestRepo" -SourceLocation $testPath -InstallationPolicy Trusted
Copy-Item $buildResult.PackagePath -Destination $testPath
Install-Module -Name "GDS.Common" -Repository "TestRepo" -Force

# 9. Verify installation
Import-Module GDS.Common -Force
Get-Command -Module GDS.Common
Write-Host "✓ Local install successful!" -ForegroundColor Green

# 10. Clean up test
Uninstall-Module -Name "GDS.Common" -Force
Unregister-PSRepository -Name "TestRepo"

# 11. Publish to PowerShell Gallery (optional)
$publish = Read-Host "Publish to PowerShell Gallery? (Y/N)"
if ($publish -eq 'Y') {
    $apiKey = Read-Host "Enter API Key" -AsSecureString
    $apiKeyPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey)
    )

    Publish-NuGetPackage -ModuleName "GDS.Common" -NuGetApiKey $apiKeyPlain
    Write-Host "✓ Published to PowerShell Gallery!" -ForegroundColor Green
}

Write-Host "`n✓ Complete end-to-end workflow finished!" -ForegroundColor Green
```

---

## Quick Reference

### Commands

```powershell
# Build single module
Build-NuGetPackage -ModuleName "GDS.Common"

# Build all modules
Build-AllNuGetPackages

# Build in parallel
Build-AllNuGetPackages -Parallel

# Skip tests
Build-NuGetPackage -ModuleName "GDS.Common" -SkipTests

# Force rebuild
Build-NuGetPackage -ModuleName "GDS.Common" -Force

# Publish
Publish-NuGetPackage -ModuleName "GDS.Common" -NuGetApiKey $key
```

### File Locations

- **Modules**: `PowerShell/Modules/`
- **Build Output**: `PowerShell/build/packages/`
- **Package Format**: `{ModuleName}.{Version}.nupkg`
- **Example**: `GDS.Common.1.0.0.nupkg`

### Version Format

- **Semantic Versioning**: `Major.Minor.Patch`
- **Major**: Breaking changes
- **Minor**: New features (compatible)
- **Patch**: Bug fixes

---

## See Also

- [NuGet Packaging Guide](./NUGET_PACKAGING_GUIDE.md) - Comprehensive guide
- [Build-NuGetPackage.ps1](./Public/Build-NuGetPackage.ps1) - Function source
- [Build-AllNuGetPackages.ps1](./Public/Build-AllNuGetPackages.ps1) - Function source
- [Publish-NuGetPackage.ps1](./Public/Publish-NuGetPackage.ps1) - Function source
- [PowerShell Gallery](https://www.powershellgallery.com/)

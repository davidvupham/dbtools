# Building NuGet Packages for PowerShell Modules: A Beginner's Tutorial

> **Learning Objectives**: By the end of this tutorial, you'll understand what NuGet packages are, how PowerShell uses them, and how to create your own packages from scratch.

---

## 📚 Part 1: Understanding the Fundamentals

### What is a NuGet Package?

Think of a NuGet package like a **gift box for code**. Just as you'd wrap a gift in a box with a label describing what's inside, a NuGet package wraps your PowerShell module with metadata that describes it.

```
┌─────────────────────────────────────────┐
│           .nupkg file (ZIP)             │
├─────────────────────────────────────────┤
│  📋 Metadata (who made it, version)     │
│  📁 Your PowerShell module files        │
│  📝 Documentation & dependencies        │
└─────────────────────────────────────────┘
```

**Real-world analogy**: NuGet packages are like apps in an app store. The PowerShell Gallery is the "app store," and your NuGet package is the "app" that users can download and install.

### Why Package PowerShell Modules?

| Without Packaging | With NuGet Package |
|-------------------|-------------------|
| Share via zip files or file shares | Install with one command: `Install-Module` |
| Manual version tracking | Automatic version management |
| No dependency handling | Dependencies installed automatically |
| Difficult to update | Easy updates via `Update-Module` |

### The Relationship: PowerShell Gallery ↔ NuGet

```
┌────────────────────┐
│  PowerShell Gallery│  ← Uses NuGet infrastructure under the hood
│    (Repository)    │
└─────────┬──────────┘
          │
    ┌─────▼─────┐
    │  .nupkg   │  ← Your packaged module
    │  package  │
    └─────┬─────┘
          │
    ┌─────▼─────┐
    │ PowerShell│  ← Users install with Install-Module
    │  Module   │
    └───────────┘
```

> [!NOTE]
> PowerShell Gallery uses NuGet's infrastructure, but wraps it with PowerShell-specific commands like `Publish-Module` and `Install-Module` instead of the generic `nuget push`.

---

## 📚 Part 2: Anatomy of a PowerShell Module (The Source)

Before we package anything, let's understand what makes up a PowerShell module.

### Required Files

Every PowerShell module needs at minimum two files:

```
MyModule/
├── MyModule.psd1    # 👈 Module MANIFEST (the "ID card")
└── MyModule.psm1    # 👈 Module SCRIPT (the actual code)
```

#### The Manifest (.psd1) - Your Module's ID Card

The manifest is the most critical file. It's a PowerShell hashtable that describes your module:

```powershell
# MyModule.psd1 - Example with explanations
@{
    # BASIC IDENTITY
    # ──────────────
    RootModule = 'MyModule.psm1'        # Points to your main script file
    ModuleVersion = '1.0.0'             # Follow Semantic Versioning (Major.Minor.Patch)
    GUID = 'ab12cd34-ef56-7890-ab12-cd34ef567890'  # Unique identifier (generate with New-Guid)
    Author = 'Your Name'                # Who wrote this
    CompanyName = 'Your Company'        # Organization
    Copyright = '(c) 2024 Your Name'    # Legal copyright
    Description = 'What this module does in one sentence'  # REQUIRED for publishing!
    
    # COMPATIBILITY
    # ─────────────
    PowerShellVersion = '5.1'           # Minimum PowerShell version needed
    
    # DEPENDENCIES
    # ────────────
    RequiredModules = @(
        # Other modules this depends on
        @{ ModuleName = 'PSFramework'; ModuleVersion = '1.7.0' }
    )
    
    # EXPORTS - What functions users can call
    # ───────
    FunctionsToExport = @(
        'Get-Something',
        'Set-Something',
        'New-Something'
    )
    CmdletsToExport = @()      # Usually empty for script modules
    VariablesToExport = @()    # Usually empty (don't export variables)
    AliasesToExport = @()      # Usually empty
    
    # METADATA FOR POWERSHELL GALLERY
    # ────────────────────────────────
    PrivateData = @{
        PSData = @{
            Tags = @('Tag1', 'Tag2')     # Helps users find your module
            LicenseUri = 'https://...'   # Link to license
            ProjectUri = 'https://...'   # Link to project/docs
            ReleaseNotes = 'What is new in this version'
        }
    }
}
```

> [!IMPORTANT]
> The `Description` field is **required** for publishing to PowerShell Gallery. Packages without descriptions will be rejected.

#### The Module Script (.psm1) - Your Code

This is where your actual PowerShell functions live:

```powershell
# MyModule.psm1 - Example structure

# Load private (internal) functions first
. $PSScriptRoot\Private\Helper-Function.ps1

# Load public (exported) functions
. $PSScriptRoot\Public\Get-Something.ps1
. $PSScriptRoot\Public\Set-Something.ps1

# Export only what users should access
Export-ModuleMember -Function Get-Something, Set-Something
```

### Recommended Folder Structure

A well-organized module looks like this:

```
MyModule/
├── MyModule.psd1           # Module manifest
├── MyModule.psm1           # Module loader script
├── README.md               # Documentation
├── Public/                 # Functions users can call
│   ├── Get-Something.ps1
│   └── Set-Something.ps1
├── Private/                # Internal helper functions
│   └── Helper-Function.ps1
└── tests/                  # Pester tests
    └── MyModule.Tests.ps1
```

> [!TIP]
> Keep each function in its own file. This makes code easier to maintain and test.

---

## 📚 Part 3: Creating a Module from Scratch (Hands-On Example)

Let's create a simple module step by step.

### Step 1: Create the Folder Structure

```powershell
# Create the module directory
$moduleName = "Demo.Calculator"
$modulePath = "C:\Modules\$moduleName"
New-Item -ItemType Directory -Path $modulePath -Force
New-Item -ItemType Directory -Path "$modulePath\Public" -Force
New-Item -ItemType Directory -Path "$modulePath\Private" -Force
New-Item -ItemType Directory -Path "$modulePath\tests" -Force
```

### Step 2: Create a Simple Function

```powershell
# Create Public/Add-Numbers.ps1
$functionCode = @'
function Add-Numbers {
    <#
    .SYNOPSIS
        Adds two numbers together.
    
    .DESCRIPTION
        A simple function that demonstrates module creation.
        Takes two numbers and returns their sum.
    
    .PARAMETER Number1
        The first number to add.
    
    .PARAMETER Number2
        The second number to add.
    
    .EXAMPLE
        Add-Numbers -Number1 5 -Number2 3
        # Returns: 8
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [double]$Number1,
        
        [Parameter(Mandatory)]
        [double]$Number2
    )
    
    return $Number1 + $Number2
}
'@

Set-Content -Path "$modulePath\Public\Add-Numbers.ps1" -Value $functionCode
```

### Step 3: Create the Module Script (.psm1)

```powershell
# Create Demo.Calculator.psm1
$moduleCode = @'
# Get all function files
$publicFunctions = Get-ChildItem -Path "$PSScriptRoot\Public\*.ps1" -ErrorAction SilentlyContinue
$privateFunctions = Get-ChildItem -Path "$PSScriptRoot\Private\*.ps1" -ErrorAction SilentlyContinue

# Dot-source all functions
foreach ($function in @($publicFunctions) + @($privateFunctions)) {
    try {
        . $function.FullName
    }
    catch {
        Write-Error "Failed to import function $($function.Name): $_"
    }
}

# Export only public functions
Export-ModuleMember -Function $publicFunctions.BaseName
'@

Set-Content -Path "$modulePath\$moduleName.psm1" -Value $moduleCode
```

### Step 4: Create the Module Manifest (.psd1)

PowerShell has a built-in command to generate manifests:

```powershell
# Generate a new GUID for your module
$guid = [guid]::NewGuid().ToString()

# Create the manifest
New-ModuleManifest -Path "$modulePath\$moduleName.psd1" `
    -RootModule "$moduleName.psm1" `
    -ModuleVersion '1.0.0' `
    -GUID $guid `
    -Author 'Your Name' `
    -CompanyName 'Your Company' `
    -Copyright '(c) 2024 Your Name. All rights reserved.' `
    -Description 'A simple calculator module for demonstration purposes.' `
    -PowerShellVersion '5.1' `
    -FunctionsToExport @('Add-Numbers') `
    -CmdletsToExport @() `
    -VariablesToExport @() `
    -AliasesToExport @() `
    -Tags @('Calculator', 'Math', 'Demo') `
    -ProjectUri 'https://github.com/yourrepo'
```

### Step 5: Test Your Module

```powershell
# Validate the manifest
Test-ModuleManifest -Path "$modulePath\$moduleName.psd1"

# Import and test the module
Import-Module $modulePath -Force -Verbose

# List available commands
Get-Command -Module $moduleName

# Test the function
Add-Numbers -Number1 5 -Number2 3
# Output: 8
```

---

## 📚 Part 4: Building the NuGet Package

Now that we have a working module, let's package it!

### Method 1: Using Publish-Module (Simplest)

The easiest way to create a `.nupkg` file is using `Publish-Module` with a local repository:

```powershell
# Step 1: Create a local folder to act as a repository
$repoPath = "C:\LocalNuGetRepo"
New-Item -ItemType Directory -Path $repoPath -Force

# Step 2: Register it as a PowerShell repository
Register-PSRepository -Name "LocalRepo" `
    -SourceLocation $repoPath `
    -PublishLocation $repoPath `
    -InstallationPolicy Trusted

# Step 3: Publish your module (this creates the .nupkg!)
Publish-Module -Path $modulePath -Repository "LocalRepo"

# Step 4: Check the result
Get-ChildItem $repoPath
# You should see: Demo.Calculator.1.0.0.nupkg
```

> [!TIP]
> This method is perfect for creating packages quickly without installing additional tools.

### Method 2: Using nuget.exe (More Control)

For advanced scenarios, you can use the NuGet CLI:

```powershell
# Step 1: Install NuGet CLI (if not installed)
# Download from: https://www.nuget.org/downloads
# Or use winget:
winget install Microsoft.NuGet

# Step 2: Create a .nuspec file
$nuspecContent = @"
<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2011/08/nuspec.xsd">
  <metadata>
    <id>Demo.Calculator</id>
    <version>1.0.0</version>
    <authors>Your Name</authors>
    <owners>Your Name</owners>
    <description>A simple calculator module for demonstration.</description>
    <tags>Calculator Math Demo PowerShell</tags>
  </metadata>
  <files>
    <file src="**\*.*" target="content\Demo.Calculator" />
  </files>
</package>
"@
Set-Content -Path "$modulePath\Demo.Calculator.nuspec" -Value $nuspecContent

# Step 3: Build the package
nuget pack "$modulePath\Demo.Calculator.nuspec" -OutputDirectory "C:\LocalNuGetRepo"
```

### Understanding the .nupkg Structure

A NuGet package is just a ZIP file with a different extension. Let's peek inside:

```powershell
# Rename to .zip to explore
$package = "C:\LocalNuGetRepo\Demo.Calculator.1.0.0.nupkg"
$exploreDir = "C:\Temp\PackageExplore"

# Extract the package
Expand-Archive -Path $package -DestinationPath $exploreDir -Force

# See what's inside
Get-ChildItem $exploreDir -Recurse | Format-Table FullName
```

You'll see something like:
```
C:\Temp\PackageExplore\
├── Demo.Calculator.nuspec      # Package metadata
├── [Content_Types].xml         # NuGet internal
├── _rels\                      # NuGet internal
│   └── .rels
└── content\                    # Your module files
    └── Demo.Calculator\
        ├── Demo.Calculator.psd1
        ├── Demo.Calculator.psm1
        └── Public\
            └── Add-Numbers.ps1
```

---

## 📚 Part 5: Publishing Your Package

### Option A: PowerShell Gallery (Public)

The PowerShell Gallery is the official public repository for PowerShell modules.

```powershell
# Step 1: Create an account at https://www.powershellgallery.com/

# Step 2: Get your API key from your account settings

# Step 3: Publish!
$apiKey = "your-api-key-here"  # Keep this secret!

Publish-Module -Path $modulePath `
    -Repository "PSGallery" `
    -NuGetApiKey $apiKey `
    -Verbose

# Step 4: Verify it's published
Find-Module -Name "Demo.Calculator"
```

> [!CAUTION]
> **Never** commit your API key to source control! Use environment variables or secure storage.

### Option B: Azure Artifacts (Private/Enterprise)

For enterprise scenarios, Azure Artifacts provides private feeds:

```powershell
# Step 1: Set up your feed URL (from Azure DevOps portal)
$feedUrl = "https://pkgs.dev.azure.com/YourOrg/_packaging/YourFeed/nuget/v2"
$pat = "your-personal-access-token"

# Step 2: Register the feed as a repository
Register-PSRepository -Name "AzureArtifacts" `
    -SourceLocation $feedUrl `
    -PublishLocation $feedUrl `
    -InstallationPolicy Trusted

# Step 3: Publish
Publish-Module -Path $modulePath `
    -Repository "AzureArtifacts" `
    -NuGetApiKey $pat
```

### Option C: File Share Repository (Simple Enterprise)

For simpler scenarios, use a network file share:

```powershell
# Step 1: Create a network share
$sharePath = "\\server\PowerShellModules"

# Step 2: Register as a repository
Register-PSRepository -Name "CompanyModules" `
    -SourceLocation $sharePath `
    -PublishLocation $sharePath `
    -InstallationPolicy Trusted

# Step 3: Publish (just copies the .nupkg)
Publish-Module -Path $modulePath -Repository "CompanyModules"

# Team members can now install:
Install-Module -Name "Demo.Calculator" -Repository "CompanyModules"
```

---

## 📚 Part 6: Versioning Best Practices

### Semantic Versioning (SemVer)

Follow the **Major.Minor.Patch** format:

| Version Part | When to Increment | Example Changes |
|--------------|-------------------|-----------------|
| **Major** (X.0.0) | Breaking changes | Renamed functions, removed parameters |
| **Minor** (1.X.0) | New features (backward compatible) | Added new functions |
| **Patch** (1.0.X) | Bug fixes | Fixed typos, bug corrections |

```powershell
# Update version in manifest
Update-ModuleManifest -Path "$modulePath\Demo.Calculator.psd1" -ModuleVersion "1.1.0"

# Add release notes (optional but recommended)
Update-ModuleManifest -Path "$modulePath\Demo.Calculator.psd1" -ReleaseNotes @"
Version 1.1.0:
- Added Subtract-Numbers function
- Fixed rounding issue in Add-Numbers
"@
```

### Pre-release Versions

For beta/alpha releases:

```powershell
# In the manifest, use Prerelease field in PSData
PrivateData = @{
    PSData = @{
        Prerelease = 'beta1'  # Results in version: 1.0.0-beta1
    }
}
```

```powershell
# Install pre-release versions
Install-Module -Name "Demo.Calculator" -AllowPrerelease
```

---

## 📚 Part 7: Complete Workflow Example

Here's a complete workflow from development to publishing:

```powershell
#requires -Version 5.1

<#
.SYNOPSIS
    Complete module build and publish workflow.
#>

# Configuration
$ModuleName = "Demo.Calculator"
$ModulePath = "C:\Modules\$ModuleName"
$OutputPath = "C:\Packages"
$Version = "1.0.0"

# Step 1: Validate the module
Write-Host "📋 Validating module manifest..." -ForegroundColor Cyan
$manifest = Test-ModuleManifest -Path "$ModulePath\$ModuleName.psd1"
Write-Host "   Module: $($manifest.Name) v$($manifest.Version)" -ForegroundColor Green

# Step 2: Run PSScriptAnalyzer (code quality)
Write-Host "`n🔍 Running PSScriptAnalyzer..." -ForegroundColor Cyan
$analysisResults = Invoke-ScriptAnalyzer -Path $ModulePath -Recurse
if ($analysisResults) {
    Write-Warning "Found $($analysisResults.Count) issues:"
    $analysisResults | Format-Table -AutoSize
} else {
    Write-Host "   No issues found!" -ForegroundColor Green
}

# Step 3: Run Pester tests (if available)
Write-Host "`n🧪 Running Pester tests..." -ForegroundColor Cyan
if (Test-Path "$ModulePath\tests") {
    $testResults = Invoke-Pester -Path "$ModulePath\tests" -PassThru
    if ($testResults.FailedCount -gt 0) {
        throw "Tests failed! Fix issues before packaging."
    }
    Write-Host "   All tests passed!" -ForegroundColor Green
} else {
    Write-Host "   No tests found (skipping)" -ForegroundColor Yellow
}

# Step 4: Create the package
Write-Host "`n📦 Creating NuGet package..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

# Register temporary local repository
$tempRepoName = "TempBuildRepo"
if (Get-PSRepository -Name $tempRepoName -ErrorAction SilentlyContinue) {
    Unregister-PSRepository -Name $tempRepoName
}
Register-PSRepository -Name $tempRepoName `
    -SourceLocation $OutputPath `
    -PublishLocation $OutputPath `
    -InstallationPolicy Trusted

# Publish to local repo (creates .nupkg)
Publish-Module -Path $ModulePath -Repository $tempRepoName

# Cleanup temp repo
Unregister-PSRepository -Name $tempRepoName

# Step 5: Display results
$package = Get-ChildItem "$OutputPath\$ModuleName.*.nupkg" | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 1

Write-Host "`n✅ Package created successfully!" -ForegroundColor Green
Write-Host "   Location: $($package.FullName)" -ForegroundColor Gray
Write-Host "   Size: $([Math]::Round($package.Length / 1KB, 2)) KB" -ForegroundColor Gray

# Step 6: Optional - Test installation
Write-Host "`n🧪 Testing package installation..." -ForegroundColor Cyan
$testInstallPath = "$env:TEMP\TestInstall"
Register-PSRepository -Name "TestInstall" `
    -SourceLocation $OutputPath `
    -InstallationPolicy Trusted

Install-Module -Name $ModuleName -Repository "TestInstall" -Scope CurrentUser -Force
$installedModule = Get-Module -Name $ModuleName -ListAvailable

Write-Host "   Installed successfully at: $($installedModule.ModuleBase)" -ForegroundColor Green

# Cleanup
Uninstall-Module -Name $ModuleName -Force -ErrorAction SilentlyContinue
Unregister-PSRepository -Name "TestInstall"

Write-Host "`n🎉 Build workflow complete!" -ForegroundColor Green
```

---

## 📚 Part 8: Common Issues and Solutions

### Issue: "Module manifest not found"

**Cause**: The .psd1 file name doesn't match the folder name.

```powershell
# ❌ Wrong: Folder is "MyModule" but manifest is "MyMod.psd1"
# ✅ Correct: Both should be "MyModule"

# Fix: Rename to match
Rename-Item "MyMod.psd1" "MyModule.psd1"
```

### Issue: "The specified module manifest is invalid"

**Cause**: Syntax error in the .psd1 file.

```powershell
# Validate manifest with detailed errors
try {
    $null = Test-ModuleManifest -Path ".\MyModule.psd1" -ErrorAction Stop
    Write-Host "Manifest is valid!" -ForegroundColor Green
}
catch {
    Write-Host "Manifest error: $($_.Exception.Message)" -ForegroundColor Red
}

# Common fixes:
# 1. Ensure all hashtable entries end with proper syntax
# 2. Check for missing closing brackets @{ ... }
# 3. Verify all paths are correct (RootModule, etc.)
```

### Issue: "A module with version X already exists"

**Cause**: You're trying to publish a version that already exists.

```powershell
# Solution: Increment the version
Update-ModuleManifest -Path ".\MyModule.psd1" -ModuleVersion "1.0.1"
```

### Issue: "The module manifest's Description field is empty"

**Cause**: PowerShell Gallery requires a description.

```powershell
# Solution: Add a description
Update-ModuleManifest -Path ".\MyModule.psd1" `
    -Description "A module that does amazing things"
```

---

## 📚 Part 9: Quick Reference Card

### Essential Commands

```powershell
# CREATE MODULE MANIFEST
New-ModuleManifest -Path ".\MyModule.psd1" -ModuleVersion "1.0.0" -Author "Name"

# VALIDATE MANIFEST
Test-ModuleManifest -Path ".\MyModule.psd1"

# UPDATE VERSION
Update-ModuleManifest -Path ".\MyModule.psd1" -ModuleVersion "1.1.0"

# CREATE PACKAGE (Local Repository Method)
Register-PSRepository -Name "Local" -SourceLocation "C:\Packages" -PublishLocation "C:\Packages"
Publish-Module -Path ".\MyModule" -Repository "Local"

# PUBLISH TO POWERSHELL GALLERY
Publish-Module -Path ".\MyModule" -Repository "PSGallery" -NuGetApiKey $key

# INSTALL A MODULE
Install-Module -Name "MyModule" -Scope CurrentUser

# UPDATE A MODULE
Update-Module -Name "MyModule"
```

### Manifest Fields Quick Reference

| Field | Required | Purpose |
|-------|----------|---------|
| `RootModule` | Yes | Points to .psm1 file |
| `ModuleVersion` | Yes | Version number (SemVer) |
| `GUID` | Yes | Unique identifier |
| `Author` | Yes | Module author |
| `Description` | Yes* | Module description (*required for Gallery) |
| `FunctionsToExport` | Yes | Functions to make available |
| `RequiredModules` | No | Dependencies |
| `Tags` | No | Searchable tags |

---

## 🎓 Summary

You've learned:

1. **What NuGet packages are** - ZIP archives with metadata for distributing code
2. **PowerShell module structure** - .psd1 (manifest) + .psm1 (code)
3. **How to create a module** - Folder structure, functions, manifest
4. **How to build packages** - Using `Publish-Module` or `nuget.exe`
5. **Publishing options** - PowerShell Gallery, Azure Artifacts, file shares
6. **Versioning** - Semantic versioning (Major.Minor.Patch)
7. **Troubleshooting** - Common issues and fixes

### Next Steps

- Explore the other guides in this directory for advanced topics
- Set up CI/CD pipelines to automate builds
- Learn about code signing for trusted module distribution

---

## 📖 Additional Resources

| Resource | Link |
|----------|------|
| PowerShell Gallery | https://www.powershellgallery.com/ |
| NuGet Documentation | https://docs.nuget.org/ |
| Semantic Versioning | https://semver.org/ |
| Module Manifest Reference | https://docs.microsoft.com/powershell/module/microsoft.powershell.core/about/about_module_manifests |

---

*Tutorial created for the GDS PowerShell Modules project*

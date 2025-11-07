# JFrog Artifactory CI/CD Guide for GDS PowerShell Modules

## Overview

This guide covers the complete workflow for building, publishing, and consuming GDS PowerShell modules using JFrog Artifactory with GitHub Actions CI/CD.

## Table of Contents

1. [JFrog Artifactory Setup](#jfrog-artifactory-setup)
2. [GitHub Actions Workflow](#github-actions-workflow)
3. [Publishing to JFrog](#publishing-to-jfrog)
4. [Installing from JFrog](#installing-from-jfrog)
5. [Complete CI/CD Pipeline](#complete-cicd-pipeline)
6. [Troubleshooting](#troubleshooting)

---

## JFrog Artifactory Setup

### 1. Create NuGet Repository in JFrog

1. Log in to your JFrog Artifactory instance
2. Navigate to **Administration** → **Repositories** → **Local**
3. Click **New Local Repository**
4. Select **NuGet** as package type
5. Configure:
   - **Repository Key**: `powershell-modules-local`
   - **Description**: GDS PowerShell Modules
   - **Public Description**: (optional)
   - Click **Save & Finish**

### 2. Create Virtual Repository (Recommended)

1. Navigate to **Administration** → **Repositories** → **Virtual**
2. Click **New Virtual Repository**
3. Select **NuGet** as package type
4. Configure:
   - **Repository Key**: `powershell-modules`
   - **Description**: GDS PowerShell Modules (Virtual)
   - **Repositories**: Select `powershell-modules-local`
   - **Default Deployment Repository**: `powershell-modules-local`
   - Click **Save & Finish**

### 3. Generate API Key or Access Token

#### Option A: API Key (Legacy)
1. Click on your username → **Edit Profile**
2. Enter your password
3. Click **Generate API Key**
4. Copy the API key

#### Option B: Access Token (Recommended)
1. Click on your username → **Edit Profile**
2. Navigate to **Authentication Settings**
3. Click **Generate Token**
4. Configure:
   - **Token Scope**: Select required permissions
   - **Expiration**: Set appropriate expiration
   - Click **Generate**
5. Copy the access token

### 4. Get Repository URLs

Your JFrog URLs will be:
- **Source/Install URL**: `https://{instance}.jfrog.io/artifactory/api/nuget/v3/powershell-modules`
- **Publish URL**: `https://{instance}.jfrog.io/artifactory/api/nuget/powershell-modules-local`

Replace `{instance}` with your JFrog instance name.

---

## GitHub Actions Workflow

### 1. Set Up GitHub Secrets

In your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add the following secrets:
   - **JFROG_URL**: Your JFrog instance URL (e.g., `https://mycompany.jfrog.io`)
   - **JFROG_USER**: Your JFrog username
   - **JFROG_TOKEN**: Your JFrog API key or access token
   - **JFROG_REPO**: Repository name (e.g., `powershell-modules`)

### 2. Create GitHub Actions Workflow

Create `.github/workflows/build-publish-powershell.yml`:

```yaml
name: Build and Publish PowerShell Modules to JFrog

on:
  push:
    branches:
      - main
      - develop
    paths:
      - 'PowerShell/Modules/**'
  pull_request:
    branches:
      - main
    paths:
      - 'PowerShell/Modules/**'
  release:
    types: [published]
  workflow_dispatch:
    inputs:
      publish:
        description: 'Publish to JFrog'
        required: false
        default: 'false'

env:
  MODULES_PATH: PowerShell/Modules
  BUILD_OUTPUT: PowerShell/build/packages

jobs:
  build:
    name: Build PowerShell Modules
    runs-on: windows-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for versioning

      - name: Setup PowerShell
        shell: pwsh
        run: |
          $PSVersionTable | Format-List
          Write-Host "PowerShell version: $($PSVersionTable.PSVersion)"

      - name: Install PSFramework
        shell: pwsh
        run: |
          Write-Host "Installing PSFramework..."
          Install-Module -Name PSFramework -Force -Scope CurrentUser -Repository PSGallery
          Get-Module -ListAvailable -Name PSFramework

      - name: Install Build Dependencies
        shell: pwsh
        run: |
          Write-Host "Installing build dependencies..."
          Install-Module -Name Pester -Force -Scope CurrentUser -MinimumVersion 5.0.0
          Install-Module -Name PSScriptAnalyzer -Force -Scope CurrentUser

      - name: Add Modules to PSModulePath
        shell: pwsh
        run: |
          $modulesPath = Join-Path $env:GITHUB_WORKSPACE "PowerShell/Modules"
          $env:PSModulePath = "$modulesPath" + [System.IO.Path]::PathSeparator + $env:PSModulePath
          Write-Host "PSModulePath updated: $env:PSModulePath"

      - name: Import GDS.Common
        shell: pwsh
        run: |
          $modulesPath = Join-Path $env:GITHUB_WORKSPACE "PowerShell/Modules"
          $env:PSModulePath = "$modulesPath" + [System.IO.Path]::PathSeparator + $env:PSModulePath
          Import-Module GDS.Common -Force -Verbose
          Get-Command -Module GDS.Common

      - name: Run Tests
        shell: pwsh
        run: |
          $modulesPath = Join-Path $env:GITHUB_WORKSPACE "PowerShell/Modules"
          $env:PSModulePath = "$modulesPath" + [System.IO.Path]::PathSeparator + $env:PSModulePath

          Write-Host "Running PSScriptAnalyzer..."
          $analysisResults = Invoke-ScriptAnalyzer -Path $env:MODULES_PATH -Recurse -Severity Error,Warning

          if ($analysisResults) {
            $analysisResults | Format-Table -AutoSize
            $errorCount = ($analysisResults | Where-Object Severity -eq 'Error').Count
            if ($errorCount -gt 0) {
              Write-Error "PSScriptAnalyzer found $errorCount error(s)"
              exit 1
            }
          }

          Write-Host "Running Pester tests..."
          $testResults = Invoke-Pester -Path "$env:MODULES_PATH" -PassThru -Output Detailed

          if ($testResults.FailedCount -gt 0) {
            Write-Error "$($testResults.FailedCount) test(s) failed"
            exit 1
          }

      - name: Build NuGet Packages
        shell: pwsh
        run: |
          $modulesPath = Join-Path $env:GITHUB_WORKSPACE "PowerShell/Modules"
          $env:PSModulePath = "$modulesPath" + [System.IO.Path]::PathSeparator + $env:PSModulePath

          Import-Module GDS.Common -Force

          Write-Host "Building all GDS module packages..."
          $results = Build-AllNuGetPackages -Parallel -Verbose

          # Check for failures
          $failed = $results | Where-Object { -not $_.Success }
          if ($failed) {
            Write-Error "Build failed for: $($failed.ModuleName -join ', ')"
            $failed | ForEach-Object {
              Write-Error "  $($_.ModuleName): $($_.Errors -join '; ')"
            }
            exit 1
          }

          Write-Host "All packages built successfully!"
          $results | Format-Table ModuleName, Version, Success

      - name: Upload Build Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: nuget-packages
          path: PowerShell/build/packages/*.nupkg
          retention-days: 30

      - name: Display Build Summary
        shell: pwsh
        run: |
          Write-Host "`n=== Build Summary ===" -ForegroundColor Cyan
          $packages = Get-ChildItem -Path $env:BUILD_OUTPUT -Filter "*.nupkg"
          $packages | ForEach-Object {
            Write-Host "  ✓ $($_.Name) ($([math]::Round($_.Length/1KB, 2)) KB)" -ForegroundColor Green
          }
          Write-Host "`nTotal packages: $($packages.Count)" -ForegroundColor Cyan

  publish-jfrog:
    name: Publish to JFrog Artifactory
    needs: build
    runs-on: windows-latest
    # Only publish on main branch, release, or manual trigger
    if: |
      github.event_name == 'release' ||
      (github.event_name == 'push' && github.ref == 'refs/heads/main') ||
      (github.event_name == 'workflow_dispatch' && github.event.inputs.publish == 'true')

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Download Build Artifacts
        uses: actions/download-artifact@v4
        with:
          name: nuget-packages
          path: PowerShell/build/packages

      - name: Setup PowerShell
        shell: pwsh
        run: |
          Install-Module -Name PSFramework -Force -Scope CurrentUser

      - name: Add Modules to PSModulePath
        shell: pwsh
        run: |
          $modulesPath = Join-Path $env:GITHUB_WORKSPACE "PowerShell/Modules"
          $env:PSModulePath = "$modulesPath" + [System.IO.Path]::PathSeparator + $env:PSModulePath

      - name: Register JFrog Repository
        shell: pwsh
        env:
          JFROG_URL: ${{ secrets.JFROG_URL }}
          JFROG_REPO: ${{ secrets.JFROG_REPO }}
          JFROG_USER: ${{ secrets.JFROG_USER }}
          JFROG_TOKEN: ${{ secrets.JFROG_TOKEN }}
        run: |
          # Construct JFrog NuGet feed URL
          $sourceUrl = "$env:JFROG_URL/artifactory/api/nuget/v3/$env:JFROG_REPO"
          $publishUrl = "$env:JFROG_URL/artifactory/api/nuget/$env:JFROG_REPO"

          Write-Host "Registering JFrog repository..."
          Write-Host "Source URL: $sourceUrl"
          Write-Host "Publish URL: $publishUrl"

          # Register repository
          Register-PSRepository -Name 'JFrog' `
            -SourceLocation $sourceUrl `
            -PublishLocation $publishUrl `
            -InstallationPolicy Trusted `
            -PackageManagementProvider NuGet

          Get-PSRepository -Name 'JFrog' | Format-List

      - name: Publish Packages to JFrog
        shell: pwsh
        env:
          JFROG_USER: ${{ secrets.JFROG_USER }}
          JFROG_TOKEN: ${{ secrets.JFROG_TOKEN }}
        run: |
          $modulesPath = Join-Path $env:GITHUB_WORKSPACE "PowerShell/Modules"
          $env:PSModulePath = "$modulesPath" + [System.IO.Path]::PathSeparator + $env:PSModulePath

          Import-Module GDS.Common -Force

          # Get all built packages
          $packages = Get-ChildItem -Path $env:BUILD_OUTPUT -Filter "*.nupkg"

          Write-Host "`nPublishing $($packages.Count) package(s) to JFrog..." -ForegroundColor Cyan

          # Create credentials for authentication
          $credential = New-Object System.Management.Automation.PSCredential(
            $env:JFROG_USER,
            (ConvertTo-SecureString $env:JFROG_TOKEN -AsPlainText -Force)
          )

          foreach ($package in $packages) {
            try {
              Write-Host "`nPublishing: $($package.Name)..." -ForegroundColor Yellow

              # Extract module name from package
              $packageName = $package.BaseName -replace '\.\d+\.\d+\.\d+$', ''

              # Find module path
              $modulePath = Join-Path $env:GITHUB_WORKSPACE "PowerShell/Modules/$packageName"

              if (Test-Path $modulePath) {
                # Publish module
                Publish-Module -Path $modulePath `
                  -Repository 'JFrog' `
                  -NuGetApiKey "$($env:JFROG_USER):$($env:JFROG_TOKEN)" `
                  -Force `
                  -Verbose

                Write-Host "  ✓ Published successfully" -ForegroundColor Green
              }
              else {
                Write-Warning "  Module path not found: $modulePath"
              }
            }
            catch {
              Write-Error "  ✗ Failed to publish $($package.Name): $_"
              # Continue with other packages
            }
          }

      - name: Verify Publication
        shell: pwsh
        env:
          JFROG_URL: ${{ secrets.JFROG_URL }}
          JFROG_REPO: ${{ secrets.JFROG_REPO }}
          JFROG_USER: ${{ secrets.JFROG_USER }}
          JFROG_TOKEN: ${{ secrets.JFROG_TOKEN }}
        run: |
          # Register repository for verification
          $sourceUrl = "$env:JFROG_URL/artifactory/api/nuget/v3/$env:JFROG_REPO"
          Register-PSRepository -Name 'JFrogVerify' `
            -SourceLocation $sourceUrl `
            -InstallationPolicy Trusted `
            -ErrorAction SilentlyContinue

          Write-Host "`n=== Verifying Published Modules ===" -ForegroundColor Cyan

          # Find modules
          $modules = Find-Module -Repository 'JFrogVerify' -Name "GDS.*" -ErrorAction SilentlyContinue

          if ($modules) {
            $modules | Format-Table Name, Version, Repository
            Write-Host "✓ $($modules.Count) module(s) found in JFrog" -ForegroundColor Green
          }
          else {
            Write-Warning "No modules found in JFrog repository (may take a few moments to index)"
          }
```

### 3. Multi-Stage Workflow (Recommended)

Create `.github/workflows/powershell-modules-cicd.yml`:

```yaml
name: PowerShell Modules CI/CD

on:
  push:
    branches: [main, develop]
    paths:
      - 'PowerShell/Modules/**'
  pull_request:
    branches: [main]
  release:
    types: [published]
  workflow_dispatch:

env:
  MODULES_PATH: PowerShell/Modules
  BUILD_OUTPUT: PowerShell/build/packages

jobs:
  # Job 1: Validate
  validate:
    name: Validate Code
    runs-on: windows-latest

    steps:
      - uses: actions/checkout@v4

      - name: Install Tools
        shell: pwsh
        run: |
          Install-Module -Name PSScriptAnalyzer -Force -Scope CurrentUser
          Install-Module -Name Pester -Force -Scope CurrentUser -MinimumVersion 5.0.0

      - name: Run PSScriptAnalyzer
        shell: pwsh
        run: |
          $results = Invoke-ScriptAnalyzer -Path $env:MODULES_PATH -Recurse -Severity Error,Warning
          if ($results) {
            $results | Format-Table -AutoSize
            $errors = $results | Where-Object Severity -eq 'Error'
            if ($errors) {
              Write-Error "Found $($errors.Count) error(s)"
              exit 1
            }
          }

      - name: Run Pester Tests
        shell: pwsh
        run: |
          $config = New-PesterConfiguration
          $config.Run.Path = $env:MODULES_PATH
          $config.Run.Exit = $true
          $config.TestResult.Enabled = $true
          $config.TestResult.OutputPath = 'test-results.xml'
          $config.CodeCoverage.Enabled = $true

          Invoke-Pester -Configuration $config

      - name: Upload Test Results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: test-results.xml

  # Job 2: Build
  build:
    name: Build NuGet Packages
    needs: validate
    runs-on: windows-latest

    outputs:
      packages: ${{ steps.build-packages.outputs.packages }}

    steps:
      - uses: actions/checkout@v4

      - name: Install PSFramework
        shell: pwsh
        run: |
          Install-Module -Name PSFramework -Force -Scope CurrentUser

      - name: Setup PSModulePath
        shell: pwsh
        run: |
          $modulesPath = Join-Path $env:GITHUB_WORKSPACE $env:MODULES_PATH
          $env:PSModulePath = "$modulesPath" + [System.IO.Path]::PathSeparator + $env:PSModulePath
          echo "PSModulePath=$env:PSModulePath" >> $env:GITHUB_ENV

      - name: Build Packages
        id: build-packages
        shell: pwsh
        run: |
          Import-Module GDS.Common -Force

          $results = Build-AllNuGetPackages -Parallel -Verbose

          # Check for failures
          $failed = $results | Where-Object { -not $_.Success }
          if ($failed) {
            Write-Error "Build failed for: $($failed.ModuleName -join ', ')"
            exit 1
          }

          # Output package list
          $packageNames = ($results | Where-Object Success).ModuleName -join ','
          echo "packages=$packageNames" >> $env:GITHUB_OUTPUT

          # Display summary
          $results | Format-Table ModuleName, Version, Success

      - name: Upload NuGet Packages
        uses: actions/upload-artifact@v4
        with:
          name: nuget-packages
          path: ${{ env.BUILD_OUTPUT }}/*.nupkg
          retention-days: 30

  # Job 3: Publish to JFrog (only on main/release)
  publish-jfrog:
    name: Publish to JFrog Artifactory
    needs: build
    runs-on: windows-latest
    if: |
      github.event_name == 'release' ||
      (github.event_name == 'push' && github.ref == 'refs/heads/main')

    steps:
      - uses: actions/checkout@v4

      - name: Download Artifacts
        uses: actions/download-artifact@v4
        with:
          name: nuget-packages
          path: ${{ env.BUILD_OUTPUT }}

      - name: Install PSFramework
        shell: pwsh
        run: |
          Install-Module -Name PSFramework -Force -Scope CurrentUser

      - name: Setup PSModulePath
        shell: pwsh
        run: |
          $modulesPath = Join-Path $env:GITHUB_WORKSPACE $env:MODULES_PATH
          $env:PSModulePath = "$modulesPath" + [System.IO.Path]::PathSeparator + $env:PSModulePath
          echo "PSModulePath=$env:PSModulePath" >> $env:GITHUB_ENV

      - name: Configure JFrog Repository
        shell: pwsh
        env:
          JFROG_URL: ${{ secrets.JFROG_URL }}
          JFROG_REPO: ${{ secrets.JFROG_REPO }}
        run: |
          $sourceUrl = "$env:JFROG_URL/artifactory/api/nuget/v3/$env:JFROG_REPO"
          $publishUrl = "$env:JFROG_URL/artifactory/api/nuget/$env:JFROG_REPO"

          Register-PSRepository -Name 'JFrog' `
            -SourceLocation $sourceUrl `
            -PublishLocation $publishUrl `
            -InstallationPolicy Trusted

          Get-PSRepository | Format-Table

      - name: Publish to JFrog
        shell: pwsh
        env:
          JFROG_USER: ${{ secrets.JFROG_USER }}
          JFROG_TOKEN: ${{ secrets.JFROG_TOKEN }}
        run: |
          Import-Module GDS.Common -Force

          $packages = Get-ChildItem -Path $env:BUILD_OUTPUT -Filter "*.nupkg"
          Write-Host "Publishing $($packages.Count) package(s) to JFrog..."

          foreach ($package in $packages) {
            $packageName = $package.BaseName -replace '\.\d+\.\d+\.\d+$', ''
            $modulePath = Join-Path $env:GITHUB_WORKSPACE "$env:MODULES_PATH/$packageName"

            if (Test-Path $modulePath) {
              Write-Host "`nPublishing: $packageName..." -ForegroundColor Yellow

              try {
                Publish-Module -Path $modulePath `
                  -Repository 'JFrog' `
                  -NuGetApiKey "$env:JFROG_USER`:$env:JFROG_TOKEN" `
                  -Force -Verbose

                Write-Host "  ✓ Published: $packageName" -ForegroundColor Green
              }
              catch {
                Write-Error "  ✗ Failed: $packageName - $_"
              }
            }
          }

      - name: Create GitHub Release Assets (on release)
        if: github.event_name == 'release'
        uses: softprops/action-gh-release@v1
        with:
          files: PowerShell/build/packages/*.nupkg
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Publishing to JFrog

### Manual Publish

```powershell
# 1. Set JFrog configuration
$jfrogUrl = "https://mycompany.jfrog.io"
$jfrogRepo = "powershell-modules"
$jfrogUser = "myuser"
$jfrogToken = "mytoken"

# 2. Construct URLs
$sourceUrl = "$jfrogUrl/artifactory/api/nuget/v3/$jfrogRepo"
$publishUrl = "$jfrogUrl/artifactory/api/nuget/$jfrogRepo"

# 3. Register repository
Register-PSRepository -Name 'JFrog' `
    -SourceLocation $sourceUrl `
    -PublishLocation $publishUrl `
    -InstallationPolicy Trusted `
    -PackageManagementProvider NuGet

# 4. Import GDS.Common
Import-Module GDS.Common

# 5. Publish module
Publish-Module -Path ".\Modules\GDS.Common" `
    -Repository 'JFrog' `
    -NuGetApiKey "${jfrogUser}:${jfrogToken}" `
    -Force -Verbose
```

### Using GDS.Common Function

```powershell
# Import GDS.Common
Import-Module GDS.Common

# Build package first
Build-NuGetPackage -ModuleName "GDS.Common"

# Configure JFrog
$jfrogUrl = "https://mycompany.jfrog.io"
$jfrogRepo = "powershell-modules"
$feedUrl = "$jfrogUrl/artifactory/api/nuget/v3/$jfrogRepo"

# Register and publish
Register-PSRepository -Name 'JFrog' -SourceLocation $feedUrl -InstallationPolicy Trusted
Publish-NuGetPackage -ModuleName "GDS.Common" `
    -Repository "JFrog" `
    -FeedUrl $feedUrl `
    -NuGetApiKey "${jfrogUser}:${jfrogToken}"
```

### Batch Publish All Modules

```powershell
# Build all modules
Import-Module GDS.Common
$results = Build-AllNuGetPackages -Parallel

# Configure JFrog
$jfrogCreds = "${jfrogUser}:${jfrogToken}"
Register-PSRepository -Name 'JFrog' -SourceLocation $sourceUrl -PublishLocation $publishUrl -InstallationPolicy Trusted

# Publish all successful builds
$results | Where-Object { $_.Success } | ForEach-Object {
    $modulePath = Join-Path ".\Modules" $_.ModuleName

    try {
        Publish-Module -Path $modulePath `
            -Repository 'JFrog' `
            -NuGetApiKey $jfrogCreds `
            -Force
        Write-Host "✓ Published: $($_.ModuleName)" -ForegroundColor Green
    }
    catch {
        Write-Error "✗ Failed: $($_.ModuleName) - $_"
    }
}
```

---

## Installing from JFrog

### One-Time Setup

```powershell
# 1. Configure credentials
$jfrogUrl = "https://mycompany.jfrog.io"
$jfrogRepo = "powershell-modules"
$jfrogUser = "myuser"
$jfrogToken = "mytoken"

# 2. Register JFrog as PSRepository
$sourceUrl = "$jfrogUrl/artifactory/api/nuget/v3/$jfrogRepo"

Register-PSRepository -Name 'JFrog' `
    -SourceLocation $sourceUrl `
    -InstallationPolicy Trusted `
    -PackageManagementProvider NuGet

# 3. Set credentials (if required for private repos)
# Method A: Using credential provider
$credential = New-Object System.Management.Automation.PSCredential(
    $jfrogUser,
    (ConvertTo-SecureString $jfrogToken -AsPlainText -Force)
)

# Method B: Store in PSRepository configuration
# Credentials are handled by NuGet.config
```

### Install Modules

```powershell
# Install GDS.Common
Install-Module -Name GDS.Common -Repository 'JFrog' -Scope CurrentUser

# Install with specific version
Install-Module -Name GDS.Common -Repository 'JFrog' -RequiredVersion "1.0.0"

# Install all GDS modules
Find-Module -Name "GDS.*" -Repository 'JFrog' | Install-Module -Scope CurrentUser

# Verify installation
Get-Module -ListAvailable -Name GDS.*
```

### Update Modules

```powershell
# Update to latest version
Update-Module -Name GDS.Common

# Update all GDS modules
Get-Module -ListAvailable -Name "GDS.*" | Update-Module
```

### Using Credential Provider

For automated scenarios, configure NuGet credential provider:

```powershell
# Install JFrog CLI
choco install jfrog-cli  # Windows

# Configure JFrog CLI
jfrog config add jfrog-server `
    --artifactory-url="$jfrogUrl/artifactory" `
    --user="$jfrogUser" `
    --access-token="$jfrogToken"

# Configure NuGet
jfrog nuget-config --repo-resolve="$jfrogRepo" --repo-deploy="$jfrogRepo"

# Now Install-Module will use stored credentials
Install-Module -Name GDS.Common -Repository 'JFrog'
```

---

## Complete CI/CD Pipeline

### GitHub Actions + JFrog Complete Example

Create `.github/workflows/complete-pipeline.yml`:

```yaml
name: Complete PowerShell CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  release:
    types: [published]

env:
  MODULES_PATH: PowerShell/Modules
  BUILD_OUTPUT: PowerShell/build/packages

jobs:
  lint-and-test:
    name: Lint and Test
    runs-on: windows-latest

    steps:
      - uses: actions/checkout@v4

      - name: Install Dependencies
        shell: pwsh
        run: |
          Install-Module PSScriptAnalyzer, Pester, PSFramework -Force -Scope CurrentUser

      - name: Lint
        shell: pwsh
        run: |
          $results = Invoke-ScriptAnalyzer -Path $env:MODULES_PATH -Recurse
          if ($results | Where-Object Severity -eq 'Error') { exit 1 }

      - name: Test
        shell: pwsh
        run: |
          $results = Invoke-Pester -Path $env:MODULES_PATH -PassThru
          if ($results.FailedCount -gt 0) { exit 1 }

  build:
    name: Build Packages
    needs: lint-and-test
    runs-on: windows-latest

    steps:
      - uses: actions/checkout@v4

      - name: Install PSFramework
        shell: pwsh
        run: Install-Module PSFramework -Force -Scope CurrentUser

      - name: Setup Environment
        shell: pwsh
        run: |
          $modulesPath = Join-Path $env:GITHUB_WORKSPACE $env:MODULES_PATH
          $env:PSModulePath = "$modulesPath" + [System.IO.Path]::PathSeparator + $env:PSModulePath
          echo "PSModulePath=$env:PSModulePath" >> $env:GITHUB_ENV

      - name: Build All Packages
        shell: pwsh
        run: |
          Import-Module GDS.Common -Force
          $results = Build-AllNuGetPackages -Parallel
          if ($results | Where-Object { -not $_.Success }) { exit 1 }

      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: nuget-packages
          path: ${{ env.BUILD_OUTPUT }}/*.nupkg

  publish-dev:
    name: Publish to JFrog (Dev)
    needs: build
    runs-on: windows-latest
    if: github.ref == 'refs/heads/develop'
    environment: development

    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          name: nuget-packages
          path: ${{ env.BUILD_OUTPUT }}

      - name: Publish to JFrog Dev
        shell: pwsh
        env:
          JFROG_URL: ${{ secrets.JFROG_URL }}
          JFROG_REPO: powershell-modules-dev
          JFROG_USER: ${{ secrets.JFROG_USER }}
          JFROG_TOKEN: ${{ secrets.JFROG_TOKEN }}
        run: |
          # Setup and publish (see previous examples)
          # ... publishing code ...

  publish-prod:
    name: Publish to JFrog (Production)
    needs: build
    runs-on: windows-latest
    if: github.event_name == 'release'
    environment: production

    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          name: nuget-packages
          path: ${{ env.BUILD_OUTPUT }}

      - name: Publish to JFrog Production
        shell: pwsh
        env:
          JFROG_URL: ${{ secrets.JFROG_URL }}
          JFROG_REPO: ${{ secrets.JFROG_REPO }}
          JFROG_USER: ${{ secrets.JFROG_USER }}
          JFROG_TOKEN: ${{ secrets.JFROG_TOKEN }}
        run: |
          # Setup
          $sourceUrl = "$env:JFROG_URL/artifactory/api/nuget/v3/$env:JFROG_REPO"
          $publishUrl = "$env:JFROG_URL/artifactory/api/nuget/$env:JFROG_REPO"

          Register-PSRepository -Name 'JFrog' `
            -SourceLocation $sourceUrl `
            -PublishLocation $publishUrl `
            -InstallationPolicy Trusted

          # Setup PSModulePath
          $modulesPath = Join-Path $env:GITHUB_WORKSPACE $env:MODULES_PATH
          $env:PSModulePath = "$modulesPath" + [System.IO.Path]::PathSeparator + $env:PSModulePath

          Import-Module GDS.Common -Force

          # Publish all packages
          $packages = Get-ChildItem -Path $env:BUILD_OUTPUT -Filter "*.nupkg"
          foreach ($package in $packages) {
            $packageName = $package.BaseName -replace '\.\d+\.\d+\.\d+$', ''
            $modulePath = Join-Path $env:GITHUB_WORKSPACE "$env:MODULES_PATH/$packageName"

            Publish-Module -Path $modulePath `
              -Repository 'JFrog' `
              -NuGetApiKey "$env:JFROG_USER`:$env:JFROG_TOKEN" `
              -Force
          }

      - name: Create Release Summary
        shell: pwsh
        run: |
          $packages = Get-ChildItem -Path $env:BUILD_OUTPUT -Filter "*.nupkg"
          $summary = "## Published Packages`n`n"
          foreach ($pkg in $packages) {
            $summary += "- $($pkg.Name)`n"
          }
          echo $summary >> $env:GITHUB_STEP_SUMMARY
```

---

## Troubleshooting

### Issue: "Cannot register repository"

```powershell
# Check URL format
$jfrogUrl = "https://mycompany.jfrog.io"  # No trailing slash
$repo = "powershell-modules"
$sourceUrl = "$jfrogUrl/artifactory/api/nuget/v3/$repo"

# Test URL accessibility
Invoke-WebRequest -Uri $sourceUrl -UseBasicParsing
```

### Issue: "Authentication failed"

```powershell
# Test credentials
$user = "myuser"
$token = "mytoken"
$auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${user}:${token}"))
$headers = @{Authorization = "Basic $auth"}

Invoke-WebRequest -Uri "$jfrogUrl/artifactory/api/system/ping" -Headers $headers
```

### Issue: "Module not found after publish"

```powershell
# JFrog may need time to index
# Wait 1-2 minutes, then:
Find-Module -Name "GDS.Common" -Repository 'JFrog'

# Or clear cache
Remove-Item "$env:LOCALAPPDATA\NuGet\v3-cache" -Recurse -Force
```

### Issue: "Version conflict"

```powershell
# Check existing versions in JFrog
Find-Module -Name "GDS.Common" -Repository 'JFrog' -AllVersions

# Increment version before building
Update-ModuleManifest -Path .\Modules\GDS.Common\GDS.Common.psd1 -ModuleVersion "1.0.1"
```

---

## Best Practices

### 1. Repository Structure
- **Dev Repository**: `powershell-modules-dev` (for testing)
- **Prod Repository**: `powershell-modules` (for production)
- **Virtual Repository**: Aggregate both

### 2. Versioning Strategy
- **Development**: Use pre-release versions (1.0.0-dev.1)
- **Production**: Use stable versions (1.0.0)
- **Use semantic versioning**

### 3. Security
- **Use access tokens** (not passwords)
- **Limit token scope** to specific repositories
- **Rotate tokens regularly**
- **Store secrets in GitHub Secrets** (never in code)

### 4. CI/CD
- **Run tests before building**
- **Build on all branches**
- **Publish only from main/release**
- **Use environments** for approval gates
- **Tag releases** in Git

---

## Complete Example Workflow

### 1. Developer Makes Changes

```bash
# Make code changes
git checkout -b feature/new-feature

# Test locally
pwsh
Import-Module GDS.Common
Build-NuGetPackage -ModuleName "GDS.Common" -SkipTests

# Commit and push
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
```

### 2. GitHub Actions Runs

- ✅ Validates code (PSScriptAnalyzer)
- ✅ Runs tests (Pester)
- ✅ Builds packages
- ✅ Uploads artifacts

### 3. Pull Request Reviewed and Merged

```bash
# Merge to main
git checkout main
git merge feature/new-feature
git push origin main
```

### 4. GitHub Actions Publishes

- ✅ Builds packages
- ✅ Publishes to JFrog
- ✅ Creates GitHub release

### 5. Users Install from JFrog

```powershell
# Register JFrog repo (one time)
Register-PSRepository -Name 'JFrog' -SourceLocation "https://company.jfrog.io/artifactory/api/nuget/v3/powershell-modules"

# Install module
Install-Module -Name GDS.Common -Repository 'JFrog'

# Use it
Import-Module GDS.Common
Write-Log -Message "Hello from JFrog!" -Level Info
```

---

## Reference

### JFrog URLs

```
# V3 API (for Install-Module)
https://{instance}.jfrog.io/artifactory/api/nuget/v3/{repo}

# V2 API (for Publish-Module)
https://{instance}.jfrog.io/artifactory/api/nuget/{repo}

# Web UI
https://{instance}.jfrog.io/ui/repos/tree/General/{repo}
```

### Authentication Formats

```powershell
# For Publish-Module
$apiKey = "${username}:${token}"

# For web requests
$auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${username}:${token}"))
$headers = @{Authorization = "Basic $auth"}
```

---

## See Also

- [NUGET_BUILD_HOWTO.md](./NUGET_BUILD_HOWTO.md) - Build guide
- [NUGET_PACKAGING_GUIDE.md](./NUGET_PACKAGING_GUIDE.md) - Packaging guide
- [PSMODULEPATH_SETUP.md](./PSMODULEPATH_SETUP.md) - Module path setup
- [JFrog Artifactory Documentation](https://www.jfrog.com/confluence/display/JFROG/NuGet+Repositories)

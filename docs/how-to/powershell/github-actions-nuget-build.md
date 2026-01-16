# How to Build NuGet Packages with GitHub Actions

A step-by-step guide to automate PowerShell module builds using GitHub Actions.

---

## Prerequisites

- GitHub repository with PowerShell modules
- Module manifests (.psd1) for each module
- Basic familiarity with GitHub Actions

---

## Step 1: Create the Workflow File

Create `.github/workflows/build-nuget-packages.yml` in your repository:

```yaml
name: Build PowerShell NuGet Packages

on:
  push:
    branches: [main, develop]
    paths:
      - 'PowerShell/Modules/**'
  pull_request:
    branches: [main]
  workflow_dispatch:  # Manual trigger

env:
  MODULES_PATH: PowerShell/Modules
  BUILD_OUTPUT: PowerShell/build/packages

jobs:
  build:
    name: Build NuGet Packages
    runs-on: windows-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install dependencies
        shell: pwsh
        run: |
          Install-Module -Name PSFramework -Force -Scope CurrentUser
          Install-Module -Name Pester -Force -Scope CurrentUser -MinimumVersion 5.0
          Install-Module -Name PSScriptAnalyzer -Force -Scope CurrentUser

      - name: Add modules to PSModulePath
        shell: pwsh
        run: |
          $modulesPath = Join-Path $env:GITHUB_WORKSPACE $env:MODULES_PATH
          $env:PSModulePath = "$modulesPath$([IO.Path]::PathSeparator)$env:PSModulePath"
          echo "PSModulePath=$env:PSModulePath" >> $env:GITHUB_ENV

      - name: Run tests
        shell: pwsh
        run: |
          # PSScriptAnalyzer
          $analysis = Invoke-ScriptAnalyzer -Path $env:MODULES_PATH -Recurse -Severity Error
          if ($analysis) {
            $analysis | Format-Table
            exit 1
          }

          # Pester tests
          $results = Invoke-Pester -Path $env:MODULES_PATH -PassThru
          if ($results.FailedCount -gt 0) { exit 1 }

      - name: Build packages
        shell: pwsh
        run: |
          # Create output directory
          New-Item -ItemType Directory -Path $env:BUILD_OUTPUT -Force

          # Register temporary local repository
          Register-PSRepository -Name 'LocalBuild' `
            -SourceLocation $env:BUILD_OUTPUT `
            -PublishLocation $env:BUILD_OUTPUT `
            -InstallationPolicy Trusted

          # Build each module
          Get-ChildItem -Path $env:MODULES_PATH -Directory | ForEach-Object {
            $manifest = Join-Path $_.FullName "$($_.Name).psd1"
            if (Test-Path $manifest) {
              Write-Host "Building: $($_.Name)"
              Publish-Module -Path $_.FullName -Repository 'LocalBuild' -Force
            }
          }

          # List built packages
          Get-ChildItem $env:BUILD_OUTPUT -Filter "*.nupkg" | Format-Table Name, Length

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: nuget-packages
          path: ${{ env.BUILD_OUTPUT }}/*.nupkg
          retention-days: 30
```

---

## Step 2: Configure Triggers

Choose when the workflow runs by modifying the `on:` section:

```yaml
on:
  # On push to specific branches
  push:
    branches: [main, develop]
    paths:
      - 'PowerShell/Modules/**'  # Only when modules change

  # On pull requests
  pull_request:
    branches: [main]

  # On release
  release:
    types: [published]

  # Manual trigger with inputs
  workflow_dispatch:
    inputs:
      skip_tests:
        description: 'Skip tests'
        type: boolean
        default: false
```

---

## Step 3: Add Publishing (Optional)

To publish packages to a repository, add a publish job:

### Publish to PowerShell Gallery

```yaml
  publish:
    name: Publish to PowerShell Gallery
    needs: build
    runs-on: windows-latest
    if: github.event_name == 'release'

    steps:
      - uses: actions/checkout@v4

      - uses: actions/download-artifact@v4
        with:
          name: nuget-packages
          path: packages

      - name: Publish
        shell: pwsh
        env:
          PSGALLERY_KEY: ${{ secrets.PSGALLERY_API_KEY }}
        run: |
          Get-ChildItem packages -Directory | ForEach-Object {
            $manifest = "$($_.FullName)\$($_.Name).psd1"
            if (Test-Path $manifest) {
              Publish-Module -Path $_.FullName `
                -Repository PSGallery `
                -NuGetApiKey $env:PSGALLERY_KEY
            }
          }
```

### Publish to Azure Artifacts

```yaml
      - name: Publish to Azure
        shell: pwsh
        env:
          AZURE_FEED: ${{ secrets.AZURE_ARTIFACTS_FEED }}
          AZURE_PAT: ${{ secrets.AZURE_PAT }}
        run: |
          Register-PSRepository -Name 'Azure' `
            -SourceLocation $env:AZURE_FEED `
            -PublishLocation $env:AZURE_FEED `
            -InstallationPolicy Trusted

          Get-ChildItem $env:MODULES_PATH -Directory | ForEach-Object {
            Publish-Module -Path $_.FullName `
              -Repository 'Azure' `
              -NuGetApiKey $env:AZURE_PAT
          }
```

---

## Step 4: Set Up Secrets

Add required secrets in GitHub:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add secrets:

| Secret Name | Description |
|-------------|-------------|
| `PSGALLERY_API_KEY` | PowerShell Gallery API key |
| `AZURE_ARTIFACTS_FEED` | Azure Artifacts feed URL |
| `AZURE_PAT` | Azure DevOps PAT |

---

## Step 5: Verify the Workflow

1. Push changes to trigger the workflow
2. Go to **Actions** tab to monitor progress
3. Download artifacts to verify packages

```powershell
# Verify downloaded package
Expand-Archive -Path "MyModule.1.0.0.nupkg" -DestinationPath "./inspect"
Get-ChildItem "./inspect" -Recurse
```

---

## Common Customizations

### Skip Tests Conditionally

```yaml
      - name: Run tests
        if: github.event.inputs.skip_tests != 'true'
        shell: pwsh
        run: |
          Invoke-Pester -Path $env:MODULES_PATH -PassThru
```

### Build Specific Modules Only

```yaml
      - name: Build specific modules
        shell: pwsh
        run: |
          $modules = @('GDS.Common', 'GDS.Security')
          foreach ($name in $modules) {
            $path = Join-Path $env:MODULES_PATH $name
            Publish-Module -Path $path -Repository 'LocalBuild'
          }
```

### Add Version from Git Tag

```yaml
      - name: Set version from tag
        if: github.event_name == 'release'
        shell: pwsh
        run: |
          $version = "${{ github.event.release.tag_name }}".TrimStart('v')
          Get-ChildItem $env:MODULES_PATH -Directory | ForEach-Object {
            Update-ModuleManifest -Path "$($_.FullName)\$($_.Name).psd1" -ModuleVersion $version
          }
```

---

## Troubleshooting

### "Module manifest not found"

Ensure module folder and .psd1 file names match:

```
GDS.Common/
└── GDS.Common.psd1  ✓ (names must match)
```

### "PowerShell version mismatch"

Specify PowerShell version:

```yaml
    runs-on: windows-latest
    defaults:
      run:
        shell: pwsh  # Uses PowerShell 7+
```

### "Tests not found"

Ensure Pester test files end with `.Tests.ps1`:

```
tests/
├── MyModule.Tests.ps1  ✓
└── test-functions.ps1  ✗ (won't be discovered)
```

---

## Complete Example Workflow

See the full workflow file: [.github/workflows/build-nuget-packages.yml](../../.github/workflows/build-nuget-packages.yml)

---

## Related Documentation

- [nuget-tutorial.md](../tutorials/powershell/nuget-tutorial.md) - Learn NuGet fundamentals
- [nuget-packaging-guide.md](../reference/powershell/nuget-packaging-guide.md) - Full reference
- [jfrog-cicd-guide.md](./jfrog-cicd-guide.md) - JFrog-specific CI/CD

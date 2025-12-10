# JFrog Artifactory Quick Start Guide

## TL;DR

### For Developers
```powershell
# Build and publish to JFrog
Import-Module GDS.NuGet
Build-AllNuGetPackages -Parallel
# Then push to GitHub - GitHub Actions handles JFrog publishing
```

### For Users
```powershell
# Install from JFrog
.\Install-GDSModulesFromJFrog.ps1 -JFrogUrl "https://company.jfrog.io" -JFrogRepo "powershell-modules"
```

---

## Setup Guide

### 1. Configure GitHub Secrets

In your GitHub repository → **Settings** → **Secrets and variables** → **Actions**:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `JFROG_URL` | JFrog instance URL | `https://mycompany.jfrog.io` |
| `JFROG_REPO` | Repository name | `powershell-modules` |
| `JFROG_USER` | JFrog username | `myuser` |
| `JFROG_TOKEN` | Access token/API key | `eyJ...` |

### 2. GitHub Actions Workflow

Already created: `.github/workflows/powershell-modules-jfrog.yml`

**What it does:**
- ✅ Validates code on every PR
- ✅ Runs tests (PSScriptAnalyzer, Pester)
- ✅ Builds NuGet packages
- ✅ Publishes to JFrog (on main branch/release)
- ✅ Creates release assets

### 3. Trigger Build

```bash
# Make changes and push
git add .
git commit -m "Update module"
git push origin main

# GitHub Actions automatically:
# 1. Validates
# 2. Tests
# 3. Builds
# 4. Publishes to JFrog
```

---

## Publishing to JFrog

### Automatic (Recommended)

Push to `main` branch or create a release - GitHub Actions handles everything.

### Manual

```powershell
# 1. Configure
$jfrogUrl = "https://mycompany.jfrog.io"
$jfrogRepo = "powershell-modules"
$sourceUrl = "$jfrogUrl/artifactory/api/nuget/v3/$jfrogRepo"
$publishUrl = "$jfrogUrl/artifactory/api/nuget/$jfrogRepo"

# 2. Register repository
Register-PSRepository -Name 'JFrog' `
    -SourceLocation $sourceUrl `
    -PublishLocation $publishUrl `
    -InstallationPolicy Trusted

# 3. Build and publish
Import-Module GDS.NuGet
Build-AllNuGetPackages -Parallel

$creds = "${jfrogUser}:${jfrogToken}"
Import-Module GDS.NuGet
Publish-NuGetPackage -ModuleName "GDS.Common" -Repository 'JFrog' -NuGetApiKey $creds
```

---

## Installing from JFrog

### One-Time Setup

```powershell
# Register JFrog as PowerShell repository
$jfrogUrl = "https://mycompany.jfrog.io"
$jfrogRepo = "powershell-modules"
$sourceUrl = "$jfrogUrl/artifactory/api/nuget/v3/$jfrogRepo"

Register-PSRepository -Name 'JFrog' `
    -SourceLocation $sourceUrl `
    -InstallationPolicy Trusted
```

### Install Modules

```powershell
# Install GDS.Common
Install-Module -Name GDS.Common -Repository 'JFrog' -Scope CurrentUser

# Install GDS.ActiveDirectory (includes dependencies)
Install-Module -Name GDS.ActiveDirectory -Repository 'JFrog' -Scope CurrentUser

# Verify
Get-Module -ListAvailable -Name GDS.*
```

### Using Installation Script

```powershell
# Install all GDS modules automatically
.\Install-GDSModulesFromJFrog.ps1 `
    -JFrogUrl "https://mycompany.jfrog.io" `
    -JFrogRepo "powershell-modules"

# Or specific modules
.\Install-GDSModulesFromJFrog.ps1 `
    -JFrogUrl "https://mycompany.jfrog.io" `
    -JFrogRepo "powershell-modules" `
    -Modules @("GDS.Common", "GDS.ActiveDirectory")
```

---

## CI/CD Workflow

### Development Workflow

1. **Developer creates branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes and push**
   ```bash
   git add .
   git commit -m "Add feature"
   git push origin feature/my-feature
   ```

3. **Create Pull Request**
   - GitHub Actions runs validation
   - Runs tests
   - Builds packages (no publish)

4. **Merge to main**
   ```bash
   git checkout main
   git merge feature/my-feature
   git push origin main
   ```

5. **GitHub Actions publishes to JFrog**
   - Validates
   - Tests
   - Builds
   - **Publishes to JFrog** ✅

### Release Workflow

1. **Create release**
   ```bash
   git tag -a v1.1.0 -m "Release v1.1.0"
   git push origin v1.1.0
   ```

2. **Create GitHub Release**
   - Go to GitHub → Releases → New Release
   - Select tag `v1.1.0`
   - Publish release

3. **GitHub Actions**
   - Publishes to JFrog
   - Attaches .nupkg files to GitHub release

---

## Quick Commands

### Build
```powershell
# Build all modules
.\BuildAllModules.ps1 -Parallel -SkipTests
```

### Publish (Manual)
```powershell
Register-PSRepository -Name 'JFrog' -SourceLocation "https://company.jfrog.io/artifactory/api/nuget/v3/repo"
Publish-Module -Path ".\Modules\GDS.Common" -Repository 'JFrog' -NuGetApiKey "user:token"
```

### Install
```powershell
Register-PSRepository -Name 'JFrog' -SourceLocation "https://company.jfrog.io/artifactory/api/nuget/v3/repo"
Install-Module -Name GDS.Common -Repository 'JFrog'
```

### Or use script
```powershell
.\Install-GDSModulesFromJFrog.ps1 -JFrogUrl "https://company.jfrog.io" -JFrogRepo "repo"
```

---

## Files Reference

- `.github/workflows/powershell-modules-jfrog.yml` - GitHub Actions workflow
- `PowerShell/Install-GDSModulesFromJFrog.ps1` - Installation script (project level)
- `JFROG_CICD_GUIDE.md` - Comprehensive guide (in this directory)

---

## Troubleshooting

### Issue: Cannot register repository
```powershell
# Check URL (no trailing slash)
$url = "https://company.jfrog.io/artifactory/api/nuget/v3/repo-name"
Invoke-WebRequest -Uri $url -UseBasicParsing
```

### Issue: Authentication failed
```powershell
# Test credentials
$user = "myuser"
$token = "mytoken"
$auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${user}:${token}"))
Invoke-WebRequest -Uri "https://company.jfrog.io/artifactory/api/system/ping" `
    -Headers @{Authorization="Basic $auth"}
```

### Issue: GitHub Actions fails
- Check GitHub Secrets are set correctly
- Verify JFrog URL format
- Check token has appropriate permissions
- Review workflow logs

---

## More Information

See comprehensive guide: [JFROG_CICD_GUIDE.md](./JFROG_CICD_GUIDE.md)

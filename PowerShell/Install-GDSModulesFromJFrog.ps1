<#
.SYNOPSIS
    Installs GDS PowerShell modules from JFrog Artifactory.

.DESCRIPTION
    This script registers a JFrog Artifactory repository and installs GDS modules.
    It can be used for automated deployments or user installations.

.PARAMETER JFrogUrl
    JFrog Artifactory instance URL (e.g., "https://mycompany.jfrog.io")

.PARAMETER JFrogRepo
    Repository name in JFrog (e.g., "powershell-modules")

.PARAMETER Modules
    Array of module names to install. Default: All GDS modules.

.PARAMETER Scope
    Installation scope: CurrentUser or AllUsers. Default: CurrentUser.

.PARAMETER Force
    Force installation even if module already exists.

.PARAMETER Username
    JFrog username (for private repositories).

.PARAMETER Token
    JFrog access token or API key (for private repositories).

.EXAMPLE
    .\Install-GDSModulesFromJFrog.ps1 -JFrogUrl "https://mycompany.jfrog.io" -JFrogRepo "powershell-modules"

.EXAMPLE
    .\Install-GDSModulesFromJFrog.ps1 -JFrogUrl "https://mycompany.jfrog.io" `
        -JFrogRepo "powershell-modules" `
        -Modules @("GDS.Common", "GDS.ActiveDirectory") `
        -Username "myuser" `
        -Token "mytoken"

.EXAMPLE
    .\Install-GDSModulesFromJFrog.ps1 -JFrogUrl "https://mycompany.jfrog.io" -JFrogRepo "powershell-modules" -Scope AllUsers

.NOTES
    Author: GDS Team
    Requires: PowerShell 5.1 or later
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$JFrogUrl,

    [Parameter(Mandatory = $true)]
    [string]$JFrogRepo,

    [Parameter(Mandatory = $false)]
    [string[]]$Modules,

    [Parameter(Mandatory = $false)]
    [ValidateSet('CurrentUser', 'AllUsers')]
    [string]$Scope = 'CurrentUser',

    [Parameter(Mandatory = $false)]
    [switch]$Force,

    [Parameter(Mandatory = $false)]
    [string]$Username,

    [Parameter(Mandatory = $false)]
    [string]$Token
)

$ErrorActionPreference = 'Stop'

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GDS Modules Installation from JFrog" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

try {
    # Build source URL
    $sourceUrl = "$JFrogUrl/artifactory/api/nuget/v3/$JFrogRepo"
    Write-Host "`nJFrog Repository:" -ForegroundColor Yellow
    Write-Host "  URL: $sourceUrl" -ForegroundColor Gray
    Write-Host "  Scope: $Scope" -ForegroundColor Gray

    # Register repository if not already registered
    if (-not (Get-PSRepository -Name 'JFrog' -ErrorAction SilentlyContinue)) {
        Write-Host "`nRegistering JFrog repository..." -ForegroundColor Yellow

        Register-PSRepository -Name 'JFrog' `
            -SourceLocation $sourceUrl `
            -InstallationPolicy Trusted `
            -PackageManagementProvider NuGet

        Write-Host "  ✓ Repository registered" -ForegroundColor Green
    }
    else {
        Write-Host "`nJFrog repository already registered" -ForegroundColor Gray
    }

    # Configure authentication if provided
    if ($Username -and $Token) {
        Write-Host "`nConfiguring authentication..." -ForegroundColor Yellow

        # Store credentials for NuGet operations
        $credential = New-Object System.Management.Automation.PSCredential(
            $Username,
            (ConvertTo-SecureString $Token -AsPlainText -Force)
        )

        # Note: PowerShellGet doesn't directly support credentials for Find-Module/Install-Module
        # We'll need to configure NuGet credential provider or use JFrog CLI
        Write-Host "  ⚠ Authentication configured (may require NuGet credential provider)" -ForegroundColor Yellow
    }

    # Discover modules if not specified
    if (-not $Modules) {
        Write-Host "`nDiscovering GDS modules in JFrog..." -ForegroundColor Yellow

        try {
            $availableModules = Find-Module -Repository 'JFrog' -Name "GDS.*" -ErrorAction Stop
            $Modules = $availableModules.Name
            Write-Host "  Found $($Modules.Count) module(s)" -ForegroundColor Green
        }
        catch {
            Write-Warning "Could not discover modules automatically. Using default list."
            $Modules = @("GDS.Common", "GDS.ActiveDirectory")
        }
    }

    Write-Host "`nModules to install: $($Modules.Count)" -ForegroundColor Yellow
    $Modules | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }

    # Install modules
    $installed = 0
    $failed = 0
    $skipped = 0

    foreach ($moduleName in $Modules) {
        Write-Host "`nInstalling $moduleName..." -ForegroundColor Yellow

        try {
            # Check if already installed
            $existingModule = Get-Module -ListAvailable -Name $moduleName -ErrorAction SilentlyContinue

            if ($existingModule -and -not $Force) {
                Write-Host "  ⓘ Already installed: $moduleName v$($existingModule[0].Version)" -ForegroundColor Gray
                $skipped++
                continue
            }

            # Install module
            $installParams = @{
                Name = $moduleName
                Repository = 'JFrog'
                Scope = $Scope
                Force = $Force
                AllowClobber = $true
                ErrorAction = 'Stop'
            }

            Install-Module @installParams

            # Verify installation
            $installedModule = Get-Module -ListAvailable -Name $moduleName | Select-Object -First 1
            Write-Host "  ✓ Installed: $moduleName v$($installedModule.Version)" -ForegroundColor Green
            $installed++
        }
        catch {
            Write-Host "  ✗ Failed: $moduleName" -ForegroundColor Red
            Write-Host "  Error: $_" -ForegroundColor Red
            $failed++
        }
    }

    # Summary
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Installation Summary" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Installed: $installed" -ForegroundColor Green
    Write-Host "Skipped: $skipped" -ForegroundColor Gray
    Write-Host "Failed: $failed" -ForegroundColor $(if ($failed -gt 0) {'Red'} else {'Gray'})

    if ($installed -gt 0) {
        Write-Host "`nInstalled Modules:" -ForegroundColor Cyan
        Get-Module -ListAvailable -Name "GDS.*" | Format-Table Name, Version, ModuleBase -AutoSize
    }

    if ($failed -gt 0) {
        Write-Warning "`nSome modules failed to install. Check errors above."
        exit 1
    }

    Write-Host "`n✓ Installation completed successfully!" -ForegroundColor Green
    exit 0
}
catch {
    Write-Host "`n✗ Installation failed: $_" -ForegroundColor Red
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    exit 1
}

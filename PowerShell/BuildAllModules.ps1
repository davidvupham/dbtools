<#
.SYNOPSIS
    Convenience script to build all GDS module NuGet packages.

.DESCRIPTION
    This script builds NuGet packages for all GDS PowerShell modules.
    It's a wrapper around Build-AllNuGetPackages for easy execution.

.PARAMETER SkipTests
    Skip running PSScriptAnalyzer and Pester tests.

.PARAMETER Force
    Force rebuild even if packages already exist.

.PARAMETER Parallel
    Build modules in parallel for faster execution.

.PARAMETER Publish
    Publish packages after building (requires -ApiKey).

.PARAMETER ApiKey
    API key for publishing to repository.

.PARAMETER Repository
    Target repository (default: PSGallery).

.EXAMPLE
    .\BuildAllModules.ps1

.EXAMPLE
    .\BuildAllModules.ps1 -SkipTests -Parallel

.EXAMPLE
    .\BuildAllModules.ps1 -Publish -ApiKey "your-key"

.NOTES
    Run this from the PowerShell directory.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [switch]$SkipTests,

    [Parameter(Mandatory = $false)]
    [switch]$Force,

    [Parameter(Mandatory = $false)]
    [switch]$Parallel,

    [Parameter(Mandatory = $false)]
    [switch]$Publish,

    [Parameter(Mandatory = $false)]
    [string]$ApiKey,

    [Parameter(Mandatory = $false)]
    [string]$Repository = 'PSGallery'
)

$ErrorActionPreference = 'Stop'

try {
    # Import GDS.NuGet (assumes it's in PSModulePath)
    Write-Host "Importing GDS.NuGet module..." -ForegroundColor Cyan
    Import-Module GDS.NuGet -Force

    # Build all packages
    Write-Host "`nBuilding all GDS module packages..." -ForegroundColor Cyan
    $results = Build-AllNuGetPackages -SkipTests:$SkipTests -Force:$Force -Parallel:$Parallel

    # Check results
    $successful = $results | Where-Object { $_.Success }
    $failed = $results | Where-Object { -not $_.Success }

    if ($failed) {
        Write-Host "`n⚠ Some builds failed!" -ForegroundColor Yellow
        $failed | ForEach-Object {
            Write-Host "  ✗ $($_.ModuleName): $($_.Errors -join '; ')" -ForegroundColor Red
        }
    }

    # Publish if requested
    if ($Publish) {
        if (-not $ApiKey) {
            Write-Error "ApiKey is required when using -Publish"
            exit 1
        }

        Write-Host "`nPublishing packages to $Repository..." -ForegroundColor Cyan

        foreach ($result in $successful) {
            try {
                Write-Host "Publishing $($result.ModuleName)..." -ForegroundColor Yellow
                Publish-NuGetPackage -ModuleName $result.ModuleName `
                    -Repository $Repository `
                    -NuGetApiKey $ApiKey
                Write-Host "  ✓ Published successfully" -ForegroundColor Green
            }
            catch {
                Write-Host "  ✗ Publish failed: $_" -ForegroundColor Red
            }
        }
    }

    Write-Host "`n✓ Build process completed!" -ForegroundColor Green
    exit 0
}
catch {
    Write-Host "`n✗ Build process failed: $_" -ForegroundColor Red
    exit 1
}

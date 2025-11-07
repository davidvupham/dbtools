<#
.SYNOPSIS
    Builds NuGet packages for all GDS PowerShell modules.

.DESCRIPTION
    This function discovers all GDS modules and builds NuGet packages for each one.
    It provides summary reporting of the build process.

.PARAMETER ModulesPath
    Path to the modules directory. Default: Detects from script location.

.PARAMETER OutputPath
    Directory where NuGet packages will be created. Default: "../../build/packages"

.PARAMETER ExcludeModules
    Array of module names to exclude from build.

.PARAMETER SkipTests
    Skip running PSScriptAnalyzer and Pester tests for all modules.

.PARAMETER Force
    Force rebuild even if packages already exist.

.PARAMETER Parallel
    Build modules in parallel for faster execution.

.EXAMPLE
    Build-AllNuGetPackages

.EXAMPLE
    Build-AllNuGetPackages -ExcludeModules @("GDS.Test")

.EXAMPLE
    Build-AllNuGetPackages -SkipTests -Force

.EXAMPLE
    Build-AllNuGetPackages -Parallel

.OUTPUTS
    Returns an array of build results for each module.

.NOTES
    Author: GDS Team
    Module: GDS.Common
#>
function Build-AllNuGetPackages {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [string]$ModulesPath,

        [Parameter(Mandatory = $false)]
        [string]$OutputPath,

        [Parameter(Mandatory = $false)]
        [string[]]$ExcludeModules = @(),

        [Parameter(Mandatory = $false)]
        [switch]$SkipTests,

        [Parameter(Mandatory = $false)]
        [switch]$Force,

        [Parameter(Mandatory = $false)]
        [switch]$Parallel
    )

    $ErrorActionPreference = 'Continue'
    $startTime = Get-Date

    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Building All GDS NuGet Packages" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    # Determine modules path
    if (-not $ModulesPath) {
        $scriptRoot = $PSScriptRoot
        $ModulesPath = Split-Path $scriptRoot -Parent | Split-Path -Parent
    }

    Write-Host "`nModules Path: $ModulesPath" -ForegroundColor Gray

    # Discover modules
    $modules = Get-ChildItem -Path $ModulesPath -Directory | Where-Object {
        $_.Name -like "GDS.*" -and $_.Name -notin $ExcludeModules
    }

    Write-Host "Found $($modules.Count) module(s) to build" -ForegroundColor Gray
    $modules | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Gray }

    # Build results
    $buildResults = @()

    if ($Parallel -and $modules.Count -gt 1) {
        Write-Host "`nBuilding modules in parallel..." -ForegroundColor Yellow

        # Build in parallel using jobs
        $jobs = $modules | ForEach-Object {
            $moduleName = $_.Name
            $modulePath = $_.FullName

            Start-Job -ScriptBlock {
                param($ModuleName, $ModulePath, $OutputPath, $SkipTests, $Force)

                # Import function
                . $using:PSScriptRoot\Build-NuGetPackage.ps1

                Build-NuGetPackage -ModuleName $ModuleName `
                    -ModulePath $ModulePath `
                    -OutputPath $OutputPath `
                    -SkipTests:$SkipTests `
                    -Force:$Force
            } -ArgumentList $moduleName, $modulePath, $OutputPath, $SkipTests, $Force
        }

        # Wait for all jobs
        $jobs | Wait-Job | ForEach-Object {
            $result = Receive-Job -Job $_
            $buildResults += $result
            Remove-Job -Job $_
        }
    }
    else {
        # Build sequentially
        Write-Host "`nBuilding modules sequentially..." -ForegroundColor Yellow

        foreach ($module in $modules) {
            Write-Host "`n----------------------------------------" -ForegroundColor Cyan
            Write-Host "Building: $($module.Name)" -ForegroundColor Cyan
            Write-Host "----------------------------------------" -ForegroundColor Cyan

            try {
                $result = Build-NuGetPackage -ModuleName $module.Name `
                    -ModulePath $module.FullName `
                    -OutputPath $OutputPath `
                    -SkipTests:$SkipTests `
                    -Force:$Force `
                    -ErrorAction Stop

                $buildResults += $result
            }
            catch {
                Write-Host "✗ Build failed: $_" -ForegroundColor Red
                $buildResults += [PSCustomObject]@{
                    ModuleName = $module.Name
                    Version = $null
                    PackagePath = $null
                    Success = $false
                    Errors = @($_.Exception.Message)
                    Warnings = @()
                }
            }
        }
    }

    # Summary
    $duration = (Get-Date) - $startTime
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Build Summary" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    $successful = ($buildResults | Where-Object { $_.Success }).Count
    $failed = ($buildResults | Where-Object { -not $_.Success }).Count

    Write-Host "`nTotal Modules: $($buildResults.Count)" -ForegroundColor White
    Write-Host "Successful: $successful" -ForegroundColor Green
    Write-Host "Failed: $failed" -ForegroundColor $(if ($failed -gt 0) { 'Red' } else { 'Gray' })
    Write-Host "Duration: $([math]::Round($duration.TotalSeconds, 2)) seconds" -ForegroundColor Gray

    if ($successful -gt 0) {
        Write-Host "`nSuccessful Builds:" -ForegroundColor Green
        $buildResults | Where-Object { $_.Success } | ForEach-Object {
            Write-Host "  ✓ $($_.ModuleName) v$($_.Version)" -ForegroundColor Green
        }
    }

    if ($failed -gt 0) {
        Write-Host "`nFailed Builds:" -ForegroundColor Red
        $buildResults | Where-Object { -not $_.Success } | ForEach-Object {
            Write-Host "  ✗ $($_.ModuleName)" -ForegroundColor Red
            $_.Errors | ForEach-Object {
                Write-Host "    - $_" -ForegroundColor Red
            }
        }
    }

    # Warnings
    $totalWarnings = ($buildResults | ForEach-Object { $_.Warnings.Count } | Measure-Object -Sum).Sum
    if ($totalWarnings -gt 0) {
        Write-Host "`nWarnings: $totalWarnings" -ForegroundColor Yellow
        $buildResults | Where-Object { $_.Warnings.Count -gt 0 } | ForEach-Object {
            Write-Host "  ⚠ $($_.ModuleName):" -ForegroundColor Yellow
            $_.Warnings | ForEach-Object {
                Write-Host "    - $_" -ForegroundColor Yellow
            }
        }
    }

    Write-Host "`n========================================" -ForegroundColor Cyan

    if ($failed -eq 0) {
        Write-Host "✓ All packages built successfully!" -ForegroundColor Green
    }
    else {
        Write-Host "✗ Some packages failed to build" -ForegroundColor Red
    }

    return $buildResults
}

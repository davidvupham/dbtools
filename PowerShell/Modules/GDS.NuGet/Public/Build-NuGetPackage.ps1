<#
.SYNOPSIS
    Builds a NuGet package for a PowerShell module.

.DESCRIPTION
    This function builds a NuGet package (.nupkg) for a specified PowerShell module.
    It validates the module, runs tests (optional), and creates the package using PowerShellGet.

.PARAMETER ModuleName
    The name of the module to build (e.g., "GDS.Common", "GDS.ActiveDirectory").

.PARAMETER ModulePath
    Optional path to the module directory. If not specified, searches in standard locations.

.PARAMETER OutputPath
    Directory where the NuGet package will be created. Default: "../../build/packages"

.PARAMETER Version
    Optional version override. If not specified, uses version from module manifest.

.PARAMETER SkipTests
    Skip running PSScriptAnalyzer and Pester tests.

.PARAMETER SkipValidation
    Skip module manifest validation.

.PARAMETER Force
    Force rebuild even if package already exists.

.EXAMPLE
    Build-NuGetPackage -ModuleName "GDS.Common"

.EXAMPLE
    Build-NuGetPackage -ModuleName "GDS.Common" -Version "1.1.0" -OutputPath "C:\Packages"

.EXAMPLE
    Build-NuGetPackage -ModuleName "GDS.ActiveDirectory" -SkipTests

.OUTPUTS
    Returns a PSCustomObject with build information:
    - ModuleName
    - Version
    - PackagePath
    - Success
    - Errors

.NOTES
    Requires PowerShellGet module.
    Author: GDS Team
    Module: GDS.Common
#>
function Build-NuGetPackage {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$ModuleName,

        [Parameter(Mandatory = $false)]
        [string]$ModulePath,

        [Parameter(Mandatory = $false)]
        [string]$OutputPath,

        [Parameter(Mandatory = $false)]
        [string]$Version,

        [Parameter(Mandatory = $false)]
        [switch]$SkipTests,

        [Parameter(Mandatory = $false)]
        [switch]$SkipValidation,

        [Parameter(Mandatory = $false)]
        [switch]$Force
    )

    $ErrorActionPreference = 'Stop'

    # Initialize result object
    $result = [PSCustomObject]@{
        ModuleName = $ModuleName
        Version = $null
        PackagePath = $null
        Success = $false
        Errors = @()
        Warnings = @()
    }

    try {
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Building NuGet Package: $ModuleName" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan

        # Find module path if not specified
        if (-not $ModulePath) {
            $scriptRoot = $PSScriptRoot
            $modulesRoot = Split-Path $scriptRoot -Parent | Split-Path -Parent
            $ModulePath = Join-Path $modulesRoot $ModuleName

            if (-not (Test-Path $ModulePath)) {
                throw "Module path not found: $ModulePath"
            }
        }

        Write-Host "Module Path: $ModulePath" -ForegroundColor Gray

        # Determine output path
        if (-not $OutputPath) {
            $OutputPath = Join-Path (Split-Path (Split-Path $ModulePath -Parent) -Parent) "build" "packages"
        }

        # Ensure output directory exists
        if (-not (Test-Path $OutputPath)) {
            New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
        }

        Write-Host "Output Path: $OutputPath" -ForegroundColor Gray

        # Find module manifest
        $manifestPath = Join-Path $ModulePath "$ModuleName.psd1"
        if (-not (Test-Path $manifestPath)) {
            throw "Module manifest not found: $manifestPath"
        }

        # Validate manifest
        if (-not $SkipValidation) {
            Write-Host "`n[1/5] Validating module manifest..." -ForegroundColor Yellow
            try {
                $manifest = Test-ModuleManifest -Path $manifestPath -ErrorAction Stop
                $moduleVersion = if ($Version) { $Version } else { $manifest.Version.ToString() }
                $result.Version = $moduleVersion
                Write-Host "✓ Module manifest valid (Version: $moduleVersion)" -ForegroundColor Green
            }
            catch {
                throw "Module manifest validation failed: $_"
            }
        }
        else {
            $manifestData = Import-PowerShellDataFile -Path $manifestPath
            $moduleVersion = if ($Version) { $Version } else { $manifestData.ModuleVersion }
            $result.Version = $moduleVersion
        }

        # Run PSScriptAnalyzer
        if (-not $SkipTests) {
            Write-Host "`n[2/5] Running PSScriptAnalyzer..." -ForegroundColor Yellow
            if (Get-Module -ListAvailable -Name PSScriptAnalyzer) {
                $analysisResults = Invoke-ScriptAnalyzer -Path $ModulePath -Recurse
                if ($analysisResults) {
                    $errorCount = ($analysisResults | Where-Object { $_.Severity -eq 'Error' }).Count
                    $warningCount = ($analysisResults | Where-Object { $_.Severity -eq 'Warning' }).Count

                    if ($errorCount -gt 0) {
                        Write-Host "✗ PSScriptAnalyzer found $errorCount error(s)" -ForegroundColor Red
                        $analysisResults | Where-Object { $_.Severity -eq 'Error' } | Format-Table -AutoSize
                        throw "PSScriptAnalyzer errors found. Fix errors before building."
                    }
                    if ($warningCount -gt 0) {
                        Write-Host "⚠ PSScriptAnalyzer found $warningCount warning(s)" -ForegroundColor Yellow
                        $result.Warnings += "PSScriptAnalyzer warnings: $warningCount"
                    }
                }
                else {
                    Write-Host "✓ PSScriptAnalyzer passed" -ForegroundColor Green
                }
            }
            else {
                Write-Host "⚠ PSScriptAnalyzer not installed, skipping" -ForegroundColor Yellow
                $result.Warnings += "PSScriptAnalyzer not installed"
            }
        }

        # Run Pester tests
        if (-not $SkipTests) {
            Write-Host "`n[3/5] Running Pester tests..." -ForegroundColor Yellow
            $testsPath = Join-Path $ModulePath "tests"
            if (Test-Path $testsPath) {
                if (Get-Module -ListAvailable -Name Pester) {
                    $testResults = Invoke-Pester -Path $testsPath -PassThru -Show None
                    if ($testResults.FailedCount -gt 0) {
                        Write-Host "✗ $($testResults.FailedCount) test(s) failed" -ForegroundColor Red
                        throw "Pester tests failed. Fix tests before building."
                    }
                    else {
                        Write-Host "✓ All tests passed ($($testResults.PassedCount) passed)" -ForegroundColor Green
                    }
                }
                else {
                    Write-Host "⚠ Pester not installed, skipping tests" -ForegroundColor Yellow
                    $result.Warnings += "Pester not installed"
                }
            }
            else {
                Write-Host "⚠ No tests found, skipping" -ForegroundColor Yellow
            }
        }

        # Update version if override specified
        if ($Version -and $Version -ne $manifest.Version.ToString()) {
            Write-Host "`n[4/5] Updating module version to $Version..." -ForegroundColor Yellow
            Update-ModuleManifest -Path $manifestPath -ModuleVersion $Version
            Write-Host "✓ Module version updated" -ForegroundColor Green
        }

        # Build package
        Write-Host "`n[5/5] Building NuGet package..." -ForegroundColor Yellow

        # Create temporary repository
        $tempRepoName = "TempRepo_$([Guid]::NewGuid().ToString().Replace('-', '').Substring(0, 8))"

        try {
            Register-PSRepository -Name $tempRepoName `
                -SourceLocation $OutputPath `
                -PublishLocation $OutputPath `
                -InstallationPolicy Trusted `
                -ErrorAction Stop

            # Publish to temp repository (creates .nupkg)
            Publish-Module -Path $ModulePath `
                -Repository $tempRepoName `
                -NuGetApiKey "temp" `
                -Force:$Force `
                -ErrorAction Stop

            # Find the created package
            $packageFile = Get-ChildItem -Path $OutputPath -Filter "$ModuleName.$moduleVersion.nupkg" -ErrorAction Stop
            $result.PackagePath = $packageFile.FullName
            $result.Success = $true

            Write-Host "✓ Package created successfully" -ForegroundColor Green
            Write-Host "`nPackage Details:" -ForegroundColor Cyan
            Write-Host "  Name: $ModuleName" -ForegroundColor Gray
            Write-Host "  Version: $moduleVersion" -ForegroundColor Gray
            Write-Host "  Size: $([math]::Round($packageFile.Length / 1KB, 2)) KB" -ForegroundColor Gray
            Write-Host "  Path: $($packageFile.FullName)" -ForegroundColor Gray
        }
        finally {
            # Clean up temporary repository
            Unregister-PSRepository -Name $tempRepoName -ErrorAction SilentlyContinue
        }

        Write-Host "`n✓ Build completed successfully!" -ForegroundColor Green
    }
    catch {
        $result.Success = $false
        $result.Errors += $_.Exception.Message
        Write-Host "`n✗ Build failed: $_" -ForegroundColor Red
        throw
    }

    return $result
}

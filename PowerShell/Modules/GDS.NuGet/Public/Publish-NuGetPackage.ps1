<#
.SYNOPSIS
    Publishes a NuGet package to a PowerShell repository.

.DESCRIPTION
    This function publishes a PowerShell module NuGet package to a specified repository
    (PowerShell Gallery, Azure Artifacts, or private feed).

.PARAMETER ModuleName
    The name of the module to publish.

.PARAMETER PackagePath
    Path to the .nupkg file. If not specified, searches in default build location.

.PARAMETER Repository
    Target repository name. Options: 'PSGallery', 'AzureArtifacts', or custom name.
    Default: 'PSGallery'

.PARAMETER NuGetApiKey
    API key for the target repository. Required for authentication.

.PARAMETER FeedUrl
    Feed URL for custom repositories.

.PARAMETER WhatIf
    Shows what would happen without actually publishing.

.EXAMPLE
    Publish-NuGetPackage -ModuleName "GDS.Common" -NuGetApiKey $apiKey

.EXAMPLE
    Publish-NuGetPackage -ModuleName "GDS.Common" -Repository "AzureArtifacts" `
        -FeedUrl "https://pkgs.dev.azure.com/org/_packaging/feed/nuget/v2" `
        -NuGetApiKey $pat

.EXAMPLE
    Publish-NuGetPackage -ModuleName "GDS.Common" -WhatIf

.NOTES
    Author: GDS Team
    Module: GDS.Common
#>
function Publish-NuGetPackage {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param(
        [Parameter(Mandatory = $true)]
        [string]$ModuleName,

        [Parameter(Mandatory = $false)]
        [string]$PackagePath,

        [Parameter(Mandatory = $false)]
        [string]$Repository = 'PSGallery',

        [Parameter(Mandatory = $true)]
        [string]$NuGetApiKey,

        [Parameter(Mandatory = $false)]
        [string]$FeedUrl
    )

    $ErrorActionPreference = 'Stop'

    try {
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Publishing NuGet Package: $ModuleName" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan

        # Find package if path not specified
        if (-not $PackagePath) {
            $searchPath = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) "build" "packages"
            $packageFiles = Get-ChildItem -Path $searchPath -Filter "$ModuleName.*.nupkg" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending

            if (-not $packageFiles) {
                throw "Package not found for module: $ModuleName. Build the package first using Build-NuGetPackage."
            }

            $PackagePath = $packageFiles[0].FullName
        }

        if (-not (Test-Path $PackagePath)) {
            throw "Package file not found: $PackagePath"
        }

        Write-Host "Package: $PackagePath" -ForegroundColor Gray
        Write-Host "Repository: $Repository" -ForegroundColor Gray

        # Register custom repository if FeedUrl is provided
        if ($FeedUrl -and $Repository -ne 'PSGallery') {
            if (-not (Get-PSRepository -Name $Repository -ErrorAction SilentlyContinue)) {
                Write-Host "Registering repository: $Repository" -ForegroundColor Yellow
                Register-PSRepository -Name $Repository `
                    -SourceLocation $FeedUrl `
                    -PublishLocation $FeedUrl `
                    -InstallationPolicy Trusted
            }
        }

        # Publish
        if ($PSCmdlet.ShouldProcess($ModuleName, "Publish to $Repository")) {
            Write-Host "`nPublishing package..." -ForegroundColor Yellow

            # Extract module path from package
            $tempDir = Join-Path $env:TEMP "NuGetPublish_$([Guid]::NewGuid().ToString())"
            Expand-Archive -Path $PackagePath -DestinationPath $tempDir -Force

            # Find module directory in extracted package
            $modulePath = Get-ChildItem -Path $tempDir -Directory -Recurse | Where-Object { $_.Name -eq $ModuleName } | Select-Object -First 1

            if (-not $modulePath) {
                throw "Module directory not found in package"
            }

            # Publish module
            Publish-Module -Path $modulePath.FullName `
                -Repository $Repository `
                -NuGetApiKey $NuGetApiKey `
                -Force `
                -Verbose

            # Clean up
            Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue

            Write-Host "✓ Package published successfully!" -ForegroundColor Green
        }
        else {
            Write-Host "✓ WhatIf: Would publish $ModuleName to $Repository" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "✗ Publish failed: $_" -ForegroundColor Red
        throw
    }
}

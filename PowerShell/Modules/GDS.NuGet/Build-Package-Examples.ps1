<#
.SYNOPSIS
    Example script showing various ways to build NuGet packages.

.DESCRIPTION
    This script provides practical examples of building and publishing NuGet packages
    for GDS PowerShell modules.

.NOTES
    Copy and modify these examples for your use cases.
#>

# Import the GDS.Common module (assumes it's in PSModulePath)
Import-Module GDS.Common -Force

Write-Host "GDS NuGet Package Build Examples" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Example 1: Build a single module
Write-Host "`nExample 1: Build a single module" -ForegroundColor Yellow
Write-Host "Command: Build-NuGetPackage -ModuleName 'GDS.Common'" -ForegroundColor Gray
# Uncomment to run:
# Build-NuGetPackage -ModuleName "GDS.Common"

# Example 2: Build with custom version
Write-Host "`nExample 2: Build with custom version" -ForegroundColor Yellow
Write-Host "Command: Build-NuGetPackage -ModuleName 'GDS.Common' -Version '1.1.0'" -ForegroundColor Gray
# Uncomment to run:
# Build-NuGetPackage -ModuleName "GDS.Common" -Version "1.1.0"

# Example 3: Build without tests (faster)
Write-Host "`nExample 3: Build without tests (faster)" -ForegroundColor Yellow
Write-Host "Command: Build-NuGetPackage -ModuleName 'GDS.Common' -SkipTests" -ForegroundColor Gray
# Uncomment to run:
# Build-NuGetPackage -ModuleName "GDS.Common" -SkipTests

# Example 4: Build all modules
Write-Host "`nExample 4: Build all modules" -ForegroundColor Yellow
Write-Host "Command: Build-AllNuGetPackages" -ForegroundColor Gray
# Uncomment to run:
# Build-AllNuGetPackages

# Example 5: Build all modules in parallel (faster)
Write-Host "`nExample 5: Build all modules in parallel (faster)" -ForegroundColor Yellow
Write-Host "Command: Build-AllNuGetPackages -Parallel" -ForegroundColor Gray
# Uncomment to run:
# Build-AllNuGetPackages -Parallel

# Example 6: Build all except specific modules
Write-Host "`nExample 6: Build all except specific modules" -ForegroundColor Yellow
Write-Host "Command: Build-AllNuGetPackages -ExcludeModules @('GDS.Test')" -ForegroundColor Gray
# Uncomment to run:
# Build-AllNuGetPackages -ExcludeModules @("GDS.Test")

# Example 7: Build to custom output path
Write-Host "`nExample 7: Build to custom output path" -ForegroundColor Yellow
Write-Host "Command: Build-NuGetPackage -ModuleName 'GDS.Common' -OutputPath 'C:\Packages'" -ForegroundColor Gray
# Uncomment to run:
# Build-NuGetPackage -ModuleName "GDS.Common" -OutputPath "C:\Packages"

# Example 8: Force rebuild
Write-Host "`nExample 8: Force rebuild (overwrite existing)" -ForegroundColor Yellow
Write-Host "Command: Build-NuGetPackage -ModuleName 'GDS.Common' -Force" -ForegroundColor Gray
# Uncomment to run:
# Build-NuGetPackage -ModuleName "GDS.Common" -Force

# Example 9: Publish to PowerShell Gallery
Write-Host "`nExample 9: Publish to PowerShell Gallery" -ForegroundColor Yellow
Write-Host "Command: Publish-NuGetPackage -ModuleName 'GDS.Common' -NuGetApiKey 'your-key'" -ForegroundColor Gray
# Uncomment to run (requires API key):
# $apiKey = Read-Host "Enter PowerShell Gallery API Key" -AsSecureString
# $apiKeyPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
#     [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey)
# )
# Publish-NuGetPackage -ModuleName "GDS.Common" -NuGetApiKey $apiKeyPlain

# Example 10: Publish to Azure Artifacts
Write-Host "`nExample 10: Publish to Azure Artifacts" -ForegroundColor Yellow
Write-Host "Command: Publish-NuGetPackage with Azure Artifacts feed" -ForegroundColor Gray
# Uncomment to run:
# $feedUrl = "https://pkgs.dev.azure.com/yourorg/_packaging/yourfeed/nuget/v2"
# $pat = "your-personal-access-token"
# Publish-NuGetPackage -ModuleName "GDS.Common" `
#     -Repository "AzureArtifacts" `
#     -FeedUrl $feedUrl `
#     -NuGetApiKey $pat

# Example 11: WhatIf (dry run)
Write-Host "`nExample 11: WhatIf (dry run)" -ForegroundColor Yellow
Write-Host "Command: Publish-NuGetPackage -ModuleName 'GDS.Common' -WhatIf" -ForegroundColor Gray
# Uncomment to run:
# Publish-NuGetPackage -ModuleName "GDS.Common" -NuGetApiKey "dummy" -WhatIf

# Example 12: Complete workflow - Build and Publish
Write-Host "`nExample 12: Complete workflow - Build and Publish" -ForegroundColor Yellow
Write-Host @"
# Build the package
`$buildResult = Build-NuGetPackage -ModuleName "GDS.Common" -Verbose

# Check if successful
if (`$buildResult.Success) {
    # Publish to gallery
    Publish-NuGetPackage -ModuleName "GDS.Common" -NuGetApiKey `$apiKey
}
else {
    Write-Error "Build failed: `$(`$buildResult.Errors -join ', ')"
}
"@ -ForegroundColor Gray

Write-Host "`n=================================" -ForegroundColor Cyan
Write-Host "Uncomment examples above to run them" -ForegroundColor White
Write-Host "=================================" -ForegroundColor Cyan

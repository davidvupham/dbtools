@{
    RootModule = 'GDS.NuGet.psm1'
    ModuleVersion = '1.0.0'
    GUID = '12345678-1234-1234-1234-123456789099'
    Author = 'GDS Team'
    CompanyName = 'GDS'
    Copyright = '(c) GDS Team. All rights reserved.'
    Description = 'NuGet package building and publishing for GDS PowerShell modules'
    PowerShellVersion = '5.1'
    RequiredModules = @(
        @{ ModuleName = 'GDS.Common'; ModuleVersion = '1.0.0' }
    )
    FunctionsToExport = @(
        'Build-NuGetPackage',
        'Build-AllNuGetPackages',
        'Publish-NuGetPackage'
    )
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
    PrivateData = @{
        PSData = @{
            Tags = @('Build', 'CI/CD', 'NuGet', 'GDS', 'DevOps')
            LicenseUri = ''
            ProjectUri = ''
            IconUri = ''
            ReleaseNotes = 'Initial release - NuGet package building and publishing for GDS modules'
        }
    }
}

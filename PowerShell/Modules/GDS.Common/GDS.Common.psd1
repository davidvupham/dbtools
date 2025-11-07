@{
    RootModule = 'GDS.Common.psm1'
    ModuleVersion = '1.0.0'
    GUID = '12345678-1234-1234-1234-123456789000'
    Author = 'GDS Team'
    CompanyName = 'GDS'
    Copyright = '(c) GDS Team. All rights reserved.'
    Description = 'Common utilities and shared functions for GDS PowerShell modules'
    PowerShellVersion = '5.1'
    RequiredModules = @(
        @{ ModuleName = 'PSFramework'; ModuleVersion = '1.7.0' }
    )
    FunctionsToExport = @(
        'Write-Log',
        'Initialize-Logging',
        'Set-GDSLogging'
    )
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
    PrivateData = @{
        PSData = @{
            Tags = @('Common', 'Logging', 'GDS')
            LicenseUri = ''
            ProjectUri = ''
            IconUri = ''
            ReleaseNotes = ''
        }
    }
}

@{
    RootModule = 'GDS.Logging.psm1'
    ModuleVersion = '1.0.0'
    GUID = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    Author = 'GDS Team'
    CompanyName = 'GDS'
    Copyright = '(c) GDS Team. All rights reserved.'
    Description = 'Logging utilities for GDS PowerShell modules using PSFramework'
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
            Tags = @('Logging', 'GDS', 'PSFramework')
            LicenseUri = ''
            ProjectUri = ''
            IconUri = ''
            ReleaseNotes = ''
        }
    }
}

@{
    RootModule = 'GDS.ActiveDirectory.psm1'
    ModuleVersion = '1.0.0'
    GUID = '12345678-1234-1234-1234-123456789017'
    Author = 'GDS Team'
    CompanyName = 'GDS'
    Copyright = '(c) GDS Team. All rights reserved.'
    Description = 'Functions for Active Directory management'
    PowerShellVersion = '5.1'
    RequiredModules = @(
        @{ ModuleName = 'GDS.Logging'; ModuleVersion = '1.0.0' }
    )
    FunctionsToExport = @('Export-ADObjectsToDatabase', 'Get-GdsUserGroupMembership', 'Remove-GdsUserGroupMembership')
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
    PrivateData = @{
        PSData = @{
            Tags = @('ActiveDirectory', 'AD', 'GDS')
            LicenseUri = ''
            ProjectUri = ''
            IconUri = ''
            ReleaseNotes = ''
        }
    }
}

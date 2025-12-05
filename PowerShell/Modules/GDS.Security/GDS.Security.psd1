@{
    RootModule        = 'GDS.Security.psm1'
    ModuleVersion     = '1.0.0'
    GUID              = 'a1b2c3d4-e5f6-7890-1234-567890abcdef'
    Author            = 'GDS'
    CompanyName       = 'GDS'
    Copyright         = '(c) 2025 GDS. All rights reserved.'
    Description       = 'Module for security-related functions, including script signing and certificate management.'
    PowerShellVersion = '5.1'
    FunctionsToExport = @('New-GDSSelfSignedCertificate', 'Set-GDSAuthenticodeSignature')
    CmdletsToExport   = @()
    VariablesToExport = @()
    AliasesToExport   = @()
}

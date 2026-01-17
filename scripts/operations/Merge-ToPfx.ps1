<#
.SYNOPSIS
    Merges a Certificate (.crt) and Private Key (.key) into a PFX file using PowerShell 7+.
    Does NOT require OpenSSL.

.DESCRIPTION
    Uses .NET Core's X509Certificate2.CreateFromPem or CreateFromEncryptedPem to pair keys.
    Requires PowerShell 7.0 or newer (Core).

    Equivalent OpenSSL command:
    openssl pkcs12 -export -out "NewCertificate.pfx" -inkey "my.key" -in "my.cert"

.PARAMETER CertFile
    Path to the public certificate file (.crt, .cert, or .cer).

.PARAMETER KeyFile
    Path to the private key file (.key).

.PARAMETER KeyPassword
    (Optional) Password if the .key file is encrypted.
    If you have a .pass file, pass its content here: -KeyPassword (Get-Content claim.pass)

.PARAMETER OutputFile
    Path to save the resulting .pfx file. Defaults to "NewCertificate.pfx".

.EXAMPLE
    .\Merge-ToPfx.ps1 -CertFile "my.cert" -KeyFile "my.key" -KeyPassword "secret"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$CertFile,

    [Parameter(Mandatory)]
    [string]$KeyFile,

    [Parameter()]
    [string]$KeyPassword,

    [Parameter()]
    [string]$OutputFile = ".\NewCertificate.pfx"
)

# Function to read file content ensuring absolute paths
function Get-FileContent {
    param($Path)
    $FullPath = Resolve-Path $Path
    return [System.IO.File]::ReadAllText($FullPath)
}

if ($PSVersionTable.PSVersion.Major -lt 7) {
    Throw "This script requires PowerShell 7 (Core) or newer to use .NET generic PEM loaders."
}

Write-Host "Reading Certificate and Key..." -ForegroundColor Cyan

$certContent = Get-FileContent -Path $CertFile
$keyContent = Get-FileContent -Path $KeyFile

$certObj = $null

try {
    if ([string]::IsNullOrWhiteSpace($KeyPassword)) {
        # Attempt to load as unencrypted
        Write-Host "Attempting to create from unencrypted PEM..."
        $certObj = [System.Security.Cryptography.X509Certificates.X509Certificate2]::CreateFromPem($certContent, $keyContent)
    }
    else {
        # Attempt to load as encrypted
        Write-Host "Attempting to create from ENCRYPTED PEM..."
        $certObj = [System.Security.Cryptography.X509Certificates.X509Certificate2]::CreateFromEncryptedPem($certContent, $keyContent, $KeyPassword)
    }
}
catch {
    Write-Error "Failed to combine Certificate and Key. Ensure the password is correct/matching."
    Write-Error $_
    exit 1
}

if ($certObj -and $certObj.HasPrivateKey) {
    Write-Host "Success! Certificate paired with Private Key." -ForegroundColor Green

    # Prompt for PFX export password
    Write-Host "Enter a password to protect the new .pfx file:" -ForegroundColor Yellow
    $pfxPass = Read-Host -AsSecureString

    # Export
    $pfxBytes = $certObj.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Pfx, $pfxPass)
    [System.IO.File]::WriteAllBytes((Resolve-Path . -Path $OutputFile), $pfxBytes)

    Write-Host "Created: $OutputFile" -ForegroundColor Green
}
else {
    Write-Error "Could not verify private key linking."
}

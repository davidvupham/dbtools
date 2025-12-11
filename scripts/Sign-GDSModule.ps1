<#
.SYNOPSIS
    Signs all PowerShell module files recursively using a Code Signing certificate.

.DESCRIPTION
    This script automates the signing of PowerShell scripts (.ps1), modules (.psm1),
    manifests (.psd1), and type data (.ps1xml).

    It automatically searches for a valid Code Signing certificate in the CurrentUser\My store.
    If multiple are found, it selects the one with the latest expiration date.

.PARAMETER ModulePath
    Path to the module or directory containing files to sign. Defaults to the current location.

.PARAMETER TimeStampServer
    URL of the timestamp server. Defaults to DigiCert's timestamp server.
    Using a timestamp server ensures signatures remain valid verifying the certificate was valid at time of signing.

.EXAMPLE
    .\Sign-GDSModule.ps1 -ModulePath "C:\Repo\MyModule"
#>
param (
    [Parameter(Mandatory = $false)]
    [string]$ModulePath = $PWD,

    [Parameter(Mandatory = $false)]
    [string]$TimeStampServer = "http://timestamp.digicert.com"
)

$ErrorActionPreference = "Stop"

Write-Host "Searching for valid Code Signing certificate..." -ForegroundColor Cyan

# Find valid code signing cert (CodeSigningOid = 1.3.6.1.5.5.7.3.3)
# We filter for only valid (unexpired) certs and pick the one that expires last (newest/most recent)
$cert = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert |
Where-Object { $_.NotAfter -gt (Get-Date) } |
Sort-Object NotAfter |
Select-Object -Last 1

if (-not $cert) {
    Write-Error "No valid Code Signing certificate found in Cert:\CurrentUser\My"
    exit 1
}

Write-Host "Found Certificate: $($cert.Subject)" -ForegroundColor Green
Write-Host "Thumbprint:        $($cert.Thumbprint)" -ForegroundColor Gray
Write-Host "Expires:           $($cert.NotAfter)" -ForegroundColor Gray

# specific extensions to sign
$extensions = @("*.ps1", "*.psm1", "*.psd1", "*.ps1xml")

Write-Host "Scanning '$ModulePath' for files..." -ForegroundColor Cyan
$files = Get-ChildItem -Path $ModulePath -Include $extensions -Recurse

if ($files.Count -eq 0) {
    Write-Warning "No PowerShell files found to sign in $ModulePath"
    exit 0
}

Write-Host "Signing $($files.Count) files..." -ForegroundColor Cyan

foreach ($file in $files) {
    Write-Host "Signing: $($file.Name)" -NoNewline

    try {
        $sig = Set-AuthenticodeSignature -FilePath $file.FullName `
            -Certificate $cert `
            -TimestampServer $TimeStampServer `
            -ErrorAction Stop

        if ($sig.Status -eq 'Valid') {
            Write-Host " [OK]" -ForegroundColor Green
        }
        else {
            Write-Host " [$($sig.Status)]" -ForegroundColor Red
            Write-Warning "Signature status for $($file.Name) is $($sig.Status). Check error details."
        }
    }
    catch {
        Write-Host " [FAILED]" -ForegroundColor Red
        Write-Error $_
    }
}

Write-Host "Done." -ForegroundColor Green

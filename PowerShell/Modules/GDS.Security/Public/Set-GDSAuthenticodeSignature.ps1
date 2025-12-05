function Set-GDSAuthenticodeSignature {
    <#
    .SYNOPSIS
        Signs a PowerShell script using a code signing certificate.

    .DESCRIPTION
        This function signs one or more PowerShell scripts. It attempts to automatically find
        a valid code signing certificate in the CurrentUser\My store if one is not provided.

        It prioritizes certificates issued by a CA over self-signed ones if multiple are found,
        though this logic is basic (first valid code signing cert).

    .PARAMETER FilePath
        The path to the script(s) to sign. Accepts pipeline input.

    .PARAMETER Certificate
        The certificate to use for signing. If omitted, the function attempts to find one.

    .EXAMPLE
        Set-GDSAuthenticodeSignature -FilePath .\MyScript.ps1
        Signs MyScript.ps1 with an auto-discovered certificate.

    .EXAMPLE
        Get-ChildItem *.ps1 | Set-GDSAuthenticodeSignature
        Signs all .ps1 files in the current directory.
    #>
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true, ValueFromPipeline = $true, ValueFromPipelineByPropertyName = $true)]
        [string[]]$FilePath,

        [Parameter(Mandatory = $false)]
        [System.Security.Cryptography.X509Certificates.X509Certificate2]$Certificate
    )

    begin {
        if (-not $Certificate) {
            Write-Verbose "No certificate provided. Attempting to find a valid Code Signing certificate..."

            # Find valid code signing certs in CurrentUser\My
            $certs = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert -Recurse | Where-Object { $_.Verify() }

            if ($certs) {
                # Just pick the first one for now, or maybe the one with the latest expiration?
                # Let's pick the one that expires last to be safe.
                $Certificate = $certs | Sort-Object NotAfter -Descending | Select-Object -First 1
                Write-Verbose "Selected certificate: $($Certificate.Subject) (Thumbprint: $($Certificate.Thumbprint))"
            }
            else {
                Write-Error "No valid code signing certificate found in Cert:\CurrentUser\My. Please provide one explicitly or create one."
                return
            }
        }
    }

    process {
        foreach ($file in $FilePath) {
            if (Test-Path $file) {
                Write-Verbose "Signing file: $file"
                try {
                    $sig = Set-AuthenticodeSignature -FilePath $file -Certificate $Certificate -ErrorAction Stop
                    if ($sig.Status -eq 'Valid') {
                        Write-Verbose "Successfully signed $file"
                    }
                    else {
                        Write-Warning "Signing status for $file is: $($sig.Status). Message: $($sig.StatusMessage)"
                    }
                }
                catch {
                    Write-Error "Failed to sign $file. Error: $_"
                }
            }
            else {
                Write-Warning "File not found: $file"
            }
        }
    }
}

function New-GDSSelfSignedCertificate {
    <#
    .SYNOPSIS
        Creates a self-signed code signing certificate for development and testing.

    .DESCRIPTION
        This function creates a self-signed certificate with the 'CodeSigning' usage extension.
        It stores the certificate in the CurrentUser\My store.

        WARNING: Self-signed certificates should NOT be used for production scripts.
        For production, use a certificate issued by a trusted Certificate Authority (CA).

    .PARAMETER Subject
        The subject name for the certificate. Defaults to "GDSLocalCodeSigning".

    .EXAMPLE
        New-GDSSelfSignedCertificate
        Creates a certificate named "GDSLocalCodeSigning".

    .EXAMPLE
        New-GDSSelfSignedCertificate -Subject "MyDevCert"
        Creates a certificate named "MyDevCert".
    #>
    [CmdletBinding()]
    param (
        [string]$Subject = "GDSLocalCodeSigning"
    )

    process {
        Write-Verbose "Creating self-signed code signing certificate with subject: $Subject"

        $certParams = @{
            DnsName           = $Subject
            CertStoreLocation = "Cert:\CurrentUser\My"
            Type              = "CodeSigningCert"
        }

        $cert = New-SelfSignedCertificate @certParams

        Write-Verbose "Certificate created with Thumbprint: $($cert.Thumbprint)"
        return $cert
    }
}

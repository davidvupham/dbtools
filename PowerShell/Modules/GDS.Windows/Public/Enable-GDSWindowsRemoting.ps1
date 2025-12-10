function Enable-GDSWindowsRemoting {
    <#
    .SYNOPSIS
        Configures Windows Remote Management (WinRM) for Ansible connectivity.

    .DESCRIPTION
        This function configures a Windows host for Ansible management by:
        - Enabling the WinRM service.
        - Creating a WinRM HTTPS listener.
        - Configuring firewall rules for WinRM HTTPS (port 5986).
        - Configuring authentication methods (Basic, CredSSP).

        It supports both local execution and remote execution on a list of servers via Invoke-Command.

        SECURITY NOTE:
        - HTTPS is enforced. HTTP (Port 5985) is NOT supported.
        - Basic Authentication is DISABLED by default.
        - LocalAccountTokenFilterPolicy is NOT enabled by default.

    .PARAMETER ComputerName
        An array of computer names to configure. Defaults to 'localhost'.
        If remote computers are specified, the function uses Invoke-Command to execute the configuration logic on them.

    .PARAMETER Credential
        The credentials to use when connecting to remote computers.

    .PARAMETER SubjectName
        The subject name for the self-signed certificate (if generated). Defaults to the computer name.

    .PARAMETER CertValidityDays
        The validity period in days for the self-signed certificate. Defaults to 1095 days (3 years).

    .PARAMETER SkipNetworkProfileCheck
        If specified, enables PS Remoting without checking the network profile (useful for Public networks).

    .PARAMETER CreateSelfSignedCert
        Deprecated. Use -ForceNewSSLCert to generate a self-signed certificate.

    .PARAMETER ForceNewSSLCert
        If specified, forces the generation of a new self-signed certificate, even if a listener exists.
        You must specify either this parameter OR -CertificateThumbprint.

    .PARAMETER CertificateThumbprint
        The thumbprint of an existing certificate to use for the WinRM HTTPS listener.
        The certificate must exist in the LocalMachine\My store.
        You must specify either this parameter OR -ForceNewSSLCert.

    .PARAMETER EnableBasicAuth
        If specified, enables Basic authentication. Defaults to $false (Basic auth DISABLED).
        WARNING: Basic authentication sends credentials in clear text if not using HTTPS. Since this function enforces HTTPS, it is safer, but still less secure than Kerberos.

    .PARAMETER EnableCredSSP
        If specified, enables CredSSP authentication.

    .PARAMETER EnableLocalAccountTokenFilter
        If specified, sets the LocalAccountTokenFilterPolicy to 1.
        This is REQUIRED if you are using a LOCAL Administrator account for remote access.
        It is NOT required for Domain accounts.
        Defaults to $false.

    .EXAMPLE
        # Generate a new self-signed certificate and configure locally (Secure Defaults)
        Enable-GDSWindowsRemoting -ForceNewSSLCert

    .EXAMPLE
        # Use an existing certificate from an internal CA
        Enable-GDSWindowsRemoting -CertificateThumbprint "A1B2C3D4E5F6..."

    .EXAMPLE
        # Configure a remote server using an existing certificate
        Enable-GDSWindowsRemoting -ComputerName "Server01" -Credential (Get-Credential) -CertificateThumbprint "A1B2C3D4E5F6..."

    .EXAMPLE
        # Enable Basic Auth and Local Admin access (Legacy/Dev scenarios)
        Enable-GDSWindowsRemoting -ForceNewSSLCert -EnableBasicAuth -EnableLocalAccountTokenFilter
    #>
    [CmdletBinding(SupportsShouldProcess = $true)]
    Param (
        [Parameter(ValueFromPipeline = $true)]
        [ValidateNotNullOrEmpty()]
        [string[]]$ComputerName = "localhost",

        [pscredential]$Credential,

        [string]$SubjectName = $env:COMPUTERNAME,
        [int]$CertValidityDays = 1095,
        [switch]$SkipNetworkProfileCheck,
        [bool]$CreateSelfSignedCert = $false,
        [switch]$ForceNewSSLCert,
        [string]$CertificateThumbprint,
        [switch]$EnableBasicAuth = $false,
        [switch]$EnableCredSSP,
        [switch]$EnableLocalAccountTokenFilter,
        [switch]$LogToEventLog
    )

    Begin {
        # Define the configuration logic as a script block
        $ConfigurationScript = {
            [CmdletBinding()]
            Param (
                $SubjectName,
                $CertValidityDays,
                $SkipNetworkProfileCheck,
                $CreateSelfSignedCert,
                $ForceNewSSLCert,
                $CertificateThumbprint,
                $EnableBasicAuth,
                $EnableCredSSP,
                $EnableLocalAccountTokenFilter,
                $LogToEventLog
            )

            # --- Embedded Private Functions ---

            function New-GDSLegacySelfSignedCert {
                [CmdletBinding()]
                Param (
                    [Parameter(Mandatory = $true)]
                    [string]$SubjectName,

                    [int]$ValidDays = 1095
                )

                $hostnonFQDN = $env:computerName
                $hostFQDN = [System.Net.Dns]::GetHostByName(($env:computerName)).Hostname
                $SignatureAlgorithm = "SHA256"

                $name = New-Object -COM "X509Enrollment.CX500DistinguishedName.1"
                $name.Encode("CN=$SubjectName", 0)

                $key = New-Object -COM "X509Enrollment.CX509PrivateKey.1"
                $key.ProviderName = "Microsoft Enhanced RSA and AES Cryptographic Provider"
                $key.KeySpec = 1
                $key.Length = 4096
                $key.SecurityDescriptor = "D:PAI(A;;0xd01f01ff;;;SY)(A;;0xd01f01ff;;;BA)(A;;0x80120089;;;NS)"
                $key.MachineContext = 1
                $key.Create()

                $serverauthoid = New-Object -COM "X509Enrollment.CObjectId.1"
                $serverauthoid.InitializeFromValue("1.3.6.1.5.5.7.3.1")
                $ekuoids = New-Object -COM "X509Enrollment.CObjectIds.1"
                $ekuoids.Add($serverauthoid)
                $ekuext = New-Object -COM "X509Enrollment.CX509ExtensionEnhancedKeyUsage.1"
                $ekuext.InitializeEncode($ekuoids)

                $cert = New-Object -COM "X509Enrollment.CX509CertificateRequestCertificate.1"
                $cert.InitializeFromPrivateKey(2, $key, "")
                $cert.Subject = $name
                $cert.Issuer = $cert.Subject
                $cert.NotBefore = (Get-Date).AddDays(-1)
                $cert.NotAfter = $cert.NotBefore.AddDays($ValidDays)

                $SigOID = New-Object -ComObject X509Enrollment.CObjectId
                $SigOID.InitializeFromValue(([Security.Cryptography.Oid]$SignatureAlgorithm).Value)

                [string[]] $AlternativeName += $hostnonFQDN
                $AlternativeName += $hostFQDN
                $IAlternativeNames = New-Object -ComObject X509Enrollment.CAlternativeNames

                foreach ($AN in $AlternativeName) {
                    $AltName = New-Object -ComObject X509Enrollment.CAlternativeName
                    $AltName.InitializeFromString(0x3, $AN)
                    $IAlternativeNames.Add($AltName)
                }

                $SubjectAlternativeName = New-Object -ComObject X509Enrollment.CX509ExtensionAlternativeNames
                $SubjectAlternativeName.InitializeEncode($IAlternativeNames)

                [String[]]$KeyUsage = ("DigitalSignature", "KeyEncipherment")
                $KeyUsageObj = New-Object -ComObject X509Enrollment.CX509ExtensionKeyUsage
                $KeyUsageObj.InitializeEncode([int][Security.Cryptography.X509Certificates.X509KeyUsageFlags]($KeyUsage))
                $KeyUsageObj.Critical = $true

                $cert.X509Extensions.Add($KeyUsageObj)
                $cert.X509Extensions.Add($ekuext)
                $cert.SignatureInformation.HashAlgorithm = $SigOID
                $CERT.X509Extensions.Add($SubjectAlternativeName)
                $cert.Encode()

                $enrollment = New-Object -COM "X509Enrollment.CX509Enrollment.1"
                $enrollment.InitializeFromRequest($cert)
                $certdata = $enrollment.CreateRequest(0)
                $enrollment.InstallResponse(2, $certdata, 0, "")

                # extract/return the thumbprint from the generated cert
                $parsed_cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2
                $parsed_cert.Import([System.Text.Encoding]::UTF8.GetBytes($certdata))

                return $parsed_cert.Thumbprint
            }

            function New-GDSModernSelfSignedCert {
                [CmdletBinding()]
                Param (
                    [Parameter(Mandatory = $true)]
                    [string]$SubjectName,

                    [int]$ValidDays = 1095
                )

                $certParam = @{
                    DnsName           = $SubjectName
                    CertStoreLocation = "Cert:\LocalMachine\My"
                    NotAfter          = (Get-Date).AddDays($ValidDays)
                    FriendlyName      = "GDSWinRM-SelfSigned"
                    TextExtension     = @("2.5.29.37={text}1.3.6.1.5.5.7.3.1") # Server Auth EKU
                }

                $cert = New-SelfSignedCertificate @certParam
                return $cert.Thumbprint
            }

            # --- End Embedded Private Functions ---

            # Helper functions for logging
            function Write-ProgressLog {
                $Message = $args[0]
                $EventSource = "Enable-GDSWindowsRemoting"

                if ($LogToEventLog) {
                    if ([System.Diagnostics.EventLog]::Exists('Application') -eq $False -or [System.Diagnostics.EventLog]::SourceExists($EventSource) -eq $False) {
                        try {
                            New-EventLog -LogName Application -Source $EventSource -ErrorAction Stop
                        }
                        catch {
                            Write-Warning "Could not create EventLog source. Run as Administrator."
                        }
                    }
                    try {
                        Write-EventLog -LogName Application -Source $EventSource -EntryType Information -EventId 1 -Message $Message -ErrorAction SilentlyContinue
                    }
                    catch {}
                }
            }

            function Write-VerboseLog {
                $Message = $args[0]
                Write-Verbose $Message
                Write-ProgressLog $Message
            }

            function Write-HostLog {
                $Message = $args[0]
                Write-Output $Message
                Write-ProgressLog $Message
            }

            $ErrorActionPreference = "Stop"

            try {
                # Get the ID and security principal of the current user account
                $myWindowsID = [System.Security.Principal.WindowsIdentity]::GetCurrent()
                $myWindowsPrincipal = new-object System.Security.Principal.WindowsPrincipal($myWindowsID)

                # Get the security principal for the Administrator role
                $adminRole = [System.Security.Principal.WindowsBuiltInRole]::Administrator

                # Check to see if we are currently running "as Administrator"
                if (-Not $myWindowsPrincipal.IsInRole($adminRole)) {
                    throw "You need elevated Administrator privileges in order to run this script. Start Windows PowerShell by using the Run as Administrator option."
                }

                # Detect PowerShell version.
                if ($PSVersionTable.PSVersion.Major -lt 3) {
                    throw "PowerShell version 3 or higher is required."
                }

                # --- Certificate Auto-Detection Logic ---
                if (-not $CertificateThumbprint -and -not $ForceNewSSLCert) {
                    Write-Verbose "No certificate specified. Attempting to auto-detect a valid Server Authentication certificate..."

                    $certs = Get-ChildItem Cert:\LocalMachine\My
                    $candidates = $certs | Where-Object {
                        $_.Subject -like "*$env:COMPUTERNAME*" -and
                        $_.NotAfter -gt (Get-Date) -and
                        ($_.EnhancedKeyUsageList.FriendlyName -eq "Server Authentication" -or
                        ($_.Extensions | Where-Object { $_.Oid.Value -eq "1.3.6.1.5.5.7.3.1" }))
                    }

                    if ($candidates.Count -eq 1) {
                        $CertificateThumbprint = $candidates[0].Thumbprint
                        Write-HostLog "Auto-detected valid certificate: $($candidates[0].Subject) (Thumbprint: $CertificateThumbprint)"
                    }
                    elseif ($candidates.Count -gt 1) {
                        $errorMsg = "Multiple valid certificates found matching hostname '$env:COMPUTERNAME'. Please specify -CertificateThumbprint explicitly.`n" +
                        ($candidates | Format-Table Subject, Thumbprint, NotAfter | Out-String)
                        throw $errorMsg
                    }
                    else {
                        Write-Warning "No valid 'Server Authentication' certificate found matching hostname '$env:COMPUTERNAME'. A new self-signed certificate will be generated."
                        $ForceNewSSLCert = $true
                    }
                }
                # ----------------------------------------

                # Find and start the WinRM service.
                Write-Verbose "Verifying WinRM service."
                $winrmService = Get-Service "WinRM" -ErrorAction SilentlyContinue
                if (-not $winrmService) {
                    throw "Unable to find the WinRM service."
                }

                if ($winrmService.Status -ne "Running") {
                    Write-Verbose "Setting WinRM service to start automatically on boot."
                    Set-Service -Name "WinRM" -StartupType Automatic
                    Write-Verbose "Starting WinRM service."
                    Start-Service -Name "WinRM" -ErrorAction Stop
                    Write-ProgressLog "Started WinRM service."
                }

                # Make sure there is a SSL listener.
                $listeners = Get-ChildItem WSMan:\localhost\Listener
                if (-not ($listeners | Where-Object { $_.Keys -like "TRANSPORT=HTTPS" })) {

                    $thumbprint = $null

                    if ($CertificateThumbprint) {
                        # Verify certificate exists
                        $cert = Get-Item "Cert:\LocalMachine\My\$CertificateThumbprint" -ErrorAction SilentlyContinue
                        if (-not $cert) {
                            throw "Certificate with thumbprint $CertificateThumbprint not found in Cert:\LocalMachine\My"
                        }
                        $thumbprint = $CertificateThumbprint
                        Write-HostLog "Using existing certificate with thumbprint: $thumbprint"
                    }
                    else {
                        # Generate Self-Signed Cert
                        if (Get-Command New-SelfSignedCertificate -ErrorAction SilentlyContinue) {
                            $thumbprint = New-GDSModernSelfSignedCert -SubjectName $SubjectName -ValidDays $CertValidityDays
                            Write-HostLog "Modern self-signed SSL certificate generated; thumbprint: $thumbprint"
                        }
                        else {
                            $thumbprint = New-GDSLegacySelfSignedCert -SubjectName $SubjectName -ValidDays $CertValidityDays
                            Write-HostLog "Legacy self-signed SSL certificate generated; thumbprint: $thumbprint"
                        }
                    }

                    $valueset = @{
                        Hostname              = $SubjectName
                        CertificateThumbprint = $thumbprint
                    }

                    $selectorset = @{
                        Transport = "HTTPS"
                        Address   = "*"
                    }

                    Write-Verbose "Enabling SSL listener."
                    New-WSManInstance -ResourceURI 'winrm/config/Listener' -SelectorSet $selectorset -ValueSet $valueset
                    Write-ProgressLog "Enabled SSL listener."
                }
                else {
                    Write-Verbose "SSL listener is already active."

                    # Force a new SSL cert on Listener if the $ForceNewSSLCert
                    if ($ForceNewSSLCert) {
                        if (Get-Command New-SelfSignedCertificate -ErrorAction SilentlyContinue) {
                            $thumbprint = New-GDSModernSelfSignedCert -SubjectName $SubjectName -ValidDays $CertValidityDays
                            Write-HostLog "Modern self-signed SSL certificate generated; thumbprint: $thumbprint"
                        }
                        else {
                            $thumbprint = New-GDSLegacySelfSignedCert -SubjectName $SubjectName -ValidDays $CertValidityDays
                            Write-HostLog "Legacy self-signed SSL certificate generated; thumbprint: $thumbprint"
                        }

                        $valueset = @{
                            CertificateThumbprint = $thumbprint
                            Hostname              = $SubjectName
                        }

                        # Delete the listener for SSL
                        $selectorset = @{
                            Address   = "*"
                            Transport = "HTTPS"
                        }
                        Remove-WSManInstance -ResourceURI 'winrm/config/Listener' -SelectorSet $selectorset

                        # Add new Listener with new SSL cert
                        New-WSManInstance -ResourceURI 'winrm/config/Listener' -SelectorSet $selectorset -ValueSet $valueset
                    }
                }

                # Check for basic authentication.
                $basicAuthSetting = Get-ChildItem WSMan:\localhost\Service\Auth | Where-Object { $_.Name -eq "Basic" }

                if ($EnableBasicAuth) {
                    if (($basicAuthSetting.Value) -eq $false) {
                        Write-Verbose "Enabling basic auth support."
                        Set-Item -Path "WSMan:\localhost\Service\Auth\Basic" -Value $true
                        Write-ProgressLog "Enabled basic auth support."
                    }
                    else {
                        Write-Verbose "Basic auth is already enabled."
                    }
                }
                else {
                    if (($basicAuthSetting.Value) -eq $true) {
                        Write-Verbose "Disabling basic auth support (Secure Default)."
                        Set-Item -Path "WSMan:\localhost\Service\Auth\Basic" -Value $false
                        Write-ProgressLog "Disabled basic auth support."
                    }
                    else {
                        Write-Verbose "Basic auth is already disabled."
                    }
                }

                # If EnableCredSSP if set to true
                if ($EnableCredSSP) {
                    # Check for CredSSP authentication
                    $credsspAuthSetting = Get-ChildItem WSMan:\localhost\Service\Auth | Where-Object { $_.Name -eq "CredSSP" }
                    if (($credsspAuthSetting.Value) -eq $false) {
                        Write-Verbose "Enabling CredSSP auth support."
                        Enable-WSManCredSSP -role server -Force
                        Write-ProgressLog "Enabled CredSSP auth support."
                    }
                }

                # Configure firewall to allow WinRM HTTPS connections.
                if (Get-Command New-NetFirewallRule -ErrorAction SilentlyContinue) {
                    # Modern Windows (Use NetSecurity module)
                    $fwRule = Get-NetFirewallRule -DisplayName "Allow WinRM HTTPS" -ErrorAction SilentlyContinue
                    if (-not $fwRule) {
                        Write-Verbose "Adding firewall rule 'Allow WinRM HTTPS' (NetSecurity)."
                        New-NetFirewallRule -DisplayName "Allow WinRM HTTPS" -Name "WinRM-HTTPS-Port-5986" -Direction Inbound -LocalPort 5986 -Protocol TCP -Action Allow -Profile Any
                        Write-ProgressLog "Added firewall rule to allow WinRM HTTPS."
                    }
                    else {
                        Write-Verbose "Firewall rule 'Allow WinRM HTTPS' already exists."
                    }
                }
                else {
                    # Legacy Windows (Use netsh)
                    $fwtest1 = netsh advfirewall firewall show rule name="Allow WinRM HTTPS"
                    $fwtest2 = netsh advfirewall firewall show rule name="Allow WinRM HTTPS" profile=any
                    if ($fwtest1.count -lt 5) {
                        Write-Verbose "Adding firewall rule to allow WinRM HTTPS."
                        netsh advfirewall firewall add rule profile=any name="Allow WinRM HTTPS" dir=in localport=5986 protocol=TCP action=allow
                        Write-ProgressLog "Added firewall rule to allow WinRM HTTPS."
                    }
                    elseif (($fwtest1.count -ge 5) -and ($fwtest2.count -lt 5)) {
                        Write-Verbose "Updating firewall rule to allow WinRM HTTPS for any profile."
                        netsh advfirewall firewall set rule name="Allow WinRM HTTPS" new profile=any
                        Write-ProgressLog "Updated firewall rule to allow WinRM HTTPS for any profile."
                    }
                    else {
                        Write-Verbose "Firewall rule already exists to allow WinRM HTTPS."
                    }
                }

                $httpsOptions = New-PSSessionOption -SkipCACheck -SkipCNCheck -SkipRevocationCheck
                $httpsResult = New-PSSession -UseSSL -ComputerName "localhost" -SessionOption $httpsOptions -ErrorVariable httpsError -ErrorAction SilentlyContinue

                if ($httpsResult) {
                    Write-Verbose "HTTPS: Enabled"
                    Remove-PSSession $httpsResult
                }
                else {
                    throw "Unable to establish an HTTPS remoting session to localhost."
                }
                Write-VerboseLog "PS Remoting has been successfully configured for Ansible."

            }
            catch {
                Write-Error "Configuration failed: $($_.Exception.Message)"
                throw $_
            }
        }
    }

    Process {
        $localTargets = @()
        $remoteTargets = @()

        foreach ($Computer in $ComputerName) {
            if ($Computer -eq "localhost" -or $Computer -eq $env:COMPUTERNAME) {
                $localTargets += $Computer
            }
            else {
                $remoteTargets += $Computer
            }
        }

        # 1. Process Local Targets (Sequential)
        foreach ($Computer in $localTargets) {
            Write-Verbose "Processing target (Local): $Computer"
            try {
                & $ConfigurationScript -SubjectName $SubjectName `
                    -CertValidityDays $CertValidityDays `
                    -SkipNetworkProfileCheck:$SkipNetworkProfileCheck `
                    -CreateSelfSignedCert:$CreateSelfSignedCert `
                    -ForceNewSSLCert:$ForceNewSSLCert `
                    -CertificateThumbprint $CertificateThumbprint `
                    -EnableBasicAuth:$EnableBasicAuth `
                    -EnableCredSSP:$EnableCredSSP `
                    -EnableLocalAccountTokenFilter:$EnableLocalAccountTokenFilter `
                    -LogToEventLog:$LogToEventLog
            }
            catch {
                Write-Error "Failed to configure local machine: $_"
            }
        }

        # 2. Process Remote Targets (Batched/Parallel)
        if ($remoteTargets.Count -gt 0) {
            Write-Verbose "Processing targets (Remote): $($remoteTargets -join ', ')"

            $InvokeParams = @{
                ComputerName = $remoteTargets
                ScriptBlock  = $ConfigurationScript
                ArgumentList = @(
                    $SubjectName,
                    $CertValidityDays,
                    $SkipNetworkProfileCheck,
                    $CreateSelfSignedCert,
                    $ForceNewSSLCert,
                    $CertificateThumbprint,
                    $EnableBasicAuth,
                    $EnableCredSSP,
                    $EnableLocalAccountTokenFilter,
                    $LogToEventLog
                )
            }

            if ($Credential) {
                $InvokeParams.Credential = $Credential
            }

            try {
                Invoke-Command @InvokeParams -ErrorAction Stop
            }
            catch {
                Write-Error "Failed to execute on remote targets: $_"
            }
        }
    }
}

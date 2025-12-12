function Enable-GDSWindowsRemoting {
    <#
    .SYNOPSIS
        Configures Windows Remote Management (WinRM) with HTTPS for secure remote access.

    .DESCRIPTION
        This function configures a Windows host for secure remote management by:
        - Enabling the WinRM service.
        - Creating a WinRM HTTPS listener.
        - Configuring firewall rules for WinRM HTTPS (port 5986).
        - Configuring authentication methods.

        Use cases include PowerShell remoting, Ansible, SCCM, and other management tools.

        It supports both local execution and remote execution on a list of servers via Invoke-Command.

        BEHAVIOR:

        WinRM Service:
        - If WinRM is already running: No changes to service or authentication settings.
        - If WinRM is not running: Service is started, set to automatic, and secure defaults applied.

        Listeners (always ensured, independent of WinRM state):
        - HTTPS listener on port 5986 is always ensured (created if missing).
        - Existing HTTP listeners are never modified or removed.

        Firewall (always ensured, independent of WinRM state):
        - Firewall rule for port 5986 is always ensured (added if missing).

        Authentication (only applied on fresh WinRM setup):
        - Kerberos and Negotiate: Enabled by default (no action needed).
        - Basic: DISABLED by default. Use -EnableBasicAuth to enable.
        - CredSSP: Disabled. Use -EnableCredSSP to enable.
        - CredSSP: Disabled. Use -EnableCredSSP to enable.

    .PARAMETER ComputerName
        An array of computer names to configure. Defaults to 'localhost'.
        If remote computers are specified, the function uses Invoke-Command to execute the configuration logic on them.

    .PARAMETER Credential
        The credentials to use when connecting to remote computers.

    .PARAMETER CertificateThumbprint
        The thumbprint of an existing "Server Authentication" certificate to use for the WinRM HTTPS listener.
        If not specified, the function attempts to auto-detect a valid certificate matching the hostname.
        If no valid certificate is found, the function will throw an error.

    .PARAMETER EnableBasicAuth
        If specified, enables Basic authentication. Defaults to $false (Basic auth DISABLED).
        WARNING: Basic authentication sends credentials in clear text if not using HTTPS. Since this function enforces HTTPS, it is safer, but still less secure than Kerberos.

    .PARAMETER EnableCredSSP
        If specified, enables CredSSP authentication.

    .PARAMETER LogToEventLog
        If specified, writes configuration progress and errors to the Windows Event Log (Application log, Source: Enable-GDSWindowsRemoting).

    .EXAMPLE
        # Configure locally using an auto-detected valid certificate
        Enable-GDSWindowsRemoting

    .EXAMPLE
        # Use an existing certificate from an internal CA
        Enable-GDSWindowsRemoting -CertificateThumbprint "A1B2C3D4E5F6..."

    .EXAMPLE
        # Configure a remote server using an existing certificate
        Enable-GDSWindowsRemoting -ComputerName "Server01" -Credential (Get-Credential) -CertificateThumbprint "A1B2C3D4E5F6..."

    .EXAMPLE
        Enable-GDSWindowsRemoting -EnableBasicAuth
    #>
    [CmdletBinding(SupportsShouldProcess = $true)]
    Param (
        [Parameter(ValueFromPipeline = $true)]
        [ValidateNotNullOrEmpty()]
        [string[]]$ComputerName = "localhost",

        [pscredential]$Credential,

        [string]$CertificateThumbprint,
        [switch]$EnableBasicAuth = $false,
        [switch]$EnableCredSSP,
        [switch]$LogToEventLog
    )

    Begin {
        # Define the configuration logic as a script block
        $ConfigurationScript = {
            [CmdletBinding()]
            Param (
                $CertificateThumbprint,
                $EnableBasicAuth,
                $EnableCredSSP,
                $LogToEventLog
            )

            # --- Embedded Private Functions ---

            function Get-GDSServerAuthCertificates {
                [CmdletBinding()]
                Param(
                    [string]$ComputerName = $env:COMPUTERNAME
                )

                Write-Verbose "Scanning for Server Authentication certificates for host: $ComputerName"
                $certs = Get-ChildItem Cert:\LocalMachine\My
                $candidates = $certs | Where-Object {
                    $_.Subject -like "*$ComputerName*" -and
                    $_.NotAfter -gt (Get-Date) -and
                    ($_.EnhancedKeyUsageList.FriendlyName -eq "Server Authentication" -or
                    ($_.Extensions | Where-Object { $_.Oid.Value -eq "1.3.6.1.5.5.7.3.1" }))
                }
                return $candidates
            }

            function Write-CandidateDetails {
                param($Certs)
                if ($Certs) {
                    Write-Verbose "Found $($Certs.Count) candidate certificate(s):"
                    foreach ($c in $Certs) {
                        Write-Verbose "  - Thumbprint: $($c.Thumbprint)"
                        Write-Verbose "    Subject:    $($c.Subject)"
                        Write-Verbose "    Issuer:     $($c.Issuer)"
                        Write-Verbose "    Expires:    $($c.NotAfter)"
                        Write-Verbose "    --------------------------------"
                    }
                }
                else {
                    Write-Verbose "No candidate certificates found matching criteria."
                }
            }

            function Select-GDSBestCertificate {
                [CmdletBinding()]
                Param(
                    [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
                    [System.Security.Cryptography.X509Certificates.X509Certificate2[]]$Certificates,

                    [Parameter(Mandatory = $true)]
                    [string]$SubjectName
                )

                if (-not $Certificates) { return $null }

                # 1. Sort by Expiration Date (Newest first)
                $sorted = $Certificates | Sort-Object NotAfter -Descending

                # 2. Try to find exact CN match first among sorted
                $exactMatch = $sorted | Where-Object { $_.Subject -eq "CN=$SubjectName" } | Select-Object -First 1

                if ($exactMatch) {
                    return $exactMatch
                }

                # 3. Fallback to best match (newest valid one)
                return $sorted | Select-Object -First 1
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
                Write-Host $Message
                Write-ProgressLog $Message
            }

            # Default SubjectName to the target machine's hostname if not specified
            # Default SubjectName to the target machine's hostname if not specified
            $SubjectName = $env:COMPUTERNAME

            $ErrorActionPreference = "Stop"

            try {
                Write-HostLog "Starting configuration for host: $env:COMPUTERNAME..."

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
                # --- Certificate Auto-Detection Logic ---
                if (-not $CertificateThumbprint) {
                    Write-Verbose "No certificate specified. Attempting to auto-detect a valid Server Authentication certificate..."


                    $candidates = Get-GDSServerAuthCertificates -ComputerName $env:COMPUTERNAME
                    Write-CandidateDetails -Certs $candidates

                    if ($candidates) {
                        $selectedCert = Select-GDSBestCertificate -Certificates $candidates -SubjectName $env:COMPUTERNAME

                        if ($selectedCert) {
                            $CertificateThumbprint = $selectedCert.Thumbprint

                            # Extract CN from certificate subject for listener hostname
                            # This ensures the listener hostname matches the certificate CN
                            if ($selectedCert.Subject -match 'CN=([^,]+)') {
                                $SubjectName = $matches[1]
                                Write-Verbose "Using certificate CN as hostname: $SubjectName"
                            }

                            Write-HostLog "Auto-detected valid certificate: $($selectedCert.Subject)"
                            Write-HostLog "Thumbprint: $CertificateThumbprint (Expires: $($selectedCert.NotAfter))"

                            if ($candidates.Count -gt 1) {
                                Write-Verbose "Multiple certificates found ($($candidates.Count)). Selected the newest/best match."
                            }
                        }
                    }

                    if (-not $CertificateThumbprint) {
                        throw "No valid 'Server Authentication' certificate found matching hostname '$env:COMPUTERNAME'. Please ensure a valid certificate exists or specify one using -CertificateThumbprint."
                    }
                }
                # ----------------------------------------
                # ----------------------------------------

                # Find and start the WinRM service.
                Write-Verbose "Verifying WinRM service."
                $winrmService = Get-Service "WinRM" -ErrorAction SilentlyContinue
                if (-not $winrmService) {
                    throw "Unable to find the WinRM service."
                }

                # Track if WinRM was already configured (for idempotent auth behavior)
                $winrmWasAlreadyRunning = ($winrmService.Status -eq "Running")

                if (-not $winrmWasAlreadyRunning) {
                    Write-HostLog "WinRM service is not running. Starting service..."
                    Write-Verbose "Setting WinRM service to start automatically on boot."
                    Set-Service -Name "WinRM" -StartupType Automatic
                    Write-Verbose "Starting WinRM service."
                    Start-Service -Name "WinRM" -ErrorAction Stop
                    Write-ProgressLog "Started WinRM service."
                }
                else {
                    Write-Verbose "WinRM service is already running."
                }

                # Make sure there is a SSL listener.
                $listeners = Get-ChildItem WSMan:\localhost\Listener
                if (-not ($listeners | Where-Object { $_.Keys -like "TRANSPORT=HTTPS" })) {

                    $valueset = @{
                        Hostname              = $SubjectName
                        CertificateThumbprint = $CertificateThumbprint
                    }

                    $selectorset = @{
                        Transport = "HTTPS"
                        Address   = "*"
                    }

                    Write-HostLog "HTTPS Listener not found. Creating listener on port 5986..."
                    Write-Verbose "Enabling SSL listener."
                    New-WSManInstance -ResourceURI 'winrm/config/Listener' -SelectorSet $selectorset -ValueSet $valueset
                    Write-ProgressLog "Enabled SSL listener."
                }
                else {
                    Write-Verbose "SSL listener is already active."
                }

                # Check for basic authentication.
                # Only enforce secure defaults if WinRM was not already running (fresh setup).
                # If WinRM was already configured, only change auth if explicitly requested.
                $basicAuthSetting = Get-ChildItem WSMan:\localhost\Service\Auth | Where-Object { $_.Name -eq "Basic" }

                if ($EnableBasicAuth) {
                    # Explicitly requested to enable Basic auth
                    if (($basicAuthSetting.Value) -eq $false) {
                        Write-Verbose "Enabling basic auth support."
                        Set-Item -Path "WSMan:\localhost\Service\Auth\Basic" -Value $true
                        Write-ProgressLog "Enabled basic auth support."
                    }
                    else {
                        Write-Verbose "Basic auth is already enabled."
                    }
                }
                elseif (-not $winrmWasAlreadyRunning) {
                    # Fresh WinRM setup: enforce secure default (disable Basic auth)
                    if (($basicAuthSetting.Value) -eq $true) {
                        Write-Verbose "Disabling basic auth support (Secure Default for fresh setup)."
                        Set-Item -Path "WSMan:\localhost\Service\Auth\Basic" -Value $false
                        Write-ProgressLog "Disabled basic auth support."
                    }
                    else {
                        Write-Verbose "Basic auth is already disabled."
                    }
                }
                else {
                    # WinRM was already running: leave existing auth settings alone (idempotent)
                    Write-Verbose "WinRM was already configured. Leaving Basic auth setting unchanged (current: $($basicAuthSetting.Value))."
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
                        Write-HostLog "Firewall rule 'Allow WinRM HTTPS' not found. Creating rule..."
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
                        Write-HostLog "Firewall rule 'Allow WinRM HTTPS' not found. Creating rule..."
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
                Write-HostLog "Configuration completed successfully for host: $env:COMPUTERNAME."

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
                & $ConfigurationScript -CertificateThumbprint $CertificateThumbprint `
                    -EnableBasicAuth:$EnableBasicAuth `
                    -EnableCredSSP:$EnableCredSSP `
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
                    $CertificateThumbprint,
                    $EnableBasicAuth,
                    $EnableCredSSP,
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

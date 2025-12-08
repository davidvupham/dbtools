function Set-GDSSqlServiceUserRights {
    <#
    .SYNOPSIS
        Sets the required Windows User Rights for a SQL Server Service Account.

    .DESCRIPTION
        This function is a specific wrapper around Set-GDSWindowsUserRight to configure the
        three critical privileges recommended for SQL Server service accounts:
        1. Log on as a service
        2. Perform volume maintenance tasks (IFI)
        3. Lock pages in memory

    .PARAMETER ServiceAccount
        The specific service account to configure. If not specified, the function attempts to retrieve
        the 'Log On As' account from the service specified by -ServiceName.

    .PARAMETER ServiceName
        The name of the SQL Server service to look up if ServiceAccount is not provided.
        Default is 'MSSQLSERVER'.

    .PARAMETER Ensure
        Specifies whether to grant ('Present') or revoke ('Absent') these rights. Default is 'Present'.

    .EXAMPLE
        Set-GDSSqlServiceUserRights -ServiceAccount 'CONTOSO\svc_sql'

        Grants rights to the explicitly provided account.

    .EXAMPLE
        Set-GDSSqlServiceUserRights

        Attempts to find the service 'MSSQLSERVER', gets its logon account, and grants rights to it.
        Useful for post-installation configuration.
    #>
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $false, Position = 0)]
        [string]$ServiceAccount,

        [Parameter(Mandatory = $false)]
        [string]$ServiceName = 'MSSQLSERVER',

        [Parameter()]
        [ValidateSet('Present', 'Absent')]
        [string]$Ensure = 'Present'
    )

    process {
        # Auto-detect identity if not provided
        if ([string]::IsNullOrWhiteSpace($ServiceAccount)) {
            Write-Verbose "No ServiceAccount specified. Attempting to detect service account for '$ServiceName'..."
            try {
                $service = Get-CimInstance -ClassName Win32_Service -Filter "Name = '$ServiceName'" -ErrorAction Stop

                if (-not $service) {
                    throw "Service '$ServiceName' not found."
                }

                $ServiceAccount = $service.StartName
                Write-Verbose "Detected service account for '$ServiceName': '$ServiceAccount'"
            }
            catch {
                throw "Failed to determine service account for '$ServiceName'. Is the service installed? Error: $_"
            }
        }

        if ([string]::IsNullOrWhiteSpace($ServiceAccount)) {
            throw "Resolved ServiceAccount is empty. Cannot apply rights."
        }

        $sqlRights = @(
            'Log on as a service',               # SeServiceLogonRight
            'Perform volume maintenance tasks',  # SeManageVolumePrivilege (IFI)
            'Lock pages in memory'               # SeLockMemoryPrivilege
        )

        try {
            Write-Verbose "Configuring SQL specific rights for account '$ServiceAccount'..."
            Set-GDSWindowsUserRight -UserRight $sqlRights -ServiceAccount $ServiceAccount -Ensure $Ensure

            if ($Ensure -eq 'Present') {
                Write-Verbose "Successfully granted all SQL Server service rights to '$ServiceAccount'."
            }
            else {
                Write-Verbose "Successfully revoked all SQL Server service rights from '$ServiceAccount'."
            }
        }
        catch {
            $errMsg = "Failed to configure SQL Server user rights for '$ServiceAccount': $_"
            Write-Error $errMsg
            throw $errMsg
        }
    }
}

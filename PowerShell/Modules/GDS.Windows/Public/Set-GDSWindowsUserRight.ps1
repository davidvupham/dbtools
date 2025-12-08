function Set-GDSWindowsUserRight {
    <#
    .SYNOPSIS
        Sets a specific User Right for a given account using DSC v3.

    .DESCRIPTION
        This function leverages the 'UserRightsAssignment' DSC resource from the PSDscResources module
        to grant or revoke user rights (privileges) to a specified identity (account) on Windows Server.

        This wrapper uses Invoke-DscResource to apply the setting directly without compiling a full configuration.

    .PARAMETER UserRight
        The constant name of the user right to configure (e.g., 'SeServiceLogonRight', 'SeLockMemoryPrivilege').

    .PARAMETER ServiceAccount
        The account to grant/revoke the right for (e.g., 'DOMAIN\ServiceAccount', 'NT SERVICE\MSSQLSERVER').

    .PARAMETER Ensure
        Specifies whether the right should be 'Present' (granted) or 'Absent' (revoked).
        Default is 'Present'.

    .EXAMPLE
        Set-GDSWindowsUserRight -UserRight 'Log on as a service' -ServiceAccount 'CONTOSO\svc_sql'

        Grants 'Log on as a service' to the account 'CONTOSO\svc_sql'.

    .EXAMPLE
        Set-GDSWindowsUserRight -UserRight 'Lock pages in memory' -ServiceAccount 'CONTOSO\svc_sql' -Ensure Absent

        Revokes 'Lock pages in memory' from the account 'CONTOSO\svc_sql'.

    .EXAMPLE
        Set-GDSWindowsUserRight -UserRight 'Log on as a service', 'Lock pages in memory' -ServiceAccount 'CONTOSO\svc_sql'

        Grants multiple rights ('Log on as a service' and 'Lock pages in memory') to the account.

    .EXAMPLE
        $rights = @('Log on as a service', 'Log on as a batch job')
        Set-GDSWindowsUserRight -UserRight $rights -ServiceAccount 'CONTOSO\svc_sql'

        Grants multiple rights specified in an array variable.
    #>
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true, Position = 0)]
        [ValidateNotNullOrEmpty()]
        [string[]]$UserRight,

        [Parameter(Mandatory = $true, Position = 1)]
        [ValidateNotNullOrEmpty()]
        [string]$ServiceAccount,

        [Parameter()]
        [ValidateSet('Present', 'Absent')]
        [string]$Ensure = 'Present'
    )

    process {
        # Ensure PSDscResources module is available
        if (-not (Get-Module -ListAvailable -Name PSDscResources)) {
            throw "The 'PSDscResources' module is required but not found. Please install it using 'Install-Module PSDscResources'."
        }

        # Mapping of friendly names to DSC expected policy names (usually matching secedit output format with underscores)
        $UserRightMapping = @{
            'Log on as a service'                           = 'Log_on_as_a_service'
            'Lock pages in memory'                          = 'Lock_pages_in_memory'
            'Perform volume maintenance tasks'              = 'Perform_volume_maintenance_tasks'
            'Log on as a batch job'                         = 'Log_on_as_a_batch_job'
            'Allow log on locally'                          = 'Allow_log_on_locally'
            'Deny log on locally'                           = 'Deny_log_on_locally'
            'Access this computer from the network'         = 'Access_this_computer_from_the_network'
            'Deny access to this computer from the network' = 'Deny_access_to_this_computer_from_the_network'
        }

        foreach ($right in $UserRight) {
            # Check if there is a mapping for the friendly name
            if ($UserRightMapping.ContainsKey($right)) {
                $policyName = $UserRightMapping[$right]
                Write-Verbose "Mapped friendly name '$right' to policy '$policyName'."
            }
            else {
                # Assume it's already in the correct format (e.g. SeServiceLogonRight or Log_on_as_a_service)
                $policyName = $right
            }

            $properties = @{
                Policy   = $policyName
                Identity = $ServiceAccount
                Ensure   = $Ensure
            }

            Write-Verbose "Invoking DSC resource UserRightsAssignment from PSDscResources..."
            Write-Verbose "Policy: $policyName"
            Write-Verbose "Identity: $ServiceAccount"
            Write-Verbose "Ensure: $Ensure"

            try {
                # Use Invoke-DscResource (DSC v3 / PS 7+ style invoke)
                # This requires running as Administrator
                $result = Invoke-DscResource -Name UserRightsAssignment -ModuleName PSDscResources -Method Set -Property $properties

                # If we get here without error, it succeeded.
                # We can optionally return the result or just be silent (verb based).
                # "Set" verb usually doesn't return output unless -PassThru is used, but Invoke-DscResource usually returns an object.

                Write-Verbose "Successfully applied user right configuration for $right ($policyName)."

                if ($result.InDesiredState -eq $false) {
                    Write-Warning "DSC Resource reported that it was not in the desired state for '$right' even after Set execution. Please verify."
                }
            }
            catch {
                throw "Failed to set user right '$right' for '$ServiceAccount': $_"
            }
        }
    }
}

function Set-GDSWindowsUserRight {
    <#
    .SYNOPSIS
        Sets a specific Windows User Right for a given account using DSC v3 principles with Carbon.

    .DESCRIPTION
        This function grants or revokes Windows User Rights (privileges) to a specified identity
        (account) on Windows Server.

        IMPLEMENTATION NOTES:
        ---------------------
        This function uses the Carbon PowerShell module (https://get-carbon.org) as its underlying
        implementation rather than the SecurityPolicyDsc DSC resource. This design decision was made
        because:

        1. SecurityPolicyDsc requires WinRM to be enabled and configured, even for local operations.
           This is a significant prerequisite that may not be acceptable in all environments.

        2. Carbon's Grant-CPrivilege and Revoke-CPrivilege functions are IDEMPOTENT - they can be
           called multiple times without error or side effects, matching DSC's desired state model.

        3. Carbon works in both PowerShell 5.1 and PowerShell 7 without WinRM dependencies.

        This function follows DSC v3 conventions and can be used as a DSC v3 resource adapter or
        called directly from Ansible, Terraform, or other IaC tools.

    .PARAMETER UserRight
        The user right to configure. Accepts either:
        - Friendly names: 'Log on as a service', 'Lock pages in memory'
        - Privilege constants: 'SeServiceLogonRight', 'SeLockMemoryPrivilege'

    .PARAMETER ServiceAccount
        The account to grant/revoke the right for (e.g., 'DOMAIN\ServiceAccount', 'NT SERVICE\MSSQLSERVER').

    .PARAMETER Ensure
        Specifies whether the right should be 'Present' (granted) or 'Absent' (revoked).
        Default is 'Present'.

    .EXAMPLE
        Set-GDSWindowsUserRight -UserRight 'Log on as a service' -ServiceAccount 'CONTOSO\svc_sql'

        Grants 'Log on as a service' to the account 'CONTOSO\svc_sql'. This operation is idempotent.

    .EXAMPLE
        Set-GDSWindowsUserRight -UserRight 'Lock pages in memory' -ServiceAccount 'CONTOSO\svc_sql' -Ensure Absent

        Revokes 'Lock pages in memory' from the account 'CONTOSO\svc_sql'.

    .EXAMPLE
        Set-GDSWindowsUserRight -UserRight 'Log on as a service', 'Lock pages in memory' -ServiceAccount 'CONTOSO\svc_sql'

        Grants multiple rights. Each operation is idempotent.

    .EXAMPLE
        $rights = @('Log on as a service', 'Log on as a batch job')
        Set-GDSWindowsUserRight -UserRight $rights -ServiceAccount 'CONTOSO\svc_sql'

        Grants multiple rights specified in an array variable.

    .NOTES
        IDEMPOTENCY: This function is idempotent. Running it multiple times with the same parameters
        will not cause errors or unintended changes. If the right is already granted/revoked, no
        action is taken.

        DEPENDENCIES: Requires the Carbon PowerShell module.
        Install with: Install-Module -Name Carbon -Force -Scope CurrentUser

        PERMISSIONS: Requires Administrator privileges to modify User Rights.

    .LINK
        https://get-carbon.org
        https://get-carbon.org/Grant-CPrivilege.html
        https://get-carbon.org/Revoke-CPrivilege.html
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
        # Ensure Carbon module is available
        if (-not (Get-Module -ListAvailable -Name Carbon)) {
            throw "The 'Carbon' module is required but not found. Please install it using 'Install-Module Carbon -Force -Scope CurrentUser'."
        }

        # Import Carbon if not already imported
        if (-not (Get-Module -Name Carbon)) {
            Import-Module Carbon -ErrorAction Stop
        }

        # Mapping of friendly names to privilege constants (Se* format)
        $UserRightMapping = @{
            'Log on as a service'                           = 'SeServiceLogonRight'
            'Lock pages in memory'                          = 'SeLockMemoryPrivilege'
            'Perform volume maintenance tasks'              = 'SeManageVolumePrivilege'
            'Log on as a batch job'                         = 'SeBatchLogonRight'
            'Allow log on locally'                          = 'SeInteractiveLogonRight'
            'Deny log on locally'                           = 'SeDenyInteractiveLogonRight'
            'Access this computer from the network'         = 'SeNetworkLogonRight'
            'Deny access to this computer from the network' = 'SeDenyNetworkLogonRight'
        }

        foreach ($right in $UserRight) {
            # Map friendly name to privilege constant if needed
            if ($UserRightMapping.ContainsKey($right)) {
                $privilegeName = $UserRightMapping[$right]
                Write-Verbose "Mapped friendly name '$right' to privilege '$privilegeName'."
            }
            else {
                # Assume it's already a privilege constant (e.g., SeServiceLogonRight)
                $privilegeName = $right
            }

            Write-Verbose "Processing privilege '$privilegeName' for account '$ServiceAccount' (Ensure: $Ensure)."

            try {
                if ($Ensure -eq 'Present') {
                    # Grant the privilege (idempotent - no error if already granted)
                    Write-Verbose "Granting '$privilegeName' to '$ServiceAccount'..."
                    Grant-CPrivilege -Identity $ServiceAccount -Privilege $privilegeName

                    Write-Verbose "Successfully ensured '$right' ($privilegeName) is granted to '$ServiceAccount'."
                }
                else {
                    # Revoke the privilege (idempotent - no error if not present)
                    Write-Verbose "Revoking '$privilegeName' from '$ServiceAccount'..."
                    Revoke-CPrivilege -Identity $ServiceAccount -Privilege $privilegeName

                    Write-Verbose "Successfully ensured '$right' ($privilegeName) is revoked from '$ServiceAccount'."
                }
            }
            catch {
                throw "Failed to set user right '$right' ($privilegeName) for '$ServiceAccount': $_"
            }
        }
    }
}

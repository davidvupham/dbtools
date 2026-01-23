function Get-GdsUserGroupMembership {
    <#
    .SYNOPSIS
        Lists security groups a user is a member of.

    .DESCRIPTION
        Retrieves the security groups for a specified user, with optional name filtering.
        Outputs ADGroup objects which can be piped to other commands.

    .PARAMETER UserName
        The SAM account name of the user.

    .PARAMETER Filter
        Wildcard filter for group names (e.g., 'SQL*'). Default is '*'.
        Only returns groups where the Name matches this filter.

    .EXAMPLE
        Get-GdsUserGroupMembership -UserName "jdoe"
        Lists all security groups for jdoe.

    .EXAMPLE
        Get-GdsUserGroupMembership -UserName "jdoe" -Filter "SQL*"
        Lists security groups for jdoe starting with "SQL".
    #>
    [CmdletBinding()]
    # OutputType: Microsoft.ActiveDirectory.Management.ADGroup (when ActiveDirectory module is available)
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [ValidateNotNullOrEmpty()]
        [string]$UserName,

        [Parameter(Mandatory = $false, Position = 1)]
        [string]$Filter = '*'
    )

    begin {
    }

    process {
        try {
            $groups = Get-ADPrincipalGroupMembership -Identity $UserName | Where-Object {
                $_.GroupCategory -eq 'Security' -and $_.Name -like $Filter
            }

            $groups
        }
        catch {
            Write-Error "Failed to retrieve groups for user '$UserName': $_"
        }
    }
}

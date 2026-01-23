function Remove-GdsUserGroupMembership {
    <#
    .SYNOPSIS
        Removes a specified user from one or more Active Directory security groups.

    .DESCRIPTION
        Removes the user from the specified security groups.
        This function accepts a list of groups via parameter or pipeline.

    .PARAMETER UserName
        The SAM account name of the user to remove from the groups.

    .PARAMETER Group
        The group(s) to remove the user from.
        Accepts strings (Group Names) or ADGroup objects (e.g., from Get-GdsUserGroupMembership).

    .EXAMPLE
        Remove-GdsUserGroupMembership -UserName "jdoe" -Group "SQLdb_Readers"
        Removes jdoe from SQLdb_Readers.

    .EXAMPLE
        Get-GdsUserGroupMembership -UserName "jdoe" -Filter "SQL*" | Remove-GdsUserGroupMembership -UserName "jdoe"
        Removes jdoe from all his groups starting with "SQL".
    #>
    [CmdletBinding(SupportsShouldProcess)]
    [OutputType([void])]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string]$UserName,

        [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
        [ValidateNotNullOrEmpty()]
        [object[]]$Group
    )

    process {
        foreach ($item in $Group) {
            # Resolve Group Name if it's an ADObject
            if ($item -is [string]) {
                $groupName = $item
            }
            elseif ($item.PSObject.Properties['Name']) {
                $groupName = $item.Name
            }
            else {
                $groupName = $item.ToString()
            }

            if ($PSCmdlet.ShouldProcess("Group: $groupName", "Remove User: $UserName")) {
                try {
                    # Confirm:$false because ShouldProcess already handled the confirmation check (or -WhatIf)
                    Remove-ADGroupMember -Identity $groupName -Members $UserName -Confirm:$false -ErrorAction Stop
                    Write-Verbose "Successfully removed user '$UserName' from group '$groupName'."
                }
                catch {
                    Write-Error "Failed to remove user '$UserName' from group '$groupName': $_"
                }
            }
        }
    }
}

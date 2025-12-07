function Get-GDSUserRightPolicyState {
    <#
    .SYNOPSIS
        Determines if specific User Rights are managed by Group Policy.

    .DESCRIPTION
        This function uses 'gpresult' to generate an XML report of the applied policies on the computer.
        It then parses this report to check if the specified User Rights (Privileges) are defined in any GPO.

        This requires Administrative privileges to run 'gpresult /Scope Computer'.

    .PARAMETER UserRight
        One or more User Right constants (e.g., 'SeServiceLogonRight', 'SeLockMemoryPrivilege').
        Common rights:
        - SeServiceLogonRight (Log on as a service)
        - SeLockMemoryPrivilege (Lock pages in memory)
        - SeManageVolumePrivilege (Perform volume maintenance tasks)
        - SeBatchLogonRight (Log on as a batch job)
        - SeInteractiveLogonRight (Allow log on locally)
        - SeDenyInteractiveLogonRight (Deny log on locally)
        - SeNetworkLogonRight (Access this computer from the network)

    .EXAMPLE
        Get-GDSUserRightPolicyState -UserRight 'SeServiceLogonRight', 'SeLockMemoryPrivilege'

        Checks if 'Log on as a service' and 'Lock pages in memory' are managed by GPO.

    .EXAMPLE
        Get-GDSUserRightPolicyState -UserRight 'SeManageVolumePrivilege' | Format-Table

        Checks for 'Perform volume maintenance tasks' and displays the result in a table.
    #>
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true, Position = 0)]
        [ValidateNotNullOrEmpty()]
        [string[]]$UserRight
    )

    process {
        # Define a temporary file for the XML report
        $tempFile = [System.IO.Path]::GetTempFileName()

        try {
            Write-Verbose "Running gpresult to capture policy data to $tempFile..."

            # Run gpresult. This requires elevation.
            # We redirect stderr to null to avoid clutter if it fails, but capture exit code.
            $process = Start-Process -FilePath "gpresult.exe" -ArgumentList "/Scope Computer /X `"$tempFile`" /F" -Wait -NoNewWindow -PassThru

            if ($process.ExitCode -ne 0) {
                throw "gpresult failed with exit code $($process.ExitCode). Ensure you are running as Administrator."
            }

            if (-not (Test-Path -Path $tempFile)) {
                throw "gpresult failed to generate the report file at $tempFile."
            }

            Write-Verbose "Parsing XML report..."
            [xml]$xml = Get-Content -Path $tempFile -Raw

            # Navigate to the Security Extension section
            # Path usually: /Rsop/ComputerResults/ExtensionData[Name="Security"]/Extension/...
            # But structure can vary slightly depending on schema versions. Using simpler xpath or traversal.

            # The XML structure for Security usually contains 'UserRightsAssignment'
            $securityContext = $xml.Rsop.ComputerResults.ExtensionData | Where-Object { $_.Name -eq "Security" }

            if (-not $securityContext) {
                Write-Warning "No Security extension data found in GPO report. User Rights may not be configured by GPO."
            }

            # User Rights are typically under $securityContext.Extension.UserRightsAssignment
            # It might be an array of checks.
            $definedRights = $securityContext.Extension.UserRightsAssignment

            foreach ($right in $UserRight) {
                $status = [PSCustomObject]@{
                    UserRight      = $right
                    IsManagedByGPO = $false
                    SourceGPO      = $null
                    Accounts       = $null
                }

                if ($definedRights) {
                    # $definedRights might be a single object or array. userRightsAssignment item has 'Name' (the Se* constant) and 'Member' (list of SIDs/Names)
                    # We also need to find WHERE it came from.
                    # In gpresult XML, the precedence is often shown or just the winning GPO.
                    # Actually, gpresult /X usually shows the winning value.
                    # Finding the Source GPO involves looking up the GPO Identifier usually, but typically gpresult /H (HTML) is better for humans, /X is raw data.
                    #
                    # Refinement: standard gpresult /X output usually has:
                    # <ExtensionData>
                    #   <Extension>
                    #     <UserRightsAssignment>
                    #       <Name>SeServiceLogonRight</Name>
                    #       <Member>...</Member>
                    #     </UserRightsAssignment>
                    #   </Extension>
                    #   <Name>Security</Name>
                    # </ExtensionData>
                    #
                    # Wait, gpresult /X does NOT explicitly list the Source GPO for each security setting in a simple way like it does for Registry keys sometimes.
                    # However, RSOP data implies it comes from *some* GPO if it is present here.
                    # If it is NOT present here, it is not being managed/forced by GPO (or at least not winning).

                    $foundRight = $definedRights | Where-Object { $_.Name -eq $right }

                    if ($foundRight) {
                        $status.IsManagedByGPO = $true
                        # Extract members if meaningful
                        if ($foundRight.Member) {
                            $status.Accounts = ($foundRight.Member | Out-String).Trim()
                        }

                        # Trying to deduce Source GPO is harder with just /X for Security.
                        # Usually, if it's in RSOP Computer Scope Security, it IS managed.
                        # To find the specific GPO Name, we might need to parse `Rsop.ComputerResults.Gpo` list and correlate,
                        # but the simple XML structure doesn't always perform a direct link per-setting for Security sections easily.
                        # For the user's request "find out if ... is managed by GPO", simply finding it in RSOP is sufficient to say "Yes".
                        $status.SourceGPO = "Managed (See gpresult /H for specific GPO name)"
                    }
                }

                Write-Output $status
            }

        }
        catch {
            Write-Error "Error retrieving GPO policy state: $_"
        }
        finally {
            if (Test-Path -Path $tempFile) {
                Remove-Item -Path $tempFile -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

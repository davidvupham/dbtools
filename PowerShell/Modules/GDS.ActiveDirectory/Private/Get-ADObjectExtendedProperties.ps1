<#
.SYNOPSIS
    Extracts all properties from an AD object and returns them as a JSON string.

.DESCRIPTION
    This function captures all properties from an AD object, excluding those that are
    already stored in dedicated columns, and returns them as JSON for storage in
    the ExtendedProperties column.

.PARAMETER ADObject
    The AD object (ADUser, ADGroup, etc.) to extract properties from.

.PARAMETER ExcludedProperties
    Array of property names to exclude from extended properties (already stored in dedicated columns).

.EXAMPLE
    $extendedProps = Get-ADObjectExtendedProperties -ADObject $user

.NOTES
    This function is part of the GDS.ActiveDirectory module.
#>
function Get-ADObjectExtendedProperties {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [PSObject]$ADObject,

        [Parameter(Mandatory = $false)]
        [string[]]$ExcludedProperties = @(
            'SamAccountName', 'DistinguishedName', 'DisplayName', 'GivenName', 'Surname',
            'EmailAddress', 'UserPrincipalName', 'Enabled', 'LastLogonDate', 'PasswordLastSet',
            'Created', 'Modified', 'SID', 'Description', 'Department', 'Title', 'Manager',
            'Office', 'PhoneNumber', 'MobilePhone', 'Name', 'GroupCategory', 'GroupScope',
            'ObjectClass', 'ObjectGUID', 'PropertyNames', 'PSComputerName', 'PSSite',
            'PSShowComputerName', 'RunspaceId', 'PSRemotingProtocolVersion'
        )
    )

    try {
        $extendedProps = @{}

        # Get all properties from the object
        $allProperties = $ADObject.PSObject.Properties

        foreach ($prop in $allProperties) {
            $propName = $prop.Name

            # Skip excluded properties
            if ($ExcludedProperties -contains $propName) {
                continue
            }

            # Skip null or empty values
            if ($null -eq $prop.Value) {
                continue
            }

            # Handle different property types
            $value = $prop.Value

            # Convert complex objects to strings or simple types
            if ($value -is [System.Security.Principal.SecurityIdentifier]) {
                $value = $value.Value
            }
            elseif ($value -is [System.Guid]) {
                $value = $value.ToString()
            }
            elseif ($value -is [DateTime]) {
                $value = $value.ToString('o')  # ISO 8601 format
            }
            elseif ($value -is [System.Array] -or $value -is [System.Collections.ArrayList]) {
                # Convert arrays to string arrays
                $value = @($value | ForEach-Object {
                    if ($_ -is [PSObject]) {
                        $_.ToString()
                    }
                    else {
                        $_
                    }
                })
            }
            elseif ($value -is [PSObject] -and $value.PSObject.TypeNames -contains 'Microsoft.ActiveDirectory.Management.ADPropertyValueCollection') {
                # Handle AD property value collections
                $value = @($value | ForEach-Object { $_.ToString() })
            }
            elseif ($value -is [Hashtable] -or $value -is [PSCustomObject]) {
                # Convert complex objects to hashtable
                $value = $value | ConvertTo-Json -Compress -Depth 3
            }

            # Store the property
            $extendedProps[$propName] = $value
        }

        # Convert to JSON
        if ($extendedProps.Count -gt 0) {
            return ($extendedProps | ConvertTo-Json -Compress -Depth 10)
        }
        else {
            return $null
        }
    }
    catch {
        Write-Log -Message "Error extracting extended properties" -Level Warning -Exception $_.Exception -Context @{
            ObjectType = $ADObject.GetType().Name
            DistinguishedName = $ADObject.DistinguishedName
        }
        return $null
    }
}

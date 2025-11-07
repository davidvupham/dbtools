<#
.SYNOPSIS
    Writes Active Directory user objects to the database.

.DESCRIPTION
    This function takes ADUser objects and writes them to the ADUsers table in the database.
    It handles both INSERT and UPDATE operations based on whether the user already exists.

.PARAMETER Connection
    The SqlConnection object to use for database operations.

.PARAMETER ADUser
    The ADUser object(s) to write to the database.

.PARAMETER SchemaName
    The database schema name. Defaults to 'dbo'.

.PARAMETER UpdateMode
    'Full' to replace all data, 'Incremental' to update only. Default is 'Incremental'.

.EXAMPLE
    $users = Get-ADUser -Filter *
    Write-ADUserToDatabase -Connection $conn -ADUser $users

.NOTES
    This function is part of the GDS.ActiveDirectory module.
#>
function Write-ADUserToDatabase {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [System.Data.SqlClient.SqlConnection]$Connection,

        [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
        [Microsoft.ActiveDirectory.Management.ADUser[]]$ADUser,

        [Parameter(Mandatory = $false)]
        [string]$SchemaName = 'dbo',

        [Parameter(Mandatory = $false)]
        [ValidateSet('Full', 'Incremental')]
        [string]$UpdateMode = 'Incremental'
    )

    begin {
        $stats = @{
            Inserted = 0
            Updated = 0
            Errors = @()
        }

        Write-Log -Message "Initializing ADUser database write operation" -Level Info -Context @{
            SchemaName = $SchemaName
            UpdateMode = $UpdateMode
        }

        # Prepare MERGE statement for upsert operation
        $mergeQuery = @"
MERGE [$SchemaName].[ADUsers] AS target
USING (SELECT @SamAccountName, @DistinguishedName, @DisplayName, @GivenName, @Surname,
              @EmailAddress, @UserPrincipalName, @Enabled, @LastLogonDate, @PasswordLastSet,
              @Created, @Modified, @SID, @Description, @Department, @Title, @Manager,
              @Office, @PhoneNumber, @MobilePhone, @ExtendedProperties, @SyncAction) AS source
    (SamAccountName, DistinguishedName, DisplayName, GivenName, Surname, EmailAddress,
     UserPrincipalName, Enabled, LastLogonDate, PasswordLastSet, Created, Modified, SID,
     Description, Department, Title, Manager, Office, PhoneNumber, MobilePhone, ExtendedProperties, SyncAction)
ON target.SamAccountName = source.SamAccountName
WHEN MATCHED THEN
    UPDATE SET
        DistinguishedName = source.DistinguishedName,
        DisplayName = source.DisplayName,
        GivenName = source.GivenName,
        Surname = source.Surname,
        EmailAddress = source.EmailAddress,
        UserPrincipalName = source.UserPrincipalName,
        Enabled = source.Enabled,
        LastLogonDate = source.LastLogonDate,
        PasswordLastSet = source.PasswordLastSet,
        Created = source.Created,
        Modified = source.Modified,
        SID = source.SID,
        Description = source.Description,
        Department = source.Department,
        Title = source.Title,
        Manager = source.Manager,
        Office = source.Office,
        PhoneNumber = source.PhoneNumber,
        MobilePhone = source.MobilePhone,
        ExtendedProperties = source.ExtendedProperties,
        SyncDate = GETUTCDATE(),
        SyncAction = source.SyncAction
WHEN NOT MATCHED THEN
    INSERT (SamAccountName, DistinguishedName, DisplayName, GivenName, Surname, EmailAddress,
            UserPrincipalName, Enabled, LastLogonDate, PasswordLastSet, Created, Modified, SID,
            Description, Department, Title, Manager, Office, PhoneNumber, MobilePhone, ExtendedProperties, SyncAction)
    VALUES (source.SamAccountName, source.DistinguishedName, source.DisplayName, source.GivenName,
            source.Surname, source.EmailAddress, source.UserPrincipalName, source.Enabled,
            source.LastLogonDate, source.PasswordLastSet, source.Created, source.Modified,
            source.SID, source.Description, source.Department, source.Title, source.Manager,
            source.Office, source.PhoneNumber, source.MobilePhone, source.ExtendedProperties, source.SyncAction);
"@

        $mergeCommand = New-Object System.Data.SqlClient.SqlCommand($mergeQuery, $Connection)

        # Add parameters
        $mergeCommand.Parameters.Add('@SamAccountName', [System.Data.SqlDbType]::NVarChar, 255) | Out-Null
        $mergeCommand.Parameters.Add('@DistinguishedName', [System.Data.SqlDbType]::NVarChar, 500) | Out-Null
        $mergeCommand.Parameters.Add('@DisplayName', [System.Data.SqlDbType]::NVarChar, 500) | Out-Null
        $mergeCommand.Parameters.Add('@GivenName', [System.Data.SqlDbType]::NVarChar, 255) | Out-Null
        $mergeCommand.Parameters.Add('@Surname', [System.Data.SqlDbType]::NVarChar, 255) | Out-Null
        $mergeCommand.Parameters.Add('@EmailAddress', [System.Data.SqlDbType]::NVarChar, 255) | Out-Null
        $mergeCommand.Parameters.Add('@UserPrincipalName', [System.Data.SqlDbType]::NVarChar, 255) | Out-Null
        $mergeCommand.Parameters.Add('@Enabled', [System.Data.SqlDbType]::Bit) | Out-Null
        $mergeCommand.Parameters.Add('@LastLogonDate', [System.Data.SqlDbType]::DateTime2) | Out-Null
        $mergeCommand.Parameters.Add('@PasswordLastSet', [System.Data.SqlDbType]::DateTime2) | Out-Null
        $mergeCommand.Parameters.Add('@Created', [System.Data.SqlDbType]::DateTime2) | Out-Null
        $mergeCommand.Parameters.Add('@Modified', [System.Data.SqlDbType]::DateTime2) | Out-Null
        $mergeCommand.Parameters.Add('@SID', [System.Data.SqlDbType]::NVarChar, 255) | Out-Null
        $mergeCommand.Parameters.Add('@Description', [System.Data.SqlDbType]::NVarChar, -1) | Out-Null
        $mergeCommand.Parameters.Add('@Department', [System.Data.SqlDbType]::NVarChar, 255) | Out-Null
        $mergeCommand.Parameters.Add('@Title', [System.Data.SqlDbType]::NVarChar, 255) | Out-Null
        $mergeCommand.Parameters.Add('@Manager', [System.Data.SqlDbType]::NVarChar, 500) | Out-Null
        $mergeCommand.Parameters.Add('@Office', [System.Data.SqlDbType]::NVarChar, 255) | Out-Null
        $mergeCommand.Parameters.Add('@PhoneNumber', [System.Data.SqlDbType]::NVarChar, 50) | Out-Null
        $mergeCommand.Parameters.Add('@MobilePhone', [System.Data.SqlDbType]::NVarChar, 50) | Out-Null
        $mergeCommand.Parameters.Add('@ExtendedProperties', [System.Data.SqlDbType]::NVarChar, -1) | Out-Null
        $mergeCommand.Parameters.Add('@SyncAction', [System.Data.SqlDbType]::NVarChar, 50) | Out-Null
    }

    process {
        foreach ($user in $ADUser) {
            $startTime = Get-Date
            try {
                Write-Log -Message "Processing ADUser" -Level Debug -Context @{
                    SamAccountName = $user.SamAccountName
                    DistinguishedName = $user.DistinguishedName
                }

                # Helper function to convert DateTime to DBNull if null
                function Get-DateTimeOrNull {
                    param($date)
                    if ($date -and $date -is [DateTime]) {
                        return $date
                    }
                    return [DBNull]::Value
                }

                # Helper function to get string or null
                function Get-StringOrNull {
                    param($value)
                    if ([string]::IsNullOrWhiteSpace($value)) {
                        return [DBNull]::Value
                    }
                    return $value
                }

                # Extract extended properties (all properties not in dedicated columns)
                $extendedProperties = Get-ADObjectExtendedProperties -ADObject $user
                if ($extendedProperties) {
                    Write-Log -Message "Extracted extended properties" -Level Debug -Context @{
                        SamAccountName = $user.SamAccountName
                        ExtendedPropertiesLength = $extendedProperties.Length
                    }
                }

                # Set parameter values
                $mergeCommand.Parameters['@SamAccountName'].Value = $user.SamAccountName
                $mergeCommand.Parameters['@DistinguishedName'].Value = $user.DistinguishedName
                $mergeCommand.Parameters['@DisplayName'].Value = Get-StringOrNull -value $user.DisplayName
                $mergeCommand.Parameters['@GivenName'].Value = Get-StringOrNull -value $user.GivenName
                $mergeCommand.Parameters['@Surname'].Value = Get-StringOrNull -value $user.Surname
                $mergeCommand.Parameters['@EmailAddress'].Value = Get-StringOrNull -value $user.EmailAddress
                $mergeCommand.Parameters['@UserPrincipalName'].Value = Get-StringOrNull -value $user.UserPrincipalName
                $mergeCommand.Parameters['@Enabled'].Value = if ($user.Enabled -ne $null) { [bool]$user.Enabled } else { [DBNull]::Value }
                $mergeCommand.Parameters['@LastLogonDate'].Value = Get-DateTimeOrNull -date $user.LastLogonDate
                $mergeCommand.Parameters['@PasswordLastSet'].Value = Get-DateTimeOrNull -date $user.PasswordLastSet
                $mergeCommand.Parameters['@Created'].Value = Get-DateTimeOrNull -date $user.Created
                $mergeCommand.Parameters['@Modified'].Value = Get-DateTimeOrNull -date $user.Modified
                $mergeCommand.Parameters['@SID'].Value = Get-StringOrNull -value $user.SID.Value
                $mergeCommand.Parameters['@Description'].Value = Get-StringOrNull -value $user.Description
                $mergeCommand.Parameters['@Department'].Value = Get-StringOrNull -value $user.Department
                $mergeCommand.Parameters['@Title'].Value = Get-StringOrNull -value $user.Title
                $mergeCommand.Parameters['@Manager'].Value = Get-StringOrNull -value $user.Manager
                $mergeCommand.Parameters['@Office'].Value = Get-StringOrNull -value $user.Office
                $mergeCommand.Parameters['@PhoneNumber'].Value = Get-StringOrNull -value $user.PhoneNumber
                $mergeCommand.Parameters['@MobilePhone'].Value = Get-StringOrNull -value $user.MobilePhone
                $mergeCommand.Parameters['@ExtendedProperties'].Value = Get-StringOrNull -value $extendedProperties
                $mergeCommand.Parameters['@SyncAction'].Value = 'UPDATE'

                # Check if this is an insert or update
                $checkQuery = "SELECT COUNT(*) FROM [$SchemaName].[ADUsers] WHERE SamAccountName = @SamAccountName"
                $checkCmd = New-Object System.Data.SqlClient.SqlCommand($checkQuery, $Connection)
                $checkCmd.Parameters.Add('@SamAccountName', [System.Data.SqlDbType]::NVarChar, 255).Value = $user.SamAccountName
                $exists = ($checkCmd.ExecuteScalar() -gt 0)

                # Execute merge
                $rowsAffected = $mergeCommand.ExecuteNonQuery()

                $duration = (Get-Date) - $startTime
                $action = if ($exists) { 'Updated' } else { 'Inserted' }

                if ($exists) {
                    $stats.Updated++
                }
                else {
                    $stats.Inserted++
                }

                Write-Log -Message "Successfully processed ADUser" -Level Info -Context @{
                    SamAccountName = $user.SamAccountName
                    Action = $action
                    DurationMs = $duration.TotalMilliseconds
                    RowsAffected = $rowsAffected
                }
            }
            catch {
                $duration = (Get-Date) - $startTime
                $errorMsg = "Error processing user $($user.SamAccountName): $_"
                Write-Log -Message $errorMsg -Level Error -Exception $_.Exception -Context @{
                    SamAccountName = $user.SamAccountName
                    DistinguishedName = $user.DistinguishedName
                    DurationMs = $duration.TotalMilliseconds
                }
                $stats.Errors += $errorMsg
            }
        }
    }

    end {
        Write-Log -Message "ADUser database write operation completed" -Level Info -Context @{
            Inserted = $stats.Inserted
            Updated = $stats.Updated
            Errors = $stats.Errors.Count
        }
        return $stats
    }
}

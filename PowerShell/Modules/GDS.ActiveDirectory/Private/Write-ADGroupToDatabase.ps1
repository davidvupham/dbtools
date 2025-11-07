<#
.SYNOPSIS
    Writes Active Directory group objects to the database.

.DESCRIPTION
    This function takes ADGroup objects and writes them to the ADGroups table in the database.
    It also handles group membership relationships and writes them to ADGroupMembers table.

.PARAMETER Connection
    The SqlConnection object to use for database operations.

.PARAMETER ADGroup
    The ADGroup object(s) to write to the database.

.PARAMETER SchemaName
    The database schema name. Defaults to 'dbo'.

.PARAMETER UpdateMode
    'Full' to replace all data, 'Incremental' to update only. Default is 'Incremental'.

.EXAMPLE
    $groups = Get-ADGroup -Filter *
    Write-ADGroupToDatabase -Connection $conn -ADGroup $groups

.NOTES
    This function is part of the GDS.ActiveDirectory module.
#>
function Write-ADGroupToDatabase {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [System.Data.SqlClient.SqlConnection]$Connection,

        [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
        [Microsoft.ActiveDirectory.Management.ADGroup[]]$ADGroup,

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

        Write-Log -Message "Initializing ADGroup database write operation" -Level Info -Context @{
            SchemaName = $SchemaName
            UpdateMode = $UpdateMode
        }

        # Prepare MERGE statement for upsert operation
        $mergeQuery = @"
MERGE [$SchemaName].[ADGroups] AS target
USING (SELECT @SamAccountName, @DistinguishedName, @DisplayName, @Name, @Description,
              @GroupCategory, @GroupScope, @SID, @Created, @Modified, @ExtendedProperties, @SyncAction) AS source
    (SamAccountName, DistinguishedName, DisplayName, Name, Description, GroupCategory,
     GroupScope, SID, Created, Modified, ExtendedProperties, SyncAction)
ON target.SamAccountName = source.SamAccountName
WHEN MATCHED THEN
    UPDATE SET
        DistinguishedName = source.DistinguishedName,
        DisplayName = source.DisplayName,
        Name = source.Name,
        Description = source.Description,
        GroupCategory = source.GroupCategory,
        GroupScope = source.GroupScope,
        SID = source.SID,
        Created = source.Created,
        Modified = source.Modified,
        ExtendedProperties = source.ExtendedProperties,
        SyncDate = GETUTCDATE(),
        SyncAction = source.SyncAction
WHEN NOT MATCHED THEN
    INSERT (SamAccountName, DistinguishedName, DisplayName, Name, Description, GroupCategory,
            GroupScope, SID, Created, Modified, ExtendedProperties, SyncAction)
    VALUES (source.SamAccountName, source.DistinguishedName, source.DisplayName, source.Name,
            source.Description, source.GroupCategory, source.GroupScope, source.SID,
            source.Created, source.Modified, source.ExtendedProperties, source.SyncAction);
"@

        $mergeCommand = New-Object System.Data.SqlClient.SqlCommand($mergeQuery, $Connection)

        # Add parameters
        $mergeCommand.Parameters.Add('@SamAccountName', [System.Data.SqlDbType]::NVarChar, 255) | Out-Null
        $mergeCommand.Parameters.Add('@DistinguishedName', [System.Data.SqlDbType]::NVarChar, 500) | Out-Null
        $mergeCommand.Parameters.Add('@DisplayName', [System.Data.SqlDbType]::NVarChar, 500) | Out-Null
        $mergeCommand.Parameters.Add('@Name', [System.Data.SqlDbType]::NVarChar, 255) | Out-Null
        $mergeCommand.Parameters.Add('@Description', [System.Data.SqlDbType]::NVarChar, -1) | Out-Null
        $mergeCommand.Parameters.Add('@GroupCategory', [System.Data.SqlDbType]::NVarChar, 50) | Out-Null
        $mergeCommand.Parameters.Add('@GroupScope', [System.Data.SqlDbType]::NVarChar, 50) | Out-Null
        $mergeCommand.Parameters.Add('@SID', [System.Data.SqlDbType]::NVarChar, 255) | Out-Null
        $mergeCommand.Parameters.Add('@Created', [System.Data.SqlDbType]::DateTime2) | Out-Null
        $mergeCommand.Parameters.Add('@Modified', [System.Data.SqlDbType]::DateTime2) | Out-Null
        $mergeCommand.Parameters.Add('@ExtendedProperties', [System.Data.SqlDbType]::NVarChar, -1) | Out-Null
        $mergeCommand.Parameters.Add('@SyncAction', [System.Data.SqlDbType]::NVarChar, 50) | Out-Null

        # Prepare query to get group ID
        $getGroupIdQuery = "SELECT Id FROM [$SchemaName].[ADGroups] WHERE SamAccountName = @SamAccountName"
        $getGroupIdCommand = New-Object System.Data.SqlClient.SqlCommand($getGroupIdQuery, $Connection)
        $getGroupIdCommand.Parameters.Add('@SamAccountName', [System.Data.SqlDbType]::NVarChar, 255) | Out-Null

        # Prepare insert statement for group members
        $insertMemberQuery = @"
IF NOT EXISTS (SELECT 1 FROM [$SchemaName].[ADGroupMembers]
               WHERE GroupId = @GroupId AND MemberDistinguishedName = @MemberDistinguishedName)
BEGIN
    INSERT INTO [$SchemaName].[ADGroupMembers] (GroupId, MemberSamAccountName, MemberDistinguishedName, MemberType)
    VALUES (@GroupId, @MemberSamAccountName, @MemberDistinguishedName, @MemberType)
END
"@
        $insertMemberCommand = New-Object System.Data.SqlClient.SqlCommand($insertMemberQuery, $Connection)
        $insertMemberCommand.Parameters.Add('@GroupId', [System.Data.SqlDbType]::Int) | Out-Null
        $insertMemberCommand.Parameters.Add('@MemberSamAccountName', [System.Data.SqlDbType]::NVarChar, 255) | Out-Null
        $insertMemberCommand.Parameters.Add('@MemberDistinguishedName', [System.Data.SqlDbType]::NVarChar, 500) | Out-Null
        $insertMemberCommand.Parameters.Add('@MemberType', [System.Data.SqlDbType]::NVarChar, 50) | Out-Null
    }

    process {
        foreach ($group in $ADGroup) {
            $startTime = Get-Date
            try {
                Write-Log -Message "Processing ADGroup" -Level Debug -Context @{
                    SamAccountName = $group.SamAccountName
                    DistinguishedName = $group.DistinguishedName
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
                $extendedProperties = Get-ADObjectExtendedProperties -ADObject $group
                if ($extendedProperties) {
                    Write-Log -Message "Extracted extended properties" -Level Debug -Context @{
                        SamAccountName = $group.SamAccountName
                        ExtendedPropertiesLength = $extendedProperties.Length
                    }
                }

                # Set parameter values for group
                $mergeCommand.Parameters['@SamAccountName'].Value = $group.SamAccountName
                $mergeCommand.Parameters['@DistinguishedName'].Value = $group.DistinguishedName
                $mergeCommand.Parameters['@DisplayName'].Value = Get-StringOrNull -value $group.DisplayName
                $mergeCommand.Parameters['@Name'].Value = Get-StringOrNull -value $group.Name
                $mergeCommand.Parameters['@Description'].Value = Get-StringOrNull -value $group.Description
                $mergeCommand.Parameters['@GroupCategory'].Value = Get-StringOrNull -value $group.GroupCategory
                $mergeCommand.Parameters['@GroupScope'].Value = Get-StringOrNull -value $group.GroupScope
                $mergeCommand.Parameters['@SID'].Value = Get-StringOrNull -value $group.SID.Value
                $mergeCommand.Parameters['@Created'].Value = Get-DateTimeOrNull -date $group.Created
                $mergeCommand.Parameters['@Modified'].Value = Get-DateTimeOrNull -date $group.Modified
                $mergeCommand.Parameters['@ExtendedProperties'].Value = Get-StringOrNull -value $extendedProperties
                $mergeCommand.Parameters['@SyncAction'].Value = 'UPDATE'

                # Check if this is an insert or update
                $checkQuery = "SELECT COUNT(*) FROM [$SchemaName].[ADGroups] WHERE SamAccountName = @SamAccountName"
                $checkCmd = New-Object System.Data.SqlClient.SqlCommand($checkQuery, $Connection)
                $checkCmd.Parameters.Add('@SamAccountName', [System.Data.SqlDbType]::NVarChar, 255).Value = $group.SamAccountName
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

                # Get the group ID
                $getGroupIdCommand.Parameters['@SamAccountName'].Value = $group.SamAccountName
                $groupId = $getGroupIdCommand.ExecuteScalar()

                # If UpdateMode is Full, delete existing members first
                if ($UpdateMode -eq 'Full' -and $groupId) {
                    $deleteMembersQuery = "DELETE FROM [$SchemaName].[ADGroupMembers] WHERE GroupId = @GroupId"
                    $deleteMembersCmd = New-Object System.Data.SqlClient.SqlCommand($deleteMembersQuery, $Connection)
                    $deleteMembersCmd.Parameters.Add('@GroupId', [System.Data.SqlDbType]::Int).Value = $groupId
                    $membersDeleted = $deleteMembersCmd.ExecuteNonQuery()
                    Write-Log -Message "Deleted existing group members" -Level Debug -Context @{
                        GroupId = $groupId
                        MembersDeleted = $membersDeleted
                    }
                }

                # Get and process group members
                $membersProcessed = 0
                if ($groupId) {
                    try {
                        $members = Get-ADGroupMember -Identity $group.DistinguishedName -ErrorAction SilentlyContinue
                        Write-Log -Message "Retrieved group members" -Level Debug -Context @{
                            GroupId = $groupId
                            MemberCount = $members.Count
                        }

                        foreach ($member in $members) {
                            try {
                                $insertMemberCommand.Parameters['@GroupId'].Value = $groupId
                                $insertMemberCommand.Parameters['@MemberSamAccountName'].Value = Get-StringOrNull -value $member.SamAccountName
                                $insertMemberCommand.Parameters['@MemberDistinguishedName'].Value = $member.DistinguishedName
                                $insertMemberCommand.Parameters['@MemberType'].Value = Get-StringOrNull -value $member.objectClass
                                $insertMemberCommand.ExecuteNonQuery() | Out-Null
                                $membersProcessed++
                            }
                            catch {
                                Write-Log -Message "Error adding member to group" -Level Warning -Exception $_.Exception -Context @{
                                    GroupId = $groupId
                                    MemberDN = $member.DistinguishedName
                                }
                            }
                        }
                    }
                    catch {
                        Write-Log -Message "Error retrieving members for group" -Level Warning -Exception $_.Exception -Context @{
                            SamAccountName = $group.SamAccountName
                        }
                    }
                }

                Write-Log -Message "Successfully processed ADGroup" -Level Info -Context @{
                    SamAccountName = $group.SamAccountName
                    Action = $action
                    DurationMs = $duration.TotalMilliseconds
                    RowsAffected = $rowsAffected
                    MembersProcessed = $membersProcessed
                }
            }
            catch {
                $duration = (Get-Date) - $startTime
                $errorMsg = "Error processing group $($group.SamAccountName): $_"
                Write-Log -Message $errorMsg -Level Error -Exception $_.Exception -Context @{
                    SamAccountName = $group.SamAccountName
                    DistinguishedName = $group.DistinguishedName
                    DurationMs = $duration.TotalMilliseconds
                }
                $stats.Errors += $errorMsg
            }
        }
    }

    end {
        Write-Log -Message "ADGroup database write operation completed" -Level Info -Context @{
            Inserted = $stats.Inserted
            Updated = $stats.Updated
            Errors = $stats.Errors.Count
        }
        return $stats
    }
}

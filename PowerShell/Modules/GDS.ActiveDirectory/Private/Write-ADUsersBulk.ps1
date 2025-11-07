<#
.SYNOPSIS
    Writes Active Directory user objects to the database using bulk insert for optimal performance.

.DESCRIPTION
    This function uses SqlBulkCopy for efficient bulk insertion of ADUser objects.
    For updates, it uses a staging table approach with MERGE for optimal performance.

.PARAMETER Connection
    The SqlConnection object to use for database operations.

.PARAMETER ADUsers
    The ADUser object(s) to write to the database.

.PARAMETER SchemaName
    The database schema name. Defaults to 'dbo'.

.PARAMETER UpdateMode
    'Full' to replace all data, 'Incremental' to update only. Default is 'Incremental'.

.PARAMETER BatchSize
    Number of rows to process in each batch. Default is 5000.

.EXAMPLE
    $users = Get-ADUser -Filter * -Properties *
    Write-ADUsersBulk -Connection $conn -ADUsers $users

.NOTES
    This function is part of the GDS.ActiveDirectory module.
    Uses SqlBulkCopy for optimal performance with large datasets.
#>
function Write-ADUsersBulk {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [System.Data.SqlClient.SqlConnection]$Connection,

        [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
        [Microsoft.ActiveDirectory.Management.ADUser[]]$ADUsers,

        [Parameter(Mandatory = $false)]
        [string]$SchemaName = 'dbo',

        [Parameter(Mandatory = $false)]
        [ValidateSet('Full', 'Incremental')]
        [string]$UpdateMode = 'Incremental',

        [Parameter(Mandatory = $false)]
        [int]$BatchSize = 5000
    )

    begin {
        $stats = @{
            Inserted = 0
            Updated = 0
            Errors = @()
        }

        $allUsers = New-Object System.Collections.ArrayList
        $startTime = Get-Date

        Write-Log -Message "Initializing bulk ADUser database write operation" -Level Info -Context @{
            SchemaName = $SchemaName
            UpdateMode = $UpdateMode
            BatchSize = $BatchSize
        } -ModuleName "ActiveDirectory"
    }

    process {
        foreach ($user in $ADUsers) {
            [void]$allUsers.Add($user)
        }
    }

    end {
        if ($allUsers.Count -eq 0) {
            Write-Log -Message "No users to process" -Level Info -ModuleName "ActiveDirectory"
            return $stats
        }

        try {
            Write-Log -Message "Processing $($allUsers.Count) users in bulk mode" -Level Info -Context @{
                TotalUsers = $allUsers.Count
            } -ModuleName "ActiveDirectory"

            # Create staging table
            $stagingTableName = "#ADUsers_Staging_$([System.Guid]::NewGuid().ToString().Replace('-', ''))"
            $createStagingTableQuery = @"
CREATE TABLE $stagingTableName (
    [SamAccountName] NVARCHAR(255) NOT NULL,
    [DistinguishedName] NVARCHAR(500) NOT NULL,
    [DisplayName] NVARCHAR(500) NULL,
    [GivenName] NVARCHAR(255) NULL,
    [Surname] NVARCHAR(255) NULL,
    [EmailAddress] NVARCHAR(255) NULL,
    [UserPrincipalName] NVARCHAR(255) NULL,
    [Enabled] BIT NULL,
    [LastLogonDate] DATETIME2 NULL,
    [PasswordLastSet] DATETIME2 NULL,
    [Created] DATETIME2 NULL,
    [Modified] DATETIME2 NULL,
    [SID] NVARCHAR(255) NULL,
    [Description] NVARCHAR(MAX) NULL,
    [Department] NVARCHAR(255) NULL,
    [Title] NVARCHAR(255) NULL,
    [Manager] NVARCHAR(500) NULL,
    [Office] NVARCHAR(255) NULL,
    [PhoneNumber] NVARCHAR(50) NULL,
    [MobilePhone] NVARCHAR(50) NULL,
    [ExtendedProperties] NVARCHAR(MAX) NULL,
    [SyncAction] NVARCHAR(50) NULL
)
"@

            $createCmd = New-Object System.Data.SqlClient.SqlCommand($createStagingTableQuery, $Connection)
            $createCmd.ExecuteNonQuery() | Out-Null
            Write-Log -Message "Created staging table" -Level Debug -ModuleName "ActiveDirectory"

            # Prepare DataTable for bulk insert
            $dataTable = New-Object System.Data.DataTable
            $dataTable.Columns.Add('SamAccountName', [string]) | Out-Null
            $dataTable.Columns.Add('DistinguishedName', [string]) | Out-Null
            $dataTable.Columns.Add('DisplayName', [string]) | Out-Null
            $dataTable.Columns.Add('GivenName', [string]) | Out-Null
            $dataTable.Columns.Add('Surname', [string]) | Out-Null
            $dataTable.Columns.Add('EmailAddress', [string]) | Out-Null
            $dataTable.Columns.Add('UserPrincipalName', [string]) | Out-Null
            $dataTable.Columns.Add('Enabled', [bool]) | Out-Null
            $dataTable.Columns.Add('LastLogonDate', [DateTime]) | Out-Null
            $dataTable.Columns.Add('PasswordLastSet', [DateTime]) | Out-Null
            $dataTable.Columns.Add('Created', [DateTime]) | Out-Null
            $dataTable.Columns.Add('Modified', [DateTime]) | Out-Null
            $dataTable.Columns.Add('SID', [string]) | Out-Null
            $dataTable.Columns.Add('Description', [string]) | Out-Null
            $dataTable.Columns.Add('Department', [string]) | Out-Null
            $dataTable.Columns.Add('Title', [string]) | Out-Null
            $dataTable.Columns.Add('Manager', [string]) | Out-Null
            $dataTable.Columns.Add('Office', [string]) | Out-Null
            $dataTable.Columns.Add('PhoneNumber', [string]) | Out-Null
            $dataTable.Columns.Add('MobilePhone', [string]) | Out-Null
            $dataTable.Columns.Add('ExtendedProperties', [string]) | Out-Null
            $dataTable.Columns.Add('SyncAction', [string]) | Out-Null

            # Helper functions
            function Get-DateTimeOrNull {
                param($date)
                if ($date -and $date -is [DateTime]) {
                    return $date
                }
                return [DBNull]::Value
            }

            function Get-StringOrNull {
                param($value)
                if ([string]::IsNullOrWhiteSpace($value)) {
                    return [DBNull]::Value
                }
                return $value
            }

            # Populate DataTable
            $processedCount = 0
            foreach ($user in $allUsers) {
                try {
                    $extendedProperties = Get-ADObjectExtendedProperties -ADObject $user

                    $row = $dataTable.NewRow()
                    $row['SamAccountName'] = $user.SamAccountName
                    $row['DistinguishedName'] = $user.DistinguishedName
                    $row['DisplayName'] = Get-StringOrNull -value $user.DisplayName
                    $row['GivenName'] = Get-StringOrNull -value $user.GivenName
                    $row['Surname'] = Get-StringOrNull -value $user.Surname
                    $row['EmailAddress'] = Get-StringOrNull -value $user.EmailAddress
                    $row['UserPrincipalName'] = Get-StringOrNull -value $user.UserPrincipalName
                    $row['Enabled'] = if ($user.Enabled -ne $null) { [bool]$user.Enabled } else { [DBNull]::Value }
                    $row['LastLogonDate'] = Get-DateTimeOrNull -date $user.LastLogonDate
                    $row['PasswordLastSet'] = Get-DateTimeOrNull -date $user.PasswordLastSet
                    $row['Created'] = Get-DateTimeOrNull -date $user.Created
                    $row['Modified'] = Get-DateTimeOrNull -date $user.Modified
                    $row['SID'] = Get-StringOrNull -value $user.SID.Value
                    $row['Description'] = Get-StringOrNull -value $user.Description
                    $row['Department'] = Get-StringOrNull -value $user.Department
                    $row['Title'] = Get-StringOrNull -value $user.Title
                    $row['Manager'] = Get-StringOrNull -value $user.Manager
                    $row['Office'] = Get-StringOrNull -value $user.Office
                    $row['PhoneNumber'] = Get-StringOrNull -value $user.PhoneNumber
                    $row['MobilePhone'] = Get-StringOrNull -value $user.MobilePhone
                    $row['ExtendedProperties'] = Get-StringOrNull -value $extendedProperties
                    $row['SyncAction'] = 'UPDATE'

                    $dataTable.Rows.Add($row)
                    $processedCount++

                    if ($processedCount % 1000 -eq 0) {
                        Write-Log -Message "Prepared $processedCount users for bulk insert" -Level Debug -ModuleName "ActiveDirectory"
                    }
                }
                catch {
                    $errorMsg = "Error preparing user $($user.SamAccountName): $_"
                    Write-Log -Message $errorMsg -Level Warning -Exception $_.Exception -ModuleName "ActiveDirectory"
                    $stats.Errors += $errorMsg
                }
            }

            Write-Log -Message "Prepared $processedCount users, starting bulk insert" -Level Info -ModuleName "ActiveDirectory"

            # Perform bulk insert to staging table
            $bulkCopy = New-Object System.Data.SqlClient.SqlBulkCopy($Connection, [System.Data.SqlClient.SqlBulkCopyOptions]::TableLock, $null)
            $bulkCopy.DestinationTableName = $stagingTableName
            $bulkCopy.BatchSize = $BatchSize
            $bulkCopy.BulkCopyTimeout = 600  # 10 minutes
            $bulkCopy.WriteToServer($dataTable)

            Write-Log -Message "Bulk insert to staging table completed" -Level Info -Context @{
                RowsInserted = $processedCount
            } -ModuleName "ActiveDirectory"

            # MERGE from staging to target table
            $mergeQuery = @"
MERGE [$SchemaName].[ADUsers] AS target
USING $stagingTableName AS source
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

-- Get counts
SELECT
    SUM(CASE WHEN EXISTS (SELECT 1 FROM [$SchemaName].[ADUsers] WHERE SamAccountName = s.SamAccountName) THEN 1 ELSE 0 END) AS Updated,
    SUM(CASE WHEN NOT EXISTS (SELECT 1 FROM [$SchemaName].[ADUsers] WHERE SamAccountName = s.SamAccountName) THEN 1 ELSE 0 END) AS Inserted
FROM $stagingTableName s;
"@

            $mergeCmd = New-Object System.Data.SqlClient.SqlCommand($mergeQuery, $Connection)
            $result = $mergeCmd.ExecuteScalar()

            # Get actual counts
            $countQuery = @"
SELECT
    (SELECT COUNT(*) FROM $stagingTableName s WHERE EXISTS (SELECT 1 FROM [$SchemaName].[ADUsers] u WHERE u.SamAccountName = s.SamAccountName)) AS Updated,
    (SELECT COUNT(*) FROM $stagingTableName s WHERE NOT EXISTS (SELECT 1 FROM [$SchemaName].[ADUsers] u WHERE u.SamAccountName = s.SamAccountName)) AS Inserted
"@
            $countCmd = New-Object System.Data.SqlClient.SqlCommand($countQuery, $Connection)
            $reader = $countCmd.ExecuteReader()
            if ($reader.Read()) {
                $stats.Updated = $reader['Updated']
                $stats.Inserted = $reader['Inserted']
            }
            $reader.Close()

            # Clean up staging table
            $dropQuery = "DROP TABLE $stagingTableName"
            $dropCmd = New-Object System.Data.SqlClient.SqlCommand($dropQuery, $Connection)
            $dropCmd.ExecuteNonQuery() | Out-Null

            $duration = (Get-Date) - $startTime
            Write-Log -Message "Bulk ADUser database write operation completed" -Level Info -Context @{
                Inserted = $stats.Inserted
                Updated = $stats.Updated
                Errors = $stats.Errors.Count
                TotalDurationMs = $duration.TotalMilliseconds
                Throughput = [math]::Round($processedCount / $duration.TotalSeconds, 2)
            } -ModuleName "ActiveDirectory"
        }
        catch {
            Write-Log -Message "Error in bulk ADUser write operation" -Level Error -Exception $_.Exception -ModuleName "ActiveDirectory"
            throw
        }

        return $stats
    }
}

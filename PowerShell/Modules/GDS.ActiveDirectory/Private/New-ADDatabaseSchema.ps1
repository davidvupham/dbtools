<#
.SYNOPSIS
    Creates the database schema for storing Active Directory objects.

.DESCRIPTION
    This function creates the necessary tables, indexes, and constraints in a SQL Server database
    for storing Active Directory users, groups, and group memberships.

.PARAMETER Connection
    The SqlConnection object to use for database operations.

.PARAMETER SchemaName
    The database schema name to create tables in. Defaults to 'dbo'.

.EXAMPLE
    $conn = Get-DatabaseConnection -Server "SQLSERVER01" -Database "ADInventory"
    New-ADDatabaseSchema -Connection $conn

.NOTES
    This function is part of the GDS.ActiveDirectory module.
#>
function New-ADDatabaseSchema {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [System.Data.SqlClient.SqlConnection]$Connection,

        [Parameter(Mandatory = $false)]
        [string]$SchemaName = 'dbo'
    )

    $ErrorActionPreference = 'Stop'

    try {
        # Ensure schema exists
        $schemaCheckQuery = @"
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '$SchemaName')
BEGIN
    EXEC('CREATE SCHEMA [$SchemaName]')
END
"@

        $schemaCmd = New-Object System.Data.SqlClient.SqlCommand($schemaCheckQuery, $Connection)
        $schemaCmd.ExecuteNonQuery() | Out-Null
        Write-Log -Message "Schema '$SchemaName' verified/created" -Level Info -Context @{SchemaName = $SchemaName}

        # Create ADUsers table
        $createUsersTableQuery = @"
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[$SchemaName].[ADUsers]') AND type in (N'U'))
BEGIN
    CREATE TABLE [$SchemaName].[ADUsers] (
        [Id] INT IDENTITY(1,1) PRIMARY KEY,
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
        [SyncDate] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        [SyncAction] NVARCHAR(50) NULL,
        CONSTRAINT [UQ_ADUsers_SamAccountName] UNIQUE ([SamAccountName])
    )

    CREATE INDEX [IX_ADUsers_DistinguishedName] ON [$SchemaName].[ADUsers] ([DistinguishedName])
    CREATE INDEX [IX_ADUsers_EmailAddress] ON [$SchemaName].[ADUsers] ([EmailAddress])
    CREATE INDEX [IX_ADUsers_SyncDate] ON [$SchemaName].[ADUsers] ([SyncDate])

    PRINT 'Table [$SchemaName].[ADUsers] created successfully'
END
ELSE
BEGIN
    PRINT 'Table [$SchemaName].[ADUsers] already exists'
END
"@

        $usersCmd = New-Object System.Data.SqlClient.SqlCommand($createUsersTableQuery, $Connection)
        $usersCmd.ExecuteNonQuery() | Out-Null
        Write-Log -Message "ADUsers table verified/created" -Level Info

        # Create ADGroups table
        $createGroupsTableQuery = @"
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[$SchemaName].[ADGroups]') AND type in (N'U'))
BEGIN
    CREATE TABLE [$SchemaName].[ADGroups] (
        [Id] INT IDENTITY(1,1) PRIMARY KEY,
        [SamAccountName] NVARCHAR(255) NOT NULL,
        [DistinguishedName] NVARCHAR(500) NOT NULL,
        [DisplayName] NVARCHAR(500) NULL,
        [Name] NVARCHAR(255) NULL,
        [Description] NVARCHAR(MAX) NULL,
        [GroupCategory] NVARCHAR(50) NULL,
        [GroupScope] NVARCHAR(50) NULL,
        [SID] NVARCHAR(255) NULL,
        [Created] DATETIME2 NULL,
        [Modified] DATETIME2 NULL,
        [ExtendedProperties] NVARCHAR(MAX) NULL,
        [SyncDate] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        [SyncAction] NVARCHAR(50) NULL,
        CONSTRAINT [UQ_ADGroups_SamAccountName] UNIQUE ([SamAccountName])
    )

    CREATE INDEX [IX_ADGroups_DistinguishedName] ON [$SchemaName].[ADGroups] ([DistinguishedName])
    CREATE INDEX [IX_ADGroups_SyncDate] ON [$SchemaName].[ADGroups] ([SyncDate])

    PRINT 'Table [$SchemaName].[ADGroups] created successfully'
END
ELSE
BEGIN
    PRINT 'Table [$SchemaName].[ADGroups] already exists'
END
"@

        $groupsCmd = New-Object System.Data.SqlClient.SqlCommand($createGroupsTableQuery, $Connection)
        $groupsCmd.ExecuteNonQuery() | Out-Null
        Write-Log -Message "ADGroups table verified/created" -Level Info

        # Create ADGroupMembers table
        $createGroupMembersTableQuery = @"
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[$SchemaName].[ADGroupMembers]') AND type in (N'U'))
BEGIN
    CREATE TABLE [$SchemaName].[ADGroupMembers] (
        [GroupId] INT NOT NULL,
        [MemberSamAccountName] NVARCHAR(255) NULL,
        [MemberDistinguishedName] NVARCHAR(500) NOT NULL,
        [MemberType] NVARCHAR(50) NULL,
        [AddedDate] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT [PK_ADGroupMembers] PRIMARY KEY ([GroupId], [MemberDistinguishedName]),
        CONSTRAINT [FK_ADGroupMembers_GroupId] FOREIGN KEY ([GroupId])
            REFERENCES [$SchemaName].[ADGroups]([Id]) ON DELETE CASCADE
    )

    CREATE INDEX [IX_ADGroupMembers_MemberSamAccountName] ON [$SchemaName].[ADGroupMembers] ([MemberSamAccountName])
    CREATE INDEX [IX_ADGroupMembers_MemberDistinguishedName] ON [$SchemaName].[ADGroupMembers] ([MemberDistinguishedName])

    PRINT 'Table [$SchemaName].[ADGroupMembers] created successfully'
END
ELSE
BEGIN
    PRINT 'Table [$SchemaName].[ADGroupMembers] already exists'
END
"@

        $groupMembersCmd = New-Object System.Data.SqlClient.SqlCommand($createGroupMembersTableQuery, $Connection)
        $groupMembersCmd.ExecuteNonQuery() | Out-Null
        Write-Log -Message "ADGroupMembers table verified/created" -Level Info

        Write-Log -Message "Database schema creation completed successfully" -Level Info
        return $true
    }
    catch {
        Write-Log -Message "Failed to create database schema" -Level Error -Exception $_.Exception
        throw
    }
}

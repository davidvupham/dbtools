<#
.SYNOPSIS
    Exports Active Directory objects (Users and Groups) to a SQL Server database.

.DESCRIPTION
    This cmdlet retrieves Active Directory users and/or groups and stores them in a SQL Server database.
    It supports both full and incremental sync modes, and can create the database schema automatically.

.PARAMETER Server
    The SQL Server instance name (e.g., "SQLSERVER01" or "SQLSERVER01\INSTANCE").

.PARAMETER Database
    The name of the database to store the AD objects in.

.PARAMETER Credential
    Optional PSCredential object for SQL Server Authentication. If not provided, Windows Authentication is used.

.PARAMETER ObjectType
    Specifies which object types to export. Valid values are 'User', 'Group', or 'All'. Default is 'All'.

.PARAMETER Filter
    Optional LDAP filter string to limit which AD objects are retrieved (e.g., "Department -eq 'IT'").

.PARAMETER SearchBase
    Optional distinguished name of the OU to search from. If not specified, searches the entire domain.

.PARAMETER CreateSchema
    If specified, creates the database schema (tables, indexes) if they don't exist.

.PARAMETER UpdateMode
    Specifies the update mode: 'Full' replaces all data, 'Incremental' updates existing records. Default is 'Incremental'.

.PARAMETER SchemaName
    The database schema name to use. Defaults to 'dbo'.

.PARAMETER WhatIf
    Shows what would happen if the cmdlet runs. The cmdlet is not executed.

.PARAMETER Verbose
    Provides detailed information about the operations being performed.

.EXAMPLE
    Export-ADObjectsToDatabase -Server "SQLSERVER01" -Database "ADInventory" -CreateSchema

    Exports all AD users and groups to the ADInventory database, creating the schema if needed.

.EXAMPLE
    Export-ADObjectsToDatabase -Server "SQLSERVER01" -Database "ADInventory" `
        -ObjectType "User" -SearchBase "OU=Users,DC=contoso,DC=com"

    Exports only users from a specific OU.

.EXAMPLE
    Export-ADObjectsToDatabase -Server "SQLSERVER01" -Database "ADInventory" `
        -Filter "Department -eq 'IT'" -UpdateMode "Full"

    Exports all AD objects matching the filter and replaces all existing data.

.EXAMPLE
    $cred = Get-Credential
    Export-ADObjectsToDatabase -Server "SQLSERVER01" -Database "ADInventory" `
        -Credential $cred -CreateSchema

    Exports AD objects using SQL Server authentication.

.OUTPUTS
    PSCustomObject with the following properties:
    - UsersProcessed: Number of users processed
    - GroupsProcessed: Number of groups processed
    - UsersInserted: Number of users inserted
    - UsersUpdated: Number of users updated
    - GroupsInserted: Number of groups inserted
    - GroupsUpdated: Number of groups updated
    - Errors: Array of error messages

.NOTES
    This cmdlet requires:
    - The ActiveDirectory PowerShell module
    - Appropriate permissions to read from Active Directory
    - Appropriate permissions to write to the SQL Server database
    - Windows OS (for Active Directory cmdlets)

    Author: GDS Team
    Module: GDS.ActiveDirectory
#>
function Export-ADObjectsToDatabase {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Server,

        [Parameter(Mandatory = $true)]
        [string]$Database,

        [Parameter(Mandatory = $false)]
        [System.Management.Automation.PSCredential]$Credential,

        [Parameter(Mandatory = $false)]
        [ValidateSet('User', 'Group', 'All')]
        [string[]]$ObjectType = @('All'),

        [Parameter(Mandatory = $false)]
        [string]$Filter,

        [Parameter(Mandatory = $false)]
        [string]$SearchBase,

        [Parameter(Mandatory = $false)]
        [switch]$CreateSchema,

        [Parameter(Mandatory = $false)]
        [ValidateSet('Full', 'Incremental')]
        [string]$UpdateMode = 'Incremental',

        [Parameter(Mandatory = $false)]
        [string]$SchemaName = 'dbo'
    )

    $ErrorActionPreference = 'Stop'

    # Initialize logging if not already initialized
    if (-not (Get-Module -Name GDS.Common -ErrorAction SilentlyContinue)) {
        Import-Module GDS.Common -ErrorAction SilentlyContinue
    }

    if (Get-Command Initialize-Logging -ErrorAction SilentlyContinue) {
        Initialize-Logging -ModuleName "ActiveDirectory"
    }

    $script:ExportStartTime = Get-Date
    Write-Log -Message "Starting AD objects export to database" -Level Info -Context @{
        Server = $Server
        Database = $Database
        ObjectType = $ObjectType
        UpdateMode = $UpdateMode
        CreateSchema = $CreateSchema
    }

    # Initialize result object
    $result = [PSCustomObject]@{
        UsersProcessed = 0
        GroupsProcessed = 0
        UsersInserted = 0
        UsersUpdated = 0
        GroupsInserted = 0
        GroupsUpdated = 0
        Errors = @()
    }

    try {
        # Validate ActiveDirectory module is available
        if (-not (Get-Module -ListAvailable -Name ActiveDirectory)) {
            throw "ActiveDirectory PowerShell module is not available. Please install RSAT-AD-PowerShell feature."
        }

        Import-Module ActiveDirectory -ErrorAction Stop | Out-Null

        # Import GDS.Common for logging
        if (-not (Get-Module -Name GDS.Common -ErrorAction SilentlyContinue)) {
            Import-Module GDS.Common -ErrorAction SilentlyContinue
        }

        # Build common parameters for AD cmdlets
        $adParams = @{}
        if ($SearchBase) {
            $adParams['SearchBase'] = $SearchBase
        }
        if ($Filter) {
            $adParams['Filter'] = $Filter
        }

        # Determine what to export
        $exportUsers = ($ObjectType -contains 'All' -or $ObjectType -contains 'User')
        $exportGroups = ($ObjectType -contains 'All' -or $ObjectType -contains 'Group')

        if (-not $exportUsers -and -not $exportGroups) {
            throw "No object types specified for export. Use -ObjectType 'User', 'Group', or 'All'."
        }

        # Connect to database
        Write-Log -Message "Connecting to SQL Server" -Level Info -Context @{
            Server = $Server
            Database = $Database
            Authentication = if ($Credential) { "SQL" } else { "Windows" }
        }
        $connection = Get-DatabaseConnection -Server $Server -Database $Database -Credential $Credential
        Write-Log -Message "Database connection established" -Level Info

        try {
            # Create schema if requested
            if ($CreateSchema) {
                if ($PSCmdlet.ShouldProcess("Database schema in $Database", "Create")) {
                    Write-Log -Message "Creating database schema" -Level Info -Context @{SchemaName = $SchemaName}
                    New-ADDatabaseSchema -Connection $connection -SchemaName $SchemaName
                    Write-Log -Message "Database schema created/verified successfully" -Level Info
                }
            }

            # Begin transaction
            $transaction = $connection.BeginTransaction()
            Write-Log -Message "Database transaction started" -Level Info

            try {
                # Export Users
                if ($exportUsers) {
                    if ($PSCmdlet.ShouldProcess("AD Users", "Export to database")) {
                        Write-Log -Message "Retrieving AD Users" -Level Info -Context $adParams
                        $userStartTime = Get-Date
                        $users = Get-ADUser @adParams -Properties *
                        $userRetrievalTime = (Get-Date) - $userStartTime
                        Write-Log -Message "Retrieved AD Users" -Level Info -Context @{
                            Count = $users.Count
                            DurationMs = $userRetrievalTime.TotalMilliseconds
                        }

                        if ($users.Count -gt 0) {
                            Write-Log -Message "Writing users to database" -Level Info
                            $userStats = $users | Write-ADUserToDatabase -Connection $connection -SchemaName $SchemaName -UpdateMode $UpdateMode
                            $result.UsersProcessed = $users.Count
                            $result.UsersInserted = $userStats.Inserted
                            $result.UsersUpdated = $userStats.Updated
                            $result.Errors += $userStats.Errors
                            Write-Log -Message "Users export completed" -Level Info -Context @{
                                Processed = $users.Count
                                Inserted = $userStats.Inserted
                                Updated = $userStats.Updated
                                Errors = $userStats.Errors.Count
                            }
                        }
                    }
                }

                # Export Groups
                if ($exportGroups) {
                    if ($PSCmdlet.ShouldProcess("AD Groups", "Export to database")) {
                        Write-Log -Message "Retrieving AD Groups" -Level Info -Context $adParams
                        $groupStartTime = Get-Date
                        $groups = Get-ADGroup @adParams -Properties *
                        $groupRetrievalTime = (Get-Date) - $groupStartTime
                        Write-Log -Message "Retrieved AD Groups" -Level Info -Context @{
                            Count = $groups.Count
                            DurationMs = $groupRetrievalTime.TotalMilliseconds
                        }

                        if ($groups.Count -gt 0) {
                            Write-Log -Message "Writing groups to database" -Level Info
                            $groupStats = $groups | Write-ADGroupToDatabase -Connection $connection -SchemaName $SchemaName -UpdateMode $UpdateMode
                            $result.GroupsProcessed = $groups.Count
                            $result.GroupsInserted = $groupStats.Inserted
                            $result.GroupsUpdated = $groupStats.Updated
                            $result.Errors += $groupStats.Errors
                            Write-Log -Message "Groups export completed" -Level Info -Context @{
                                Processed = $groups.Count
                                Inserted = $groupStats.Inserted
                                Updated = $groupStats.Updated
                                Errors = $groupStats.Errors.Count
                            }
                        }
                    }
                }

                # Commit transaction
                if (-not $WhatIfPreference) {
                    $transaction.Commit()
                    Write-Log -Message "Transaction committed successfully" -Level Info
                }
                else {
                    $transaction.Rollback()
                    Write-Log -Message "Transaction rolled back (WhatIf mode)" -Level Info
                }
            }
            catch {
                Write-Log -Message "Error during export operation" -Level Error -Exception $_.Exception
                $transaction.Rollback()
                Write-Log -Message "Transaction rolled back due to error" -Level Warning
                throw
            }
        }
        finally {
            # Close connection
            if ($connection.State -eq [System.Data.ConnectionState]::Open) {
                $connection.Close()
                Write-Log -Message "Database connection closed" -Level Info
            }
        }
    }
    catch {
        $errorMsg = "Failed to export AD objects: $_"
        Write-Log -Message $errorMsg -Level Error -Exception $_.Exception
        $result.Errors += $errorMsg
    }

    # Log final results
    $totalDuration = (Get-Date) - $script:ExportStartTime
    Write-Log -Message "AD objects export completed" -Level Info -Context @{
        UsersProcessed = $result.UsersProcessed
        UsersInserted = $result.UsersInserted
        UsersUpdated = $result.UsersUpdated
        GroupsProcessed = $result.GroupsProcessed
        GroupsInserted = $result.GroupsInserted
        GroupsUpdated = $result.GroupsUpdated
        TotalErrors = $result.Errors.Count
        TotalDurationMs = $totalDuration.TotalMilliseconds
    }

    # Return result
    return $result
}

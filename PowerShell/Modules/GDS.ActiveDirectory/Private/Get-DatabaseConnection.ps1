<#
.SYNOPSIS
    Creates a SQL Server database connection.

.DESCRIPTION
    This function creates and opens a connection to a SQL Server database using either
    Windows Authentication or SQL Server Authentication.

.PARAMETER Server
    The SQL Server instance name or connection string server portion.

.PARAMETER Database
    The name of the database to connect to.

.PARAMETER Credential
    Optional PSCredential object for SQL Server Authentication. If not provided, Windows Authentication is used.

.PARAMETER ConnectionTimeout
    Connection timeout in seconds. Default is 30.

.EXAMPLE
    $conn = Get-DatabaseConnection -Server "SQLSERVER01" -Database "ADInventory"

.EXAMPLE
    $cred = Get-Credential
    $conn = Get-DatabaseConnection -Server "SQLSERVER01" -Database "ADInventory" -Credential $cred

.NOTES
    This function is part of the GDS.ActiveDirectory module.
    The connection must be closed by the caller using $conn.Close()
#>
function Get-DatabaseConnection {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Server,

        [Parameter(Mandatory = $true)]
        [string]$Database,

        [Parameter(Mandatory = $false)]
        [System.Management.Automation.PSCredential]$Credential,

        [Parameter(Mandatory = $false)]
        [int]$ConnectionTimeout = 30
    )

    $ErrorActionPreference = 'Stop'

    try {
        # Build connection string
        $connectionStringBuilder = New-Object System.Data.SqlClient.SqlConnectionStringBuilder
        $connectionStringBuilder.DataSource = $Server
        $connectionStringBuilder.InitialCatalog = $Database
        $connectionStringBuilder.ConnectTimeout = $ConnectionTimeout
        $connectionStringBuilder.IntegratedSecurity = $true

        # If credential is provided, use SQL Authentication
        if ($Credential) {
            $connectionStringBuilder.IntegratedSecurity = $false
            $connectionStringBuilder.UserID = $Credential.UserName
            $connectionStringBuilder.Password = $Credential.GetNetworkCredential().Password
        }

        # Create and open connection
        $connection = New-Object System.Data.SqlClient.SqlConnection($connectionStringBuilder.ConnectionString)
        $connection.Open()

        Write-Verbose "Successfully connected to SQL Server: $Server, Database: $Database"
        return $connection
    }
    catch {
        Write-Error "Failed to connect to database: $_"
        throw
    }
}

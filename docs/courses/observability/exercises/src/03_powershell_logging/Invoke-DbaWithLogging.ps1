#!/usr/bin/env pwsh
# Invoke-DbaWithLogging.ps1 - Capture dbatools output to structured logs

$modulePath = Join-Path $PSScriptRoot "StructuredLogger.psm1"
Import-Module $modulePath -Force

$logPath = Join-Path $PSScriptRoot "logs/dbatools.json"
$logger = New-StructuredLogger -LogPath $logPath -MinLevel 'Verbose'

function Invoke-DbaWithStreamCapture {
    param(
        [StructuredLogger]$Logger,
        [scriptblock]$ScriptBlock,
        [string]$OperationName
    )

    $Logger.Info("Starting operation: $OperationName")
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

    # Save current preferences
    $savedVerbose = $VerbosePreference
    $savedWarning = $WarningPreference
    $savedInfo = $InformationPreference

    try {
        # Enable all streams
        $VerbosePreference = 'Continue'
        $WarningPreference = 'Continue'
        $InformationPreference = 'Continue'

        # Capture all streams
        $output = & $ScriptBlock *>&1

        foreach ($item in $output) {
            $level = switch ($item.GetType().Name) {
                'ErrorRecord'       { 'Error' }
                'WarningRecord'     { 'Warning' }
                'VerboseRecord'     { 'Verbose' }
                'InformationRecord' { 'Information' }
                default             { 'Information' }
            }

            $Logger.Log($level, $item.ToString(), @{
                Source = "DbaTools"
                Operation = $OperationName
            })
        }

        $stopwatch.Stop()
        $Logger.Info("Completed operation: $OperationName", @{
            DurationMs = $stopwatch.ElapsedMilliseconds
        })

    } catch {
        $stopwatch.Stop()
        $Logger.Error("Failed operation: $OperationName", @{
            DurationMs = $stopwatch.ElapsedMilliseconds
            Error = $_.Exception.Message
        })
        throw
    } finally {
        # Restore preferences
        $VerbosePreference = $savedVerbose
        $WarningPreference = $savedWarning
        $InformationPreference = $savedInfo
    }
}

# Example usage (simulated dbatools call)
Write-Host "Simulating dbatools operation with stream capture..."

Invoke-DbaWithStreamCapture -Logger $logger -OperationName "Test-DbaConnection" -ScriptBlock {
    # Simulate dbatools verbose output
    Write-Verbose "Testing connection to SQL Server..."
    Write-Verbose "Connection successful"
    Write-Information "SQL Server 2019 detected" -InformationAction Continue
    Write-Warning "Server is running with default collation"

    # Return result
    @{ ComputerName = "prod-db-01"; SqlInstance = "prod-db-01"; IsAccessible = $true }
}

Write-Host "`nCheck logs/dbatools.json for captured output"

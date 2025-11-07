<#
.SYNOPSIS
    Configures advanced PSFramework logging settings for GDS modules.

.DESCRIPTION
    Provides advanced configuration options for PSFramework logging including
    multiple output targets, log levels, and integration with external systems.

.PARAMETER ModuleName
    Module name to configure logging for.

.PARAMETER EnableEventLog
    Enable Windows Event Log output.

.PARAMETER EnableFileLog
    Enable file-based logging (default: enabled).

.PARAMETER EnableConsoleLog
    Enable console output (default: enabled).

.PARAMETER LogPath
    Custom log file path.

.PARAMETER MinimumLevel
    Minimum log level to record.

.PARAMETER MaxLogSizeMB
    Maximum log file size before rotation.

.PARAMETER RetentionDays
    Number of days to retain logs.

.EXAMPLE
    Set-GDSLogging -ModuleName "ActiveDirectory" -EnableEventLog -MinimumLevel "Debug"

.NOTES
    This function provides advanced PSFramework logging configuration.
    See: https://psframework.org/documentation/documents/psframework/logging.html
#>
function Set-GDSLogging {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$ModuleName,

        [Parameter(Mandatory = $false)]
        [switch]$EnableEventLog,

        [Parameter(Mandatory = $false)]
        [switch]$EnableFileLog = $true,

        [Parameter(Mandatory = $false)]
        [switch]$EnableConsoleLog = $true,

        [Parameter(Mandatory = $false)]
        [string]$LogPath,

        [Parameter(Mandatory = $false)]
        [ValidateSet('Debug', 'Verbose', 'Info', 'Warning', 'Error', 'Critical')]
        [string]$MinimumLevel = 'Info',

        [Parameter(Mandatory = $false)]
        [int]$MaxLogSizeMB = 10,

        [Parameter(Mandatory = $false)]
        [int]$RetentionDays = 30
    )

    # Ensure PSFramework is loaded
    if (-not (Get-Module -Name PSFramework -ErrorAction SilentlyContinue)) {
        Import-Module PSFramework -ErrorAction Stop
    }

    # Map log level
    $levelMap = @{
        'Debug' = 'Debug'
        'Verbose' = 'Verbose'
        'Info' = 'Important'
        'Warning' = 'Warning'
        'Error' = 'Error'
        'Critical' = 'Critical'
    }
    $psfLevel = $levelMap[$MinimumLevel]

    try {
        # Set minimum log level
        Set-PSFConfig -FullName 'PSFramework.Logging.MinimumLevel' -Value $psfLevel

        # Configure file logging
        if ($EnableFileLog) {
            if ($LogPath) {
                $logDir = Split-Path $LogPath -Parent
                if (-not (Test-Path $logDir)) {
                    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
                }
                $filePath = $LogPath
            }
            else {
                $filePath = Join-Path $env:APPDATA "PSFramework\Logs\${ModuleName}_$(Get-Date -Format 'yyyyMMdd').log"
            }

            Set-PSFLoggingProvider -Name 'logfile' -InstanceName $ModuleName `
                -FilePath $filePath `
                -Enabled $true `
                -LogRotationMaxSizeMB $MaxLogSizeMB `
                -LogRetentionDays $RetentionDays
        }
        else {
            Set-PSFLoggingProvider -Name 'logfile' -InstanceName $ModuleName -Enabled $false
        }

        # Configure console logging
        Set-PSFLoggingProvider -Name 'console' -Enabled $EnableConsoleLog

        # Configure event log if requested (Windows only)
        if ($EnableEventLog) {
            # Check if running on Windows
            $isWindowsPlatform = ($PSVersionTable.PSVersion.Major -lt 6) -or $IsWindows

            if ($isWindowsPlatform) {
                $eventLogSource = "GDS.$ModuleName"
                if (-not [System.Diagnostics.EventLog]::SourceExists($eventLogSource)) {
                    New-EventLog -LogName Application -Source $eventLogSource -ErrorAction SilentlyContinue
                }

                Set-PSFLoggingProvider -Name 'eventlog' -InstanceName $ModuleName `
                    -LogName 'Application' `
                    -Source $eventLogSource `
                    -Enabled $true

                Write-PSFMessage -Level Important -Message "Event Log enabled for $ModuleName" -Tag "Configuration"
            }
            else {
                Write-PSFMessage -Level Warning -Message "Event Log not available on non-Windows platforms. Skipping Event Log configuration." -Tag "Configuration"
            }
        }

        Write-PSFMessage -Level Important -Message "PSFramework logging configured for module: $ModuleName" -Tag "Configuration", $ModuleName
    }
    catch {
        Write-Error "Failed to configure PSFramework logging: $_"
        throw
    }
}

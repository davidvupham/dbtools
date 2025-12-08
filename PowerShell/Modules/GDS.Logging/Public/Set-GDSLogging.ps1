<#
.SYNOPSIS
    Configures advanced PSFramework logging settings for GDS modules.

.DESCRIPTION
    Provides advanced configuration options for PSFramework logging including
    multiple output targets, log levels, and integration with external systems.

.PARAMETER ModuleName
    Log owner name (aliases: LogOwner, LogFileName) to configure logging for. The same value scopes PSFramework configuration.

.PARAMETER EnableEventLog
    Enable Windows Event Log output.

.PARAMETER EnableFileLog
    Enable file-based logging (default: enabled).

.PARAMETER EnableConsoleLog
    Enable console output (default: enabled).

.PARAMETER LogPath
    Custom log file path. If omitted, the directory specified by the GDS_LOG_DIR environment variable is used.

.PARAMETER MinimumLevel
    Minimum log level to record.

.EXAMPLE
    Set-GDSLogging -ModuleName "ActiveDirectory" -EnableEventLog -MinimumLevel "Debug"

.NOTES
    This function provides advanced PSFramework logging configuration.
    Ensure the GDS_LOG_DIR environment variable is set when file logging is enabled.
    Log entries retain module tags even when multiple modules write to the same log owner.
    See: https://psframework.org/documentation/documents/psframework/logging.html
#>
function Set-GDSLogging {
    [CmdletBinding()]
    param(
        [Alias('LogOwner', 'LogFileName')]
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
        [string]$MinimumLevel = 'Info'
    )

    # Ensure PSFramework is loaded
    if (-not (Get-Module -Name PSFramework -ErrorAction SilentlyContinue)) {
        Import-Module PSFramework -ErrorAction Stop
    }

    # Persist module scoped configuration
    $configPrefix = "GDS.Logging.$ModuleName"
    Set-PSFConfig -FullName "$configPrefix.MinimumLevel" -Value $MinimumLevel -Initialize -Validation 'string' -Description "Minimum log level for $ModuleName module"

    try {
        # Configure file logging
        if ($EnableFileLog) {
            if ($LogPath) {
                $resolvedLogPath = [Environment]::ExpandEnvironmentVariables($LogPath)
                if (-not [System.IO.Path]::IsPathRooted($resolvedLogPath)) {
                    $resolvedLogPath = Join-Path -Path (Get-Location) -ChildPath $resolvedLogPath
                }

                $resolvedLogPath = [System.IO.Path]::GetFullPath($resolvedLogPath)

                $logDir = Split-Path -Path $resolvedLogPath -Parent
                if (-not (Test-Path $logDir)) {
                    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
                }
                $filePath = $resolvedLogPath
            }
            else {
                $logDirectoryValue = Get-GDSLogRoot
                if ([string]::IsNullOrWhiteSpace($logDirectoryValue)) {
                    throw "Environment variable 'GDS_LOG_DIR' must be set to a writable directory before enabling file logging."
                }

                $expandedLogDirectory = [Environment]::ExpandEnvironmentVariables($logDirectoryValue)

                if (-not (Test-Path -LiteralPath $expandedLogDirectory)) {
                    New-Item -ItemType Directory -Path $expandedLogDirectory -Force | Out-Null
                }

                $resolvedDirectory = $expandedLogDirectory
                $resolved = Resolve-Path -Path $expandedLogDirectory -ErrorAction SilentlyContinue
                if ($resolved) {
                    $resolvedDirectory = $resolved.ProviderPath
                }
                elseif (-not [System.IO.Path]::IsPathRooted($expandedLogDirectory)) {
                    $resolvedDirectory = [System.IO.Path]::GetFullPath((Join-Path -Path (Get-Location) -ChildPath $expandedLogDirectory))
                }
                else {
                    $resolvedDirectory = [System.IO.Path]::GetFullPath($expandedLogDirectory)
                }

                if (-not (Test-Path -LiteralPath $resolvedDirectory)) {
                    New-Item -ItemType Directory -Path $resolvedDirectory -Force | Out-Null
                }

                $filePath = Join-Path -Path $resolvedDirectory -ChildPath "${ModuleName}_$(Get-Date -Format 'yyyyMMdd').log"
            }

            Set-PSFLoggingProvider -Name 'logfile' -InstanceName $ModuleName `
                -FilePath $filePath `
                -Enabled $true
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

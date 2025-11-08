<#
.SYNOPSIS
    Initializes PSFramework logging for a module.

.DESCRIPTION
    Configures PSFramework logging providers for file-based logging with automatic
    rotation and structured output. PSFramework is the de facto standard for PowerShell
    logging and provides comprehensive features.

.PARAMETER ModuleName
    Optional log owner name (aliases: LogOwner, LogFileName). Defaults to the invoking script name; provide a value to override or share log files across scripts. The same value is used for PSFramework configuration scoping.

.PARAMETER LogPath
    Optional custom log file path. If not specified, the module writes to the directory defined by the GDS_LOG_DIR environment variable.

.PARAMETER LogLevel
    Minimum log level to record. Default is 'Info'. Valid values: Debug, Verbose, Info, Warning, Error, Critical.

.EXAMPLE
    Initialize-Logging -ModuleName "ActiveDirectory"

.EXAMPLE
    Initialize-Logging -ModuleName "ActiveDirectory" -LogPath "C:\Logs\AD.log" -LogLevel "Debug"

.NOTES
    This function configures PSFramework logging providers. PSFramework automatically:
    - Creates log files in the directory specified by GDS_LOG_DIR (or the provided LogPath)
    - Rotates logs when size limit is reached
    - Maintains retention policies
    - Provides structured logging
    - Tags each entry with both the log owner (script) and the emitting module

    See: https://psframework.org/documentation/documents/psframework/logging.html
#>
function Initialize-Logging {
    [CmdletBinding()]
    param(
        [Alias('LogOwner', 'LogFileName')]
        [Parameter(Mandatory = $false)]
        [string]$ModuleName,

        [Parameter(Mandatory = $false)]
        [string]$LogPath,

        [Parameter(Mandatory = $false)]
        [ValidateSet('Debug', 'Verbose', 'Info', 'Warning', 'Error', 'Critical')]
        [string]$LogLevel = 'Info'
    )

    # Ensure PSFramework is loaded
    if (-not (Get-Module -Name PSFramework -ErrorAction SilentlyContinue)) {
        Import-Module PSFramework -ErrorAction Stop
    }

    # Detect module name from call stack if not provided
    $callStack = Get-PSCallStack
    $ModuleName = Resolve-GDSModuleName -ExplicitName $ModuleName -CallStack $callStack

    # Persist module scoped configuration
    $configPrefix = "GDS.Common.Logging.$ModuleName"
    Set-PSFConfig -FullName "$configPrefix.MinimumLevel" -Value $LogLevel -Initialize -Validation 'string' -Description "Minimum log level for $ModuleName module"

    # Configure PSFramework logging
    try {
        # Determine log file path
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

            $logFilePath = $resolvedLogPath
        }
        else {
            $logDirectoryValue = Get-GDSLogRoot
            if ([string]::IsNullOrWhiteSpace($logDirectoryValue)) {
                throw "Environment variable 'GDS_LOG_DIR' must be set to a writable directory before calling Initialize-Logging."
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

            $logFilePath = Join-Path -Path $resolvedDirectory -ChildPath "${ModuleName}_$(Get-Date -Format 'yyyyMMdd').log"
        }

        # Configure file logging provider
        Set-PSFLoggingProvider -Name 'logfile' -InstanceName $ModuleName `
            -FilePath $logFilePath `
            -Enabled $true

        # Enable console output for Info and above
        Set-PSFLoggingProvider -Name 'console' -Enabled $true

        Write-PSFMessage -Level Important -Message "PSFramework logging initialized for module: $ModuleName" -Tag "Initialization", $ModuleName
    }
    catch {
        Write-Warning "Failed to initialize PSFramework logging: $_"
        throw
    }
}

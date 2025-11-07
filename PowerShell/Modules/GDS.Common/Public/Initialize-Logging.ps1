<#
.SYNOPSIS
    Initializes PSFramework logging for a module.

.DESCRIPTION
    Configures PSFramework logging providers for file-based logging with automatic
    rotation and structured output. PSFramework is the de facto standard for PowerShell
    logging and provides comprehensive features.

.PARAMETER ModuleName
    Module name for log file naming. If not specified, attempts to detect from calling module.

.PARAMETER LogPath
    Optional custom log file path. If not specified, uses PSFramework default location.

.PARAMETER LogLevel
    Minimum log level to record. Default is 'Info'. Valid values: Debug, Verbose, Info, Warning, Error, Critical.

.PARAMETER MaxLogSizeMB
    Maximum log file size in MB before rotation. Default is 10MB.

.PARAMETER RetentionDays
    Number of days to retain log files. Default is 30 days.

.EXAMPLE
    Initialize-Logging -ModuleName "ActiveDirectory"

.EXAMPLE
    Initialize-Logging -ModuleName "ActiveDirectory" -LogPath "C:\Logs\AD.log" -LogLevel "Debug"

.NOTES
    This function configures PSFramework logging providers. PSFramework automatically:
    - Creates log files in AppData\PSFramework\Logs by default
    - Rotates logs when size limit is reached
    - Maintains retention policies
    - Provides structured logging

    See: https://psframework.org/documentation/documents/psframework/logging.html
#>
function Initialize-Logging {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [string]$ModuleName,

        [Parameter(Mandatory = $false)]
        [string]$LogPath,

        [Parameter(Mandatory = $false)]
        [ValidateSet('Debug', 'Verbose', 'Info', 'Warning', 'Error', 'Critical')]
        [string]$LogLevel = 'Info',

        [Parameter(Mandatory = $false)]
        [int]$MaxLogSizeMB = 10,

        [Parameter(Mandatory = $false)]
        [int]$RetentionDays = 30
    )

    # Ensure PSFramework is loaded
    if (-not (Get-Module -Name PSFramework -ErrorAction SilentlyContinue)) {
        Import-Module PSFramework -ErrorAction Stop
    }

    # Detect module name from call stack if not provided
    if (-not $ModuleName) {
        $callStack = Get-PSCallStack
        foreach ($frame in $callStack) {
            if ($frame.ScriptName -and $frame.ScriptName -match 'GDS\.(\w+)') {
                $ModuleName = $Matches[1]
                break
            }
        }
        if (-not $ModuleName) {
            $ModuleName = "GDS.Common"
        }
    }

    # Map log level to PSFramework level
    $levelMap = @{
        'Debug' = 'Debug'
        'Verbose' = 'Verbose'
        'Info' = 'Important'
        'Warning' = 'Warning'
        'Error' = 'Error'
        'Critical' = 'Critical'
    }
    $psfLevel = $levelMap[$LogLevel]

    # Configure PSFramework logging
    try {
        # Set minimum log level
        Set-PSFConfig -FullName 'PSFramework.Logging.MinimumLevel' -Value $psfLevel -Initialize -Validation 'string' -Description "Minimum log level for $ModuleName module"

        # Configure file logging provider
        if ($LogPath) {
            # Custom log path
            $logDir = Split-Path $LogPath -Parent
            if (-not (Test-Path $logDir)) {
                New-Item -ItemType Directory -Path $logDir -Force | Out-Null
            }

            Set-PSFLoggingProvider -Name 'logfile' -InstanceName $ModuleName `
                -FilePath $LogPath `
                -Enabled $true `
                -LogRotationMaxSizeMB $MaxLogSizeMB `
                -LogRetentionDays $RetentionDays
        }
        else {
            # Use PSFramework default location (AppData\PSFramework\Logs)
            $defaultPath = Join-Path $env:APPDATA "PSFramework\Logs\${ModuleName}_$(Get-Date -Format 'yyyyMMdd').log"
            Set-PSFLoggingProvider -Name 'logfile' -InstanceName $ModuleName `
                -FilePath $defaultPath `
                -Enabled $true `
                -LogRotationMaxSizeMB $MaxLogSizeMB `
                -LogRetentionDays $RetentionDays
        }

        # Enable console output for Info and above
        Set-PSFLoggingProvider -Name 'console' -Enabled $true

        Write-PSFMessage -Level Important -Message "PSFramework logging initialized for module: $ModuleName" -Tag "Initialization", $ModuleName
    }
    catch {
        Write-Warning "Failed to initialize PSFramework logging: $_"
        throw
    }
}

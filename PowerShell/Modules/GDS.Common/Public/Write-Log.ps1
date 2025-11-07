<#
.SYNOPSIS
    Writes log entries using PSFramework logging (de facto standard for PowerShell).

.DESCRIPTION
    This function provides a wrapper around PSFramework's Write-PSFMessage for consistent
    logging across GDS modules. PSFramework is the de facto standard for PowerShell logging
    and provides comprehensive features including multiple output targets, structured logging,
    and performance optimization.

.PARAMETER Message
    The log message to write.

.PARAMETER Level
    The log level: Debug, Verbose, Info, Warning, Error, or Critical. Default is 'Info'.

.PARAMETER Exception
    Optional exception object to include in the log entry.

.PARAMETER Context
    Optional hashtable with additional context information.

.PARAMETER Tag
    Optional tags for categorizing log entries (e.g., 'Initialization', 'Processing', 'Error').

.PARAMETER ModuleName
    Optional module name. If not specified, attempts to detect from calling module.

.EXAMPLE
    Write-Log -Message "Processing user" -Level Info -Context @{User="jdoe"}

.EXAMPLE
    Write-Log -Message "Error occurred" -Level Error -Exception $_.Exception -Tag "Error"

.EXAMPLE
    Write-Log -Message "Starting operation" -Level Info -Tag "Initialization" -ModuleName "ActiveDirectory"

.NOTES
    This function wraps PSFramework's Write-PSFMessage for consistency across GDS modules.
    PSFramework provides:
    - Multiple output targets (file, event log, Splunk, Azure, etc.)
    - Asynchronous logging (no performance impact)
    - Structured logging
    - Automatic log rotation
    - Runspace-safe concurrent operations

    See: https://psframework.org/documentation/documents/psframework/logging.html
#>
function Write-Log {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,

        [Parameter(Mandatory = $false)]
        [ValidateSet('Debug', 'Verbose', 'Info', 'Warning', 'Error', 'Critical')]
        [string]$Level = 'Info',

        [Parameter(Mandatory = $false)]
        [System.Exception]$Exception,

        [Parameter(Mandatory = $false)]
        [hashtable]$Context,

        [Parameter(Mandatory = $false)]
        [string[]]$Tag,

        [Parameter(Mandatory = $false)]
        [string]$ModuleName
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

    # Build tags
    $allTags = @($ModuleName)
    if ($Tag) {
        $allTags += $Tag
    }

    # Map our log levels to PSFramework levels
    $levelMap = @{
        'Debug' = 'Debug'
        'Verbose' = 'Verbose'
        'Info' = 'Important'
        'Warning' = 'Warning'
        'Error' = 'Error'
        'Critical' = 'Critical'
    }
    $psfLevel = $levelMap[$Level]

    # Build message with context
    $fullMessage = $Message
    if ($Context) {
        $contextString = ($Context.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ', '
        $fullMessage = "$Message | Context: $contextString"
    }

    # Add exception information if provided
    if ($Exception) {
        $fullMessage += " | Exception: $($Exception.GetType().FullName): $($Exception.Message)"
        if ($Exception.StackTrace) {
            $fullMessage += " | StackTrace: $($Exception.StackTrace)"
        }
    }

    # Write log using PSFramework
    try {
        $params = @{
            Level = $psfLevel
            Message = $fullMessage
            Tag = $allTags
        }

        # Add function name if available
        $callStack = Get-PSCallStack
        if ($callStack.Count -gt 1) {
            $params['FunctionName'] = $callStack[1].FunctionName
        }

        # Add target data for structured logging
        if ($Context -or $Exception) {
            $targetData = @{}
            if ($Context) {
                $targetData['Context'] = $Context
            }
            if ($Exception) {
                $targetData['Exception'] = @{
                    Type = $Exception.GetType().FullName
                    Message = $Exception.Message
                    StackTrace = $Exception.StackTrace
                }
            }
            $params['Target'] = $targetData
        }

        Write-PSFMessage @params
    }
    catch {
        # Fallback to basic logging if PSFramework fails
        Write-Warning "PSFramework logging failed: $_"
        Write-Warning "Original message: $Message"
    }
}

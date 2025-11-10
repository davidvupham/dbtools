# Developer's Guide: PSFramework Logging in GDS Modules

## Overview

This guide shows developers how to use PSFramework logging through the GDS.Common module. PSFramework is the de facto standard for PowerShell logging and provides comprehensive, production-ready logging capabilities.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Usage](#basic-usage)
3. [Advanced Usage](#advanced-usage)
4. [Common Patterns](#common-patterns)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)
7. [Complete Examples](#complete-examples)

---

## Quick Start

### Setup Your Module

```powershell
# In your module's .psm1 file or function
Import-Module GDS.Common

# Configure the shared log directory (required)
if (-not $env:GDS_LOG_DIR) {
    $env:GDS_LOG_DIR = "/var/log/gds"   # Use a writable path for your environment
}

# Initialize logging once at module start
Initialize-Logging -ModuleName "YourModule"
```

> Tip: On Windows use `M:\GDS\Logs` (or `%ALLUSERSPROFILE%\GDS\Logs` when the M: drive is unavailable); on Linux/macOS use `/gds/log` (falling back to `/var/log/gds`). The directory is created automatically if it doesn't exist.

> Note: If you omit `-ModuleName`, the log owner defaults to the calling script name so every module invoked by that script writes to the same log file. Specify a custom name only when you need to override that behaviour. When `GDS_LOG_DIR` is unset, the module chooses a platform-specific default in this order:
>
> 1. Windows: `M:\GDS\Logs`, then `%ALLUSERSPROFILE%\GDS\Logs`
> 2. Linux/macOS: `/gds/log`, then `/var/log/gds`
>
> The `-ModuleName` parameter (aliases: `-LogOwner`, `-LogFileName`) controls both the log file name and the PSFramework configuration prefix (`GDS.Common.Logging.<ModuleName>`).

### Basic Logging

```powershell
# Write log messages
Write-Log -Message "Operation started" -Level Info
Write-Log -Message "Processing item" -Level Verbose
Write-Log -Message "Warning condition" -Level Warning
Write-Log -Message "Error occurred" -Level Error
```

That's it! You're now logging with PSFramework.

---

## Basic Usage

### 1. Import and Initialize

```powershell
# At the top of your script or module
Import-Module GDS.Common

# Initialize logging (do this once)
Initialize-Logging -ModuleName "MyModule"
```

### 2. Write Log Messages

#### Simple Messages

```powershell
# Information
Write-Log -Message "User login successful" -Level Info

# Debug information
Write-Log -Message "Entering ProcessUser function" -Level Debug

# Verbose details
Write-Log -Message "Retrieved 150 records from database" -Level Verbose

# Warnings
Write-Log -Message "Connection retry attempt 3/5" -Level Warning

# Errors
Write-Log -Message "Failed to connect to database" -Level Error

# Critical errors
Write-Log -Message "System out of memory" -Level Critical
```

#### Messages with Context

```powershell
# Add context information as a hashtable
Write-Log -Message "User authenticated" -Level Info -Context @{
    UserName = $userName
    LoginTime = Get-Date
    IPAddress = $ipAddress
}

# Multiple context values
Write-Log -Message "Database query completed" -Level Info -Context @{
    Query = "SELECT * FROM Users"
    RowCount = 150
    DurationMs = 234
}
```

#### Messages with Exceptions

```powershell
try {
    # Your code
    $result = Invoke-SomeOperation
}
catch {
    # Log the exception
    Write-Log -Message "Operation failed" -Level Error -Exception $_.Exception
}
```

#### Messages with Tags

```powershell
# Add tags for categorization
Write-Log -Message "Starting sync" -Level Info -Tag "Sync", "Initialization"
Write-Log -Message "Processing complete" -Level Info -Tag "Sync", "Completion"

# Later, you can query by tag
Get-PSFMessage -Tag "Sync"
```

### 3. Log Levels Explained

| Level | When to Use | Example |
|-------|-------------|---------|
| **Debug** | Detailed debugging information | "Variable value: X=5" |
| **Verbose** | Detailed operational information | "Connecting to server..." |
| **Info** | General informational messages | "Operation completed successfully" |
| **Warning** | Warning messages | "Retry attempt 3 of 5" |
| **Error** | Error messages | "Failed to process record" |
| **Critical** | Critical errors | "System failure" |

---

## Advanced Usage

### 1. Custom Configuration

```powershell
# Configure logging with custom settings
Set-GDSLogging -ModuleName "MyModule" `
    -MinimumLevel "Debug" `
    -LogPath "C:\Logs\MyModule.log" `
    -EnableEventLog:$IsWindows
```

> PSFramework handles log rotation and retention for the file provider. To customise those behaviours, set the appropriate `PSFramework.Logging.FileSystem.*` configuration keys with `Set-PSFConfig` (see the PSFramework logging documentation for the full list).

### 2. Query Log Messages

```powershell
# Get recent messages from memory
Get-PSFMessage

# Get last 10 messages
Get-PSFMessage -Last 10

# Get errors only
Get-PSFMessage -Level Error

# Get messages by tag
Get-PSFMessage -Tag "Database"

# Get messages from specific function
Get-PSFMessage -FunctionName "Get-ADUser"

# Get messages within time range
Get-PSFMessage | Where-Object { $_.Timestamp -gt (Get-Date).AddHours(-1) }
```

### 3. Conditional Logging

```powershell
# Log only if verbose preference is set
if ($VerbosePreference -eq 'Continue') {
    Write-Log -Message "Detailed operation info" -Level Verbose
}

# Log with custom condition
if ($DebugMode) {
    Write-Log -Message "Debug info: $variableValue" -Level Debug
}
```

### 4. Performance Logging

```powershell
function Get-DataWithLogging {
    $startTime = Get-Date

    Write-Log -Message "Starting data retrieval" -Level Info -Tag "Performance"

    try {
        # Your operation
        $data = Get-SomeData

        $duration = (Get-Date) - $startTime
        Write-Log -Message "Data retrieval completed" -Level Info -Context @{
            RowCount = $data.Count
            DurationMs = $duration.TotalMilliseconds
        } -Tag "Performance"

        return $data
    }
    catch {
        $duration = (Get-Date) - $startTime
        Write-Log -Message "Data retrieval failed" -Level Error -Exception $_.Exception -Context @{
            DurationMs = $duration.TotalMilliseconds
        } -Tag "Performance", "Error"
        throw
    }
}
```

---

## Common Patterns

### Pattern 1: Function Entry/Exit Logging

```powershell
function Invoke-MyOperation {
    param(
        [string]$Name,
        [int]$Count
    )

    # Log function entry
    Write-Log -Message "Entering Invoke-MyOperation" -Level Debug -Context @{
        Name = $Name
        Count = $Count
    }

    try {
        # Your logic here
        $result = DoSomething -Name $Name -Count $Count

        # Log success
        Write-Log -Message "Invoke-MyOperation completed successfully" -Level Info -Context @{
            Name = $Name
            ResultCount = $result.Count
        }

        return $result
    }
    catch {
        # Log error
        Write-Log -Message "Invoke-MyOperation failed" -Level Error -Exception $_.Exception -Context @{
            Name = $Name
            Count = $Count
        }
        throw
    }
}
```

### Pattern 2: Batch Processing with Progress

```powershell
function Process-Items {
    param(
        [array]$Items
    )

    Write-Log -Message "Starting batch processing" -Level Info -Context @{
        TotalItems = $Items.Count
    }

    $processed = 0
    $errors = 0

    foreach ($item in $Items) {
        try {
            # Process item
            Process-SingleItem -Item $item
            $processed++

            # Log progress every 100 items
            if ($processed % 100 -eq 0) {
                Write-Log -Message "Batch processing progress" -Level Info -Context @{
                    Processed = $processed
                    Total = $Items.Count
                    PercentComplete = [math]::Round(($processed / $Items.Count) * 100, 2)
                }
            }
        }
        catch {
            $errors++
            Write-Log -Message "Failed to process item" -Level Warning -Exception $_.Exception -Context @{
                ItemId = $item.Id
                ItemName = $item.Name
            }
        }
    }

    # Log completion summary
    Write-Log -Message "Batch processing completed" -Level Info -Context @{
        TotalItems = $Items.Count
        Processed = $processed
        Errors = $errors
        SuccessRate = [math]::Round(($processed / $Items.Count) * 100, 2)
    }
}
```

### Pattern 3: Database Operations

```powershell
function Invoke-DatabaseQuery {
    param(
        [string]$Query,
        [hashtable]$Parameters
    )

    $startTime = Get-Date

    Write-Log -Message "Executing database query" -Level Debug -Context @{
        Query = $Query.Substring(0, [Math]::Min(100, $Query.Length))  # First 100 chars
    }

    try {
        # Execute query
        $result = Invoke-SqlCmd -Query $Query -Parameters $Parameters

        $duration = (Get-Date) - $startTime

        Write-Log -Message "Database query successful" -Level Info -Context @{
            RowCount = $result.Count
            DurationMs = $duration.TotalMilliseconds
        } -Tag "Database", "Performance"

        return $result
    }
    catch {
        $duration = (Get-Date) - $startTime

        Write-Log -Message "Database query failed" -Level Error -Exception $_.Exception -Context @{
            Query = $Query
            DurationMs = $duration.TotalMilliseconds
        } -Tag "Database", "Error"

        throw
    }
}
```

### Pattern 4: API Calls with Retry

```powershell
function Invoke-APIWithRetry {
    param(
        [string]$Endpoint,
        [int]$MaxRetries = 3
    )

    $attempt = 0

    while ($attempt -lt $MaxRetries) {
        $attempt++

        Write-Log -Message "Calling API" -Level Info -Context @{
            Endpoint = $Endpoint
            Attempt = $attempt
            MaxRetries = $MaxRetries
        } -Tag "API"

        try {
            $response = Invoke-RestMethod -Uri $Endpoint

            Write-Log -Message "API call successful" -Level Info -Context @{
                Endpoint = $Endpoint
                Attempt = $attempt
                StatusCode = 200
            } -Tag "API"

            return $response
        }
        catch {
            Write-Log -Message "API call failed" -Level Warning -Exception $_.Exception -Context @{
                Endpoint = $Endpoint
                Attempt = $attempt
                MaxRetries = $MaxRetries
            } -Tag "API", "Retry"

            if ($attempt -eq $MaxRetries) {
                Write-Log -Message "API call failed after all retries" -Level Error -Context @{
                    Endpoint = $Endpoint
                    TotalAttempts = $attempt
                } -Tag "API", "Error"
                throw
            }

            # Wait before retry
            Start-Sleep -Seconds (2 * $attempt)
        }
    }
}
```

### Pattern 5: Workflow Logging

```powershell
function Start-Workflow {
    param(
        [string]$WorkflowName,
        [hashtable]$Parameters
    )

    $workflowId = [Guid]::NewGuid().ToString()
    $startTime = Get-Date

    # Log workflow start
    Write-Log -Message "Workflow started" -Level Info -Context @{
        WorkflowId = $workflowId
        WorkflowName = $WorkflowName
        Parameters = ($Parameters.Keys -join ', ')
    } -Tag "Workflow", "Start"

    try {
        # Step 1
        Write-Log -Message "Workflow step 1: Initialize" -Level Info -Context @{
            WorkflowId = $workflowId
            Step = 1
        } -Tag "Workflow"
        Step1-Initialize

        # Step 2
        Write-Log -Message "Workflow step 2: Process" -Level Info -Context @{
            WorkflowId = $workflowId
            Step = 2
        } -Tag "Workflow"
        Step2-Process

        # Step 3
        Write-Log -Message "Workflow step 3: Finalize" -Level Info -Context @{
            WorkflowId = $workflowId
            Step = 3
        } -Tag "Workflow"
        Step3-Finalize

        $duration = (Get-Date) - $startTime

        # Log workflow completion
        Write-Log -Message "Workflow completed successfully" -Level Info -Context @{
            WorkflowId = $workflowId
            WorkflowName = $WorkflowName
            DurationMs = $duration.TotalMilliseconds
            Status = "Success"
        } -Tag "Workflow", "Complete"
    }
    catch {
        $duration = (Get-Date) - $startTime

        # Log workflow failure
        Write-Log -Message "Workflow failed" -Level Error -Exception $_.Exception -Context @{
            WorkflowId = $workflowId
            WorkflowName = $WorkflowName
            DurationMs = $duration.TotalMilliseconds
            Status = "Failed"
        } -Tag "Workflow", "Error"

        throw
    }
}
```

---

## Working with Third-Party Modules

Modules such as `dbatools` emit pipeline output and standard PowerShell streams. They do not automatically write to the PSFramework log configured via `GDS.Common`. Wrap their calls and log the results yourself so every action lands in the same file.

### 1. Initialize a Shared Log Owner

```powershell
Import-Module GDS.Common, dbatools

if (-not $env:GDS_LOG_DIR) {
    $env:GDS_LOG_DIR = "/var/log/gds"
}

Initialize-Logging -ModuleName "DatabaseMaintenance"
```

### 2. Wrap External Calls and Log Outcomes

```powershell
function Invoke-LoggedQuery {
    param(
        [string]$SqlInstance,
        [string]$Database,
        [string]$Query
    )

    $start = Get-Date

    try {
        $result = Invoke-DbaQuery -SqlInstance $SqlInstance -Database $Database -Query $Query

        Write-Log -Level Info -Message "Invoke-DbaQuery completed" -Context @{
            SqlInstance = $SqlInstance
            Database    = $Database
            Rows        = $result.Count
            DurationMs  = ((Get-Date) - $start).TotalMilliseconds
        } -Tag "dbatools", "Success"

        return $result
    }
    catch {
        Write-Log -Level Error -Message "Invoke-DbaQuery failed" -Exception $_.Exception -Context @{
            SqlInstance = $SqlInstance
            Database    = $Database
            DurationMs  = ((Get-Date) - $start).TotalMilliseconds
        } -Tag "dbatools", "Error"

        throw
    }
}
```

### 3. Capture Verbose, Warning, or Information Streams

- **Manual capture.**

    ```powershell
    $verbose = Invoke-Command {
        $VerbosePreference = 'Continue'
        Invoke-DbaDbUpgrade -SqlInstance $SqlInstance -Database $Database 4>&1
    }

    if ($verbose) {
        Write-Log -Level Verbose -Message "dbatools verbose output" -Context @{
            Lines = ($verbose | Out-String).Trim()
        } -Tag "dbatools", "Verbose"
    }
    ```

- **PSFramework message proxies.**

    ```powershell
    Register-PSFMessageProxy -InformationTarget PSFramework
    Register-PSFMessageProxy -VerboseTarget    PSFramework
    Register-PSFMessageProxy -WarningTarget    PSFramework
    ```

    Once registered, built-in stream output is forwarded to `Write-PSFMessage`, so it is routed to the same providers configured through `GDS.Common`.

### 4. Standardise Context Metadata

Agree on core fields—`OperationId`, `SqlInstance`, `Database`, etc.—and reuse them for every log entry (your code and third-party wrappers alike).

```powershell
$commonContext = @{
    OperationId = $operationId
    SqlInstance = $SqlInstance
    Database    = $Database
}

Write-Log -Level Verbose -Message "Starting maintenance step" -Context $commonContext -Tag "Maintenance", "Start"
```

### 5. Transcript for Full Fidelity (Optional)

Use transcripts when you need every character captured. Still log the transcript location so operators can find it alongside the structured log.

```powershell
$transcriptPath = Join-Path $env:GDS_LOG_DIR "DatabaseMaintenance-$(Get-Date -Format yyyyMMdd_HHmmss).txt"
Start-Transcript -Path $transcriptPath -Force

try {
    Invoke-LoggedQuery @params
}
finally {
    Stop-Transcript | Out-Null
    Write-Log -Level Info -Message "Transcript captured" -Context @{ Path = $transcriptPath } -Tag "Transcript"
}
```

These practices ensure that your code, third-party modules, and optional transcripts stay aligned in a single PSFramework-managed log file.

---

## Alternative Logging Options

PSFramework covers the vast majority of GDS scenarios, but there are cases where other logging patterns may be preferred. The table below highlights the primary alternatives, their strengths, and trade-offs.

| Option | Pros | Cons | Ideal When |
| --- | --- | --- | --- |
| Built-in PowerShell streams (`Write-Information`, `Write-Verbose`, `Write-Warning`, `Write-Error`) | Native behaviour; no extra dependencies; respects preference variables | Ephemeral output; no rotation/retention; limited structure | Short-lived scripts, local tooling, or CI jobs where console output is captured externally |
| Custom logging implementation | Tailored to bespoke requirements; org-specific formatting; minimal dependencies | Requires ongoing maintenance; rotation/retention must be hand-built; easy to introduce inconsistencies | Highly regulated environments that forbid third-party modules or demand strict formatting rules |
| Windows Event Log (`Write-EventLog`) | Native Windows experience; integrates with Event Viewer, SIEM, and existing monitoring; built-in retention policies | Windows-only; needs source registration (often elevation); limited structured payloads | Windows services, scheduled tasks, or compliance workloads that mandate Event Viewer visibility |
| Serilog / PSSerilog | Rich structured logging; huge ecosystem of sinks (Seq, Elasticsearch, Datadog, Splunk, etc.); aligns with .NET application logging | Additional dependency; heavier configuration; some sinks require .NET runtime on host | Hybrid solutions that combine PowerShell with .NET services or where a Serilog-based observability pipeline already exists |
| Log4Posh / NLog wrappers | Familiar for teams using Log4j/NLog; flexible configuration; supports multiple appenders | Smaller communities; slower release cadence; more manual setup than PSFramework | When existing infrastructure standardises on these frameworks or migration effort must be minimised |
| Cloud-native cmdlets (Azure Monitor, AWS CloudWatch, Google Cloud Logging) | Direct integration with managed logging platforms; simplifies forwarding | Cloud-platform specific; often incurs additional costs; limited offline capability | Cloud automation that must emit logs straight into the provider’s monitoring stack |

### When to choose an alternative

- **Minimal scripts**: Use the built-in streams when persistence is unnecessary and output is consumed immediately by operators or CI logs.
- **Strict dependency policies**: Implement a custom logger (or reuse an existing internal one) when external modules such as PSFramework cannot be deployed.
- **Windows compliance workloads**: Write to the Windows Event Log so operations and security teams can rely on familiar tooling.
- **Unified observability**: Adopt Serilog, Log4Posh, or cloud-native sinks when PowerShell is only one part of a larger system that already uses those formats.
- **Hybrid approach**: Combine PSFramework with other outputs (e.g., PSFramework for file + console, plus `Write-EventLog` for critical events) when multiple stakeholders need the data in different systems.

## Best Practices

### 1. Initialize Once

```powershell
# ✅ Good - Initialize in module or script start
if (-not (Get-PSFConfig -FullName 'PSFramework.Logging.MinimumLevel' -ErrorAction SilentlyContinue)) {
    Initialize-Logging -ModuleName "MyModule"
}

# ❌ Bad - Initialize in every function
function Get-Something {
    Initialize-Logging  # Don't do this
}
```

### 2. Use Appropriate Log Levels

```powershell
# ✅ Good - Use correct levels
Write-Log -Message "Operation started" -Level Info
Write-Log -Message "Retrieved 100 records" -Level Verbose
Write-Log -Message "Connection lost, retrying" -Level Warning
Write-Log -Message "Failed to process" -Level Error

# ❌ Bad - Everything is Info
Write-Log -Message "Retrieved 100 records" -Level Info  # Should be Verbose
Write-Log -Message "CRITICAL ERROR" -Level Info  # Should be Critical
```

### 3. Include Context

```powershell
# ✅ Good - Rich context
Write-Log -Message "User login" -Level Info -Context @{
    UserName = $userName
    Source = $sourceIP
    LoginTime = Get-Date
}

# ❌ Bad - No context
Write-Log -Message "User login" -Level Info
```

### 4. Don't Log Sensitive Information

```powershell
# ❌ Bad - Logging passwords
Write-Log -Message "Login attempt" -Context @{
    UserName = $userName
    Password = $password  # Don't do this!
}

# ✅ Good - Sanitize sensitive data
Write-Log -Message "Login attempt" -Context @{
    UserName = $userName
    PasswordLength = $password.Length
}
```

### 5. Use Tags for Categorization

```powershell
# ✅ Good - Use tags
Write-Log -Message "Database query" -Tag "Database", "Performance"
Write-Log -Message "API call" -Tag "API", "External"

# Later filter by tag
Get-PSFMessage -Tag "Database"
```

### 6. Log Exceptions Properly

```powershell
# ✅ Good - Include exception
try {
    DoSomething
}
catch {
    Write-Log -Message "Operation failed" -Level Error -Exception $_.Exception
}

# ❌ Bad - Just the message
try {
    DoSomething
}
catch {
    Write-Log -Message "Operation failed" -Level Error  # Missing exception details
}
```

### 7. Performance Considerations

```powershell
# ✅ Good - Log summaries for large loops
for ($i = 0; $i -lt 10000; $i++) {
    ProcessItem $i

    # Log every 1000 items
    if ($i % 1000 -eq 0) {
        Write-Log -Message "Progress update" -Context @{ Processed = $i }
    }
}

# ❌ Bad - Log every iteration
for ($i = 0; $i -lt 10000; $i++) {
    ProcessItem $i
    Write-Log -Message "Processing item $i"  # 10,000 log entries!
}
```

---

## Troubleshooting

### Check if Logging is Configured

```powershell
# Check PSFramework configuration
Get-PSFConfig -FullName 'PSFramework.Logging.MinimumLevel'

# Check logging providers
Get-PSFLoggingProvider

# View recent messages
Get-PSFMessage -Last 20
```

### Enable Debug Logging

```powershell
# Temporarily enable debug logging
Set-GDSLogging -ModuleName "MyModule" -MinimumLevel "Debug"

# Run your code
Test-MyFunction

# View debug messages
Get-PSFMessage -Level Debug
```

### Find Log Files

```powershell
if (-not $env:GDS_LOG_DIR) {
    throw "GDS_LOG_DIR environment variable is not configured."
}

# Default log location
$logPath = $env:GDS_LOG_DIR
Get-ChildItem $logPath

# Open log directory
if ($IsWindows) {
    Start-Process explorer.exe $logPath
}
else {
    ls $logPath
}
```

### Test Logging

```powershell
# Quick test
Write-Log -Message "Test message" -Level Info
Get-PSFMessage -Last 1
```

---

## Complete Examples

### Example 1: Simple Script

```powershell
# SimpleScript.ps1
Import-Module GDS.Common

# Initialize logging
Initialize-Logging -ModuleName "SimpleScript"

# Start
Write-Log -Message "Script started" -Level Info

try {
    # Do work
    $users = Get-ADUser -Filter *
    Write-Log -Message "Retrieved users" -Level Info -Context @{
        Count = $users.Count
    }

    # Process users
    foreach ($user in $users) {
        Write-Log -Message "Processing user" -Level Verbose -Context @{
            UserName = $user.SamAccountName
        }
    }

    Write-Log -Message "Script completed successfully" -Level Info
}
catch {
    Write-Log -Message "Script failed" -Level Error -Exception $_.Exception
    throw
}
```

### Example 2: Module Function

```powershell
# MyModule.psm1

# Initialize at module load
Initialize-Logging -ModuleName "MyModule"

function Get-UserReport {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Department
    )

    Write-Log -Message "Generating user report" -Level Info -Context @{
        Department = $Department
    } -Tag "Report"

    $startTime = Get-Date

    try {
        # Get users
        Write-Log -Message "Retrieving users" -Level Verbose -Tag "Report"
        $users = Get-ADUser -Filter "Department -eq '$Department'" -Properties *

        # Process data
        Write-Log -Message "Processing user data" -Level Verbose -Tag "Report"
        $report = $users | Select-Object Name, Title, EmailAddress

        $duration = (Get-Date) - $startTime

        Write-Log -Message "Report generated successfully" -Level Info -Context @{
            Department = $Department
            UserCount = $report.Count
            DurationMs = $duration.TotalMilliseconds
        } -Tag "Report", "Success"

        return $report
    }
    catch {
        $duration = (Get-Date) - $startTime

        Write-Log -Message "Failed to generate report" -Level Error -Exception $_.Exception -Context @{
            Department = $Department
            DurationMs = $duration.TotalMilliseconds
        } -Tag "Report", "Error"

        throw
    }
}

Export-ModuleMember -Function Get-UserReport
```

### Example 3: Advanced Module with Configuration

```powershell
# AdvancedModule.psm1

# Module-level initialization
$script:ModuleConfig = @{
    LogLevel = 'Info'
    EnableEventLog = $IsWindows
}

function Initialize-MyModule {
    param(
        [string]$LogLevel = 'Info',
        [switch]$EnableEventLog
    )

    # Update config
    $script:ModuleConfig.LogLevel = $LogLevel
    $script:ModuleConfig.EnableEventLog = $EnableEventLog

    # Configure logging
    Set-GDSLogging -ModuleName "AdvancedModule" `
        -MinimumLevel $LogLevel `
        -EnableEventLog:$EnableEventLog

    Write-Log -Message "Module initialized" -Level Info -Context @{
        LogLevel = $LogLevel
        EventLogEnabled = $EnableEventLog
    }
}

function Invoke-ComplexOperation {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$OperationName,

        [Parameter(Mandatory)]
        [hashtable]$Parameters
    )

    $operationId = [Guid]::NewGuid().ToString()
    $startTime = Get-Date

    Write-Log -Message "Operation started" -Level Info -Context @{
        OperationId = $operationId
        OperationName = $OperationName
        ParameterCount = $Parameters.Count
    } -Tag "Operation", "Start"

    try {
        # Validate
        Write-Log -Message "Validating parameters" -Level Verbose -Context @{
            OperationId = $operationId
        } -Tag "Operation", "Validation"

        if (-not (Test-Parameters $Parameters)) {
            throw "Invalid parameters"
        }

        # Execute
        Write-Log -Message "Executing operation" -Level Info -Context @{
            OperationId = $operationId
        } -Tag "Operation", "Execute"

        $result = Execute-Operation -Name $OperationName -Parameters $Parameters

        # Complete
        $duration = (Get-Date) - $startTime

        Write-Log -Message "Operation completed" -Level Info -Context @{
            OperationId = $operationId
            OperationName = $OperationName
            DurationMs = $duration.TotalMilliseconds
            ResultCount = $result.Count
            Status = "Success"
        } -Tag "Operation", "Complete"

        return $result
    }
    catch {
        $duration = (Get-Date) - $startTime

        Write-Log -Message "Operation failed" -Level Error -Exception $_.Exception -Context @{
            OperationId = $operationId
            OperationName = $OperationName
            DurationMs = $duration.TotalMilliseconds
            Status = "Failed"
        } -Tag "Operation", "Error"

        throw
    }
}

# Initialize on module import
Initialize-MyModule

Export-ModuleMember -Function Initialize-MyModule, Invoke-ComplexOperation
```

---

## Summary

### Quick Reference

```powershell
# Initialize (once)
Initialize-Logging -ModuleName "YourModule"

# Basic logging
Write-Log -Message "Message" -Level Info

# With context
Write-Log -Message "Message" -Level Info -Context @{Key="Value"}

# With exception
Write-Log -Message "Error" -Level Error -Exception $_.Exception

# With tags
Write-Log -Message "Message" -Level Info -Tag "Category"

# Configure
Set-GDSLogging -ModuleName "YourModule" -MinimumLevel "Debug"

# Query
Get-PSFMessage -Last 10
```

### Remember

1. ✅ Initialize logging once at module/script start
2. ✅ Use appropriate log levels
3. ✅ Include context for rich logging
4. ✅ Log exceptions with `-Exception` parameter
5. ✅ Use tags for categorization
6. ❌ Don't log sensitive information
7. ❌ Don't over-log (performance impact)

---

## Additional Resources

- [PSFramework Documentation](https://psframework.org/documentation/documents/psframework/logging.html)
- [GDS.Common Migration Guide](./PSFRAMEWORK_MIGRATION.md)
- [Cross-Platform Support](./PSFRAMEWORK_CROSS_PLATFORM.md)
- [Best Practices Analysis](./POWERSHELL_LOGGING_BEST_PRACTICES.md)

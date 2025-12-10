# Part 5: PowerShell Logging

## What You'll Learn

In this part, you'll learn:

- Structured logging best practices for PowerShell
- Correct use of PowerShell streams
- Logging framework options (PSFramework, Serilog, custom)
- Capturing third-party module output
- Correlation IDs and trace context
- Kafka integration patterns

---

## Why Structured Logging?

Traditional text logs:

```
2025-01-15 10:30:45 ERROR - Database connection failed: timeout after 30s
```

Structured JSON logs:

```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "Error",
  "message": "Database connection failed",
  "correlationId": "abc-123",
  "context": {
    "sqlInstance": "prod-db-01",
    "database": "CustomerDB",
    "errorType": "ConnectionTimeout",
    "timeoutSeconds": 30
  }
}
```

### Benefits of Structured Logging

| Benefit | Description |
|---------|-------------|
| **Searchable** | Query by any field |
| **Parseable** | Machines can process automatically |
| **Correlatable** | Link logs across services |
| **Rich Context** | Include relevant metadata |
| **Consistent** | Standard format across scripts |

---

## PowerShell Streams

PowerShell has six output streams. Understanding them is crucial for proper logging:

| Stream | Number | Cmdlet | Use Case |
|--------|--------|--------|----------|
| **Output** | 1 | (Return value) | Function return data |
| **Error** | 2 | `Write-Error` | Errors and exceptions |
| **Warning** | 3 | `Write-Warning` | Unexpected but handled conditions |
| **Verbose** | 4 | `Write-Verbose` | Detailed operational info |
| **Debug** | 5 | `Write-Debug` | Developer diagnostics |
| **Information** | 6 | `Write-Information` | General informational messages |

### Best Practices

```powershell
# ❌ DON'T use Write-Host for logging (bypasses streams)
Write-Host "Processing started"

# ✅ DO use Write-Information
Write-Information "Processing started" -InformationAction Continue

# ✅ DO use Write-Verbose for detailed operations
Write-Verbose "Connecting to database $SqlInstance"

# ✅ DO use Write-Warning for unexpected but handled conditions
Write-Warning "Retry attempt 2 of 3 after transient failure"

# ✅ DO use Write-Error for failures
Write-Error "Database connection failed: $($_.Exception.Message)"
```

### Enabling Streams

By default, Verbose, Debug, and Information streams are suppressed:

```powershell
# Enable for current session
$VerbosePreference = 'Continue'
$InformationPreference = 'Continue'

# Or per-command
Write-Information "Message" -InformationAction Continue
```

---

## Log Levels

| Level | When to Use | Production Default |
|-------|-------------|-------------------|
| **Debug** | Developer diagnostics, variable values | Disabled |
| **Verbose** | Detailed operation steps | Disabled |
| **Information** | Normal operations, business events | Enabled |
| **Warning** | Unexpected but handled conditions | Enabled |
| **Error** | Failures requiring attention | Enabled |
| **Critical** | System-threatening failures | Enabled |

### Level Decision Guide

```powershell
# DEBUG: Variable values, loop iterations
Write-Debug "Processing item $i of $total with value: $item"

# VERBOSE: Step-by-step operations
Write-Verbose "Connecting to SQL Server $SqlInstance"
Write-Verbose "Executing query: $Query"
Write-Verbose "Retrieved $($results.Count) rows"

# INFORMATION: Normal business events
Write-Information "Backup completed successfully for database $Database"

# WARNING: Degraded operation, retries
Write-Warning "Primary connection failed, using secondary endpoint"
Write-Warning "Deprecated API called, will be removed in v3.0"

# ERROR: Operation failed
Write-Error "Failed to create backup: disk space exhausted"

# CRITICAL: System-level failure (usually throw)
throw "Configuration file not found - cannot start application"
```

---

## Structured Logging Implementation

### Basic JSON Logger

```powershell
```powershell
function Write-StructuredLog {
    Import-Module GDS.Logging
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [ValidateSet('Debug', 'Verbose', 'Information', 'Warning', 'Error', 'Critical')]
        [string]$Level,

        [Parameter(Mandatory)]
        [string]$Message,

        [hashtable]$Context = @{},

        [string]$CorrelationId,

        [string[]]$Tags = @()
    )

    $logEntry = [ordered]@{
        timestamp     = (Get-Date).ToUniversalTime().ToString('o')
        level         = $Level
        message       = $Message
        correlationId = $CorrelationId
        tags          = $Tags
        context       = $Context
        source        = @{
            script   = $MyInvocation.ScriptName
            function = (Get-PSCallStack)[1].FunctionName
            line     = $MyInvocation.ScriptLineNumber
        }
    }

    $json = $logEntry | ConvertTo-Json -Compress -Depth 5

    # Output based on level
    switch ($Level) {
        'Debug'       { Write-Debug $json }
        'Verbose'     { Write-Verbose $json }
        'Information' { Write-Information $json -InformationAction Continue }
        'Warning'     { Write-Warning $json }
        'Error'       { Write-Error $json }
        'Critical'    { Write-Error $json }
    }

    return $json
}

# Usage
Write-StructuredLog -Level Information -Message "Backup completed" -Context @{
    SqlInstance = "prod-db-01"
    Database    = "CustomerDB"
    DurationMs  = 5432
    BackupSizeMB = 2048
} -CorrelationId "abc-123" -Tags @("backup", "production")
```

### Output Example

```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "Information",
  "message": "Backup completed",
  "correlationId": "abc-123",
  "tags": ["backup", "production"],
  "context": {
    "SqlInstance": "prod-db-01",
    "Database": "CustomerDB",
    "DurationMs": 5432,
    "BackupSizeMB": 2048
  },
  "source": {
    "script": "/scripts/Backup-Database.ps1",
    "function": "Invoke-DatabaseBackup",
    "line": 45
  }
}
```

---

## Logging Framework Options

### Option A: PSFramework

PSFramework is a mature PowerShell-native logging framework:

```powershell
# Install
Install-Module PSFramework -Scope CurrentUser

# Configure
Set-PSFLoggingProvider -Name logfile -Enabled $true -FilePath "/var/log/myapp/myapp-{0:yyyy-MM-dd}.json"

# Use message functions
Write-PSFMessage -Level Important -Message "Batch completed" -Tag "ETL" -Data @{
    RowCount = 150
    DurationMs = 234
}

# Automatic rotation and retention built-in
```

**Strengths**:

- PowerShell-native
- Built-in rotation/retention
- Message proxies for stream capture
- Cross-platform support

### Option B: Serilog via PoShLog

Use the .NET Serilog library from PowerShell:

```powershell
# Install
Install-Module PoShLog -Scope CurrentUser
Import-Module PoShLog

# Configure
New-Logger |
    Set-MinimumLevel -Value Information |
    Add-ConsoleSink |
    Add-FileSink -Path "/var/log/myapp/myapp-.log" -RollingInterval Day |
    Start-Logger

# Write logs
Write-Log -Level Information -Message "Batch completed" -Properties @{
    RowCount   = 150
    DurationMs = 234
} -Tags "ETL", "Batch"

# Close when done
Close-Logger
```

**Strengths**:

- Rich sink ecosystem
- Advanced enrichment
- .NET ecosystem integration

### Option C: Custom Lightweight Logger

When you need minimal dependencies:

```powershell
class StructuredLogger {
    [string]$LogPath
    [string]$MinLevel
    [string]$CorrelationId
    hidden [hashtable]$LevelPriority = @{
        Debug = 0; Verbose = 1; Information = 2; Warning = 3; Error = 4; Critical = 5
    }

    StructuredLogger([string]$logPath, [string]$minLevel) {
        $this.LogPath = $logPath
        $this.MinLevel = $minLevel
        $this.CorrelationId = [Guid]::NewGuid().ToString()
    }

    [void] Log([string]$level, [string]$message, [hashtable]$context) {
        if ($this.LevelPriority[$level] -lt $this.LevelPriority[$this.MinLevel]) {
            return
        }

        $entry = @{
            timestamp     = (Get-Date).ToUniversalTime().ToString('o')
            level         = $level
            message       = $message
            correlationId = $this.CorrelationId
            context       = $context
        } | ConvertTo-Json -Compress

        Add-Content -Path $this.LogPath -Value $entry -Encoding UTF8
    }
}

# Usage
$logger = [StructuredLogger]::new("/var/log/app.json", "Information")
$logger.Log("Information", "Operation completed", @{ Duration = 100 })
```

---

## Correlation IDs

Correlation IDs link related log entries across operations:

```powershell
function Invoke-DataPipeline {
    param([string]$SourcePath)

    # Generate correlation ID for this operation
    $correlationId = [Guid]::NewGuid().ToString()

    Write-StructuredLog -Level Information -Message "Pipeline started" -CorrelationId $correlationId -Context @{
        SourcePath = $SourcePath
    }

    try {
        # Pass correlation ID to sub-operations
        $data = Import-Data -Path $SourcePath -CorrelationId $correlationId

        Write-StructuredLog -Level Information -Message "Data imported" -CorrelationId $correlationId -Context @{
            RowCount = $data.Count
        }

        Transform-Data -Data $data -CorrelationId $correlationId
        Export-Data -Data $data -CorrelationId $correlationId

        Write-StructuredLog -Level Information -Message "Pipeline completed" -CorrelationId $correlationId

    } catch {
        Write-StructuredLog -Level Error -Message "Pipeline failed" -CorrelationId $correlationId -Context @{
            Error = $_.Exception.Message
            StackTrace = $_.ScriptStackTrace
        }
        throw
    }
}
```

### Trace Context for OpenTelemetry

For integration with distributed tracing:

```powershell
function Get-TraceContext {
    param([string]$ParentTraceId, [string]$ParentSpanId)

    $traceId = if ($ParentTraceId) { $ParentTraceId } else {
        [Guid]::NewGuid().ToString("N") + [Guid]::NewGuid().ToString("N").Substring(0, 16)
    }
    $spanId = [Guid]::NewGuid().ToString("N").Substring(0, 16)

    return @{
        TraceId = $traceId
        SpanId = $spanId
        ParentSpanId = $ParentSpanId
        TraceParent = "00-$traceId-$spanId-01"
    }
}

# Usage
$trace = Get-TraceContext
Write-StructuredLog -Level Information -Message "Operation started" -Context @{
    TraceId = $trace.TraceId
    SpanId = $trace.SpanId
}

# Include in HTTP calls
Invoke-RestMethod -Uri $apiUrl -Headers @{
    "traceparent" = $trace.TraceParent
}
```

---

## Capturing Third-Party Module Output

When using modules like dbatools, capture their output:

### Wrapper Pattern

```powershell
function Invoke-DbaQueryWithLogging {
    param(
        [string]$SqlInstance,
        [string]$Database,
        [string]$Query,
        [string]$CorrelationId
    )

    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

    Write-StructuredLog -Level Verbose -Message "Executing query" -CorrelationId $CorrelationId -Context @{
        SqlInstance = $SqlInstance
        Database = $Database
        QueryLength = $Query.Length
    }

    try {
        $result = Invoke-DbaQuery -SqlInstance $SqlInstance -Database $Database -Query $Query

        $stopwatch.Stop()
        Write-StructuredLog -Level Information -Message "Query completed" -CorrelationId $CorrelationId -Context @{
            SqlInstance = $SqlInstance
            Database = $Database
            RowCount = $result.Count
            DurationMs = $stopwatch.ElapsedMilliseconds
        } -Tags @("dbatools", "success")

        return $result

    } catch {
        $stopwatch.Stop()
        Write-StructuredLog -Level Error -Message "Query failed" -CorrelationId $CorrelationId -Context @{
            SqlInstance = $SqlInstance
            Database = $Database
            DurationMs = $stopwatch.ElapsedMilliseconds
            Error = $_.Exception.Message
            StackTrace = $_.ScriptStackTrace
        } -Tags @("dbatools", "error")

        throw
    }
}
```

### Stream Capture Pattern

```powershell
function Invoke-DbaWithStreamCapture {
    param([scriptblock]$ScriptBlock, [string]$CorrelationId)

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

            Write-StructuredLog -Level $level -Message $item.ToString() -CorrelationId $CorrelationId -Tags @("dbatools", "captured")
        }

    } finally {
        # Restore preferences
        $VerbosePreference = $savedVerbose
        $WarningPreference = $savedWarning
        $InformationPreference = $savedInfo
    }
}

# Usage
Invoke-DbaWithStreamCapture -CorrelationId $correlationId -ScriptBlock {
    Invoke-DbaDbUpgrade -SqlInstance $SqlInstance -Database $Database
}
```

---

## Kafka Integration

### Out-of-Process (Recommended)

Write JSON to files, ship with Fluent Bit/Filebeat:

```powershell
# PowerShell writes JSON to file
$logPath = "/var/log/myapp/app.json"
Write-StructuredLog -Level Information -Message "Event" -Context @{} |
    Add-Content -Path $logPath

# Fluent Bit ships to Kafka (fluent-bit.conf)
# [INPUT]
#     Name tail
#     Path /var/log/myapp/*.json
#     Parser json
#
# [OUTPUT]
#     Name kafka
#     Brokers kafka:9092
#     Topics myapp-logs
```

### In-Process Producer

For direct Kafka integration:

```powershell
# Using .NET Confluent.Kafka client
Add-Type -Path "Confluent.Kafka.dll"

$config = [Confluent.Kafka.ProducerConfig]::new()
$config.BootstrapServers = "kafka:9092"

$producer = [Confluent.Kafka.ProducerBuilder[string,string]]::new($config).Build()

function Send-LogToKafka {
    param([string]$Topic, [hashtable]$LogEntry)

    $key = $LogEntry.correlationId
    $value = $LogEntry | ConvertTo-Json -Compress

    $message = [Confluent.Kafka.Message[string,string]]::new()
    $message.Key = $key
    $message.Value = $value

    $producer.ProduceAsync($Topic, $message).Wait()
}
```

---

## Redacting Sensitive Data

Never log passwords, tokens, or PII:

```powershell
function Get-RedactedContext {
    param([hashtable]$Context)

    $redacted = @{}

    foreach ($key in $Context.Keys) {
        $value = $Context[$key]

        $redacted[$key] = switch -Regex ($key) {
            'password|secret|token|apikey' {
                "[REDACTED length=$($value.Length)]"
            }
            'connectionstring' {
                ($value -split ';')[0] + ";[REDACTED]"
            }
            'email' {
                $parts = $value -split '@'
                "$($parts[0].Substring(0,2))***@$($parts[1])"
            }
            default { $value }
        }
    }

    return $redacted
}

# Usage
$safeContext = Get-RedactedContext -Context @{
    SqlInstance = "prod-db-01"
    ConnectionString = "Server=prod-db-01;Password=secret123"
    ApiToken = "sk_live_abc123xyz"
    Email = "user@example.com"
}

# Result:
# SqlInstance: prod-db-01
# ConnectionString: Server=prod-db-01;[REDACTED]
# ApiToken: [REDACTED length=15]
# Email: us***@example.com
```

---

## Performance Considerations

### Sampling High-Frequency Operations

```powershell
$script:logCounter = 0
$script:sampleRate = 100  # Log 1 in 100

function Write-SampledLog {
    param($Level, $Message, $Context)

    $script:logCounter++

    # Always log warnings and errors
    if ($Level -in @('Warning', 'Error', 'Critical')) {
        Write-StructuredLog -Level $Level -Message $Message -Context $Context
        return
    }

    # Sample other levels
    if ($script:logCounter % $script:sampleRate -eq 0) {
        $Context['_sampled'] = $true
        $Context['_sampleRate'] = $script:sampleRate
        Write-StructuredLog -Level $Level -Message $Message -Context $Context
    }
}
```

### Async File Writing

```powershell
# Use background job for non-blocking writes
$logQueue = [System.Collections.Concurrent.ConcurrentQueue[string]]::new()

# Background writer
$writerJob = Start-ThreadJob -ScriptBlock {
    param($queue, $logPath)
    while ($true) {
        $entry = $null
        while ($queue.TryDequeue([ref]$entry)) {
            Add-Content -Path $logPath -Value $entry -Encoding UTF8
        }
        Start-Sleep -Milliseconds 100
    }
} -ArgumentList $logQueue, "/var/log/app.json"

# Logging function
function Write-AsyncLog {
    param($LogEntry)
    $logQueue.Enqueue(($LogEntry | ConvertTo-Json -Compress))
}
```

---

## Summary

| Topic | Key Points |
|-------|------------|
| **Structured Logging** | JSON format, searchable, correlatable |
| **PowerShell Streams** | Use correct streams for each purpose |
| **Log Levels** | Debug → Verbose → Info → Warning → Error → Critical |
| **Correlation IDs** | Link related operations across logs |
| **Third-Party Capture** | Wrapper pattern or stream capture |
| **Kafka Integration** | Prefer out-of-process shipping |
| **Security** | Never log sensitive data |

### Key Takeaways

1. **Always use structured (JSON) logging**
2. **Include correlation IDs** for traceability
3. **Use appropriate log levels** consistently
4. **Wrap third-party modules** to capture output
5. **Redact sensitive data** before logging
6. **Consider performance** at high volumes

---

## What's Next?

Part 6 will cover **Python Integration** with OpenTelemetry for instrumentation and structured logging.

[Continue to Part 6: Python Integration →](06_PYTHON_INTEGRATION.md)

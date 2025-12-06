# Exercise 3: PowerShell Structured Logging

## Objective

Implement structured JSON logging in PowerShell with:

- Correlation IDs for request tracing
- Trace context for OpenTelemetry integration
- Third-party module output capture

## Prerequisites

- PowerShell 7+
- Understanding of PowerShell streams

---

## Step 1: Create the Logger Module

Create `StructuredLogger.psm1`:

```powershell
# StructuredLogger.psm1 - Structured JSON Logging for PowerShell

class StructuredLogger {
    [string]$LogPath
    [string]$MinLevel
    [string]$CorrelationId
    [string]$TraceId
    [string]$SpanId
    hidden [hashtable]$LevelPriority = @{
        Debug       = 0
        Verbose     = 1
        Information = 2
        Warning     = 3
        Error       = 4
        Critical    = 5
    }

    StructuredLogger([string]$logPath, [string]$minLevel) {
        $this.LogPath = $logPath
        $this.MinLevel = $minLevel
        $this.CorrelationId = [Guid]::NewGuid().ToString()
        $this.NewTraceContext()
    }

    [void] NewTraceContext() {
        $this.TraceId = [Guid]::NewGuid().ToString("N") + [Guid]::NewGuid().ToString("N").Substring(0, 16)
        $this.SpanId = [Guid]::NewGuid().ToString("N").Substring(0, 16)
    }

    [string] GetTraceParent() {
        return "00-$($this.TraceId)-$($this.SpanId)-01"
    }

    [void] Log([string]$level, [string]$message, [hashtable]$context) {
        if ($this.LevelPriority[$level] -lt $this.LevelPriority[$this.MinLevel]) {
            return
        }

        $entry = [ordered]@{
            timestamp     = (Get-Date).ToUniversalTime().ToString('o')
            level         = $level
            message       = $message
            correlationId = $this.CorrelationId
            traceId       = $this.TraceId
            spanId        = $this.SpanId
            context       = $context
        }

        $json = $entry | ConvertTo-Json -Compress -Depth 5

        # Write to file
        Add-Content -Path $this.LogPath -Value $json -Encoding UTF8

        # Also output to console based on level
        switch ($level) {
            'Debug'       { Write-Debug $json }
            'Verbose'     { Write-Verbose $json }
            'Information' { Write-Information $json -InformationAction Continue }
            'Warning'     { Write-Warning $json }
            'Error'       { Write-Error $json }
            'Critical'    { Write-Error $json }
        }
    }

    [void] Debug([string]$message, [hashtable]$context = @{}) {
        $this.Log('Debug', $message, $context)
    }

    [void] Verbose([string]$message, [hashtable]$context = @{}) {
        $this.Log('Verbose', $message, $context)
    }

    [void] Info([string]$message, [hashtable]$context = @{}) {
        $this.Log('Information', $message, $context)
    }

    [void] Warning([string]$message, [hashtable]$context = @{}) {
        $this.Log('Warning', $message, $context)
    }

    [void] Error([string]$message, [hashtable]$context = @{}) {
        $this.Log('Error', $message, $context)
    }

    [void] Critical([string]$message, [hashtable]$context = @{}) {
        $this.Log('Critical', $message, $context)
    }
}

# Factory function
function New-StructuredLogger {
    param(
        [Parameter(Mandatory)]
        [string]$LogPath,

        [ValidateSet('Debug', 'Verbose', 'Information', 'Warning', 'Error', 'Critical')]
        [string]$MinLevel = 'Information'
    )

    # Ensure log directory exists
    $dir = Split-Path -Parent $LogPath
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    return [StructuredLogger]::new($LogPath, $MinLevel)
}

# Sensitive data redaction
function Get-RedactedContext {
    param([hashtable]$Context)

    $sensitiveKeys = @('password', 'secret', 'token', 'apikey', 'credential', 'connectionstring')
    $redacted = @{}

    foreach ($key in $Context.Keys) {
        $value = $Context[$key]
        $keyLower = $key.ToLower()

        $isSensitive = $sensitiveKeys | Where-Object { $keyLower -like "*$_*" }

        if ($isSensitive) {
            $redacted[$key] = "[REDACTED length=$($value.Length)]"
        }
        elseif ($value -is [hashtable]) {
            $redacted[$key] = Get-RedactedContext -Context $value
        }
        else {
            $redacted[$key] = $value
        }
    }

    return $redacted
}

Export-ModuleMember -Function New-StructuredLogger, Get-RedactedContext
```

---

## Step 2: Create a Test Script

Create `Test-Logging.ps1`:

```powershell
#!/usr/bin/env pwsh
# Test-Logging.ps1 - Demonstrate structured logging

# Import the module
$modulePath = Join-Path $PSScriptRoot "StructuredLogger.psm1"
Import-Module $modulePath -Force

# Create logger
$logPath = Join-Path $PSScriptRoot "logs/app.json"
$logger = New-StructuredLogger -LogPath $logPath -MinLevel 'Debug'

Write-Host "Correlation ID: $($logger.CorrelationId)"
Write-Host "Trace ID: $($logger.TraceId)"
Write-Host "Logs written to: $logPath"
Write-Host ""

# ============================================
# Test: Basic Logging
# ============================================

$logger.Info("Application started", @{
    Version = "1.0.0"
    Environment = "Development"
})

$logger.Debug("Debug message - detailed diagnostics", @{
    Variable = "value"
})

$logger.Verbose("Verbose message - operational details")

$logger.Warning("Warning message - unexpected condition", @{
    RetryCount = 2
    MaxRetries = 3
})

$logger.Error("Error message - operation failed", @{
    ErrorType = "TimeoutException"
    Message = "Connection timed out after 30s"
})

# ============================================
# Test: Context Redaction
# ============================================

Write-Host "`nTesting sensitive data redaction..."

$sensitiveContext = @{
    SqlInstance = "prod-db-01"
    ConnectionString = "Server=prod-db-01;Password=secret123"
    ApiToken = "sk_live_abc123xyz789"
    NormalField = "This is fine"
}

$redacted = Get-RedactedContext -Context $sensitiveContext
$logger.Info("Connection attempt with redacted credentials", $redacted)

# ============================================
# Test: HTTP Call with Trace Context
# ============================================

Write-Host "`nMaking HTTP call with trace context..."

$traceParent = $logger.GetTraceParent()
$logger.Info("Making external API call", @{
    Url = "https://httpbin.org/headers"
    TraceParent = $traceParent
})

try {
    $response = Invoke-RestMethod -Uri "https://httpbin.org/headers" -Headers @{
        "traceparent" = $traceParent
    }

    $logger.Info("API call completed", @{
        StatusCode = 200
        ReturnedHeaders = ($response.headers | ConvertTo-Json -Compress)
    })
}
catch {
    $logger.Error("API call failed", @{
        Error = $_.Exception.Message
    })
}

# ============================================
# Test: Simulated Workflow
# ============================================

Write-Host "`nSimulating database operation workflow..."

function Invoke-DatabaseOperation {
    param(
        [StructuredLogger]$Logger,
        [string]$SqlInstance,
        [string]$Database,
        [string]$Query
    )

    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

    $Logger.Info("Starting database operation", @{
        SqlInstance = $SqlInstance
        Database = $Database
        QueryLength = $Query.Length
    })

    try {
        # Simulate query execution
        Start-Sleep -Milliseconds 150

        $stopwatch.Stop()
        $Logger.Info("Database operation completed", @{
            SqlInstance = $SqlInstance
            Database = $Database
            DurationMs = $stopwatch.ElapsedMilliseconds
            RowCount = 42  # Simulated
        })

        return 42
    }
    catch {
        $stopwatch.Stop()
        $Logger.Error("Database operation failed", @{
            SqlInstance = $SqlInstance
            Database = $Database
            DurationMs = $stopwatch.ElapsedMilliseconds
            Error = $_.Exception.Message
        })
        throw
    }
}

$result = Invoke-DatabaseOperation -Logger $logger `
    -SqlInstance "prod-db-01" `
    -Database "CustomerDB" `
    -Query "SELECT * FROM Customers WHERE Status = 'Active'"

Write-Host "Query returned $result rows"

# ============================================
# View Log Output
# ============================================

Write-Host "`n--- Log File Contents ---"
Get-Content $logPath | ForEach-Object {
    $_ | ConvertFrom-Json | ConvertTo-Json -Depth 5
}

Write-Host "`n--- Summary ---"
Write-Host "Log entries written: $((Get-Content $logPath).Count)"
Write-Host "Correlation ID preserved across all entries"
```

---

## Step 3: Run the Test Script

```powershell
./Test-Logging.ps1
```

---

## Step 4: Examine the Output

Check the generated `logs/app.json`:

```json
{"timestamp":"2025-01-15T10:30:45.123Z","level":"Information","message":"Application started","correlationId":"abc-123","traceId":"...","spanId":"...","context":{"Version":"1.0.0","Environment":"Development"}}
{"timestamp":"2025-01-15T10:30:45.130Z","level":"Warning","message":"Warning message - unexpected condition","correlationId":"abc-123","traceId":"...","spanId":"...","context":{"RetryCount":2,"MaxRetries":3}}
```

Notice:

- All entries share the same `correlationId`
- Timestamps are in UTC ISO-8601 format
- Context is properly nested
- Sensitive data is redacted

---

## Step 5: Third-Party Module Capture

Create `Invoke-DbaWithLogging.ps1`:

```powershell
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
```

---

## Verification Checklist

- [ ] Logger creates JSON log files
- [ ] Correlation ID is consistent across log entries
- [ ] Trace context (traceId, spanId) is included
- [ ] Sensitive data is properly redacted
- [ ] HTTP calls include traceparent header
- [ ] Third-party module output is captured

---

## Challenge Tasks

1. Add log rotation (create new file each day)
2. Implement async file writing using runspaces
3. Add ability to send logs to Kafka
4. Create a log reader that formats JSON for console

---

## Next Steps

Move to [Exercise 4: Create Alerts](04_create_alerts.md)

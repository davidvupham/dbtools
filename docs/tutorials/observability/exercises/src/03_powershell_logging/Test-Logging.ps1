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

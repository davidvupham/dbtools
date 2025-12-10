# PowerShell Logging Architecture: Best Practices and Options

## Audience and Purpose

This document proposes a practical, cross‑platform logging architecture for PowerShell workloads. It outlines best practices, evaluates industry‑standard options, and presents patterns to satisfy the following requirements:

- Support both Windows and Linux
- Log output from third‑party modules (e.g., dbatools)
- Provide options to write to a file and/or stream to Kafka

Implementation details are intentionally high‑level to support design review and team alignment.

---

## Table of Contents

- [Audience and Purpose](#audience-and-purpose)
- [Requirements](#requirements)
- [Best Practices](#best-practices)
  - [1) Structured Logging](#1-structured-logging)
  - [2) Correct Use of PowerShell Streams](#2-correct-use-of-powershell-streams)
  - [3) Standard Log Levels and Filtering](#3-standard-log-levels-and-filtering)
    - [Log Level Decision Guide](#log-level-decision-guide)
  - [4) Correlation and Context](#4-correlation-and-context)
  - [5) Secure by Default](#5-secure-by-default)
    - [Redaction Patterns](#redaction-patterns)
  - [6) Rotation, Retention, and Size Management](#6-rotation-retention-and-size-management)
  - [7) Multi‑Target Outputs](#7-multitarget-outputs)
  - [8) Performance and Reliability](#8-performance-and-reliability)
    - [Performance Measurement](#performance-measurement)
- [Options and Approaches](#options-and-approaches)
  - [Option A: PSFramework‑Based Logging](#option-a-psframeworkbased-logging)
  - [Option B: Serilog via PSSerilog (Hybrid PowerShell/.NET)](#option-b-serilog-via-psserilog-hybrid-powershellnet)
    - [Typical Setup (using PoShLog as a Serilog wrapper)](#typical-setup-using-poshlog-as-a-serilog-wrapper)
    - [Kafka Integration with Serilog](#kafka-integration-with-serilog)
    - [Capturing Third‑Party Module Output (e.g., dbatools) with Serilog](#capturing-thirdparty-module-output-eg-dbatools-with-serilog)
    - [Complexity vs PSFramework](#complexity-vs-psframework)
  - [Option C: Native Streams + External Shippers (Fluent Bit, Filebeat, Vector)](#option-c-native-streams--external-shippers-fluent-bit-filebeat-vector)
  - [Option D: Custom Lightweight Logger](#option-d-custom-lightweight-logger)
  - [Option E: Platform‑Native Sinks (Windows Event Log / Syslog)](#option-e-platformnative-sinks-windows-event-log--syslog)
  - [Option F: Native PowerShell Transcription](#option-f-native-powershell-transcription)
    - [Basic Transcription Setup](#basic-transcription-setup)
    - [Transcription via Group Policy (Windows Enterprise)](#transcription-via-group-policy-windows-enterprise)
    - [Combining Transcription with Structured Logging](#combining-transcription-with-structured-logging)
    - [Transcript Management](#transcript-management)
- [Kafka Streaming Options](#kafka-streaming-options)
  - [1) Out‑of‑Process Shipping (Recommended Baseline)](#1-outofprocess-shipping-recommended-baseline)
  - [2) In‑Process Producer](#2-inprocess-producer)
- [OpenTelemetry Integration (OTLP)](#opentelemetry-integration-otlp)
  - [Why OpenTelemetry?](#why-opentelemetry)
  - [Integration Patterns](#integration-patterns)
    - [1) Via Serilog OTLP Sink](#1-via-serilog-otlp-sink)
    - [2) Via OpenTelemetry Collector + File/Stdout](#2-via-opentelemetry-collector--filestdout)
    - [3) Correlation with Distributed Traces](#3-correlation-with-distributed-traces)
  - [Recommendations](#recommendations)
- [Capturing Third‑Party Module Output (e.g., dbatools)](#capturing-thirdparty-module-output-eg-dbatools)
- [Data Model (Schema Guidance)](#data-model-schema-guidance)
- [Cross‑Platform Considerations](#crossplatform-considerations)
- [Non‑Functional Requirements](#nonfunctional-requirements)
- [Configuration Examples](#configuration-examples)
  - [Example 1: JSON Configuration File (PSFramework-style)](#example-1-json-configuration-file-psframework-style)
  - [Example 2: PowerShell Configuration Script](#example-2-powershell-configuration-script)
  - [Example 3: Environment-Specific Configuration](#example-3-environment-specific-configuration)
- [Querying and Analyzing Structured Logs](#querying-and-analyzing-structured-logs)
  - [Command-Line Querying with jq](#command-line-querying-with-jq)
  - [PowerShell JSON Log Analysis](#powershell-json-log-analysis)
  - [Grep Patterns for Quick Searches](#grep-patterns-for-quick-searches)
  - [Integration with Log Aggregation Platforms](#integration-with-log-aggregation-platforms)
- [Comparison Matrix (Summary)](#comparison-matrix-summary)
- [Recommended Path(s)](#recommended-paths)
- [High‑Level Implementation Plan (No Code)](#highlevel-implementation-plan-no-code)
- [Troubleshooting Common Logging Issues](#troubleshooting-common-logging-issues)
  - [Issue 1: Logs Not Appearing](#issue-1-logs-not-appearing)
  - [Issue 2: High Logging Overhead / Performance Degradation](#issue-2-high-logging-overhead--performance-degradation)
  - [Issue 3: Missing Third-Party Module Output](#issue-3-missing-third-party-module-output)
  - [Issue 4: Kafka Logs Not Arriving](#issue-4-kafka-logs-not-arriving)
  - [Issue 5: Log Files Growing Too Large](#issue-5-log-files-growing-too-large)
  - [Issue 6: Sensitive Data Appearing in Logs](#issue-6-sensitive-data-appearing-in-logs)
  - [Issue 7: Cannot Parse JSON Logs](#issue-7-cannot-parse-json-logs)
- [Open Questions (for Review)](#open-questions-for-review)
- [References](#references)
- [Document Revision History](#document-revision-history)

---

## Requirements

- Cross‑platform operation on PowerShell 7+ (Windows, Linux; macOS by extension)
- Structured, queryable logs (JSON)
- Appropriate log levels and filtering (Debug, Verbose, Info, Warning, Error, Critical)
- Ability to capture and unify third‑party module output into the same logs
- Options for durable file logs (rotation, retention) and streaming to Kafka
- Security controls (avoid sensitive data, access control to log files, optional redaction)
- Operational reliability under load (batching, backpressure handling, resilience to sink outages)

---

## Best Practices

### 1) Structured Logging

- Emit machine‑readable JSON with a consistent schema.
- Include timestamp (UTC/ISO‑8601), level, message, correlation/operation IDs, tags, function/script/module names, and a context bag for key/value pairs.

Example event (illustrative):

```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "Info",
  "message": "Processed batch",
  "correlationId": "c1b2f1a5-3d0a-49a6-9b43-5e1a31b2f8a7",
  "function": "Invoke-DataLoad",
  "module": "DataOps",
  "tags": ["ETL", "Batch"],
  "context": {
    "rowCount": 150,
    "durationMs": 234
  }
}
```

### 2) Correct Use of PowerShell Streams

- Prefer `Write-Information`, `Write-Verbose`, `Write-Warning`, `Write-Error` and handle them consistently.
- Avoid `Write-Host` for anything that should be logged or captured.

**Important**: When using `Write-Information`, ensure the information stream is enabled:

```powershell
$InformationPreference = 'Continue'  # Enable for current scope
# or
Write-Information "Message" -InformationAction Continue
```

PowerShell stream numbers for redirection:

- Stream 1: Standard output
- Stream 2: Error (ErrorRecord)
- Stream 3: Warning (WarningRecord)
- Stream 4: Verbose (VerboseRecord)
- Stream 5: Debug (DebugRecord)
- Stream 6: Information (InformationRecord)

### 3) Standard Log Levels and Filtering

- Support at least: Debug, Verbose, Info, Warning, Error, Critical.
- Provide a configurable minimum level (e.g., Info in production, Debug in development).

#### Log Level Decision Guide

| Level | When to Use | Examples | Production Default |
| --- | --- | --- | --- |
| **Debug** | Developer troubleshooting; detailed diagnostic information | Variable values, loop iterations, conditional branches | Disabled |
| **Verbose** | Detailed operational flow; step-by-step execution | "Starting process X", "Connecting to Y", "Processing item Z" | Disabled |
| **Information** | Normal operations; business events; successful completions | "Batch completed", "User logged in", "Report generated" | Enabled |
| **Warning** | Unexpected but handled conditions; degraded operation | "Retry attempt 2/3", "Fallback to default", "Deprecated API used" | Enabled |
| **Error** | Failures requiring attention; recoverable errors | "Query failed", "File not found", "Validation error" | Enabled |
| **Critical/Fatal** | System-threatening failures; unrecoverable errors | "Database unreachable", "Out of memory", "Configuration invalid" | Enabled |

**Sampling Guidance**: For operations exceeding 100 ops/sec, consider sampling Debug/Verbose logs (e.g., log 1 in 100) or aggregate metrics instead of individual events.

### 4) Correlation and Context

- Generate a correlation or operation ID at the workflow boundary; propagate it through nested calls.
- Standardize core fields for context (e.g., `OperationId`, `SqlInstance`, `Database`, `ItemId`). Keep payloads concise.

### 5) Secure by Default

- Do not log secrets or credentials. Redact or summarize sensitive values (e.g., lengths, hashes).
- Ensure log directories have appropriate permissions (Windows ACLs; Linux file modes/ownership).
- Consider encryption at rest or transport where required.

#### Redaction Patterns

Implement redaction for sensitive data before logging:

```powershell
# Function to redact sensitive values
function Get-RedactedContext {
    param($OriginalContext)

    @{
        # Redact passwords and secrets
        Password = if ($OriginalContext.Password) {
            "[REDACTED length=$($OriginalContext.Password.Length)]"
        }

        # Redact connection strings (show only provider)
        ConnectionString = if ($OriginalContext.ConnectionString) {
            $provider = ($OriginalContext.ConnectionString -split ';')[0]
            "$provider;[REDACTED]"
        }

        # Hash tokens for traceability without exposure
        ApiToken = if ($OriginalContext.ApiToken) {
            $hash = [System.Security.Cryptography.SHA256]::Create()
            $hashBytes = $hash.ComputeHash([Text.Encoding]::UTF8.GetBytes($OriginalContext.ApiToken))
            "sha256:$([Convert]::ToBase64String($hashBytes).Substring(0,16))..."
        }

        # Redact PII (show only partial)
        Email = if ($OriginalContext.Email) {
            $parts = $OriginalContext.Email -split '@'
            "$($parts[0].Substring(0,[Math]::Min(2,$parts[0].Length)))***@$($parts[1])"
        }

        # Safe fields pass through
        SqlInstance = $OriginalContext.SqlInstance
        Database = $OriginalContext.Database
        RowCount = $OriginalContext.RowCount
        DurationMs = $OriginalContext.DurationMs
    }
}

# Usage in logging
Import-Module GDS.Logging
$safeContext = Get-RedactedContext -OriginalContext @{
    SqlInstance = "prod-sql-01"
    Database = "CustomerDB"
    ConnectionString = "Server=prod-sql-01;Database=CustomerDB;User=sa;Password=Secret123"
    ApiToken = "sk_live_51H..."
    Email = "user@example.com"
    RowCount = 150
}

Write-Log -Level Information -Message "Query completed" -Context $safeContext
```

### 6) Rotation, Retention, and Size Management

- Rotate files by size and/or date. Apply retention policies appropriate to the environment.
- Prefer built‑in or well‑tested mechanisms over hand‑rolled rotation logic.

### 7) Multi‑Target Outputs

- Support console and file for development and operations.
- Add Kafka streaming for centralized ingestion, alerting, and analytics.

### 8) Performance and Reliability

- Avoid synchronous, per‑message blocking I/O on hot paths.
- Use batching/buffering for file and Kafka sinks; handle backpressure and transient failures gracefully.
- Keep logging overhead below 2–5% CPU on typical workloads; avoid logging inside tight loops unless sampled or aggregated.

#### Performance Measurement

Measure logging overhead systematically:

```powershell
# Benchmark logging overhead
function Measure-LoggingOverhead {
    Import-Module GDS.Logging
    param(
        [int]$Iterations = 1000,
        [string]$LogLevel = 'Information'
    )

    # Baseline (no logging)
    $baselineTime = Measure-Command {
        1..$Iterations | ForEach-Object {
            $data = Get-Random -Minimum 1 -Maximum 100
            # Simulate work
        }
    }

    # With logging
    $loggedTime = Measure-Command {
        1..$Iterations | ForEach-Object {
            $data = Get-Random -Minimum 1 -Maximum 100
            Write-Log -Level $LogLevel -Message "Processed item" -Context @{
                ItemId = $_
                Value = $data
            }
        }
    }

    $overhead = (($loggedTime.TotalMilliseconds - $baselineTime.TotalMilliseconds) / $baselineTime.TotalMilliseconds) * 100

    [PSCustomObject]@{
        BaselineMs = $baselineTime.TotalMilliseconds
        LoggedMs = $loggedTime.TotalMilliseconds
        OverheadPct = [Math]::Round($overhead, 2)
        MsPerLog = [Math]::Round(($loggedTime.TotalMilliseconds - $baselineTime.TotalMilliseconds) / $Iterations, 4)
    }
}

# Run benchmark
Measure-LoggingOverhead -Iterations 1000

# Expected output (example):
# BaselineMs  : 45.2
# LoggedMs    : 52.1
# OverheadPct : 15.3
# MsPerLog    : 0.0069
```

**Sampling Pattern for High-Frequency Operations**:

```powershell
# Sample 1% of debug logs in hot paths
$script:logCounter = 0

function Write-SampledLog {
    Import-Module GDS.Logging
    param($Level, $Message, $Context, [int]$SampleRate = 100)

    $script:logCounter++

    # Always log Warning/Error/Critical
    if ($Level -in @('Warning', 'Error', 'Critical')) {
        Write-Log -Level $Level -Message $Message -Context $Context
        return
    }

    # Sample Debug/Verbose/Information based on rate
    if ($script:logCounter % $SampleRate -eq 0) {
        $Context['_sampled'] = $true
        $Context['_sampleRate'] = $SampleRate
        Write-Log -Level $Level -Message $Message -Context $Context
    }
}

# Usage in tight loop
1..10000 | ForEach-Object {
    $result = Invoke-SomeOperation -Id $_
    # Only logs 1 in 100 (1%)
    Write-SampledLog -Level Debug -Message "Operation completed" -Context @{
        ItemId = $_
        Result = $result
    } -SampleRate 100
}
```

---

## Options and Approaches

This section outlines architectural options frequently used in production PowerShell environments. Each option can satisfy the requirements with different trade‑offs.

### Option A: PSFramework‑Based Logging

- Overview: Use PSFramework for structured logging, levels, providers (file, console, Windows Event Log), configuration, and message proxies.
- Strengths: Mature, widely adopted, cross‑platform core features; built‑in rotation/retention and configuration; message proxies make it easier to capture built‑in streams.
- Considerations: Windows Event Log provider is Windows‑only; Kafka requires an adapter or external shipper.

When to choose:

- Desire a PowerShell‑native, batteries‑included framework.
- Need consistent handling of PowerShell streams and easy configuration.

### Option B: Serilog via PSSerilog (Hybrid PowerShell/.NET)

- Overview: Leverage Serilog from PowerShell through modules such as PSSerilog or PoShLog, or via direct .NET interop. Serilog offers rich structured logging and many sinks (file/rolling file, console, Seq, OpenTelemetry, and Kafka via REST proxy/custom sink or shipper).
- Strengths: Large ecosystem, powerful enrichment, advanced batching and durability options through sinks.
- Considerations: Additional dependency; some sinks are .NET‑centric and may require careful packaging on Linux; capturing PowerShell streams is not automatic and typically requires wrappers or redirection.

When to choose:

- Teams already standardized on Serilog across services.
- Kafka or observability stack alignment favors Serilog sinks.

#### Typical Setup (using PoShLog as a Serilog wrapper)

PoShLog exposes a fluent PowerShell API over Serilog. Equivalent patterns apply with PSSerilog; the exact cmdlet names differ.

```powershell
# Install and import (one-time per host)
Install-Module PoShLog -Scope CurrentUser -Force
Import-Module PoShLog

# Initialize a logger with console + rolling file sinks
New-Logger `
  | Set-MinimumLevel -Value Information `
  | Add-ConsoleSink `
  | Add-FileSink -Path "/var/log/myapp/myapp-.log" -RollingInterval Day `
  | Start-Logger

# Write structured messages
Write-Log -Level Information -Message "Batch completed" -Properties @{
  RowCount    = 150
  DurationMs  = 234
  Correlation = $correlationId
} -Tags "ETL","Batch"
```

Notes:

- Rolling file naming like `myapp-.log` with `-RollingInterval Day` produces `myapp-YYYYMMDD.log`.
- Use `Set-MinimumLevel` (e.g., `Debug`, `Verbose`, `Information`, `Warning`, `Error`, `Fatal`) to control volume.

#### Kafka Integration with Serilog

You have two main options:

- Shipper‑based (recommended): Emit JSON to file/stdout and forward to Kafka via Fluent Bit/Filebeat/Vector. This is the most operationally robust path.
- In‑process: Use a custom Serilog sink or Kafka REST Proxy.
  - REST Proxy pattern: Use `Serilog.Sinks.Http` (or a small PowerShell batching loop) to POST events to a Kafka REST endpoint.
  - Custom sink: Build a Serilog sink using the Confluent.Kafka .NET client and load it alongside PoShLog/PSSerilog. This gives low‑latency delivery but requires packaging and careful backpressure handling.

Example (conceptual, REST proxy):

```powershell
# Pseudo-configuration sketch; actual sink configuration varies by module
New-Logger `
  | Set-MinimumLevel -Value Information `
  | Add-ConsoleSink `
  | Add-FileSink -Path "/var/log/myapp/myapp-.log" -RollingInterval Day `
  | Add-HttpSink -Uri "https://kafka-rest.example/topics/myapp-logs" -BatchSize 100 -QueueLimit 5000 `
  | Start-Logger
```

If no REST proxy is available, prefer a shipper agent rather than writing an in‑process producer unless your team is comfortable managing batching, retries, and circuit‑breaking in the PowerShell runtime.

#### Capturing Third‑Party Module Output (e.g., dbatools) with Serilog

Serilog does not automatically capture PowerShell streams. Use one or more of these patterns:

1) Wrap and log with standardized context

```powershell
$start = Get-Date
try {
  $result = Invoke-DbaQuery -SqlInstance $SqlInstance -Database $Database -Query $Query
  Write-Log -Level Information -Message "Invoke-DbaQuery completed" -Properties @{
    SqlInstance = $SqlInstance
    Database    = $Database
    Rows        = $result.Count
    DurationMs  = ((Get-Date) - $start).TotalMilliseconds
  } -Tags "dbatools","Success"
} catch {
  Write-Log -Level Error -Message "Invoke-DbaQuery failed" -Exception $_.Exception -Properties @{
    SqlInstance = $SqlInstance
    Database    = $Database
    DurationMs  = ((Get-Date) - $start).TotalMilliseconds
  } -Tags "dbatools","Error"
  throw
}
```

1) Capture all streams (Error, Warning, Verbose, Information) and forward to Serilog

```powershell
# Enable preferences to capture streams
$VerbosePreference = 'Continue'
$WarningPreference = 'Continue'
$InformationPreference = 'Continue'
$ErrorActionPreference = 'Continue'

# Capture all relevant streams
$capturedOutput = & {
    2>&1  # Stream 2: Error
    3>&1  # Stream 3: Warning
    4>&1  # Stream 4: Verbose
    6>&1  # Stream 6: Information

    try {
        Invoke-DbaDbUpgrade -SqlInstance $SqlInstance -Database $Database
    } catch {
        # Terminating errors need explicit handling
        $_
    }
}

# Process captured output by stream type
foreach ($item in $capturedOutput) {
    $level = 'Information'
    $message = $item.ToString()

    switch ($item.GetType().Name) {
        'ErrorRecord' {
            $level = 'Error'
            $message = $item.Exception.Message
            Write-Log -Level $level -Message "dbatools error: $message" -Exception $item.Exception -Properties @{
                ScriptStackTrace = $item.ScriptStackTrace
                CategoryInfo = $item.CategoryInfo.ToString()
            } -Tags "dbatools","Error"
        }
        'WarningRecord' {
            $level = 'Warning'
            Write-Log -Level $level -Message "dbatools warning: $message" -Properties @{
                Message = $item.Message
            } -Tags "dbatools","Warning"
        }
        'VerboseRecord' {
            $level = 'Verbose'
            Write-Log -Level $level -Message "dbatools verbose: $message" -Properties @{
                Message = $item.Message
            } -Tags "dbatools","Verbose"
        }
        'InformationRecord' {
            $level = 'Information'
            Write-Log -Level $level -Message "dbatools info: $message" -Properties @{
                Message = $item.MessageData.ToString()
                Source = $item.Source
            } -Tags "dbatools","Information"
        }
        default {
            # Standard output
            Write-Log -Level Information -Message "dbatools output: $message" -Tags "dbatools"
        }
    }
}
```

1) Standardize metadata

- Define shared keys (e.g., `OperationId`, `SqlInstance`, `Database`, `DurationMs`, `RowCount`, `Attempt`) and ensure all wrappers populate them.

#### Complexity vs PSFramework

- Setup and configuration:
  - PSFramework: Lower friction for PowerShell‑native use; built‑in providers and message proxies help capture streams with fewer custom wrappers.
  - Serilog (PSSerilog/PoShLog): Moderate; clear once established, but requires selecting/packaging sinks and wiring stream capture manually.
- Kafka:
  - PSFramework: Typically paired with an external shipper; in‑process Kafka requires custom adapter.
  - Serilog: Many sink patterns exist (file, console, HTTP); Kafka is feasible via REST proxy or custom sink, but adds packaging/ops complexity.
- Capturing third‑party module output:
  - PSFramework: Easier due to message proxies forwarding Information/Verbose/Warning directly.
  - Serilog: Yes, but not automatic; rely on wrappers and stream redirection as shown above.

### Option C: Native Streams + External Shippers (Fluent Bit, Filebeat, Vector)

- Overview: Emit structured JSON to files/stdout and use an external agent to ship to Kafka (or other backends).
- Strengths: Operationally robust; decouples application from transport; battle‑tested on Windows and Linux; supports buffering, backpressure, and retries.
- Considerations: Requires agent deployment and ops ownership; more moving parts.

When to choose:

- Strong platform/ops tooling exists for log shipping.
- Desire to minimize in‑process dependencies and keep PowerShell simple.

### Option D: Custom Lightweight Logger

- Overview: Implement only the minimum needed (JSON, levels, rotation, and optional Kafka producer or REST proxy).
- Strengths: Full control; minimal footprint.
- Considerations: Maintenance burden; easy to miss edge cases (threading, buffering, error handling, cross‑platform quirks).

When to choose:

- Highly constrained environments where external modules/agents are disallowed.

### Option E: Platform‑Native Sinks (Windows Event Log / Syslog)

- Overview: On Windows, write to Event Log; on Linux, write to syslog (then ship onward to Kafka/SEIM).
- Strengths: Integrates with existing monitoring; durable and familiar to ops teams.
- Considerations: Event Log is Windows‑only; syslog requires additional configuration; limited payload size/structure compared to JSON files.

When to choose:

- Compliance or operational standards mandate native event infrastructure.

### Option F: Native PowerShell Transcription

- Overview: Use built‑in `Start-Transcript` / `Stop-Transcript` to capture all console output to a text file.
- Strengths: No dependencies; automatic full session capture; works on Windows, Linux, and macOS; ideal for compliance and audit trails; captures all output including third‑party module messages.
- Considerations: Plain text (not structured JSON); captures everything (can be noisy); limited filtering; typically used as supplementary logging alongside structured logs.

When to choose:

- Compliance or audit requirements mandate complete session recording.
- Simple supplementary logging for troubleshooting alongside structured logs.
- Capturing interactive sessions or ad-hoc script executions.

#### Basic Transcription Setup

```powershell
# Start transcription at the beginning of a script
$transcriptPath = Join-Path "/var/log/myapp/transcripts" "transcript-$(Get-Date -Format 'yyyyMMdd-HHmmss')-$PID.log"
Start-Transcript -Path $transcriptPath -Append

try {
    # Your script logic here
    Write-Host "Starting operations..."
    Invoke-DbaQuery -SqlInstance $SqlInstance -Database $Database -Query $Query
    Write-Host "Operations completed"
} finally {
    # Always stop transcription
    Stop-Transcript
}
```

#### Transcription via Group Policy (Windows Enterprise)

For Windows environments, enable transcription via Group Policy for automatic capture:

- Computer Configuration → Administrative Templates → Windows Components → Windows PowerShell
- Enable "Turn on PowerShell Transcription"
- Set output directory: `\\fileserver\share\PSTranscripts` or `C:\PSTranscripts`
- Enable "Include invocation headers" for timestamps

#### Combining Transcription with Structured Logging

Best practice is to use transcription for full audit trails while maintaining structured logging for queryable events:

```powershell
# Initialize both transcription and structured logging
Start-Transcript -Path $transcriptPath -Append

# Initialize structured logger (example with PSFramework)
Set-PSFLoggingProvider -Name logfile -Enabled $true -FilePath "/var/log/myapp/structured-{0:yyyy-MM-dd}.json"

# Now all console output goes to transcript, structured events go to JSON
Write-Host "Processing batch $batchId"  # Captured in transcript
Write-PSFMessage -Level Information -Message "Batch started" -Tag "ETL" -Data @{
    BatchId = $batchId
    StartTime = Get-Date
}  # Captured in structured log

# Both systems capture errors and warnings in their own formats
```

#### Transcript Management

Implement rotation and retention for transcript files:

```powershell
# Clean up old transcripts (retain 30 days)
$transcriptDir = "/var/log/myapp/transcripts"
$retentionDays = 30

Get-ChildItem -Path $transcriptDir -Filter "transcript-*.log" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$retentionDays) } |
    Remove-Item -Force

# Compress old transcripts to save space
Get-ChildItem -Path $transcriptDir -Filter "transcript-*.log" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) -and $_.Extension -ne '.gz' } |
    ForEach-Object {
        # Use gzip on Linux, Compress-Archive on Windows
        if ($IsLinux -or $IsMacOS) {
            gzip $_.FullName
        } else {
            Compress-Archive -Path $_.FullName -DestinationPath "$($_.FullName).zip" -Force
            Remove-Item $_.FullName
        }
    }
```

---

## Kafka Streaming Options

Two common patterns provide reliable Kafka ingestion while supporting Windows and Linux.

### 1) Out‑of‑Process Shipping (Recommended Baseline)

- Emit JSON logs to file or stdout.
- Use a log shipper (Fluent Bit, Filebeat, Vector, Logstash) to parse, batch, and forward to Kafka.
- Pros: Robust buffering and retry; decouples app from Kafka availability; minimal app changes; cross‑platform.
- Cons: Requires installing and managing an agent.

Key considerations:

- Topic design (by application/domain; consider partition keys like `correlationId` or `operationId`).
- Schema discipline (JSON schema or Protobuf/Avro if/when using a schema registry).
- Delivery semantics (at‑least‑once typical; idempotent consumers recommended).

### 2) In‑Process Producer

- Use a .NET Kafka client (e.g., Confluent.Kafka) from PowerShell or a Serilog Kafka sink to publish directly.
- Pros: Single deployment artifact; immediate feedback on publish success/failure.
- Cons: Application must handle batching, backpressure, retries; adds dependency footprint; increases coupling to Kafka.

Key considerations:

- Batch size and linger settings to balance latency with throughput.
- Backoff and circuit breaking on broker errors.
- Async flush on shutdown to avoid message loss.

---

## OpenTelemetry Integration (OTLP)

OpenTelemetry is emerging as the de facto standard for unified observability (logs, traces, metrics). For organizations adopting OpenTelemetry, consider these integration patterns:

### Why OpenTelemetry?

- **Unified observability**: Correlate logs with distributed traces and metrics.
- **Vendor neutrality**: Export to any OTLP-compatible backend (Jaeger, Prometheus, Grafana, DataDog, New Relic, etc.).
- **Future-proof**: Industry standard with broad ecosystem support.

### Integration Patterns

#### 1) Via Serilog OTLP Sink

```powershell
# Install Serilog OTLP sink (example, package names vary)
# Install-Package Serilog.Sinks.OpenTelemetry

# Configure logger with OTLP exporter
New-Logger `
  | Set-MinimumLevel -Value Information `
  | Add-ConsoleSink `
  | Add-OtlpSink -Endpoint "http://otel-collector:4318/v1/logs" -Protocol HttpProtobuf `
  | Start-Logger

# Log events are exported as OTLP logs
Write-Log -Level Information -Message "Operation completed" -Properties @{
    TraceId = $traceId
    SpanId = $spanId
    OperationName = "ProcessBatch"
    DurationMs = 234
}
```

#### 2) Via OpenTelemetry Collector + File/Stdout

Emit structured JSON logs and configure the OpenTelemetry Collector to read and forward them:

```yaml
# otel-collector-config.yaml
receivers:
  filelog:
    include: [/var/log/myapp/*.json]
    operators:
      - type: json_parser

processors:
  batch:
    timeout: 10s
    send_batch_size: 100

exporters:
  otlp:
    endpoint: "otel-backend:4317"

  # Also export to Kafka if needed
  kafka:
    brokers: ["kafka:9092"]
    topic: "myapp-logs"

service:
  pipelines:
    logs:
      receivers: [filelog]
      processors: [batch]
      exporters: [otlp, kafka]
```

#### 3) Correlation with Distributed Traces

Include trace context in logs to correlate with distributed traces:

```powershell
# Generate or propagate trace context
$traceId = [Guid]::NewGuid().ToString("N")
$spanId = [Guid]::NewGuid().ToString("N").Substring(0, 16)

# Include in all log entries
Write-Log -Level Information -Message "Database query started" -Properties @{
    TraceId = $traceId
    SpanId = $spanId
    ParentSpanId = $parentSpanId
    SqlInstance = $SqlInstance
    Query = $query
}

# When forwarded via OTLP, logs are automatically correlated with traces
```

### Recommendations

- **Start with Collector pattern**: Use OpenTelemetry Collector as an intermediary for flexibility (easier to change backends).
- **Use consistent trace context**: Propagate W3C Trace Context headers or equivalent across services.
- **Enrich logs with span/trace IDs**: Ensure correlation between logs and traces for unified troubleshooting.

---

## Capturing Third‑Party Module Output (e.g., dbatools)

Goal: Ensure everything ends up in the same structured log stream without losing fidelity.

Approaches (can be combined):

- Wrap calls and log start/stop/summary with standardized context.
- Capture PowerShell streams emitted by the third‑party module.
- Use message proxying features (when leveraging a framework that supports them) to forward Information/Verbose/Warning to the structured logger.

Practical patterns:

1) Wrapper with standardized context and timing

```powershell
$start = Get-Date
try {
  $result = Invoke-DbaQuery -SqlInstance $SqlInstance -Database $Database -Query $Query
  # Log success (rows, durationMs, instance, database, etc.)
} catch {
  # Log error with exception and context
  throw
}
```

1) Capture all streams explicitly (when not using proxies)

```powershell
# Enable preferences to capture streams
$VerbosePreference = 'Continue'
$WarningPreference = 'Continue'
$InformationPreference = 'Continue'
$ErrorActionPreference = 'Continue'

# Capture all relevant streams
$allOutput = & {
    2>&1  # Stream 2: Error
    3>&1  # Stream 3: Warning
    4>&1  # Stream 4: Verbose
    6>&1  # Stream 6: Information

    try {
        Invoke-DbaDbUpgrade -SqlInstance $SqlInstance -Database $Database
    } catch {
        # Terminating errors need explicit handling
        $_
    }
}

# Process and emit structured logs for each captured item
foreach ($item in $allOutput) {
    $logEntry = @{
        Timestamp = Get-Date -Format 'o'
        Source = 'dbatools'
        SqlInstance = $SqlInstance
        Database = $Database
    }

    switch ($item.GetType().Name) {
        'ErrorRecord' {
            $logEntry['Level'] = 'Error'
            $logEntry['Message'] = $item.Exception.Message
            $logEntry['Exception'] = @{
                Type = $item.Exception.GetType().Name
                Message = $item.Exception.Message
                StackTrace = $item.ScriptStackTrace
            }
        }
        'WarningRecord' {
            $logEntry['Level'] = 'Warning'
            $logEntry['Message'] = $item.Message
        }
        'VerboseRecord' {
            $logEntry['Level'] = 'Verbose'
            $logEntry['Message'] = $item.Message
        }
        'InformationRecord' {
            $logEntry['Level'] = 'Information'
            $logEntry['Message'] = $item.MessageData.ToString()
        }
        default {
            $logEntry['Level'] = 'Information'
            $logEntry['Message'] = $item.ToString()
        }
    }

    # Emit to structured logger
    Write-StructuredLog -Entry $logEntry
}
```

1) Normalize context metadata

- Define a small, shared vocabulary (e.g., `OperationId`, `SqlInstance`, `Database`, `DurationMs`, `RowCount`, `Attempt`).
- Ensure wrappers for third‑party modules populate these fields consistently.

---

## Data Model (Schema Guidance)

Recommended core fields:

- `timestamp` (UTC ISO‑8601), `level`, `message`
- `correlationId`/`operationId`
- `script`, `function`, `module` (as available)
- `tags` (array of strings)
- `context` (hashtable/object with domain fields such as `SqlInstance`, `Database`, `RowCount`, `DurationMs`)
- `exception` (object with `type`, `message`, `stack` when present; keep concise in production and expand on demand)

Notes:

- Favor flatter, well‑named context fields where possible for easier querying.
- Keep messages human‑readable; reserve context for structured data.

---

## Cross‑Platform Considerations

- Paths and permissions:
  - Use platform‑appropriate default directories for logs and ensure the directory exists with correct permissions.
  - Use `Join-Path` instead of hard‑coding separators.
- Providers:
  - Windows Event Log is Windows‑only; consider syslog or file + shipper on Linux.
- Encoding and locale:
  - Emit UTF‑8; avoid locale‑specific formatting in numeric/time fields (use ISO‑8601/UTC).
- Packaging:
  - If using .NET libraries (e.g., Kafka clients), ensure cross‑platform compatibility and packaging for PowerShell 7 on Linux.

---

## Non‑Functional Requirements

- Performance:
  - Target sub‑millisecond overhead for Info‑level events; batch debug/verbose logging or sample when necessary.
- Resilience:
  - File or memory buffering during sink outages; backpressure strategy to avoid unbounded memory growth.
- Security and Compliance:
  - Redaction for sensitive data; role‑appropriate access to log directories; retention aligned with policy.
- Operability:
  - Clear configuration model (minimum level, targets, directories, Kafka endpoints/topics).
  - Health diagnostics (e.g., periodic heartbeat entries; counters for dropped/queued messages).

---

## Configuration Examples

Practical configuration file examples for common scenarios:

### Example 1: JSON Configuration File (PSFramework-style)

```json
{
  "logging": {
    "minimumLevel": "Information",
    "overrides": {
      "GDS.Common": "Verbose",
      "dbatools": "Warning"
    },
    "targets": {
      "console": {
        "enabled": true,
        "minimumLevel": "Information",
        "colorize": true
      },
      "file": {
        "enabled": true,
        "minimumLevel": "Verbose",
        "path": "/var/log/myapp/app-{Date:yyyy-MM-dd}.json",
        "rollingInterval": "Day",
        "retainedFileCountLimit": 30,
        "fileSizeLimitBytes": 104857600,
        "buffered": true,
        "flushIntervalSeconds": 5
      },
      "kafka": {
        "enabled": true,
        "minimumLevel": "Information",
        "brokers": ["kafka-01:9092", "kafka-02:9092", "kafka-03:9092"],
        "topic": "myapp-logs",
        "compressionType": "gzip",
        "batchSize": 100,
        "lingerMs": 10,
        "retries": 3,
        "partitionKey": "correlationId"
      }
    },
    "enrichment": {
      "environment": "Production",
      "application": "DataOps",
      "version": "1.2.3",
      "hostname": true,
      "processId": true
    },
    "redaction": {
      "enabled": true,
      "patterns": [
        "Password",
        "ApiKey",
        "Token",
        "Secret",
        "ConnectionString"
      ]
    }
  }
}
```

### Example 2: PowerShell Configuration Script

```powershell
# logging-config.ps1
# Source this at the start of your script or module

# Configuration object
$script:LoggingConfig = @{
    MinimumLevel = 'Information'

    # Module-specific overrides
    ModuleLevels = @{
        'GDS.Common' = 'Verbose'
        'dbatools' = 'Warning'
    }

    # File logging
    FileLogging = @{
        Enabled = $true
        Path = '/var/log/myapp'
        FilePattern = 'app-{0:yyyy-MM-dd}.json'
        RetentionDays = 30
        MaxFileSizeMB = 100
        BufferSize = 100
        FlushIntervalSeconds = 5
    }

    # Kafka streaming
    KafkaLogging = @{
        Enabled = $true
        Brokers = @('kafka-01:9092', 'kafka-02:9092', 'kafka-03:9092')
        Topic = 'myapp-logs'
        CompressionType = 'gzip'
        BatchSize = 100
        LingerMs = 10
        Retries = 3
        TimeoutMs = 30000
        PartitionKey = 'correlationId'  # Field to use for partitioning
    }

    # Enrichment (added to every log entry)
    Enrichment = @{
        Environment = $env:ENVIRONMENT ?? 'Development'
        Application = 'DataOps'
        Version = '1.2.3'
        Hostname = $env:COMPUTERNAME ?? (hostname)
        ProcessId = $PID
    }

    # Transcription
    Transcription = @{
        Enabled = $true
        Path = '/var/log/myapp/transcripts'
        RetentionDays = 30
    }
}

# Initialize logging based on config
function Initialize-Logging {
    param($Config = $script:LoggingConfig)

    # Set minimum level
    Set-LogMinimumLevel -Level $Config.MinimumLevel

    # Configure file logging
    if ($Config.FileLogging.Enabled) {
        $filePath = Join-Path $Config.FileLogging.Path ($Config.FileLogging.FilePattern -f (Get-Date))

        # Ensure directory exists
        $null = New-Item -Path $Config.FileLogging.Path -ItemType Directory -Force -ErrorAction SilentlyContinue

        Enable-FileLogging -Path $filePath -BufferSize $Config.FileLogging.BufferSize
    }

    # Configure Kafka logging
    if ($Config.KafkaLogging.Enabled) {
        Enable-KafkaLogging -Brokers $Config.KafkaLogging.Brokers `
                            -Topic $Config.KafkaLogging.Topic `
                            -BatchSize $Config.KafkaLogging.BatchSize
    }

    # Start transcription
    if ($Config.Transcription.Enabled) {
        $transcriptFile = Join-Path $Config.Transcription.Path "transcript-$(Get-Date -Format 'yyyyMMdd-HHmmss')-$PID.log"
        $null = New-Item -Path $Config.Transcription.Path -ItemType Directory -Force -ErrorAction SilentlyContinue
        Start-Transcript -Path $transcriptFile -Append
    }
}

# Cleanup function
function Stop-Logging {
    param($Config = $script:LoggingConfig)

    if ($Config.Transcription.Enabled) {
        Stop-Transcript
    }

    # Flush any buffered logs
    Flush-Logs
}

# Usage:
# . ./logging-config.ps1
# Initialize-Logging
```

### Example 3: Environment-Specific Configuration

```powershell
# Get environment-specific config
function Get-LoggingConfig {
    param(
        [ValidateSet('Development', 'Staging', 'Production')]
        [string]$Environment = $env:ENVIRONMENT ?? 'Development'
    )

    $baseConfig = @{
        Enrichment = @{
            Environment = $Environment
            Application = 'DataOps'
        }
    }

    switch ($Environment) {
        'Development' {
            $baseConfig.MinimumLevel = 'Debug'
            $baseConfig.FileLogging = @{ Enabled = $true; RetentionDays = 7 }
            $baseConfig.KafkaLogging = @{ Enabled = $false }
            $baseConfig.ConsoleLogging = @{ Enabled = $true; Colorize = $true }
        }
        'Staging' {
            $baseConfig.MinimumLevel = 'Verbose'
            $baseConfig.FileLogging = @{ Enabled = $true; RetentionDays = 14 }
            $baseConfig.KafkaLogging = @{ Enabled = $true; Topic = 'staging-logs' }
            $baseConfig.ConsoleLogging = @{ Enabled = $true }
        }
        'Production' {
            $baseConfig.MinimumLevel = 'Information'
            $baseConfig.FileLogging = @{ Enabled = $true; RetentionDays = 30 }
            $baseConfig.KafkaLogging = @{ Enabled = $true; Topic = 'production-logs' }
            $baseConfig.ConsoleLogging = @{ Enabled = $false }
            $baseConfig.Transcription = @{ Enabled = $true; RetentionDays = 90 }
        }
    }

    return $baseConfig
}

# Usage
$config = Get-LoggingConfig -Environment $env:ENVIRONMENT
Initialize-Logging -Config $config
```

---

## Querying and Analyzing Structured Logs

Once logs are emitted as structured JSON, use these tools and patterns for analysis:

### Command-Line Querying with jq

```bash
# Find all errors in the last day
cat /var/log/myapp/app-2025-11-10.json | jq 'select(.level == "Error")'

# Count logs by level
cat /var/log/myapp/app-*.json | jq -r '.level' | sort | uniq -c

# Find slow queries (> 1 second)
cat /var/log/myapp/app-*.json | jq 'select(.context.durationMs > 1000) | {message, durationMs: .context.durationMs, sqlInstance: .context.sqlInstance}'

# Extract all unique SQL instances accessed
cat /var/log/myapp/app-*.json | jq -r '.context.sqlInstance' | sort -u

# Get average duration by operation
cat /var/log/myapp/app-*.json | jq -r '[.context.durationMs] | add/length'
```

### PowerShell JSON Log Analysis

```powershell
# Read and parse JSON logs
$logs = Get-Content /var/log/myapp/app-2025-11-10.json | ForEach-Object { $_ | ConvertFrom-Json }

# Find errors
$logs | Where-Object { $_.level -eq 'Error' }

# Group by SQL instance and count
$logs | Group-Object { $_.context.sqlInstance } |
    Select-Object Name, Count |
    Sort-Object Count -Descending

# Calculate percentiles for duration
$durations = $logs | Where-Object { $_.context.durationMs } | Select-Object -ExpandProperty context | Select-Object -ExpandProperty durationMs
$p50 = ($durations | Sort-Object)[[Math]::Floor($durations.Count * 0.5)]
$p95 = ($durations | Sort-Object)[[Math]::Floor($durations.Count * 0.95)]
$p99 = ($durations | Sort-Object)[[Math]::Floor($durations.Count * 0.99)]

Write-Host "Duration Percentiles: P50=$p50ms, P95=$p95ms, P99=$p99ms"

# Find operations with warnings or errors
$logs | Where-Object { $_.level -in @('Warning', 'Error') } |
    Select-Object timestamp, level, message, @{N='SqlInstance';E={$_.context.sqlInstance}}
```

### Grep Patterns for Quick Searches

```bash
# Find all entries for a specific correlation ID
grep -r "c1b2f1a5-3d0a-49a6-9b43-5e1a31b2f8a7" /var/log/myapp/

# Find all SQL connection errors
grep -r '"level":"Error"' /var/log/myapp/ | grep -i "connection"

# Count logs per hour
grep -oP '(?<="timestamp":")[^"]+' /var/log/myapp/app-2025-11-10.json | cut -c12-13 | sort | uniq -c
```

### Integration with Log Aggregation Platforms

When logs are shipped to Kafka/Elasticsearch/Splunk/etc., use their query languages:

**Elasticsearch/Kibana (KQL)**:

```text
level:Error AND context.sqlInstance:prod-sql-01
context.durationMs > 1000
tags:dbatools AND level:Warning
```

**Splunk**:

```text
source="/var/log/myapp/*.json" level=Error context.sqlInstance=prod-sql-01
| stats avg(context.durationMs) by context.sqlInstance
```

**Grafana Loki (LogQL)**:

```text
{app="myapp"} | json | level="Error" | line_format "{{.message}}"
{app="myapp"} | json | context_durationMs > 1000
```

---

## Comparison Matrix (Summary)

| Option | Cross‑Platform | Capture 3rd‑party Streams | File Logging | Kafka | Structured (JSON) | Ops Footprint | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PSFramework | Yes (core) | Strong (proxies) | Built‑in | Via adapter/shipper | Yes | Low‑Med | Mature PowerShell‑native |
| PSSerilog/Serilog | Yes | Via stream handling | Strong (sinks) | Strong (sinks/custom) | Yes | Med | Aligns with .NET estates |
| Streams + Shipper | Yes | Strong (wrapped/captured) | Yes | Strong (agent) | Yes | Med‑High | Operationally robust |
| Custom Logger | Yes | Custom effort | Custom | Custom | Custom | Low (code), Med (risk) | Max control, more maintenance |
| Event Log/Syslog | Partial (Win/Linux) | Limited | Indirect | Via syslog pipeline | Limited | Med | Compliance‑driven |
| Transcription | Yes (native) | Excellent (automatic) | Yes (text) | No (needs shipper) | No | Low | Audit trails, supplement only |

---

## Recommended Path(s)

Two proven patterns meet the requirements with different operational models:

1. Baseline (operations‑friendly)

- Emit structured JSON to file (rotation/retention) and console.
- Deploy a shipper (Fluent Bit, Filebeat, Vector) to forward to Kafka with buffering and retries.
- Use wrappers to standardize context and capture third‑party streams.

1. Framework‑centric (developer‑friendly)

- Use a mature PowerShell logging framework to handle structured output, levels, providers, and message proxies.
- For Kafka, either add a small adapter (in‑process producer) or prefer the same external shipper from (1) for resilience.

Either path should include:

- A shared schema and field naming guidance.
- A configuration surface for `MinimumLevel`, targets (file, console, Kafka), and destinations (directories, brokers, topics).
- Patterns for capturing third‑party module output and normalizing context.

---

## High‑Level Implementation Plan (No Code)

Phase 1 — Foundation

- Choose the primary option (framework or streams+shipper).
- Define the JSON schema, minimum fields, and tag taxonomy.
- Establish directory/permission standards and rotation/retention defaults.
- Produce wrapper patterns for third‑party modules and example usage.

Phase 2 — Kafka Integration

- If using a shipper: author shipper config (parsing, batching, topics, keys); validate backpressure behavior.
- If in‑process: define batching/retry strategy; add graceful shutdown flush; load test for backpressure.

Phase 3 — Reliability and Security

- Add redaction rules for sensitive fields.
- Add health counters/telemetry (queued, dropped, flush duration), and an operational runbook.
- Establish CI smoke tests and environment validation checks for logging.

---

## Troubleshooting Common Logging Issues

### Issue 1: Logs Not Appearing

**Symptoms**: No log output despite logging calls.

**Possible Causes & Solutions**:

```powershell
# Check 1: Verify minimum log level
# If minimum level is "Warning", Info/Debug/Verbose won't appear
Get-LogConfiguration | Select-Object MinimumLevel

# Solution: Lower the minimum level temporarily
Set-LogMinimumLevel -Level Debug

# Check 2: Verify Information stream is enabled
$InformationPreference  # Should be 'Continue'
$InformationPreference = 'Continue'

# Check 3: Verify logging provider is enabled (PSFramework)
Get-PSFLoggingProvider | Where-Object { $_.Enabled -eq $true }

# Check 4: Verify file path is writable
Test-Path -Path "/var/log/myapp" -PathType Container
New-Item -Path "/var/log/myapp" -ItemType Directory -Force -ErrorAction SilentlyContinue
```

### Issue 2: High Logging Overhead / Performance Degradation

**Symptoms**: Application slows significantly with logging enabled.

**Possible Causes & Solutions**:

```powershell
# Cause 1: Logging inside tight loops
# BAD:
1..100000 | ForEach-Object {
    Write-Log -Level Debug "Processing $_"  # 100k log calls!
}

# GOOD: Use sampling
$script:logCounter = 0
1..100000 | ForEach-Object {
    $script:logCounter++
    if ($script:logCounter % 1000 -eq 0) {  # Log every 1000th
        Write-Log -Level Debug "Processing checkpoint: $_"
    }
}

# Cause 2: Synchronous/unbuffered writes
# Solution: Enable buffering
Set-PSFLoggingProvider -Name logfile -Enabled $true `
    -BufferSize 100 `
    -FlushInterval (New-TimeSpan -Seconds 5)

# Cause 3: Excessive Debug/Verbose logging in production
# Solution: Raise minimum level
Set-LogMinimumLevel -Level Information  # Disable Debug/Verbose
```

### Issue 3: Missing Third-Party Module Output

**Symptoms**: dbatools (or other module) output not in logs.

**Possible Causes & Solutions**:

```powershell
# Cause: Module uses Write-Host or streams not captured

# Solution 1: Enable PSFramework message proxies (automatic)
Set-PSFConfig -FullName 'PSFramework.Message.Info.Maximum' -Value 9
Set-PSFConfig -FullName 'PSFramework.Message.Verbose.Maximum' -Value 9

# Solution 2: Explicit stream capture
$VerbosePreference = 'Continue'
$WarningPreference = 'Continue'
$InformationPreference = 'Continue'

$output = & { 2>&1; 3>&1; 4>&1; 6>&1; Invoke-DbaQuery ... }
$output | ForEach-Object { Write-Log -Level Information -Message $_.ToString() }

# Solution 3: Wrapper functions
function Invoke-DbaQueryWithLogging {
    param($SqlInstance, $Database, $Query)

    Write-Log -Level Information "Starting query" -Context @{
        SqlInstance = $SqlInstance
        Database = $Database
    }

    try {
        $result = Invoke-DbaQuery @PSBoundParameters
        Write-Log -Level Information "Query completed" -Context @{
            RowCount = $result.Count
        }
        return $result
    } catch {
        Write-Log -Level Error "Query failed" -Exception $_.Exception
        throw
    }
}
```

### Issue 4: Kafka Logs Not Arriving

**Symptoms**: Logs written to file but not appearing in Kafka.

**Possible Causes & Solutions**:

```bash
# Check 1: Verify Kafka broker connectivity
telnet kafka-01 9092
# or
nc -zv kafka-01 9092

# Check 2: Verify topic exists
kafka-topics.sh --bootstrap-server kafka-01:9092 --list | grep myapp-logs

# Check 3: Check shipper (Fluent Bit/Filebeat) status
systemctl status fluent-bit
journalctl -u fluent-bit -n 50

# Check 4: Verify shipper configuration
cat /etc/fluent-bit/fluent-bit.conf

# Check 5: Test Kafka producer manually
echo '{"test":"message"}' | kafka-console-producer.sh \
    --bootstrap-server kafka-01:9092 \
    --topic myapp-logs
```

### Issue 5: Log Files Growing Too Large

**Symptoms**: Disk space consumed rapidly.

**Possible Causes & Solutions**:

```powershell
# Cause: No rotation or retention policy

# Solution 1: Enable file rotation (PSFramework)
Set-PSFLoggingProvider -Name logfile -Enabled $true `
    -FilePath "/var/log/myapp/app-{0:yyyy-MM-dd}.json" `
    -FileRotation Daily `
    -RetainedFileCountLimit 30

# Solution 2: Manual cleanup script
$retentionDays = 30
Get-ChildItem "/var/log/myapp" -Filter "*.json" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$retentionDays) } |
    Remove-Item -Force

# Solution 3: Compress old logs
Get-ChildItem "/var/log/myapp" -Filter "*.json" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } |
    ForEach-Object {
        Compress-Archive -Path $_.FullName -DestinationPath "$($_.FullName).zip"
        Remove-Item $_.FullName
    }

# Solution 4: Use logrotate (Linux)
# Create /etc/logrotate.d/myapp:
# /var/log/myapp/*.json {
#     daily
#     rotate 30
#     compress
#     delaycompress
#     notifempty
#     create 0644 myapp myapp
# }
```

### Issue 6: Sensitive Data Appearing in Logs

**Symptoms**: Passwords, tokens, or PII found in log files.

**Immediate Remediation**:

```powershell
# 1. Rotate logs immediately
Get-ChildItem "/var/log/myapp" -Filter "*.json" |
    Rename-Item -NewName { $_.Name + ".REDACT_REQUIRED" }

# 2. Implement redaction function
function Get-RedactedValue {
    param($Value, $FieldName)

    $sensitivePatterns = @('password', 'secret', 'token', 'key', 'connectionstring')

    if ($sensitivePatterns | Where-Object { $FieldName -like "*$_*" }) {
        return "[REDACTED length=$($Value.Length)]"
    }

    return $Value
}

# 3. Update all logging calls to use redaction
# 4. Review and purge/redact affected logs
# 5. Update security procedures
```

### Issue 7: Cannot Parse JSON Logs

**Symptoms**: `ConvertFrom-Json` fails or jq errors.

**Possible Causes & Solutions**:

```powershell
# Cause 1: Multi-line JSON (pretty-printed)
# Solution: Ensure single-line JSON output
# Use -Compress with ConvertTo-Json

# Cause 2: Invalid JSON characters
# Solution: Escape special characters in messages
function Get-SafeLogMessage {
    param($Message)
    # Escape quotes and backslashes
    return $Message -replace '\\', '\\\\' -replace '"', '\"'
}

# Cause 3: Mixed log formats in same file
# Solution: Standardize on single format per file

# Debugging: Check for invalid lines
Get-Content /var/log/myapp/app.json | ForEach-Object {
    try {
        $_ | ConvertFrom-Json | Out-Null
    } catch {
        Write-Warning "Invalid JSON at line $($_.LineNumber): $_"
    }
}
```

---

## Open Questions (for Review)

- Which operational model is preferred: shipper‑centric vs in‑process Kafka?
- Do we require Windows Event Log or syslog integration in addition to files/Kafka?
- What are the mandated retention periods and access controls for logs?
- Are we integrating with a schema registry (Avro/Protobuf/JSON‑Schema) for Kafka topics?

---

## References

- **Microsoft PowerShell Documentation**
  - PowerShell Logging guidance (streams, transcription, eventing)
  - about_Redirection: <https://docs.microsoft.com/powershell/module/microsoft.powershell.core/about/about_redirection>
  - about_Preference_Variables: <https://docs.microsoft.com/powershell/module/microsoft.powershell.core/about/about_preference_variables>
  - Start-Transcript / Stop-Transcript cmdlets

- **PSFramework**
  - Official documentation: <https://psframework.org>
  - Logging concepts and cross‑platform notes
  - Message proxies and providers

- **Serilog Ecosystem**
  - Serilog documentation: <https://serilog.net>
  - PSSerilog module: <https://github.com/PoShLog/PoShLog> (maintained fork)
  - PoShLog module: <https://github.com/PoShLog/PoShLog>
  - Serilog sinks catalog: <https://github.com/serilog/serilog/wiki/Provided-Sinks>

- **OpenTelemetry**
  - OpenTelemetry specification: <https://opentelemetry.io>
  - OTLP (OpenTelemetry Protocol): <https://opentelemetry.io/docs/specs/otlp/>
  - OpenTelemetry Collector: <https://opentelemetry.io/docs/collector/>
  - W3C Trace Context: <https://www.w3.org/TR/trace-context/>

- **Kafka & Streaming**
  - Confluent Kafka .NET client: <https://github.com/confluentinc/confluent-kafka-dotnet>
  - Kafka REST Proxy: <https://docs.confluent.io/platform/current/kafka-rest/>
  - Apache Kafka documentation: <https://kafka.apache.org/documentation/>

- **Log Shippers**
  - Fluent Bit documentation: <https://docs.fluentbit.io>
  - Filebeat documentation: <https://www.elastic.co/guide/en/beats/filebeat/current/index.html>
  - Vector documentation: <https://vector.dev/docs/>
  - Logstash documentation: <https://www.elastic.co/guide/en/logstash/current/index.html>

- **Module-Specific**
  - dbatools documentation: <https://dbatools.io>
  - dbatools behavior of streams and usage patterns

- **Log Analysis Tools**
  - jq manual: <https://stedolan.github.io/jq/manual/>
  - Elasticsearch/Kibana KQL: <https://www.elastic.co/guide/en/kibana/current/kuery-query.html>
  - Grafana Loki LogQL: <https://grafana.com/docs/loki/latest/logql/>
  - Splunk SPL: <https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/>

---

## Document Revision History

| Date | Version | Changes |
| --- | --- | --- |
| 2025-11-10 | 2.0 | Major update: Added PowerShell Transcription (Option F), OpenTelemetry integration, configuration examples, log analysis patterns, redaction examples, performance measurement, sampling patterns, troubleshooting section, enhanced stream capture with all streams (2,3,4,6), log level decision guide, and comprehensive querying examples |
| 2025-01-15 | 1.0 | Initial version with PSFramework, Serilog, and Kafka integration patterns |

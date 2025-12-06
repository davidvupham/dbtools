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

## Step 1: Inspect the Logger Module

Navigate to the exercise source directory:

```bash
cd src/03_powershell_logging
```

Open `StructuredLogger.psm1`. This module defines the `StructuredLogger` class which handles:

1. **JSON Formatting**: Converts log entries to JSON.
2. **Trace Context**: Manages `TraceId` and `SpanId`.
3. **Redaction**: Removes sensitive data like passwords.

---

## Step 2: Run the Test Script

`Test-Logging.ps1` demonstrates the logger's capabilities.

Run the script:

```powershell
./Test-Logging.ps1
```

This script performs several tests:

1. **Basic Logging**: Logs messages at different levels.
2. **Context Redaction**: Demonstrates redacting secrets.
3. **Trace Context**: Propagates headers in HTTP calls.
4. **Simulated Workflow**: Logs a database operation with duration.

---

## Step 3: Analyze the Logs

You can inspect the raw JSON logs in `logs/app.json`.

For a better view, use the provided analysis tool:

```powershell
./Analyze-Logs.ps1
```

This script parses the JSON log file and provides a summary report, including:

- Count of entries by log level.
- Details of any errors found.

---

## Step 4: Third-Party Module Capture

`Invoke-DbaWithLogging.ps1` demonstrates how to capture output from other modules (simulating `dbatools`) into your structured logs.

Run the script:

```powershell
./Invoke-DbaWithLogging.ps1
```

Check the output file:

```powershell
./Analyze-Logs.ps1 -LogPath logs/dbatools.json
```

Notice how `Write-Verbose` and `Write-Warning` from the script block were captured as structured log entries.

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
4. Enhance `Analyze-Logs.ps1` to filter by time range

---

## Next Steps

Move to [Exercise 4: Create Alerts](04_create_alerts.md)

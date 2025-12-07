# How-to: Run a PowerShell Script Before a Windows Service Starts

This guide helps you configure a Windows Server environment to ensure a specific PowerShell script executes and completes before a target Windows Service (such as SQL Server) starts up.

## Introduction

In many enterprise scenarios, a service like SQL Server requires certain conditions to be met before it can function correctly. Examples include:

- Mounting a specific storage volume.
- Adding a static network route.
- Verifying Active Directory connectivity.
- Decrypting a configuration file.

The most robust method to achieve this is by creating a **Service Dependency**. You create a custom "helper" service that runs your script, and then configure the target service (e.g., `MSSQLSERVER`) to depend on it. The Windows Service Control Manager (SCM) enforces this startup order.

## Prerequisites

- **Administrator Privileges**: You must be an Administrator on the target machine.
- **PowerShell 5.1 or Later**: Standard on Windows Server.
- **Service Name**: Identify the exact service name of your target (e.g., `MSSQLSERVER` for default SQL instances).

## Step 1: Create the Pre-Requisite Script

Create the PowerShell script that contains your logic.

> **Important**: This script effectively "becomes" a service. If the script finishes and exits, the service stops.
>
> - **Option A (Blocking):** If your goal is to strictly run a task *once* before the other service starts, the script should perform the task and then **stay running** (e.g., sleep efficiently) so the dependency remains "satisfied".
> - **Option B (Run-Once):** If the script exits, the helper service stops. If the target service is already running, this is fine. But if both start at boot, a stopped dependency might prevent the dependent service from starting depending on recovery settings.
>
> **Recommended Pattern**: Perform checks, then enter a sleep loop to keep the service "Running".

**Example Script:** `C:\Ops\PreSqlCheck.ps1`

```powershell
# C:\Ops\PreSqlCheck.ps1
$LogPath = "C:\Ops\PreSqlLog.txt"
$TargetServiceName = "MSSQLSERVER"
$StartupTimeoutSeconds = 300 # 5 Minutes to wait for SQL to start
$NotificationEmail = "admin@example.com"
$SMTPServer = "smtp.example.com"

function Log-Message {
    param($Message)
    "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'): $Message" | Out-File $LogPath -Append
}

function Send-Notification {
    param($Subject, $Body)
    Log-Message "SENDING ALERT: $Subject"
    # Send-MailMessage -To $NotificationEmail -From "sql-watchdog@example.com" -Subject $Subject -Body $Body -SmtpServer $SMTPServer
}

Log-Message "Starting GDS Pre-SQL Service Wrapper..."

try {
    # PHASE 1: PRE-REQUISITES (Blocking)
    # The dependent service (SQL) CANNOT start until we finish this phase?
    # NOTE: Without a proper Service Wrapper (like NSSM), Windows SCM may timeout waiting for this script.
    # We assume here that the checks are fast or a wrapper is used.

    # 1. Example: Wait for a specific drive
    $retryCount = 0
    while (!(Test-Path "F:\Data")) {
        Log-Message "Waiting for F: drive..."
        Start-Sleep -Seconds 5
        $retryCount++
        if ($retryCount -gt 60) { throw "Timeout waiting for F: drive." }
    }

    Log-Message "Pre-requisites met. Service is now 'Ready'. SQL Server should start soon."

    # PHASE 2: WATCHDOG (Monitoring)
    # Now we monitor if the dependent service actually starts successfully.

    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    $started = $false

    # Loop to wait for start
    while ($timer.Elapsed.TotalSeconds -lt $StartupTimeoutSeconds) {
        $status = (Get-Service -Name $TargetServiceName -ErrorAction SilentlyContinue).Status
        if ($status -eq 'Running') {
            Log-Message "$TargetServiceName has successfully started."
            $started = $true
            break
        }
        Start-Sleep -Seconds 5
    }

    if (-not $started) {
        Send-Notification -Subject "CRITICAL: $TargetServiceName Failed to Start" `
                          -Body "The service $TargetServiceName did not reach 'Running' state within $StartupTimeoutSeconds seconds after pre-reqs were met."
    }

    # PHASE 3: STAY ALIVE
    # We must keep running to maintain the dependency chain, otherwise Windows might stop the dependent service.
    while ($true) {
        # Optional: Continue monitoring for random crashes
        $currentStatus = (Get-Service -Name $TargetServiceName -ErrorAction SilentlyContinue).Status
        if ($currentStatus -ne 'Running' -and $started) {
            Send-Notification -Subject "WARNING: $TargetServiceName Stopped Unexpectedly" `
                              -Body "The service was running but is now $currentStatus."
            $started = $false # Reset flag avoiding spam, or handle logic to avoid repeat alerts
        }
        Start-Sleep -Seconds 60
    }
}
catch {
    Log-Message "ERROR: $_"
    Send-Notification -Subject "GDS Pre-SQL Script Failure" -Body "Script crashed: $_"
    exit 1
}
```

## Step 2: Create the Helper Service

We effectively wrap the PowerShell script in a Windows Service. While tools like `NSSM` are popular, you can do this natively with PowerShell.

Run the following in an Elevated PowerShell console:

```powershell
$ServiceName = "GDS_PreSQLChecks"
$ScriptPath = "C:\Ops\PreSqlCheck.ps1"

# Note: We launch PowerShell, bypass policy, and run the file.
# The service will report "Running" as long as the PowerShell process is alive.
$BinaryPath = "powershell.exe -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File `"$ScriptPath`""

New-Service -Name $ServiceName `
    -DisplayName "GDS Pre-SQL Startup Checks" `
    -Description "Runs pre-requisite checks for SQL Server" `
    -BinaryPathName $BinaryPath `
    -StartupType Automatic
```

## Step 3: Configure the Dependency

Now tell the target service (`MSSQLSERVER`) that it cannot start until `GDS_PreSQLChecks` is running.

**Warning**: This modifies the service configuration. Ensure you know the existing dependencies.

```powershell
$TargetService = "MSSQLSERVER"
$HelperService = "GDS_PreSQLChecks"

# 1. Get existing dependencies (e.g., RPCSS) so we don't remove them
$Service = Get-Service -Name $TargetService
$CurrentDependencies = $Service.RequiredServices.Name

if ($CurrentDependencies -notcontains $HelperService) {
    # 2. Add our new helper service
    $NewDependencies = $CurrentDependencies + $HelperService

    # 3. Apply the new list.
    # 'sc.exe' is often more reliable for this specific config than Set-Service on older OS versions.
    # The dependencies must be slash-separated for sc.exe
    $DepString = $NewDependencies -join "/"

    Write-Host "Setting dependencies for $TargetService to: $DepString"
    sc.exe config $TargetService depend= $DepString
}
```

## Verification

1. **Restart configuration**: `Restart-Service GDS_PreSQLChecks` (This might force SQL to restart if configured to cascade, otherwise testing reboot is best).
2. **Reboot the Server**.
3. **Observe**:
   - Check `C:\Ops\PreSqlLog.txt`.
   - Check Event Viewer (System Log).
   - Verify `MSSQLSERVER` started *after* the log timestamps show success.

## Troubleshooting

- **Service hangs on start**: If your script doesn't signal "started" quickly, Windows might timeout. For pure PowerShell script services, this is usually strictly time-based. Ensure the script starts quickly.
- **Service stops immediately**: Review the script logic. Did it throw an error and `exit`?
- **Zombie processes**: Since we are launching `powershell.exe` directly as a service, if the service is killed forcibly, verify the process actually terminates.

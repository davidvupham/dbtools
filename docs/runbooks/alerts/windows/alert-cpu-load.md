# Alert: CPU load is critical

**🔗 [← Back to Windows Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 19, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Severity](https://img.shields.io/badge/Severity-Critical-red)

> [!IMPORTANT]
> **Related Docs:** [Windows Index](./README.md) | [Alerts Index](../README.md)

## Table of Contents

- [Summary](#summary)
- [Description](#description)
- [Impact](#impact)
- [Troubleshooting steps](#troubleshooting-steps)
- [Common causes](#common-causes)
- [Post-recovery verification](#post-recovery-verification)
- [Related alerts](#related-alerts)
- [Additional resources](#additional-resources)

## Summary

| Attribute | Value |
|:---|:---|
| **Type** | Alert |
| **Severity** | Critical |
| **Source** | Nagios / SCOM / Prometheus |
| **Delivery** | Email |
| **Threshold** | CPU > 90% for 5 minutes |

[↑ Back to Table of Contents](#table-of-contents)

## Description

This alert fires when Windows server CPU utilization exceeds 90% for more than 5 consecutive minutes. High CPU indicates the system is overloaded and applications may become unresponsive.

[↑ Back to Table of Contents](#table-of-contents)

## Impact

- Application response times increase
- RDP sessions may be slow or unresponsive
- Scheduled tasks may timeout or fail
- Services running on this host may become unavailable

[↑ Back to Table of Contents](#table-of-contents)

## Troubleshooting steps

### 1. Connect to the server

```powershell
# PowerShell remoting
Enter-PSSession -ComputerName <server-hostname>

# Or use RDP
mstsc /v:<server-hostname>
```

### 2. Check current CPU usage

```powershell
# View CPU usage over 10 seconds
Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 2 -MaxSamples 5

# Check number of CPU cores
(Get-CimInstance Win32_Processor).NumberOfLogicalProcessors
```

### 3. Identify high CPU processes

```powershell
# View top processes by CPU usage
Get-Process | Sort-Object CPU -Descending | Select-Object -First 15 Name, Id, CPU, WorkingSet64

# More detailed view with username
Get-CimInstance Win32_Process |
    Select-Object Name, ProcessId, @{N='CPU';E={$_.KernelModeTime + $_.UserModeTime}},
                  @{N='MemoryMB';E={[math]::Round($_.WorkingSetSize/1MB,2)}} |
    Sort-Object CPU -Descending | Select-Object -First 15
```

### 4. Check for specific problematic processes

```powershell
# Get details about a specific process
Get-Process -Id <PID> | Select-Object *

# Check process command line
Get-CimInstance Win32_Process -Filter "ProcessId = <PID>" |
    Select-Object Name, ProcessId, CommandLine
```

### 5. Check for runaway services

```powershell
# Find services and their process IDs
Get-CimInstance Win32_Service | Where-Object {$_.State -eq 'Running'} |
    Select-Object Name, ProcessId, State |
    ForEach-Object {
        $proc = Get-Process -Id $_.ProcessId -ErrorAction SilentlyContinue
        [PSCustomObject]@{
            Service = $_.Name
            PID = $_.ProcessId
            CPU = $proc.CPU
        }
    } | Sort-Object CPU -Descending | Select-Object -First 10
```

### 6. Check scheduled tasks

```powershell
# View running scheduled tasks
Get-ScheduledTask | Where-Object {$_.State -eq 'Running'} |
    Select-Object TaskName, State, TaskPath
```

### 7. Stop problematic process if needed

> [!WARNING]
> Only stop processes after confirming with the application team. Document the process details before terminating.

```powershell
# Graceful stop
Stop-Process -Id <PID>

# Force stop if unresponsive
Stop-Process -Id <PID> -Force
```

### 8. Restart a service if needed

```powershell
# Restart a service
Restart-Service -Name <ServiceName> -Force
```

### 9. Verify resolution

```powershell
# Monitor CPU for a few minutes
while ($true) {
    Get-Counter '\Processor(_Total)\% Processor Time' | Select-Object -ExpandProperty CounterSamples | Select-Object CookedValue
    Start-Sleep -Seconds 5
}
# Press Ctrl+C to stop
```

[↑ Back to Table of Contents](#table-of-contents)

## Common causes

| Cause | Resolution |
|:---|:---|
| Runaway application process | Stop process, investigate root cause |
| Antivirus scan | Reschedule scans to off-peak hours |
| Windows Update | Allow updates to complete or reschedule |
| IIS application pool issue | Recycle application pool |
| SQL Server on same host | Check for expensive queries |
| Backup software | Schedule backups during off-peak hours |
| Malware/crypto mining | Investigate and remove malicious processes |

[↑ Back to Table of Contents](#table-of-contents)

## Post-recovery verification

1. Verify CPU has returned to normal:

   ```powershell
   Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 2 -MaxSamples 5
   # CPU should be below 80%
   ```

2. Check application health
3. Verify services are running normally:

   ```powershell
   Get-Service | Where-Object {$_.StartType -eq 'Automatic' -and $_.Status -ne 'Running'}
   ```

4. Review Event Viewer for any errors during high CPU period

[↑ Back to Table of Contents](#table-of-contents)

## Related alerts

- [Memory usage critical](#) <!-- Add link when created -->
- [Disk space low](#) <!-- Add link when created -->

[↑ Back to Table of Contents](#table-of-contents)

## Additional resources

- [Windows Performance Monitor](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/perfmon)
- [Troubleshooting High CPU Usage](https://docs.microsoft.com/en-us/troubleshoot/windows-server/performance/troubleshoot-high-cpu-usage)

[↑ Back to Table of Contents](#table-of-contents)

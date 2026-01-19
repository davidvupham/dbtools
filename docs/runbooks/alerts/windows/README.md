# Windows server alerts, reports, and notifications

**🔗 [← Back to Alerts Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 19, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows-blue)

> [!IMPORTANT]
> **On-Call Contact:** Infrastructure On-Call (PagerDuty) | **Escalation:** Platform Engineering Team

## Table of Contents

- [Prerequisites](#prerequisites)
- [Alerts](#alerts)
- [Reports](#reports)
- [Notifications](#notifications)
- [Common diagnostic commands](#common-diagnostic-commands)
- [Useful links](#useful-links)

## Prerequisites

Before troubleshooting Windows alerts, ensure you have:

- [ ] RDP or PowerShell remoting access to the target server
- [ ] Appropriate local administrator permissions
- [ ] Access to monitoring dashboards (Grafana/Prometheus/Nagios/SCOM)

[↑ Back to Table of Contents](#table-of-contents)

## Alerts

| Name | Severity | File |
|:---|:---|:---|
| CPU load is critical | Critical | [alert-cpu-load.md](./alert-cpu-load.md) |

[↑ Back to Table of Contents](#table-of-contents)

## Reports

| Name | Schedule | File |
|:---|:---|:---|
| *No reports documented yet* | | |

[↑ Back to Table of Contents](#table-of-contents)

## Notifications

| Name | Trigger | File |
|:---|:---|:---|
| *No notifications documented yet* | | |

[↑ Back to Table of Contents](#table-of-contents)

## Common diagnostic commands

### Check system information

```powershell
# View system info
Get-ComputerInfo | Select-Object CsName, OsName, OsVersion, CsNumberOfProcessors, CsTotalPhysicalMemory
```

### Check CPU usage

```powershell
# View current CPU usage
Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 2 -MaxSamples 5

# View top processes by CPU
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, CPU, Id
```

### Check memory usage

```powershell
# View memory usage
Get-Counter '\Memory\Available MBytes'

# Detailed memory info
Get-CimInstance Win32_OperatingSystem |
    Select-Object @{N='TotalGB';E={[math]::Round($_.TotalVisibleMemorySize/1MB,2)}},
                  @{N='FreeGB';E={[math]::Round($_.FreePhysicalMemory/1MB,2)}},
                  @{N='UsedPercent';E={[math]::Round((($_.TotalVisibleMemorySize-$_.FreePhysicalMemory)/$_.TotalVisibleMemorySize)*100,2)}}
```

### Check disk space

```powershell
# View disk usage
Get-PSDrive -PSProvider FileSystem |
    Select-Object Name, @{N='UsedGB';E={[math]::Round($_.Used/1GB,2)}},
                        @{N='FreeGB';E={[math]::Round($_.Free/1GB,2)}},
                        @{N='TotalGB';E={[math]::Round(($_.Used+$_.Free)/1GB,2)}}
```

### Check running services

```powershell
# View stopped services that should be running
Get-Service | Where-Object {$_.StartType -eq 'Automatic' -and $_.Status -ne 'Running'}

# View service status
Get-Service -Name <ServiceName> | Select-Object Name, Status, StartType
```

### Check event logs

```powershell
# View recent errors in System log
Get-EventLog -LogName System -EntryType Error -Newest 20 |
    Select-Object TimeGenerated, Source, Message

# View recent errors in Application log
Get-EventLog -LogName Application -EntryType Error -Newest 20 |
    Select-Object TimeGenerated, Source, Message
```

[↑ Back to Table of Contents](#table-of-contents)

## Useful links

- [Grafana Windows dashboard](#) <!-- Update with actual link -->
- [Nagios/SCOM monitoring](#) <!-- Update with actual link -->
- [Internal wiki - Windows runbooks](#) <!-- Update with actual link -->

[↑ Back to Table of Contents](#table-of-contents)

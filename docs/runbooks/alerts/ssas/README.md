# SQL Server Analysis Services alerts, reports, and notifications

**🔗 [← Back to Alerts Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 19, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Platform](https://img.shields.io/badge/Platform-SSAS-purple)

> [!IMPORTANT]
> **On-Call Contact:** DBA On-Call (PagerDuty) | **Escalation:** Database Infrastructure Team

## Table of Contents

- [Prerequisites](#prerequisites)
- [Alerts](#alerts)
- [Reports](#reports)
- [Notifications](#notifications)
- [Common diagnostic queries](#common-diagnostic-queries)
- [Useful links](#useful-links)

## Prerequisites

Before troubleshooting SSAS alerts, ensure you have:

- [ ] VPN connectivity to database network
- [ ] SQL Server Management Studio (SSMS) installed
- [ ] Analysis Services permissions (server administrator for some operations)
- [ ] Access to monitoring dashboards (Grafana/Prometheus)
- [ ] PowerShell remoting access to SSAS servers

[↑ Back to Table of Contents](#table-of-contents)

## Alerts

| Name | Severity | File |
|:---|:---|:---|
| SSAS is offline | Critical | [alert-offline.md](./alert-offline.md) |

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

## Common diagnostic queries

### Check SSAS service status

```powershell
# Check SSAS service status
Get-Service -Name "MSSQLServerOLAPService" -ComputerName <server-hostname>

# For named instances
Get-Service -Name "MSOLAP`$<instance-name>" -ComputerName <server-hostname>
```

### List SSAS databases

```sql
-- Run in SSMS connected to SSAS
SELECT [CATALOG_NAME] AS DatabaseName
FROM $SYSTEM.DBSCHEMA_CATALOGS
```

### Check SSAS memory usage

```powershell
# Check memory usage
Get-Process -Name msmdsrv -ComputerName <server-hostname> |
    Select-Object ProcessName, @{N='Memory(GB)';E={[math]::Round($_.WorkingSet64/1GB,2)}}
```

### Check processing status

```sql
-- Check last processed time for cubes
SELECT
    [CATALOG_NAME] AS DatabaseName,
    [CUBE_NAME] AS CubeName,
    [LAST_DATA_UPDATE] AS LastProcessed
FROM $SYSTEM.MDSCHEMA_CUBES
WHERE CUBE_SOURCE = 1
```

[↑ Back to Table of Contents](#table-of-contents)

## Useful links

- [SSAS documentation](https://docs.microsoft.com/en-us/analysis-services/)
- [Grafana SSAS dashboard](#) <!-- Update with actual link -->
- [Internal wiki - SSAS runbooks](#) <!-- Update with actual link -->

[↑ Back to Table of Contents](#table-of-contents)

# Alert: SSAS is offline

**🔗 [← Back to SSAS Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 19, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Severity](https://img.shields.io/badge/Severity-Critical-red)

> [!IMPORTANT]
> **Related Docs:** [SSAS Index](./README.md) | [Alerts Index](../README.md)

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
| **Source** | Nagios / Prometheus / SCOM |
| **Delivery** | Email |
| **Threshold** | SSAS service not responding |

[↑ Back to Table of Contents](#table-of-contents)

## Description

This alert fires when SQL Server Analysis Services (SSAS) is not responding or the service has stopped. SSAS downtime impacts all dependent reporting, dashboards, and analytical workloads that query OLAP cubes or tabular models.

[↑ Back to Table of Contents](#table-of-contents)

## Impact

- Business intelligence dashboards unavailable
- Scheduled cube processing jobs fail
- Excel/Power BI connections to cubes fail
- MDX queries return errors

[↑ Back to Table of Contents](#table-of-contents)

## Troubleshooting steps

### 1. Verify service status

```powershell
# Check SSAS service status
Get-Service -Name "MSSQLServerOLAPService" -ComputerName <server-hostname>

# Or for a named instance
Get-Service -Name "MSOLAP`$<instance-name>" -ComputerName <server-hostname>
```

### 2. Attempt to start the service

```powershell
# Start the SSAS service
Start-Service -Name "MSSQLServerOLAPService" -ComputerName <server-hostname>

# Verify it started
Get-Service -Name "MSSQLServerOLAPService" -ComputerName <server-hostname>
```

### 3. Check Windows Event Log for errors

```powershell
# View recent SSAS-related errors
Get-EventLog -LogName Application -Source "MSSQLServerOLAPService" -Newest 20 -ComputerName <server-hostname> |
    Where-Object { $_.EntryType -eq "Error" } |
    Format-List TimeGenerated, Message
```

### 4. Check SSAS log files

Default location: `C:\Program Files\Microsoft SQL Server\MSAS<version>.MSSQLSERVER\OLAP\Log\`

```powershell
# View recent log entries
Get-Content "\\<server-hostname>\c$\Program Files\Microsoft SQL Server\MSAS16.MSSQLSERVER\OLAP\Log\msmdsrv.log" -Tail 100
```

### 5. Check for resource issues

```powershell
# Check memory usage
Get-Process -Name msmdsrv -ComputerName <server-hostname> |
    Select-Object ProcessName, @{N='Memory(GB)';E={[math]::Round($_.WorkingSet64/1GB,2)}}

# Check disk space
Get-WmiObject Win32_LogicalDisk -ComputerName <server-hostname> |
    Where-Object { $_.DriveType -eq 3 } |
    Select-Object DeviceID, @{N='FreeGB';E={[math]::Round($_.FreeSpace/1GB,2)}}, @{N='TotalGB';E={[math]::Round($_.Size/1GB,2)}}
```

### 6. Verify connectivity after restart

```powershell
# Test SSAS connectivity using AMO
$server = New-Object Microsoft.AnalysisServices.Server
$server.Connect("<server-hostname>")
$server.Connected
$server.Disconnect()
```

Or test with SQL Server Management Studio (SSMS):

1. Open SSMS
2. Connect to Analysis Services
3. Server name: `<server-hostname>`
4. Verify databases are accessible

[↑ Back to Table of Contents](#table-of-contents)

## Common causes

| Cause | Resolution |
|:---|:---|
| Out of memory | Increase server memory or reduce memory limits in SSAS config |
| Disk full | Free up disk space, especially on data/temp drives |
| Service account issues | Verify service account password has not expired |
| Corrupt database | Restore from backup or detach problematic database |
| Windows Update reboot | Verify no pending restarts, check maintenance windows |
| Port blocked | Verify port 2383 (default) is open |

[↑ Back to Table of Contents](#table-of-contents)

## Post-recovery verification

1. Verify all SSAS databases are online:

   ```sql
   -- Run in SSMS connected to SSAS
   SELECT [CATALOG_NAME] AS DatabaseName
   FROM $SYSTEM.DBSCHEMA_CATALOGS
   ```

2. Test a sample MDX query against a cube
3. Verify scheduled processing jobs resume
4. Confirm downstream dashboards/reports are functioning

[↑ Back to Table of Contents](#table-of-contents)

## Related alerts

- *No related alerts documented yet*

[↑ Back to Table of Contents](#table-of-contents)

## Additional resources

- [SSAS Operations Guide](https://docs.microsoft.com/en-us/analysis-services/instances/analysis-services-instance-management)
- [SSAS Performance Counters](https://docs.microsoft.com/en-us/analysis-services/instances/performance-counters-ssas)

[↑ Back to Table of Contents](#table-of-contents)

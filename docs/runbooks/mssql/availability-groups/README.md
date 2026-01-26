# Availability Groups runbooks

**[← Back to SQL Server Runbooks](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 26, 2026
> **Maintainers:** Database Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-High_Availability-blue)

> [!IMPORTANT]
> **On-Call Contact:** DBA On-Call (PagerDuty) | **Escalation:** Database Infrastructure Team

## Table of Contents

- [Overview](#overview)
- [Runbooks](#runbooks)
- [Quick reference](#quick-reference)
- [Related resources](#related-resources)

## Overview

SQL Server Always On Availability Groups provide high availability and disaster recovery for databases. These runbooks cover troubleshooting procedures for AG issues and the underlying Windows Server Failover Clustering (WSFC) infrastructure.

[↑ Back to Table of Contents](#table-of-contents)

## Runbooks

| Runbook | Description | Use when |
|:---|:---|:---|
| [Troubleshoot Availability Groups](./troubleshoot-availability-groups.md) | Comprehensive troubleshooting guide | AG health issues, failover problems, sync issues |

[↑ Back to Table of Contents](#table-of-contents)

## Quick reference

### Common diagnostic commands

**Check AG status (T-SQL):**
```sql
SELECT ag.name, ar.replica_server_name, ars.role_desc, ars.synchronization_health_desc
FROM sys.availability_groups ag
JOIN sys.availability_replicas ar ON ag.group_id = ar.group_id
JOIN sys.dm_hadr_availability_replica_states ars ON ar.replica_id = ars.replica_id;
```

**Check cluster status (PowerShell):**
```powershell
Get-ClusterNode | Select-Object Name, State
Get-ClusterQuorum | Select-Object Cluster, QuorumResource, QuorumType
```

**Generate cluster log:**
```powershell
Get-ClusterLog -Destination C:\Temp -TimeSpan 60
```

[↑ Back to Table of Contents](#table-of-contents)

## Related resources

- [Microsoft: Always On Availability Groups](https://learn.microsoft.com/en-us/sql/database-engine/availability-groups/windows/overview-of-always-on-availability-groups-sql-server)
- [Microsoft: Troubleshooting Always On Issues](https://learn.microsoft.com/en-us/troubleshoot/sql/database-engine/availability-groups/troubleshooting-alwayson-issues)
- [SQL Server Alerts Runbooks](../../alerts/mssql/README.md)

[↑ Back to Table of Contents](#table-of-contents)

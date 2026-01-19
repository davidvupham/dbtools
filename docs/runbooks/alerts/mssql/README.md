# SQL Server alerts, reports, and notifications

**🔗 [← Back to Alerts Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 19, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Platform](https://img.shields.io/badge/Platform-SQL_Server-blue)

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

Before troubleshooting SQL Server alerts, ensure you have:

- [ ] VPN connectivity to database network
- [ ] SQL Server Management Studio (SSMS) installed
- [ ] Appropriate database permissions (db_datareader minimum, sysadmin for some operations)
- [ ] Access to monitoring dashboards (Grafana/Prometheus)

[↑ Back to Table of Contents](#table-of-contents)

## Alerts

| Name | Severity | File |
|:---|:---|:---|
| High CPU utilization | Critical | [alert-cpu-utilization.md](./alert-cpu-utilization.md) |
| Blocking detected | Warning | [alert-blocking-detected.md](./alert-blocking-detected.md) |

[↑ Back to Table of Contents](#table-of-contents)

## Reports

| Name | Schedule | File |
|:---|:---|:---|
| Daily backup status | Daily 06:00 UTC | [report-daily-backup.md](./report-daily-backup.md) |

[↑ Back to Table of Contents](#table-of-contents)

## Notifications

| Name | Trigger | File |
|:---|:---|:---|
| Backup job is running | Backup job starts | [notification-backup-job-running.md](./notification-backup-job-running.md) |
| Maintenance window starting | 30 min before maintenance | [notification-maintenance-window.md](./notification-maintenance-window.md) |

[↑ Back to Table of Contents](#table-of-contents)

## Common diagnostic queries

### Check current connections

```sql
SELECT
    db_name(dbid) AS database_name,
    COUNT(*) AS connection_count,
    loginame AS login_name
FROM sys.sysprocesses
GROUP BY dbid, loginame
ORDER BY connection_count DESC;
```

### Check long-running queries

```sql
SELECT
    r.session_id,
    r.start_time,
    DATEDIFF(MINUTE, r.start_time, GETDATE()) AS duration_minutes,
    r.status,
    t.text AS query_text
FROM sys.dm_exec_requests r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
WHERE r.session_id > 50
ORDER BY r.start_time;
```

### Check disk space

```sql
SELECT
    volume_mount_point AS drive,
    CAST(available_bytes / 1073741824.0 AS DECIMAL(10,2)) AS free_gb,
    CAST(total_bytes / 1073741824.0 AS DECIMAL(10,2)) AS total_gb,
    CAST((available_bytes * 100.0 / total_bytes) AS DECIMAL(5,2)) AS free_percent
FROM sys.master_files f
CROSS APPLY sys.dm_os_volume_stats(f.database_id, f.file_id)
GROUP BY volume_mount_point, available_bytes, total_bytes;
```

[↑ Back to Table of Contents](#table-of-contents)

## Useful links

- [SQL Server documentation](https://docs.microsoft.com/en-us/sql/sql-server/)
- [Grafana SQL Server dashboard](#) <!-- Update with actual link -->
- [Internal wiki - SQL Server runbooks](#) <!-- Update with actual link -->

[↑ Back to Table of Contents](#table-of-contents)

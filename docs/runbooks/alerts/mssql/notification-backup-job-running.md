# Notification: Backup job is running

**🔗 [← Back to SQL Server Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 19, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Type](https://img.shields.io/badge/Type-Notification-green)

> [!IMPORTANT]
> **Related Docs:** [Daily backup report](./report-daily-backup.md) | [Maintenance window starting](./notification-maintenance-window.md)

## Table of Contents

- [Summary](#summary)
- [Description](#description)
- [Notification contents](#notification-contents)
- [Actions required](#actions-required)
- [Monitoring backup progress](#monitoring-backup-progress)
- [Performance considerations](#performance-considerations)
- [Canceling a backup](#canceling-a-backup)
- [Related notifications](#related-notifications)
- [Additional resources](#additional-resources)

## Summary

| Attribute | Value |
|:---|:---|
| **Type** | Notification |
| **Severity** | Info |
| **Source** | SQL Server Agent / Monitoring System |
| **Delivery** | Email |
| **Trigger** | Backup job starts execution |

[↑ Back to Table of Contents](#table-of-contents)

## Description

Informational notification indicating that a scheduled or manual backup job has started execution. This notification helps track backup activity and provides awareness during backup windows when performance may be temporarily impacted.

[↑ Back to Table of Contents](#table-of-contents)

## Notification contents

| Field | Description |
|:---|:---|
| Server name | SQL Server instance running the backup |
| Database name | Database being backed up |
| Backup type | Full, Differential, or Transaction Log |
| Job name | SQL Server Agent job name |
| Start time | When the backup began (UTC) |
| Estimated duration | Based on historical backup times |

[↑ Back to Table of Contents](#table-of-contents)

## Actions required

| Scenario | Action |
|:---|:---|
| Normal scheduled backup | No action required |
| Unexpected backup running | Verify who initiated and why |
| Backup taking longer than expected | Monitor disk I/O and check for blocking |
| Need to cancel backup | Contact DBA on-call before canceling |

[↑ Back to Table of Contents](#table-of-contents)

## Monitoring backup progress

### Check current backup status

```sql
-- View active backup operations
SELECT
    r.session_id,
    r.command,
    r.percent_complete,
    r.estimated_completion_time / 60000 AS est_minutes_remaining,
    t.text AS query_text
FROM sys.dm_exec_requests r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
WHERE r.command LIKE '%BACKUP%';
```

### Check backup history

```sql
-- View recent backup history
SELECT TOP 10
    database_name,
    backup_start_date,
    backup_finish_date,
    DATEDIFF(MINUTE, backup_start_date, backup_finish_date) AS duration_minutes,
    CASE type
        WHEN 'D' THEN 'Full'
        WHEN 'I' THEN 'Differential'
        WHEN 'L' THEN 'Log'
    END AS backup_type,
    CAST(backup_size / 1073741824.0 AS DECIMAL(10,2)) AS size_gb
FROM msdb.dbo.backupset
ORDER BY backup_start_date DESC;
```

[↑ Back to Table of Contents](#table-of-contents)

## Performance considerations

During backup operations:

- **I/O impact:** Backup reads can compete with production workloads
- **CPU usage:** Compression (if enabled) increases CPU utilization
- **Network:** Backups to network shares consume bandwidth

> [!NOTE]
> If users report slowness during backup windows, this is expected behavior. Consider adjusting backup schedules if impact is significant.

[↑ Back to Table of Contents](#table-of-contents)

## Canceling a backup

> [!WARNING]
> Only cancel backups if absolutely necessary. Canceled backups must be rerun to maintain recovery point objectives.

```sql
-- Find the session ID running the backup
SELECT session_id, command, percent_complete
FROM sys.dm_exec_requests
WHERE command LIKE '%BACKUP%';

-- Cancel the backup (replace XXX with session_id)
KILL XXX;
```

[↑ Back to Table of Contents](#table-of-contents)

## Related notifications

- [Daily backup report](./report-daily-backup.md)
- [Maintenance window starting](./notification-maintenance-window.md)

[↑ Back to Table of Contents](#table-of-contents)

## Additional resources

- [SQL Server backup best practices](https://docs.microsoft.com/en-us/sql/relational-databases/backup-restore/backup-overview-sql-server)

[↑ Back to Table of Contents](#table-of-contents)

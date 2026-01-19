# Report: Daily backup status

**🔗 [← Back to SQL Server Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 19, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Type](https://img.shields.io/badge/Type-Report-blue)

> [!IMPORTANT]
> **Related Docs:** [Backup job is running](./notification-backup-job-running.md) | [SQL Server Index](./README.md)

## Table of Contents

- [Summary](#summary)
- [Description](#description)
- [Report contents](#report-contents)
- [Actions required](#actions-required)
- [Troubleshooting failed backups](#troubleshooting-failed-backups)
- [Related alerts](#related-alerts)
- [Additional resources](#additional-resources)

## Summary

| Attribute | Value |
|:---|:---|
| **Type** | Report |
| **Severity** | Info |
| **Source** | SQL Server Agent Job |
| **Delivery** | Email |
| **Schedule** | Daily at 06:00 UTC |

[↑ Back to Table of Contents](#table-of-contents)

## Description

Daily automated report summarizing backup status for all SQL Server databases. The report includes full, differential, and transaction log backup completion status.

[↑ Back to Table of Contents](#table-of-contents)

## Report contents

The report includes the following information for each database:

| Column | Description |
|:---|:---|
| Database name | Name of the database |
| Last full backup | Date/time of most recent full backup |
| Last differential backup | Date/time of most recent differential backup |
| Last log backup | Date/time of most recent transaction log backup |
| Backup size | Size of the backup file |
| Backup duration | Time taken to complete backup |
| Status | Success or failure indicator |

[↑ Back to Table of Contents](#table-of-contents)

## Actions required

| Report status | Action |
|:---|:---|
| All backups successful | No action required |
| Full backup failed | Investigate immediately, rerun backup manually |
| Differential backup failed | Check disk space, verify backup job configuration |
| Log backup failed | Check disk space, verify backup destination accessibility |
| Backup older than SLA | Escalate to DBA team lead |

[↑ Back to Table of Contents](#table-of-contents)

## Troubleshooting failed backups

### 1. Check SQL Server Agent job history

```sql
-- View recent backup job history
SELECT
    j.name AS job_name,
    h.run_date,
    h.run_time,
    h.run_duration,
    CASE h.run_status
        WHEN 0 THEN 'Failed'
        WHEN 1 THEN 'Succeeded'
        WHEN 2 THEN 'Retry'
        WHEN 3 THEN 'Canceled'
    END AS status,
    h.message
FROM msdb.dbo.sysjobs j
JOIN msdb.dbo.sysjobhistory h ON j.job_id = h.job_id
WHERE j.name LIKE '%backup%'
    AND h.step_id = 0
ORDER BY h.run_date DESC, h.run_time DESC;
```

### 2. Verify backup destination has sufficient space

```bash
# Check disk space on backup share (Linux)
df -h /mnt/backup

# Check disk space on backup share (Windows PowerShell)
Get-PSDrive -PSProvider FileSystem
```

### 3. Check network connectivity to backup share

```bash
# Test connectivity to backup share
ping backup-server.example.com

# Test SMB access (Windows)
Test-Path "\\backup-server\sqlbackups"
```

### 4. Review SQL Server error log

```sql
-- Check recent error log entries
EXEC xp_readerrorlog 0, 1, 'backup';
```

### 5. Manually rerun failed backup

```sql
-- Example: Run full backup manually
BACKUP DATABASE [DatabaseName]
TO DISK = N'\\backup-server\sqlbackups\DatabaseName_Full.bak'
WITH COMPRESSION, CHECKSUM, STATS = 10;
```

[↑ Back to Table of Contents](#table-of-contents)

## Related alerts

- [Backup job is running](./notification-backup-job-running.md)

[↑ Back to Table of Contents](#table-of-contents)

## Additional resources

- [SQL Server backup best practices](https://docs.microsoft.com/en-us/sql/relational-databases/backup-restore/backup-overview-sql-server)

[↑ Back to Table of Contents](#table-of-contents)

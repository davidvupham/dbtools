# Alert: High CPU utilization

**🔗 [← Back to SQL Server Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 19, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Severity](https://img.shields.io/badge/Severity-Critical-red)

> [!IMPORTANT]
> **Related Docs:** [Blocking detected](./alert-blocking-detected.md) | [SQL Server Index](./README.md)

## Table of Contents

- [Summary](#summary)
- [Description](#description)
- [Troubleshooting steps](#troubleshooting-steps)
- [Related alerts](#related-alerts)
- [Additional resources](#additional-resources)

## Summary

| Attribute | Value |
|:---|:---|
| **Type** | Alert |
| **Severity** | Critical |
| **Source** | Prometheus / SQL Server Agent |
| **Delivery** | Email |
| **Threshold** | CPU > 90% for 5 minutes |

[↑ Back to Table of Contents](#table-of-contents)

## Description

This alert fires when SQL Server process CPU utilization exceeds 90% for more than 5 consecutive minutes. High CPU can indicate runaway queries, missing indexes, or inadequate server resources.

[↑ Back to Table of Contents](#table-of-contents)

## Troubleshooting steps

### 1. Connect to the server

```bash
# SSH to the database server
ssh dbadmin@<server-hostname>
```

### 2. Identify high CPU queries

```sql
-- Find currently running queries sorted by CPU
SELECT
    r.session_id,
    r.cpu_time,
    r.total_elapsed_time,
    t.text AS query_text,
    r.status
FROM sys.dm_exec_requests r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
WHERE r.cpu_time > 0
ORDER BY r.cpu_time DESC;
```

### 3. Check for missing indexes

```sql
-- Review missing index recommendations
SELECT TOP 10
    mig.index_group_handle,
    mid.statement AS table_name,
    mid.equality_columns,
    mid.inequality_columns,
    mid.included_columns,
    migs.user_seeks * migs.avg_total_user_cost AS impact
FROM sys.dm_db_missing_index_groups mig
JOIN sys.dm_db_missing_index_group_stats migs
    ON mig.index_group_handle = migs.group_handle
JOIN sys.dm_db_missing_index_details mid
    ON mig.index_handle = mid.index_handle
ORDER BY impact DESC;
```

### 4. Kill problematic session if needed

> [!WARNING]
> Only kill sessions after confirming with the application team. Document the session ID and query before terminating.

```sql
-- Kill a specific session (replace XXX with session_id)
KILL XXX;
```

### 5. Verify resolution

- Monitor CPU in Grafana/Prometheus dashboard
- Confirm alert clears within 5 minutes

[↑ Back to Table of Contents](#table-of-contents)

## Related alerts

- [Blocking detected](./alert-blocking-detected.md)

[↑ Back to Table of Contents](#table-of-contents)

## Additional resources

- [SQL Server CPU troubleshooting guide](https://docs.microsoft.com/en-us/sql/relational-databases/performance/troubleshoot-high-cpu-usage)

[↑ Back to Table of Contents](#table-of-contents)

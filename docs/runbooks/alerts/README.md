# Database alerts, reports, and notifications

**🔗 [← Back to Runbooks Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 19, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Topic](https://img.shields.io/badge/Topic-Alerts-red)

> [!IMPORTANT]
> **Platform Docs:** [SQL Server](./mssql/README.md) | [SSAS](./ssas/README.md) | [PostgreSQL](./postgresql/README.md) | [MongoDB](./mongodb/README.md) | [Snowflake](./snowflake/README.md) | [Linux](./linux/README.md) | [Windows](./windows/README.md)

This directory contains documentation for all database alerts, reports, and notifications across supported platforms. Each entry includes the alert description, severity, and troubleshooting steps.

## Table of Contents

- [Overview](#overview)
- [Directory structure](#directory-structure)
- [Alert catalog](#alert-catalog)
  - [SQL Server](#sql-server)
  - [SSAS](#ssas)
  - [PostgreSQL](#postgresql)
  - [MongoDB](#mongodb)
  - [Snowflake](#snowflake)
  - [Linux](#linux)
  - [Windows](#windows)
- [Severity levels](#severity-levels)
- [Naming conventions](#naming-conventions)
- [Related documentation](#related-documentation)

## Overview

| Platform | Alerts | Reports | Notifications | Documentation |
|:---|:---:|:---:|:---:|:---|
| SQL Server | X | X | X | [mssql/](./mssql/README.md) |
| SSAS | X | | | [ssas/](./ssas/README.md) |
| PostgreSQL | X | X | X | [postgresql/](./postgresql/README.md) |
| MongoDB | X | X | X | [mongodb/](./mongodb/README.md) |
| Snowflake | X | X | X | [snowflake/](./snowflake/README.md) |
| Linux | X | | | [linux/](./linux/README.md) |
| Windows | X | | | [windows/](./windows/README.md) |

[↑ Back to Table of Contents](#table-of-contents)

## Directory structure

```text
docs/runbooks/alerts/
├── README.md                          # This file (master index)
├── mssql/
│   ├── README.md                      # SQL Server overview and contacts
│   ├── alert-cpu-utilization.md
│   ├── alert-blocking-detected.md
│   ├── report-daily-backup.md
│   └── notification-maintenance-window.md
├── ssas/
│   ├── README.md                      # SSAS overview and contacts
│   └── alert-offline.md
├── linux/
│   ├── README.md                      # Linux overview and contacts
│   └── alert-cpu-load.md
├── windows/
│   ├── README.md                      # Windows overview and contacts
│   └── alert-cpu-load.md
├── postgresql/
│   ├── README.md
│   ├── alert-connection-pool-exhausted.md
│   └── ...
├── mongodb/
│   ├── README.md
│   ├── alert-replica-set-unhealthy.md
│   └── ...
└── snowflake/
    ├── README.md
    ├── alert-credit-consumption.md
    └── ...
```

[↑ Back to Table of Contents](#table-of-contents)

## Alert catalog

### SQL Server

| Name | Type | Severity | MIR3 | File |
|:---|:---|:---|:---:|:---|
| High CPU utilization | Alert | Critical | | [alert-cpu-utilization.md](./mssql/alert-cpu-utilization.md) |
| Blocking detected | Alert | Warning | | [alert-blocking-detected.md](./mssql/alert-blocking-detected.md) |
| Daily backup status | Report | Info | | [report-daily-backup.md](./mssql/report-daily-backup.md) |
| Backup job is running | Notification | Info | | [notification-backup-job-running.md](./mssql/notification-backup-job-running.md) |
| Maintenance window starting | Notification | Info | | [notification-maintenance-window.md](./mssql/notification-maintenance-window.md) |

[View all SQL Server →](./mssql/README.md)

### SSAS

| Name | Type | Severity | MIR3 | File |
|:---|:---|:---|:---:|:---|
| SSAS is offline | Alert | Critical | | [alert-offline.md](./ssas/alert-offline.md) |

[View all SSAS →](./ssas/README.md)

### PostgreSQL

| Name | Type | Severity | MIR3 | File |
|:---|:---|:---|:---:|:---|
| Connection pool exhausted | Alert | Critical | | [alert-connection-pool-exhausted.md](./postgresql/alert-connection-pool-exhausted.md) |
| Replication lag | Alert | Warning | | [alert-replication-lag.md](./postgresql/alert-replication-lag.md) |

[View all PostgreSQL →](./postgresql/README.md)

### MongoDB

| Name | Type | Severity | MIR3 | File |
|:---|:---|:---|:---:|:---|
| Replica set unhealthy | Alert | Critical | | [alert-replica-set-unhealthy.md](./mongodb/alert-replica-set-unhealthy.md) |
| High oplog usage | Alert | Warning | | [alert-oplog-usage.md](./mongodb/alert-oplog-usage.md) |

[View all MongoDB →](./mongodb/README.md)

### Snowflake

| Name | Type | Severity | MIR3 | File |
|:---|:---|:---|:---:|:---|
| Credit consumption spike | Alert | Warning | | [alert-credit-consumption.md](./snowflake/alert-credit-consumption.md) |
| Warehouse suspended | Alert | Info | | [alert-warehouse-suspended.md](./snowflake/alert-warehouse-suspended.md) |

[View all Snowflake →](./snowflake/README.md)

### Linux

| Name | Type | Severity | MIR3 | File |
|:---|:---|:---|:---:|:---|
| CPU load is critical | Alert | Critical | | [alert-cpu-load.md](./linux/alert-cpu-load.md) |

[View all Linux →](./linux/README.md)

### Windows

| Name | Type | Severity | MIR3 | File |
|:---|:---|:---|:---:|:---|
| CPU load is critical | Alert | Critical | | [alert-cpu-load.md](./windows/alert-cpu-load.md) |

[View all Windows →](./windows/README.md)

[↑ Back to Table of Contents](#table-of-contents)

## Severity levels

| Severity | Response time | Description |
|:---|:---|:---|
| **Critical** | Immediate | Service down or data at risk. Page on-call. |
| **Warning** | 30 minutes | Degraded performance or approaching limits. |
| **Info** | Next business day | Informational, no immediate action required. |

[↑ Back to Table of Contents](#table-of-contents)

## Naming conventions

Files follow this naming pattern:

```text
{type}-{descriptive-name}.md
```

| Type | Prefix | Example |
|:---|:---|:---|
| Alert | `alert-` | `alert-cpu-utilization.md` |
| Report | `report-` | `report-daily-backup.md` |
| Notification | `notification-` | `notification-maintenance-window.md` |

Common commands:

```bash
# List all alerts for a platform
ls mssql/alert-*

# List all reports across platforms
ls */report-*

# Find all critical alerts (search within files)
grep -l "Critical" */alert-*.md
```

[↑ Back to Table of Contents](#table-of-contents)

## Related documentation

- [Monitoring architecture](../../explanation/architecture/README.md)
- [On-call procedures](../README.md)

[↑ Back to Table of Contents](#table-of-contents)

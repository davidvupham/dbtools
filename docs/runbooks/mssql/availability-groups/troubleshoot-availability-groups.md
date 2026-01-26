# Troubleshoot SQL Server Always On Availability Groups

**[← Back to MSSQL Runbooks Index](../README.md)**

> **Document Version:** 2.0 (Refactored)
> **Last Updated:** January 26, 2026
> **Maintainers:** Database Infrastructure Team
> **Status:** Production

## Overview
This runbook provides a modular guide to troubleshooting SQL Server Always On Availability Groups.

## Troubleshooting Index

| Issue | Description | Script |
|:---|:---|:---|
| **[Replica in RESOLVING](./troubleshooting/01-replica-resolving-state.md)** | Replica is offline or not part of quorum | `check-cluster-node-status.ps1` |
| **[Database Not Synchronizing](./troubleshooting/02-database-not-synchronizing.md)** | Data movement suspended or stuck | `check-database-sync.sql` |
| **[Automatic Failover Failed](./troubleshooting/03-automatic-failover-failed.md)** | Primary failed but secondary didn't take over | `check-failover-readiness.sql` |
| **[Listener Connectivity](./troubleshooting/04-listener-connectivity.md)** | Apps cannot connect to listener | `check-listener-connectivity.ps1` |
| **[High Queues / Latency](./troubleshooting/05-high-queues-latency.md)** | Lag between primary and secondary | `check-queues.sql` |
| **[Endpoint/Certificate](./troubleshooting/06-endpoint-certificate-issues.md)** | Connection errors (1418, 35250) | `check-endpoint-status.sql` |
| **[Quorum Failure](./troubleshooting/07-quorum-failure.md)** | Entire cluster is offline | `check-cluster-quorum.ps1` |
| **[Split-Brain](./troubleshooting/08-split-brain.md)** | Multiple primaries detected | N/A |
| **[Database Reverting](./troubleshooting/09-database-reverting.md)** | Secondary undoing transactions | N/A |
| **[Max Failures Exceeded](./troubleshooting/10-max-failures-exceeded.md)** | Cluster stopped failing over | `check-ag-resource-status.ps1` |

## Cluster Issues
- **[Node Quarantined](./troubleshooting/11-cluster-node-quarantined.md)**
- **[Network Issues](./troubleshooting/12-cluster-network-issues.md)**
- **[Service Failures](./troubleshooting/13-cluster-service-failures.md)**

## Diagnostic Scripts

All scripts are located in `scripts/`.

### SQL Scripts (`scripts/sql/`)
- `check-ag-health.sql`
- `check-database-sync.sql`
- `check-failover-time-estimate.sql`
- `force-failover-allow-data-loss.sql` (⚠️ Dangerous)

### PowerShell Scripts (`scripts/powershell/`)
- `check-cluster-node-status.ps1`
- `generate-cluster-log.ps1`

# Troubleshoot SQL Server Always On Availability Groups

**[← Back to MSSQL Runbooks Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 26, 2026
> **Maintainers:** Database Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Platform](https://img.shields.io/badge/Platform-SQL_Server-blue)
![Type](https://img.shields.io/badge/Type-Runbook-orange)

> [!IMPORTANT]
> **On-Call Contact:** DBA On-Call (PagerDuty) | **Escalation:** Database Infrastructure Team
> **Related Docs:** [Failover Cluster Troubleshooting](#failover-cluster-issues) | [Microsoft AG Documentation](https://learn.microsoft.com/en-us/sql/database-engine/availability-groups/windows/overview-of-always-on-availability-groups-sql-server)

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick reference: Common issues](#quick-reference-common-issues)
- [Diagnostic tools and queries](#diagnostic-tools-and-queries)
- [Issue 1: Replica in RESOLVING state](#issue-1-replica-in-resolving-state)
- [Issue 2: Database not synchronizing](#issue-2-database-not-synchronizing)
- [Issue 3: Automatic failover did not occur](#issue-3-automatic-failover-did-not-occur)
- [Issue 4: Listener connectivity issues](#issue-4-listener-connectivity-issues)
- [Issue 5: High redo queue or log send queue](#issue-5-high-redo-queue-or-log-send-queue)
- [Issue 6: Endpoint and certificate problems](#issue-6-endpoint-and-certificate-problems)
- [Issue 7: Quorum failure](#issue-7-quorum-failure)
- [Issue 8: Split-brain scenario](#issue-8-split-brain-scenario)
- [Issue 9: Database in reverting state](#issue-9-database-in-reverting-state)
- [Issue 10: Maximum failures threshold exceeded](#issue-10-maximum-failures-threshold-exceeded)
- [Failover cluster issues](#failover-cluster-issues)
  - [Cluster node quarantined](#cluster-node-quarantined)
  - [Cluster network issues](#cluster-network-issues)
  - [Cluster service failures](#cluster-service-failures)
- [Forced failover procedure](#forced-failover-procedure)
- [Post-incident recovery](#post-incident-recovery)
- [Monitoring and prevention](#monitoring-and-prevention)
- [Additional resources](#additional-resources)
- [Appendix A: SQL diagnostic queries](#appendix-a-sql-diagnostic-queries)
- [Appendix B: PowerShell diagnostic commands](#appendix-b-powershell-diagnostic-commands)
- [Appendix C: Common AG operations](#appendix-c-common-ag-operations)

## Overview

SQL Server Always On Availability Groups (AG) provide high availability and disaster recovery for databases. AGs depend on Windows Server Failover Clustering (WSFC) for health monitoring, quorum management, and automatic failover capabilities.

This runbook covers troubleshooting procedures for common AG issues, including:
- Replica state problems (RESOLVING, NOT SYNCHRONIZING)
- Failover failures (automatic and manual)
- Connectivity and listener issues
- Performance problems (redo queue, send queue)
- Underlying Windows Failover Cluster issues

[↑ Back to Table of Contents](#table-of-contents)

## Prerequisites

Before troubleshooting, ensure you have:

- [ ] VPN connectivity to the database network
- [ ] SQL Server Management Studio (SSMS) 18.0 or later
- [ ] `sysadmin` role on all AG replicas
- [ ] Local administrator access on all cluster nodes
- [ ] Failover Cluster Manager access
- [ ] Access to Windows Event Viewer on all nodes
- [ ] Access to monitoring dashboards (Grafana/Prometheus)

**Required permissions for NT AUTHORITY\SYSTEM:**
- `VIEW SERVER STATE`
- `ALTER ANY AVAILABILITY GROUP`
- `CONNECT SQL`

[↑ Back to Table of Contents](#table-of-contents)

## Quick reference: Common issues

| Symptom | Likely cause | Quick check | Section |
|:---|:---|:---|:---|
| Replica shows RESOLVING | Lease/health timeout, cluster issues | Check cluster node status | [Issue 1](#issue-1-replica-in-resolving-state) |
| Database NOT SYNCHRONIZING | Suspended data movement, disk space | Check `sys.dm_hadr_database_replica_states` | [Issue 2](#issue-2-database-not-synchronizing) |
| No automatic failover | Sync state, permissions, threshold | Check `is_failover_ready` | [Issue 3](#issue-3-automatic-failover-did-not-occur) |
| Cannot connect to listener | DNS, multi-subnet, IP offline | Ping listener, check DNS | [Issue 4](#issue-4-listener-connectivity-issues) |
| High latency/lag | Redo blocked, network, IO | Check redo_queue_size | [Issue 5](#issue-5-high-redo-queue-or-log-send-queue) |
| Replicas disconnected | Endpoint, certificate, firewall | Check endpoint state | [Issue 6](#issue-6-endpoint-and-certificate-problems) |
| Cluster offline | Quorum loss | Check cluster quorum | [Issue 7](#issue-7-quorum-failure) |
| Multiple primaries | Split-brain | Check quorum state | [Issue 8](#issue-8-split-brain-scenario) |

[↑ Back to Table of Contents](#table-of-contents)

## Diagnostic tools and queries

### Check AG health status

```sql
-- Comprehensive AG health check
SELECT
    ag.name AS ag_name,
    ar.replica_server_name,
    ars.role_desc,
    ars.operational_state_desc,
    ars.connected_state_desc,
    ars.synchronization_health_desc,
    ars.last_connect_error_number,
    ars.last_connect_error_description
FROM sys.availability_groups ag
JOIN sys.availability_replicas ar ON ag.group_id = ar.group_id
JOIN sys.dm_hadr_availability_replica_states ars ON ar.replica_id = ars.replica_id
ORDER BY ag.name, ar.replica_server_name;
```

### Check database synchronization state

```sql
-- Database-level sync status
SELECT
    ag.name AS ag_name,
    ar.replica_server_name,
    db.name AS database_name,
    drs.synchronization_state_desc,
    drs.synchronization_health_desc,
    drs.is_suspended,
    drs.suspend_reason_desc,
    drs.log_send_queue_size / 1024.0 AS log_send_queue_mb,
    drs.redo_queue_size / 1024.0 AS redo_queue_mb,
    drs.last_hardened_time,
    drs.last_redone_time
FROM sys.availability_groups ag
JOIN sys.availability_replicas ar ON ag.group_id = ar.group_id
JOIN sys.dm_hadr_database_replica_states drs ON ar.replica_id = drs.replica_id
JOIN sys.databases db ON drs.database_id = db.database_id
ORDER BY ag.name, ar.replica_server_name, db.name;
```

### Check failover readiness

```sql
-- Verify all databases are failover-ready
SELECT
    ar.replica_server_name,
    drcs.database_name,
    drcs.is_failover_ready,
    drs.synchronization_state_desc
FROM sys.dm_hadr_database_replica_cluster_states drcs
JOIN sys.dm_hadr_database_replica_states drs
    ON drcs.replica_id = drs.replica_id AND drcs.group_database_id = drs.group_database_id
JOIN sys.availability_replicas ar ON drcs.replica_id = ar.replica_id
ORDER BY ar.replica_server_name, drcs.database_name;
```

### Check Windows Cluster status (PowerShell)

```powershell
# Check cluster node status
Get-ClusterNode | Select-Object Name, State, NodeWeight

# Check cluster quorum status
Get-ClusterQuorum | Select-Object Cluster, QuorumResource, QuorumType

# Check AG cluster resource status
Get-ClusterResource | Where-Object {$_.ResourceType -eq "SQL Server Availability Group"} |
    Select-Object Name, State, OwnerNode

# Generate cluster log for troubleshooting
Get-ClusterLog -Destination C:\Temp -TimeSpan 60
```

### View Always On health extended events

```sql
-- Check for health events (run on primary)
SELECT
    XEL.object_name AS event_name,
    XEL.event_data.value('(event/@timestamp)[1]', 'datetime2') AS event_time,
    XEL.event_data.value('(event/data[@name="availability_group_name"]/value)[1]', 'varchar(50)') AS ag_name,
    XEL.event_data.value('(event/data[@name="error_number"]/value)[1]', 'int') AS error_number,
    XEL.event_data.value('(event/data[@name="message"]/value)[1]', 'varchar(max)') AS message
FROM (
    SELECT object_name, CAST(event_data AS XML) AS event_data
    FROM sys.fn_xe_file_target_read_file(
        'AlwaysOn_health*.xel', NULL, NULL, NULL
    )
) XEL
WHERE XEL.object_name IN ('error_reported', 'availability_replica_state_change',
    'availability_group_lease_expired', 'alwayson_ddl_executed')
ORDER BY event_time DESC;
```

[↑ Back to Table of Contents](#table-of-contents)

## Issue 1: Replica in RESOLVING state

### Symptoms

- AG dashboard shows replica in "Resolving" state
- Databases are not accessible on the affected replica
- Error: "The local node is not part of quorum"

### Causes

1. **Lease timeout** (default 20 seconds) - SQL Server thread failed to respond to cluster health check
2. **Health check timeout** (default 30 seconds) - ODBC connection to SQL Server timed out
3. **Maximum failures threshold exceeded** - Too many failovers in the specified period
4. **Cluster node issues** - Node down, quarantined, or network isolated
5. **Non-yielding scheduler** - SQL Server under heavy load (CPU/IO)

### Troubleshooting steps

#### Step 1: Check cluster node status

```powershell
# Check if node is online
Get-ClusterNode | Select-Object Name, State

# Check if node is quarantined
Get-ClusterNode | Select-Object Name, State, DrainStatus, QuarantineStatus
```

If node is DOWN:
1. Investigate hardware/OS issues
2. Start cluster service: `Start-ClusterNode -Name <NodeName>`

If node is QUARANTINED:
```powershell
# Clear quarantine status
Start-ClusterNode -Name <NodeName> -ClearQuarantine
```

#### Step 2: Check cluster logs for cause

```powershell
# Generate and review cluster log
Get-ClusterLog -Destination C:\Temp -TimeSpan 30

# Search for relevant events (in the generated log file)
Select-String -Path "C:\Temp\*.log" -Pattern "lease|timeout|quorum|heartbeat" -Context 2,2
```

#### Step 3: Check SQL Server error log

```sql
-- Check for lease/health timeouts
EXEC xp_readerrorlog 0, 1, N'lease';
EXEC xp_readerrorlog 0, 1, N'timeout';
EXEC xp_readerrorlog 0, 1, N'availability';
```

#### Step 4: Check NT AUTHORITY\SYSTEM permissions

```sql
-- Verify required permissions
SELECT
    p.name AS login_name,
    sp.permission_name,
    sp.state_desc
FROM sys.server_permissions sp
JOIN sys.server_principals p ON sp.grantee_principal_id = p.principal_id
WHERE p.name = 'NT AUTHORITY\SYSTEM';

-- Grant if missing
GRANT VIEW SERVER STATE TO [NT AUTHORITY\SYSTEM];
GRANT CONNECT SQL TO [NT AUTHORITY\SYSTEM];
```

#### Step 5: Check for resource exhaustion

```sql
-- Check for scheduler issues
SELECT
    scheduler_id,
    cpu_id,
    status,
    is_online,
    current_tasks_count,
    runnable_tasks_count
FROM sys.dm_os_schedulers
WHERE status = 'VISIBLE ONLINE';

-- Check for non-yielding conditions (in error log)
EXEC xp_readerrorlog 0, 1, N'non-yielding';
```

### Resolution

If the cluster and node are healthy but AG is still RESOLVING:

```sql
-- Perform forced failover if needed (WITH DATA LOSS)
-- Only use this after confirming primary is permanently unavailable
ALTER AVAILABILITY GROUP [AGName] FORCE_FAILOVER_ALLOW_DATA_LOSS;
```

> [!WARNING]
> Forced failover may result in data loss. Only use when the primary is unrecoverable and you need to restore service immediately.

[↑ Back to Table of Contents](#table-of-contents)

## Issue 2: Database not synchronizing

### Symptoms

- Database shows "Not Synchronizing" in AG dashboard
- Database may be in "Recovery Pending" state
- Data movement is suspended

### Causes

1. **Data movement suspended** - Explicitly paused by administrator
2. **Disk space exhaustion** - Log file cannot grow
3. **File access issues** - Data or log file inaccessible
4. **Seeding issues** - Direct seeding interrupted by log backups
5. **Network issues** - Connectivity between replicas

### Troubleshooting steps

#### Step 1: Check if data movement is suspended

```sql
-- Check suspension status
SELECT
    db.name AS database_name,
    drs.is_suspended,
    drs.suspend_reason_desc,
    drs.synchronization_state_desc
FROM sys.dm_hadr_database_replica_states drs
JOIN sys.databases db ON drs.database_id = db.database_id
WHERE drs.is_suspended = 1;
```

If suspended, resume data movement:

```sql
-- Resume via T-SQL
ALTER DATABASE [DatabaseName] SET HADR RESUME;

-- Or via SSMS: Right-click database > Resume Data Movement
```

#### Step 2: Check disk space

```sql
-- Check disk space on all drives
SELECT
    volume_mount_point AS drive,
    CAST(available_bytes / 1073741824.0 AS DECIMAL(10,2)) AS free_gb,
    CAST(total_bytes / 1073741824.0 AS DECIMAL(10,2)) AS total_gb
FROM sys.master_files f
CROSS APPLY sys.dm_os_volume_stats(f.database_id, f.file_id)
GROUP BY volume_mount_point, available_bytes, total_bytes;
```

#### Step 3: Check for file access issues

```sql
-- Check error log for file access errors
EXEC xp_readerrorlog 0, 1, N'not available';
EXEC xp_readerrorlog 0, 1, N'Operating system error';
```

If database is in Recovery Pending due to file issues:

```sql
-- After resolving file access, bring database online
ALTER DATABASE [DatabaseName] SET ONLINE;
```

#### Step 4: Check for seeding issues (SQL Server 2016+)

```sql
-- Check seeding status
SELECT
    ag.name AS ag_name,
    ar.replica_server_name,
    d.name AS database_name,
    has.current_state,
    has.failure_state_desc,
    has.error_code,
    has.performed_seeding,
    has.start_time_utc,
    has.end_time_utc
FROM sys.dm_hadr_automatic_seeding has
JOIN sys.availability_groups ag ON ag.group_id = has.ag_id
JOIN sys.availability_replicas ar ON ar.replica_id = has.ag_remote_replica_id
LEFT JOIN sys.databases d ON d.group_database_id = has.ag_db_id;
```

> [!TIP]
> If using automatic seeding, temporarily disable transaction log backups during initial sync to prevent seeding failures.

#### Step 5: Check network connectivity

```powershell
# Test connectivity to other replicas
Test-NetConnection -ComputerName <OtherReplicaName> -Port 5022
```

### Resolution for persistent issues

If other methods fail:

1. Remove database from AG on secondary
2. Restore database from backup with `NORECOVERY`
3. Re-add database to AG

```sql
-- On secondary
ALTER DATABASE [DatabaseName] SET HADR OFF;

-- Restore from backup
RESTORE DATABASE [DatabaseName]
FROM DISK = 'BackupPath'
WITH NORECOVERY;

-- Re-join to AG
ALTER DATABASE [DatabaseName] SET HADR AVAILABILITY GROUP = [AGName];
```

[↑ Back to Table of Contents](#table-of-contents)

## Issue 3: Automatic failover did not occur

### Symptoms

- Primary replica failed but AG did not failover automatically
- Secondary remains secondary despite primary being unavailable
- AG remains in RESOLVING state

### Causes

1. **Not all databases synchronized** - Even one database out of sync prevents failover
2. **Secondary not configured for automatic failover** - Missing configuration
3. **NT AUTHORITY\SYSTEM lacks permissions** - Cannot perform health check
4. **Maximum failures threshold reached** - Cluster prevents further failovers
5. **Failure condition level too low** - Health issue not monitored

### Troubleshooting steps

#### Step 1: Verify failover mode configuration

```sql
-- Check failover configuration
SELECT
    ar.replica_server_name,
    ar.availability_mode_desc,
    ar.failover_mode_desc,
    ar.seeding_mode_desc
FROM sys.availability_replicas ar;
```

Requirements for automatic failover:
- Primary AND one secondary must have `availability_mode = SYNCHRONOUS_COMMIT`
- Both must have `failover_mode = AUTOMATIC`
- Maximum 2 replicas can be automatic failover partners

#### Step 2: Check database failover readiness

```sql
-- All databases MUST show is_failover_ready = 1
SELECT
    ar.replica_server_name,
    drcs.database_name,
    drcs.is_failover_ready,
    drs.synchronization_state_desc,
    drs.synchronization_health_desc
FROM sys.dm_hadr_database_replica_cluster_states drcs
JOIN sys.dm_hadr_database_replica_states drs
    ON drcs.replica_id = drs.replica_id
    AND drcs.group_database_id = drs.group_database_id
JOIN sys.availability_replicas ar ON drcs.replica_id = ar.replica_id
WHERE drcs.is_failover_ready = 0;
```

> [!IMPORTANT]
> If ANY database shows `is_failover_ready = 0`, automatic failover will NOT occur. All databases in the AG must be synchronized.

#### Step 3: Check maximum failures threshold

```powershell
# Check cluster resource properties
Get-ClusterResource -Name "<AG_Resource_Name>" | Get-ClusterParameter |
    Where-Object {$_.Name -like "*Failure*"} |
    Select-Object Name, Value
```

Default: 3 failures in 6 hours (360 minutes)

```powershell
# Increase threshold if needed (temporary, for troubleshooting)
Get-ClusterResource -Name "<AG_Resource_Name>" |
    Set-ClusterParameter -Name "FailoverThreshold" -Value 5
```

#### Step 4: Check failure condition level

```sql
-- Check current failure condition level
SELECT
    ag.name,
    ag.failure_condition_level,
    ag.health_check_timeout
FROM sys.availability_groups ag;

-- Failure condition levels:
-- 1: SQL Server service is down
-- 2: SQL Server does not respond to health checks (lease timeout)
-- 3: (Default) Critical SQL Server errors (spinlock, write violation, dump)
-- 4: Moderate SQL Server errors (persistent out of memory)
-- 5: Any qualified failure condition
```

#### Step 5: Verify NT AUTHORITY\SYSTEM permissions on secondary

```sql
-- Run on SECONDARY replica
SELECT
    p.name AS login_name,
    sp.permission_name
FROM sys.server_permissions sp
JOIN sys.server_principals p ON sp.grantee_principal_id = p.principal_id
WHERE p.name = 'NT AUTHORITY\SYSTEM';

-- Grant required permissions
GRANT VIEW SERVER STATE TO [NT AUTHORITY\SYSTEM];
GRANT ALTER ANY AVAILABILITY GROUP TO [NT AUTHORITY\SYSTEM];
```

[↑ Back to Table of Contents](#table-of-contents)

## Issue 4: Listener connectivity issues

### Symptoms

- Applications cannot connect to AG listener
- Connection timeout errors
- Intermittent connectivity after failover

### Causes

1. **Multi-subnet configuration issues** - Client not using MultiSubnetFailover
2. **DNS resolution problems** - Wrong IP returned
3. **Listener IP offline** - Cluster resource failed
4. **RegisterAllProvidersIP setting** - Multiple IPs registered in DNS
5. **Active Directory permissions** - Listener creation failed

### Troubleshooting steps

#### Step 1: Verify listener configuration

```sql
-- Check listener details
SELECT
    ag.name AS ag_name,
    agl.dns_name,
    agl.port,
    lip.ip_address,
    lip.ip_subnet_mask,
    lip.state_desc
FROM sys.availability_group_listeners agl
JOIN sys.availability_groups ag ON agl.group_id = ag.group_id
JOIN sys.availability_group_listener_ip_addresses lip ON agl.listener_id = lip.listener_id;
```

#### Step 2: Test listener connectivity

```powershell
# Test DNS resolution
Resolve-DnsName -Name <ListenerDnsName>

# Test TCP connectivity
Test-NetConnection -ComputerName <ListenerDnsName> -Port <ListenerPort>

# Check which IP is online (from cluster)
Get-ClusterResource | Where-Object {$_.ResourceType -like "IP Address"} |
    Get-ClusterParameter | Select-Object ClusterObject, Name, Value
```

#### Step 3: Check client connection string

For multi-subnet AGs, clients MUST use:

```
Server=ListenerName;Database=DBName;MultiSubnetFailover=True
```

Or for legacy applications that cannot use MultiSubnetFailover:

```powershell
# Change RegisterAllProvidersIP to 0 (only active IP in DNS)
Get-ClusterResource -Name "<ListenerResourceName>" |
    Set-ClusterParameter RegisterAllProvidersIP 0

# Reduce DNS TTL for faster failover
Get-ClusterResource -Name "<ListenerResourceName>" |
    Set-ClusterParameter HostRecordTTL 300
```

#### Step 4: Check listener creation permissions (if creating new)

The Cluster Name Object (CNO) requires:
- "Create Computer objects" permission in Active Directory
- Appropriate OU permissions

```powershell
# Verify CNO has required AD permissions
Get-ClusterResource -Name "Cluster Name" | Get-ClusterParameter
```

#### Step 5: Check firewall rules

```powershell
# Verify port is open on all nodes
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*SQL*" -or $_.DisplayName -like "*1433*"}

# Create firewall rule if missing
New-NetFirewallRule -DisplayName "SQL Server Listener" -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow
```

[↑ Back to Table of Contents](#table-of-contents)

## Issue 5: High redo queue or log send queue

### Symptoms

- High latency between primary and secondary
- Failover takes longer than expected
- Synchronization health shows warning/critical

### Understanding the queues

| Queue | Location | Impact | Concern |
|:---|:---|:---|:---|
| **Log Send Queue** | Primary | Data not yet sent to secondary | Potential data loss (RPO) |
| **Redo Queue** | Secondary | Received but not applied | Failover time (RTO) |

### Troubleshooting steps

#### Step 1: Check current queue sizes

```sql
-- Monitor queue sizes
SELECT
    ar.replica_server_name,
    db.name AS database_name,
    drs.log_send_queue_size / 1024.0 AS send_queue_mb,
    drs.redo_queue_size / 1024.0 AS redo_queue_mb,
    drs.log_send_rate / 1024.0 AS send_rate_kbps,
    drs.redo_rate / 1024.0 AS redo_rate_kbps,
    CASE
        WHEN drs.redo_rate > 0
        THEN drs.redo_queue_size / drs.redo_rate
        ELSE 0
    END AS estimated_redo_time_seconds
FROM sys.dm_hadr_database_replica_states drs
JOIN sys.availability_replicas ar ON drs.replica_id = ar.replica_id
JOIN sys.databases db ON drs.database_id = db.database_id
ORDER BY drs.redo_queue_size DESC;
```

#### Step 2: Check for blocked redo thread (secondary)

```sql
-- Check for blocking on secondary (run on secondary)
SELECT
    wait_type,
    waiting_tasks_count,
    wait_time_ms,
    max_wait_time_ms
FROM sys.dm_os_wait_stats
WHERE wait_type IN ('HADR_SYNC_COMMIT', 'HADR_DATABASE_FLOW_CONTROL',
    'HADR_LOG_SEND', 'HADR_TRANSPORT_RECV', 'PARALLEL_REDO_WORKER_WAIT_WORK')
ORDER BY wait_time_ms DESC;
```

#### Step 3: Check for reporting queries blocking redo

```sql
-- Check for Sch-S locks blocking redo (run on secondary)
SELECT
    resource_type,
    resource_database_id,
    request_mode,
    request_type,
    request_status,
    request_session_id
FROM sys.dm_tran_locks
WHERE request_mode = 'Sch-S' AND resource_type = 'OBJECT';

-- Check AlwaysOn_health for blocked redo
-- Open Extended Events: AlwaysOn_health*.xel
-- Filter for 'redo_blocked_low_memory' or 'redo_blocked_exception'
```

#### Step 4: Check flow control

```sql
-- Check flow control delays (run on primary)
SELECT
    ar.replica_server_name,
    fc.database_name,
    fc.flow_control_active,
    fc.flow_control_send_wait_ms
FROM sys.dm_hadr_database_replica_states drs
CROSS APPLY sys.fn_hadr_database_flow_control_info(drs.database_id) fc
JOIN sys.availability_replicas ar ON drs.replica_id = ar.replica_id;
```

#### Step 5: Check network latency

```powershell
# Test network latency to secondary
Test-Connection -ComputerName <SecondaryReplicaName> -Count 10 |
    Measure-Object -Property ResponseTime -Average -Minimum -Maximum
```

### Resolution

For high redo queue:
1. Disable or limit reporting queries on secondary
2. Check for schema modification operations (DDL)
3. Increase secondary hardware resources (CPU/IO)

For high send queue:
1. Check network bandwidth between sites
2. Consider asynchronous commit for remote replicas
3. Evaluate workload distribution

[↑ Back to Table of Contents](#table-of-contents)

## Issue 6: Endpoint and certificate problems

### Symptoms

- Replicas show DISCONNECTED state
- Error 1418: Server network address cannot be reached
- Error 35250: Connection to replica failed
- Certificate-related errors in SQL Server error log

### Troubleshooting steps

#### Step 1: Check endpoint configuration

```sql
-- Check endpoint status on all replicas
SELECT
    name,
    protocol_desc,
    type_desc,
    state_desc,
    port,
    ip_address,
    encryption_algorithm_desc
FROM sys.tcp_endpoints
WHERE type_desc = 'DATABASE_MIRRORING';

-- Check endpoint permissions
SELECT
    spe.class_desc,
    spe.permission_name,
    spe.state_desc,
    sp.name AS principal_name
FROM sys.server_permissions spe
JOIN sys.server_principals sp ON spe.grantee_principal_id = sp.principal_id
WHERE spe.class = 105; -- ENDPOINT class
```

#### Step 2: Verify endpoint is started

```sql
-- Start endpoint if stopped
ALTER ENDPOINT [Hadr_endpoint] STATE = STARTED;
```

#### Step 3: Check certificate expiration

```sql
-- Check certificate details
SELECT
    name,
    certificate_id,
    start_date,
    expiry_date,
    DATEDIFF(day, GETDATE(), expiry_date) AS days_until_expiry
FROM sys.certificates
WHERE name LIKE '%hadr%' OR name LIKE '%mirror%' OR name LIKE '%endpoint%';
```

> [!WARNING]
> Expired certificates will cause AG communication to fail. Monitor certificate expiration proactively.

#### Step 4: Test port connectivity

```powershell
# Test endpoint port from each replica to others
Test-NetConnection -ComputerName <OtherReplicaName> -Port 5022
```

#### Step 5: Check firewall rules

```powershell
# Verify endpoint port is allowed
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*5022*" -or $_.DisplayName -like "*mirroring*"}

# Create rule if missing
New-NetFirewallRule -DisplayName "AG Endpoint" -Direction Inbound -Protocol TCP -LocalPort 5022 -Action Allow
```

### Resolution for certificate issues

```sql
-- If certificate expired, create new certificate
CREATE CERTIFICATE AGCert_New
    WITH SUBJECT = 'AG Endpoint Certificate',
    EXPIRY_DATE = '20280101';

-- Update endpoint to use new certificate
ALTER ENDPOINT [Hadr_endpoint]
    FOR DATABASE_MIRRORING (
        AUTHENTICATION = CERTIFICATE AGCert_New
    );

-- Exchange certificates with other replicas
-- Backup, copy, and create certificate from file on each replica
```

[↑ Back to Table of Contents](#table-of-contents)

## Issue 7: Quorum failure

### Symptoms

- All cluster services offline
- AG resources fail to come online
- Error: "Cluster service has terminated because quorum was lost"

### Understanding quorum

- Quorum requires majority of votes (N/2 + 1) to be online
- Votes come from nodes and witness (file share or cloud witness)
- Without quorum, cluster takes all resources offline to prevent split-brain

### Troubleshooting steps

#### Step 1: Check current quorum status

```powershell
# Check quorum state
Get-ClusterQuorum | Select-Object Cluster, QuorumResource, QuorumType

# Check node votes
Get-ClusterNode | Select-Object Name, State, NodeWeight, DynamicWeight

# Check cluster health
Get-Cluster | Select-Object Name, QuorumType, CrossSiteThreshold
```

#### Step 2: Determine cause of quorum loss

```powershell
# Generate cluster log
Get-ClusterLog -Destination C:\Temp -TimeSpan 60

# Search for quorum-related events
Select-String -Path "C:\Temp\*.log" -Pattern "quorum|vote|witness" -Context 3,3
```

Common causes:
- Multiple nodes failed simultaneously
- Network partition isolated nodes
- Witness became unavailable

#### Step 3: Restore quorum (if possible)

If nodes are available but cluster is down:

```powershell
# Force start cluster on a node (use on most up-to-date node)
Start-ClusterNode -Name <NodeName> -FixQuorum
```

> [!CAUTION]
> Force quorum only on the node with the most recent data. This makes that node's cluster database authoritative.

#### Step 4: Verify AG state after quorum restoration

After forcing quorum, AG will be in RESOLVING state:

```sql
-- Check AG state
SELECT name, replica_server_name, role_desc
FROM sys.dm_hadr_availability_replica_states;

-- AG will need forced failover (see Forced Failover section)
```

### Prevention

- Use odd number of votes
- Configure cluster witness (file share or Azure cloud witness)
- Monitor witness availability
- Consider dynamic quorum in Windows Server 2012 R2+

[↑ Back to Table of Contents](#table-of-contents)

## Issue 8: Split-brain scenario

### Symptoms

- Multiple nodes believe they are primary
- Both sites accepting writes
- Data corruption risk

### Causes

1. Forced quorum on multiple sites simultaneously
2. Manual intervention during network partition
3. External cluster manager misconfiguration (Linux)

### Troubleshooting steps

#### Step 1: Identify the split-brain condition

```powershell
# Check cluster state on each site
Get-ClusterNode | Select-Object Name, State
Get-Cluster | Select-Object Name, QuorumType

# Check if cluster is in forced quorum mode
Get-Cluster | Select-Object Name, Quarantine*
```

```sql
-- Check which node thinks it's primary
SELECT replica_server_name, role_desc
FROM sys.dm_hadr_availability_replica_states
WHERE is_local = 1;
```

#### Step 2: Determine which site has the most current data

```sql
-- Check last hardened LSN on each site
SELECT
    ar.replica_server_name,
    drs.last_hardened_lsn,
    drs.last_hardened_time
FROM sys.dm_hadr_database_replica_states drs
JOIN sys.availability_replicas ar ON drs.replica_id = ar.replica_id
WHERE drs.database_id = DB_ID('YourDatabase');
```

The site with the highest `last_hardened_lsn` has the most recent data.

### Resolution

> [!CAUTION]
> Split-brain recovery may require data reconciliation. Document all changes made on each site before proceeding.

1. **Isolate the secondary site:**
   ```powershell
   # Stop cluster service on secondary site
   Stop-ClusterNode -Name <SecondaryNode>
   ```

2. **Clear forced quorum state on primary site:**
   ```powershell
   # Restart cluster normally
   Stop-Cluster
   Start-Cluster
   ```

3. **Rejoin secondary:**
   - Fix underlying issue (network, witness)
   - Start cluster node normally
   - May need to reseed AG databases

### Prevention

- Never force quorum on multiple sites
- Use proper witness configuration
- Have documented DR procedures
- Test failover procedures regularly

[↑ Back to Table of Contents](#table-of-contents)

## Issue 9: Database in reverting state

### Symptoms

- Database shows "Reverting" state on secondary
- Undo operations in progress
- Cannot failover to this replica

### Cause

Secondary must undo transactions that were committed locally but not on primary (typically after a failed failover attempt).

### Troubleshooting steps

#### Step 1: Check reverting status

```sql
-- Monitor reverting progress
SELECT
    db.name AS database_name,
    drs.synchronization_state_desc,
    drs.redo_queue_size / 1024.0 AS redo_queue_mb,
    drs.redo_rate / 1024.0 AS redo_rate_kbps
FROM sys.dm_hadr_database_replica_states drs
JOIN sys.databases db ON drs.database_id = db.database_id
WHERE drs.synchronization_state_desc = 'REVERTING';
```

### Resolution

> [!WARNING]
> Do NOT failover to a replica in reverting state - this may result in an unusable database requiring restore from backup.

Options:
1. **Wait** - Let the reverting process complete
2. **Do NOT restart SQL Server** - Restart will not speed up reverting
3. **Remove and reseed** - If reverting takes too long:

```sql
-- Remove from AG
ALTER AVAILABILITY GROUP [AGName] REMOVE DATABASE [DatabaseName];

-- Restore with NORECOVERY
RESTORE DATABASE [DatabaseName] FROM DISK = '...' WITH NORECOVERY;

-- Re-add to AG
ALTER DATABASE [DatabaseName] SET HADR AVAILABILITY GROUP = [AGName];
```

[↑ Back to Table of Contents](#table-of-contents)

## Issue 10: Maximum failures threshold exceeded

### Symptoms

- AG fails to failover
- Cluster log shows "failoverCount > computedFailoverThreshold"
- Replica stuck in RESOLVING

### Cause

Cluster resource failed too many times within the monitoring period (default: 3 failures in 6 hours).

### Troubleshooting steps

#### Step 1: Check failure threshold settings

```powershell
# Check current settings
Get-ClusterResource -Name "<AG_ResourceName>" | Get-ClusterParameter |
    Where-Object {$_.Name -match "Failure"}
```

#### Step 2: Check failure history

```powershell
# View recent failures
Get-ClusterResource -Name "<AG_ResourceName>" | Get-ClusterResourceState

# Check cluster events
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-FailoverClustering/Operational'; Level=2,3} -MaxEvents 50
```

#### Step 3: Address root cause

Before adjusting thresholds, identify and fix the underlying issue:
- Network instability
- Hardware problems
- SQL Server health issues
- Resource contention

### Resolution

Temporarily increase threshold to allow failover:

```powershell
# Increase threshold (use cautiously)
Get-ClusterResource -Name "<AG_ResourceName>" |
    Set-ClusterParameter -Name "FailureThreshold" -Value 10

Get-ClusterResource -Name "<AG_ResourceName>" |
    Set-ClusterParameter -Name "FailureInterval" -Value 360
```

> [!WARNING]
> Increasing the threshold without fixing the root cause may mask serious problems. Always investigate why failures occurred.

[↑ Back to Table of Contents](#table-of-contents)

## Failover cluster issues

### Cluster node quarantined

#### Symptoms
- Node shows "Quarantined" status
- Node cannot rejoin cluster
- AG resources unavailable on that node

#### Cause
Node failed 3+ times within 1 hour (Windows Server 2016+), triggering automatic quarantine for 2 hours.

#### Resolution

```powershell
# Clear quarantine
Start-ClusterNode -Name <NodeName> -ClearQuarantine

# Check quarantine settings
Get-Cluster | Select-Object QuarantineThreshold, QuarantineDuration

# Adjust settings if needed
(Get-Cluster).QuarantineThreshold = 5
(Get-Cluster).QuarantineDuration = 3600  # seconds
```

### Cluster network issues

#### Symptoms
- Nodes losing connectivity intermittently
- "Heartbeat lost" messages in cluster log
- Events 1135, 1177 in Windows event log

#### Troubleshooting

```powershell
# Check cluster network status
Get-ClusterNetwork | Select-Object Name, State, Role

# Check network adapters
Get-ClusterNetworkInterface | Select-Object Name, Node, Network, State

# Validate cluster
Test-Cluster -Node <Node1>,<Node2> -Include "Network"
```

#### Resolution
- Verify network adapter settings (speed, duplex)
- Check switch configuration
- Ensure dedicated heartbeat network
- Review network driver versions

### Cluster service failures

#### Symptoms
- Cluster service won't start
- Event ID 1069: Cluster resource failed
- Services dependent on cluster unavailable

#### Troubleshooting

```powershell
# Check service status
Get-Service -Name ClusSvc | Select-Object Name, Status, StartType

# Check cluster events
Get-WinEvent -LogName "Microsoft-Windows-FailoverClustering/Operational" -MaxEvents 20

# Verify cluster database
Get-ClusterLog -UseLocalTime -Destination C:\Temp
```

#### Resolution

```powershell
# Repair cluster service
Clear-ClusterNode -Force  # Use with caution

# Re-add node to cluster if needed
Add-ClusterNode -Name <NodeName> -Cluster <ClusterName>
```

[↑ Back to Table of Contents](#table-of-contents)

## Forced failover procedure

Use forced failover only when:
- Primary is permanently unavailable
- Service restoration is critical
- You accept potential data loss

### Pre-failover checks

```sql
-- Determine data loss (run on target secondary)
SELECT
    ar.replica_server_name,
    db.name AS database_name,
    drs.last_hardened_lsn,
    drs.end_of_log_lsn,
    drs.synchronization_state_desc
FROM sys.dm_hadr_database_replica_states drs
JOIN sys.availability_replicas ar ON drs.replica_id = ar.replica_id
JOIN sys.databases db ON drs.database_id = db.database_id
WHERE drs.is_local = 1;
```

### Forced failover steps

#### Step 1: Force cluster quorum (if needed)

```powershell
# On the secondary node you want to become primary
Start-ClusterNode -Name $env:COMPUTERNAME -FixQuorum
```

#### Step 2: Force AG failover

```sql
-- Connect to target secondary
-- This will result in data loss for any uncommitted transactions
ALTER AVAILABILITY GROUP [AGName] FORCE_FAILOVER_ALLOW_DATA_LOSS;
```

#### Step 3: Verify new primary

```sql
-- Confirm role change
SELECT
    replica_server_name,
    role_desc,
    synchronization_health_desc
FROM sys.dm_hadr_availability_replica_states;
```

#### Step 4: Resume databases (if needed)

```sql
-- Resume any suspended databases
ALTER DATABASE [DatabaseName] SET HADR RESUME;
```

### Post-failover actions

1. Update DNS if necessary
2. Verify application connectivity
3. Monitor for synchronization
4. Plan for original primary recovery
5. Document incident and data loss assessment

[↑ Back to Table of Contents](#table-of-contents)

## Post-incident recovery

### After primary recovery

When the original primary comes back online:

```sql
-- On recovered server, it will join as secondary
-- Check its synchronization state
SELECT
    ar.replica_server_name,
    drs.synchronization_state_desc,
    drs.synchronization_health_desc
FROM sys.dm_hadr_database_replica_states drs
JOIN sys.availability_replicas ar ON drs.replica_id = ar.replica_id;
```

### Resynchronize former primary

If the former primary cannot sync:

```sql
-- Remove database from AG on former primary
ALTER AVAILABILITY GROUP [AGName] REMOVE DATABASE [DatabaseName];

-- Drop database
DROP DATABASE [DatabaseName];

-- Restore from current primary backup
RESTORE DATABASE [DatabaseName] FROM DISK = '...' WITH NORECOVERY;

-- Rejoin AG
ALTER DATABASE [DatabaseName] SET HADR AVAILABILITY GROUP = [AGName];
```

### Transaction log considerations

After prolonged outage:

```sql
-- Check log size growth on primary (log truncation delayed)
SELECT
    db.name,
    mf.name AS file_name,
    mf.size * 8 / 1024 AS size_mb,
    mf.growth * 8 / 1024 AS growth_mb
FROM sys.master_files mf
JOIN sys.databases db ON mf.database_id = db.database_id
WHERE mf.type_desc = 'LOG';
```

Consider removing failed replica from AG to allow log truncation if recovery will be prolonged.

[↑ Back to Table of Contents](#table-of-contents)

## Monitoring and prevention

### Key metrics to monitor

| Metric | Warning threshold | Critical threshold |
|:---|:---|:---|
| Log send queue | > 100 MB | > 500 MB |
| Redo queue | > 500 MB | > 2 GB |
| Synchronization state | NOT SYNCHRONIZED | DISCONNECTED |
| Cluster quorum | Degraded | Lost |
| Certificate expiry | < 30 days | < 7 days |

### Recommended alerts

```sql
-- Alert: Database not synchronized
SELECT * FROM sys.dm_hadr_database_replica_states
WHERE synchronization_state_desc != 'SYNCHRONIZED';

-- Alert: High redo queue
SELECT * FROM sys.dm_hadr_database_replica_states
WHERE redo_queue_size > 524288; -- 512 MB

-- Alert: Replica disconnected
SELECT * FROM sys.dm_hadr_availability_replica_states
WHERE connected_state_desc = 'DISCONNECTED';
```

### Preventive maintenance

1. **Validate cluster monthly:**
   ```powershell
   Test-Cluster -Include All
   ```

2. **Test failover quarterly:**
   ```sql
   -- Planned manual failover (no data loss)
   ALTER AVAILABILITY GROUP [AGName] FAILOVER;
   ```

3. **Monitor certificate expiration:**
   ```sql
   SELECT name, expiry_date FROM sys.certificates
   WHERE expiry_date < DATEADD(month, 3, GETDATE());
   ```

4. **Review AG configuration after changes:**
   ```sql
   -- Generate AG configuration report
   SELECT * FROM sys.availability_groups;
   SELECT * FROM sys.availability_replicas;
   SELECT * FROM sys.availability_group_listeners;
   ```

[↑ Back to Table of Contents](#table-of-contents)

## Additional resources

### Microsoft documentation
- [Always On Availability Groups Overview](https://learn.microsoft.com/en-us/sql/database-engine/availability-groups/windows/overview-of-always-on-availability-groups-sql-server)
- [Troubleshooting Always On Issues](https://learn.microsoft.com/en-us/troubleshoot/sql/database-engine/availability-groups/troubleshooting-alwayson-issues)
- [Troubleshooting Availability Group Failover](https://learn.microsoft.com/en-us/troubleshoot/sql/database-engine/availability-groups/troubleshooting-availability-group-failover)
- [WSFC Disaster Recovery Through Forced Quorum](https://learn.microsoft.com/en-us/sql/sql-server/failover-clusters/windows/wsfc-disaster-recovery-through-forced-quorum-sql-server)
- [Troubleshooting Automatic Failover Problems](https://learn.microsoft.com/en-us/troubleshoot/sql/database-engine/availability-groups/troubleshooting-automatic-failover-problems)

### Community resources
- [Diagnose Unexpected Failover or AG in RESOLVING State](https://techcommunity.microsoft.com/t5/sql-server-support-blog/diagnose-unexpected-failover-or-availability-group-in-resolving/ba-p/318474)
- [Recover WSFC Using Forced Quorum](https://www.mssqltips.com/sqlservertip/4917/recover-wsfc-using-forced-quorum-for-sql-server-alwayson-availability-group/)
- [Troubleshoot AG with AGDiag](https://www.mssqltips.com/sqlservertip/7994/troubleshoot-sql-server-always-on-availability-groups-with-agdiag/)
- [The Smart Way to Troubleshoot AG Outages](https://learnsqlserverhadr.com/the-smart-way-troubleshooting-sql-server-cluster-ag-outages/)

### Tools
- **AGDiag** - Automated AG diagnostics tool
- **SQL LogScout** - Log collection for AG troubleshooting
- **Failover Cluster Manager** - GUI for cluster management
- **Always On Dashboard** - SSMS built-in monitoring

[↑ Back to Table of Contents](#table-of-contents)

---

## Appendix A: SQL diagnostic queries

### Complete AG health report

```sql
-- Comprehensive AG health dashboard query
SELECT
    ag.name AS ag_name,
    ar.replica_server_name,
    ar.availability_mode_desc,
    ar.failover_mode_desc,
    ars.role_desc,
    ars.operational_state_desc,
    ars.connected_state_desc,
    ars.recovery_health_desc,
    ars.synchronization_health_desc,
    ars.last_connect_error_number,
    ars.last_connect_error_description,
    ars.last_connect_error_timestamp
FROM sys.availability_groups ag
INNER JOIN sys.availability_replicas ar ON ag.group_id = ar.group_id
INNER JOIN sys.dm_hadr_availability_replica_states ars ON ar.replica_id = ars.replica_id
ORDER BY ag.name, ar.replica_server_name;
```

### Database-level detail report

```sql
-- Detailed database synchronization report
SELECT
    ag.name AS ag_name,
    ar.replica_server_name,
    adc.database_name,
    drs.is_local,
    drs.is_primary_replica,
    drs.synchronization_state_desc,
    drs.synchronization_health_desc,
    drs.database_state_desc,
    drs.is_suspended,
    drs.suspend_reason_desc,
    drs.last_sent_time,
    drs.last_received_time,
    drs.last_hardened_time,
    drs.last_redone_time,
    drs.log_send_queue_size / 1024.0 AS log_send_queue_mb,
    drs.log_send_rate / 1024.0 AS log_send_rate_kbps,
    drs.redo_queue_size / 1024.0 AS redo_queue_mb,
    drs.redo_rate / 1024.0 AS redo_rate_kbps,
    drs.filestream_send_rate / 1024.0 AS filestream_send_rate_kbps,
    drs.end_of_log_lsn,
    drs.last_hardened_lsn,
    drs.last_redone_lsn,
    drs.last_commit_lsn,
    drs.last_commit_time,
    drs.low_water_mark_for_ghosts
FROM sys.availability_groups ag
INNER JOIN sys.availability_replicas ar ON ag.group_id = ar.group_id
INNER JOIN sys.dm_hadr_database_replica_states drs ON ar.replica_id = drs.replica_id
INNER JOIN sys.availability_databases_cluster adc ON drs.group_database_id = adc.group_database_id
ORDER BY ag.name, ar.replica_server_name, adc.database_name;
```

### Estimate failover time (RTO)

```sql
-- Calculate estimated failover time based on redo queue
SELECT
    ar.replica_server_name,
    adc.database_name,
    drs.redo_queue_size / 1024.0 AS redo_queue_mb,
    drs.redo_rate / 1024.0 AS redo_rate_kbps,
    CASE
        WHEN drs.redo_rate > 0
        THEN CAST(drs.redo_queue_size / drs.redo_rate AS DECIMAL(10,2))
        ELSE -1
    END AS estimated_redo_seconds,
    CASE
        WHEN drs.redo_rate > 0
        THEN CAST((drs.redo_queue_size / drs.redo_rate) / 60.0 AS DECIMAL(10,2))
        ELSE -1
    END AS estimated_redo_minutes
FROM sys.dm_hadr_database_replica_states drs
INNER JOIN sys.availability_replicas ar ON drs.replica_id = ar.replica_id
INNER JOIN sys.availability_databases_cluster adc ON drs.group_database_id = adc.group_database_id
WHERE drs.is_local = 0  -- Remote replicas only
ORDER BY drs.redo_queue_size DESC;
```

### Estimate data loss (RPO)

```sql
-- Calculate potential data loss based on send queue
SELECT
    ar.replica_server_name,
    adc.database_name,
    ar.availability_mode_desc,
    drs.log_send_queue_size / 1024.0 AS send_queue_mb,
    drs.last_sent_time,
    drs.last_hardened_time,
    DATEDIFF(SECOND, drs.last_hardened_time, GETDATE()) AS seconds_behind,
    CASE
        WHEN ar.availability_mode_desc = 'SYNCHRONOUS_COMMIT'
            AND drs.synchronization_state_desc = 'SYNCHRONIZED'
        THEN 'No data loss expected'
        ELSE 'Potential data loss: ' +
            CAST(drs.log_send_queue_size / 1024.0 AS VARCHAR(20)) + ' MB'
    END AS rpo_assessment
FROM sys.dm_hadr_database_replica_states drs
INNER JOIN sys.availability_replicas ar ON drs.replica_id = ar.replica_id
INNER JOIN sys.availability_databases_cluster adc ON drs.group_database_id = adc.group_database_id
WHERE drs.is_local = 0
ORDER BY drs.log_send_queue_size DESC;
```

### Check AG cluster state

```sql
-- AG cluster state information
SELECT
    ag.name AS ag_name,
    agcs.primary_replica,
    agcs.primary_recovery_health_desc,
    agcs.secondary_recovery_health_desc,
    agcs.synchronization_health_desc
FROM sys.dm_hadr_availability_group_states agcs
INNER JOIN sys.availability_groups ag ON agcs.group_id = ag.group_id;
```

### Check listener status

```sql
-- Listener configuration and IP status
SELECT
    ag.name AS ag_name,
    agl.dns_name AS listener_name,
    agl.port AS listener_port,
    agl.ip_configuration_string_from_cluster,
    lip.ip_address,
    lip.ip_subnet_mask,
    lip.is_dhcp,
    lip.network_subnet_ip,
    lip.network_subnet_prefix_length,
    lip.state_desc AS ip_state
FROM sys.availability_group_listeners agl
INNER JOIN sys.availability_groups ag ON agl.group_id = ag.group_id
INNER JOIN sys.availability_group_listener_ip_addresses lip ON agl.listener_id = lip.listener_id
ORDER BY ag.name, agl.dns_name;
```

### Check endpoint health

```sql
-- Database mirroring endpoint status
SELECT
    e.name AS endpoint_name,
    e.protocol_desc,
    e.type_desc,
    e.state_desc AS endpoint_state,
    te.port,
    te.ip_address,
    e.is_encryption_enabled,
    e.encryption_algorithm_desc,
    e.connection_auth_desc
FROM sys.endpoints e
INNER JOIN sys.tcp_endpoints te ON e.endpoint_id = te.endpoint_id
WHERE e.type_desc = 'DATABASE_MIRRORING';
```

### Check endpoint permissions

```sql
-- Verify endpoint connect permissions
SELECT
    e.name AS endpoint_name,
    sp.name AS principal_name,
    sp.type_desc AS principal_type,
    perm.permission_name,
    perm.state_desc AS permission_state
FROM sys.server_permissions perm
INNER JOIN sys.server_principals sp ON perm.grantee_principal_id = sp.principal_id
INNER JOIN sys.endpoints e ON perm.major_id = e.endpoint_id
WHERE perm.class_desc = 'ENDPOINT'
    AND e.type_desc = 'DATABASE_MIRRORING'
ORDER BY e.name, sp.name;
```

### Check AG-related waits

```sql
-- AG-related wait statistics
SELECT
    wait_type,
    waiting_tasks_count,
    wait_time_ms,
    max_wait_time_ms,
    signal_wait_time_ms
FROM sys.dm_os_wait_stats
WHERE wait_type LIKE 'HADR%'
    OR wait_type LIKE 'PWAIT_HADR%'
    OR wait_type IN ('PARALLEL_REDO_WORKER_WAIT_WORK',
        'PARALLEL_REDO_DRAIN_WORKER', 'PARALLEL_REDO_LOG_CACHE',
        'PARALLEL_REDO_TRAN_LIST', 'PARALLEL_REDO_WORKER_SYNC')
ORDER BY wait_time_ms DESC;
```

### Check transport statistics

```sql
-- AG transport layer statistics
SELECT
    ag.name AS ag_name,
    ar.replica_server_name,
    hts.total_bytes_sent / 1048576.0 AS total_mb_sent,
    hts.total_bytes_received / 1048576.0 AS total_mb_received,
    hts.total_sends,
    hts.total_receives,
    hts.avg_send_latency_ms,
    hts.avg_receive_latency_ms
FROM sys.dm_hadr_transport_statistics hts
INNER JOIN sys.availability_replicas ar ON hts.replica_id = ar.replica_id
INNER JOIN sys.availability_groups ag ON ar.group_id = ag.group_id
ORDER BY ag.name, ar.replica_server_name;
```

### Search error log for AG events

```sql
-- Search SQL Server error log for AG-related messages
CREATE TABLE #ErrorLog (
    LogDate DATETIME,
    ProcessInfo VARCHAR(50),
    Text VARCHAR(MAX)
);

INSERT INTO #ErrorLog
EXEC xp_readerrorlog 0, 1;

SELECT LogDate, ProcessInfo, Text
FROM #ErrorLog
WHERE Text LIKE '%availability%'
   OR Text LIKE '%AlwaysOn%'
   OR Text LIKE '%HADR%'
   OR Text LIKE '%replica%'
   OR Text LIKE '%failover%'
   OR Text LIKE '%lease%'
   OR Text LIKE '%quorum%'
ORDER BY LogDate DESC;

DROP TABLE #ErrorLog;
```

### Check automatic seeding status

```sql
-- Automatic seeding progress (SQL Server 2016+)
SELECT
    ag.name AS ag_name,
    ar.replica_server_name,
    adc.database_name,
    has.current_state,
    has.performed_seeding,
    has.failure_state_desc,
    has.error_code,
    has.number_of_attempts,
    has.start_time_utc,
    has.end_time_utc,
    has.seeding_mode_desc
FROM sys.dm_hadr_automatic_seeding has
INNER JOIN sys.availability_groups ag ON has.ag_id = ag.group_id
INNER JOIN sys.availability_replicas ar ON has.ag_remote_replica_id = ar.replica_id
LEFT JOIN sys.availability_databases_cluster adc ON has.ag_db_id = adc.group_database_id
ORDER BY has.start_time_utc DESC;
```

### Check physical seeding stats

```sql
-- Physical seeding progress
SELECT
    ag.name AS ag_name,
    ar.replica_server_name,
    local_database_name,
    role_desc,
    internal_state_desc,
    transfer_rate_bytes_per_second / 1048576.0 AS transfer_rate_mbps,
    transferred_size_bytes / 1073741824.0 AS transferred_gb,
    database_size_bytes / 1073741824.0 AS database_size_gb,
    CAST(100.0 * transferred_size_bytes / NULLIF(database_size_bytes, 0) AS DECIMAL(5,2)) AS percent_complete,
    estimate_time_complete_utc,
    total_disk_io_wait_time_ms,
    total_network_wait_time_ms,
    failure_code,
    failure_message
FROM sys.dm_hadr_physical_seeding_stats pss
INNER JOIN sys.availability_replicas ar ON pss.remote_machine_name = ar.replica_server_name
INNER JOIN sys.availability_groups ag ON ar.group_id = ag.group_id
ORDER BY ag.name, ar.replica_server_name;
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Appendix B: PowerShell diagnostic commands

### Cluster node management

```powershell
#region Cluster Node Status

# Get detailed cluster node information
Get-ClusterNode | Select-Object Name, State, NodeWeight, DynamicWeight, NodeHighestVersion, NodeLowestVersion

# Check node drain status
Get-ClusterNode | Select-Object Name, State, DrainStatus

# Check if any nodes are quarantined
Get-ClusterNode | Where-Object { $_.State -eq 'Quarantined' } |
    Select-Object Name, State, QuarantineStatus

# Get node uptime
Get-ClusterNode | ForEach-Object {
    $node = $_
    $uptime = (Get-CimInstance -ComputerName $node.Name -ClassName Win32_OperatingSystem).LastBootUpTime
    [PSCustomObject]@{
        Name = $node.Name
        State = $node.State
        LastBoot = $uptime
        Uptime = (Get-Date) - $uptime
    }
}

# Start a cluster node
Start-ClusterNode -Name "NodeName"

# Stop a cluster node (drain roles first)
Suspend-ClusterNode -Name "NodeName" -Drain

# Stop cluster node immediately
Stop-ClusterNode -Name "NodeName"

# Clear node quarantine
Start-ClusterNode -Name "NodeName" -ClearQuarantine

# Evict node from cluster (use with caution)
Remove-ClusterNode -Name "NodeName" -Force

#endregion
```

### Cluster quorum management

```powershell
#region Quorum Management

# Get current quorum configuration
Get-ClusterQuorum | Select-Object Cluster, QuorumResource, QuorumType

# Get detailed quorum status
Get-Cluster | Select-Object Name, QuorumType, WitnessDatabaseWriteTimeout,
    QuarantineThreshold, QuarantineDuration, CrossSiteDelay, CrossSiteThreshold

# Check witness status
$witness = (Get-ClusterQuorum).QuorumResource
if ($witness) {
    Get-ClusterResource -Name $witness.Name |
        Select-Object Name, State, ResourceType, OwnerNode
}

# Configure file share witness
Set-ClusterQuorum -NodeAndFileShareMajority "\\FileServer\Witness"

# Configure cloud witness (Azure)
Set-ClusterQuorum -CloudWitness -AccountName "StorageAccountName" -AccessKey "AccessKey"

# Configure node majority (no witness)
Set-ClusterQuorum -NodeMajority

# Force start cluster with quorum
Start-ClusterNode -Name $env:COMPUTERNAME -FixQuorum

# Check vote configuration
Get-ClusterNode | Select-Object Name, NodeWeight, DynamicWeight

# Adjust node vote (0 = no vote, 1 = has vote)
(Get-ClusterNode -Name "NodeName").NodeWeight = 0

#endregion
```

### AG resource management

```powershell
#region AG Resource Management

# Get all AG resources
Get-ClusterResource | Where-Object { $_.ResourceType -eq "SQL Server Availability Group" } |
    Select-Object Name, State, OwnerNode, OwnerGroup

# Get AG resource parameters
Get-ClusterResource -Name "AG_ResourceName" | Get-ClusterParameter

# Get failure threshold settings
Get-ClusterResource -Name "AG_ResourceName" | Get-ClusterParameter |
    Where-Object { $_.Name -match "Failure|RestartPeriod|RetryPeriod" } |
    Select-Object Name, Value

# Modify failure threshold
Get-ClusterResource -Name "AG_ResourceName" |
    Set-ClusterParameter -Name "FailoverThreshold" -Value 5

# Modify failure period (minutes)
Get-ClusterResource -Name "AG_ResourceName" |
    Set-ClusterParameter -Name "FailurePeriod" -Value 360

# Take AG resource offline
Stop-ClusterResource -Name "AG_ResourceName"

# Bring AG resource online
Start-ClusterResource -Name "AG_ResourceName"

# Move AG to different node
Move-ClusterGroup -Name "AG_GroupName" -Node "TargetNode"

# Get AG dependency report
Get-ClusterResource -Name "AG_ResourceName" | Get-ClusterResourceDependency

#endregion
```

### Listener management

```powershell
#region Listener Management

# Get listener resources
Get-ClusterResource | Where-Object {
    $_.ResourceType -eq "Network Name" -or
    $_.ResourceType -eq "IP Address"
} | Select-Object Name, State, ResourceType, OwnerGroup

# Get listener IP parameters
Get-ClusterResource | Where-Object { $_.ResourceType -eq "IP Address" } |
    Get-ClusterParameter | Select-Object ClusterObject, Name, Value

# Check listener network name
Get-ClusterResource | Where-Object { $_.ResourceType -eq "Network Name" } |
    Get-ClusterParameter -Name DnsName, Name |
    Select-Object ClusterObject, Name, Value

# Get RegisterAllProvidersIP setting
Get-ClusterResource -Name "ListenerName" |
    Get-ClusterParameter -Name RegisterAllProvidersIP

# Change RegisterAllProvidersIP
Get-ClusterResource -Name "ListenerName" |
    Set-ClusterParameter RegisterAllProvidersIP 0

# Change DNS TTL
Get-ClusterResource -Name "ListenerName" |
    Set-ClusterParameter HostRecordTTL 300

# Verify DNS registration
Resolve-DnsName -Name "ListenerDnsName" -Type A

# Test listener connectivity
Test-NetConnection -ComputerName "ListenerDnsName" -Port 1433

#endregion
```

### Network diagnostics

```powershell
#region Network Diagnostics

# Get cluster networks
Get-ClusterNetwork | Select-Object Name, State, Role, Address, AddressMask

# Get cluster network interfaces
Get-ClusterNetworkInterface |
    Select-Object Name, Node, Network, State, Adapter, Address

# Test cluster network connectivity
Test-Cluster -Node "Node1","Node2" -Include "Network"

# Test endpoint connectivity between replicas
$replicas = @("Replica1", "Replica2", "Replica3")
$port = 5022
foreach ($source in $replicas) {
    foreach ($target in $replicas) {
        if ($source -ne $target) {
            $result = Invoke-Command -ComputerName $source -ScriptBlock {
                Test-NetConnection -ComputerName $using:target -Port $using:port
            }
            [PSCustomObject]@{
                Source = $source
                Target = $target
                Port = $port
                TcpTestSucceeded = $result.TcpTestSucceeded
                PingSucceeded = $result.PingSucceeded
            }
        }
    }
}

# Check network latency between nodes
$replicas = @("Replica1", "Replica2")
foreach ($target in $replicas) {
    $ping = Test-Connection -ComputerName $target -Count 10
    [PSCustomObject]@{
        Target = $target
        MinLatency = ($ping | Measure-Object -Property ResponseTime -Minimum).Minimum
        MaxLatency = ($ping | Measure-Object -Property ResponseTime -Maximum).Maximum
        AvgLatency = ($ping | Measure-Object -Property ResponseTime -Average).Average
    }
}

#endregion
```

### Cluster log analysis

```powershell
#region Cluster Log Analysis

# Generate cluster log (last 60 minutes)
Get-ClusterLog -Destination "C:\Temp\ClusterLogs" -TimeSpan 60

# Generate cluster log from all nodes
Get-ClusterLog -Destination "C:\Temp\ClusterLogs" -TimeSpan 60 -UseLocalTime

# Search cluster log for specific patterns
$logPath = "C:\Temp\ClusterLogs\*.log"

# Search for quorum issues
Select-String -Path $logPath -Pattern "quorum|vote|witness" -Context 2,2

# Search for lease timeout
Select-String -Path $logPath -Pattern "lease|timeout" -Context 2,2

# Search for heartbeat/network issues
Select-String -Path $logPath -Pattern "heartbeat|unreachable|Failed to connect" -Context 2,2

# Search for failover events
Select-String -Path $logPath -Pattern "failover|role change|state change" -Context 2,2

# Search for resource failures
Select-String -Path $logPath -Pattern "failed|error|exception" -Context 2,2

#endregion
```

### Windows event log analysis

```powershell
#region Event Log Analysis

# Get recent failover cluster events (errors and warnings)
Get-WinEvent -FilterHashtable @{
    LogName = 'Microsoft-Windows-FailoverClustering/Operational'
    Level = 2,3  # Error, Warning
} -MaxEvents 50 | Select-Object TimeCreated, LevelDisplayName, Id, Message

# Get SQL Server AG events
Get-WinEvent -FilterHashtable @{
    LogName = 'Application'
    ProviderName = 'MSSQLSERVER'
} -MaxEvents 50 | Where-Object {
    $_.Message -match 'availability|AlwaysOn|HADR|replica'
} | Select-Object TimeCreated, Id, Message

# Get specific cluster event IDs
$importantEventIds = @(1135, 1177, 1069, 1205, 1222)  # Node communication, quorum, resource failures
Get-WinEvent -FilterHashtable @{
    LogName = 'Microsoft-Windows-FailoverClustering/Operational'
    Id = $importantEventIds
} -MaxEvents 20 | Select-Object TimeCreated, Id, Message

# Export events to file
Get-WinEvent -FilterHashtable @{
    LogName = 'Microsoft-Windows-FailoverClustering/Operational'
    StartTime = (Get-Date).AddHours(-24)
} | Export-Csv -Path "C:\Temp\ClusterEvents.csv" -NoTypeInformation

#endregion
```

### Cluster validation

```powershell
#region Cluster Validation

# Run full cluster validation
Test-Cluster -Include All -ReportName "C:\Temp\ClusterValidation"

# Run specific validation tests
Test-Cluster -Include "Inventory","Network","System Configuration"

# Run validation on specific nodes
Test-Cluster -Node "Node1","Node2" -Include All

# Run storage validation only
Test-Cluster -Include "Storage"

# Run network validation only
Test-Cluster -Include "Network"

# Check validation report
Start-Process "C:\Temp\ClusterValidation.htm"

#endregion
```

### Service management

```powershell
#region Service Management

# Check cluster service status on all nodes
$nodes = (Get-ClusterNode).Name
foreach ($node in $nodes) {
    Get-Service -ComputerName $node -Name ClusSvc |
        Select-Object MachineName, Name, Status, StartType
}

# Restart cluster service on a node (use with caution)
Invoke-Command -ComputerName "NodeName" -ScriptBlock {
    Restart-Service -Name ClusSvc -Force
}

# Check SQL Server service status
foreach ($node in $nodes) {
    Get-Service -ComputerName $node -Name "MSSQLSERVER","SQLSERVERAGENT" |
        Select-Object MachineName, Name, Status, StartType
}

# Check SQL Server AG health from service perspective
foreach ($node in $nodes) {
    $sqlService = Get-Service -ComputerName $node -Name "MSSQLSERVER"
    [PSCustomObject]@{
        Node = $node
        SQLService = $sqlService.Status
        ClusterService = (Get-Service -ComputerName $node -Name ClusSvc).Status
    }
}

#endregion
```

### Firewall management

```powershell
#region Firewall Management

# Check firewall rules for SQL Server and AG
Get-NetFirewallRule | Where-Object {
    $_.DisplayName -match "SQL|1433|5022|AG|Availability"
} | Select-Object DisplayName, Direction, Action, Enabled

# Create firewall rule for AG endpoint
New-NetFirewallRule -DisplayName "AG Endpoint (TCP 5022)" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 5022 `
    -Action Allow `
    -Profile Domain

# Create firewall rule for SQL Server
New-NetFirewallRule -DisplayName "SQL Server (TCP 1433)" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 1433 `
    -Action Allow `
    -Profile Domain

# Enable rules on all nodes
$nodes = (Get-ClusterNode).Name
foreach ($node in $nodes) {
    Invoke-Command -ComputerName $node -ScriptBlock {
        Enable-NetFirewallRule -DisplayName "AG Endpoint (TCP 5022)"
        Enable-NetFirewallRule -DisplayName "SQL Server (TCP 1433)"
    }
}

#endregion
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Appendix C: Common AG operations

### Manual planned failover (no data loss)

```sql
-- Step 1: Verify synchronization state on current primary
SELECT
    ar.replica_server_name,
    drs.synchronization_state_desc,
    drcs.is_failover_ready
FROM sys.dm_hadr_database_replica_states drs
JOIN sys.availability_replicas ar ON drs.replica_id = ar.replica_id
JOIN sys.dm_hadr_database_replica_cluster_states drcs
    ON drs.replica_id = drcs.replica_id AND drs.group_database_id = drcs.group_database_id;

-- Step 2: Perform planned failover (run on target secondary)
ALTER AVAILABILITY GROUP [AGName] FAILOVER;

-- Step 3: Verify new primary
SELECT replica_server_name, role_desc
FROM sys.dm_hadr_availability_replica_states
WHERE is_local = 1;
```

### Add database to AG

```sql
-- On PRIMARY: Add database to AG
ALTER AVAILABILITY GROUP [AGName] ADD DATABASE [DatabaseName];

-- On SECONDARY (if using manual seeding): Restore and join
RESTORE DATABASE [DatabaseName]
FROM DISK = N'\\BackupShare\DatabaseName_Full.bak'
WITH NORECOVERY;

RESTORE LOG [DatabaseName]
FROM DISK = N'\\BackupShare\DatabaseName_Log.trn'
WITH NORECOVERY;

ALTER DATABASE [DatabaseName] SET HADR AVAILABILITY GROUP = [AGName];
```

### Remove database from AG

```sql
-- On PRIMARY: Remove from AG
ALTER AVAILABILITY GROUP [AGName] REMOVE DATABASE [DatabaseName];

-- On SECONDARY: Bring database online (if needed)
ALTER DATABASE [DatabaseName] SET HADR OFF;
RESTORE DATABASE [DatabaseName] WITH RECOVERY;
```

### Add replica to AG

```sql
-- On PRIMARY: Add replica definition
ALTER AVAILABILITY GROUP [AGName]
ADD REPLICA ON N'NewReplicaServer'
WITH (
    ENDPOINT_URL = N'TCP://NewReplicaServer.domain.com:5022',
    AVAILABILITY_MODE = SYNCHRONOUS_COMMIT,
    FAILOVER_MODE = AUTOMATIC,
    SEEDING_MODE = AUTOMATIC
);

-- On NEW SECONDARY: Join AG
ALTER AVAILABILITY GROUP [AGName] JOIN;

-- If using automatic seeding, grant create database permission
ALTER AVAILABILITY GROUP [AGName] GRANT CREATE ANY DATABASE;
```

### Remove replica from AG

```sql
-- On PRIMARY: Remove replica
ALTER AVAILABILITY GROUP [AGName]
REMOVE REPLICA ON N'ReplicaToRemove';
```

### Change availability mode

```sql
-- Change to synchronous commit
ALTER AVAILABILITY GROUP [AGName]
MODIFY REPLICA ON N'ReplicaServer'
WITH (AVAILABILITY_MODE = SYNCHRONOUS_COMMIT);

-- Change to asynchronous commit
ALTER AVAILABILITY GROUP [AGName]
MODIFY REPLICA ON N'ReplicaServer'
WITH (AVAILABILITY_MODE = ASYNCHRONOUS_COMMIT);
```

### Change failover mode

```sql
-- Enable automatic failover
ALTER AVAILABILITY GROUP [AGName]
MODIFY REPLICA ON N'ReplicaServer'
WITH (FAILOVER_MODE = AUTOMATIC);

-- Change to manual failover
ALTER AVAILABILITY GROUP [AGName]
MODIFY REPLICA ON N'ReplicaServer'
WITH (FAILOVER_MODE = MANUAL);
```

### Suspend and resume data movement

```sql
-- Suspend data movement
ALTER DATABASE [DatabaseName] SET HADR SUSPEND;

-- Resume data movement
ALTER DATABASE [DatabaseName] SET HADR RESUME;

-- Check suspended databases
SELECT
    db.name,
    drs.is_suspended,
    drs.suspend_reason_desc
FROM sys.dm_hadr_database_replica_states drs
JOIN sys.databases db ON drs.database_id = db.database_id
WHERE drs.is_suspended = 1;
```

### Create AG listener

```sql
-- Create listener with single subnet
ALTER AVAILABILITY GROUP [AGName]
ADD LISTENER N'AGListener' (
    WITH IP ((N'10.0.0.100', N'255.255.255.0')),
    PORT = 1433
);

-- Create listener with multiple subnets
ALTER AVAILABILITY GROUP [AGName]
ADD LISTENER N'AGListener' (
    WITH IP (
        (N'10.0.1.100', N'255.255.255.0'),
        (N'10.0.2.100', N'255.255.255.0')
    ),
    PORT = 1433
);
```

### Modify listener

```sql
-- Add IP to existing listener
ALTER AVAILABILITY GROUP [AGName]
MODIFY LISTENER N'AGListener' (
    ADD IP (N'10.0.3.100', N'255.255.255.0')
);

-- Change listener port
ALTER AVAILABILITY GROUP [AGName]
MODIFY LISTENER N'AGListener' (
    PORT = 1434
);
```

### Configure read-only routing

```sql
-- Set read-only routing URL on each replica
ALTER AVAILABILITY GROUP [AGName]
MODIFY REPLICA ON N'Replica1'
WITH (SECONDARY_ROLE (READ_ONLY_ROUTING_URL = N'TCP://Replica1.domain.com:1433'));

ALTER AVAILABILITY GROUP [AGName]
MODIFY REPLICA ON N'Replica2'
WITH (SECONDARY_ROLE (READ_ONLY_ROUTING_URL = N'TCP://Replica2.domain.com:1433'));

-- Set read-only routing list when Replica1 is primary
ALTER AVAILABILITY GROUP [AGName]
MODIFY REPLICA ON N'Replica1'
WITH (PRIMARY_ROLE (READ_ONLY_ROUTING_LIST = (N'Replica2', N'Replica1')));

-- Set read-only routing list when Replica2 is primary
ALTER AVAILABILITY GROUP [AGName]
MODIFY REPLICA ON N'Replica2'
WITH (PRIMARY_ROLE (READ_ONLY_ROUTING_LIST = (N'Replica1', N'Replica2')));
```

### Check and modify health check timeout

```sql
-- Check current settings
SELECT
    name,
    failure_condition_level,
    health_check_timeout
FROM sys.availability_groups;

-- Modify health check timeout (milliseconds)
ALTER AVAILABILITY GROUP [AGName]
SET (HEALTH_CHECK_TIMEOUT = 60000);  -- 60 seconds

-- Modify failure condition level
ALTER AVAILABILITY GROUP [AGName]
SET (FAILURE_CONDITION_LEVEL = 3);
```

[↑ Back to Table of Contents](#table-of-contents)

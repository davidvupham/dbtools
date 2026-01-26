# Issue: Replica in RESOLVING State

**[← Back to AG Troubleshooting Index](../troubleshoot-availability-groups.md)**

## Symptoms
- AG dashboard shows replica in "Resolving" state
- Databases are not accessible on the affected replica
- Error: "The local node is not part of quorum"

## Diagnostic Steps

### 1. Check Cluster Node Status
Run the following PowerShell to verify node health:
```powershell
./../scripts/powershell/check-cluster-node-status.ps1
```

### 2. Check for Lease/Health Timeouts
Review the SQL Error log for lease timeouts or connectivity issues.

## Resolution
1. **Node Down:** Start the cluster service: `Start-ClusterNode -Name <NodeName>`
2. **Quarantined:** clear quarantine: `Start-ClusterNode -Name <NodeName> -ClearQuarantine`
3. **Forced Failover:** If primary is permanently lost and recovery is urgent (allows data loss):
    ```sql
    -- Run from target secondary
    -- WARNING: Data loss possible
    :r ../scripts/sql/force-failover-allow-data-loss.sql
    ```

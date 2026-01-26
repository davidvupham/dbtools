# Issue: Automatic Failover Did Not Occur

**[← Back to AG Troubleshooting Index](../troubleshoot-availability-groups.md)**

## Symptoms
- Primary failed but secondary did not take over
- AG remains in RESOLVING state

## Diagnostic Steps

### 1. Verify Failover Readiness
All databases must be synchronized for automatic failover.
```sql
:r ../scripts/sql/check-failover-readiness.sql
```

### 2. Check Cluster Failure Thresholds
If the AG has failed/restarted too many times (default 3 in 6 hours), the cluster stops automatic failover.
```powershell
./../scripts/powershell/check-ag-resource-status.ps1
```

## Resolution
1. **Fix Synchronization:** Ensure all DBs are `SYNCHRONIZED`.
2. **Reset Thresholds:** Manually bring the AG online in Failover Cluster Manager if thresholds were exceeded.

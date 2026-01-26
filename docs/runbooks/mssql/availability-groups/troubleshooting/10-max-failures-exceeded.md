# Issue: Maximum Failures Threshold Exceeded

**[← Back to AG Troubleshooting Index](../troubleshoot-availability-groups.md)**

## Symptoms
- AG fails to failover
- Cluster log shows "failoverCount > computedFailoverThreshold"

## Diagnostic Steps

### 1. Check Threshold Settings
```powershell
./../scripts/powershell/check-ag-resource-status.ps1
```

## Resolution
1. **Identify Root Cause:** Why did it fail 3 times in 6 hours? (Network? Storage?)
2. **Reset Counter:** Bring the resource online manually in Failover Cluster Manager.
3. **Temporary Increase:** Increase `FailoverThreshold` if instability is temporary and monitored.

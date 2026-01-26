# Issue: Quorum Failure

**[← Back to AG Troubleshooting Index](../troubleshoot-availability-groups.md)**

## Symptoms
- Entire cluster is offline ("Quorum Lost")
- SQL Server services will not start

## Diagnostic Steps

### 1. Check Quorum Health
```powershell
./../scripts/powershell/check-cluster-quorum.ps1
```

## Resolution
1. **Bring Nodes Online:** Try to bring enough nodes online to regain majority.
2. **Force Quorum:** If majority is impossible and you accept split-brain risks:
   ```powershell
   Start-ClusterNode -Name <NodeName> -FixQuorum
   ```

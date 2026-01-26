# Issue: Cluster Service Failures

**[← Back to AG Troubleshooting Index](../troubleshoot-availability-groups.md)**

## Symptoms
- Cluster service won't start
- Event ID 1069

## Resolution
1. **Force Start:** `Start-ClusterNode -ForceQuorum` (Use with EXTREME CAUTION, only on last surviving node).
2. **Log Analysis:**
   ```powershell
   ./../scripts/powershell/generate-cluster-log.ps1
   ```

# Issue: Cluster Node Quarantined

**[← Back to AG Troubleshooting Index](../troubleshoot-availability-groups.md)**

## Symptoms
- Node shows "Quarantined" status
- Node cannot rejoin cluster

## cause
Node failed sporadically (3+ times in 1 hour).

## Resolution
1. **Clear Quarantine:**
   ```powershell
   Start-ClusterNode -Name <NodeName> -ClearQuarantine
   ```
2. **Investigate:** Check cluster logs for the reason behind the flakiness (often NIC drivers or storage paths).

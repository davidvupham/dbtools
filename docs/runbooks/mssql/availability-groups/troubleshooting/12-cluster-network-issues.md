# Issue: Cluster Network Issues

**[← Back to AG Troubleshooting Index](../troubleshoot-availability-groups.md)**

## Symptoms
- "Heartbeat lost" messages
- Event ID 1135 (Node removed from active cluster membership)

## Diagnostic Steps
```powershell
# Validate Cluster Network
Test-Cluster -Node <Node1>,<Node2> -Include "Network"
```

## Resolution
1. **Check Hardware:** Verify physical NICs and cables.
2. **Drivers:** Update network drivers (common cause of packet loss).
3. **Antivirus:** Ensure exclusion for Cluster communication ports (UDP 3343).

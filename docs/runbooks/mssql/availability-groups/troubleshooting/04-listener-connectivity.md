# Issue: Listener Connectivity Issues

**[← Back to AG Troubleshooting Index](../troubleshoot-availability-groups.md)**

## Symptoms
- Applications cannot connect via listener name
- Connection timeouts after failover

## Diagnostic Steps

### 1. Test Connectivity
```powershell
./../scripts/powershell/check-listener-connectivity.ps1 <ListenerName> 1433
```

### 2. Check Firewall Rules
Ensure port 1433 is open on all nodes.
```powershell
./../scripts/powershell/check-firewall-rules.ps1
```

## Resolution
1. **Multi-Subnet:** Ensure connection strings use `MultiSubnetFailover=True`.
2. **DNS:** Flush DNS if old IP is cached (`ipconfig /flushdns`).

# Issue: High Redo/Log Send Queue

**[← Back to AG Troubleshooting Index](../troubleshoot-availability-groups.md)**

## Symptoms
- High latency (RPO/RTO risk)
- "Synchronizing" state persists longer than expected

## Diagnostic Steps

### 1. Monitor Queue Sizes
```sql
:r ../scripts/sql/check-queues.sql
```

### 2. Check Data Loss Risk
```sql
:r ../scripts/sql/check-data-loss-risk.sql
```

## Resolution
1. **Flow Control:** Check if network bandwidth is the bottleneck `check-flow-control.sql`.
2. **Blocking:** Check if reporting queries on secondary are blocking redo `check-redo-blocking.sql`.

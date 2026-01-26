# Issue: Database Not Synchronizing

**[← Back to AG Troubleshooting Index](../troubleshoot-availability-groups.md)**

## Symptoms
- Database shows "Not Synchronizing" or "Recovery Pending"
- Data movement is suspended

## Diagnostic Steps

### 1. Check Suspension Status
```sql
:r ../scripts/sql/check-database-sync.sql
```

### 2. Check Disk Space
Ensure transaction log drives are not full on the secondary replica.

## Resolution
1. **Resume Movement:**
   ```sql
   ALTER DATABASE [DatabaseName] SET HADR RESUME;
   ```
2. **Re-initialize:** If stuck, remove from AG, restore logs, and re-join.

# Issue: Database in Reverting State

**[← Back to AG Troubleshooting Index](../troubleshoot-availability-groups.md)**

## Symptoms
- Database shows "Reverting" state on secondary
- Undo operations in progress

## Resolution
1. **Wait:** Allow the undo process to complete.
2. **Do NOT restart:** Restarting SQL Server will only restart the recovery process.
3. **Remove and Reseed:** If reverting is stuck:
   - Remove database from AG on secondary.
   - Restore from backup with `NORECOVERY`.
   - Re-join AG.

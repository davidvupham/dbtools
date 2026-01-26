# Issue: Split-Brain Scenario

**[← Back to AG Troubleshooting Index](../troubleshoot-availability-groups.md)**

## Symptoms
- Multiple sites/nodes believe they are Primary
- Data divergence risk

## Resolution
1. **Isolate Secondary:** Shut down cluster service on the secondary/isolated site.
2. **Re-establish Primary:** Ensure proper quorum on the main site.
3. **Reconcile Data:** You may need to drop the secondary databases and re-seed from the surviving primary.

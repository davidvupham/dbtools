# Dev Container Troubleshooting - Quick Start

## Current Status

✅ **Ready for Test 1** - Minimal container configuration

## What We've Done

1. Created timestamped backups of original files (20251114_065651)
2. Replaced with minimal configuration:
   - Dockerfile: Just base miniconda image
   - devcontainer.json: Minimal config, no features
   - postCreate.sh: Removed (not used yet)
3. Created helper scripts for testing

## Next Steps - START HERE

### 1. Test the Minimal Container

**In VS Code:**
- Press `F1` (or `Ctrl+Shift+P`)
- Type: `Dev Containers: Rebuild Container`
- Wait and observe:
  - Does it build successfully?
  - Does VS Code attach?
  - Does control return to you?

**Record the results in:** `DEVCONTAINER_TROUBLESHOOTING.md`

### 2. If Test 1 Succeeds ✅

Great! The base container works. Now follow `TEST_PLAN.md` to incrementally add components:
- Test 2: User management
- Test 3: System packages
- Test 4: ODBC drivers
- Test 5: PowerShell
- Test 6: Conda environment
- Test 7: Docker feature (CRITICAL)
- Test 8: Network & mounts
- Test 9: VS Code extensions
- Test 10: postCreate.sh

**Before each test:**
```bash
cd .devcontainer
./backup_current.sh test2  # Change number for each test
```

### 3. If Test 1 Fails ❌

The issue is with the base configuration. Check:
```bash
# Check container status
./check_container.sh

# View container logs
docker logs <container_id>

# Try to attach manually
./attach_container.sh
```

## Helper Scripts

All in `.devcontainer/` directory:

- `backup_current.sh <name>` - Backup before making changes
- `restore_version.sh <timestamp>` - Restore a previous version
- `check_container.sh` - Check container status and logs
- `attach_container.sh` - Manually attach to running container
- `test_log.sh` - Monitor container in real-time (advanced)

## Important Files

- `DEVCONTAINER_TROUBLESHOOTING.md` - Detailed troubleshooting log
- `TEST_PLAN.md` - Step-by-step component addition guide
- `archive/` - All backups stored here

## Restore Original Configuration

If you need to go back to the full original configuration:

```bash
cd .devcontainer
./restore_version.sh 20251114_065651
```

Then rebuild in VS Code.

## Tips

1. **Test incrementally** - Add one component at a time
2. **Always backup** - Before each change
3. **Document results** - Update DEVCONTAINER_TROUBLESHOOTING.md
4. **Check logs** - Use helper scripts to investigate issues
5. **Be patient** - Some builds take several minutes

## Expected Timeline

- Test 1 (minimal): ~1-2 minutes
- Test 2-6 (Dockerfile components): ~2-5 minutes each
- Test 7 (Docker feature): ~3-7 minutes (largest)
- Test 8-9: ~2-4 minutes each
- Test 10 (postCreate): ~1-2 minutes

## Common Issues & Solutions

### Container builds but VS Code doesn't attach
- Check: Docker logs for errors
- Try: Restart VS Code
- Check: Docker Desktop is running

### Build hangs at specific step
- Note: Which step (record in log)
- Try: Ctrl+C and rebuild
- Check: Network connectivity
- Try: Remove that component and continue

### Permission errors
- Check: User UID/GID matches
- Check: Volume mount permissions
- Try: Run as root temporarily to debug

## Questions?

Review the detailed guides:
- `DEVCONTAINER_TROUBLESHOOTING.md` - Comprehensive troubleshooting
- `TEST_PLAN.md` - Detailed test procedures

---

**Current Test**: Test 1 - Minimal Container
**Status**: 🔄 Ready to rebuild in VS Code
**Last Updated**: 2025-11-14 07:01

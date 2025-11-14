# Dev Container Troubleshooting Tools

This directory contains tools and documentation for troubleshooting dev container issues.

## Quick Start

**START HERE:** Read `README_TROUBLESHOOTING.md` for immediate next steps.

## Files

### Documentation
- **README_TROUBLESHOOTING.md** - Quick start guide (read this first!)
- **TEST_PLAN.md** - Step-by-step incremental testing guide
- **DEVCONTAINER_TROUBLESHOOTING.md** - Detailed troubleshooting log and notes

### Helper Scripts
- **backup_current.sh** - Create backup before making changes
- **restore_version.sh** - Restore a previous version
- **check_container.sh** - Check container status and logs
- **attach_container.sh** - Manually attach to running container
- **test_log.sh** - Monitor container in real-time

## Usage

### Before Each Test
```bash
cd .devcontainer/troubleshooting
./backup_current.sh test2  # Change number for each test
```

### To Restore Original Configuration
```bash
cd .devcontainer/troubleshooting
./restore_version.sh 20251114_065651
```

### To Check Container Status
```bash
cd .devcontainer/troubleshooting
./check_container.sh
```

### To Attach to Running Container
```bash
cd .devcontainer/troubleshooting
./attach_container.sh
```

## Current Status

- ✅ Backups created (timestamp: 20251114_065651)
- ✅ Minimal configuration ready
- 🔄 Ready for Test 1: Minimal Container

## Next Action

Rebuild the dev container in VS Code and record results in `DEVCONTAINER_TROUBLESHOOTING.md`.

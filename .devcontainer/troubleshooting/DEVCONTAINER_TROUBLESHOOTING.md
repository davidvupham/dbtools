# Dev Container Troubleshooting Log

**Issue**: Dev container builds successfully but control does not return to VS Code

**Date Started**: November 14, 2025
**Approach**: Incremental build-up from minimal configuration

---

## Backup Files Created

**Timestamp**: 20251114_065651

- `archive/Dockerfile.20251114_065651`
- `archive/devcontainer.json.20251114_065651`
- `archive/postCreate.sh.20251114_065651`

---

## Testing Strategy

### Phase 1: Minimal Container (No Features)

- Basic miniconda image
- Minimal Dockerfile
- Minimal devcontainer.json (no features, no extensions, no mounts)
- **Goal**: Verify container builds and VS Code attaches successfully

### Phase 2: Add Dockerfile Components Incrementally

- System packages (curl, wget, etc.)
- ODBC drivers
- PowerShell
- User creation and configuration
- Conda environment setup
- Each addition gets tested and backed up

### Phase 3: Add devcontainer.json Features

- Common-utils feature
- Docker-outside-of-docker feature
- Git feature
- Network configuration
- Volume mounts
- Each addition gets tested and backed up

### Phase 4: Add VS Code Customizations

- Extensions (in batches)
- Settings
- Port forwarding
- Each batch gets tested and backed up

### Phase 5: Add postCreate.sh (Final Phase)

- Only after container builds and returns control
- Add with verbose logging to file
- Monitor for hanging operations

---

## Test Results

### Test 1: Minimal Container

**Date**: 2025-11-14
**Files**:

- Dockerfile: Minimal (base image only)
- devcontainer.json: Minimal (no features, no postCreate)
- postCreate.sh: Not used

**Configuration**:

```json
{
  "name": "dbtools-minimal-test",
  "build": {
    "dockerfile": "Dockerfile",
    "context": ".."
  },
  "remoteUser": "vscode"
}
```

**Dockerfile**:

```dockerfile
FROM mcr.microsoft.com/devcontainers/miniconda:latest
CMD ["sleep", "infinity"]
```

**Result**: ❌ FAILED - Container builds but VS Code does not attach

- **Build time**: 5.2 seconds (fast, successful)
- **VS Code attachment**: NO - Control never returned
- **Container status**: Running (confirmed with docker ps)
- **Container ID**: 5148bdad8a89

**Issues Found**:

1. ⚠️ **CRITICAL**: Container has features installed that are NOT in devcontainer.json:
   - `ghcr.io/devcontainers/features/common-utils:2`
   - `ghcr.io/devcontainers/features/git:1`
   - `ghcr.io/devcontainers/features/node:1`
   - `ghcr.io/devcontainers/features/python:1`

2. **Root Cause**: VS Code is not using our minimal `.devcontainer/devcontainer.json`
   - Multiple devcontainer.json files found:
     - `/home/dpham/src/dbtools/.devcontainer/devcontainer.json` (our minimal one)
     - `/home/dpham/src/dbtools/.devcontainer/redhat/devcontainer.json`
     - `/home/dpham/src/dbtools/.devcontainer/ubuntu/devcontainer.json`
   - VS Code may be using cached configuration or wrong file

3. **Container metadata shows**: Features from a different/older configuration

**Diagnostics**:

- See `test1.devcontainer.build.terminal.output.txt` for full build output
- See `test1_diagnostics.txt` for detailed analysis

**Next Steps**:

1. ✅ Remove container (done - stopped and removed 5148bdad8a89)
2. Clear VS Code dev container cache
3. Remove all cached images
4. Try explicit rebuild with --no-cache
5. Verify VS Code is reading the correct devcontainer.json

---

## Debugging Tools Used

### Check Container Logs

```bash
docker logs <container_name>
```

### Attach to Running Container

```bash
docker exec -it <container_name> bash
```

### Check Running Processes

```bash
docker exec <container_name> ps aux
```

### Monitor Build Output

- VS Code Dev Containers output panel
- Terminal during rebuild

---

## Notes

- Original configuration had extensive setup: ODBC drivers, PowerShell, conda env, multiple features
- postCreate.sh never executed, suggesting issue occurs before that phase
- Possible culprits:
  - Dockerfile hanging on a RUN command
  - Feature installation hanging
  - Volume mount permissions
  - Network creation timing
  - VS Code server installation

---

## Component Inventory (Original Configuration)

### Dockerfile Components

1. Base: mcr.microsoft.com/devcontainers/miniconda:latest
2. System packages: wget, gnupg, ca-certificates, unixodbc-dev, curl, iputils-ping, docker.io, netcat-openbsd
3. Microsoft packages: powershell, msodbcsql18, mssql-tools18
4. Conda environment: Python 3.13, named 'gds'
5. PowerShell modules: dbatools, Pester, PSFramework
6. User management: Create gds user with UID/GID 1000
7. Profile configuration: Bash and PowerShell profiles
8. Python packages: pip, ruff, pytest, pytest-cov, wheel, build, pyodbc, aiohttp
9. VS Code server directories pre-creation

### devcontainer.json Features

1. common-utils (Zsh disabled)
2. git
3. docker-outside-of-docker

### devcontainer.json Lifecycle

1. initializeCommand: Create tool-library-network
2. postCreateCommand: Run postCreate.sh
3. postStartCommand: Fix VS Code server permissions

### Mounts

1. SSH keys (readonly)
2. /data (cached)
3. /logs (cached)
4. Docker socket

### Extensions

- 20+ extensions configured

---

## Progress Tracking

- [x] Create versioned backups
- [x] Create troubleshooting log
- [ ] Test minimal container
- [ ] Incrementally add Dockerfile components
- [ ] Incrementally add devcontainer features
- [ ] Incrementally add VS Code customizations
- [ ] Add postCreate.sh with logging

---

## Timeline

| Time | Action | Result |
|------|--------|--------|
| 06:56 | Created backups (20251114_065651) | ✅ Success |
| 06:57 | Created troubleshooting log | ✅ Success |
| 06:59 | Created minimal Dockerfile | ✅ Success |
| 06:59 | Created minimal devcontainer.json | ✅ Success |
| 06:59 | Removed postCreate.sh | ✅ Success |
| 07:00 | Ready for Test 1: Minimal Container | 🔄 Ready to rebuild |

---

## Current Configuration (Test 1)

### Dockerfile

```dockerfile
# Minimal Dockerfile for troubleshooting
# Test 1: Bare minimum - just base image

FROM mcr.microsoft.com/devcontainers/miniconda:latest

# Keep container running - VS Code will attach to this
CMD ["sleep", "infinity"]
```

### devcontainer.json

```json
{
  "name": "dbtools-minimal-test-1",
  "build": {
    "dockerfile": "Dockerfile",
    "context": ".."
  },
  "remoteUser": "vscode"
}
```

### postCreate.sh

Not present (removed for testing)

---

## Next Steps

1. **Rebuild the dev container** in VS Code
   - Command Palette (F1) → "Dev Containers: Rebuild Container"
   - Watch for:
     - Build output in terminal
     - Time to complete
     - Whether VS Code attaches successfully
     - Whether control returns to VS Code

2. **If successful**, add components incrementally:
   - First: Add system packages (apt-get installs)
   - Second: Add ODBC/PowerShell
   - Third: Add conda environment
   - Fourth: Add user management
   - Fifth: Add devcontainer features
   - Last: Add postCreate.sh

3. **If it fails**, check:
   - Docker logs: `docker logs <container_name>`
   - VS Code output panel
   - Document exactly where it hangs

---

## Helper Scripts

Create these scripts to help with testing:

### check_container.sh

```bash
#!/bin/bash
# Check if container is running and accessible
container_name="dbtools-minimal-test-1"
echo "Checking for container..."
docker ps -a | grep "$container_name" || echo "No container found"
echo ""
echo "Latest container logs:"
docker logs --tail 50 "$container_name" 2>&1 || echo "Cannot get logs"
```

### attach_container.sh

```bash
#!/bin/bash
# Attach to running container for debugging
container_id=$(docker ps -q --filter "ancestor=vsc-dbtools-*")
if [ -n "$container_id" ]; then
  echo "Attaching to container $container_id..."
  docker exec -it "$container_id" bash
else
  echo "No running dev container found"
fi
```

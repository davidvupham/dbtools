# Incremental Component Test Plan

This document guides you through systematically adding components to identify what causes the dev container to hang.

---

## ✅ Test 1: Minimal Container (CURRENT)

**Status**: Ready to test
**Timestamp**: Initial setup

### Configuration

- **Dockerfile**: Base miniconda image only
- **devcontainer.json**: Minimal (no features, no postCreate)
- **postCreate.sh**: Not present

### Expected Behavior

- Container builds quickly (~1-2 minutes)
- VS Code attaches successfully
- Terminal opens with bash prompt
- User is `vscode`

### Test Steps

1. In VS Code: F1 → "Dev Containers: Rebuild Container"
2. Watch build output
3. Wait for VS Code to attach
4. Open terminal and verify:

   ```bash
   whoami  # Should be: vscode
   pwd     # Should be: /workspaces/dbtools
   python --version  # Should work (from miniconda)
   ```

### Record Results

- Build time: ________
- VS Code attached: YES / NO
- Terminal accessible: YES / NO
- Issues: ________

---

## Test 2: Add User Management

**When to run**: After Test 1 succeeds

### Changes to Make

**Save current version first**:

```bash
cd .devcontainer
./backup_current.sh test2
```

**Add to Dockerfile** (after `FROM` line, before `CMD`):

```dockerfile
ARG DEVCONTAINER_USER=gds
ARG DEVCONTAINER_UID=1000
ARG DEVCONTAINER_GID=1000

ENV DEVCONTAINER_USER=${DEVCONTAINER_USER}
ENV DEVCONTAINER_HOME=/home/${DEVCONTAINER_USER}

RUN bash <<'BASH'
set -euo pipefail
if getent passwd vscode >/dev/null 2>&1; then
    usermod -l "${DEVCONTAINER_USER}" -d "${DEVCONTAINER_HOME}" -m vscode
elif ! getent passwd "${DEVCONTAINER_USER}" >/dev/null 2>&1; then
    useradd -m -u "${DEVCONTAINER_UID}" "${DEVCONTAINER_USER}"
fi
chown -R "${DEVCONTAINER_USER}:${DEVCONTAINER_USER}" "${DEVCONTAINER_HOME}"
BASH

USER ${DEVCONTAINER_USER}
```

**Update devcontainer.json**:

```json
{
  "name": "dbtools-test-2-user",
  "build": {
    "dockerfile": "Dockerfile",
    "context": "..",
    "args": {
      "DEVCONTAINER_USER": "${localEnv:USER}"
    }
  },
  "remoteUser": "${localEnv:USER}"
}
```

### Test & Record

- Build time: ________
- Attached: YES / NO
- User correct: YES / NO (`whoami`)
- Issues: ________

---

## Test 3: Add System Packages

**When to run**: After Test 2 succeeds

### Changes to Make

**Save current version**:

```bash
./backup_current.sh test3
```

**Add to Dockerfile** (after ENV, before user management):

```dockerfile
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y curl wget ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
```

**Update name in devcontainer.json**:

```json
"name": "dbtools-test-3-apt"
```

### Test & Record

- Build time: ________
- Attached: YES / NO
- curl works: YES / NO (`curl --version`)
- Issues: ________

---

## Test 4: Add ODBC Drivers

**When to run**: After Test 3 succeeds

### Changes to Make

**Save current version**:

```bash
./backup_current.sh test4
```

**Replace apt-get section in Dockerfile**:

```dockerfile
RUN apt-get update && \
    apt-get install -y curl wget gnupg ca-certificates unixodbc-dev && \
    wget -q https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y msodbcsql18 mssql-tools18 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH=/opt/mssql-tools18/bin:$PATH
```

### Test & Record

- Build time: ________
- Attached: YES / NO
- sqlcmd works: YES / NO (`sqlcmd -?`)
- Issues: ________

---

## Test 5: Add PowerShell

**When to run**: After Test 4 succeeds

### Changes to Make

**Save current version**:

```bash
./backup_current.sh test5
```

**Add to apt-get install line**:

```dockerfile
apt-get install -y ... powershell && \
```

**Add after system packages**:

```dockerfile
RUN pwsh -NoLogo -NoProfile -Command "\
    Set-PSRepository -Name PSGallery -InstallationPolicy Trusted; \
    Install-Module -Name dbatools -Scope AllUsers -Force"
```

### Test & Record

- Build time: ________
- Attached: YES / NO
- pwsh works: YES / NO (`pwsh -version`)
- Module loaded: YES / NO (`pwsh -c "Get-Module -ListAvailable dbatools"`)
- Issues: ________

---

## Test 6: Add Conda Environment

**When to run**: After Test 5 succeeds

### Changes to Make

**Save current version**:

```bash
./backup_current.sh test6
```

**Add to Dockerfile**:

```dockerfile
ARG PYTHON_VERSION=3.13
ARG CONDA_ENV_NAME=gds

RUN conda create -n ${CONDA_ENV_NAME} python=${PYTHON_VERSION} -y && \
    conda clean -afy

ENV PATH=/opt/conda/envs/${CONDA_ENV_NAME}/bin:$PATH
```

### Test & Record

- Build time: ________
- Attached: YES / NO
- Python version: ________ (`python --version`)
- Conda env: ________ (`conda env list`)
- Issues: ________

---

## Test 7: Add Docker Feature (CRITICAL TEST)

**When to run**: After Test 6 succeeds
**Note**: This is a common source of issues

### Changes to Make

**Save current version**:

```bash
./backup_current.sh test7
```

**Update devcontainer.json**:

```json
{
  "name": "dbtools-test-7-docker",
  "build": { ... },
  "remoteUser": "...",
  "features": {
    "ghcr.io/devcontainers/features/docker-outside-of-docker:1": {
      "version": "latest"
    }
  }
}
```

### Test & Record

- Build time: ________
- Attached: YES / NO
- docker works: YES / NO (`docker --version`)
- docker daemon: YES / NO (`docker ps`)
- Issues: ________

---

## Test 8: Add Network & Mounts

**When to run**: After Test 7 succeeds

### Changes to Make

**Save current version**:

```bash
./backup_current.sh test8
```

**Update devcontainer.json**:

```json
{
  ...
  "initializeCommand": "docker network inspect tool-library-network >/dev/null 2>&1 || docker network create tool-library-network",
  "runArgs": [
    "--network", "tool-library-network",
    "--mount", "type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock"
  ]
}
```

### Test & Record

- Build time: ________
- Attached: YES / NO
- Network exists: YES / NO (`docker network ls | grep tool-library`)
- Socket accessible: YES / NO (`ls -l /var/run/docker.sock`)
- Issues: ________

---

## Test 9: Add VS Code Extensions (Batch)

**When to run**: After Test 8 succeeds

### Changes to Make

**Save current version**:

```bash
./backup_current.sh test9
```

**Add to devcontainer.json**:

```json
{
  ...
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "charliermarsh.ruff"
      ]
    }
  }
}
```

### Test & Record

- Build time: ________
- Attached: YES / NO
- Extensions loaded: YES / NO (check Extensions view)
- Issues: ________

---

## Test 10: Add postCreate.sh (FINAL TEST)

**When to run**: After Test 9 succeeds
**Note**: This was never executed before, so likely not the issue

### Changes to Make

**Save current version**:

```bash
./backup_current.sh test10
```

**Create postCreate.sh with logging**:

```bash
#!/usr/bin/env bash
set -euo pipefail

LOG_FILE="/tmp/postCreate.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "[$(date)] postCreate.sh started"
echo "[$(date)] Current directory: $(pwd)"
echo "[$(date)] Current user: $(whoami)"
echo "[$(date)] Python version: $(python --version)"

echo "[$(date)] postCreate.sh completed successfully"
```

**Update devcontainer.json**:

```json
{
  ...
  "postCreateCommand": "bash .devcontainer/postCreate.sh"
}
```

### Test & Record

- Build time: ________
- Attached: YES / NO
- postCreate ran: YES / NO (`cat /tmp/postCreate.log`)
- Issues: ________

---

## Helper Scripts

### backup_current.sh

Create this to quickly backup before each test:

```bash
#!/bin/bash
test_name=${1:-"test_$(date +%s)"}
timestamp=$(date +%Y%m%d_%H%M%S)
mkdir -p archive
cp -p Dockerfile "archive/Dockerfile.${test_name}_${timestamp}"
cp -p devcontainer.json "archive/devcontainer.json.${test_name}_${timestamp}"
[ -f postCreate.sh ] && cp -p postCreate.sh "archive/postCreate.sh.${test_name}_${timestamp}"
echo "✅ Backed up as: ${test_name}_${timestamp}"
```

---

## Recording Template

Copy this for each test:

```
### Test N: [Name]
Date/Time:
Build time:
VS Code attached:
Terminal accessible:
Tests passed:
Issues encountered:
Notes:
```

---

## What to Watch For

### Signs of Success ✅

- Container appears in Docker Desktop
- Build completes in reasonable time
- VS Code shows "Dev Container" badge
- Terminal opens automatically
- Commands execute normally

### Signs of Trouble ⚠️

- Build hangs at specific step
- Container starts but VS Code doesn't attach
- Container exits immediately
- Timeout errors
- Permission denied errors

### Common Culprits

1. **Docker-outside-of-docker feature** - Often causes hangs
2. **Network creation timing** - initializeCommand may fail
3. **Volume mounts** - Permission issues
4. **Large features** - Timeout during installation
5. **User UID/GID mismatch** - File ownership issues

---

## Emergency Recovery

If you get stuck:

```bash
# Stop and remove all containers
docker stop $(docker ps -aq) && docker rm $(docker ps -aq)

# Restore original version
./restore_version.sh 20251114_065651

# Start from Test 1 again
```

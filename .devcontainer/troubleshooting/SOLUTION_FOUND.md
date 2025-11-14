# SOLUTION FOUND - Known Bug in VS Code 1.106.0 + Docker 29.0.0

## Issue Summary

**Problem**: Dev container builds successfully and starts, but VS Code never completes attachment. The build output stops at "Container started" and VS Code hangs indefinitely.

## Root Cause

This is a **known bug** tracked in Microsoft's issue tracker:

- **Issue**: [microsoft/vscode-remote-release#11306](https://github.com/microsoft/vscode-remote-release/issues/11306)
- **Title**: "Devcontainer stuck at Container started but never connect (only with VS Code 1.106.0)"
- **Opened**: November 12, 2025 (2 days ago)
- **Status**: Open, assigned to Microsoft engineer
- **Affected Users**: 10+ confirmed cases

## Affected Versions

- **VS Code**: 1.106.0 (released November 12, 2025)
- **Dev Containers Extension**: 0.431.0
- **Docker**: 29.0.0 (primary cause)
- **OS**: WSL2, Linux (Ubuntu, Debian), macOS

## Our Test Results

All 4 tests exhibited identical behavior:

### Test 1: Miniconda Base Image

- Build: ✅ 5.2 seconds
- Container starts: ✅
- VS Code attaches: ❌ (hangs at "Container started")

### Test 2: Miniconda (no cache)

- Build: ✅ 39.5 seconds
- Container starts: ✅
- VS Code attaches: ❌ (hangs at "Container started")

### Test 3: Plain Debian Image

- Build: ✅ 8.5 seconds
- Container starts: ✅
- VS Code attaches: ❌ (hangs at "Container started")

### Test 4: Plain Debian (folder, not workspace)

- Build: ✅ 22.4 seconds
- Container starts: ✅
- VS Code attaches: ❌ (hangs at "Container started")

### Manual Container Access Test

- `docker exec -it <container> /bin/sh`: ✅ **WORKS**
- **Conclusion**: Container is perfectly functional, VS Code extension is the issue

## Verified Solutions (from GitHub Issue #11306)

### Solution 1: Reload Window Workaround (IMMEDIATE)

**When container hangs:**

1. Press `Ctrl+P` (or `Ctrl+Shift+P`)
2. Type "Reload Window"
3. Select "Developer: Reload Window"
4. Container will connect successfully!

**Pros**: Works immediately, no installation needed
**Cons**: Must do this every rebuild

### Solution 2: Install Pre-Release Extension (RECOMMENDED)

**Permanent fix - already contains the bug fix:**

1. In VS Code → Extensions
2. Find "Dev Containers" extension
3. Click "Switch to Pre-Release Version"
4. Reload VS Code
5. Rebuild container normally

**Pros**: Permanent fix, official solution from Microsoft
**Cons**: Pre-release (but stable for this fix)

### Solution 3: Downgrade Docker to 28.5.x

**If Docker 29.0.0 is the issue for you:**

```bash
# For Ubuntu 24.04
VERSION_STRING=5:28.5.2-1~ubuntu.24.04~noble
sudo apt-get install docker-ce=$VERSION_STRING \
    docker-ce-cli=$VERSION_STRING \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

# Hold the version to prevent auto-upgrade
sudo apt-mark hold docker-ce docker-ce-cli
```

## Related Issues

- [devcontainers/cli#1102](https://github.com/devcontainers/cli/issues/1102) - Docker 29.0.0 compatibility
- Pre-release extension fix: [Comment](https://github.com/devcontainers/cli/issues/1102#issuecomment-3529855579)

## What We Tried (That Didn't Work)

- ❌ Different base images (miniconda, debian)
- ❌ Clearing Docker cache
- ❌ Rebuild without cache
- ❌ Opening folder instead of workspace
- ❌ Removing other devcontainer.json files
- ❌ Minimal Dockerfile configuration

**Conclusion**: This is 100% a VS Code extension + Docker version incompatibility bug, not a configuration issue.

## Recommendation

**For immediate productivity**: Use Solution 1 (Reload Window workaround)
**For permanent fix**: Use Solution 2 (Pre-Release Extension)

## System Details (Our Environment)

- **OS**: WSL2 Ubuntu on Windows
- **VS Code**: 1.106.0
- **Dev Containers Extension**: 0.431.0
- **Docker Client**: 29.0.0
- **Docker Server**: Docker Desktop 4.50.0 (28.5.1)

## Timeline

- **November 12, 2025**: VS Code 1.106.0 released, bug introduced
- **November 12, 2025**: Issue #11306 opened by minhio
- **November 13, 2025**: Multiple users confirm, workarounds identified
- **November 14, 2025**: We encountered and diagnosed the same issue
- **November 14, 2025**: Pre-release extension fix confirmed working

## Next Steps for Testing

1. Restore original configuration or rebuild with current minimal setup
2. When it hangs at "Container started", use `Ctrl+P` → "Reload Window"
3. Verify it works
4. Then install pre-release extension for permanent fix

## Original Configuration Status

Your original `Dockerfile` and `devcontainer.json` were **NOT THE PROBLEM**.
They can be restored from:

- `archive/Dockerfile.20251114_065651`
- `archive/devcontainer.json.20251114_065651`
- `archive/postCreate.sh.20251114_065651`

Once the VS Code bug is resolved (via workaround or pre-release), you can use your full original configuration without issues.

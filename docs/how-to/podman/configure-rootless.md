# Configure Rootless Podman

**🔗 [← Back to Podman Documentation Index](../../explanation/podman/README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 13, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Security](https://img.shields.io/badge/Security-Rootless-blue)

> [!IMPORTANT]
> **Related Docs:** [Installation](./install-podman-rhel.md) | [Troubleshooting](./troubleshooting.md)

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [User Configuration](#user-configuration)
- [Networking](#networking)
- [Caveats and Limitations](#caveats-and-limitations)
- [Troubleshooting](#troubleshooting)

## Overview

Rootless Podman allows unprivileged users to run containers directly without requiring root privileges or a setuid binary. This significantly improves security by ensuring that even if a container is compromised, the attacker does not gain root access to the host.

## Prerequisites

On RHEL 8/9, rootless Podman works out of the box for users created after the `container-tools` module is installed, provided `shadow-utils` are up to date.

**Required Components:**
* `slirp4netns`: User-mode networking
* `fuse-overlayfs`: User-mode filesystem implementation

**Install Dependencies:**

```bash
sudo dnf install -y slirp4netns fuse-overlayfs
```

[↑ Back to Table of Contents](#table-of-contents)

## User Configuration

### 1. Verify Subordinate UIDs/GIDs

Rootless Podman relies on `/etc/subuid` and `/etc/subgid` to map a range of UIDs/GIDs to the unprivileged user.

**Check for existing range:**

```bash
grep $USER /etc/subuid
grep $USER /etc/subgid
```

**Expected Output:**
```text
username:100000:65536
```
*(This allows `username` to use 65,536 UIDs starting from ID 100,000)*

**If no output:**
Add entries for the user manually:

```bash
sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 $USER
```
> **Note:** You must log out and log back in for these changes to take effect.

### 2. Enable User Linger

Recommended for long-running containers (web servers, databases) to ensure they persist after logout.

```bash
loginctl enable-linger $USER
```

[↑ Back to Table of Contents](#table-of-contents)

## Networking

### Network Backends

| Backend | Description | Status |
|:---|:---|:---|
| **Netavark** | Modern, high-performance stack supporting IPv6 and complex setups. | Default in RHEL 9 (Podman 4.0+) |
| **Slirp4netns** | Legacy user-mode networking. Stable but slower. | Default in RHEL 8 |

**Check current backend:**
```bash
podman info --format '{{.Host.NetworkBackend}}'
```

### Exposing Ports

Rootless users cannot bind to privileged ports (< 1024) by default.

**Problem:**
```bash
podman run -p 80:80 nginx
# Error: bind: permission denied
```

**Solution 1: Use Unprivileged Ports (Recommended)**
Map to a high port (e.g., 8080) instead.
```bash
podman run -p 8080:80 nginx
```

**Solution 2: Allow Low Ports System-wide**
Configure sysctl to lower the privileged port threshold.
```bash
echo "net.ipv4.ip_unprivileged_port_start=80" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

[↑ Back to Table of Contents](#table-of-contents)

## Caveats and Limitations

1. **Ping**: ICMP ping might not work inside containers unless configured in `sysctl` (`net.ipv4.ping_group_range`).
2. **Resource Limits**: Rootless containers are strictly bound by the user's systemd cgroup limits.
3. **Storage Performance**: `fuse-overlayfs` is slightly slower than kernel native overlayfs (though difference is negligible for most apps).

[↑ Back to Table of Contents](#table-of-contents)

## Troubleshooting

### "There might not be enough IDs available in the namespace"

**Fix:**
1. Verify `/etc/subuid` entries exist.
2. Run migration tool to reset configuration:
   ```bash
   podman system migrate
   ```

### "Permission denied" on volume mounts

**Fix:**
Private files on the host (like in `$HOME`) may be inaccessible to the container process. Use the `:Z` flag (SELinux) to relabel them correctly.

```bash
podman run -v ./data:/data:Z ...
```

See [Troubleshooting Guide](./troubleshooting.md) for more details.

[↑ Back to Table of Contents](#table-of-contents)

# Podman Troubleshooting

**🔗 [← Back to Podman Documentation Index](../../explanation/podman/README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 13, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Troubleshooting-orange)

> [!IMPORTANT]
> **Related Docs:** [Runbooks](../../runbooks/podman/maintenance.md) | [Operations Guide](../../how-to/podman/configure-rootless.md)

## Table of Contents

- [Common Issues](#common-issues)
  - [Permission Denied (Mounts)](#1-permission-denied-mounting-volumes)
  - [OOMKilled](#2-oomkilled-or-unexpected-exits)
  - [Network Namespace Error](#3-error-error-joining-network-namespace)
  - [Binding Port 80/443](#4-container-cannot-bind-to-port-80-or-443)
- [Debugging Workflow](#debugging-workflow)

## Common Issues

### 1. "Permission Denied" mounting volumes

**Symptom:**
Containers fail to start or applications inside cannot access mounted files, showing "Permission denied".

**Cause:**
SELinux is blocking access, or file ownership on the host doesn't match the container user.

**Solution:**

* **SELinux Relabeling**: Append `:Z` (private) or `:z` (shared) to the volume mount options.

    ```bash
    podman run -v ./data:/data:Z nginx
    ```

* **Fix Ownership**: Use `podman unshare chown` to set permissions from the container's perspective.

    ```bash
    # Maps host user to container root to set ownership
    podman unshare chown -R 1000:1000 ./data
    ```

[↑ Back to Table of Contents](#table-of-contents)

### 2. "OOMKilled" or Unexpected Exits

**Symptom:**
Container exits immediately or under load with exit code 137.

**Cause:**
The container exceeded its memory limit or the system is out of memory.

**Diagnosis:**
Inspect the container state:

```bash
podman inspect <container_id> --format '{{.State.OOMKilled}}'
```

**Solution:**
Increase memory limits using `--memory`:

```bash
podman run --memory 1g ...
```

[↑ Back to Table of Contents](#table-of-contents)

### 3. "Error: error joining network namespace"

**Symptom:**
Podman fails to start containers in rootless mode with text like `failed to create new network namespace`.

**Cause:**
`slirp4netns` might be missing, broken, or the user lacks sufficient subordinate UIDs.

**Solution:**

1. Ensure `slirp4netns` is installed: `sudo dnf install slirp4netns`.
2. Check `/etc/subuid` for your user entry.
3. Run migration tool to reset the user's namespace configuration:

   ```bash
   podman system migrate
   ```

[↑ Back to Table of Contents](#table-of-contents)

### 4. Container cannot bind to port 80 or 443

**Symptom:**
`Error: bind: permission denied` when trying to expose low ports.

**Cause:**
Rootless users cannot bind to ports < 1024 by default.

**Solution:**

* **Option A**: Map to a high port (e.g., `-p 8080:80`).
* **Option B**: Enable unprivileged port binding system-wide:

    ```bash
    echo "net.ipv4.ip_unprivileged_port_start=80" | sudo tee -a /etc/sysctl.conf
    sudo sysctl -p
    ```

[↑ Back to Table of Contents](#table-of-contents)

## Debugging Workflow

### 1. View Logs

Always start by checking container logs:

```bash
podman logs -f <container_name>
```

### 2. Inspect Configuration

Check the full JSON configuration of a container to verify env vars, mounts, and network settings.

```bash
podman inspect <container_name>
```

### 3. Access Shell

If the container is running but behaving strangely, exec into it for manual investigation:

```bash
podman exec -it <container_name> /bin/bash
```

### 4. Reset Environment

If Podman becomes unresponsive or inconsistent (often after an upgrade):

```bash
podman system migrate
```

[↑ Back to Table of Contents](#table-of-contents)

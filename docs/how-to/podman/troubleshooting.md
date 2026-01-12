# Troubleshooting Podman

This guide provides solutions for common issues encountered when running Podman, with a focus on rootless configurations.

## Common Issues

### 1. "Permission Denied" mounting volumes

**Symptom:**
Containers fail to start or applications inside cannot access mounted files, showing "Permission denied".

**Cause:**
SELinux is blocking access, or file ownership on the host doesn't match the container user.

**Solution:**

* **SELinux**: Append `:Z` (private) or `:z` (shared) to the volume mount options.

    ```bash
    podman run -v ./data:/data:Z nginx
    ```

* **Ownership**: Use `podman unshare chown` to set permissions from the container's perspective.

    ```bash
    podman unshare chown -R 1000:1000 ./data
    ```

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

### 3. "Error: error joining network namespace ... failed to create new network namespace"

**Symptom:**
Podman fails to start containers in rootless mode.

**Cause:**
`slirp4netns` might be missing or broken, or the user lacks sufficient subordinate UIDs.

**Solution:**

* Ensure `slirp4netns` is installed: `sudo dnf install slirp4netns`.
* Check `/etc/subuid` for your user entry.
* Run `podman system migrate` to reset the user's namespace configuration.

### 4. Container cannot bind to port 80 or 443

**Symptom:**
`Error: bind: permission denied` when trying to expose low ports.

**Cause:**
Rootless users cannot bind to ports < 1024 by default.

**Solution:**

* Map to a high port (e.g., `-p 8080:80`).
* Enable unprivileged port binding system-wide:

    ```bash
    echo "net.ipv4.ip_unprivileged_port_start=80" | sudo tee -a /etc/sysctl.conf
    sudo sysctl -p
    ```

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

If the container is running but behaving strangely, exec into it:

```bash
podman exec -it <container_name> /bin/bash
```

### 4. Reset Environment

If Podman becomes unresponsive or inconsistent (often after an upgrade):

```bash
podman system migrate
```

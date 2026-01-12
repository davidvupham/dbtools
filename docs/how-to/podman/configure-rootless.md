# Configure Rootless Podman

Rootless Podman allows unprivileged users to run containers directly without requiring root privileges or a setuid
binary. This significantly improves security by ensuring that even if a container is compromised, the attacker does not
gain root access to the host.

## Prerequisites

On RHEL 8/9, rootless Podman works out of the box for users created after the `container-tools` module is installed,
provided `shadow-utils` (`useradd`, `usermod`) are up to date.

Key components required:

* `slirp4netns`: User-mode networking.
* `fuse-overlayfs`: User-mode filesystem.

Ensure dependencies are installed:

```bash
sudo dnf install -y slirp4netns fuse-overlayfs
```

## User Configuration

### 1. Verify Subordinate UIDs/GIDs

Rootless Podman relies on `/etc/subuid` and `/etc/subgid` to map a range of UIDs/GIDs to the unprivileged user.

Check if your user has a range defined:

```bash
grep $USER /etc/subuid
grep $USER /etc/subgid
```

**Expected Output:**

```text
username:100000:65536
```

(This means `username` can use 65,536 UIDs starting from ID 100,000).

**If no output:**
You need to add entries for the user:

```bash
sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 $USER
```

*Note: You must log out and log back in for these changes to take effect.*

### 2. Enable User Linger (Optional but Recommended)

If you want long-running containers (like web servers or databases) to persist after you log out:

```bash
loginctl enable-linger $USER
```

## Networking

Rootless Podman uses `slirp4netns` by default.

### Exposing Ports

Rootless users usually cannot bind to ports < 1024 (privileged ports).

**Attempting to bind port 80:**

```bash
podman run -p 80:80 nginx
# Error: bind: permission denied
```

**Solution 1: Use unprivileged ports**
Map to a high port (e.g., 8080):

```bash
podman run -p 8080:80 nginx
```

**Solution 2: Allow lower ports (System-wide)**
This allows **all** unprivileged users to bind to ports >= 80.

```bash
echo "net.ipv4.ip_unprivileged_port_start=80" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## Caveats and Limitations

1. **Ping**: ICMP ping might not work inside containers unless configured in `sysctl`.
2. **Resource Limits**: Rootless containers are subject to the user's cgroup limits.

## Troubleshooting

### "there might not be enough IDs available in the namespace"

* Check `/etc/subuid` and `/etc/subgid`.
* Run `podman system migrate` to reset local configuration if standard processing changes.

### "permission denied" on volume mounts

* Files on the host owned by the user might appear as `root` inside the container.
* Use the `:Z` flag when mounting SELinux protected volumes:

    ```bash
    podman run -v ./data:/data:Z ...
    ```

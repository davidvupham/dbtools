# Podman Operations & Maintenance

**🔗 [← Back to Podman Documentation Index](../../explanation/podman/README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 13, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Runbook-orange)

> [!IMPORTANT]
> **Related Docs:** [Architecture](../../explanation/podman/podman-architecture.md) | [Installation](../../how-to/podman/install-podman-rhel.md) | [Cheatsheet](../../reference/podman/cheatsheet.md) | [Systemd Integration](../../how-to/podman/systemd-integration.md) | [Troubleshooting](../../how-to/podman/troubleshooting.md)

## Table of Contents

- [Disk Space Management](#disk-space-management)
- [Updates and Upgrades](#updates-and-upgrades)
- [Backup & Restore](#backup--restore)

## Disk Space Management

Containers and images can consume significant disk space over time.

### Monitor Usage

Check how much space Podman is using:

```bash
podman system df
```

**Output Example:**
```text
TYPE            TOTAL   ACTIVE   SIZE    RECLAIMABLE
Images          5       2        1.1GB   500MB (45%)
Containers      3       1        150MB   50MB (33%)
Local Volumes   2       1        200MB   100MB (50%)
```

### Pruning (Cleanup)

> [!WARNING]
> These commands are destructive.

1. **Remove stopped containers:**

    ```bash
    podman container prune
    ```

2. **Remove unused images (dangling):**

    ```bash
    podman image prune
    ```

3. **Remove ALL unused data:** (images, containers, networks)

    ```bash
    # -a (all): Remove all unused images, not just dangling ones
    # --volumes: Prune unused volumes as well
    podman system prune -a --volumes
    ```

[↑ Back to Table of Contents](#table-of-contents)

## Updates and Upgrades

### Check usage before upgrade

Before upgrading RHEL packages, ensure critical containers are healthy.

```bash
podman ps -a
```

### Apply Upgrade

```bash
sudo dnf update -y container-tools
```

### Automatic Container Updates

Automate image updates for running containers managed by systemd.

1. **Label your container**: Start it with `--label "io.containers.autoupdate=registry"`.
2. **Enable the timer**:

    ```bash
    systemctl --user enable --now podman-auto-update.timer
    ```

This timer will check for regular updates (default: daily) and restart containers if a newer image is found in the registry.

### Post-Upgrade Validation

After an upgrade, it is recommended to run `podman system migrate` to apply any internal storage or namespace changes.

```bash
podman system migrate
```

[↑ Back to Table of Contents](#table-of-contents)

## Backup & Restore

### Exporting Containers

Export a container's filesystem content to a tarball:

```bash
podman export <container_id> -o my_container.tar
```

### Saving Images

Save an image (layers + metadata) for transfer to an air-gapped system:

```bash
podman save -o my_image.tar <image_name>
```

### Loading Images

Load an image from a tarball:

```bash
podman load -i my_image.tar
```

[↑ Back to Table of Contents](#table-of-contents)

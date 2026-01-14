# Podman Operations & Maintenance

This runbook outlines standard operational tasks for maintaining a healthy Podman environment.

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

**Warning:** These commands are destructive.

1. **Remove stopped containers:**

    ```bash
    podman container prune
    ```

2. **Remove unused images (dangling):**

    ```bash
    podman image prune
    ```

3. **Remove ALL unused data (images, containers, networks):**

    ```bash
    podman system prune --volumes
    ```

    * `--all` (`-a`): Remove all unused images, not just dangling ones.
    * `--volumes`: Prune unused volumes as well.

## Updates and Upgrades

Podman on RHEL is updated via `dnf`.

### Check usage before upgrade

Before upgrading, ensure critical containers are healthy.

```bash
podman ps -a
```

### Apply Upgrade

```bash
sudo dnf update -y container-tools
```

### Automatic Container Updates (`podman auto-update`)

You can automate image updates for running containers managed by systemd.

1. **Label your container**: Start it with `--label "io.containers.autoupdate=registry"`.
2. **Enable the timer**:

    ```bash
    systemctl --user enable --now podman-auto-update.timer
    ```

This timer will check for regular updates (default: daily) and restart containers if a newer image is found in the registry.

### Post-Upgrade Validation

After an upgrade, it is recommended to run `podman system migrate` to apply any internal storage or namespace changes
required by the new version.

```bash
podman system migrate
```

## Backup & Restore

### Exporting Containers

You can export a container's filesystem to a tarball:

```bash
podman export <container_id> -o my_container.tar
```

### Saving Images

Save an image for transfer to an air-gapped system:

```bash
podman save -o my_image.tar <image_name>
```

### Loading Images

Load an image from a tarball:

```bash
podman load -i my_image.tar
```

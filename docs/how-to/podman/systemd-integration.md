# Podman Systemd Integration

**🔗 [← Back to Podman Documentation Index](../../explanation/podman/README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 13, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Feature](https://img.shields.io/badge/Feature-Systemd-blue)

> [!IMPORTANT]
> **Related Docs:** [Installation](./install-podman-rhel.md) | [Reference](../../reference/podman/cheatsheet.md)

## Table of Contents

- [Overview](#overview)
- [Method 1: Quadlet (Recommended)](#method-1-quadlet-recommended)
- [Method 2: Legacy Generation](#method-2-legacy-generation)
- [Auto-Update Configuration](#auto-update-configuration)

## Overview

Integrating Podman with Systemd allows you to manage containers as native system services. This ensures containers start at boot, restart on failure, and can be managed with standard `systemctl` commands.

### Methods

| Method | Description | Use Case |
|:---|:---|:---|
| **Quadlet** | Declarative `.container` files managed by a generator. | **Recommended** for RHEL 9 / Podman v4.6+ |
| **`podman generate systemd`** | Generates standard unit files from existing containers. | Legacy / RHEL 8 / Older Podman |

[↑ Back to Table of Contents](#table-of-contents)

## Method 1: Quadlet (Recommended)

Quadlet allows you to define containers in a simplified format, which a systemd generator then converts into full service units automatically.

### 1. Create a `.container` file

For a rootless user, create the directory:

```bash
mkdir -p ~/.config/containers/systemd/
```

Create a file named `my-web.container`:

```ini
[Unit]
Description=My Nginx Web Server
After=network-online.target

[Container]
Image=nginx:alpine
PublishPort=8080:80
Exec=nginx -g 'daemon off;'

[Service]
Restart=always

[Install]
WantedBy=default.target
```

### 2. Activate the Service

Reload the systemd daemon (this triggers the generator):

```bash
systemctl --user daemon-reload
```

Start and enable the generated service (note the `.service` extension):

```bash
systemctl --user start my-web.service
systemctl --user enable my-web.service
```

### 3. Verify

```bash
systemctl --user status my-web.service
```

[↑ Back to Table of Contents](#table-of-contents)

## Method 2: Legacy Generation

This method involves running a container first, then asking Podman to create a unit file for it.

### 1. Run the Container

```bash
podman run -d --name my-old-web -p 8081:80 nginx:alpine
```

### 2. Generate Unit File

```bash
mkdir -p ~/.config/systemd/user/
cd ~/.config/systemd/user/

# Generate the file
podman generate systemd --name my-old-web --files --new
```

* `--files`: Write to a file instead of stdout.
* `--new`: Create a transient container service (creates on start, removes on stop).

### 3. Enable and Start

```bash
podman stop my-old-web
podman rm my-old-web
systemctl --user daemon-reload
systemctl --user enable --now container-my-old-web.service
```

[↑ Back to Table of Contents](#table-of-contents)

## Auto-Update Configuration

Podman and Systemd can work together to automatically update your containers when a new image is available.

### Setup Steps

1. **Tag the container**:
   * **Quadlet:** Add `AutoUpdate=registry` under `[Container]`.
   * **CLI:** Add `--label "io.containers.autoupdate=registry"`.

2. **Enable the timer**:

   ```bash
   systemctl --user enable --now podman-auto-update.timer
   ```

**How it works:**
The timer runs (default: daily), checks the registry for newer image digests, pulls them, and restarts any affected services transparently.

[↑ Back to Table of Contents](#table-of-contents)

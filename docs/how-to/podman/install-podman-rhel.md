# How to Install Podman on Red Hat Enterprise Linux (RHEL)

This guide covers the installation of Podman on RHEL 8 and RHEL 9.

## Prerequisites

* A system running Red Hat Enterprise Linux 8 or 9.
* Root or sudo privileges.
* Subscription Manager registered (to access repositories).

## Installation Steps

On RHEL 8 and 9, Podman is available through the `container-tools` module.

### 1. Update System

Ensure your system is up to date.

```bash
sudo dnf update -y
```

### 2. Install Container Tools

The `container-tools` module includes Podman, Buildah, Skopeo, and generic runc.

```bash
sudo dnf module install -y container-tools:rhel8
# OR for the latest stream
sudo dnf install -y container-tools
```

### 3. Verify Installation

Check the installed version of Podman.

```bash
podman --version
```

Verify basic functionality by running a test container:

```bash
podman run --rm hello-world
```

## Basic Configuration

### Registries Configuration (`/etc/containers/registries.conf`)

By default, RHEL may be configured to look at Red Hat's registries. You may want to add `docker.io` or `quay.io` to your
search registries.

Edit `/etc/containers/registries.conf`:

```toml
[registries.search]
registries = ['registry.access.redhat.com', 'registry.redhat.io', 'docker.io', 'quay.io']
```

### Storage Configuration (`/etc/containers/storage.conf`)

Podman uses `overlay` driver by default.

* **Root functionality**: Configuring storage for root is managed in `/etc/containers/storage.conf`.
* **Rootless functionality**: Users have their own configuration in `$HOME/.config/containers/storage.conf` (if
    overriding defaults is needed).

The default location for root container storage is `/var/lib/containers/storage`.
The default location for rootless container storage is `$HOME/.local/share/containers/storage`.

## Upgrade Podman

To upgrade Podman to a newer version provided by the RHEL streams:

```bash
sudo dnf update -y podman
```

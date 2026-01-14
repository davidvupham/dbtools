# How to Install Podman on Red Hat Enterprise Linux (RHEL)

**🔗 [← Back to Podman Documentation Index](../../explanation/podman/README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 13, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![RHEL Version](https://img.shields.io/badge/RHEL-8%2F9-red)

> [!IMPORTANT]
> **Related Docs:** [Architecture](../../explanation/podman/podman-architecture.md) | [Cheatsheet](../../reference/podman/cheatsheet.md) | [Maintenance](../../runbooks/podman/maintenance.md) | [Troubleshooting](./troubleshooting.md) | [Tutorial](../../tutorials/podman/getting-started.md)

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Steps](#installation-steps)
- [Basic Configuration](#basic-configuration)
- [Upgrade Procedure](#upgrade-procedure)
- [Verification](#verification)

## Prerequisites

* **OS**: Red Hat Enterprise Linux 8 or 9
* **Privileges**: Root or sudo access
* **Network**: Subscription Manager registered (to access repositories)

[↑ Back to Table of Contents](#table-of-contents)

## Installation Steps

On RHEL 8 and 9, Podman is available through the native `container-tools` module.

### 1. Update System

Ensure your system is up to date to avoid dependency conflicts.

```bash
sudo dnf update -y
```

### 2. Install Container Tools

The `container-tools` module is a meta-package that includes Podman, Buildah, Skopeo, and generic runc.

```bash
# For RHEL 8 specific stream
sudo dnf module install -y container-tools:rhel8

# OR for the latest rolling stream (Recommended)
sudo dnf install -y container-tools
```

### 3. Verify Installation

Check the installed version and ensure the binary is in your path.

```bash
podman --version
```

[↑ Back to Table of Contents](#table-of-contents)

## Basic Configuration

### Registries Configuration (`/etc/containers/registries.conf`)

By default, RHEL is configured to search Red Hat's registries. To use Docker Hub or Quay.io, add them to the search list.

**File:** `/etc/containers/registries.conf`

```toml
[registries.search]
registries = ['registry.access.redhat.com', 'registry.redhat.io', 'docker.io', 'quay.io']
```

### Storage Configuration (`/etc/containers/storage.conf`)

Podman uses the `overlay` driver by default.

* **Root Users**: Configuration is managed in `/etc/containers/storage.conf`.
  * Default path: `/var/lib/containers/storage`
* **Rootless Users**: Users can override defaults in `$HOME/.config/containers/storage.conf`.
  * Default path: `$HOME/.local/share/containers/storage`

[↑ Back to Table of Contents](#table-of-contents)

## Upgrade Procedure

To upgrade Podman to a newer version provided by the RHEL streams:

```bash
# Update just the Podman package
sudo dnf update -y podman

# OR update the entire container tools group
sudo dnf update -y container-tools
```

**Post-Upgrade Recommendation:**
Run `podman system migrate` after major upgrades to apply any storage or namespace format changes.

```bash
podman system migrate
```

[↑ Back to Table of Contents](#table-of-contents)

## Verification

Verify basic functionality by running a test container:

```bash
# Run a transient hello-world container
podman run --rm hello-world
```

**Expected Output:**
You should see a "Hello from Docker!" (or similar OCI) welcome message indicating the runtime is working correctly.

[↑ Back to Table of Contents](#table-of-contents)

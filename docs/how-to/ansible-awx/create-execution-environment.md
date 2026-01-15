# Create a Custom Execution Environment

**[← Back to Ansible AWX How-To](./README.md)**

> **Document Version:** 1.1
> **Last Updated:** January 15, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-How_To-blue)

> [!IMPORTANT]
> **Related Docs:** [Architecture](../../explanation/ansible-awx/architecture.md) | [Best Practices](../../reference/ansible-awx/best-practices.md)

## Table of Contents

- [Objective](#objective)
- [Audience](#audience)
- [Prerequisites](#prerequisites)
- [Steps](#steps)
  - [1. Create the Context Directory](#1-create-the-context-directory)
  - [2. Define the Dockerfile](#2-define-the-dockerfile)
  - [3. Build the Image](#3-build-the-image)
  - [4. Push to Registry](#4-push-to-registry)
  - [5. Configure AWX](#5-configure-awx)
- [Expected Outcome](#expected-outcome)
- [Troubleshooting](#troubleshooting)

## Objective

This guide explains how to create a custom Ansible Execution Environment (EE). This allows you to package specific dependencies (Python libraries, system binaries, Ansible Collections) into a portable container image for use with AWX.

[↑ Back to Table of Contents](#table-of-contents)

## Audience

This guide is for:

- **Automation Engineers** who need custom Python packages or collections in AWX
- **Platform Engineers** managing AWX infrastructure

[↑ Back to Table of Contents](#table-of-contents)

## Prerequisites

- **Host**: Linux, macOS, or Windows via **WSL 2**
- **Engine**: Docker or Podman installed
- **Registry**: Access to a container registry (e.g., Docker Hub, Quay.io, or private registry)

[↑ Back to Table of Contents](#table-of-contents)

## Steps

### 1. Create the Context Directory

Create a directory for your Docker build context:

```bash
mkdir -p docker/ansible-awx
cd docker/ansible-awx
```

[↑ Back to Table of Contents](#table-of-contents)

### 2. Define the Dockerfile

Create a `Dockerfile` that extends the official Ansible Runner or AWX EE base image.

> [!NOTE]
> See `docker/ansible-awx/Dockerfile` in the codebase for the reference implementation.

```dockerfile
# Start from the official AWX Execution Environment
FROM quay.io/ansible/awx-ee:latest

# Switch to root to install system packages
USER root

# Install system dependencies
# RUN dnf install -y git gcc

# Switch back to runner user (1000) for pip installs if desired,
# or stay root for global installs (common in EEs)
# USER 1000

# Install Python dependencies
# RUN pip install requests pandas

# Install Ansible Collections
# Note: In production, consider using a requirements.yml + ansible-builder
RUN ansible-galaxy collection install community.general
```

[↑ Back to Table of Contents](#table-of-contents)

### 3. Build the Image

Run the docker build command. Tag it with your registry and version.

```bash
docker build -t my-registry/custom-awx-ee:1.0.0 .
```

> [!TIP]
> **WSL 2 Users**: Ensure your Docker Desktop is configured to use the WSL 2 backend, or use Podman within your WSL distribution.

[↑ Back to Table of Contents](#table-of-contents)

### 4. Push to Registry

AWX must be able to pull the image from a registry.

```bash
docker push my-registry/custom-awx-ee:1.0.0
```

[↑ Back to Table of Contents](#table-of-contents)

### 5. Configure AWX

1. Log in to your AWX web interface.
2. Navigate to **Administration** -> **Execution Environments**.
3. Click **Add**.
4. **Name**: `Custom Environment`.
5. **Image**: `my-registry/custom-awx-ee:1.0.0`.
6. **Pull Policy**: `Always` or `Missing` (use `Always` if using 'latest' tag).
7. Save.
8. Update your Job Templates to use this new Execution Environment.

[↑ Back to Table of Contents](#table-of-contents)

## Expected Outcome

After completing these steps, you have:

- A custom Execution Environment image in your registry
- AWX configured to use the new EE for job execution
- Job Templates updated to reference the custom EE

[↑ Back to Table of Contents](#table-of-contents)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Image pull fails in AWX | Verify registry credentials are configured in AWX under **Administration** -> **Credential Types** |
| Collection not found at runtime | Ensure `ANSIBLE_COLLECTIONS_PATH` is set correctly in the Dockerfile |
| Permission denied errors | Check that the container runs as UID 1000 (runner user) |

[↑ Back to Table of Contents](#table-of-contents)

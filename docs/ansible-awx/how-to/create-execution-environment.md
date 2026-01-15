# Create a Custom Execution Environment

**🔗 [← Back to Ansible AWX Index](../README.md)**

> **Document Version:** 1.1
> **Last Updated:** January 15, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-How_To-blue)

> [!IMPORTANT]
> **Related Docs:** [Architecture](../explanation/architecture.md)

## Objective

This guide explains how to create a custom Ansible Execution Environment (EE). This allow you to package specific dependencies (Python libraries, System binaries, Ansible Collections) into a portable container image for use with AWX.

## Prerequisites

- **Host**: Linux, macOS, or Windows via **WSL 2**.
- **Engine**: Docker or Podman installed.
- **Registry**: Access to a container registry (e.g., Docker Hub, Quay.io, or private registry).

## Steps

### 1. Create the Context Directory

Create a directory for your Docker build context:

```bash
mkdir -p docker/ansible-awx
cd docker/ansible-awx
```

### 2. Define the Dockerfile

Creates a `Dockerfile` that extends the official Ansible Runner or AWX EE base image.

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

### 3. Build the Image

Run the docker build command. Tag it with your registry and version.

```bash
docker build -t my-registry/custom-awx-ee:1.0.0 .
```

> [!TIP]
> **WSL 2 Users**: Ensure your Docker Desktop is configured to use the WSL 2 backend, or use Podman within your WSL distribution.

### 4. Push to Registry

AWX must be able to pull the image from a registry.

```bash
docker push my-registry/custom-awx-ee:1.0.0
```

### 5. Configure AWX

1. Log in to your AWX web interface.
2. Navigate to **Administration** -> **Execution Environments**.
3. Click **Add**.
4. **Name**: `Custom Environment`.
5. **Image**: `my-registry/custom-awx-ee:1.0.0`.
6. **Pull Policy**: `Always` or `Missing` (use `Always` if using 'latest' tag).
7. Save.
8. Update your Job Templates to use this new Execution Environment.

[↑ Back to Table of Contents](#objective)

# Podman Cheatsheet

**🔗 [← Back to Podman Documentation Index](../../explanation/podman/README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 13, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Cheatsheet-purple)

> [!IMPORTANT]
> **Related Docs:** [Architecture](../../explanation/podman/podman-architecture.md) | [Installation](../../how-to/podman/install-podman-rhel.md) | [Maintenance](../../runbooks/podman/maintenance.md) | [Troubleshooting](../../how-to/podman/troubleshooting.md) | [Tutorial](../../tutorials/podman/getting-started.md)

## Table of Contents

- [Basic Management](#basic-management)
- [Images](#images)
- [Containers](#containers)
- [Pods](#pods)
- [System & Maintenance](#system--maintenance)

## Basic Management

| Action | Command |
| :--- | :--- |
| **Check Version** | `podman --version` |
| **System Info** | `podman info` |
| **Login to Registry** | `podman login docker.io` |
| **Logout** | `podman logout` |

[↑ Back to Table of Contents](#table-of-contents)

## Images

| Action | Command |
| :--- | :--- |
| **Search Image** | `podman search <term>` |
| **Pull Image** | `podman pull <image_name>` |
| **List Images** | `podman images` |
| **Remove Image** | `podman rmi <image_id>` |
| **Build Image** | `podman build -t <tag> .` |
| **Inspect Image** | `podman inspect <image_id>` |

[↑ Back to Table of Contents](#table-of-contents)

## Containers

| Action | Command |
| :--- | :--- |
| **Run Container** | `podman run -dt --name <name> <image>` |
| **Run & Remove** | `podman run --rm -it <image> /bin/bash` |
| **List Running** | `podman ps` |
| **List All** | `podman ps -a` |
| **Stop Container** | `podman stop <name>` |
| **Start Container** | `podman start <name>` |
| **Remove Container** | `podman rm <name>` |
| **View Logs** | `podman logs <name>` |
| **Execute Command** | `podman exec -it <name> /bin/bash` |

[↑ Back to Table of Contents](#table-of-contents)

## Pods

| Action | Command |
| :--- | :--- |
| **Create Pod** | `podman pod create --name <pod_name>` |
| **Run in Pod** | `podman run -dt --pod <pod_name> <image>` |
| **List Pods** | `podman pod ps` |
| **Stop Pod** | `podman pod stop <pod_name>` |
| **Remove Pod** | `podman pod rm <pod_name>` |
| **Generate Kube** | `podman generate kube <pod_name> > pod.yaml` |
| **Play Kube** | `podman play kube pod.yaml` |

[↑ Back to Table of Contents](#table-of-contents)

## System & Maintenance

| Action | Command |
| :--- | :--- |
| **Show Disk Usage** | `podman system df` |
| **Prune Unused** | `podman system prune` |
| **Prune All** | `podman system prune -a --volumes` |
| **Reset Storage** | `podman system reset` (Warning: Deletes everything) |
| **Run as User** | `podman run --userns=keep-id ...` |

[↑ Back to Table of Contents](#table-of-contents)

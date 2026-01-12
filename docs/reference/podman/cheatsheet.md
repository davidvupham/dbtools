# Podman Cheatsheet

## Basic Management

| Action | Command |
| :--- | :--- |
| **Check Version** | `podman --version` |
| **System Info** | `podman info` |
| **Login to Registry** | `podman login docker.io` |
| **Logout** | `podman logout` |

## Images

| Action | Command |
| :--- | :--- |
| **Search Image** | `podman search <term>` |
| **Pull Image** | `podman pull <image_name>` |
| **List Images** | `podman images` |
| **Remove Image** | `podman rmi <image_id>` |
| **Build Image** | `podman build -t <tag> .` |
| **Inspect Image** | `podman inspect <image_id>` |

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

## Pods (Podman Specific)

| Action | Command |
| :--- | :--- |
| **Create Pod** | `podman pod create --name <pod_name>` |
| **Run in Pod** | `podman run -dt --pod <pod_name> <image>` |
| **List Pods** | `podman pod ps` |
| **Stop Pod** | `podman pod stop <pod_name>` |
| **Remove Pod** | `podman pod rm <pod_name>` |
| **Generate Kube** | `podman generate kube <pod_name> > pod.yaml` |
| **Play Kube** | `podman play kube pod.yaml` |

## System & Maintenance

| Action | Command |
| :--- | :--- |
| **Show Disk Usage** | `podman system df` |
| **Prune Unused** | `podman system prune` |
| **Prune All** | `podman system prune -a --volumes` |
| **Reset Storage** | `podman system reset` (Warning: Deletes everything) |

## Advanced

| Action | Command |
| :--- | :--- |
| **Generate Systemd** | `podman generate systemd --name <container> --files` |
| **Run as User** | `podman run --userns=keep-id ...` (Map user ID directly) |

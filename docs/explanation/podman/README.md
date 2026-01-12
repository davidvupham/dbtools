# Podman Overview

Podman (Pod Manager) is a daemonless container engine for developing, managing, and running OCI (Open Container Initiative)
containers and pods on your Linux system.

## What is Podman?

Podman interacts with the image, container, and storage registry directly, without requiring a central "daemon" process
(like `dockerd`). This architecture provides several key benefits:

* **Daemonless**: No single point of failure or root-owned daemon process running in the background.
* **Rootless by Design**: Containers can be run easily by unprivileged users, significantly improving security
    posture.
* **Docker Compatible**: Podman provides a Docker-compatible command line interface. In most cases, you can simply alias `docker=podman`.

## Architecture: Daemonless and Fork/Exec

Unlike Docker, which uses a client-server architecture (CLI client talks to Docker Daemon), Podman uses a traditional **Fork/Exec** model.

* When you run a `podman` command, the Podman binary itself performs the operation.
* It creates a child process ensuring that the container itself is a direct descendant of the process that launched it.
* This fits naturally into systemd and other process managers.

## Comparison: Podman vs Docker

| Feature | Docker | Podman |
| :--- | :--- | :--- |
| **Architecture** | Client-Server (Daemon) | Daemonless (Fork/Exec) |
| **Root Privileges** | Required for Daemon (mostly) | Not Required (Rootless) |
| **Orchestration** | Docker Swarm | Kubernetes (Podman can generate K8s YAML) |
| **Process Model** | Container is child of Daemon | Container is child of generic process |
| **Image Standard** | OCI Compliant | OCI Compliant |

## Key Concepts

### Pods

Podman supports the concept of **Pods**, similar to Kubernetes Pods. A Pod is a group of one or more containers sharing
the same network, pid, and ipc namespaces. This allows you to manage closely related containers as a single unit
locally, mirroring how they would run in Kubernetes.

### Rootless Mode

Running containers as a non-root user is a core feature. It maps the user's UID on the host to root (UID 0) inside the
container using `user_namespaces`. This ensures that even if a container breakout occurs, the attacker only has the
privileges of the unprivileged user on the host.

## When to use Podman?

* You need improved security (Rootless).
* You are running on Red Hat Enterprise Linux (RHEL), where it is the native tool.
* You want to generate Kubernetes YAML from your local containers (`podman generate kube`).
* You want integration with systemd (`podman generate systemd`).

# Getting Started with Podman

**🔗 [← Back to Podman Documentation Index](../../explanation/podman/README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 13, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Tutorial-blue)

> [!IMPORTANT]
> **Prerequisites:** Podman installed ([Installation Guide](../../how-to/podman/install-podman-rhel.md)) | basic terminal knowledge.

## Table of Contents

- [1. Running Your First Container](#1-running-your-first-container)
- [2. Building an Image](#2-building-an-image)
- [3. Working with Pods](#3-working-with-pods)
- [4. Cleanup](#4-cleanup)

## 1. Running Your First Container

Let's pull and run a simple web server to verify your installation.

```bash
# Run Nginx in detached mode
podman run -dt -p 8080:80 --name my-nginx nginx:alpine
```

**Command Breakdown:**
* `-d`: Detached mode (run in background).
* `-t`: Allocate a pseudo-TTY (often needed for interactive shell access later).
* `-p 8080:80`: Map host port `8080` to container port `80`.
* `--name`: Assign a friendly name (easier than using random IDs).

**Verify it works:**
Open your browser to `http://localhost:8080` or use curl:

```bash
curl http://localhost:8080
```

[↑ Back to Table of Contents](#table-of-contents)

## 2. Building an Image

Create a file named `Containerfile` (Podman's preference, though `Dockerfile` works too) in your current directory:

```dockerfile
FROM registry.access.redhat.com/ubi9/ubi:latest
RUN dnf install -y python3
CMD ["python3", "-m", "http.server", "8000"]
```

**Build the image:**

```bash
podman build -t my-python-app .
```

* `-t` (`--tag`): Name your image `my-python-app`.
* `.`: Build context is the current directory.

**Run your new image:**

```bash
podman run -dt -p 8001:8000 my-python-app
```

Check with `curl http://localhost:8001`.

[↑ Back to Table of Contents](#table-of-contents)

## 3. Working with Pods

One of Podman's unique features is the native ability to manage **Pods** locally. A Pod is a group of containers that share network, storage, and IPC namespaces.

**Scenario**: We want a "Database" and a "Web Admin Interface" to talk to each other on `localhost`.

### Step A: Create an empty Pod
We expose port `8081` on the Pod itself.

```bash
podman pod create --name my-app-pod -p 8081:80
```

### Step B: Run containers inside the Pod

1. **Start Database (PostgreSQL):**
   * Note we don't publish ports here; it shares the Pod's network.

    ```bash
    podman run -dt --pod my-app-pod -e POSTGRES_PASSWORD=secret postgres:alpine
    ```

2. **Start Web Interface (Adminer):**

    ```bash
    podman run -dt --pod my-app-pod adminer
    ```

**Why this is cool:**
Since both containers are in the same Pod, they are on `localhost` relative to each other. Adminer can talk to Postgres on `localhost:5432` without complex bridge networking!

### Step C: Access the application
Go to `http://localhost:8081`. Log in with:
* System: PostgreSQL
* Server: `localhost`
* Username: `postgres`
* Password: `secret`

[↑ Back to Table of Contents](#table-of-contents)

## 4. Cleanup

Stop and remove the Pod (which automatically handles all containers inside it):

```bash
podman pod stop my-app-pod
podman pod rm my-app-pod
```

Clean up individual containers:

```bash
podman stop my-nginx my-python-app
podman rm my-nginx my-python-app
```

[↑ Back to Table of Contents](#table-of-contents)

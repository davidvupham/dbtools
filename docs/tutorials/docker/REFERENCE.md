# Docker Quick Reference

A cheat sheet for common Docker commands and configurations.

## Docker CLI

### Images

| Command | Description |
| :--- | :--- |
| `docker build -t <name> .` | Build an image from a Dockerfile in the current directory. |
| `docker images` | List all local images. |
| `docker rmi <image_id>` | Delete an image. |
| `docker image prune` | Remove unused (dangling) images. |
| `docker history <image>` | Show the history (layers) of an image. |

### Containers

| Command | Description |
| :--- | :--- |
| `docker run -d -p <host>:<container> <image>` | Run a container in background (-d) exposing ports (-p). |
| `docker ps` | List running containers. |
| `docker ps -a` | List all containers (running and stopped). |
| `docker logs -f <container>` | Follow log output of a container. |
| `docker exec -it <container> sh` | Open an interactive shell inside a running container. |
| `docker stop <container>` | Gracefully stop a container. |
| `docker rm <container>` | Remove a stopped container. |
| `docker system prune` | **WARNING:** Remove all stopped containers, unused networks, and dangling images. |

### Volumes & Networks

| Command | Description |
| :--- | :--- |
| `docker volume create <name>` | Create a named volume. |
| `docker volume ls` | List volumes. |
| `docker network create <name>` | Create a user-defined bridge network. |
| `docker network ls` | List networks. |
| `docker network connect <net> <container>` | Connect a running container to a network. |

---

## Dockerfile Instructions

| Instruction | Usage | Description |
| :--- | :--- | :--- |
| `FROM` | `FROM python:3.9` | Base image. Must be first. |
| `WORKDIR` | `WORKDIR /app` | Set working directory. |
| `COPY` | `COPY . .` | Copy from host to container. `COPY src dest`. |
| `RUN` | `RUN pip install -r req.txt` | Execute build-time command. |
| `ENV` | `ENV DEBUG=true` | Set persistent environment variable. |
| `ARG` | `ARG VERSION=1.0` | Set build-time variable. |
| `CMD` | `CMD ["python", "app.py"]` | Default command. Overridable. |
| `ENTRYPOINT` | `ENTRYPOINT ["/entry.sh"]` | Application executable. Not usually overridden. |
| `EXPOSE` | `EXPOSE 80` | Document listening ports. |
| `USER` | `USER appuser` | Switch user ID for security. |

---

## Docker Compose

See `docker-compose.yml` structure.

| Command | Description |
| :--- | :--- |
| `docker compose up -d` | Start entire stack in background. |
| `docker compose down` | Stop stack and remove containers/networks. |
| `docker compose down -v` | Stop stack and REMOVE VOLUMES (Data loss warning!). |
| `docker compose logs -f <service>` | Follow logs for specific service. |
| `docker compose build` | Rebuild images for services. |
| `docker compose restart <service>` | Restart a specific service. |

---

## Dos and Don'ts

| Category | Do ✅ | Don't ❌ |
| :--- | :--- | :--- |
| **Images** | Use specific tags (`node:18`) | Use `latest` tag in production |
| **Builds** | Use `.dockerignore` to block local files | Copy your entire local directory |
| **Security** | Run as a non-root user | Run everthing as `root` (default) |
| **Secrets** | Mount secrets at runtime | Bake secrets (`API_KEY`) into the image |
| **Networking** | Use user-defined bridge networks | Link containers via IP addresses |
| **Persistence** | Use Volumes for database data | Store data inside the container layer |
| **Process** | Run one process per container | Use Docker as a monolithic VM |

---

## Glossary

### Core Concepts

- **Image:** Read-only template containing application code and dependencies. Think of it as a "class" in OOP.
- **Container:** Runnable instance of an image. Think of it as an "object" created from the class.
- **Layer:** Images are built in layers. Each Dockerfile instruction creates a layer. Layers are cached for efficiency.
- **Registry:** Storage for images (Docker Hub, GitHub Container Registry, JFrog Artifactory, AWS ECR).

### Runtime

- **Daemon:** The background service (`dockerd`) running on the host that manages containers.
- **Volume:** Persistent data storage that lives outside the container lifecycle. Survives container removal.
- **Bind Mount:** Mounts a host directory directly into a container. Used for development.
- **tmpfs:** In-memory storage that disappears when container stops. Used for secrets and temp files.

### Networking

- **Bridge Network:** Default network type. Containers on the same bridge can communicate.
- **Overlay Network:** Multi-host networking for Swarm/Kubernetes.
- **Port Mapping:** `-p 8080:80` maps host port 8080 to container port 80.

### Build

- **Dockerfile:** Text file with instructions to build an image.
- **Build Context:** The set of files sent to the Docker daemon for building (the `.` in `docker build .`).
- **Multi-stage Build:** Using multiple `FROM` statements to create smaller final images.
- **BuildKit:** Modern build system with better caching and parallel builds.

### Orchestration

- **Service:** A desired state definition (image, replicas, ports) in Swarm or Compose.
- **Replica:** A copy of a container running as part of a service.
- **Stack:** A collection of services deployed together (Compose or Swarm).

### Security

- **Capability:** Linux kernel permissions (e.g., `NET_BIND_SERVICE`). Drop unused ones.
- **Seccomp:** Secure computing mode that restricts system calls.
- **Non-root User:** Running containers as a user other than root for security.

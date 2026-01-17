# Quick Reference

Command cheat sheet for Docker and Podman. Commands are nearly identical between tools.

---

## Container Lifecycle

| Action | Docker | Podman |
|--------|--------|--------|
| Run container | `docker run IMAGE` | `podman run IMAGE` |
| Run detached | `docker run -d IMAGE` | `podman run -d IMAGE` |
| Run interactive | `docker run -it IMAGE sh` | `podman run -it IMAGE sh` |
| Run with name | `docker run --name NAME IMAGE` | `podman run --name NAME IMAGE` |
| List running | `docker ps` | `podman ps` |
| List all | `docker ps -a` | `podman ps -a` |
| Stop container | `docker stop CONTAINER` | `podman stop CONTAINER` |
| Start container | `docker start CONTAINER` | `podman start CONTAINER` |
| Restart container | `docker restart CONTAINER` | `podman restart CONTAINER` |
| Remove container | `docker rm CONTAINER` | `podman rm CONTAINER` |
| Force remove | `docker rm -f CONTAINER` | `podman rm -f CONTAINER` |
| Remove all stopped | `docker container prune` | `podman container prune` |

---

## Container Interaction

| Action | Docker | Podman |
|--------|--------|--------|
| View logs | `docker logs CONTAINER` | `podman logs CONTAINER` |
| Follow logs | `docker logs -f CONTAINER` | `podman logs -f CONTAINER` |
| Execute command | `docker exec CONTAINER CMD` | `podman exec CONTAINER CMD` |
| Interactive shell | `docker exec -it CONTAINER sh` | `podman exec -it CONTAINER sh` |
| Copy to container | `docker cp FILE CONTAINER:PATH` | `podman cp FILE CONTAINER:PATH` |
| Copy from container | `docker cp CONTAINER:PATH FILE` | `podman cp CONTAINER:PATH FILE` |
| Inspect container | `docker inspect CONTAINER` | `podman inspect CONTAINER` |
| View stats | `docker stats` | `podman stats` |
| View top processes | `docker top CONTAINER` | `podman top CONTAINER` |

---

## Images

| Action | Docker | Podman |
|--------|--------|--------|
| List images | `docker images` | `podman images` |
| Pull image | `docker pull IMAGE` | `podman pull IMAGE` |
| Push image | `docker push IMAGE` | `podman push IMAGE` |
| Build image | `docker build -t NAME .` | `podman build -t NAME .` |
| Build with file | `docker build -f FILE .` | `podman build -f FILE .` |
| Tag image | `docker tag IMAGE NEW_TAG` | `podman tag IMAGE NEW_TAG` |
| Remove image | `docker rmi IMAGE` | `podman rmi IMAGE` |
| Image history | `docker history IMAGE` | `podman history IMAGE` |
| Inspect image | `docker inspect IMAGE` | `podman inspect IMAGE` |
| Save to tar | `docker save IMAGE -o FILE` | `podman save IMAGE -o FILE` |
| Load from tar | `docker load -i FILE` | `podman load -i FILE` |
| Prune unused | `docker image prune` | `podman image prune` |
| Prune all unused | `docker image prune -a` | `podman image prune -a` |

---

## Port Mapping

```bash
# Map host port 8080 to container port 80
docker run -p 8080:80 IMAGE
podman run -p 8080:80 IMAGE

# Map to specific host IP
docker run -p 127.0.0.1:8080:80 IMAGE

# Map random host port
docker run -P IMAGE

# Map multiple ports
docker run -p 8080:80 -p 443:443 IMAGE
```

---

## Volumes and Mounts

| Action | Docker | Podman |
|--------|--------|--------|
| Create volume | `docker volume create NAME` | `podman volume create NAME` |
| List volumes | `docker volume ls` | `podman volume ls` |
| Inspect volume | `docker volume inspect NAME` | `podman volume inspect NAME` |
| Remove volume | `docker volume rm NAME` | `podman volume rm NAME` |
| Prune volumes | `docker volume prune` | `podman volume prune` |

```bash
# Named volume
docker run -v mydata:/data IMAGE
podman run -v mydata:/data IMAGE

# Bind mount (host path)
docker run -v /host/path:/container/path IMAGE
podman run -v /host/path:/container/path IMAGE

# Read-only mount
docker run -v /host/path:/container/path:ro IMAGE

# SELinux labels (Podman/RHEL)
podman run -v /host/path:/container/path:Z IMAGE  # Private
podman run -v /host/path:/container/path:z IMAGE  # Shared

# Rootless volume ownership
podman run -v mydata:/data:U IMAGE
```

---

## Networking

| Action | Docker | Podman |
|--------|--------|--------|
| List networks | `docker network ls` | `podman network ls` |
| Create network | `docker network create NAME` | `podman network create NAME` |
| Inspect network | `docker network inspect NAME` | `podman network inspect NAME` |
| Connect container | `docker network connect NET CONTAINER` | `podman network connect NET CONTAINER` |
| Disconnect container | `docker network disconnect NET CONTAINER` | `podman network disconnect NET CONTAINER` |
| Remove network | `docker network rm NAME` | `podman network rm NAME` |

```bash
# Run on specific network
docker run --network=mynet IMAGE

# Run with host networking
docker run --network=host IMAGE

# Run with no networking
docker run --network=none IMAGE

# Set hostname
docker run --hostname=myhost IMAGE

# Set DNS
docker run --dns=8.8.8.8 IMAGE
```

---

## Docker Compose

```bash
# Start services
docker compose up
docker compose up -d          # Detached

# Stop services
docker compose down
docker compose down -v        # Also remove volumes

# View logs
docker compose logs
docker compose logs -f        # Follow

# List services
docker compose ps

# Execute in service
docker compose exec SERVICE CMD

# Build/rebuild
docker compose build
docker compose up --build     # Build and start

# Scale service
docker compose up -d --scale SERVICE=3

# Pull images
docker compose pull
```

---

## Podman-Specific

```bash
# Pods
podman pod create --name mypod
podman pod create --name mypod -p 8080:80
podman run --pod mypod IMAGE
podman pod ls
podman pod stop mypod
podman pod rm mypod

# Generate Kubernetes YAML
podman generate kube CONTAINER > pod.yaml
podman generate kube --service CONTAINER > pod.yaml

# Play Kubernetes YAML
podman play kube pod.yaml
podman play kube --down pod.yaml

# Generate systemd unit
podman generate systemd --new --name CONTAINER

# Rootless with keep-id
podman run --userns=keep-id IMAGE

# Enter user namespace
podman unshare
podman unshare chown 1000:1000 /path
```

---

## Docker Swarm

```bash
# Initialize swarm
docker swarm init
docker swarm init --advertise-addr IP

# Join swarm
docker swarm join --token TOKEN HOST:PORT

# Leave swarm
docker swarm leave
docker swarm leave --force    # Manager

# List nodes
docker node ls

# Deploy stack
docker stack deploy -c compose.yml STACK

# List stacks
docker stack ls

# List stack services
docker stack services STACK

# Remove stack
docker stack rm STACK

# Create service
docker service create --name NAME IMAGE

# List services
docker service ls

# Service logs
docker service logs SERVICE

# Scale service
docker service scale SERVICE=N

# Update service
docker service update --image NEW_IMAGE SERVICE

# Remove service
docker service rm SERVICE
```

---

## System Management

| Action | Docker | Podman |
|--------|--------|--------|
| System info | `docker info` | `podman info` |
| Disk usage | `docker system df` | `podman system df` |
| Prune all | `docker system prune` | `podman system prune` |
| Prune all + volumes | `docker system prune -a --volumes` | `podman system prune -a --volumes` |
| Events | `docker events` | `podman events` |
| Version | `docker version` | `podman version` |

---

## Registry Operations

```bash
# Login to registry
docker login
docker login registry.example.com

# Logout
docker logout

# Search Docker Hub
docker search TERM

# Tag for registry
docker tag IMAGE registry.example.com/IMAGE:TAG

# Push to registry
docker push registry.example.com/IMAGE:TAG
```

---

## Dockerfile Instructions

```dockerfile
# Base image
FROM ubuntu:22.04
FROM scratch                      # Empty base

# Metadata
LABEL maintainer="name@example.com"
LABEL version="1.0"

# Environment variables
ENV APP_HOME=/app
ENV PATH="${APP_HOME}/bin:${PATH}"
ARG BUILD_VERSION=1.0             # Build-time only

# Working directory
WORKDIR /app

# Copy files
COPY src/ ./src/
COPY --chown=user:group file.txt ./
ADD https://example.com/file.tar.gz ./  # Can extract archives

# Run commands
RUN apt-get update && apt-get install -y \
    package1 \
    package2 \
    && rm -rf /var/lib/apt/lists/*

# Install packages (Alpine)
RUN apk add --no-cache package1 package2

# User
USER appuser
USER 1000:1000

# Expose ports (documentation)
EXPOSE 80 443

# Volumes (documentation)
VOLUME /data

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost/ || exit 1

# Default command
CMD ["python", "app.py"]
ENTRYPOINT ["python"]
CMD ["app.py"]                    # Arguments to ENTRYPOINT
```

---

## Multi-stage Build

```dockerfile
# Build stage
FROM golang:1.21 AS builder
WORKDIR /app
COPY . .
RUN go build -o myapp

# Runtime stage
FROM alpine:3.18
COPY --from=builder /app/myapp /usr/local/bin/
USER 1000
CMD ["myapp"]
```

---

## Compose File (docker-compose.yml)

```yaml
version: "3.8"

services:
  web:
    image: nginx:alpine
    # Or build from Dockerfile
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html:ro
      - data:/data
    environment:
      - ENV_VAR=value
    env_file:
      - .env
    networks:
      - frontend
    depends_on:
      - db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    networks:
      - frontend

volumes:
  data:
  pgdata:

networks:
  frontend:
    driver: bridge
```

---

## Common Options

```bash
# Resource limits
--memory=512m
--cpus=1.5

# Restart policies
--restart=no
--restart=always
--restart=unless-stopped
--restart=on-failure:3

# Environment
-e VAR=value
--env-file=.env

# Labels
--label key=value

# Logging
--log-driver=json-file
--log-opt max-size=10m
--log-opt max-file=3

# Security
--read-only                # Read-only root filesystem
--cap-drop=ALL            # Drop all capabilities
--cap-add=NET_BIND_SERVICE
--security-opt=no-new-privileges
```

---

## Useful Aliases

Add to your shell profile (`.bashrc`, `.zshrc`):

```bash
# Docker
alias d='docker'
alias dc='docker compose'
alias dps='docker ps'
alias dpsa='docker ps -a'
alias di='docker images'
alias drm='docker rm'
alias drmi='docker rmi'
alias dprune='docker system prune -af'

# Podman (if you prefer podman)
alias docker='podman'
alias docker-compose='podman-compose'
```

---

## Configuration Files

### Docker

| File | Purpose |
|------|---------|
| `~/.docker/config.json` | Registry credentials, CLI settings |
| `/etc/docker/daemon.json` | Daemon configuration |

### Podman

| File | Purpose |
|------|---------|
| `~/.config/containers/registries.conf` | Registry configuration |
| `~/.config/containers/storage.conf` | Storage configuration |
| `~/.config/containers/containers.conf` | Runtime configuration |
| `/etc/subuid` | User namespace UID mapping |
| `/etc/subgid` | User namespace GID mapping |

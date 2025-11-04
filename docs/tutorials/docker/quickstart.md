# Docker: Beginner to Advanced Guide

Whether you're just getting started or want to harden production images, this guide walks you through Docker from zero to expert—complete with copy‑pasteable commands, example Dockerfiles, and best practices.

> Looking for a structured deep dive? See the multi‑chapter series: `docs/tutorials/docker/mastering/README.md`.

---

## What Docker is (and isn’t)

- Docker is:
  - A platform for building, shipping, and running containers.
  - Containers = isolated processes with their own filesystem, network, and resources.
  - Images = immutable templates used to create containers.
  - Registries (e.g., Docker Hub) = where images are stored and pulled from.

- Docker isn’t:
  - A full virtual machine. Containers share the host kernel; they’re lighter than VMs.
  - A configuration management tool (like Ansible/Puppet). It packages environments, not entire infra lifecycles.
  - A security boundary you can blindly trust. Apply hardening and least privileges.
  - A silver bullet for stateful prod databases. Use managed services or persistent volumes with care.

---

## Quick Start (5 minutes)

Try these to confirm your setup:

```bash
# Check the engine
docker version

# Run a tiny test container and then exit
docker run --rm hello-world

# Start NGINX on port 8080 (Ctrl+C to stop)
docker run --rm -p 8080:80 nginx:alpine

# List images and containers
docker images
docker ps -a
```

Open http://localhost:8080 in your browser when running the NGINX example.

---

## Core Concepts in 60 Seconds

- Image: read-only layers; built from a Dockerfile.
- Container: a running (or stopped) instance of an image.
- Registry: remote storage for images (Docker Hub, GHCR, ECR, ACR).
- Volume: persistent data managed by Docker.
- Bind mount: map a host directory/file into a container.
- Network: virtual network to connect containers/services.

---

## Beginner: Running Containers

Run a temporary Alpine shell:

```bash
docker run --rm -it alpine:3.19 sh
```

Run BusyBox to test simple commands:

```bash
docker run --rm busybox:1.36 echo "Hello from BusyBox"
```

Map ports and run NGINX:

```bash
# host:container
docker run --rm -d --name web -p 8080:80 nginx:alpine

# See logs and then stop
docker logs -f web
docker stop web
```

Environment variables and command overrides:

```bash
# Print env inside container
docker run --rm -e GREETING=Hi alpine:3.19 sh -c 'echo "$GREETING from $(cat /etc/alpine-release)"'
```

Volumes and bind mounts:

```bash
# Named volume persists data between container restarts
docker volume create mydata

docker run --rm -d --name pg \
  -e POSTGRES_PASSWORD=secret \
  -v mydata:/var/lib/postgresql/data \
  -p 5432:5432 postgres:16-alpine

# Bind mount the current directory into /work
docker run --rm -it -v "$PWD":/work -w /work alpine:3.19 ls -la
```

Clean up:

```bash
docker stop pg
# Remove unused objects—use with care
# Review what will be pruned before confirming
docker system prune
```

---

## Beginner: Images and the Dockerfile

A Dockerfile describes how to build an image. Here’s a minimal Python example:

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
# Run a simple HTTP server
CMD ["python", "-m", "http.server", "8000"]
```

Create a simple `requirements.txt` (can be empty for this demo). Build and run:

```bash
# Build the image with a tag
docker build -t my-python-app:dev .

# Run it and map the port
docker run --rm -d -p 8000:8000 --name py my-python-app:dev

# Verify
curl -I http://localhost:8000

# Tear down
docker stop py
```

Don’t forget a `.dockerignore` to keep images small:

```
# .dockerignore
__pycache__/
*.pyc
*.pyo
*.pytest_cache/
.git/
.env
node_modules/
```

---

## Intermediate: Docker Compose (Multi‑Container)

Compose lets you define multi‑container apps. Save this as `compose.yaml`:

```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
  redis:
    image: redis:7-alpine
```

Run the app:

```bash
# Up in the foreground (Ctrl+C to stop)
docker compose up

# Or run detached
docker compose up -d

# View logs
docker compose logs -f

# Stop and remove containers, networks, etc.
docker compose down
```

Networks are created automatically; `web` can reach `redis` by the service name `redis:6379`.

---

## Intermediate: Multi‑Stage Builds and Smaller Images

Multi‑stage builds let you compile in one image and ship only the runtime in another.

```dockerfile
# Dockerfile (Go example)
FROM golang:1.22-alpine AS build
WORKDIR /src
COPY . .
RUN go build -o app ./...

FROM alpine:3.19
WORKDIR /app
COPY --from=build /src/app ./app
# Non‑root user for safety
RUN adduser -D appuser
USER appuser
ENTRYPOINT ["./app"]
```

Build and run:

```bash
docker build -t my-go-app:latest .
docker run --rm my-go-app:latest --help
```

Benefits: much smaller final images, fewer CVEs, faster pulls.

---

## Intermediate: Tagging, Pushing, and Pulling

```bash
# Tag an image for Docker Hub (replace USERNAME)
docker tag my-python-app:dev USERNAME/my-python-app:dev

# Log in and push
docker login
docker push USERNAME/my-python-app:dev

# Anywhere else, pull and run
docker pull USERNAME/my-python-app:dev
docker run --rm -p 8000:8000 USERNAME/my-python-app:dev
```

For private registries (GHCR, ECR, ACR), use their login and tag formats.

---

## Managing Images

List and inspect images:

```bash
# List all local images
docker image ls

# Only dangling (untagged) layers
docker image ls --filter dangling=true

# Inspect metadata, size, layers, architecture, env, entrypoint
docker image inspect <image>:<tag>

# See how the image was built (layer commands)
docker image history <image>:<tag>
```

Find images by name, tag, or digest:

```bash
# By tag
docker pull nginx:alpine

# Show digest (immutable reference)
docker inspect nginx:alpine --format '{{index .RepoDigests 0}}'
```

Remove and prune safely:

```bash
# Remove a specific image (fails if containers use it)
docker image rm <image>:<tag>

# Force remove (dangerous: also removes by digest); stop/remove dependent containers first
docker image rm -f <image>:<tag>

# Remove dangling images only
docker image prune -f

# Remove unused images older than 72h (keeps in-use images)
docker image prune -f --filter "until=72h"

# Broader cleanup: unused containers, networks, and images (confirm before using -a)
docker system prune
# Everything unused, including images without containers
# WARNING: This will remove a lot. Review before running.
docker system prune -a
```

Move images between hosts (air-gapped, CI → prod):

```bash
# Save to a tarball and load elsewhere
docker image save -o myimg.tar <image>:<tag>
# On another machine
# copy myimg.tar then
#
docker image load -i myimg.tar
```

Quick size review and sorting:

```bash
# Human table with sizes
docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}'

# Largest images first (approximate; size strings vary)
docker images --format '{{.Repository}}:{{.Tag}} {{.Size}}' | sort -h -k2,2
```

Retag and push under a new name (see also the Tagging section above):

```bash
# Retag locally
docker tag <image>:<oldtag> myrepo/<name>:<newtag>
# Push
docker push myrepo/<name>:<newtag>
```

Tip: Use explicit tags and clean up regularly to keep disk usage under control.

---

## Which images are “running”? (containers using images)

Images themselves don’t run—containers do. Here’s how to see running containers and the images they’re based on:

```bash
# Running containers
docker ps

# All containers (running and stopped)
docker ps -a

# Show name, image, and status in a tidy table
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
```

See which images are currently in use by running containers:

```bash
# Unique image list with counts of running containers using them
docker ps --format '{{.Image}}' | sort | uniq -c
```

List containers created from a specific image (by name or ID):

```bash
# By image name:tag
docker ps -a --filter ancestor=nginx:alpine

# By image ID
docker ps -a --filter ancestor=$(docker image inspect --format '{{.Id}}' nginx:alpine)
```

Map a container to the exact image digest it’s running:

```bash
# .Config.Image is the repo:tag; .Image is the immutable image ID/digest
docker inspect -f '{{.Name}} -> {{.Config.Image}} (id: {{.Image}})' <container-name>
```

Note: You cannot remove an image that has dependent containers.

```bash
# This will fail if any container (even stopped) depends on the image
docker rmi <image>:<tag>

# Remove dependent containers first, then remove the image
docker ps -a --filter ancestor=<image>:<tag>
# docker rm <container(s)>
# docker rmi <image>:<tag>
```

---

## Advanced: Security Hardening Essentials

- Run as a non‑root user in the image (`USER` directive).
- Make the filesystem read‑only if possible: `--read-only` and mount writable dirs explicitly.
- Drop capabilities and block privilege escalation:

  ```bash
  docker run --rm \
    --cap-drop ALL --security-opt no-new-privileges \
    --read-only -v app-tmp:/tmp \
    myimage:tag
  ```
- Use minimal bases (alpine, distroless) and remove build tools from final image (multi‑stage).
- Don’t bake secrets into images. Use env vars, Docker secrets, or external secret stores.
- Scan images for vulnerabilities (e.g., `docker scout quickview` or third‑party tools like Trivy).
- Keep host and engine patched; prefer rootless Docker where applicable.

---

## Advanced: Resource Limits and Scheduling

```bash
# Limit memory and CPU
docker run --rm --memory=512m --cpus=1.0 myimage:tag

# Control restarts (useful in Compose)
docker run --restart=on-failure:3 myimage:tag
```

Compose example:

```yaml
services:
  api:
    image: myorg/api:1.0
    deploy:
      resources:
        limits:
          cpus: "1"
          memory: 512M
```

Note: `deploy` resources are fully honored by Swarm/K8s; for plain Compose on Docker Desktop, use `mem_limit`/`cpus` or run flags.

---

## Observability and Debugging

- Logs: `docker logs -f <name>`
- Shell into a container: `docker exec -it <name> sh` (or `bash` if available)
- Inspect everything: `docker inspect <name-or-id>`
- Stats: `docker stats`
- Events: `docker events`
- Port mappings: `docker port <name>`

Common issues:

- Container exits immediately: the main process ended. Use a long‑running command or correct `CMD/ENTRYPOINT`.
- Port not reachable: check `-p host:container`, firewall, and that app binds to `0.0.0.0`.
- Permission denied on mounts: check user IDs, SELinux/AppArmor settings, and mount options.

Cleanup helpers:

```bash
# Stop and remove all containers (careful!)
docker stop $(docker ps -q)
docker rm $(docker ps -aq)

# Remove dangling images and unused data
docker image prune -f
docker system prune -a
```

---

## Advanced: Topics to Level Up

These practical additions are often used in real projects and pipelines.

### Networking modes and user-defined bridges

- Modes: `none`, `bridge` (default), `host` (Linux), `macvlan` (advanced/L2).
- Prefer user‑defined bridges for built‑in DNS and isolation:

```bash
# Create an isolated network and attach containers
docker network create app-net
docker run -d --name api --network app-net myorg/api:1.0
docker run -d --name web --network app-net -p 8080:80 myorg/web:1.0

# Containers resolve each other by name (api:port)
docker exec web getent hosts api
```

### Compose profiles (dev/prod variants)

Enable or disable services by profile without changing files:

```yaml
services:
  web:
    image: myorg/web:1.0
    profiles: ["dev"]
  redis:
    image: redis:7-alpine
    profiles: ["prod"]
```

```bash
# Start only dev services
docker compose --profile dev up -d

# Start only prod services
docker compose --profile prod up -d
```

### Rootless mode and user namespaces

- Reduce daemon attack surface by running Docker rootless where possible.
- Even without rootless, prefer non‑root USER in images (see Security section).

References: Docker docs on Rootless Mode and User Namespaces.

### Secrets management (don’t use env vars in prod)

- Avoid putting secrets in images or plain env vars.
- Use orchestrator secrets (Docker Swarm/Kubernetes) or external vaults.

Compose example (Swarm‑style secrets):

```yaml
services:
  app:
    image: myorg/app:1.0
    secrets:
      - db_password
secrets:
  db_password:
    file: ./secrets/db_password.txt
```

### CI: Image scanning in the pipeline

Integrate scanners to catch known CVEs before shipping:

```yaml
# GitHub Actions example (Trivy)
- name: Scan image with Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: myorg/app:1.0
    format: 'sarif'
    output: 'trivy-results.sarif'
```

### Buildx/BuildKit and multi‑arch builds

- Use Buildx for multi‑platform images and better caching.
- Example (GitHub Actions): setup Buildx and `docker/build-push-action`.
- Local buildx quick start:

```bash
docker buildx create --use --name mybuilder
docker buildx build --platform linux/amd64,linux/arm64 -t myorg/app:1.0 --push .
```

Tip: Consider BuildKit cache mounts to speed up dependency installs.

### Registries beyond Docker Hub

- Private/public registries: GHCR, ECR, GCR, ACR, JFrog Artifactory, self‑hosted registry.
- Authenticate and tag with the registry’s hostname (e.g., `ghcr.io/owner/image:tag`, `myregistry.jfrog.io/myrepo/image:tag`).

For JFrog Artifactory:
- Set up a Docker repository in Artifactory.
- Login: `docker login myregistry.jfrog.io` (use your Artifactory credentials or API key).
- Tag: `docker tag myimage:latest myregistry.jfrog.io/myrepo/myimage:v1.0`
- Push: `docker push myregistry.jfrog.io/myrepo/myimage:v1.0`
- Pull: `docker pull myregistry.jfrog.io/myrepo/myimage:v1.0`

JFrog provides advanced features like artifact management, security scanning, and integration with CI/CD pipelines.

## Best Practices – Do’s and Don’ts

Do:

- Use small, well‑maintained base images; pin versions (e.g., `python:3.12-slim`).
- Add a `.dockerignore` to reduce context size and improve cache hits.
- Combine related commands in single `RUN` steps to reduce layers.
- Switch to non‑root users; set correct ownership/permissions.
- Leverage multi‑stage builds to ship only runtime dependencies.
- Explicitly expose/listen on ports; make health checks part of your design.
- Tag images meaningfully (`1.4.2`, `2025-11-04`, `commit-sha`).

Don’t:

- Don’t bake secrets, SSH keys, or tokens into images or layers.
- Don’t `apt-get update` in one layer and install in another—do it in a single `RUN`:

  ```dockerfile
  RUN apt-get update && apt-get install -y --no-install-recommends curl \
      && rm -rf /var/lib/apt/lists/*
  ```
- Don’t run everything as root or grant unnecessary capabilities.
- Don’t copy the entire repo when only a subdir is needed (use `.dockerignore` and targeted `COPY`).
- Don’t rely on `latest` tags in production.

---

## Cheat Sheet

```bash
# Images
docker images
docker pull <image>:<tag>
docker build -t <name>:<tag> .
docker tag <src>:<tag> <repo>/<name>:<tag>
docker push <repo>/<name>:<tag>
docker image inspect <image>:<tag>
docker image history <image>:<tag>
docker image prune -f

# Containers
docker run --rm -d --name <n> -p 8080:80 <image>:<tag>
docker ps -a
docker logs -f <n>
docker exec -it <n> sh
docker stop <n> && docker rm <n>

# Volumes & Networks
docker volume ls && docker network ls

# Compose
docker compose up -d
docker compose logs -f
docker compose down

# Buildx (multi-arch)
docker buildx create --use --name mybuilder
docker buildx build --platform linux/amd64,linux/arm64 -t <repo>/<name>:tag --push .
```

---

## Glossary

- Image: Template for containers.
- Container: Running instance of an image.
- Layer: A file system delta; images are composed of layers.
- Registry: Storage for images.
- Volume: Persistent data managed by Docker.
- Bind mount: Maps a host path into a container path.
- Compose: Declarative tool for multi‑container apps.

---

## Next Steps

- Convert a small app you maintain into a container using a Dockerfile.
- Add Compose to wire it with a cache/DB.
- Harden the image (non‑root user, minimal base, multi‑stage).
- Set up CI to build, scan, and push tags on each commit.

# Detailed feature comparison

> **Module:** Comparison | **Level:** Intermediate | **Time:** 20 minutes

## Learning objectives

By the end of this section, you will be able to:

- Compare specific features in depth
- Understand performance differences
- Make informed technology choices

---

## Image building

### Dockerfile support

Both Docker and Podman fully support Dockerfiles:

```dockerfile
FROM alpine:3.19
RUN apk add --no-cache python3
COPY app.py /app/
CMD ["python3", "/app/app.py"]
```

```bash
# Docker
docker build -t myapp .

# Podman
podman build -t myapp .
```

### Buildah (Podman ecosystem)

Podman uses Buildah for building, which offers additional capabilities:

```bash
# Script-based build (no Dockerfile needed)
container=$(buildah from alpine:3.19)
buildah run $container apk add --no-cache python3
buildah copy $container app.py /app/
buildah config --cmd "python3 /app/app.py" $container
buildah commit $container myapp:latest
```

### Multi-stage builds

Both support multi-stage builds identically:

```dockerfile
FROM node:20 AS builder
WORKDIR /app
COPY . .
RUN npm ci && npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

---

## Security comparison

### Privilege model

| Aspect | Docker | Podman |
|--------|--------|--------|
| Daemon | Root by default | No daemon |
| Rootless | Optional, complex setup | Default |
| User namespaces | Optional | Default in rootless |
| Seccomp | Enabled | Enabled |
| SELinux | Supported | Native support |

### UID mapping (rootless)

```bash
# Podman rootless UID mapping
podman unshare cat /proc/self/uid_map
# 0 1000 1           # UID 0 in container = UID 1000 on host
# 1 100000 65536     # UIDs 1-65536 mapped to 100000-165536

# Check subuid/subgid
cat /etc/subuid
# username:100000:65536
```

### Security contexts

```bash
# Docker
docker run --security-opt label=disable nginx
docker run --security-opt seccomp=unconfined nginx

# Podman (same syntax)
podman run --security-opt label=disable nginx
podman run --security-opt seccomp=unconfined nginx
```

---

## Networking comparison

### Network modes

| Mode | Docker | Podman |
|------|--------|--------|
| Bridge | Default | Default (rootful) |
| Host | Supported | Supported |
| None | Supported | Supported |
| Container | Supported | Supported |
| Slirp4netns | N/A | Default (rootless) |

### Port binding (rootless)

```bash
# Docker rootless - needs special setup
docker run -p 80:80 nginx  # Fails without setup

# Podman rootless - works but limited
podman run -p 8080:80 nginx  # Works (port > 1024)
podman run -p 80:80 nginx    # Fails without net.ipv4.ip_unprivileged_port_start=0
```

### CNI vs netavark

```bash
# Podman network backends
# CNI (legacy)
podman network create --driver bridge mynet

# Netavark (modern, default in Podman 4+)
podman network create mynet

# Check backend
podman info --format '{{.Host.NetworkBackend}}'
```

---

## Storage comparison

### Storage drivers

| Driver | Docker | Podman |
|--------|--------|--------|
| overlay2 | Default | Supported |
| vfs | Supported | Default (rootless) |
| btrfs | Supported | Supported |
| zfs | Supported | Supported |
| fuse-overlayfs | N/A | Rootless option |

### Volume locations

```bash
# Docker volumes
/var/lib/docker/volumes/

# Podman rootful volumes
/var/lib/containers/storage/volumes/

# Podman rootless volumes
~/.local/share/containers/storage/volumes/
```

### Volume operations

```bash
# Both use identical syntax
docker volume create myvolume
podman volume create myvolume

docker run -v myvolume:/data nginx
podman run -v myvolume:/data nginx
```

---

## Performance comparison

### Startup time

| Metric | Docker | Podman |
|--------|--------|--------|
| Cold start | ~1-2s | ~0.5-1s |
| Warm start | ~0.5s | ~0.3s |
| Image pull | Similar | Similar |

*Note: Podman can be faster due to no daemon overhead*

### Resource overhead

```bash
# Docker daemon memory
ps aux | grep dockerd
# Typically 50-100MB

# Podman (no daemon)
# Only container processes
```

### Runtime comparison

| Runtime | Docker | Podman |
|---------|--------|--------|
| Default | runc | crun |
| Memory | Higher | Lower |
| Speed | Standard | Faster (crun) |

---

## Orchestration comparison

### Docker Swarm

```bash
# Docker only
docker swarm init
docker service create --replicas 3 nginx
docker stack deploy -c compose.yaml myapp
```

### Podman pods

```bash
# Podman pods (Kubernetes-like)
podman pod create --name mypod -p 8080:80
podman run -d --pod mypod nginx
podman run -d --pod mypod redis

# Generate Kubernetes YAML
podman generate kube mypod > mypod.yaml
```

### Kubernetes integration

```bash
# Podman: Native Kubernetes YAML support
podman play kube deployment.yaml
podman generate kube mycontainer

# Docker: Requires conversion
# No direct Kubernetes YAML support
```

---

## SystemD integration

### Docker with SystemD

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My App
After=docker.service
Requires=docker.service

[Service]
Restart=always
ExecStart=/usr/bin/docker start -a myapp
ExecStop=/usr/bin/docker stop myapp

[Install]
WantedBy=multi-user.target
```

### Podman SystemD generation

```bash
# Generate systemd unit file automatically
podman generate systemd --name mycontainer --files --new

# Generated file
cat container-mycontainer.service

# Install and enable
mv container-mycontainer.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now container-mycontainer
```

---

## Compatibility matrix

| Feature | Docker | Podman | Notes |
|---------|--------|--------|-------|
| Dockerfile | Full | Full | Identical |
| Compose v2 | Native | Via compatibility | Some features differ |
| Swarm | Yes | No | Docker exclusive |
| Kubernetes | Limited | Native | Podman advantage |
| Buildkit | Native | Via buildah | Different approach |
| Docker Hub | Native | Compatible | Both work |
| Rootless | Optional | Default | Podman advantage |
| Windows | Native | Limited | Docker advantage |
| macOS | Desktop | Desktop/Machine | Both supported |

---

## Decision matrix

### Choose Docker if

- [x] Need Docker Swarm
- [x] Windows containers
- [x] Maximum ecosystem compatibility
- [x] Team expertise in Docker
- [x] Using Docker Desktop features

### Choose Podman if

- [x] Security-first requirements
- [x] Kubernetes workflow
- [x] RHEL/Fedora environment
- [x] SystemD integration
- [x] Rootless by default
- [x] No daemon preference

### Either works for

- [x] Basic container operations
- [x] CI/CD pipelines
- [x] Development workflows
- [x] Image building
- [x] Compose workloads

---

## Key takeaways

1. **CLI commands are nearly identical**
2. **Podman is more secure by default** (rootless)
3. **Docker has Swarm** for orchestration
4. **Podman has better Kubernetes integration**
5. **Both are production-ready**

---

## What's next

Learn how to transition between Docker and Podman.

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [Docker vs Podman](01-docker-vs-podman.md) | [Course Overview](../course_overview.md) | [Migration Guide](03-migration-guide.md) |

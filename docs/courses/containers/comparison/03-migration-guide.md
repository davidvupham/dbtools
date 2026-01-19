# Migration guide: Docker to Podman

> **Module:** Comparison | **Level:** Intermediate | **Time:** 20 minutes

## Learning objectives

By the end of this section, you will be able to:

- Migrate containers from Docker to Podman
- Convert Docker Compose to work with Podman
- Handle common migration issues
- Set up interoperability

---

## Migration checklist

- [ ] Install Podman
- [ ] Migrate images
- [ ] Update volume permissions
- [ ] Test Compose files
- [ ] Update CI/CD pipelines
- [ ] Configure SystemD services
- [ ] Update documentation

---

## Installing Podman

### Fedora / RHEL / CentOS

```bash
sudo dnf install podman podman-compose
```

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install podman podman-compose
```

### macOS

```bash
brew install podman
podman machine init
podman machine start
```

### Windows

```powershell
# Install via winget
winget install RedHat.Podman

# Or download Podman Desktop
# https://podman-desktop.io/
```

---

## Image migration

### Export and import

```bash
# Export from Docker
docker save myimage:latest > myimage.tar

# Import to Podman
podman load < myimage.tar
```

### Direct transfer

```bash
# Using skopeo (recommended)
skopeo copy docker-daemon:myimage:latest containers-storage:myimage:latest
```

### From registry

```bash
# Images from registries work directly
podman pull docker.io/library/nginx:alpine
podman pull ghcr.io/myorg/myapp:latest
```

---

## Docker alias setup

### Simple alias

```bash
# Add to ~/.bashrc or ~/.zshrc
alias docker=podman
```

### Comprehensive setup

```bash
# ~/.bashrc or ~/.zshrc

# Alias docker to podman
alias docker=podman
alias docker-compose=podman-compose

# Or use function for more control
docker() {
    podman "$@"
}

export -f docker
```

---

## Compose migration

### Using podman-compose

```bash
# Install
pip install podman-compose

# Use like docker-compose
podman-compose up -d
podman-compose logs
podman-compose down
```

### Using Docker Compose with Podman socket

```bash
# Start Podman socket
systemctl --user enable --now podman.socket

# Set Docker host environment variable
export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/podman/podman.sock

# Use docker-compose normally
docker-compose up -d
```

### Common Compose adjustments

```yaml
# compose.yaml adjustments for Podman

# Original (may need changes)
services:
  web:
    build: .
    ports:
      - "80:80"  # May fail rootless
    volumes:
      - ./data:/data  # Check permissions

# Adjusted for Podman rootless
services:
  web:
    build: .
    ports:
      - "8080:80"  # Use port > 1024
    volumes:
      - ./data:/data:Z  # SELinux label
    userns_mode: keep-id  # Keep user namespace mapping
```

---

## Volume permission fixes

### SELinux labels

```bash
# Add :Z for private label (single container)
podman run -v ./data:/data:Z nginx

# Add :z for shared label (multiple containers)
podman run -v ./data:/data:z nginx
```

### User namespace mapping

```yaml
# In compose.yaml
services:
  app:
    image: myapp
    userns_mode: keep-id
    volumes:
      - ./data:/data
```

```bash
# Or with podman run
podman run --userns=keep-id -v ./data:/data myapp
```

### Fix existing volume ownership

```bash
# Get your UID mapping
podman unshare cat /proc/self/uid_map

# Fix ownership
podman unshare chown -R 1000:1000 ./data
```

---

## Networking adjustments

### Rootless port binding

```bash
# Allow binding to privileged ports (optional)
sudo sysctl net.ipv4.ip_unprivileged_port_start=80

# Or use port > 1024
podman run -p 8080:80 nginx
```

### Network creation

```bash
# Works identically
podman network create mynetwork
podman run --network mynetwork nginx
```

---

## CI/CD pipeline updates

### GitHub Actions

```yaml
# Before (Docker)
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t myapp .
      - run: docker push myapp

# After (Podman)
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Podman
        run: |
          sudo apt-get update
          sudo apt-get install -y podman
      - run: podman build -t myapp .
      - run: podman push myapp
```

### GitLab CI

```yaml
# .gitlab-ci.yml with Podman
build:
  image: quay.io/podman/stable
  script:
    - podman build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - podman login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - podman push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

---

## SystemD service migration

### Docker service

```ini
# Old Docker service
[Service]
ExecStart=/usr/bin/docker start -a mycontainer
ExecStop=/usr/bin/docker stop mycontainer
```

### Podman service

```bash
# Generate SystemD unit
podman generate systemd --name mycontainer --files --new

# Install for user
mkdir -p ~/.config/systemd/user
mv container-mycontainer.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now container-mycontainer

# Or install system-wide (root)
sudo mv container-mycontainer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now container-mycontainer
```

---

## Common migration issues

### Issue: "Permission denied"

```bash
# Cause: SELinux or user namespace
# Solution 1: Add SELinux label
podman run -v ./data:/data:Z myapp

# Solution 2: Adjust user namespace
podman run --userns=keep-id -v ./data:/data myapp
```

### Issue: "Port already in use"

```bash
# Cause: Rootless can't bind low ports
# Solution: Use higher port
podman run -p 8080:80 nginx
```

### Issue: "Image format not recognized"

```bash
# Cause: Docker-specific image format
# Solution: Re-export with OCI format
docker save myimage | podman load
```

### Issue: Compose features not working

```bash
# Some Docker Compose features may differ
# Check podman-compose compatibility
# Or use Podman socket with docker-compose
```

---

## Rollback plan

If migration fails, you can run both simultaneously:

```bash
# Docker (if installed)
docker run nginx

# Podman (different socket)
podman run nginx

# They use different storage
# /var/lib/docker vs /var/lib/containers
```

---

## Key takeaways

1. **Most commands work identically** with alias
2. **Volume permissions** need attention (SELinux, user namespaces)
3. **Rootless ports** require adjustment (> 1024)
4. **Compose** works via podman-compose or socket
5. **SystemD** integration is native and simpler

---

## What's next

Return to the main course content.

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [Detailed Comparison](02-detailed-comparison.md) | [Course Overview](../course_overview.md) | [DCA Overview](../certification/01-dca-overview.md) |

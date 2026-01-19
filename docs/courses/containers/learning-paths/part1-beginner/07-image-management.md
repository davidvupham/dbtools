# Image Management

> **Module:** Part 1 - Beginner | **Level:** Foundation | **Time:** 30 minutes

## Learning Objectives

By the end of this section, you will be able to:

- Tag images for different registries and versions
- Push images to container registries
- Pull images from various sources
- Manage local image storage
- Use image registries effectively

---

## Image Tagging

### Understanding Tags

Tags identify specific versions of an image:

```bash
# Full image reference
registry/namespace/repository:tag

# Examples
docker.io/library/nginx:1.25      # Official nginx
ghcr.io/myorg/myapp:v1.0.0        # GitHub Container Registry
myregistry.com/team/app:latest    # Private registry
```

### Creating Tags

```bash
# Tag during build
docker build -t myapp:v1.0 .

# Tag an existing image
docker tag myapp:v1.0 myapp:latest
docker tag myapp:v1.0 myregistry.com/myapp:v1.0

# Multiple tags
docker build -t myapp:v1.0 -t myapp:latest -t myapp:v1 .

# Tag for different registries
docker tag myapp:v1.0 docker.io/myuser/myapp:v1.0
docker tag myapp:v1.0 ghcr.io/myorg/myapp:v1.0
docker tag myapp:v1.0 gcr.io/myproject/myapp:v1.0
```

### Tagging Strategies

| Strategy | Example | Use Case |
|----------|---------|----------|
| **Semantic Version** | `v1.2.3` | Production releases |
| **Git SHA** | `abc1234` | CI/CD tracking |
| **Date-based** | `2024-01-15` | Daily builds |
| **Branch** | `main`, `develop` | Development |
| **Environment** | `prod`, `staging` | Deployment targeting |

**Best Practice - Multiple Tags:**
```bash
# Tag with all relevant identifiers
docker build \
    -t myapp:v1.2.3 \
    -t myapp:v1.2 \
    -t myapp:v1 \
    -t myapp:latest \
    -t myapp:$(git rev-parse --short HEAD) \
    .
```

---

## Container Registries

### Popular Registries

| Registry | URL | Notes |
|----------|-----|-------|
| **Docker Hub** | hub.docker.com | Default, free tier available |
| **GitHub Container Registry** | ghcr.io | Integrated with GitHub |
| **Google Artifact Registry** | gcr.io, *-docker.pkg.dev | GCP integration |
| **Amazon ECR** | *.dkr.ecr.*.amazonaws.com | AWS integration |
| **Azure Container Registry** | *.azurecr.io | Azure integration |
| **Quay.io** | quay.io | Red Hat, security scanning |
| **Harbor** | Self-hosted | Enterprise features |

### Registry Authentication

```bash
# Docker Hub
docker login
# Enter username and password

# Other registries
docker login ghcr.io
docker login gcr.io
docker login myregistry.azurecr.io

# Using access token (more secure)
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Check current logins
cat ~/.docker/config.json

# Logout
docker logout ghcr.io
```

---

## Pushing Images

### Basic Push

```bash
# 1. Tag for target registry
docker tag myapp:v1.0 docker.io/myuser/myapp:v1.0

# 2. Login to registry
docker login

# 3. Push the image
docker push docker.io/myuser/myapp:v1.0

# Push all tags for a repository
docker push --all-tags myuser/myapp
```

### Push to Different Registries

**Docker Hub:**
```bash
docker tag myapp:v1.0 myuser/myapp:v1.0
docker push myuser/myapp:v1.0
```

**GitHub Container Registry:**
```bash
# Login with personal access token
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag and push
docker tag myapp:v1.0 ghcr.io/myorg/myapp:v1.0
docker push ghcr.io/myorg/myapp:v1.0
```

**Google Cloud:**
```bash
# Configure Docker for GCP
gcloud auth configure-docker

# Tag and push
docker tag myapp:v1.0 gcr.io/myproject/myapp:v1.0
docker push gcr.io/myproject/myapp:v1.0
```

**Amazon ECR:**
```bash
# Get login command
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag myapp:v1.0 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:v1.0
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:v1.0
```

---

## Pulling Images

### Basic Pull

```bash
# Pull from Docker Hub (default)
docker pull nginx
docker pull nginx:1.25
docker pull library/nginx:1.25  # Explicit

# Pull from other registries
docker pull ghcr.io/owner/image:tag
docker pull gcr.io/project/image:tag

# Pull by digest (immutable)
docker pull nginx@sha256:abc123...

# Pull for specific platform
docker pull --platform linux/arm64 nginx
```

### Pull Behavior

```bash
# Already have image - does nothing
docker pull nginx:1.25
# 1.25: Pulling from library/nginx
# Digest: sha256:...
# Status: Image is up to date for nginx:1.25

# New layers needed
docker pull nginx:latest
# latest: Pulling from library/nginx
# a2abf6c4d29d: Already exists    # Shared layer
# a9edb18cadd1: Pull complete     # New layer
```

---

## Managing Local Images

### Listing Images

```bash
# List all images
docker images
docker image ls

# Filter by repository
docker images nginx

# Show digests
docker images --digests

# Show image IDs only
docker images -q

# Filter dangling (untagged)
docker images -f dangling=true

# Custom format
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Sort by size
docker images --format "{{.Size}}\t{{.Repository}}:{{.Tag}}" | sort -h
```

### Removing Images

```bash
# Remove by name:tag
docker rmi nginx:1.25
docker image rm nginx:1.25

# Remove by ID
docker rmi abc123

# Force remove (even if containers exist)
docker rmi -f nginx:1.25

# Remove dangling images (untagged)
docker image prune

# Remove all unused images
docker image prune -a

# Remove images matching filter
docker rmi $(docker images -q -f "dangling=true")

# Remove all images (careful!)
docker rmi $(docker images -q)
```

### Disk Space Management

```bash
# Show disk usage
docker system df

# Output:
TYPE            TOTAL   ACTIVE  SIZE      RECLAIMABLE
Images          15      5       5.2GB     3.1GB (60%)
Containers      8       3       150MB     50MB (33%)
Local Volumes   10      4       2.1GB     1.5GB (71%)
Build Cache     20      0       1.5GB     1.5GB (100%)

# Detailed breakdown
docker system df -v

# Clean up everything unused
docker system prune

# Including unused volumes (careful!)
docker system prune --volumes

# Remove all unused data aggressively
docker system prune -a --volumes
```

---

## Image Inspection

### Inspect Command

```bash
# Full JSON output
docker image inspect nginx

# Get specific fields
docker inspect --format '{{.Id}}' nginx
docker inspect --format '{{.Config.Env}}' nginx
docker inspect --format '{{.Config.ExposedPorts}}' nginx
docker inspect --format '{{.Config.Cmd}}' nginx
docker inspect --format '{{.Config.Entrypoint}}' nginx

# Get architecture
docker inspect --format '{{.Os}}/{{.Architecture}}' nginx

# Get labels
docker inspect --format '{{json .Config.Labels}}' nginx | jq
```

### View History

```bash
# Show build history
docker history nginx

# With full commands
docker history --no-trunc nginx

# Format as table
docker history --format "table {{.CreatedBy}}\t{{.Size}}" nginx
```

---

## Working with Image Archives

### Save and Load

For offline transfer or backup:

```bash
# Save image to tar file
docker save nginx:1.25 -o nginx.tar
docker save nginx:1.25 > nginx.tar

# Save multiple images
docker save nginx:1.25 redis:7 -o images.tar

# Load image from tar
docker load -i nginx.tar
docker load < nginx.tar
```

### Export and Import

Export a container filesystem (not image layers):

```bash
# Export container filesystem
docker export mycontainer > container-fs.tar

# Import as new image
docker import container-fs.tar newimage:v1
```

**Difference:**
| Operation | Preserves Layers | Preserves Metadata | Use Case |
|-----------|-----------------|-------------------|----------|
| `save/load` | Yes | Yes | Image transfer |
| `export/import` | No | No | Filesystem extraction |

---

## Image Security

### Scanning Images

```bash
# Docker Scout (Docker Desktop)
docker scout cves nginx:1.25

# Trivy (open source)
trivy image nginx:1.25

# Grype (open source)
grype nginx:1.25
```

### Verifying Images

```bash
# Check image digest
docker images --digests nginx

# Pull by digest (guaranteed same content)
docker pull nginx@sha256:abc123...

# Docker Content Trust (image signing)
export DOCKER_CONTENT_TRUST=1
docker pull nginx  # Only pulls signed images
```

---

## Podman-Specific Features

### Podman Registry Configuration

```bash
# Configure registries
# /etc/containers/registries.conf (rootful)
# ~/.config/containers/registries.conf (rootless)

# Search order
unqualified-search-registries = ["docker.io", "quay.io"]

# Short name aliases
[aliases]
"python" = "docker.io/library/python"
```

### Podman Image Commands

```bash
# Same commands work
podman images
podman pull nginx
podman push myimage
podman rmi nginx

# Podman-specific: mount image for inspection
podman image mount nginx
ls /var/lib/containers/storage/overlay/...
podman image unmount nginx

# Sign images
podman push --sign-by mykey@example.com myimage
```

---

## Best Practices

### 1. Use Specific Tags in Production

```bash
# Bad
FROM nginx:latest
docker pull nginx

# Good
FROM nginx:1.25.3
docker pull nginx:1.25.3

# Best (immutable)
FROM nginx@sha256:abc123...
```

### 2. Clean Up Regularly

```bash
# Add to cron or CI/CD
docker system prune -f
docker image prune -a --filter "until=168h"  # Remove images older than 7 days
```

### 3. Use .dockerignore

```gitignore
.git
node_modules
*.log
.env
```

### 4. Scan Before Pushing

```bash
# In CI/CD pipeline
trivy image --exit-code 1 --severity HIGH,CRITICAL myimage:v1
docker push myimage:v1
```

---

## Key Takeaways

1. **Tags identify image versions** - use semantic versioning in production
2. **Always authenticate** before pushing to registries
3. **Use specific tags or digests** for reproducibility
4. **Clean up regularly** to manage disk space
5. **Scan images for vulnerabilities** before deploying
6. **Use save/load for image transfer**, export/import for filesystems

---

## What's Next

Now that you can manage images, let's learn about persisting data with volumes.

Continue to: [08-basic-volumes.md](08-basic-volumes.md)

---

## Quick Quiz

1. What command creates a new tag for an existing image?
   - [ ] `docker retag`
   - [ ] `docker rename`
   - [x] `docker tag`
   - [ ] `docker label`

2. What must you do before pushing to a registry?
   - [ ] Build the image locally
   - [ ] Create an account on the registry
   - [x] Authenticate with `docker login`
   - [ ] All of the above

3. What's the difference between `docker save` and `docker export`?
   - [ ] They are identical
   - [x] `save` preserves layers and metadata, `export` extracts filesystem only
   - [ ] `export` is for images, `save` is for containers
   - [ ] `save` is deprecated

4. Which reference to an image is immutable?
   - [ ] `nginx:latest`
   - [ ] `nginx:1.25`
   - [x] `nginx@sha256:abc123...`
   - [ ] `nginx:stable`

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [Building Images](06-building-images.md) | [Part 1 Overview](../../course_overview.md#part-1-beginner) | [Basic Volumes](08-basic-volumes.md) |

# Chapter 16: CI/CD for Containers

Automate building, testing, scanning, and deploying Docker images in your CI/CD pipeline.

## The CI/CD Pipeline for Containers

```
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  Code   │ → │  Build  │ → │  Test   │ → │  Scan   │ → │  Push   │ → Deploy
│ Commit  │   │  Image  │   │ in Ctnr │   │  CVEs   │   │Registry │
└─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
```

---

## Building Images in CI

### GitHub Actions Example

```yaml
# .github/workflows/docker.yml
name: Build and Push

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            myorg/myapp:${{ github.sha }}
            myorg/myapp:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Key Features

- **Buildx**: Modern builder with caching and multi-platform support
- **`cache-from/cache-to`**: Use GitHub Actions cache for faster builds
- **Tag with SHA**: Unique identifier for each build

---

## Multi-Platform Builds

Build images that work on both AMD64 (Intel/AMD) and ARM64 (Apple Silicon, AWS Graviton).

```yaml
- name: Build and push (multi-arch)
  uses: docker/build-push-action@v5
  with:
    context: .
    platforms: linux/amd64,linux/arm64
    push: true
    tags: myorg/myapp:latest
```

### CLI Example

```bash
# Create a builder
docker buildx create --name multiarch --use

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t myorg/myapp:latest \
  --push .
```

---

## Running Tests in Containers

### In GitHub Actions

```yaml
- name: Run tests
  run: |
    docker compose -f docker-compose.test.yml up --abort-on-container-exit
    docker compose -f docker-compose.test.yml down
```

### Test Compose File

```yaml
# docker-compose.test.yml
services:
  test:
    build: .
    command: npm test
    environment:
      - NODE_ENV=test
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: test
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 5s
      retries: 5
```

---

## Image Scanning in CI

Scan for vulnerabilities before pushing to production.

### With Trivy

```yaml
- name: Scan image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: myorg/myapp:${{ github.sha }}
    exit-code: '1'           # Fail pipeline on vulnerabilities
    severity: 'CRITICAL,HIGH'
    format: 'sarif'
    output: 'trivy-results.sarif'

- name: Upload scan results
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: 'trivy-results.sarif'
```

### With Docker Scout

```yaml
- name: Analyze with Docker Scout
  uses: docker/scout-action@v1
  with:
    command: cves
    image: myorg/myapp:${{ github.sha }}
    only-severities: critical,high
    exit-code: true
```

---

## Caching Strategies

### Layer Caching with Registry

```yaml
- name: Build with cache
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: myorg/myapp:latest
    cache-from: type=registry,ref=myorg/myapp:buildcache
    cache-to: type=registry,ref=myorg/myapp:buildcache,mode=max
```

### GitHub Actions Cache

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

---

## Tagging Strategies

```yaml
- name: Generate tags
  id: meta
  uses: docker/metadata-action@v5
  with:
    images: myorg/myapp
    tags: |
      type=sha,prefix=
      type=ref,event=branch
      type=semver,pattern={{version}}
      type=semver,pattern={{major}}.{{minor}}

# Produces tags like:
# myorg/myapp:abc1234
# myorg/myapp:main
# myorg/myapp:1.2.3
# myorg/myapp:1.2
```

---

## Complete Pipeline Example

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build image
        uses: docker/build-push-action@v5
        with:
          context: .
          load: true
          tags: myapp:test
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Run tests
        run: docker run --rm myapp:test npm test

      - name: Scan for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp:test
          exit-code: '1'
          severity: 'CRITICAL,HIGH'

      - name: Login to registry
        if: github.ref == 'refs/heads/main'
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Push to registry
        if: github.ref == 'refs/heads/main'
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: myorg/myapp:${{ github.sha }},myorg/myapp:latest
```

---

## Summary

| Stage | Tools |
| :--- | :--- |
| Build | `docker buildx`, `docker/build-push-action` |
| Test | `docker compose run`, container-based tests |
| Scan | Trivy, Docker Scout, Snyk |
| Push | Docker Hub, GHCR, ECR, Artifactory |
| Cache | Registry cache, GitHub Actions cache |

**Next Chapter:** Debug common issues in **Chapter 18: Troubleshooting & Debugging**.

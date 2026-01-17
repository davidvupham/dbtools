# Image optimization

> **Module:** Part 2 - Intermediate | **Level:** Intermediate | **Time:** 30 minutes

## Learning objectives

By the end of this section, you will be able to:

- Reduce image size significantly
- Optimize build times with caching
- Create secure, minimal images
- Analyze and debug image layers

---

## Why optimize images?

| Benefit | Impact |
|---------|--------|
| Faster pulls | Reduced deployment time |
| Less storage | Lower registry costs |
| Faster builds | Improved developer productivity |
| Smaller attack surface | Better security |
| Lower bandwidth | Reduced network costs |

---

## Base image selection

### Alpine vs Debian vs distroless

```dockerfile
# Debian (large, full featured)
FROM node:20           # ~1GB

# Alpine (small, musl libc)
FROM node:20-alpine    # ~180MB

# Slim (smaller Debian)
FROM node:20-slim      # ~240MB

# Distroless (minimal, no shell)
FROM gcr.io/distroless/nodejs20  # ~130MB
```

### Size comparison

```bash
# Check image sizes
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

REPOSITORY     TAG          SIZE
node           20           1.1GB
node           20-slim      243MB
node           20-alpine    181MB
```

### Choosing the right base

| Use Case | Recommended Base |
|----------|-----------------|
| Development | Full image (debian) |
| Production | Alpine or slim |
| Security-critical | Distroless |
| Compiled languages | Scratch or distroless |
| Debugging needed | Alpine with shell |

---

## Multi-stage builds

### Basic pattern

```dockerfile
# Stage 1: Build
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:20-alpine AS production
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER node
CMD ["node", "dist/index.js"]
```

### Go application (scratch base)

```dockerfile
# Build stage
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /app/server

# Production stage (from scratch)
FROM scratch
COPY --from=builder /app/server /server
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
USER 1000:1000
ENTRYPOINT ["/server"]
```

### Python application

```dockerfile
# Build stage
FROM python:3.11-slim AS builder
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY . .
USER 1000:1000
CMD ["python", "app.py"]
```

---

## Layer optimization

### Combine RUN instructions

```dockerfile
# Bad: Multiple layers
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git
RUN rm -rf /var/lib/apt/lists/*

# Good: Single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        git && \
    rm -rf /var/lib/apt/lists/*
```

### Order by change frequency

```dockerfile
# Least frequently changed first
FROM node:20-alpine

# System dependencies (rarely change)
RUN apk add --no-cache dumb-init

# Application dependencies (change occasionally)
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Application code (changes frequently)
COPY . .

CMD ["dumb-init", "node", "index.js"]
```

### Use .dockerignore

```bash
# .dockerignore
node_modules
npm-debug.log
.git
.gitignore
*.md
!README.md
.env*
.vscode
coverage
tests
__pycache__
*.pyc
.pytest_cache
```

---

## Build cache optimization

### Package manager caching

```dockerfile
# npm with cache mount
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production
COPY . .
```

```dockerfile
# pip with cache mount
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
COPY . .
```

### BuildKit cache

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Or in daemon.json
{
  "features": {
    "buildkit": true
  }
}
```

### Cache from registry

```bash
# Build with cache from registry
docker build \
    --cache-from myregistry/myapp:latest \
    --tag myregistry/myapp:v1.0.0 \
    --push .
```

---

## Reducing image size

### Remove build dependencies

```dockerfile
FROM python:3.11-slim

# Install build deps, compile, remove deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev && \
    pip install --no-cache-dir psycopg2 && \
    apt-get remove -y build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*
```

### Use --no-install-recommends

```dockerfile
# Debian/Ubuntu
RUN apt-get install -y --no-install-recommends package

# Alpine
RUN apk add --no-cache package
```

### Strip binaries

```dockerfile
# Go: use ldflags
RUN go build -ldflags="-s -w" -o app

# C/C++: strip after compile
RUN strip --strip-all /app/binary
```

### Compress with UPX

```dockerfile
FROM golang:1.21-alpine AS builder
RUN apk add --no-cache upx
WORKDIR /app
COPY . .
RUN go build -ldflags="-s -w" -o app && \
    upx --best --lzma app

FROM scratch
COPY --from=builder /app/app /app
```

---

## Security hardening

### Non-root user

```dockerfile
FROM node:20-alpine

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

WORKDIR /app
COPY --chown=appuser:appgroup . .

USER appuser
CMD ["node", "index.js"]
```

### Read-only filesystem

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY . .

# Mark as read-only compatible
USER node
CMD ["node", "index.js"]
```

```yaml
# compose.yaml
services:
  api:
    image: myapi
    read_only: true
    tmpfs:
      - /tmp
```

### Remove unnecessary tools

```dockerfile
FROM node:20-alpine

# Remove shell access for security
RUN rm -rf /bin/sh /bin/ash /bin/bash 2>/dev/null || true
```

---

## Analyzing images

### Docker history

```bash
# View layers and sizes
docker history myapp:latest

# Detailed view
docker history --no-trunc myapp:latest
```

### Dive tool

```bash
# Install dive
brew install dive  # macOS
apt install dive   # Ubuntu

# Analyze image
dive myapp:latest
```

### Inspect image

```bash
# View image details
docker inspect myapp:latest

# View specific fields
docker inspect --format '{{.Size}}' myapp:latest
docker inspect --format '{{json .Config.Env}}' myapp:latest | jq
```

### Compare images

```bash
# Compare sizes
docker images myapp --format "table {{.Tag}}\t{{.Size}}"

TAG      SIZE
v1.0.0   245MB
v1.1.0   180MB
```

---

## Practical example: Optimized Node.js

```dockerfile
# syntax=docker/dockerfile:1

###################
# Build stage
###################
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Build application
COPY . .
RUN npm run build

# Prune dev dependencies
RUN npm prune --production

###################
# Production stage
###################
FROM node:20-alpine AS production

# Add dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -u 1001 -S nodejs -G nodejs

WORKDIR /app

# Copy only production artifacts
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/package.json ./

# Security: run as non-root
USER nodejs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# Use dumb-init as entrypoint
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/index.js"]
```

### Size comparison

| Approach | Size |
|----------|------|
| Naive (node:20) | ~1.2GB |
| Alpine base | ~250MB |
| Multi-stage | ~180MB |
| Production deps only | ~150MB |
| With optimizations | ~120MB |

---

## Key takeaways

1. **Use Alpine or slim** base images when possible
2. **Multi-stage builds** separate build and runtime
3. **Order Dockerfile** instructions by change frequency
4. **Use .dockerignore** to exclude unnecessary files
5. **Run as non-root** user for security
6. **Analyze images** with dive or docker history

---

## What's next

Learn about health checks and container orchestration readiness.

Continue to: [09-health-checks.md](09-health-checks.md)

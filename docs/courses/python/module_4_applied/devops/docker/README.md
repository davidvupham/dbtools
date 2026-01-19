# Docker for Python Applications

Containerize Python applications with Docker for consistent, reproducible deployments.

---

## Overview

Docker packages applications with their dependencies into containers that run consistently across environments. For Python, this solves:

- **Dependency isolation**: No more "works on my machine" issues
- **Reproducible builds**: Same image runs in dev, staging, and production
- **Easy deployment**: Ship containers instead of configuring servers
- **Microservices**: Run multiple Python services independently

### Prerequisites

- Docker Desktop or Docker Engine installed
- Basic Python project with `pyproject.toml` or `requirements.txt`
- Familiarity with command-line operations

---

## Quick Start

### Minimal Python Dockerfile

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run the application
CMD ["python", "main.py"]
```

```bash
# Build the image
docker build -t my-python-app .

# Run the container
docker run --rm my-python-app
```

### With UV Package Manager

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install dependencies first (layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application
COPY . .

# Run with uv
CMD ["uv", "run", "python", "main.py"]
```

---

## Base Images

### Choosing the Right Base

| Image | Size | Use Case |
|-------|------|----------|
| `python:3.12` | ~1GB | Full toolchain, building C extensions |
| `python:3.12-slim` | ~150MB | Most applications (recommended) |
| `python:3.12-alpine` | ~50MB | Size-critical, but has compatibility issues |
| `python:3.12-bookworm` | ~1GB | Debian stable, full toolchain |

```dockerfile
# Recommended for most use cases
FROM python:3.12-slim

# For applications with C extensions
FROM python:3.12-slim-bookworm

# Only if you need minimal size AND have tested thoroughly
FROM python:3.12-alpine
```

### Alpine Caveats

Alpine uses musl libc instead of glibc, causing issues with:
- NumPy, pandas, and scientific libraries
- psycopg2 (use psycopg2-binary or build from source)
- Some cryptography packages

```dockerfile
# Alpine with build dependencies (slower builds)
FROM python:3.12-alpine
RUN apk add --no-cache gcc musl-dev libffi-dev
```

---

## Multi-Stage Builds

Reduce image size by separating build and runtime stages.

### Basic Multi-Stage

```dockerfile
# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Copy wheels from builder
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

COPY . .

CMD ["python", "main.py"]
```

### Multi-Stage with UV

```dockerfile
# Build stage
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Ensure venv is on PATH
ENV PATH="/app/.venv/bin:$PATH"

COPY . .

CMD ["python", "main.py"]
```

---

## Layer Caching

Docker caches each layer. Order instructions from least to most frequently changing.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 1. System dependencies (rarely change)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Python dependencies (change occasionally)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Application code (changes frequently)
COPY . .

CMD ["python", "main.py"]
```

### .dockerignore

Prevent unnecessary files from entering the build context:

```dockerignore
# .dockerignore
__pycache__/
*.pyc
*.pyo
*.egg-info/
.git/
.gitignore
.venv/
venv/
.env
.env.*
*.md
!README.md
tests/
.pytest_cache/
.mypy_cache/
.ruff_cache/
Dockerfile
docker-compose*.yml
```

---

## Security Best Practices

### Non-Root User

Never run containers as root in production:

```dockerfile
FROM python:3.12-slim

# Create non-root user
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid 1000 --shell /bin/bash appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

CMD ["python", "main.py"]
```

### Pin Image Versions

```dockerfile
# Bad: tag can change
FROM python:3.12-slim

# Better: specific version
FROM python:3.12.3-slim

# Best: digest (immutable)
FROM python:3.12-slim@sha256:abc123...
```

### Scan for Vulnerabilities

```bash
# Scan image with Docker Scout
docker scout cve my-python-app

# Scan with Trivy
trivy image my-python-app
```

---

## Docker Compose

### Development Setup

```yaml
# docker-compose.yml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
      - /app/.venv  # Don't mount venv
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev
      POSTGRES_DB: myapp
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  pgdata:
```

### Development Dockerfile

```dockerfile
# Dockerfile.dev
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install all dependencies including dev
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .

# Use uvicorn with reload for development
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]
```

### Production Setup

```yaml
# docker-compose.prod.yml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://user:pass@db/myapp
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
      POSTGRES_DB: myapp
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d myapp"]
      interval: 10s
      timeout: 5s
      retries: 5
    secrets:
      - db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt

volumes:
  pgdata:
```

---

## Common Patterns

### FastAPI Application

```dockerfile
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN groupadd --gid 1000 app && useradd --uid 1000 --gid 1000 app

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY --chown=app:app . .

USER app

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Flask Application

```dockerfile
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

ENV FLASK_APP=app.py

EXPOSE 5000

CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### CLI Tool

```dockerfile
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

ENTRYPOINT ["uv", "run", "python", "-m", "mytool"]
CMD ["--help"]
```

Usage:

```bash
docker run --rm my-cli-tool process --input data.csv
docker run --rm -v $(pwd):/data my-cli-tool process --input /data/file.csv
```

### Scheduled Job (Cron)

```dockerfile
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

# For one-off runs
CMD ["uv", "run", "python", "job.py"]
```

Use with Kubernetes CronJob or external scheduler:

```yaml
# kubernetes cronjob
apiVersion: batch/v1
kind: CronJob
metadata:
  name: my-python-job
spec:
  schedule: "0 * * * *"  # Every hour
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: job
              image: my-python-job:latest
          restartPolicy: OnFailure
```

---

## Environment Variables

### Build-Time Variables

```dockerfile
ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim

ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}
```

```bash
docker build --build-arg PYTHON_VERSION=3.11 --build-arg APP_VERSION=1.0.0 -t myapp .
```

### Runtime Variables

```dockerfile
FROM python:3.12-slim

# Set defaults (can be overridden at runtime)
ENV LOG_LEVEL=INFO
ENV DATABASE_URL=""

CMD ["python", "main.py"]
```

```bash
docker run -e LOG_LEVEL=DEBUG -e DATABASE_URL=postgresql://... myapp
```

### Secrets (Never in Dockerfile)

```bash
# Use environment variables at runtime
docker run -e API_KEY=$API_KEY myapp

# Or mount secrets
docker run -v ./secrets:/run/secrets:ro myapp

# Or use Docker secrets (Swarm/Compose)
docker secret create api_key ./api_key.txt
```

---

## Health Checks

```dockerfile
FROM python:3.12-slim

# Install curl for health check
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Python health endpoint:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

---

## Debugging Containers

### Interactive Shell

```bash
# Run with shell
docker run -it --rm my-python-app /bin/bash

# Exec into running container
docker exec -it <container_id> /bin/bash
```

### Inspect Layers

```bash
# View image history
docker history my-python-app

# Inspect image metadata
docker inspect my-python-app
```

### Build Debugging

```bash
# Build with progress output
docker build --progress=plain -t my-python-app .

# Build specific stage
docker build --target builder -t my-python-app:builder .

# No cache (rebuild everything)
docker build --no-cache -t my-python-app .
```

---

## Quick Reference

### Essential Commands

```bash
# Build
docker build -t myapp .
docker build -t myapp:1.0.0 .
docker build -f Dockerfile.dev -t myapp:dev .

# Run
docker run --rm myapp
docker run -d -p 8000:8000 myapp
docker run -it --rm myapp /bin/bash
docker run -v $(pwd):/app myapp

# Manage
docker ps                    # List running containers
docker logs <container>      # View logs
docker stop <container>      # Stop container
docker rm <container>        # Remove container
docker rmi <image>           # Remove image

# Compose
docker compose up -d         # Start services
docker compose down          # Stop services
docker compose logs -f       # Follow logs
docker compose exec app bash # Shell into service
```

### Dockerfile Cheat Sheet

```dockerfile
# Instructions
FROM         # Base image
WORKDIR      # Set working directory
COPY         # Copy files into image
RUN          # Execute command during build
ENV          # Set environment variable
ARG          # Build-time variable
EXPOSE       # Document exposed port
USER         # Set runtime user
HEALTHCHECK  # Container health check
ENTRYPOINT   # Container executable
CMD          # Default arguments

# Copy patterns
COPY . .                    # Copy everything
COPY src/ ./src/            # Copy directory
COPY *.py ./                # Copy matching files
COPY --from=builder /app .  # Copy from stage
COPY --chown=user:group . . # Copy with ownership
```

---

## See Also

- [Docker Official Python Guide](https://docs.docker.com/language/python/)
- [UV Docker Documentation](https://docs.astral.sh/uv/guides/integration/docker/)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Python Docker Images](https://hub.docker.com/_/python)
- [Container Security with Trivy](https://trivy.dev/)

---

[← Back to Module 4](../../README.md) | [SQL Basics →](../sql_basics/README.md)

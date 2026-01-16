# How to Use UV with Docker

**🔗 [← Back to UV How-to Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 13, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Containers-blue)

> [!IMPORTANT]
> **Related Docs:** [CI/CD Integration](./uv-ci-cd-integration.md) | [Workspaces](./uv-workspaces.md)

This guide covers best practices for using UV in Docker containers for both development and production.

## Table of contents

- [Quick Start](#quick-start)
  - [Minimal Production Dockerfile](#minimal-production-dockerfile)
- [Understanding UV Docker Images](#understanding-uv-docker-images)
  - [Available Base Images](#available-base-images)
  - [Choosing the Right Image](#choosing-the-right-image)
- [Production Best Practices](#production-best-practices)
  - [Multi-Stage Build (Recommended)](#multi-stage-build-recommended)
  - [Key Optimizations Explained](#key-optimizations-explained)
  - [Why Use `python` Directly (Not `uv run`) in Production](#why-use-python-directly-not-uv-run-in-production)
- [Development Dockerfile](#development-dockerfile)
  - [Docker Compose for Development](#docker-compose-for-development)
  - [Docker Compose Watch (Auto-rebuild)](#docker-compose-watch-auto-rebuild)
- [Caching Strategies](#caching-strategies)
  - [Using BuildKit Cache Mounts](#using-buildkit-cache-mounts)
  - [GitHub Actions with Docker Caching](#github-actions-with-docker-caching)
- [Running Commands in Docker](#running-commands-in-docker)
  - [Using UV Run](#using-uv-run)
  - [Direct Python (After uv sync)](#direct-python-after-uv-sync)
- [Environment Variables](#environment-variables)
- [Common Patterns](#common-patterns)
  - [FastAPI Application](#fastapi-application)
  - [Flask with Gunicorn](#flask-with-gunicorn)
  - [Django Application](#django-application)
- [Deploying Workspace Packages](#deploying-workspace-packages)
  - [Option 1: Install All Workspace Members](#option-1-install-all-workspace-members)
  - [How UV Finds Workspace Packages](#how-uv-finds-workspace-packages)
  - [Option 2: Build and Install Specific Wheels](#option-2-build-and-install-specific-wheels)
  - [Where Are Packages Installed?](#where-are-packages-installed)
- [Troubleshooting](#troubleshooting)
  - ["Lock file not found"](#lock-file-not-found)
  - ["Failed to hardlink"](#failed-to-hardlink)
  - [Slow builds](#slow-builds)
  - [Permission errors](#permission-errors)
- [Related Guides](#related-guides)

## Quick Start

### Minimal Production Dockerfile

```dockerfile
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Run application
CMD ["uv", "run", "python", "main.py"]
```

---

## Understanding UV Docker Images

### Available Base Images

UV provides official Docker images at `ghcr.io/astral-sh/uv`:

| Image | Use Case |
|-------|----------|
| `ghcr.io/astral-sh/uv:latest` | Just the UV binary (for COPY --from) |
| `ghcr.io/astral-sh/uv:python3.12` | UV + Python 3.12 |
| `ghcr.io/astral-sh/uv:python3.12-bookworm` | UV + Python 3.12 on Debian Bookworm |
| `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` | Smaller image, Debian slim |
| `ghcr.io/astral-sh/uv:python3.12-alpine` | Smallest, Alpine-based |

### Choosing the Right Image

```dockerfile
# Option 1: Install UV into any Python image
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Option 2: Use UV's Python image directly
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
```

---

## Production Best Practices

### Multi-Stage Build (Recommended)

This creates the smallest, most secure production image:

```dockerfile
# ============================================
# Stage 1: Builder
# ============================================
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Compile bytecode for faster startup
ENV UV_COMPILE_BYTECODE=1

# Copy mode instead of hardlinks (needed for multi-stage)
ENV UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies first (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Install the project itself
COPY . .
RUN uv sync --frozen --no-dev

# ============================================
# Stage 2: Runtime (Production)
# ============================================
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy the virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Put venv on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY --from=builder /app .

# Run as non-root user (security best practice)
RUN useradd --create-home appuser
USER appuser

# Run the application
CMD ["python", "main.py"]
```

### Key Optimizations Explained

| Technique | Purpose |
|-----------|---------|
| `UV_COMPILE_BYTECODE=1` | Pre-compile .pyc files for faster startup |
| `UV_LINK_MODE=copy` | Required for multi-stage builds |
| `--frozen` | Fail if lock file is outdated |
| `--no-install-project` | Install deps first for better layer caching |
| `--no-dev` | Exclude development dependencies |
| Separate COPY for deps | Maximize Docker layer cache hits |

### Why Use `python` Directly (Not `uv run`) in Production

Notice the production image runs `python main.py` directly, not `uv run python main.py`:

```dockerfile
# Production: run Python directly
CMD ["python", "main.py"]

# NOT this:
# CMD ["uv", "run", "python", "main.py"]
```

**Reasons:**

| Concern | Why avoid `uv run` in production |
|---------|----------------------------------|
| **Startup time** | `uv run` checks if sync is needed on every invocation |
| **Determinism** | Production environment should be frozen at build time |
| **Image size** | Production image doesn't need UV binary at all |
| **Security** | Fewer binaries = smaller attack surface |

> [!TIP]
> The pattern is: use **UV at build time** to install everything (`uv sync`), then use **Python directly at runtime** (`python app.py`). This is the same pattern used with pip—you don't run `pip install` at container startup.

---

## Development Dockerfile

For development, you want hot-reloading and dev tools:

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Install dependencies including dev
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Copy application (will be overridden by volume mount)
COPY . .

# Install the project in editable mode
RUN uv sync --frozen

# Development server with hot reload
CMD ["uv", "run", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0"]
```

### Docker Compose for Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      # Mount source code for hot reloading
      - .:/app
      # Preserve .venv across restarts
      - app-venv:/app/.venv
    ports:
      - "8000:8000"
    environment:
      - UV_CACHE_DIR=/app/.uv-cache

volumes:
  app-venv:
```

### Docker Compose Watch (Auto-rebuild)

```yaml
# docker-compose.yml
services:
  app:
    build: .
    develop:
      watch:
        # Rebuild on dependency changes
        - action: rebuild
          path: pyproject.toml
        - action: rebuild
          path: uv.lock
        # Sync code changes (no rebuild)
        - action: sync
          path: ./src
          target: /app/src
```

Run with: `docker compose watch`

---

## Caching Strategies

### Using BuildKit Cache Mounts

For faster CI builds, use Docker's cache mounts:

```dockerfile
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Cache UV downloads between builds
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen
```

### GitHub Actions with Docker Caching

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-buildx-action@v3

      - uses: docker/build-push-action@v5
        with:
          context: .
          cache-from: type=gha
          cache-to: type=gha,mode=max
          push: true
          tags: my-app:latest
```

---

## Running Commands in Docker

### Using UV Run

```dockerfile
# Prefer uv run for consistency
CMD ["uv", "run", "python", "main.py"]
CMD ["uv", "run", "gunicorn", "app:app"]
CMD ["uv", "run", "celery", "-A", "tasks", "worker"]
```

### Direct Python (After uv sync)

If you've already synced and the venv is on PATH:

```dockerfile
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "main.py"]
CMD ["gunicorn", "app:app"]
```

---

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `UV_CACHE_DIR` | Custom cache location | `/tmp/uv-cache` |
| `UV_COMPILE_BYTECODE` | Pre-compile Python files | `1` |
| `UV_LINK_MODE` | How to link packages | `copy` |
| `UV_NO_CACHE` | Disable caching | `1` |
| `UV_FROZEN` | Always use --frozen | `1` |

---

## Common Patterns

### FastAPI Application

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev
COPY . .
RUN uv sync --frozen --no-dev

FROM python:3.12-slim-bookworm
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app .
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Flask with Gunicorn

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev
COPY . .
RUN uv sync --frozen --no-dev

FROM python:3.12-slim-bookworm
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app .
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:create_app()"]
```

### Django Application

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev
COPY . .
RUN uv sync --frozen --no-dev

FROM python:3.12-slim-bookworm
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app .
ENV PATH="/app/.venv/bin:$PATH"
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]
```

---

## Deploying Workspace Packages

When deploying a UV workspace (multiple related packages) to Docker:

### Option 1: Install All Workspace Members

Copy all workspace members and let UV install them:

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app

# Copy workspace root and all packages
COPY pyproject.toml uv.lock ./
COPY python/gds_database/ python/gds_database/
COPY python/gds_mssql/ python/gds_mssql/
COPY python/gds_postgres/ python/gds_postgres/
# ... other workspace members

RUN uv sync --frozen --no-dev

FROM python:3.12-slim-bookworm
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app
COPY --from=builder /app .
CMD ["python", "app.py"]
```

### How UV Finds Workspace Packages

UV reads the root `pyproject.toml` to discover workspace members:

```toml
# pyproject.toml
[tool.uv.workspace]
members = ["python/gds_*"]   # Pattern tells UV where to look
```

This means UV looks for any directory matching `python/gds_*` that contains a `pyproject.toml`:

```
/app/                           ← WORKDIR in Docker
├── pyproject.toml              ← Root config with [tool.uv.workspace]
├── uv.lock                     ← Lock file
├── python/
│   ├── gds_database/           ← Matches "python/gds_*" pattern
│   │   ├── pyproject.toml      ← UV finds this → installs as package
│   │   └── src/gds_database/
│   ├── gds_mssql/
│   │   ├── pyproject.toml
│   │   └── src/gds_mssql/
│   └── gds_postgres/
│       ├── pyproject.toml
│       └── src/gds_postgres/
```

> [!IMPORTANT]
> The `python/gds_*` directories must be copied to the **same relative paths** as defined in your workspace config. If the root config says `members = ["python/gds_*"]`, then UV expects `/app/python/gds_database/pyproject.toml`, `/app/python/gds_mssql/pyproject.toml`, etc.

### Option 2: Build and Install Specific Wheels

For more control, build only the packages you need:

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
WORKDIR /app
COPY . .

# Build only the packages you need
RUN uv build --package gds-database --out-dir dist/
RUN uv build --package gds-mssql --out-dir dist/

FROM python:3.12-slim-bookworm
WORKDIR /app
COPY --from=builder /app/dist/*.whl ./
RUN pip install --no-cache-dir *.whl
```

### Where Are Packages Installed?

After `uv sync`, packages are installed in the virtual environment's site-packages:

| Container Path | Contents |
|----------------|----------|
| `/app/.venv/bin/` | Python executable, scripts |
| `/app/.venv/lib/python3.x/site-packages/` | All installed packages |
| `/app/.venv/lib/python3.x/site-packages/gds_database/` | Your workspace package |

> [!TIP]
> The virtual environment's site-packages location is the same as pip's—UV just manages it differently during development.

---

## Troubleshooting

### "Lock file not found"

```dockerfile
# Ensure both files are copied
COPY pyproject.toml uv.lock ./
```

### "Failed to hardlink"

Use copy mode in multi-stage builds:

```dockerfile
ENV UV_LINK_MODE=copy
```

### Slow builds

1. Order Dockerfile to maximize caching
2. Use BuildKit cache mounts
3. Use `--no-install-project` first

### Permission errors

Run as non-root user:

```dockerfile
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser
```

---

## Related Guides

- [UV Getting Started](../../../tutorials/python/uv/uv-getting-started.md)
- [UV CI/CD Integration](./uv-ci-cd-integration.md)
- [Docker Tutorial](../../../tutorials/docker/README.md)
- [Official UV Documentation](https://docs.astral.sh/uv/)

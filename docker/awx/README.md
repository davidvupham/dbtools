# AWX Controller Image

A thin wrapper around the upstream `quay.io/ansible/awx` release that adds a curl-based health check and
keeps the version pinned for reproducibility.

## Build

```bash
cd docker/awx
docker build -t dbtools/awx:24.6.1 .
```

Override the upstream tag when you need to test a different controller release:

```bash
docker build --build-arg AWX_VERSION=24.7.0 -t dbtools/awx:24.7.0 .
```

This image is intended to run inside the Compose stack defined in `docker/docker-compose.ansible-awx.yml`,
which wires up the companion PostgreSQL and Redis dependencies that AWX expects.

## Prerequisites

The Compose stack requires an external Docker network. Create it before starting:

```bash
docker network create devcontainer-network
```

## Usage

Start the full AWX stack (controller, PostgreSQL, and Redis):

```bash
cd docker
docker compose -f docker-compose.ansible-awx.yml up -d
```

AWX takes 1-2 minutes to initialize on first startup. Check the logs:

```bash
docker logs -f awx-controller
```

Once running, access the AWX web UI at **http://localhost:8052**.

Default credentials:
- Username: `admin`
- Password: `changeme`

To stop the stack:

```bash
docker compose -f docker-compose.ansible-awx.yml down
```

## Environment Variables

Override these in your shell or a `.env` file before starting:

| Variable | Default | Description |
|----------|---------|-------------|
| `AWX_ADMIN_USER` | `admin` | AWX admin username |
| `AWX_ADMIN_PASSWORD` | `changeme` | AWX admin password |
| `AWX_SECRET_KEY` | `super-secret-key` | Encryption key for credentials |
| `AWX_POSTGRES_PASSWORD` | `awxpass` | PostgreSQL database password |

For production deployments, always set `AWX_ADMIN_PASSWORD` and `AWX_SECRET_KEY` to secure values.

## Podman alternative

Replace `docker` with `podman` for all commands:

```bash
# Build
podman build -t dbtools/awx:24.6.1 .

# Create network
podman network create devcontainer-network

# Start the stack
podman-compose -f docker-compose.ansible-awx.yml up -d

# Check logs
podman logs -f awx-controller

# Stop the stack
podman-compose -f docker-compose.ansible-awx.yml down
```

On RHEL/Fedora with SELinux, add `:Z` to volume mounts for proper labeling.

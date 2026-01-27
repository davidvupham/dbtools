# Docker services

This directory contains Docker Compose configurations for local development services.

## Podman compatibility

All services support both Docker and Podman. On RHEL/CentOS systems where Podman is the default container runtime, use these command equivalents:

| Docker command | Podman equivalent |
|----------------|-------------------|
| `docker compose` | `podman-compose` or `podman compose` |
| `docker build` | `podman build` |
| `docker run` | `podman run` |
| `docker exec` | `podman exec` |
| `docker logs` | `podman logs` |
| `docker ps` | `podman ps` |
| `docker images` | `podman images` |
| `docker inspect` | `podman inspect` |

**SELinux volume labels**: On RHEL/Fedora with SELinux enabled, add `:Z` to volume mounts for private unshared labels or `:z` for shared labels.

See [Podman cheatsheet](../docs/reference/podman/cheatsheet.md) for more details.

## Services overview

| Service | Description | Port(s) |
|---------|-------------|---------|
| [ansible/](./ansible/) | Standalone Ansible container | - |
| [awx/](./awx/) | AWX (Ansible Web UI) | 8080 |
| [awx-ee/](./awx-ee/) | AWX Execution Environment | - |
| [hammerdb/](./hammerdb/) | HammerDB performance testing | - |
| [vault/](./vault/) | HashiCorp Vault | 8200 |
| [kafka/](./kafka/) | Apache Kafka message broker | 9092 |
| [liquibase/](./liquibase/) | Liquibase database migrations | - |
| [mongodb/](./mongodb/) | MongoDB database | 27017 |
| [mssql/](./mssql/) | SQL Server database | 1433 |
| [postgresql/](./postgresql/) | PostgreSQL database | 5432 |
| [prometheus/](./prometheus/) | Prometheus monitoring | 9090 |
| [rabbitmq/](./rabbitmq/) | RabbitMQ message broker | 5672, 15672 |

## Quick start

### Start all common services

```bash
# Docker
docker compose -f docker/docker-compose.yml up -d

# Podman
podman-compose -f docker/docker-compose.yml up -d
```

### Start a specific service

```bash
# Docker - Start PostgreSQL
docker compose -f docker/postgresql/docker-compose.yml up -d

# Podman - Start PostgreSQL
podman-compose -f docker/postgresql/docker-compose.yml up -d

# Docker - Start Vault
docker compose -f docker/vault/docker-compose.yml up -d

# Podman - Start Vault
podman-compose -f docker/vault/docker-compose.yml up -d
```

### Start AWX stack

```bash
# Docker
docker compose -f docker/docker-compose.ansible-awx.yml up -d

# Podman
podman-compose -f docker/docker-compose.ansible-awx.yml up -d
```

## Service directory structure

Each service follows a consistent pattern:

```text
docker/[service]/
├── docker-compose.yml    # Primary compose configuration
├── Dockerfile            # Custom image definition (if needed)
├── README.md             # Service-specific documentation
└── [config files]        # Additional configuration
```

## Environment variables

Most services require environment variables. Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your values
```

## Networking

Services can communicate using Docker's internal networking. The default network name is `dbtools_default`.

## Related documentation

- [Podman alternatives](../docs/reference/podman/) - Running services with Podman
- [Dev container](../.devcontainer/) - Full development environment

# Docker services

This directory contains Docker Compose configurations for local development services.

## Services overview

| Service | Description | Port(s) |
|---------|-------------|---------|
| [ansible/](./ansible/) | Standalone Ansible container | - |
| [awx/](./awx/) | AWX (Ansible Web UI) | 8080 |
| [awx-ee/](./awx-ee/) | AWX Execution Environment | - |
| [hammerdb/](./hammerdb/) | HammerDB performance testing | - |
| [hvault/](./hvault/) | HashiCorp Vault | 8200 |
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
docker compose -f docker/docker-compose.yml up -d
```

### Start a specific service

```bash
# Example: Start PostgreSQL
docker compose -f docker/postgresql/docker-compose.yml up -d

# Example: Start Vault
docker compose -f docker/hvault/docker-compose.yml up -d
```

### Start AWX stack

```bash
docker compose -f docker/docker-compose.ansible-awx.yml up -d
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

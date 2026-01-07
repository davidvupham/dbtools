# Liquibase Docker - Quick Start Guide

This guide walks through building the custom Liquibase image in this repository, validating it, and running Liquibase commands inside the container. It assumes you can run Docker commands on your workstation or CI runner.

> **📖 For comprehensive operational procedures**, see the [Liquibase Docker Operations Guide](liquibase-docker-operations-guide.md) which covers:
>
> - Health checks and validation workflows
> - Rollback procedures and recovery
> - Production best practices
> - Troubleshooting common issues
> - Complete command reference

## Prerequisites

- Docker 20.10+ (or compatible OCI runtime)
- Internet access to download:
  - Liquibase distribution (GitHub releases)
  - JDBC drivers for Microsoft SQL Server, PostgreSQL, Snowflake, and MongoDB
- Optional: a SQL Server or PostgreSQL instance for end-to-end testing (local containers work fine)

The custom image bundles the JDBC drivers so you do not need to add them at runtime.

## Repository layout

- `docker/liquibase/Dockerfile`: builds Liquibase on `eclipse-temurin:21-jre`, installs the JDBC drivers, and sets `liquibase` as the entrypoint.
- `docs/tutorials/liquibase/learning-paths/series-part1-baseline.md`: contains a complete Liquibase walk-through you can pair with this Docker workflow.

## Build the image

Run the following command from the repository root:

```bash
docker build -t liquibase-custom:latest docker/liquibase
```

Build arguments (optional overrides):

- `LIQUIBASE_VERSION` (default `5.0.1`)
- `MSSQL_DRIVER_VERSION` (default `13.2.1`)
- `POSTGRES_DRIVER_VERSION` (default `42.7.8`)
- `SNOWFLAKE_DRIVER_VERSION` (default `3.27.1`)
- `MONGODB_DRIVER_VERSION` (default `3.12.14`)
- `LIQUIBASE_MONGODB_VERSION` (default `5.0.1`)
- Base image: `eclipse-temurin:21-jre`

Example overriding the Liquibase version:

```bash
docker build \
  --build-arg LIQUIBASE_VERSION=5.0.0 \
  -t liquibase-custom:5.0.0 \
  docker/liquibase
```

## Smoke test the image

Verify the image launches and reports the embedded drivers:

```bash
docker run --rm liquibase-custom:latest --version
```

Expected highlights include Liquibase `5.0.1`, Java 21, and JDBC drivers (SQL Server `13.2.1`, PostgreSQL `42.7.8`, Snowflake `3.27.1`, MongoDB `3.12.14`). If the command fails with “exec: `liquibase`: executable file not found”, rebuild; the current Dockerfile extracts the launcher correctly.

## Run Liquibase commands in the container

Recommended path convention: mount your changelog root to `/data/liquibase` inside the container and reference absolute paths. This matches our architecture docs and keeps host/container paths consistent.

Alternative (legacy) path: `/liquibase` also works (examples provided).

### 1. Prepare a changelog and properties file

Place your changelog and `liquibase.properties` in a folder, e.g. (simple quick-start layout):

```text
db/
  changelog/
    changelog.xml
    changes/*.sql
  liquibase.properties
```

Sample `liquibase.properties`:

```properties
url=jdbc:sqlserver://mssql:1433;databaseName=demo
username=sa
password=YourStrong!Passw0rd
changelog-file=changelog/changelog.xml
```

### 2. Run a dry run (`updateSQL`)

Using the canonical `/data/liquibase` path:

```bash
docker run --rm \
  --network devcontainer-network \
  -v "$(pwd)/db":/data/liquibase:ro \
  liquibase-custom:latest \
  --defaults-file /data/liquibase/liquibase.properties \
  --changelog-file /data/liquibase/changelog/changelog.xml \
  updateSQL
```

Using the legacy `/liquibase` path:

```bash
docker run --rm \
  -v "$(pwd)/db":/liquibase:ro \
  liquibase-custom:latest \
  updateSQL
```

Liquibase will print the SQL it would execute, without touching the database.

### 3. Apply changes (`update`)

```bash
docker run --rm \
  --network devcontainer-network \
  -v "$(pwd)/db":/data/liquibase:ro \
  liquibase-custom:latest \
  --defaults-file /data/liquibase/liquibase.properties \
  --changelog-file /data/liquibase/changelog/changelog.xml \
  update
```

Environment variables override properties if needed:

```bash
docker run --rm \
  --network devcontainer-network \
  -e LIQUIBASE_URL="jdbc:postgresql://postgres:5432/demo" \
  -e LIQUIBASE_USERNAME=demo \
  -e LIQUIBASE_PASSWORD=secret \
  -v "$(pwd)/db":/data/liquibase:ro \
  liquibase-custom:latest \
  --changelog-file /data/liquibase/changelog/changelog.xml \
  update
```

Validate without applying changes:

```bash
docker run --rm \
  --network devcontainer-network \
  -v "$(pwd)/db":/data/liquibase:ro \
  liquibase-custom:latest \
  --defaults-file /data/liquibase/liquibase.properties \
  validate
```

## Testing with local databases

You can pair the custom Liquibase image with the local Microsoft SQL Server and PostgreSQL images in this repo.

### Build database images (optional)

```bash
docker build -t mssql-local:latest docker/mssql
docker build -t postgres-local:latest docker/postgresql
```

Or use upstream images directly:

```bash
docker run -d --name mssql \
  -e ACCEPT_EULA=Y \
  -e MSSQL_PID=Developer \
  -e SA_PASSWORD="YourStrong!Passw0rd" \
  -p 1433:1433 \
  --network devcontainer-network \
  mcr.microsoft.com/mssql/server:2022-latest

> Looking for the Podman + Postgres + SQL Server end-to-end test? See the dedicated section in [liquibase-docker-operations-guide.md](liquibase-docker-operations-guide.md#rootless-podman-end-to-end-test-postgresql--sql-server).

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
- `docs/tutorials/liquibase/sqlserver-liquibase-tutorial.md`: contains a complete Liquibase walk-through you can pair with this Docker workflow.

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

Liquibase reads changelog files relative to the container’s working directory (`/liquibase`). Mount your project into that path.

### 1. Prepare a changelog and properties file

Place your changelog and `liquibase.properties` in a folder, e.g.:

```
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

```bash
docker run --rm \
  -v "$(pwd)/db":/liquibase \
  liquibase-custom:latest \
  updateSQL
```

Liquibase will print the SQL it would execute, without touching the database.

### 3. Apply changes (`update`)

```bash
docker run --rm \
  -v "$(pwd)/db":/liquibase \
  liquibase-custom:latest \
  update
```

Environment variables override properties if needed:

```bash
docker run --rm \
  -e LIQUIBASE_URL="jdbc:postgresql://postgres:5432/demo" \
  -e LIQUIBASE_USERNAME=demo \
  -e LIQUIBASE_PASSWORD=secret \
  -v "$(pwd)/db":/liquibase \
  liquibase-custom:latest \
  update
```

## Testing with local databases

You can pair the custom Liquibase image with the local Microsoft SQL Server and PostgreSQL images in this repo.

### Build database images (optional)

```bash
docker build -t mssql-local:latest docker/mssql
docker build -t postgres-local:latest docker/postgres
```

Or use upstream images directly:

```bash
docker run -d --name mssql \
  -e ACCEPT_EULA=Y \
  -e MSSQL_PID=Developer \
  -e SA_PASSWORD="YourStrong!Passw0rd" \
  -p 1433:1433 \
  mcr.microsoft.com/mssql/server:2022-latest

docker run -d --name postgres \
  -e POSTGRES_DB=demo \
  -e POSTGRES_USER=demo \
  -e POSTGRES_PASSWORD=secret \
  -p 5432:5432 \
  postgres:latest
```

Point your `liquibase.properties` at the running container (host `host.docker.internal` on macOS/Windows, `localhost` on Linux if using bridge networking).

## Running Liquibase interactively

To explore inside the container:

```bash
docker run --rm -it \
  -v "$(pwd)/db":/liquibase \
  --entrypoint /bin/sh \
  liquibase-custom:latest
```

Once in the shell, you can run commands such as `liquibase status` or inspect the bundled libraries under `/opt/liquibase/lib`.

## Cleanup

- Stop and remove test database containers:

```bash
docker rm -f mssql postgres
```

- Remove the custom image if needed:

```bash
docker rmi liquibase-custom:latest
```

## Troubleshooting

- **`liquibase` not found**: rebuild the image (we fixed the extraction issue in November 2025). Ensure the build completes without errors.
- **JDBC connection failures**: check hostnames, ports, and firewalls. For containers on the same Docker network, use service names.
- **Certificate/SSL issues**: add the appropriate JDBC parameters (e.g., `?encrypt=true;trustServerCertificate=true` for SQL Server).
- **Custom drivers**: override the build args to download different driver versions or copy additional JARs into `/opt/liquibase/lib`.
- **Permissions on mounted volumes**: ensure the host user can read the changelog files; root inside the container must see them.

> **💡 For detailed troubleshooting**, see the [Troubleshooting section](liquibase-docker-operations-guide.md#troubleshooting) in the Operations Guide for solutions to common issues including lock management, checksum mismatches, and connection problems.

## Next Steps

### Day-to-Day Operations

For comprehensive operational procedures, refer to the **[Liquibase Docker Operations Guide](liquibase-docker-operations-guide.md)**:

- **[Common Operations](liquibase-docker-operations-guide.md#common-operations)** - Update, rollback, preview, tagging, validation
- **[Health Checks](liquibase-docker-operations-guide.md#health-checks-and-validation)** - Pre/post-migration validation workflows
- **[Monitoring](liquibase-docker-operations-guide.md#monitoring-and-logs)** - Log management and database changelog queries
- **[Best Practices](liquibase-docker-operations-guide.md#best-practices)** - Changelog management, security, testing strategies
- **[Command Reference](liquibase-docker-operations-guide.md#command-reference)** - Complete command listing with examples

### Advanced Usage

- Integrate the image into CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins)
- Use `docker-compose.yml` in this directory to orchestrate databases and migrations together
- Publish the image to an internal container registry for team distribution
- Implement automated migration testing in non-production environments

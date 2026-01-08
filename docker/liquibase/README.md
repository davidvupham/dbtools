# Liquibase Docker - Quick Start Guide

This guide walks through building the custom Liquibase image in this repository, validating it, and running Liquibase commands inside the container. It assumes you can run Docker commands on your workstation or CI runner.

> **📖 For comprehensive operational procedures**, see the [Liquibase Docker Operations Guide](liquibase-docker-operations-guide.md) which covers:
>
> - Health checks and validation workflows
> - Rollback procedures and recovery
> - Production best practices
> - Troubleshooting common issues
> - Complete command reference

## Containerized Liquibase: Pros and Cons

Liquibase is a CLI tool, but running it in a container is still useful: you package a known-good Liquibase + Java + JDBC driver set and run it on-demand (the container runs a command and exits).

**Pros**

- Reproducible runs: same Liquibase/Java/JDBC driver versions across dev and CI
- Less workstation setup: no local Java/Liquibase/driver installs required
- Fewer dependency conflicts: isolates Java + driver jars from host tooling
- CI-friendly: clean, repeatable, disposable execution environment

**Cons / trade-offs**

- Networking can be trickier: the container must be able to reach the target DB (DNS, routing, VPN, firewall)
- Mount paths matter: changelogs/properties must be mounted where Liquibase can read them
- File permissions/labels can surprise on Linux (especially rootless Podman + SELinux)
- Slight overhead: image build/pull time vs running a local binary

If you want interactive debugging/fast iteration or container networking is constrained in your environment, a local Liquibase install may be simpler.

## Prerequisites

- Docker (Ubuntu / typical dev workstations): Docker Engine 20.10+ and Docker Compose v2 (`docker compose`)
- Podman (RHEL / SELinux environments): rootless Podman + `podman-compose`
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
docker build -t liquibase:latest docker/liquibase
```

Note: If you prefer using compose from the repo root, add `--project-directory docker/liquibase` so the build context resolves to this directory.

On RHEL with Podman:
```bash
podman build -t liquibase:latest docker/liquibase --format docker
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
  -t liquibase:5.0.0 \
  docker/liquibase
```

## Smoke test the image

Verify the image launches and reports the embedded drivers:

```bash
docker run --rm liquibase:latest --version
```

On RHEL with Podman:

```bash
podman run --rm liquibase:latest --version
```

Expected highlights include Liquibase `5.0.1`, Java 21, and JDBC drivers (SQL Server `13.2.1`, PostgreSQL `42.7.8`, Snowflake `3.27.1`, MongoDB `3.12.14`). If the command fails with “exec: `liquibase`: executable file not found”, rebuild; the current Dockerfile extracts the launcher correctly.

## Run Liquibase commands in the container

Recommended path convention: mount your changelog root to `/liquibase` inside the container. On the host we default to `/data/liquibase`; override with `LIQUIBASE_HOST_ROOT` if needed.

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

Using the canonical `/liquibase` path:

```bash
docker run --rm \
  -v "$(pwd)/db":/liquibase:ro \
  liquibase:latest \
  --defaults-file /liquibase/liquibase.properties \
  --changelog-file /liquibase/changelog/changelog.xml \
  updateSQL
```

On RHEL with rootless Podman + SELinux, add a volume label:

```bash
podman run --rm \
  -v "$(pwd)/db":/liquibase:ro,Z \
  liquibase:latest \
  --defaults-file /liquibase/liquibase.properties \
  --changelog-file /liquibase/changelog/changelog.xml \
  updateSQL
```

Liquibase will print the SQL it would execute, without touching the database.

### 3. Apply changes (`update`)

```bash
docker run --rm \
  -v "$(pwd)/db":/liquibase:ro \
  liquibase:latest \
  --defaults-file /liquibase/liquibase.properties \
  --changelog-file /liquibase/changelog/changelog.xml \
  update
```

Environment variables override properties if needed:

```bash
docker run --rm \
  -e LIQUIBASE_URL="jdbc:postgresql://postgres:5432/demo" \
  -e LIQUIBASE_USERNAME=demo \
  -e LIQUIBASE_PASSWORD=secret \
  -v "$(pwd)/db":/liquibase:ro \
  liquibase:latest \
  --changelog-file /liquibase/changelog/changelog.xml \
  update
```

For external databases, prefer DNS/IP in your JDBC URL (e.g., corporate MSSQL on Windows Server):

```bash
docker run --rm \
  -e LIQUIBASE_URL="jdbc:sqlserver://mssql.corp.example:1433;databaseName=demo" \
  -e LIQUIBASE_USERNAME=demo \
  -e LIQUIBASE_PASSWORD=secret \
  -v "$(pwd)/db":/liquibase:ro \
  liquibase:latest \
  --changelog-file /liquibase/changelog/changelog.xml \
  update
```

Validate without applying changes:

```bash
docker run --rm \
  -v "$(pwd)/db":/liquibase:ro \
  liquibase:latest \
  --defaults-file /liquibase/liquibase.properties \
  validate
```

## Compose workflow (recommended)

The repo includes a compose definition for repeatable mounts and (optionally) joining a shared container network.

**Standalone mode (default):** external DB reachable by DNS/IP; no shared container network needed.

```bash
docker compose -f docker/liquibase/docker-compose.yml run --rm liquibase --help
```

On RHEL (rootless Podman):

```bash
podman-compose -f docker/liquibase/docker-compose.yml run --rm liquibase --help
```

If you create docker/liquibase/.env (optional), the Make targets will pick it up automatically.

### Network mode (only for connecting to DB containers by name)

If your database is running in another container/compose stack and you want to connect by container/service name (e.g., `postgres`, `mssql`), run Liquibase on the same external container network.

- Copy docker/liquibase/.env.example to docker/liquibase/.env
- Set `DBTOOLS_NETWORK` to the existing network name
- On RHEL/SELinux, keep `LIQUIBASE_VOLUME_SUFFIX=:Z` (recommended)

Then include the override file:

```bash
docker compose \
  -f docker/liquibase/docker-compose.yml \
  -f docker/liquibase/docker-compose.network.yml \
  --env-file docker/liquibase/.env \
  run --rm liquibase --help
```

On RHEL:

```bash
podman-compose \
  -f docker/liquibase/docker-compose.yml \
  -f docker/liquibase/docker-compose.network.yml \
  --env-file docker/liquibase/.env \
  run --rm liquibase --help
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
  mcr.microsoft.com/mssql/server:2022-latest

docker run -d --name postgres \
  -e POSTGRES_DB=demo \
  -e POSTGRES_USER=demo \
  -e POSTGRES_PASSWORD=secret \
  -p 5432:5432 \
  postgres:latest
```
> Looking for the Podman + Postgres + SQL Server end-to-end test? See the dedicated section in [liquibase-docker-operations-guide.md](liquibase-docker-operations-guide.md#rootless-podman-end-to-end-test-postgresql--sql-server).
Point your `liquibase.properties` at the database using DNS/IP. If the database runs in another container stack and you want to connect by container/service name, use the Compose “Network mode” workflow above.

To explore inside the container:

```bash
docker run --rm -it \
  -v "$(pwd)/db":/liquibase:ro \
  --entrypoint /bin/sh \
  liquibase:latest
```

Once in the shell, you can run commands such as `liquibase status` or inspect the bundled libraries under `/opt/liquibase/lib`.

## Cleanup

- Stop and remove test database containers:

```bash
docker rm -f mssql postgres
```

- Remove the custom image if needed:

```bash
docker rmi liquibase:latest
```

## Troubleshooting

- **`liquibase` not found**: rebuild the image (we fixed the extraction issue in November 2025). Ensure the build completes without errors.
- **JDBC connection failures**: check hostnames, ports, and firewalls. For containers on the same Docker network, use service names.
- **Certificate/SSL issues**: add the appropriate JDBC parameters (e.g., `?encrypt=true;trustServerCertificate=true` for SQL Server).
- **Custom drivers**: override the build args to download different driver versions or copy additional JARs into `/opt/liquibase/lib`.
- **Permissions on mounted volumes**: ensure the host user can read the changelog files; root inside the container must see them.

## Security and secrets

- Do not commit real credentials to version control. Use templates like `*.properties.template` and provide actual values via CI/CD secrets or environment variables.
- Prefer environment variables (e.g., `LIQUIBASE_URL`, `LIQUIBASE_USERNAME`, `LIQUIBASE_PASSWORD`) or secret managers.
- If using local properties files, consider a global root such as `/data/liquibase` and ignore non-template files:

  ```gitignore
  /data/liquibase/**/*.properties
  !/data/liquibase/**/*.properties.template
  ```

> **💡 For detailed troubleshooting**, see the [Troubleshooting section](liquibase-docker-operations-guide.md#troubleshooting) in the Operations Guide for solutions to common issues including lock management, checksum mismatches, and connection problems.

## Next Steps

### Recommended follow-up

- If you use a host path other than `/data/liquibase`, set `LIQUIBASE_HOST_ROOT` in `docker/liquibase/.env`; for rootless Podman also set `LIQUIBASE_UID`/`LIQUIBASE_GID` and keep `LIQUIBASE_VOLUME_SUFFIX=:Z` when needed.
- Quick sanity check after configuring `.env`:

```bash
docker compose -f docker/liquibase/docker-compose.yml run --rm liquibase --version
# or
podman-compose -f docker/liquibase/docker-compose.yml run --rm liquibase --version
```

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

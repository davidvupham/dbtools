# Database CLI tools containers

This directory contains Dockerfiles for building lightweight database CLI tool containers. These containers provide database client utilities without requiring local installation.

## Available tools

| Directory | Description | Tools included |
|-----------|-------------|----------------|
| `db-tools` | All-in-one multi-database client | psql, sqlcmd, mongosh, snowsql, bcp |
| `psql` | PostgreSQL client | psql, pg_dump, pg_restore |
| `mssql-tools` | SQL Server client | sqlcmd, bcp |
| `mongosh` | MongoDB shell | mongosh |
| `snowsql` | Snowflake CLI | snowsql |
| `clickhouse-client` | ClickHouse client | clickhouse-client |

## Build

### Docker

```bash
# Build all-in-one container
docker build -t db-tools:latest docker/tools/db-tools

# Build individual tool containers
docker build -t psql:latest docker/tools/psql
docker build -t mssql-tools:latest docker/tools/mssql-tools
docker build -t mongosh:latest docker/tools/mongosh
docker build -t snowsql:latest docker/tools/snowsql
docker build -t clickhouse-client:latest docker/tools/clickhouse-client
```

### Podman

```bash
# Build all-in-one container
podman build -t db-tools:latest docker/tools/db-tools

# Build individual tool containers
podman build -t psql:latest docker/tools/psql
podman build -t mssql-tools:latest docker/tools/mssql-tools
podman build -t mongosh:latest docker/tools/mongosh
podman build -t snowsql:latest docker/tools/snowsql
podman build -t clickhouse-client:latest docker/tools/clickhouse-client
```

## Usage

### Docker

```bash
# PostgreSQL
docker run --rm -it psql:latest psql -h hostname -U username -d database

# SQL Server
docker run --rm -it mssql-tools:latest sqlcmd -S hostname -U username -P password

# MongoDB
docker run --rm -it mongosh:latest mongosh "mongodb://hostname:27017"

# Snowflake (mount config directory)
docker run --rm -it -v ~/.snowsql:/root/.snowsql:ro snowsql:latest snowsql

# ClickHouse
docker run --rm -it clickhouse-client:latest clickhouse-client --host hostname

# All-in-one (specify which tool to run)
docker run --rm -it db-tools:latest psql -h hostname -U username -d database
docker run --rm -it db-tools:latest sqlcmd -S hostname -U username -P password
docker run --rm -it db-tools:latest mongosh "mongodb://hostname:27017"
```

### Podman

```bash
# PostgreSQL
podman run --rm -it psql:latest psql -h hostname -U username -d database

# SQL Server
podman run --rm -it mssql-tools:latest sqlcmd -S hostname -U username -P password

# MongoDB
podman run --rm -it mongosh:latest mongosh "mongodb://hostname:27017"

# Snowflake (mount config directory with SELinux label)
podman run --rm -it -v ~/.snowsql:/root/.snowsql:ro,Z snowsql:latest snowsql

# ClickHouse
podman run --rm -it clickhouse-client:latest clickhouse-client --host hostname

# All-in-one (specify which tool to run)
podman run --rm -it db-tools:latest psql -h hostname -U username -d database
podman run --rm -it db-tools:latest sqlcmd -S hostname -U username -P password
podman run --rm -it db-tools:latest mongosh "mongodb://hostname:27017"
```

## Connecting to containers on the same network

To connect to database containers running on a shared Docker/Podman network:

### Docker

```bash
# Create network if needed
docker network create devcontainer-network

# Connect to PostgreSQL container
docker run --rm -it --network devcontainer-network psql:latest psql -h psql1 -U postgres

# Connect to SQL Server container
docker run --rm -it --network devcontainer-network mssql-tools:latest sqlcmd -S mssql1 -U SA -P "$MSSQL_SA_PASSWORD"

# Connect to MongoDB container
docker run --rm -it --network devcontainer-network mongosh:latest mongosh "mongodb://mongodb1:27017"
```

### Podman

```bash
# Create network if needed
podman network create devcontainer-network

# Connect to PostgreSQL container
podman run --rm -it --network devcontainer-network psql:latest psql -h psql1 -U postgres

# Connect to SQL Server container
podman run --rm -it --network devcontainer-network mssql-tools:latest sqlcmd -S mssql1 -U SA -P "$MSSQL_SA_PASSWORD"

# Connect to MongoDB container
podman run --rm -it --network devcontainer-network mongosh:latest mongosh "mongodb://mongodb1:27017"
```

## SELinux notes (RHEL/Fedora)

On systems with SELinux enabled, add `:Z` to volume mounts for proper labeling:

```bash
podman run --rm -it -v ~/.snowsql:/root/.snowsql:ro,Z snowsql:latest snowsql
podman run --rm -it -v ./scripts:/scripts:Z db-tools:latest psql -f /scripts/query.sql
```

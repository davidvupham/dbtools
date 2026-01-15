# Liquibase Tutorial - Containers

This directory contains the container-compose configuration used by the Liquibase course.

## What gets created

Three SQL Server containers (one per environment):

- `mssql_dev` (host port `14331`)
- `mssql_stg` (host port `14332`)
- `mssql_prd` (host port `14333`)

And an optional run-once Liquibase tool container (profile `tools`):

- `liquibase_tutorial`

## Prerequisites

Set the SQL Server SA password as an environment variable:

```bash
export MSSQL_LIQUIBASE_TUTORIAL_PWD='<YOUR_STRONG_PASSWORD>'
```

**Important**: The password must meet SQL Server complexity requirements:

- At least 8 characters
- Contains uppercase and lowercase letters
- Contains numbers
- Contains special characters

## Starting the Container

```bash
cd "$LIQUIBASE_TUTORIAL_DIR/docker"

# Start SQL Server containers (dev/stg/prd)
docker compose up -d mssql_dev mssql_stg mssql_prd
```

Tip: the course scripts wrap this for you:

```bash
"$LIQUIBASE_TUTORIAL_DIR/scripts/step02_start_containers.sh"
```

## Stopping the Container

```bash
docker compose down
```

## Removing Everything After Tutorial

To completely clean up after completing the tutorial:

```bash
# Stop and remove containers
docker compose down

# Remove tutorial data directory (destructive)
rm -rf "${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/$USER/liquibase_tutorial}"
```

## Health Check

The container includes a health check that verifies SQL Server is ready to accept connections.

Check the health status:

Each SQL Server service defines a healthcheck. Verify with:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

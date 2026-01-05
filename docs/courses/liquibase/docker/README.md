# Liquibase Tutorial - SQL Server Container

This directory contains the Docker configuration for a dedicated SQL Server instance used in the Liquibase tutorial.

## Container Details

- **Container Name**: `mssql_liquibase_tutorial`
- **Image**: `mcr.microsoft.com/mssql/server:2025-latest`
- **Port**: `1433`
- **Network**: `liquibase_tutorial`
- **Volume**: `mssql_liquibase_tutorial_data`

## Prerequisites

Set the SQL Server SA password as an environment variable:

```bash
export MSSQL_LIQUIBASE_TUTORIAL_PWD='YourStrong!Passw0rd'
```

**Important**: The password must meet SQL Server complexity requirements:

- At least 8 characters
- Contains uppercase and lowercase letters
- Contains numbers
- Contains special characters

## Starting the Container

```bash
cd "$LIQUIBASE_TUTORIAL_DIR/docker"
docker compose up -d
```

## Stopping the Container

```bash
docker compose down
```

## Removing Everything After Tutorial

To completely clean up after completing the tutorial:

```bash
# Stop and remove the container
docker compose down

# Remove the volume (deletes all databases)
docker volume rm mssql_liquibase_tutorial_data

# Remove the network
docker network rm liquibase_tutorial
```

## Health Check

The container includes a health check that verifies SQL Server is ready to accept connections.

Check the health status:

```bash
docker ps
```

Look for "healthy" in the STATUS column.

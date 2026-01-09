# Liquibase Quick Reference

## Common Commands

| Command | Description |
|---------|-------------|
| `lb -e dev -- status` | Show pending changes for dev |
| `lb -e dev -- update` | Apply pending changes |
| `lb -e dev -- updateSQL` | Preview SQL without applying |
| `lb -e dev -- rollback-count 1` | Rollback last changeset |
| `lb -e dev -- rollback-to-tag v1.0` | Rollback to tag |
| `lb -e dev -- tag v1.0` | Create a tag |
| `lb -e dev -- history` | Show deployment history |
| `lb -e dev -- diff` | Compare database to changelog |

## Environment Options

```bash
lb -e dev -- <command>    # Development (port 14331)
lb -e stg -- <command>    # Staging (port 14332)
lb -e prd -- <command>    # Production (port 14333)
```

## Step Scripts

| Script | Purpose |
|--------|---------|
| `step01_setup_environment.sh` | Create directories, set env vars |
| `step02_start_containers.sh` | Start all SQL Server containers |
| `step03_create_databases.sh` | Create orderdb on all containers |
| `step04_populate_dev.sh` | Add sample objects to dev |
| `step05_generate_baseline.sh` | Generate baseline changelog |
| `validate_tutorial.sh` | Validate entire setup |
| `cleanup_tutorial.sh` | Remove all tutorial resources |

## Formatted SQL Syntax

```sql
--liquibase formatted sql

--changeset author:id
-- Purpose: Description of change
CREATE TABLE app.example (...);
GO

--rollback DROP TABLE IF EXISTS app.example;
```

## File Naming

- Baseline: `V0000__baseline.mssql.sql`
- Changes: `V0001__description.mssql.sql`
- Format: `V<number>__<description>.mssql.sql`

## Container Ports

| Container | Port | Database |
|-----------|------|----------|
| mssql_dev | 14331 | orderdb |
| mssql_stg | 14332 | orderdb |
| mssql_prd | 14333 | orderdb |

## Troubleshooting

```bash
# Check container status
podman ps -a | grep mssql

# View container logs
podman logs mssql_dev

# Test database connection
podman exec mssql_dev /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" -Q "SELECT 1"

# Validate environment
./validation/scripts/validate_tutorial.sh
```

# Liquibase Docker Operations Guide

> **🚀 New to Liquibase Docker?** Start with the [Quick Start Guide](README.md) to build the image and run your first migration.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Building the Image](#building-the-image)
- [Directory Structure](#directory-structure)
- [Running Liquibase](#running-liquibase)
- [Common Operations](#common-operations)
- [Health Checks and Validation](#health-checks-and-validation)
- [Monitoring and Logs](#monitoring-and-logs)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Command Reference](#command-reference)

## Overview

Liquibase is a database schema change management tool that tracks, versions, and deploys database changes. This guide covers operational procedures for running Liquibase in Docker containers.

**Key Characteristics:**

- Liquibase is a **run-once** tool (not a long-running service)
- Executes a migration command and exits
- Requires connection to target database(s)
- Works with changelogs (XML, YAML, JSON, or SQL format)

## Prerequisites

### Required Software

- Docker Engine 20.10+ or Docker Desktop
- Docker Compose 2.0+
- Access to target database(s)

### Required Files

```
docker/liquibase/
├── Dockerfile                    # Image definition
├── docker-compose.yml            # Compose configuration
├── changelogs/                   # Your migration scripts
│   ├── master.xml               # Main changelog (example)
│   ├── v1.0/                    # Version-specific changes
│   └── ...
├── liquibase.properties         # Optional: default connection settings
└── OPERATIONS_GUIDE.md          # This file
```

### Network Access

- Liquibase must reach database servers (same Docker network or network connectivity)
- If databases are in other compose files, ensure network is shared

## Building the Image

> **📦 For detailed build instructions**, see the [Quick Start Guide - Build the Image](README.md#build-the-image) section.

**Quick reference:**

```bash
# Navigate to the liquibase directory
cd /workspaces/dbtools/docker/liquibase

# Build using docker-compose (recommended)
docker-compose build

# Verify build
docker run --rm liquibase:5.0.1 --version
```

For custom version builds and troubleshooting build issues, refer to the Quick Start Guide.

## Directory Structure

### Changelog Organization (Best Practice)

```
changelogs/
├── master.xml                          # Master changelog file
├── v1.0/
│   ├── 001-create-users-table.xml
│   ├── 002-create-orders-table.xml
│   └── 003-add-indexes.xml
├── v1.1/
│   ├── 001-add-user-email-column.xml
│   └── 002-create-audit-table.xml
└── v2.0/
    └── 001-refactor-schema.xml
```

### Master Changelog Example (master.xml)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
    http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-latest.xsd">

    <!-- Version 1.0 Changes -->
    <include file="changelogs/v1.0/001-create-users-table.xml"/>
    <include file="changelogs/v1.0/002-create-orders-table.xml"/>
    <include file="changelogs/v1.0/003-add-indexes.xml"/>

    <!-- Version 1.1 Changes -->
    <include file="changelogs/v1.1/001-add-user-email-column.xml"/>
    <include file="changelogs/v1.1/002-create-audit-table.xml"/>

    <!-- Version 2.0 Changes -->
    <include file="changelogs/v2.0/001-refactor-schema.xml"/>

</databaseChangeLog>
```

### Properties File Example (liquibase.properties)

```properties
# Database Connection
changelog-file=changelogs/master.xml
url=jdbc:postgresql://postgres:5432/mydb
username=dbuser
password=dbpass
driver=org.postgresql.Driver

# Liquibase Settings
log-level=INFO
contexts=dev,test
labels=core,migration

# Changelog Parameters
property.schema.name=public
property.table.prefix=app_
```

## Running Liquibase

### Basic Pattern

```bash
# Pattern: docker-compose run --rm liquibase [COMMAND] [OPTIONS]
docker-compose run --rm liquibase --help
```

**Flags explained:**

- `--rm`: Remove container after execution (cleanup)
- `liquibase`: Service name from docker-compose.yml

### Using Properties File

```bash
# Create liquibase.properties in the liquibase directory
# Then run with defaults-file option
docker-compose run --rm liquibase \
  --defaults-file=/liquibase/liquibase.properties \
  update
```

### Using Command-Line Arguments

```bash
# All connection details on command line
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  update
```

### Environment-Specific Runs

```bash
# Use contexts to control which changes apply
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  --contexts=dev \
  update

# Use labels for fine-grained control
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  --labels="v1.0,critical" \
  update
```

## Common Operations

### 1. Check Status (What Will Be Applied)

```bash
# See pending changes
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  status --verbose

# Count pending changesets
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  status --verbose | grep -c "NOT RUN"
```

**Output example:**

```
3 changesets have not been applied to mydb@jdbc:postgresql://postgres:5432/mydb
     changelogs/v1.0/001-create-users-table.xml::1::john.doe
     changelogs/v1.0/002-create-orders-table.xml::1::john.doe
     changelogs/v1.0/003-add-indexes.xml::1::john.doe
```

### 2. Update (Apply Changes)

```bash
# Apply all pending changes
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  update

# Apply specific number of changes
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  update-count 2

# Apply changes up to a specific tag
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  update-to-tag v1.0
```

### 3. Preview Changes (Dry Run)

```bash
# Generate SQL without applying
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  update-sql

# Save SQL to file
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  update-sql > /tmp/migration.sql
```

### 4. Rollback Changes

```bash
# Rollback last N changes
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  rollback-count 1

# Rollback to a specific tag
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  rollback v1.0

# Rollback to a specific date
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  rollback-to-date "2025-01-01"

# Preview rollback SQL
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  rollback-count-sql 1
```

### 5. Tag Database State

```bash
# Create a tag (bookmark) at current state
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  tag v1.0-production
```

### 6. Diff Databases

```bash
# Compare two databases
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/source_db \
  --username=dbuser \
  --password=dbpass \
  --reference-url=jdbc:postgresql://postgres:5432/target_db \
  --reference-username=dbuser \
  --reference-password=dbpass \
  diff

# Generate changelog from diff
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/source_db \
  --username=dbuser \
  --password=dbpass \
  --reference-url=jdbc:postgresql://postgres:5432/target_db \
  --reference-username=dbuser \
  --reference-password=dbpass \
  diff-changelog \
  --changelog-file=generated-diff.xml
```

### 7. Validate Changelog

```bash
# Validate changelog syntax
docker-compose run --rm liquibase \
  --changelog-file=changelogs/master.xml \
  validate
```

### 8. Generate Documentation

```bash
# Generate database documentation
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  db-doc /liquibase/output/dbdoc
```

## Health Checks and Validation

### Pre-Migration Checks

```bash
# 1. Verify Liquibase version
docker-compose run --rm liquibase --version

# 2. Validate changelog syntax
docker-compose run --rm liquibase \
  --changelog-file=changelogs/master.xml \
  validate

# 3. Test database connectivity
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  status

# 4. Check pending changes
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  status --verbose

# 5. Generate and review SQL (dry run)
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  update-sql | tee /tmp/migration-preview.sql
```

### Post-Migration Validation

```bash
# 1. Verify all changes applied
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  status

# 2. Check DATABASECHANGELOG table
docker exec postgres psql -U dbuser -d mydb \
  -c "SELECT id, author, filename, exectype, dateexecuted FROM databasechangelog ORDER BY dateexecuted DESC LIMIT 10;"

# 3. Verify database objects created
docker exec postgres psql -U dbuser -d mydb \
  -c "\dt" # List tables

# 4. Check for errors in Liquibase logs
docker-compose logs liquibase | grep -i error
```

### Health Check Script

Create a health check script `healthcheck.sh`:

```bash
#!/bin/bash
# Liquibase Health Check Script

set -e

echo "=== Liquibase Health Check ==="

# Check 1: Liquibase version
echo "1. Checking Liquibase version..."
docker-compose run --rm liquibase --version || exit 1

# Check 2: Validate changelog
echo "2. Validating changelog..."
docker-compose run --rm liquibase \
  --changelog-file=changelogs/master.xml \
  validate || exit 1

# Check 3: Database connectivity
echo "3. Testing database connectivity..."
docker-compose run --rm liquibase \
  --defaults-file=/liquibase/liquibase.properties \
  status > /dev/null || exit 1

echo "=== All health checks passed ==="
```

## Monitoring and Logs

### View Liquibase Output

```bash
# Run with verbose logging
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  --log-level=DEBUG \
  update

# Capture output to file
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  update 2>&1 | tee liquibase-$(date +%Y%m%d-%H%M%S).log
```

### Check Database Changelog Tables

```bash
# PostgreSQL - View changelog history
docker exec postgres psql -U dbuser -d mydb -c \
  "SELECT * FROM databasechangelog ORDER BY dateexecuted DESC LIMIT 10;"

# SQL Server - View changelog history
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q \
  "SELECT TOP 10 * FROM DATABASECHANGELOG ORDER BY DATEEXECUTED DESC;"

# PostgreSQL - View lock status
docker exec postgres psql -U dbuser -d mydb -c \
  "SELECT * FROM databasechangeloglock;"
```

### Release Lock (If Stuck)

```bash
# If Liquibase crashes, the lock may remain
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  release-locks

# Verify lock is released
docker exec postgres psql -U dbuser -d mydb -c \
  "SELECT * FROM databasechangeloglock;"
```

## Best Practices

### 1. Changelog Management

✅ **DO:**

- Use version directories (v1.0/, v1.1/, v2.0/)
- Include descriptive filenames (001-create-users-table.xml)
- Use sequential numbering (001, 002, 003)
- Include author and ID in every changeset
- Use contexts and labels for environment-specific changes
- Keep changesets atomic (one logical change per changeset)

❌ **DON'T:**

- Modify changesets after they've been applied
- Use the same ID for different changesets
- Put unrelated changes in one changeset
- Hard-code environment-specific values

**Example changeset:**

```xml
<changeSet id="001" author="john.doe" context="all">
    <createTable tableName="users">
        <column name="id" type="bigint" autoIncrement="true">
            <constraints primaryKey="true" nullable="false"/>
        </column>
        <column name="username" type="varchar(50)">
            <constraints unique="true" nullable="false"/>
        </column>
        <column name="created_at" type="timestamp" defaultValueComputed="CURRENT_TIMESTAMP"/>
    </createTable>
    <rollback>
        <dropTable tableName="users"/>
    </rollback>
</changeSet>
```

### 2. Rollback Strategy

✅ **DO:**

- Define explicit rollback for each changeset
- Test rollback procedures in non-production first
- Tag database state before major releases
- Keep rollback procedures simple and fast

❌ **DON'T:**

- Rely on auto-generated rollback for data changes
- Rollback without testing first
- Skip rollback definitions

### 3. Database Connection Security

✅ **DO:**

- Use environment variables for credentials
- Use properties files for connection details
- Rotate database passwords regularly
- Use read-only accounts for diff/status operations

❌ **DON'T:**

- Hard-code passwords in changelogs or compose files
- Commit credentials to version control
- Use production credentials in development

**Secure properties file pattern:**

```bash
# Use environment variables in liquibase.properties
url=jdbc:postgresql://postgres:5432/mydb
username=${DB_USERNAME}
password=${DB_PASSWORD}

# Set environment variables
export DB_USERNAME=dbuser
export DB_PASSWORD=secure_password

# Or use .env file with docker-compose
docker-compose --env-file .env run --rm liquibase update
```

### 4. Testing and Validation

✅ **DO:**

- Always run `status` before `update`
- Use `update-sql` to preview changes
- Test migrations on dev/test databases first
- Validate changelogs before applying
- Keep backups before major migrations

❌ **DON'T:**

- Run migrations directly on production without testing
- Skip dry-run validation
- Ignore warnings or errors

### 5. Performance Optimization

✅ **DO:**

- Use batch inserts for data loads
- Create indexes after bulk data inserts
- Use contexts to skip unnecessary changes
- Monitor migration execution time

❌ **DON'T:**

- Run heavy data migrations during peak hours
- Create indexes before bulk inserts
- Include large data sets in changelogs

### 6. Operational Excellence

✅ **DO:**

- Document your changelog conventions
- Use consistent naming patterns
- Tag releases in changelog
- Keep migration logs
- Automate validation in CI/CD
- Set resource limits in docker-compose

❌ **DON'T:**

- Run migrations manually in production (use automation)
- Skip documentation
- Delete old changelogs

## Troubleshooting

### Issue: "Lock is held by another process"

**Cause:** Previous Liquibase run crashed without releasing lock

**Solution:**

```bash
# Release the lock
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  release-locks
```

### Issue: "Validation Failed: Checksum mismatch"

**Cause:** Changelog file was modified after being applied

**Solution:**

```bash
# Option 1: Clear checksums (not recommended for production)
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  clear-checksums

# Option 2: Revert changelog to original state (recommended)
git checkout HEAD -- changelogs/problematic-file.xml
```

### Issue: "Connection refused" to database

**Cause:** Database not accessible from Liquibase container

**Solutions:**

```bash
# Check if database is running
docker ps | grep postgres

# Check network connectivity
docker-compose run --rm liquibase ping postgres

# Check if on same network
docker network inspect dbtools-network

# Use host.docker.internal for host databases
--url=jdbc:postgresql://host.docker.internal:5432/mydb
```

### Issue: "Driver not found"

**Cause:** JDBC driver not available in image

**Solution:**

```bash
# Verify driver exists in image
docker run --rm liquibase:5.0.1 ls -l /opt/liquibase/lib/

# If missing, rebuild image or add driver manually
docker-compose build --no-cache
```

### Issue: Out of Memory errors

**Cause:** Large migrations consuming too much memory

**Solution:**

```bash
# Increase memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G

# Or run with Java heap settings
docker-compose run --rm \
  -e JAVA_OPTS="-Xmx2g" \
  liquibase update
```

## Command Reference

### Essential Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `update` | Apply all pending changes | `liquibase update` |
| `update-count N` | Apply N changes | `liquibase update-count 5` |
| `update-sql` | Generate SQL without applying | `liquibase update-sql` |
| `status` | Show pending changes | `liquibase status --verbose` |
| `rollback TAG` | Rollback to tag | `liquibase rollback v1.0` |
| `rollback-count N` | Rollback N changes | `liquibase rollback-count 1` |
| `tag NAME` | Tag current state | `liquibase tag v1.0-prod` |
| `validate` | Validate changelog | `liquibase validate` |
| `diff` | Compare databases | `liquibase diff` |
| `release-locks` | Release stuck lock | `liquibase release-locks` |

### Docker Commands

```bash
# Build image
docker-compose build

# Rebuild without cache
docker-compose build --no-cache

# Check image size
docker images liquibase

# Run with custom command
docker-compose run --rm liquibase [COMMAND]

# Run with environment variables
docker-compose run --rm -e DB_PASSWORD=secret liquibase update

# View container logs (if run with -d)
docker-compose logs -f liquibase

# Remove stopped containers
docker-compose down

# Clean up everything
docker-compose down -v
docker rmi liquibase:5.0.1
```

### Database-Specific Connection Examples

**PostgreSQL:**

```bash
docker-compose run --rm liquibase \
  --url=jdbc:postgresql://postgres:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=changelogs/master.xml \
  update
```

**SQL Server:**

```bash
docker-compose run --rm liquibase \
  --url="jdbc:sqlserver://mssql1:1433;databaseName=mydb;encrypt=true;trustServerCertificate=true" \
  --username=SA \
  --password='YourStrong!Passw0rd' \
  --changelog-file=changelogs/master.xml \
  update
```

**Snowflake:**

```bash
docker-compose run --rm liquibase \
  --url="jdbc:snowflake://account.snowflakecomputing.com/?db=mydb&warehouse=compute_wh" \
  --username=snowuser \
  --password=snowpass \
  --changelog-file=changelogs/master.xml \
  update
```

**MongoDB:**

```bash
docker-compose run --rm liquibase \
  --url=jdbc:mongodb://mongodb1:27017/mydb \
  --username=mongouser \
  --password=mongopass \
  --changelog-file=changelogs/master.xml \
  update
```

## Additional Resources

- [Liquibase Official Documentation](https://docs.liquibase.com/)
- [Best Practices](https://docs.liquibase.com/concepts/bestpractices.html)
- [Changelog Formats](https://docs.liquibase.com/concepts/changelogs/home.html)
- [Database Tutorials](https://docs.liquibase.com/workflows/database-setup-tutorials/home.html)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## Quick Reference Card

```bash
# Most common workflow:

# 1. Check what will be applied
docker-compose run --rm liquibase --defaults-file=/liquibase/liquibase.properties status

# 2. Preview the SQL
docker-compose run --rm liquibase --defaults-file=/liquibase/liquibase.properties update-sql

# 3. Apply changes
docker-compose run --rm liquibase --defaults-file=/liquibase/liquibase.properties update

# 4. Tag the release
docker-compose run --rm liquibase --defaults-file=/liquibase/liquibase.properties tag v1.0

# If something goes wrong:
docker-compose run --rm liquibase --defaults-file=/liquibase/liquibase.properties rollback v1.0
```

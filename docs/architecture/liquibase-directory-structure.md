# Liquibase Architecture

## Overview

This repository uses Liquibase for database schema management across multiple platforms (PostgreSQL, SQL Server, Snowflake, MongoDB) with multiple databases per platform. Changes are written once and promoted through environments (dev → stage → prod) using environment-specific connection properties.

## Directory Structure

```
liquibase/changelogs/
  env/                                 # properties templates (no secrets)
    liquibase.dev.properties.template
    liquibase.stage.properties.template
    liquibase.prod.properties.template
  shared/
    modules/                           # reusable, db-agnostic modules
    data/reference/                    # CSVs for loadData
  platforms/
    postgres/
      databases/
        app/
          db.changelog-master.yaml
          baseline/
            db.changelog-baseline.yaml
          releases/
            1.0/
              db.changelog-1.0.yaml
              001-create-tables.yaml
              002-add-indexes.yaml
        analytics/
          db.changelog-master.yaml
          releases/1.0/...
    mssql/
      databases/
        erp/
          db.changelog-master.yaml
          releases/1.0/...
    snowflake/
      databases/
        datawarehouse/
          db.changelog-master.yaml
          releases/1.0/...
    mongodb/
      databases/
```

## Design Principles

### Single Source of Truth

- SQL changes are written **once** in YAML/XML changelogs
- Same changelog files deploy to dev, stage, and prod
- Environment differences handled via properties files, not duplicate SQL
- Version control tracks all schema evolution

### Platform Separation

- Each database platform gets its own folder under `platforms/`
- Platform-specific SQL isolated using `dbms` attribute when needed
- Common patterns extracted to `shared/modules/` when db-agnostic

### Database Independence

- Each database gets its own master changelog
- Databases within a platform are independent units
- Shared modules can be included across databases

### Release-Driven Versioning

- Changes organized into `releases/<version>/` folders
- Each release ends with a `tagDatabase` for rollback points
- Numbered files within releases ensure deterministic order

## Conventions

### Changelog Organization

**Master File**: Each database has one `db.changelog-master.yaml` that includes baseline (if needed) and release changelogs in order:

```yaml
databaseChangeLog:
  - preConditions:
      - runningAs:
          username: "*"
  # Include baseline for new databases
  - include:
      file: baseline/db.changelog-baseline.yaml
  - tagDatabase:
      tag: baseline
  # Incremental releases build on baseline
  - include:
      file: releases/1.0/db.changelog-1.0.yaml
  - tagDatabase:
      tag: v1.0
  - include:
      file: releases/1.1/db.changelog-1.1.yaml
  - tagDatabase:
      tag: v1.1
```

**Release Changelog**: Each release has a changelog that includes numbered changes:

```yaml
databaseChangeLog:
  - include:
      file: 001-create-core-tables.yaml
  - include:
      file: 002-add-indexes.yaml
  - include:
      file: 003-seed-reference-data.yaml
```

**ChangeSet Files**: Individual changes with rollback:

```yaml
databaseChangeLog:
  - changeSet:
      id: 20251113-01-create-users
      author: team
      changes:
        - createTable:
            tableName: users
            columns:
              - column:
                  name: id
                  type: bigserial
                  constraints:
                    primaryKey: true
              - column:
                  name: email
                  type: varchar(255)
      rollback:
        - dropTable:
            tableName: users
```

### Baseline Management

**What is a Baseline?**

A baseline is an initial schema snapshot that captures the existing database state before Liquibase management begins. It's **not** the same as release 1.0.

- **Baseline**: Initial schema snapshot (tables, indexes, constraints already in production)
- **Release 1.0**: First incremental changes *after* baseline is established

**Directory Structure**:

```
platforms/<platform>/databases/<db>/
  baseline/
    db.changelog-baseline.yaml       # Initial schema snapshot
    001-baseline-tables.yaml         # Or split into logical chunks
    002-baseline-indexes.yaml
  releases/
    1.0/                             # First incremental release
      001-add-new-feature.yaml
```

**When to Use Baselines**:

1. **Existing production database**: Use baseline to capture current state before adding Liquibase
2. **New database**: Skip baseline; start directly with `releases/1.0/`
3. **Migration from manual scripts**: Baseline represents all pre-Liquibase schema

**Creating a Baseline**:

```bash
# Generate baseline from existing database
liquibase \
  --defaults-file=liquibase/changelogs/env/liquibase.prod.properties \
  --changelog-file=liquibase/changelogs/platforms/postgres/databases/app/baseline/db.changelog-baseline.yaml \
  generateChangeLog
```

**Applying Baseline to Existing Database**:

For databases that already have the baseline schema, mark it as executed without running:

```bash
# Sync baseline (don't actually run the DDL)
liquibase \
  --defaults-file=liquibase/changelogs/env/liquibase.prod.properties \
  --changelog-file=liquibase/changelogs/platforms/postgres/databases/app/baseline/db.changelog-baseline.yaml \
  changelogSync

# Tag it
liquibase \
  --defaults-file=liquibase/changelogs/env/liquibase.prod.properties \
  --changelog-file=liquibase/changelogs/platforms/postgres/databases/app/db.changelog-master.yaml \
  tag baseline
```

**Applying to New Environments**:

For fresh dev/test databases, baseline runs normally:

```bash
# New database gets full baseline + releases
liquibase \
  --defaults-file=liquibase/changelogs/env/liquibase.dev.properties \
  --changelog-file=liquibase/changelogs/platforms/postgres/databases/app/db.changelog-master.yaml \
  update
```

**Master Changelog with Baseline**:

```yaml
databaseChangeLog:
  # Baseline comes first
  - include:
      file: baseline/db.changelog-baseline.yaml
  - tagDatabase:
      tag: baseline

  # Then incremental releases
  - include:
      file: releases/1.0/db.changelog-1.0.yaml
  - tagDatabase:
      tag: v1.0
```

**Without Baseline** (new database from scratch):

```yaml
databaseChangeLog:
  # No baseline; start directly with releases
  - include:
      file: releases/1.0/db.changelog-1.0.yaml
  - tagDatabase:
      tag: v1.0
```

### ChangeSet Best Practices

1. **Unique IDs**: Use format `YYYYMMDD-NN-description` (e.g., `20251113-01-add-user-table`)
2. **Author**: Include team/person for traceability
3. **Granularity**: One logical change per changeSet (one table, one index, etc.)
4. **Rollback**: Always provide explicit rollback for production safety
5. **Idempotency**: Use preconditions when needed to safely re-run

### Contexts and Labels

- **Minimize use**: Keep schema changes environment-agnostic
- **Data seeds only**: Use `context: dev` for dev-only test data
- **Labels for filtering**: `labels: 'db:app,platform:postgres'` for multi-DB deployments

### Platform-Specific Changes

Use `dbms` attribute for small platform deltas:

```yaml
- changeSet:
    id: 20251113-02-add-json-column
    author: team
    dbms: postgresql
    changes:
      - addColumn:
          tableName: config
          columns:
            - column:
                name: settings
                type: jsonb
```

For larger platform divergence, keep changes in separate files under each platform folder.

### Shared Modules

Reusable patterns go in `shared/modules/`:

```yaml
# shared/modules/audit/db.changelog-audit.yaml
databaseChangeLog:
  - changeSet:
      id: audit-001-create-audit-table
      author: platform-team
      changes:
        - createTable:
            tableName: audit_log
            columns:
              - column:
                  name: id
                  type: bigserial
                  constraints:
                    primaryKey: true
              - column:
                  name: timestamp
                  type: timestamp
                  defaultValueComputed: CURRENT_TIMESTAMP
```

Include from any database master:

```yaml
  - include:
      file: ../../shared/modules/audit/db.changelog-audit.yaml
```

### Reference Data

Store CSVs in `shared/data/reference/` and load with `loadData`:

```yaml
- changeSet:
    id: 20251113-03-load-countries
    author: team
    changes:
      - loadData:
          file: ../../shared/data/reference/countries.csv
          tableName: countries
```

## Environment Management

### Properties Files

Each environment has a properties file with connection details:

```properties
# liquibase/changelogs/env/liquibase.dev.properties
url=jdbc:postgresql://dev-db.example.com:5432/app
username=${DB_USER}
password=${DB_PASSWORD}
logLevel=info
```

**Security**:

- Keep `.properties.template` files in VCS as examples
- Actual `.properties` files should be `.gitignore`d or use CI/CD secrets
- Use environment variables for credentials

### Promotion Workflow

Same changelog, different properties:

```bash
# Dev
liquibase --defaults-file env/liquibase.dev.properties \
  --changelog-file platforms/postgres/databases/app/db.changelog-master.yaml update

# Stage
liquibase --defaults-file env/liquibase.stage.properties \
  --changelog-file platforms/postgres/databases/app/db.changelog-master.yaml update

# Prod
liquibase --defaults-file env/liquibase.prod.properties \
  --changelog-file platforms/postgres/databases/app/db.changelog-master.yaml update
```

## Execution Patterns

### Dry-Run Validation

Always validate before applying:

```bash
liquibase \
  --defaults-file liquibase/changelogs/env/liquibase.dev.properties \
  --changelog-file liquibase/changelogs/platforms/postgres/databases/app/db.changelog-master.yaml \
  updateSQL
```

### Single Database Deployment

```bash
liquibase \
  --defaults-file liquibase/changelogs/env/liquibase.dev.properties \
  --changelog-file liquibase/changelogs/platforms/postgres/databases/app/db.changelog-master.yaml \
  update
```

### Multi-Database Platform Deployment

Loop through all databases for a platform:

```bash
set -euo pipefail
platform=postgres
for db in app analytics; do
  cf="liquibase/changelogs/platforms/$platform/databases/$db/db.changelog-master.yaml"

  # Validate
  liquibase --defaults-file liquibase/changelogs/env/liquibase.dev.properties \
    --changelog-file "$cf" updateSQL >/dev/null

  # Apply
  liquibase --defaults-file liquibase/changelogs/env/liquibase.dev.properties \
    --changelog-file "$cf" update
done
```

### Multi-Environment Promotion

Promote through all environments sequentially:

```bash
set -euo pipefail
platform=postgres
db=app
cf="liquibase/changelogs/platforms/$platform/databases/$db/db.changelog-master.yaml"

for env in dev stage prod; do
  echo "Deploying to $env..."
  liquibase --defaults-file "liquibase/changelogs/env/liquibase.$env.properties" \
    --changelog-file "$cf" update
done
```

### CI/CD Pipeline Example

```bash
#!/bin/bash
set -euo pipefail

# Deploy all databases across all environments
for platform in postgres mssql snowflake; do
  for db_dir in liquibase/changelogs/platforms/$platform/databases/*; do
    db=$(basename "$db_dir")
    cf="$db_dir/db.changelog-master.yaml"

    if [[ ! -f "$cf" ]]; then
      continue
    fi

    echo "=== Deploying $platform/$db ==="

    # Validate
    liquibase --defaults-file liquibase/changelogs/env/liquibase.dev.properties \
      --changelog-file "$cf" validate

    # Preview
    liquibase --defaults-file liquibase/changelogs/env/liquibase.dev.properties \
      --changelog-file "$cf" updateSQL > /tmp/preview.sql

    # Apply dev
    liquibase --defaults-file liquibase/changelogs/env/liquibase.dev.properties \
      --changelog-file "$cf" update

    # Apply stage (after approval)
    liquibase --defaults-file liquibase/changelogs/env/liquibase.stage.properties \
      --changelog-file "$cf" update

    # Apply prod (after approval)
    liquibase --defaults-file liquibase/changelogs/env/liquibase.prod.properties \
      --changelog-file "$cf" update
  done
done
```

## Rollback Strategy

### Using Tags

Roll back to a specific release:

```bash
liquibase --defaults-file env/liquibase.prod.properties \
  --changelog-file platforms/postgres/databases/app/db.changelog-master.yaml \
  rollback v1.0
```

### Using Count

Roll back last N changeSets:

```bash
liquibase --defaults-file env/liquibase.prod.properties \
  --changelog-file platforms/postgres/databases/app/db.changelog-master.yaml \
  rollbackCount 3
```

### Using Date

Roll back to a timestamp:

```bash
liquibase --defaults-file env/liquibase.prod.properties \
  --changelog-file platforms/postgres/databases/app/db.changelog-master.yaml \
  rollbackToDate 2025-11-13
```

## Common Patterns

### Database Splits/Consolidation

When splitting a monolith into microservices:

1. Create new database folder: `platforms/postgres/databases/orders/`
2. Extract relevant changeSets from old master
3. Update includes in both masters to avoid duplication
4. Use preconditions to gate execution

### Zero-Downtime Migrations

1. **Add nullable column** → deploy → backfill → add constraint
2. **Rename column** → add new → dual-write → migrate → drop old
3. **Split table** → add new → dual-write → migrate → drop old

Use multiple releases with tags between steps for safe rollback.

## Troubleshooting

### Lock Issues

```bash
# Release stuck lock
liquibase --defaults-file env/liquibase.dev.properties releaseLocks
```

### Checksum Mismatches

When changeSet edited after deployment:

```bash
# Clear checksums (use with caution)
liquibase --defaults-file env/liquibase.dev.properties clearCheckSums
```

Better: never edit deployed changeSets; create new ones.

### Manual Interventions

Mark changeSets as executed without running:

```bash
liquibase --defaults-file env/liquibase.prod.properties \
  changelogSync
```

## References

- [Liquibase Documentation](https://docs.liquibase.com/)
- [Best Practices](https://www.liquibase.org/get-started/best-practices)
- Internal: `liquibase/changelogs/README.md` for quick start

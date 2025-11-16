# Liquibase Implementation Guide

> **Document Version:** 2.0
> **Last Updated:** November 16, 2025
> **Maintainers:** Global Data Services Team
> **Status:** Production - Actively Maintained

![Liquibase Version](https://img.shields.io/badge/Liquibase-4.24%2B-blue)
![Document Status](https://img.shields.io/badge/Status-Production-green)

## Overview

This repository uses Liquibase for database schema management across multiple platforms (PostgreSQL, SQL Server, Snowflake, MongoDB) with multiple databases per platform. Changes are written once and promoted through environments (dev → stage → prod) using environment-specific connection properties.

**This structure is designed for:**

- ✅ Organizations managing 3+ database platforms
- ✅ Multiple databases per platform (microservices architecture)
- ✅ Centralized change management with platform teams
- ✅ Shared infrastructure and deployment pipelines
- ✅ Medium to large enterprises (10+ databases)

**Consider alternatives if:**

- ❌ Single platform with 1-2 databases (simpler structure needed)
- ❌ Fully independent microservice teams (separate repositories may be better)
- ❌ Platform-specific tooling required (e.g., Flyway for Java-only shops)
- ❌ Small team managing < 5 databases total

## Liquibase Community vs Liquibase Secure

This architecture (directory structure, naming, promotion, CI/CD) works with both **Liquibase Community** (free, open-source) and **Liquibase Secure** (commercial). Key differences relate to stored logic, governance, and workflow automation.

### Core DDL Objects (Both Editions)

- ✅ Tables, views, indexes, constraints, foreign keys, sequences
- ✅ Primary keys, unique constraints, foreign keys
- ✅ Columns, data types, schemas referenced via `schemaName` (with `--include-schema=true`)

### Stored Logic Objects (Differences)

**Liquibase Community:**

- ⚠️ Limited support for procedures, functions, triggers, check constraints, packages
- Can detect and reference these objects during `generateChangeLog`
- Does not emit dedicated change types (e.g., `createFunction`, `createTrigger`)
- Requires manual SQL-based changeSets to manage stored logic
- No automated extraction into separate SQL files

**Liquibase Secure:**

- ✅ Automated extraction of procedures, functions, triggers, check constraints, packages
- Generates `pro:` namespaced change types (e.g., `pro:createFunction`, `pro:createTrigger`)
- Creates an `objects/` directory with separate SQL files per object
- Supports `--diff-types` like `functions`, `storedprocedures`, `triggers`, `checkconstraints`
- Improves accuracy and velocity for teams with significant stored logic

Recommendation: If your platforms rely heavily on stored logic, **Liquibase Secure** materially reduces manual effort and drift risk.

## Liquibase Limitations

**Important**: Liquibase has some fundamental limitations that apply to ALL editions (Community and Secure):

### Schema Management

Liquibase **does not manage database schemas**. From the [official Liquibase documentation](https://docs.liquibase.com/commands/inspection/generate-changelog.html):

> "*When using the update command to apply the changes in the changelog, Liquibase will not create a new database or schema. You must create them before applying the changelog to it.*"

Key points:

- ❌ `generateChangeLog` will NOT create `CREATE SCHEMA` statements
- ❌ The Schema object type has "N/A" for `--diff-types` syntax (no parameter exists to capture schemas)
- ⚠️ **Schemas must exist before running Liquibase** - create them manually or through other tooling
- ✅ Liquibase WILL include `schemaName` attributes on tables/views (when using `--include-schema=true`)
- ✅ Liquibase CAN detect schema drift (missing/unexpected/changed schemas) via `diff` and `diffChangeLog` commands, but won't auto-generate creation statements

**In production**: You should:

- Create schemas manually before first Liquibase deployment
- Use database initialization scripts run before Liquibase
- Include schema creation in your infrastructure-as-code (Terraform, ARM templates, etc.)

Example: model schema creation via SQL changeSets (works across editions):

```yaml
databaseChangeLog:
  - changeSet:
      id: 20251116-01-create-schema
      author: platform-team
      changes:
        - sql:
            sql: |
              CREATE SCHEMA IF NOT EXISTS app_schema;
      rollback:
        - sql:
            sql: |
              DROP SCHEMA IF EXISTS app_schema CASCADE;
```

Example: model schema creation via SQL changeSets (works across editions):

```yaml
databaseChangeLog:
  - changeSet:
      id: 20251116-01-create-schema
      author: platform-team
      changes:
        - sql:
            sql: |
              CREATE SCHEMA IF NOT EXISTS app_schema;
      rollback:
        - sql:
            sql: |
              DROP SCHEMA IF EXISTS app_schema CASCADE;
```

### Other Limitations

- ❌ **Database users, roles, permissions** - Security objects are not captured
- ❌ **Extended properties and descriptions** - SQL Server metadata is not captured
- ❌ **Computed columns** - May be captured incorrectly or not at all
- ℹ️ **Stored procedures, functions, triggers** - Limited in Community; automated in Liquibase Secure

## Table of Contents

- [Overview](#overview)
- [Liquibase Community vs Liquibase Secure](#liquibase-community-vs-liquibase-secure)
- [Liquibase Limitations](#liquibase-limitations)
- [Directory Structure](#directory-structure)
- [Design Principles](#design-principles)
- [Conventions](#conventions)
- [Naming Conventions](#naming-conventions)
- [Baseline Management](#baseline-management)
- [ChangeSet Best Practices](#changeset-best-practices)
- [Contexts and Labels](#contexts-and-labels)
- [Platform-Specific Changes](#platform-specific-changes)
- [Shared Modules](#shared-modules)
- [Reference Data](#reference-data)
- [Environment Management](#environment-management)
- [Execution Patterns](#execution-patterns)
- [Docker Execution](#docker-execution)
- [Rollback Strategy](#rollback-strategy)
- [Scalability and Performance](#scalability-and-performance)
- [Common Patterns](#common-patterns)
- [Edition Differences](#edition-differences)
- [Alternative Approaches](#alternative-approaches)
- [Testing Strategy](#testing-strategy)
- [Migration from Legacy](#migration-from-legacy)
- [Troubleshooting](#troubleshooting)
- [References](#references)
- [Glossary](#glossary)

## Directory Structure

Canonical root for changelogs: `/data/liquibase` (host and container). Keeping the same absolute path inside the container avoids path translation issues.

```text
/data/liquibase/
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
        catalog/
          db.changelog-master.yaml
          releases/
            1.0/
              db.changelog-1.0.yaml
              001-create-collections.yaml
              002-create-indexes.yaml
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

## Naming Conventions

### Platform Names

Use lowercase, hyphen-separated names matching your database technology:

```text
platforms/
  postgres/          # PostgreSQL
  mssql/            # Microsoft SQL Server
  mysql/            # MySQL
  oracle/           # Oracle Database
  snowflake/        # Snowflake Data Warehouse
  mongodb/          # MongoDB
  cassandra/        # Apache Cassandra
  dynamodb/         # AWS DynamoDB
```

**Guidelines:**

- Use official product name (lowercase)
- Avoid abbreviations unless universally recognized
- Be consistent across all documentation

### Database Names

Use lowercase, hyphen-separated names matching your logical database/schema:

```text
platforms/postgres/databases/
  customer-service/      # Microservice: customer domain
  order-management/      # Microservice: order domain
  analytics/            # Data warehouse
  reporting/            # Reporting database
  shared-reference/     # Shared reference data
```

**Guidelines:**

- Match your microservice/application name
- Use domain-driven design terminology
- Avoid technical jargon (e.g., `db1`, `prod_db`)
- Keep names under 30 characters for path readability

### File Naming

**Master Changelogs:**

```text
db.changelog-master.yaml        # Standard name (consistent across all databases)
```

**Release Changelogs:**

```text
releases/
  1.0/
    db.changelog-1.0.yaml       # Release aggregator
  1.1/
    db.changelog-1.1.yaml
  2.0/
    db.changelog-2.0.yaml
```

**Individual Changesets:**

Use format: `NNN-verb-noun-detail.{yaml,sql,xml}`

```text
001-create-customers-table.yaml
002-add-email-index.yaml
003-create-orders-view.sql
004-add-audit-trigger.sql
005-seed-countries-reference-data.yaml
010-alter-customer-email-length.yaml      # Leave gaps for insertions
```

**Changeset IDs:**

Use format: `YYYYMMDD-NN-description`

```yaml
changeSet:
  id: 20251114-01-create-customers-table   # Date + sequence + description
  id: 20251114-02-add-email-index
  id: 20251115-01-create-orders-view
```

**Why this format?**

- **Chronological ordering**: Sorts naturally by date
- **Uniqueness**: Date + sequence prevents collisions
- **Readability**: Description makes intent clear
- **Traceability**: Easy to correlate with JIRA tickets, PRs

**Baseline Files:**

```text
baseline/
  db.changelog-baseline.yaml                    # Main baseline
  db.changelog-baseline-2025-11-14.yaml        # Dated snapshot (for review)
  001-baseline-schemas.yaml                    # Logical split
  002-baseline-tables.yaml
  003-baseline-indexes.yaml
  004-baseline-views.yaml
  005-baseline-procedures.yaml
```

### Properties Files

```text
env/
  liquibase.dev.properties.template
  liquibase.stage.properties.template
  liquibase.prod.properties.template
  liquibase.{platform}.{database}.{env}.properties    # For complex setups
```

**Examples of complex naming:**

```text
env/
  liquibase.postgres.customer.dev.properties
  liquibase.postgres.customer.prod.properties
  liquibase.mssql.erp.dev.properties
```

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

```text
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
# NOTE: If the target file exists, Liquibase will overwrite it.
# Prefer generating to a new, dated file for review before renaming.
liquibase \
  --defaults-file=/data/liquibase/env/liquibase.prod.properties \
  --changelog-file=/data/liquibase/platforms/postgres/databases/app/baseline/db.changelog-baseline-2025-11-14.yaml \
  generateChangeLog
```

**Applying Baseline to Existing Database**:

For databases that already have the baseline schema, mark it as executed without running:

```bash
# Sync baseline (don't actually run the DDL)
liquibase \
  --defaults-file=/data/liquibase/env/liquibase.prod.properties \
  --changelog-file=/data/liquibase/platforms/postgres/databases/app/baseline/db.changelog-baseline.yaml \
  changelogSync

# Tag it
liquibase \
  --defaults-file=/data/liquibase/env/liquibase.prod.properties \
  --changelog-file=/data/liquibase/platforms/postgres/databases/app/db.changelog-master.yaml \
  tag baseline
```

**Applying to New Environments**:

For fresh dev/test databases, baseline runs normally:

```bash
# New database gets full baseline + releases
liquibase \
  --defaults-file=/data/liquibase/env/liquibase.dev.properties \
  --changelog-file=/data/liquibase/platforms/postgres/databases/app/db.changelog-master.yaml \
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

Examples:

```yaml
databaseChangeLog:
  - changeSet:
      id: 20251114-01-seed-dev-data
      author: team
      context: dev
      changes:
        - loadData:
            file: ../../shared/data/reference/sample_users.csv
            tableName: users

  - changeSet:
      id: 20251114-02-add-index-app
      author: team
      labels: 'platform:postgres,db:app'
      changes:
        - createIndex:
            tableName: users
            indexName: idx_users_email
            columns:
              - column:
                  name: email
```

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

#### MongoDB-Specific Patterns

MongoDB uses extension change types for collections, indexes, and validation schemas.

```yaml
databaseChangeLog:
  - changeSet:
      id: 20251116-01-create-collection
      author: team
      changes:
        - ext:createCollection:
            collectionName: users
        - ext:createIndex:
            collectionName: users
            keys:
              - key: email
                order: 1
            options:
              unique: true
              name: idx_email_unique
```

Considerations:

- Use the `ext:` namespace for MongoDB extension types
- Manage validation rules with JSON schema changeSets
- Document sharding/topology; avoid automating cluster-level ops in migrations

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
# /data/liquibase/env/liquibase.dev.properties
url=jdbc:postgresql://dev-db.example.com:5432/app
username=${DB_USER}
password=${DB_PASSWORD}
logLevel=info
```

**Security**:

- Keep `.properties.template` files in VCS as examples
- Actual `.properties` files should be `.gitignore`d or use CI/CD secrets
- Use environment variables for credentials (e.g., `DB_USER`, `DB_PASSWORD`)
- Prefer secret managers (e.g., HashiCorp Vault, AWS Secrets Manager, Azure Key Vault) in CI/CD
- Example `.gitignore` additions:

  ```gitignore
  /data/liquibase/**/*.properties
  !/data/liquibase/**/*.properties.template
  ```

- Export environment variables at runtime:

  ```bash
  export DB_USER=app_user
  export DB_PASSWORD='s3cr3t'
  ```

### Promotion Workflow

Same changelog, different properties:

```bash
# Dev
liquibase --defaults-file /data/liquibase/env/liquibase.dev.properties \
  --changelog-file /data/liquibase/platforms/postgres/databases/app/db.changelog-master.yaml update

# Stage
liquibase --defaults-file /data/liquibase/env/liquibase.stage.properties \
  --changelog-file /data/liquibase/platforms/postgres/databases/app/db.changelog-master.yaml update

# Prod
liquibase --defaults-file /data/liquibase/env/liquibase.prod.properties \
  --changelog-file /data/liquibase/platforms/postgres/databases/app/db.changelog-master.yaml update
```

## Execution Patterns

### Dry-Run Validation

Always validate before applying:

```bash
liquibase \
  --defaults-file /data/liquibase/env/liquibase.dev.properties \
  --changelog-file /data/liquibase/platforms/postgres/databases/app/db.changelog-master.yaml \
  updateSQL
```

### Single Database Deployment

```bash
liquibase \
  --defaults-file /data/liquibase/env/liquibase.dev.properties \
  --changelog-file /data/liquibase/platforms/postgres/databases/app/db.changelog-master.yaml \
  update
```

### Multi-Database Platform Deployment

Loop through all databases for a platform:

```bash
set -euo pipefail
platform=postgres
for db in app analytics; do
  cf="/data/liquibase/platforms/$platform/databases/$db/db.changelog-master.yaml"

  # Validate
  liquibase --defaults-file /data/liquibase/env/liquibase.dev.properties \
    --changelog-file "$cf" updateSQL >/dev/null

  # Apply
  liquibase --defaults-file /data/liquibase/env/liquibase.dev.properties \
    --changelog-file "$cf" update
done
```

### Flow Files (Liquibase Secure)

Liquibase Secure supports flow files to orchestrate multi-stage deployments with quality gates and audit capture.

```yaml
# liquibase.flowfile.yaml
stages:
  - stage:
      name: validate-changes
      actions:
        - type: liquibase
          command: validate
        - type: liquibase
          command: updateSQL

  - stage:
      name: quality-checks
      actions:
        - type: liquibase
          command: checks run

  - stage:
      name: deploy
      actions:
        - type: liquibase
          command: update
        - type: liquibase
          command: tag
          tag: v${VERSION}
```

Benefits:

- Reusable deployment workflows with gates
- Automatic rollback script capture
- Built-in audit trail and conditional logic

### Multi-Environment Promotion

Promote through all environments sequentially:

```bash
set -euo pipefail
platform=postgres
db=app
cf="/data/liquibase/platforms/$platform/databases/$db/db.changelog-master.yaml"

for env in dev stage prod; do
  echo "Deploying to $env..."
  liquibase --defaults-file "/data/liquibase/env/liquibase.$env.properties" \
    --changelog-file "$cf" update
done
```

### CI/CD Pipeline Example

```bash
#!/bin/bash
set -euo pipefail

# Deploy all databases across all environments
for platform in postgres mssql snowflake; do
  for db_dir in /data/liquibase/platforms/$platform/databases/*; do
    db=$(basename "$db_dir")
    cf="$db_dir/db.changelog-master.yaml"

    if [[ ! -f "$cf" ]]; then
      continue
    fi

    echo "=== Deploying $platform/$db ==="

    # Validate
    liquibase --defaults-file /data/liquibase/env/liquibase.dev.properties \
      --changelog-file "$cf" validate

    # Preview
    liquibase --defaults-file /data/liquibase/env/liquibase.dev.properties \
      --changelog-file "$cf" updateSQL > /tmp/preview.sql

    # Apply dev
    liquibase --defaults-file /data/liquibase/env/liquibase.dev.properties \
      --changelog-file "$cf" update

    # Apply stage (after approval)
    liquibase --defaults-file /data/liquibase/env/liquibase.stage.properties \
      --changelog-file "$cf" update

    # Apply prod (after approval)
    liquibase --defaults-file /data/liquibase/env/liquibase.prod.properties \
      --changelog-file "$cf" update
  done
done
```

### Additional Validation

Validate changelog structure and connectivity without applying changes:

```bash
liquibase \
  --defaults-file /data/liquibase/env/liquibase.dev.properties \
  --changelog-file /data/liquibase/platforms/postgres/databases/app/db.changelog-master.yaml \
  validate
```

Preview the SQL to be executed for audit/approval:

```bash
liquibase \
  --defaults-file /data/liquibase/env/liquibase.dev.properties \
  --changelog-file /data/liquibase/platforms/postgres/databases/app/db.changelog-master.yaml \
  updateSQL > /tmp/preview.sql
```

Generate SQL to sync the DATABASECHANGELOG table (no DDL executed):

```bash
liquibase \
  --defaults-file /data/liquibase/env/liquibase.dev.properties \
  --changelog-file /data/liquibase/platforms/postgres/databases/app/db.changelog-master.yaml \
  changelogSyncSQL > /tmp/sync.sql
```

## Docker Execution

Run Liquibase in Docker while keeping paths consistent by mounting host `/data/liquibase` into the container at the same path:

```bash
docker run --rm \
  --network tool-library-network \
  -v /data/liquibase:/data/liquibase:ro \
  liquibase:latest \
  --defaults-file /data/liquibase/env/liquibase.dev.properties \
  --changelog-file /data/liquibase/platforms/postgres/databases/app/db.changelog-master.yaml \
  update
```

If you prefer using a different working directory inside the container (e.g., `/liquibase`), mount accordingly and adjust paths in commands.

With Docker Compose, ensure the volume mount points to `/data/liquibase`:

```yaml
services:
  liquibase:
    image: liquibase:latest
    volumes:
      - /data/liquibase:/data/liquibase:ro
    working_dir: /data/liquibase
    networks:
      - tool-library-network
```

This keeps examples in this document valid both on host and in container.

## Drift Detection (diffChangeLog)

Detect drift between two environments and generate a changelog capturing differences:

```bash
liquibase \
  --defaults-file /data/liquibase/env/liquibase.stage.properties \
  --changelog-file /data/liquibase/platforms/postgres/databases/app/drift/db.changelog-drift-2025-11-14.yaml \
  diffChangeLog \
  --referenceUrl="${DEV_JDBC_URL}" \
  --referenceUsername="${DEV_DB_USER}" \
  --referencePassword="${DEV_DB_PASSWORD}"
```

Best practice: review and curate generated drift changelogs; do not auto-apply without code review.

### Liquibase Secure Drift Capabilities

With Liquibase Secure you can enable:

- Automated drift reports (scheduled scans and dashboards)
- Drift alerts integrated with monitoring systems
- Reconciliation workflows (automated/manual)
- Policy enforcement to block out-of-band changes

See: <https://docs.liquibase.com/secure/user-guide-5-0/what-is-the-drift-report>

## Rollback Strategy

### Using Tags

Roll back to a specific release:

```bash
liquibase --defaults-file /data/liquibase/env/liquibase.prod.properties \
  --changelog-file platforms/postgres/databases/app/db.changelog-master.yaml \
  rollback v1.0
```

### Using Count

Roll back last N changeSets:

```bash
liquibase --defaults-file /data/liquibase/env/liquibase.prod.properties \
  --changelog-file platforms/postgres/databases/app/db.changelog-master.yaml \
  rollbackCount 3
```

### Using Date

Roll back to a timestamp:

```bash
liquibase --defaults-file /data/liquibase/env/liquibase.prod.properties \
  --changelog-file platforms/postgres/databases/app/db.changelog-master.yaml \
  rollbackToDate 2025-11-13
```

## Scalability and Performance

### Managing Large Numbers of Databases

**Challenge:** As organizations grow, managing 50+ databases becomes complex.

**Solutions:**

**1. Automated Database Discovery**

Instead of hardcoding database lists, auto-discover from configuration:

```bash
#!/bin/bash
# discover-databases.sh
set -euo pipefail

# Find all db.changelog-master.yaml files
find /data/liquibase/platforms -name "db.changelog-master.yaml" | while read -r changelog; do
  # Extract platform and database from path
  platform=$(echo "$changelog" | cut -d'/' -f5)
  database=$(echo "$changelog" | cut -d'/' -f7)

  echo "Found: $platform/$database"
  echo "  Changelog: $changelog"
done
```

**2. Parallel Deployments**

Deploy to independent databases in parallel:

```bash
#!/bin/bash
# parallel-deploy.sh
set -euo pipefail

MAX_PARALLEL=5  # Adjust based on database server capacity

export -f deploy_database

deploy_database() {
  local changelog=$1
  local env=$2

  platform=$(echo "$changelog" | cut -d'/' -f5)
  database=$(echo "$changelog" | cut -d'/' -f7)

  echo "[$platform/$database] Starting deployment to $env..."

  liquibase \
    --defaults-file="/data/liquibase/env/liquibase.$env.properties" \
    --changelog-file="$changelog" \
    update

  echo "[$platform/$database] Completed deployment to $env"
}

# Find all changelogs and deploy in parallel
find /data/liquibase/platforms -name "db.changelog-master.yaml" | \
  xargs -P $MAX_PARALLEL -I {} bash -c 'deploy_database "$@"' _ {} dev
```

**3. Database Grouping**

Group databases for sequential vs parallel deployment:

```yaml
# deployment-config.yaml
deployment_groups:
  # Deploy sequentially (has dependencies)
  critical_sequential:
    - platform: postgres
      databases: [shared-reference, customer, order]

  # Deploy in parallel (independent)
  analytics_parallel:
    - platform: snowflake
      databases: [warehouse, reporting, metrics]

  # Deploy in parallel (independent microservices)
  microservices_parallel:
    - platform: postgres
      databases: [auth, notification, payment, shipping]
```

**4. Changelog Caching**

For CI/CD with many databases, cache Liquibase tracking data:

```yaml
# .github/workflows/deploy.yml
- name: Cache Liquibase metadata
  uses: actions/cache@v3
  with:
    path: |
      ~/.liquibase/cache
    key: liquibase-${{ hashFiles('**/db.changelog-master.yaml') }}
```

### Performance Optimization

**1. Minimize Changeset Count**

Instead of many small changesets:

```yaml
# ❌ Inefficient: 50 separate changesets
- changeSet: { id: add-col-1, ... }
- changeSet: { id: add-col-2, ... }
- changeSet: { id: add-col-3, ... }
# ... 47 more

# ✅ Better: Logical grouping
- changeSet:
    id: 20251114-01-add-user-profile-columns
    changes:
      - addColumn:
          tableName: users
          columns:
            - column: { name: first_name, type: varchar(100) }
            - column: { name: last_name, type: varchar(100) }
            - column: { name: phone, type: varchar(20) }
```

**2. Use Batch Operations**

```yaml
# For large data loads, use batch processing
- changeSet:
    id: 20251114-02-load-reference-data
    changes:
      - loadData:
          file: countries.csv
          tableName: countries
          batchSize: 1000  # Process 1000 rows at a time
```

**3. Create Indexes After Data Loads**

```yaml
# Sequence matters for performance
- changeSet:
    id: step-1-create-table
    changes:
      - createTable: { tableName: large_table, ... }

- changeSet:
    id: step-2-load-data
    changes:
      - loadData: { file: data.csv, tableName: large_table }

- changeSet:
    id: step-3-create-indexes  # After data load
    changes:
      - createIndex: { tableName: large_table, ... }
```

**4. Use Preconditions to Skip Expensive Operations**

```yaml
- changeSet:
    id: 20251114-03-add-index-if-missing
    preConditions:
      - onFail: MARK_RAN  # Skip if already exists
      - not:
          - indexExists:
              tableName: users
              indexName: idx_users_email
    changes:
      - createIndex:
          tableName: users
          indexName: idx_users_email
```

**5. Optimize DATABASECHANGELOG Queries**

For databases with 1000+ changesets, add index:

```sql
-- PostgreSQL example
CREATE INDEX idx_databasechangelog_orderexecuted
  ON databasechangelog(orderexecuted);

-- SQL Server example
CREATE NONCLUSTERED INDEX idx_databasechangelog_orderexecuted
  ON DATABASECHANGELOG(ORDEREXECUTED);
```

### Monitoring at Scale

**1. Track Deployment Metrics**

```bash
#!/bin/bash
# log-deployment-metrics.sh

START_TIME=$(date +%s)

liquibase update

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Log to metrics system
echo "liquibase.deployment.duration{platform=postgres,database=customer,env=prod} $DURATION" | \
  curl -X POST --data-binary @- http://metrics-server:9090/api/v1/write
```

**2. Set Up Deployment Dashboard**

Track across all databases:

- Deployment success rate
- Average deployment time
- Failed deployments (last 7 days)
- Databases needing updates
- Checksum validation failures

**3. Alerting**

```yaml
# prometheus-alerts.yaml
groups:
  - name: liquibase
    rules:
      - alert: LiquibaseDeploymentFailed
        expr: liquibase_deployment_success == 0
        for: 5m
        annotations:
          summary: "Liquibase deployment failed"
          description: "{{ $labels.database }} failed to deploy"

      - alert: LiquibaseDeploymentSlow
        expr: liquibase_deployment_duration > 300
        for: 5m
        annotations:
          summary: "Liquibase deployment taking > 5 minutes"
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

### Online Index Creation

- PostgreSQL: prefer `CREATE INDEX CONCURRENTLY` to minimize locks
- SQL Server: use `WITH (ONLINE = ON)` where edition supports it
- Oracle: use the `ONLINE` clause; test on representative data

Add preconditions to avoid duplicate indexes and expect longer build times.

### Transactional Boundaries

Understand DDL transaction behavior per platform:

- PostgreSQL: most DDL is transactional; safe to wrap changeSets
- MySQL/SQL Server/Oracle: some DDL autocommits or is non-transactional

Design changeSets so partial failures won’t leave schema unusable.

### Large Backfills and Batching

- Use chunked DML via `sql`/`sqlFile` with ID/time windows
- Schedule during low-traffic windows; add resume markers
- Guard with preconditions to skip completed batches

### Permissions and Grants

Model GRANT/REVOKE as SQL changeSets, filtered with labels/contexts; keep secrets out of VCS.

### Partitioning Lifecycle

- Pre-create future partitions (monthly/weekly)
- Archive/drop old partitions via scheduled changeSets
- Use preconditions for idempotency

### Collation/Encoding Changes

Potentially disruptive; plan maintenance windows or rebuild strategies and validate application behavior.

### Dependency-Heavy Objects

Schema-bound views, materialized views, and computed/generated columns require careful ordering and rebuild policies.

### Run Rules: `runOnChange` / `runAlways`

Avoid unless necessary. Prefer explicit new changeSets to prevent checksum churn. Use `runOnChange` for templates designed to regenerate.

### Multi-Tenant Rollouts

Loop per-tenant schema/database; use labels like `tenant:acme` to filter and track progress per tenant.

### Replication and HA

For Postgres logical replication or SQL Server Always On, avoid blocking operations; prefer online DDL and validate impact on replicas.

### Cross-Database Coordination

When multiple databases must change in lockstep, coordinate tags and approvals and deploy in a controlled order with checkpoints.

### Performance Tips

- Prefer smaller, single-purpose changeSets to improve retryability
- Batch large `loadData` operations and avoid running in prod unless necessary
- Add indexes after large data loads to reduce migration time
- Use `preConditions` to guard expensive operations when objects already exist
- Avoid editing applied changeSets; append new changeSets instead

## Alternative Approaches

## Edition Differences

### Liquibase Community

Included:

- Core DDL object management, multiple changelog formats
- Basic diff/diffChangeLog and rollbacks (tag/count/date)
- CLI and APIs, 60+ platforms, community support

Limitations:

- Manual SQL changeSets for stored logic (procedures/functions/triggers/packages/check constraints)
- No automated stored logic extraction, policy checks, or flow files
- No advanced drift/rollback features or Secure IDE features

### Liquibase Secure (adds to Community)

- Automated stored logic extraction and `pro:` change types
- Policy checks, compliance-ready audit trails, SIEM-friendly logs
- Drift reports/alerts/reconciliation and policy enforcement
- Flow files orchestration and automatic rollback generation
- Targeted rollbacks and developer IDE integrations
- Enterprise support, certified drivers, secure credential features

### When to Use This Structure

**✅ Use this multi-platform, centralized approach when:**

1. **Multiple Platforms**: Managing 3+ different database technologies
2. **Platform Teams**: Centralized DBA or platform engineering team
3. **Shared Infrastructure**: Common deployment pipelines and tooling
4. **Cross-Database Dependencies**: Some databases reference others
5. **Consistent Standards**: Need uniform change management practices
6. **Enterprise Scale**: 10+ databases across multiple platforms

### Alternative Structure #1: Monorepo per Platform

For organizations with strong platform specialization:

```text
# Separate repositories
liquibase-postgres/
  databases/
    customer/
    order/
    analytics/

liquibase-mssql/
  databases/
    erp/
    crm/

liquibase-snowflake/
  databases/
    warehouse/
```

**When to use:**

- Platform-specific teams (PostgreSQL team, SQL Server team)
- Different deployment schedules per platform
- Platform-specific tooling requirements
- Compliance/security boundaries between platforms

**Pros:**

- Simpler per-repository structure
- Independent release cycles
- Platform-specific CI/CD optimization
- Easier access control

**Cons:**

- Duplicate tooling and scripts
- Harder to share common patterns
- More repositories to maintain

### Alternative Structure #2: Database per Repository

For fully autonomous microservice teams:

```text
# Each microservice owns its database changes
customer-service/
  src/
  database/
    changelog/
      master.yaml
      releases/

order-service/
  src/
  database/
    changelog/
      master.yaml
      releases/
```

**When to use:**

- Microservices with full autonomy
- No shared database infrastructure
- Teams own entire stack (code + database)
- Different technologies per service

**Pros:**

- Maximum team autonomy
- Deployments coupled with application code
- Simpler per-service structure
- Faster iteration

**Cons:**

- Duplicate Liquibase configurations
- Harder to enforce standards
- No central visibility
- Difficult to coordinate cross-database changes

### Alternative Structure #3: Flat Organization

For small teams with few databases:

```text
/data/liquibase/
  env/
  changelogs/
    customer-db/
      master.yaml
    order-db/
      master.yaml
    analytics-db/
      master.yaml
```

**When to use:**

- Single platform (e.g., only PostgreSQL)
- < 5 total databases
- Small team (1-3 DBAs)
- Simple deployment requirements

**Pros:**

- Minimal directory depth
- Easy to navigate
- Less organizational overhead

**Cons:**

- Doesn't scale beyond 10 databases
- No platform grouping
- Harder to find shared patterns

### Hybrid Approach

Combine strategies based on your needs:

```text
/data/liquibase/
  platforms/
    postgres/          # Centralized (many databases)
      databases/
        customer/
        order/
        analytics/
    mssql/            # Per-platform repo (legacy, separate team)
      # Link to separate repository
    snowflake/        # Centralized (data platform team)
      databases/
        warehouse/
```

### Decision Matrix

| Factor | Centralized Multi-Platform | Monorepo per Platform | Database per Repo |
|--------|---------------------------|----------------------|------------------|
| Number of platforms | 3+ | 1-2 per repo | Any |
| Number of databases | 10+ | 5-20 | 1-5 |
| Team structure | Platform teams | Platform teams | Product teams |
| Deployment coupling | Independent | Independent | With application |
| Shared patterns | High | Medium | Low |
| Access control | Platform-level | Platform-level | Service-level |
| Complexity | High | Medium | Low |
| Best for | Enterprises | Mid-size orgs | Startups/Microservices |

## Testing Strategy

### Database Testing Levels

**1. Changelog Validation**

Validate changelog syntax and structure:

```bash
# Validate all changelogs in CI/CD
find platforms -name "db.changelog-master.yaml" | while read changelog; do
  liquibase --changelog-file="$changelog" validate || exit 1
done
```

**2. SQL Preview Testing**

Generate and review SQL before deployment:

```bash
# Generate SQL for review
liquibase \
  --defaults-file=/data/liquibase/env/liquibase.dev.properties \
  --changelog-file=/data/liquibase/platforms/postgres/databases/app/db.changelog-master.yaml \
  updateSQL > /tmp/preview-$(date +%Y%m%d).sql

# Check for dangerous operations
grep -E '(DROP TABLE|TRUNCATE|DELETE FROM)' /tmp/preview-*.sql
```

**3. Ephemeral Database Testing**

Test changes on temporary databases:

```bash
#!/bin/bash
# Create temporary test database
TEST_DB="test_$(date +%s)"
createdb "$TEST_DB"

# Run liquibase
liquibase \
  --url="jdbc:postgresql://localhost:5432/$TEST_DB" \
  --changelog-file=platforms/postgres/databases/app/db.changelog-master.yaml \
  update

# Run database tests
pytest tests/database/

# Cleanup
dropdb "$TEST_DB"
```

**4. Rollback Testing**

Validate rollback scripts work:

```bash
# Deploy to test database
liquibase --defaults-file=env/liquibase.test.properties update
liquibase --defaults-file=env/liquibase.test.properties tag before-rollback

# Apply new changes
liquibase --defaults-file=env/liquibase.test.properties update

# Test rollback
liquibase --defaults-file=env/liquibase.test.properties rollback before-rollback

# Verify database state
```

**5. Performance Testing**

Test migration performance on production-like data volumes:

```bash
# Generate test data
pgbench -i -s 100 test_db

# Time migration
time liquibase --defaults-file=env/liquibase.test.properties update
```

**6. Integration Testing**

Test with application code:

```yaml
# .github/workflows/integration-test.yml
jobs:
  integration-test:
    services:
      postgres:
        image: postgres:15
    steps:
      - name: Apply database changes
        run: liquibase update

      - name: Run application tests
        run: pytest tests/integration/
```

### Testing Checklist

Before promoting to production:

- [ ] Changelog validates successfully
- [ ] SQL preview reviewed (no unexpected operations)
- [ ] Changes applied successfully to dev database
- [ ] Changes applied successfully to staging database
- [ ] Rollback tested and works
- [ ] Performance acceptable (< 5 minutes for typical change)
- [ ] No breaking changes to existing applications
- [ ] Database users/permissions still work
- [ ] Indexes and constraints created successfully
- [ ] Integration tests pass

## Migration from Legacy

### Adopting This Structure in Existing Projects

**Phase 1: Assessment (Week 1-2)**

1. Inventory all databases:

   ```bash
   # Document current state
   platforms:
     - postgres: [customer_db, order_db, analytics_db]
     - mssql: [erp_db, crm_db]
     - snowflake: [warehouse_db]
   ```

2. Identify baseline requirements:
   - Which databases need baselines (existing production databases)?
   - Which are new (no baseline needed)?

3. Choose structure:
   - Will this multi-platform structure work?
   - Or is an alternative better suited?

**Phase 2: Setup Infrastructure (Week 3)**

1. Create directory structure:

   ```bash
   mkdir -p /data/liquibase/{env,shared/{modules,data/reference}}
   mkdir -p /data/liquibase/platforms/{postgres,mssql,snowflake}/databases
   ```

2. Create property templates:

   ```bash
   cp liquibase.dev.properties env/liquibase.dev.properties.template
   # Remove sensitive data
   sed -i 's/password=.*/password=${DB_PASSWORD}/' env/*.template
   ```

3. Set up CI/CD pipeline skeleton

**Phase 3: Pilot Database (Week 4-5)**

Choose one non-critical database for pilot:

1. Generate baseline:

   ```bash
   liquibase generateChangeLog \
     --changelog-file=platforms/postgres/databases/analytics/baseline/baseline-draft.yaml
   ```

2. Review and clean up baseline:
   - Add schema creation
   - Fix missing procedures/functions
   - Add `schemaName` attributes

3. Create master changelog:

   ```yaml
   databaseChangeLog:
     - include:
         file: baseline/db.changelog-baseline.yaml
     - tagDatabase:
         tag: baseline
   ```

4. Sync to existing environments:

   ```bash
   # Mark baseline as executed (don't run DDL)
   liquibase changelogSync
   liquibase tag baseline
   ```

5. Make first incremental change:

   ```bash
   # Create release 1.0 with first change
   mkdir -p releases/1.0
   # Add change, test, deploy
   ```

**Phase 4: Rollout to All Databases (Week 6-12)**

1. Prioritize databases:
   - Start with lowest risk
   - Leave critical production databases for last

2. Repeat Phase 3 for each database

3. Establish team workflows:
   - Change request process
   - Review requirements
   - Deployment schedules

**Phase 5: Optimization (Week 13+)**

1. Extract shared modules
2. Automate common tasks
3. Refine CI/CD pipelines
4. Train team members
5. Document lessons learned

### Migration Checklist

- [ ] All databases inventoried
- [ ] Directory structure created
- [ ] Property files configured
- [ ] Baselines generated for existing databases
- [ ] Baselines reviewed and cleaned
- [ ] Baseline synced to production (changelogSync)
- [ ] First incremental change tested
- [ ] CI/CD pipeline working
- [ ] Team trained on new workflow
- [ ] Documentation updated
- [ ] Rollback procedures tested
- [ ] All legacy scripts migrated or deprecated

## Troubleshooting

### Lock Issues

```bash
# Release stuck lock
liquibase --defaults-file /data/liquibase/env/liquibase.dev.properties releaseLocks
```

### Checksum Mismatches

When changeSet edited after deployment:

```bash
# Clear checksums (use with caution)
liquibase --defaults-file /data/liquibase/env/liquibase.dev.properties clearCheckSums
```

Better: never edit deployed changeSets; create new ones.

### Manual Interventions

Mark changeSets as executed without running:

```bash
liquibase --defaults-file /data/liquibase/env/liquibase.prod.properties \
  changelogSync
```

### Monitoring

Track applied changes via the `DATABASECHANGELOG` table and standard logging:

```sql
-- Recent changes
SELECT id, author, filename, dateexecuted, tag FROM databasechangelog ORDER BY dateexecuted DESC LIMIT 20;

-- Current lock status
SELECT * FROM databasechangeloglock;
```

## Glossary

- ChangeLog: The file (or tree of files) that defines database changes
- ChangeSet: The atomic unit of change (id, author, changes, rollback)
- Baseline: Initial schema snapshot prior to Liquibase-managed evolution
- Drift: Differences between expected schema (changelogs) and actual DB
- Tag: A named point-in-time marker for rollbacks and coordination
- Flow file: Liquibase Secure workflow file that orchestrates stages/actions

## References

### Official Documentation

- [Liquibase Documentation](https://docs.liquibase.com/)
- [Best Practices](https://docs.liquibase.com/start/design-liquibase-project.html)
- [Changelog Organization](https://docs.liquibase.com/workflows/liquibase-community/multiple-sql-migration.html)
- [Platform-Specific Guides](https://docs.liquibase.com/start/tutorials/home.html)

### Internal Documentation

- Internal: `/data/liquibase/README.md` (if present) for quick start
- Tutorial: `docs/tutorials/liquibase/sqlserver-liquibase-tutorial.md` for end-to-end SQL Server example
- Operations Guide: `docker/liquibase/liquibase-docker-operations-guide.md` for Docker execution patterns

### Community Resources

- [Liquibase Community Forum](https://forum.liquibase.org/)
- [GitHub Discussions](https://github.com/liquibase/liquibase/discussions)
- [Database DevOps Blog](https://www.liquibase.com/blog)

### Books and Articles

- "Refactoring Databases" by Scott W. Ambler
- "Database Reliability Engineering" by Laine Campbell & Charity Majors
- [Martin Fowler on Evolutionary Database Design](https://martinfowler.com/articles/evodb.html)

### Related Tools

- [Flyway](https://flywaydb.org/) - Alternative migration tool
- [DBmaestro](https://www.dbmaestro.com/) - Enterprise database DevOps
- [Redgate](https://www.redgate.com/) - SQL Server focused tools
- [Alembic](https://alembic.sqlalchemy.org/) - Python-based migrations

## Appendix

### Document Change History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 2.0 | 2025-11-14 | Added naming conventions, alternative approaches, testing strategy, migration guide | Platform Team |
| 1.0 | 2025-11-13 | Initial version with multi-platform structure | Platform Team |

### Contributing to This Document

This document is maintained by the Platform Engineering team. To suggest improvements:

1. Create an issue describing the improvement
2. Submit a pull request with changes
3. Tag `@platform-team` for review

### License

Internal use only. Not for distribution outside the organization.

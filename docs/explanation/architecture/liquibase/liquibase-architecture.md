# Liquibase Architecture Guide

> **Document Version:** 1.0
> **Last Updated:** December 20, 2025
> **Maintainers:** Global Data Services Team
> **Status:** Production - Actively Maintained

![Liquibase Version](https://img.shields.io/badge/Liquibase-5.0%2B-blue)
![Document Status](https://img.shields.io/badge/Status-Production-green)

> [!NOTE]
> Examples in this document use the **Global Data Services (GDS)** team, but the patterns and structures apply to **all teams**.

## Table of Contents

- [Overview](#overview)
  - [What is Liquibase?](#what-is-liquibase)
  - [Architecture Scope](#architecture-scope)
  - [Key Architectural Decisions](#key-architectural-decisions)
- [Design Principles](#design-principles)
  - [Single Source of Truth](#single-source-of-truth)
  - [Team Isolation](#team-isolation)
  - [Application-First Organization](#application-first-organization)
  - [Shared Cross-Platform Databases](#shared-cross-platform-databases)
  - [Release-Driven Versioning](#release-driven-versioning)
  - [Baseline Strategy](#baseline-strategy)
  - [Tracking Tables Location](#tracking-tables-location)
- [Directory Structure](#directory-structure)
  - [Cross-Platform Databases (e.g., dbadmin)](#cross-platform-databases-eg-dbadmin)
  - [Repository Strategy](#repository-strategy)
  - [Changelog Directory Structure (Per-Team Repo)](#changelog-directory-structure-per-team-repo)
  - [Naming Order Options](#naming-order-options)
- [Conventions](#conventions)
  - [Platform Names](#platform-names)
  - [Database Names](#database-names)
  - [File Naming](#file-naming)
  - [Properties Files Architecture](#properties-files-architecture)
- [Advanced Architecture Patterns](#advanced-architecture-patterns)
  - [Liquibase Flowfiles](#liquibase-flowfiles)
  - [Kubernetes Init Containers](#kubernetes-init-containers)
  - [Docker Execution](#docker-execution)
  - [Rollback Strategy](#rollback-strategy)
  - [Drift Detection](#drift-detection)
  - [Testing Strategy](#testing-strategy)
  - [Contexts and Labels](#contexts-and-labels)
  - [Quality Checks (Pro)](#quality-checks-pro)
- [Scalability and Performance Patterns](#scalability-and-performance-patterns)
  - [Managing Large Numbers of Databases](#managing-large-numbers-of-databases)
  - [Monitoring at Scale](#monitoring-at-scale)

- [Related Documentation](#related-documentation)

## Overview

### What is Liquibase?

Liquibase is an open-source, database-independent tool for tracking, managing, and applying database schema changes. It provides version control for database schemas, enabling teams to:

- **Define changes as code**: Schema modifications are written in changelog files (YAML, XML, JSON, or SQL).
- **Track deployment history**: The `DATABASECHANGELOG` table records every applied changeset.
- **Deploy consistently**: The same changelog deploys identically across all environments.
- **Roll back safely**: Built-in rollback support allows reverting changes when needed.
- **Integrate with CI/CD**: Automate schema deployments alongside application code.

This architecture relies on **Liquibase Community** (open-source) but implements functionality found in **Liquibase Secure** (commercial) via custom automation and standards. See [Edition Differences](../../../reference/liquibase/liquibase-reference.md#edition-differences) for feature comparison.

### Architecture Scope

This architecture supports database schema management across multiple platforms and environments:

**Supported Platforms:**

- PostgreSQL, SQL Server, Snowflake, MongoDB
- Any future platform with a JDBC driver

**Deployment Environments:**

- `dev` → `test` → `stage` → `prod`

Changes are written once and promoted through environments using environment-specific connection properties.

### Key Architectural Decisions

| Decision | Rationale |
|:---|:---|
| **Separate repo per team** | Full isolation, standard GitHub permissions, independent deployments |
| **Shared changelog repo (GDS-owned)** | The Global Data Services (GDS) team owns `gds-liquibase-shared` containing cross-platform databases like `dbadmin`. GDS manages and deploys these to all instances across all database platforms. |
| **Application-first structure** | Within each team's repo, changelogs are organized by application, then platform, then database |
| **Environment-specific properties** | Same changelogs deploy to all environments; only connection info differs |

[↑ Back to Table of Contents](#table-of-contents)

## Design Principles

### Single Source of Truth

- SQL changes are written **once** in YAML/XML changelogs
- Same changelog deploys to all environments and instances
- Each database instance × environment has its own properties file (connection details, credentials)
- Version control tracks all schema evolution

### Team Isolation

- Each team owns a **separate GitHub repository** for their changelogs
- Standard GitHub permissions control access
- Teams can version and deploy independently

### Application-First Organization

- Within each team's repo, changelogs are organized by application first
- **Nested Directory Structure**: `applications/` → `<app_name>/` → `<platform>/` → `<database>/`
- Platform-specific SQL isolated using the **Liquibase `dbms` attribute**. This configuration ensures a changeset only runs if the connected database matches the specified type (e.g., `dbms="postgresql"`), allowing safe handling of platform-specific syntax in shared files.

### Shared Cross-Platform Databases

- GDS-owned `gds-liquibase-shared` repo contains databases deployed to all platforms (e.g., `dbadmin`)
- **GDS Exclusive Ownership**: The `gds-liquibase-shared` repository is owned and managed **exclusively** by the Global Data Services (GDS) team. Other teams do not have access to reference or modify these shared databases.
- Common layer (all platforms) + platform layer (platform-specific objects)

### Release-Driven Versioning

- Changes organized into `releases/<version>/` folders
- Each release ends with a `tagDatabase` for rollback points (tags can correspond to Jira tickets, e.g., `PROJ-123`)
- Numbered files within releases ensure deterministic order

### Baseline Strategy

A **baseline** captures the current database schema as a starting point for Liquibase management. There are two key scenarios:

**1. Initial Adoption (Existing Database)**
When adopting Liquibase for an existing database, generate a baseline that represents the current schema. Use `changelogSync` to mark it as applied without re-executing SQL.

**2. Baseline Reset (Consolidation)**
Over time, changelogs accumulate (e.g., 50+ changesets). For new database instances, you can:

- **Run all changesets** — Guarantees consistency, but slow for large schemas
- **Consolidate into a new baseline** — Generate a fresh snapshot, making new deployments faster

| Scenario | Approach |
|:---|:---|
| Existing instance, adopting Liquibase | Generate baseline → `changelogSync` |
| New instance, many historical changesets | Run all changesets OR use consolidated baseline |
| Periodic maintenance | Consolidate after major releases to simplify history |

See the [Operations Guide](../../../how-to/liquibase/liquibase-operations-guide.md#baseline-management) for step-by-step procedures.

### Tracking Tables Location

Liquibase creates two tracking tables in each target database:

| Table | Purpose |
|:---|:---|
| `DATABASECHANGELOG` | Tracks all applied changesets |
| `DATABASECHANGELOGLOCK` | Prevents concurrent deployments |

**Naming Convention:**

| Platform Supports Schemas? | Configuration |
|:---|:---|
| **Yes** (PostgreSQL, SQL Server, Snowflake) | Place tables in a dedicated `liquibase` schema |
| **No** (MongoDB, some NoSQL) | Prefix table names with `liquibase_` |

**Properties Configuration:**

```properties
# For platforms with schema support
liquibase.liquibase-schema-name=liquibase

# For platforms without schema support
liquibase.database-changelog-table-name=liquibase_changelog
liquibase.database-changelog-lock-table-name=liquibase_changelog_lock
```

[↑ Back to Table of Contents](#table-of-contents)

### Directory Structure

**Recommendation: Use Relative Paths with Search Path**
Relative paths (e.g., `applications/app1/...`) need a consistent "anchor" or "root" to resolve correctly. Set `LIQUIBASE_SEARCH_PATH` to your repository root so that Liquibase can find files regardless of which directory you run the command from.

**Example Configuration:**

- **Local Dev**: `export LIQUIBASE_SEARCH_PATH=/home/user/src/my-repo`
- **Docker**: Mount repo to `/liquibase/changelog` and set `LIQUIBASE_SEARCH_PATH=/liquibase/changelog`
- **CI/CD (GitHub Actions)**:

  ```yaml
  - uses: liquibase/liquibase-github-action@v4
    with:
      # Relative path to changelog
      changelogFile: "applications/app1/postgres/db/changelog.yaml"
      # Search path set to workspace root
      searchPath: "${{ github.workspace }}"
  ```

This ensures `include file="applications/..."` works identically everywhere.

```text
. (Repository Root)
├── env/                                 # properties templates (no secrets)
│   ├── liquibase.dev.properties.template
│   ├── liquibase.prod.properties.template
├── shared/
│   ├── modules/                         # reusable, db-agnostic modules
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

### Cross-Platform Databases (e.g., dbadmin)

The `dbadmin` database exists on **every platform** but may have **different objects per platform**. Use a layered changelog structure:

**Changelog Layers:**

1. **Common Layer**: Objects shared across all platforms (e.g., audit tables, metadata tables).
2. **Platform Layer**: Platform-specific objects (e.g., PostgreSQL extensions, SQL Server CLR functions).

**1. Directory Structure:**

```text
shared/
  modules/
    dbadmin/
      db.changelog-dbadmin-common.yaml     # Platform-agnostic objects
      postgres/
        db.changelog-dbadmin-postgres.yaml # PostgreSQL-specific objects
      mssql/
        db.changelog-dbadmin-mssql.yaml    # SQL Server-specific objects
      snowflake/
        db.changelog-dbadmin-snowflake.yaml
      mongodb/
        db.changelog-dbadmin-mongodb.yaml
```

**2. Platform Master Changelog (includes both layers):**

```yaml
# platforms/postgres/databases/dbadmin/db.changelog-master.yaml
databaseChangeLog:
  # Layer 1: Common objects (all platforms)
  - include:
      file: ../../../../shared/modules/dbadmin/db.changelog-dbadmin-common.yaml

  # Layer 2: PostgreSQL-specific objects
  - include:
      file: ../../../../shared/modules/dbadmin/postgres/db.changelog-dbadmin-postgres.yaml

  - tagDatabase:
      tag: v1.0
```

```yaml
# platforms/mssql/databases/dbadmin/db.changelog-master.yaml
databaseChangeLog:
  # Layer 1: Common objects (all platforms)
  - include:
      file: ../../../../shared/modules/dbadmin/db.changelog-dbadmin-common.yaml

  # Layer 2: SQL Server-specific objects
  - include:
      file: ../../../../shared/modules/dbadmin/mssql/db.changelog-dbadmin-mssql.yaml

  - tagDatabase:
      tag: v1.0
```

**3. Example: Common vs Platform-Specific Objects**

```yaml
# db.changelog-dbadmin-common.yaml (all platforms)
databaseChangeLog:
  - changeSet:
      id: 20251220-01-create-audit-log
      author: platform-team
      changes:
        - createTable:
            tableName: audit_log
            columns:
              - column: { name: id, type: bigint, autoIncrement: true }
              - column: { name: event_time, type: timestamp }
              - column: { name: event_type, type: varchar(50) }
```

```yaml
# db.changelog-dbadmin-postgres.yaml (PostgreSQL only)
databaseChangeLog:
  - changeSet:
      id: 20251220-01-create-pg-extensions
      author: platform-team
      dbms: postgresql
      changes:
        - sql:
            sql: CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

```yaml
# db.changelog-dbadmin-mssql.yaml (SQL Server only)
databaseChangeLog:
  - changeSet:
      id: 20251220-01-create-mssql-schema
      author: platform-team
      dbms: mssql
      changes:
        - sql:
            sql: |
              IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'admin')
                EXEC('CREATE SCHEMA admin');
```

**4. Properties Files:**

Properties files are stored in the `env/` directory relative to the repository root.

**Naming Convention:**

Since each team has its own repository, team name is implicit. The naming convention is:

`liquibase.<application>.<platform>.<database>.<dbinstance>.<environment>.properties`

| Dimension | Description | Example |
|:---|:---|:---|
| `application` | Application name (required) | `payments_api`, `monitoring` |
| `platform` | Database technology | `postgres`, `mssql`, `snowflake` |
| `database` | Logical database name | `customer`, `dbadmin` |
| `dbinstance` | Database instance identifier | `dbinstance1`, `dbinstance_east` |
| `environment` | Deployment environment | `dev`, `test`, `stage`, `prod` |

**Naming Rules:**

- Use **snake_case** (underscores) for multi-word names (e.g., `payments_api`).
- **No dashes** allowed in application names.
- All dimensions are separated by periods (`.`).

**Examples:**

```text
# In team-alpha's repo
env/
  liquibase.payments_api.postgres.orders.dbinstance1.dev.properties
  liquibase.inventory_svc.postgres.catalog.dbinstance1.prod.properties
```

### Repository Strategy

Each team owns a **separate GitHub repository** for full isolation and permission control:

```text
github.com/org/alpha-liquibase       # Team Alpha's changelogs
github.com/org/beta-liquibase        # Team Beta's changelogs
github.com/org/gds-liquibase-shared  # Shared modules (GDS owned)
```

**Benefits:**

- **Isolation**: Teams cannot read/modify other teams' files
- **Permissions**: Standard GitHub repo permissions apply
- **Independence**: Teams can version and deploy independently

**Shared Modules**: The `gds-liquibase-shared` repo can be included as a Git submodule in each team's repo.

### Changelog Directory Structure (Per-Team Repo)

Within each team's repository, no team folder is needed (team is implicit):

```text
# liquibase-team-alpha repo (repository root)
applications/
  payments_api/
    postgres/
      orders/
        db.changelog-master.yaml
        releases/
          1.0/
            db.changelog-1.0.yaml
            001-create-tables.yaml
    mssql/
      legacy_orders/
        db.changelog-master.yaml
  inventory_svc/
    postgres/
      catalog/
        db.changelog-master.yaml
shared/                              # Git submodule: liquibase-shared
  modules/
    dbadmin/
      db.changelog-dbadmin-common.yaml
env/
  liquibase.payments_api.postgres.orders.dbinstance1.dev.properties.template
```

### Naming Order Options

Choose the order that matches your workflow:

**Option A: Application-First (Recommended)**

```text
liquibase.<application>.<platform>.<database>.<dbinstance>.<environment>.properties
```

- Glob by app: `liquibase.payments_api.*` → all databases for payments_api
- **Why it's best**: Aligns with the "Application-First Organization" principle. In a microservices or per-team repo structure, teams primarily think in terms of their applications ("deploy payments_api version 2") rather than database platforms. This naming groups all configuration for a single app's ecosystem together, making it easier to filter property files for a specific deployment.

**Option B: Platform-First**

```text
liquibase.<platform>.<application>.<database>.<dbinstance>.<environment>.properties
```

- Glob by platform: `liquibase.postgres.*` → all Postgres databases
- **Why it's best**: Useful for centralized **Platform DBA teams**. If a team's primary responsibility is "Manage all PostgreSQL instances" regardless of the application, this structure allows them to easily apply changes (like maintenance scripts or audits) to every database of a specific technology type at once.

**CI/CD Best Practice**: Generate properties files dynamically from a secrets manager at pipeline runtime. Never commit credentials to Git.

[↑ Back to Table of Contents](#table-of-contents)

## Conventions

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

- **Existing Databases**: Directory name MUST match the actual database name in production. This ensures consistent discoverability and mapping.
- **New Databases (Standard)**: Use lowercase, snake_case names (e.g., `customer_service`) for clarity and consistency.

```text
platforms/postgres/databases/
  CustomerServiceDB/     # Existing Legacy DB (matches actual name)
  payments_api/          # New Standard DB (snake_case)
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

Use format: `YYYYMMDD-HHMM-JIRA-description`

```yaml
changeSet:
  id: 20251114-1000-PROJ-123-create-customers   # Date + Sequence + Ticket + Description
  id: 20251114-1005-PROJ-123-add-email-index
  id: 20251115-0900-PROJ-124-create-orders
```

**Why this format?**

- **Date First (`YYYYMMDD`)**: Ensures natural chronological sorting in the changelog table and cleaner logical organization.
- **Uniqueness**: Time component (`HHMM`) prevents collisions even if multiple tickets are merged same day.
- **Traceability**: **Mandatory** Jira Ticket ID (`PROJ-123`) links every change to a requirement.
- **Readability**: Description makes intent clear.

### Properties Files Architecture

Changes are environment-agnostic. Environment details are injected via properties files.

```text
env/
  liquibase.dev.properties.template
  liquibase.stage.properties.template
  liquibase.prod.properties.template
  liquibase.{platform}.{database}.{env}.properties    # For complex setups
```

**Security Guidelines**:

- **Templates**: Keep `.properties.template` files in Git as examples (no secrets).
- **Ephemeral Generation (Recommended)**: Programmatically generate the full `.properties` file with credentials from a secrets manager (e.g., Vault) at runtime, execute Liquibase, and **immediately delete** the file. This minimizes credential exposure on the filesystem.
- **Environment Variables**: Alternatively, use environment variables (e.g., `DB_PASSWORD`) referenced in the properties file.
- **GitIgnore**: Never commit actual `.properties` files containing secrets.

[↑ Back to Table of Contents](#table-of-contents)

## Advanced Architecture Patterns

### Liquibase Flowfiles

For enterprise standardization, use **Liquibase Flowfiles** (`liquibase.flowfile.yaml`) instead of raw CLI commands.

- **Orchestration**: Chain multiple commands (e.g., `validate` -> `checks run` -> `update`) in a single execution.
- **Portability**: Define workflows once, run anywhere (local, Docker, CI/CD).
- **See Operations Guide**: [Using Flow Files (Advanced)](../../../how-to/liquibase/liquibase-operations-guide.md#using-flow-files-advanced)
- **Variables**: Use stage variables and conditionals to adapt logic per environment.

### Kubernetes Init Containers

In containerized environments (Kubernetes), run Liquibase as an **Init Container** rather than part of the application startup or a separate Job.

- **Avoids Race Conditions**: Ensures migrations finish before the app starts.
- **Prevents Locks**: Linear execution per pod avoids `DATABASECHANGELOGLOCK` contention.
- **Fail Fast**: If migration fails, the pod fails to start, preventing broken apps from serving traffic.

### Docker Execution

Liquibase can run in Docker containers for consistent, reproducible deployments:

- Mount the repository root to a standard path (e.g., `/liquibase/changelog`) inside the container
- Set `LIQUIBASE_SEARCH_PATH` to the mounted directory to resolve relative paths correctly
- **Credentials**: Avoid raw environment variables (visible in `docker inspect`). Instead, **mount** an ephemeral properties file (generated at runtime) or use Docker Secrets to pass credentials securely.

See the [Operations Guide](../../../how-to/liquibase/liquibase-operations-guide.md#docker-execution) for Docker run commands.

### Rollback Strategy

Liquibase supports rolling back changes when deployments fail or need to be reverted:

| Method | Use Case |
|:---|:---|
| **Rollback by Tag** | Roll back to a named release point (e.g., `v1.0`) |
| **Rollback by Count** | Roll back the last N changesets |
| **Rollback by Date** | Roll back to a specific date/time |

**Best Practice**: Tag releases in your changelog so you can rollback to known-good states.

See the [Operations Guide](../../../how-to/liquibase/liquibase-operations-guide.md#rollback-strategy) for rollback commands.

### Drift Detection

**Drift** is when the actual database schema differs from what Liquibase changelogs expect. This happens when:

- Manual changes are made directly to the database
- Emergency hotfixes bypass the changelog process
- Different environments diverge over time

Liquibase can detect drift using `diff` and `diffChangeLog` commands to compare environments.

See the [Operations Guide](../../../how-to/liquibase/liquibase-operations-guide.md#drift-detection) for drift detection commands.

### Testing Strategy

Database changes should be tested before production deployment:

| Test Type | Purpose |
|:---|:---|
| **Changelog Validation** | Verify syntax and structure before deployment |
| **Ephemeral Database Testing** | Apply changes to a temporary database, run tests, then destroy |
| **Rollback Testing** | Verify rollback works correctly before deploying to production |

See the [Operations Guide](../../../how-to/liquibase/liquibase-operations-guide.md#testing-strategy) for testing procedures.

### Contexts and Labels

Liquibase supports **contexts** and **labels** to control which changesets run in which environments:

- **Contexts**: Filter by environment (e.g., `context: dev` runs only in dev)
- **Labels**: Tag changesets for selective execution (e.g., `labels: 'db:app'`)

**Best Practice**: Keep schema changes environment-agnostic. Use contexts only for dev-only test data.

### Quality Checks (Pro)

Liquibase Pro/Enterprise includes **Quality Checks** that analyze changelogs for policy violations before deployment:

- Block dangerous patterns (e.g., DROP TABLE without backup)
- Enforce naming conventions
- Require rollback blocks

See the [Reference](../../../reference/liquibase/liquibase-reference.md#edition-differences) for edition feature comparison.

[↑ Back to Table of Contents](#table-of-contents)

## Scalability and Performance Patterns

### Managing Large Numbers of Databases

**1. Automated Database Discovery**
Instead of hardcoding database lists, auto-discover from configuration or directory structure.

**2. Parallel Deployments**
Deploy to independent databases in parallel to reduce total deployment time.

**3. Database Grouping**
Group databases for sequential vs parallel deployment in a configuration file (e.g., `deployment-config.yaml`).

### Monitoring at Scale

**1. Structured Logging (JSON)**
Enable structured logging (`log-format=JSON`) to output machine-readable logs.

- **Ingestion**: Easily parsed by Splunk, Datadog, or ELK.
- **Context**: Includes operation type, target database, and changeset details in every log entry.

**2. Track Deployment Metrics**
Log start time, end time, and success/failure status to a metrics system (Prometheus, Datadog).

**3. Deployment Dashboard**
Track failure rates, average duration, and pending updates across all databases.

[↑ Back to Table of Contents](#table-of-contents)

## Related Documentation

- [**Liquibase Operations Guide**](../../../how-to/liquibase/liquibase-operations-guide.md): Practical guides for Creating Baselines, Deployments, Rollbacks, and Migrations.
- [**Liquibase Reference**](../../../reference/liquibase/liquibase-reference.md): Glossary, Command Reference, Limitations, and Troubleshooting.

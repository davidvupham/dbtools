# Liquibase Architecture Guide

**🔗 [← Back to Liquibase Documentation Index](../README.md)** — Navigation guide for all Liquibase docs

> **Document Version:** 2.0
> **Last Updated:** January 6, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production - Actively Maintained

![Liquibase Version](https://img.shields.io/badge/Liquibase-5.0%2B-blue)
![Document Status](https://img.shields.io/badge/Status-Production-green)

> [!IMPORTANT]
> **New to Liquibase?** Start with the [Liquibase Concepts Guide](../concepts/liquibase/liquibase-concepts.md) first. This document assumes you understand the fundamentals (Changelog, Changeset, Change Types, tracking tables).

## Table of Contents

- [Architecture Overview](#architecture-overview)
  - [Scope](#scope)
  - [Key Decisions](#key-decisions)
- [Design Principles](#design-principles)
- [Directory Structure](#directory-structure)
  - [Repository Strategy](#repository-strategy)
  - [Team Repository Layout](#team-repository-layout)
  - [Cross-Platform Databases](#cross-platform-databases)
- [Conventions & Standards](#conventions--standards)
  - [Platform Names](#platform-names)
  - [Database Names](#database-names)
  - [File Naming](#file-naming)
  - [Properties Files](#properties-files)
  - [Search Path Configuration](#search-path-configuration)
- [Advanced Patterns](#advanced-patterns)
  - [Master Changelog Pattern](#master-changelog-pattern)
  - [Release-Based Organization](#release-based-organization)
  - [Baseline Strategy](#baseline-strategy)
  - [Tracking Tables Configuration](#tracking-tables-configuration)
  - [Platform-Specific Changes](#platform-specific-changes)
  - [Contexts and Labels](#contexts-and-labels)
- [Deployment Architecture](#deployment-architecture)
  - [Docker Execution](#docker-execution)
  - [Kubernetes Init Containers](#kubernetes-init-containers)
  - [CI/CD Integration](#cicd-integration)
- [Scalability Patterns](#scalability-patterns)
- [Related Documentation](#related-documentation)

## Architecture Overview

### Scope

This architecture supports database schema management across multiple platforms and environments:

**Supported Platforms:**
- PostgreSQL, SQL Server, Snowflake, MongoDB
- Any future platform with a JDBC driver

**Deployment Environments:**
- `dev` → `test` → `stage` → `prod`

Changes are written once and promoted through environments using environment-specific connection properties.

### Key Decisions

| Decision | Rationale |
|:---|:---|
| **Separate repo per team** | Full isolation, standard GitHub permissions, independent deployments |
| **Shared GDS-owned repo** | Central `gds-liquibase-shared` for cross-platform databases (e.g., `dbadmin`) deployed by GDS to all platforms |
| **Application-first structure** | Organize by application first, then platform, then database—aligns with microservices/team ownership |
| **Environment-agnostic changelogs** | Same changes deploy everywhere; environment differences only in properties files |
| **Release-driven versioning** | Organize changes by release to simplify rollback, tagging, and deployment tracking |

[↑ Back to Table of Contents](#table-of-contents)

## Design Principles

1. **Single Source of Truth** — Changes written once, deploy identically to all environments
2. **Team Isolation** — Each team controls their own repository and deployment schedule
3. **Application-First Organization** — Directory structure mirrors business/product structure
4. **Shared Cross-Platform Databases** — GDS manages databases deployed to all platforms
5. **Release-Driven Versioning** — Changes grouped by release for clarity and safe rollback
6. **Environment-Specific Properties** — Connection details differ per environment; changes do not

For detailed rationale on each principle, see [Concepts Guide - Key Decisions](../concepts/liquibase/liquibase-concepts.md#key-decisions-to-make).

[↑ Back to Table of Contents](#table-of-contents)

## Directory Structure

Our architecture uses an **application-first organization** for changelogs. Each team repository has the same structure:

### Repository Strategy

Each team owns a **separate GitHub repository**:

```text
github.com/org/team-alpha-liquibase    # Team Alpha's changelogs
github.com/org/team-beta-liquibase     # Team Beta's changelogs
github.com/org/gds-liquibase-shared    # Shared modules (GDS owned, read-only for others)
```

**Benefits:**
- **Isolation**: Teams manage their own changes independently
- **Permissions**: Standard GitHub permissions control access
- **Independence**: Teams can version and deploy independently
- **Shared Modules**: Include `gds-liquibase-shared` as a Git submodule for cross-platform databases

### Team Repository Layout

Each team's repository uses this structure:

```text
# Example: team-alpha-liquibase repo
.
├── applications/
│   ├── payments_api/
│   │   ├── postgres/
│   │   │   └── orders/
│   │   │       ├── db.changelog-master.yaml
│   │   │       ├── baseline/
│   │   │       │   └── db.changelog-baseline.yaml
│   │   │       └── releases/
│   │   │           ├── 1.0/
│   │   │           ├── 1.1/
│   │   │           └── 2.0/
│   │   └── mssql/
│   │       └── legacy_orders/
│   │           ├── db.changelog-master.yaml
│   │           └── releases/...
│   └── inventory_svc/
│       ├── postgres/
│       │   └── catalog/
│       │       └── db.changelog-master.yaml
│       └── releases/...
├── shared/                              # Git submodule: gds-liquibase-shared
│   └── modules/
│       └── dbadmin/
│           ├── db.changelog-dbadmin-common.yaml
│           ├── postgres/
│           ├── mssql/
│           └── snowflake/
└── properties/
    ├── liquibase.payments_api.postgres.orders.dbinstance1.dev.properties.template
    ├── liquibase.payments_api.postgres.orders.dbinstance1.test.properties.template
    └── ...
```

**Directory Structure Key:**
- `applications/` — Organize by application name (matches microservice/team ownership)
- `<app_name>/` — Each application may span multiple databases/platforms
- `<platform>/` — PostgreSQL, MSSQL, Snowflake, MongoDB
- `<database>/` — Logical database name (e.g., `orders`, `catalog`, `legacy_orders`)
- `releases/` — Changes grouped by release version for clarity and safe rollback

### Cross-Platform Databases

The `gds-liquibase-shared` repository (owned by GDS) contains databases deployed to all platforms (e.g., `dbadmin`).

Use a **layered changelog approach** for platform-specific variations:

```text
shared/modules/dbadmin/
├── db.changelog-dbadmin-common.yaml      # All platforms
├── postgres/
│   └── db.changelog-dbadmin-postgres.yaml # PostgreSQL only
├── mssql/
│   └── db.changelog-dbadmin-mssql.yaml    # SQL Server only
├── snowflake/
│   └── db.changelog-dbadmin-snowflake.yaml
└── mongodb/
    └── db.changelog-dbadmin-mongodb.yaml
```

**Master Changelog** (in each platform folder) includes both layers:

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

[↑ Back to Table of Contents](#table-of-contents)

## Conventions & Standards

### Platform Names

Use lowercase names matching database technology:

```text
postgres/     # PostgreSQL
mssql/        # Microsoft SQL Server
snowflake/    # Snowflake Data Warehouse
mongodb/      # MongoDB
```

### Database Names

- **Existing Databases:** Directory name MUST match actual database name (e.g., `CustomerServiceDB`)
- **New Databases:** Use lowercase `snake_case` (e.g., `orders`, `catalog`, `customer_service`)

### File Naming

**Master Changelog:**
```text
db.changelog-master.yaml
```

**Release Changelogs:**
```text
releases/1.0/db.changelog-1.0.yaml
releases/2.0/db.changelog-2.0.yaml
```

**Individual Changesets:**
```text
001-create-customers-table.yaml
002-add-email-index.yaml
010-alter-customer-email-length.yaml    # Leave gaps for insertions
```

**Changeset IDs:**

Use format: `YYYYMMDD-HHMM-JIRA-description`

```yaml
changeSet:
  id: 20251114-1000-PROJ-123-create-customers
  author: team
  changes: ...
```

Why this format?
- **Date (`YYYYMMDD`)**: Natural chronological sorting
- **Uniqueness**: Time component (`HHMM`) prevents collisions
- **Traceability**: **Mandatory** Jira Ticket ID links to requirement
- **Readability**: Description makes intent clear

### Properties Files

**Naming Convention:**

`liquibase.<application>.<platform>.<database>.<dbinstance>.<environment>.properties`

**Example:**

```text
liquibase.payments_api.postgres.orders.dbinstance1.dev.properties
liquibase.inventory_svc.postgres.catalog.dbinstance1.prod.properties
```

**Naming Rules:**
- Use **snake_case** for multi-word names (e.g., `payments_api`)
- **No dashes** in application names
- All dimensions separated by periods

**Security:**
- ✅ Commit `.properties.template` files (no secrets)
- ✅ Generate actual `.properties` files at runtime from secrets manager
- ✅ Delete generated files immediately after use
- ❌ Never commit files containing passwords or API keys

### Search Path Configuration

Use `LIQUIBASE_SEARCH_PATH` environment variable to resolve relative paths:

```bash
# Local Dev
export LIQUIBASE_SEARCH_PATH=/home/user/src/my-repo

# Docker
docker run -e LIQUIBASE_SEARCH_PATH=/liquibase/changelog ...

# GitHub Actions
- uses: liquibase/liquibase-github-action@v4
  with:
    changelogFile: "applications/app1/postgres/orders/db.changelog-master.yaml"
    searchPath: "${{ github.workspace }}"
```

[↑ Back to Table of Contents](#table-of-contents)

## Advanced Patterns

### Master Changelog Pattern

Create a master changelog that includes all other changelogs for clarity:

```yaml
# db.changelog-master.yaml
databaseChangeLog:
  - include: { file: baseline/db.changelog-baseline.yaml }
  - include: { file: releases/1.0/db.changelog-1.0.yaml }
  - include: { file: releases/2.0/db.changelog-2.0.yaml }
```

### Release-Based Organization

Organize changes by release for clarity and easy rollback:

```text
releases/
  1.0/
    db.changelog-1.0.yaml
    001-create-tables.yaml
    002-add-indexes.yaml
  2.0/
    db.changelog-2.0.yaml
    001-refactor-customer-table.yaml
```

**Benefits:**
- Clear version history aligned with application versioning
- Easy rollback to known-good states (tag releases)
- Simple changelog navigation

### Baseline Strategy

For existing databases, create a baseline snapshot to avoid re-running complex historical schemas:

```bash
# Generate baseline
liquibase generate-changelog --changelog-file=baseline/db.changelog-baseline.yaml

# Mark as applied (don't re-run)
liquibase changelog-sync
```

Master changelog includes baseline:

```yaml
databaseChangeLog:
  - include: { file: baseline/db.changelog-baseline.yaml }
  - tagDatabase: { tag: baseline }
  - include: { file: releases/1.0/db.changelog-1.0.yaml }
```

See [Operations Guide - Baseline Management](../../how-to/liquibase/liquibase-operations-guide.md#baseline-management) for detailed procedures.

### Tracking Tables Configuration

Liquibase creates two tracking tables. Configure their location based on platform:

**PostgreSQL/SQL Server/Snowflake (schema support):**
```properties
liquibase.liquibase-schema-name=liquibase
```

**MongoDB (no schema support):**
```properties
liquibase.database-changelog-table-name=liquibase_changelog
liquibase.database-changelog-lock-table-name=liquibase_changelog_lock
```

### Platform-Specific Changes

Use the `dbms` attribute for small platform differences in shared changelogs:

```yaml
- changeSet:
    id: 20251220-01-add-json
    dbms: postgresql
    changes:
      - addColumn:
          tableName: config
          columns:
            - column: { name: settings, type: jsonb }
```

For larger divergence, use separate files in platform-specific folders.

### Contexts and Labels

Use sparingly to control conditional execution:

- **Contexts:** Filter by environment (e.g., `context: dev` for test data)
- **Labels:** Tag changesets for selective deployment (e.g., `labels: 'db:app,platform:postgres'`)

**Best Practice:** Keep schema changes environment-agnostic. Use contexts only for non-production test data.

[↑ Back to Table of Contents](#table-of-contents)

## Deployment Architecture

### Docker Execution

Run Liquibase in Docker for consistent, reproducible deployments:

```bash
docker run \
  -v "$(pwd)":/liquibase/changelog \
  -e LIQUIBASE_SEARCH_PATH=/liquibase/changelog \
  -e LIQUIBASE_URL=jdbc:postgresql://postgres:5432/mydb \
  -e LIQUIBASE_USERNAME=user \
  liquibase/liquibase:latest update
```

**Key Practices:**
- Mount repository to standard path (`/liquibase/changelog`)
- Set `LIQUIBASE_SEARCH_PATH` to resolve relative paths
- Pass credentials via environment variables or mounted secrets file (not raw command line)

### Kubernetes Init Containers

Deploy Liquibase as an **Init Container** before the application starts:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  initContainers:
  - name: liquibase-migrate
    image: liquibase/liquibase:latest
    env:
    - name: LIQUIBASE_SEARCH_PATH
      value: /liquibase/changelog
    volumeMounts:
    - name: changelog
      mountPath: /liquibase/changelog
  containers:
  - name: app
    image: my-app:latest
  volumes:
  - name: changelog
    configMap:
      name: changelog-configmap
```

**Benefits:**
- Migrations complete before app starts
- Linear execution avoids lock contention
- Fail fast: pod fails to start if migration fails

### CI/CD Integration

Deploy changes automatically in your CI/CD pipeline:

**GitHub Actions Example:**
```yaml
- uses: liquibase/liquibase-github-action@v4
  with:
    changelogFile: "applications/app1/postgres/orders/db.changelog-master.yaml"
    searchPath: "${{ github.workspace }}"
    url: ${{ secrets.DB_URL }}
    username: ${{ secrets.DB_USER }}
    password: ${{ secrets.DB_PASSWORD }}
    command: update
```

See [Operations Guide - Execution Patterns](../../how-to/liquibase/liquibase-operations-guide.md#execution-patterns) for more examples.

[↑ Back to Table of Contents](#table-of-contents)

## Scalability Patterns

### Managing Large Numbers of Databases

1. **Automated Database Discovery** — Auto-discover databases from configuration instead of hardcoding lists
2. **Parallel Deployments** — Deploy to independent databases in parallel to reduce total time
3. **Database Grouping** — Group databases for sequential vs parallel deployment via configuration file

### Monitoring at Scale

1. **Structured Logging** — Enable `log-format=JSON` for machine-readable logs ingested by Splunk, Datadog, ELK
2. **Deployment Metrics** — Track start/end times, success/failure rates via Prometheus, Datadog
3. **Deployment Dashboard** — Monitor failure rates, duration, and pending updates across all databases

[↑ Back to Table of Contents](#table-of-contents)

## Related Documentation

**Start here:** [Liquibase Documentation Index](../README.md)

- **[Liquibase Concepts Guide](../concepts/liquibase/liquibase-concepts.md)** — Foundational understanding (read first if new to Liquibase)
- **[Liquibase Operations Guide](../../how-to/liquibase/liquibase-operations-guide.md)** — Day-to-day tasks: authoring, deploying, troubleshooting
- **[Liquibase Reference](../../reference/liquibase/liquibase-reference.md)** — Command reference, glossary, limitations, troubleshooting
- **[Liquibase Secure Implementation Analysis](../liquibase-secure-implementation-analysis.md)** — Evaluating Pro/Secure features

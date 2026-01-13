# Liquibase Architecture Guide

**🔗 [← Back to Liquibase Documentation Index](../../liquibase/README.md)** — Navigation guide for all Liquibase docs

> **Document Version:** 1.0
> **Last Updated:** January 12, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production - Actively Maintained

![Liquibase Version](https://img.shields.io/badge/Liquibase-5.0%2B-blue)
![Document Status](https://img.shields.io/badge/Status-Production-green)

> [!IMPORTANT]
> **Related Docs:** [Concepts](../../concepts/liquibase/liquibase-concepts.md) | [Operations](../../../how-to/liquibase/liquibase-operations-guide.md) | [Reference](../../../reference/liquibase/liquibase-reference.md) | [Formatted SQL](../../../reference/liquibase/formatted-sql-guide.md)

## Table of Contents

- [Architecture Overview](#architecture-overview)
  - [Scope](#scope)
  - [Key Decisions](#key-decisions)
- [Design Principles](#design-principles)
- [Directory Structure](#directory-structure)
  - [Standard Layout](#standard-layout)
  - [Example Structure](#example-structure)
  - [Benefits](#benefits)
  - [Snapshot Naming](#snapshot-naming)
  - [Snapshot Strategy](#snapshot-strategy)
  - [Repository Strategy](#repository-strategy)
  - [Cross-Platform Database Example](#cross-platform-database-example)
- [Conventions & Standards](#conventions--standards)
  - [Platform Names](#platform-names)
  - [Database Names](#database-names)
  - [File Naming](#file-naming)
  - [Formatted SQL Structure](#formatted-sql-structure)
  - [Properties Files](#properties-files)
  - [Search Path Configuration](#search-path-configuration)
- [Advanced Patterns](#advanced-patterns)
  - [Master Changelog Pattern](#master-changelog-pattern)
  - [Benefits of SQL-First Approach](#benefits-of-sql-first-approach)
  - [Baseline Strategy](#baseline-strategy)
  - [Tracking Tables Configuration](#tracking-tables-configuration)
  - [Platform-Specific Changes](#platform-specific-changes)
  - [Contexts and Labels](#contexts-and-labels)
- [Deployment Architecture](#deployment-architecture)
  - [Docker Execution](#docker-execution)
  - [Kubernetes Init Containers](#kubernetes-init-containers)
  - [CI/CD Integration](#cicd-integration)
- [Scalability Patterns](#scalability-patterns)
  - [Managing Large Numbers of Databases](#managing-large-numbers-of-databases)
  - [Monitoring at Scale](#monitoring-at-scale)
- [Related Documentation](#related-documentation)
- [Appendix: Alternative Directory Structures](#appendix-alternative-directory-structures)
  - [Application-First Organization](#application-first-organization)
  - [Shared Changelog Patterns](#shared-changelog-patterns)

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
| **Separate repo per database** | Each database has its own GitHub repository, owned by the team responsible for that database |
| **Cross-platform in single repo** | If a database exists on multiple platforms, all platforms are managed in the same repo |
| **Platform-first structure** | Organize by platform first, then database—aligns with DBA workflows and infrastructure management |
| **Environment-agnostic changelogs** | Same changes deploy everywhere; environment differences only in properties files |
| **Release-driven versioning** | Organize changes by release to simplify rollback, tagging, and deployment tracking |

[↑ Back to Table of Contents](#table-of-contents)

## Design Principles

1. **Single Source of Truth** — Changes written once, deploy identically to all environments
2. **Database Ownership** — Each database has its own repository, owned by the responsible team
3. **Platform-First Organization** — Directory structure mirrors infrastructure and DBA workflows
4. **Cross-Platform in Single Repo** — Databases spanning multiple platforms are managed in one repository
5. **Release-Driven Versioning** — Changes grouped by release for clarity and safe rollback
6. **Environment-Specific Properties** — Connection details differ per environment; changes do not

For detailed rationale on each principle, see [Concepts Guide - Key Decisions](../../concepts/liquibase/liquibase-concepts.md#key-decisions-to-make).

[↑ Back to Table of Contents](#table-of-contents)

## Directory Structure

The chosen directory structure uses a **platform-first organization** for changelogs.

### Standard Layout

```text
platform/<platform>/database/<database_name>/
├── changelog/       # All changelogs and changesets
├── env/             # Ephemeral generated properties (not committed)
└── snapshots/       # Database snapshots for drift detection
```

### Example Structure

```text
platform/
└── mssql/
    └── database/
        ├── orderdb/
        │   ├── changelog/
        │   │   ├── changelog.xml                  # Master entry point (XML/YAML wrapper)
        │   │   ├── baseline/
        │   │   │   └── V0000__baseline.mssql.sql  # Initial state
        │   │   └── changes/
        │   │       ├── V202601121200__PROJ-101_create_customers.mssql.sql
        │   │       └── V202601121430__PROJ-102_add_email_index.mssql.sql
        │   ├── env/                      # Generated at runtime
        │   └── snapshots/
        │       └── dbinstance1_prod-pre_deploy-20260112_1200.json
        ├── inventorydb/
        │   ├── changelog/
        │   ├── env/
        │   └── snapshots/
        └── customerdb/
            ├── changelog/
            ├── env/
            └── snapshots/
```


**Directory Structure Key:**
- `platform/` — Top-level organization by database platform
- `<platform>/` — Platform name: `mssql`, `postgres`, `snowflake`, `mongodb`
- `database/` — Container for all databases on this platform
- `<database_name>/` — Actual name of the database (e.g., `orderdb`, `inventorydb`)
- `changelog/` — All changelogs and changesets for this database
- `env/` — Ephemeral properties files (generated during build/deploy)
- `snapshots/` — Database snapshots for drift detection and audit (`<dbinstance>-<trigger>-<timestamp>.json`)

### Benefits

- **Clear Separation**: Each database has isolated changelog, env, and snapshot folders
- **Drift Management**: Dedicated snapshots folder supports drift detection workflows
- **Snapshot Context**: Filenames capture specific lifecycle events (pre-deploy, post-deploy) for easier auditing
- **Security**: Properties files are ephemeral and never committed

### Snapshot Naming

**Pattern:**
`<dbinstance>-<trigger>-<timestamp>.json`

**Example:**
`dbinstance1_prod-pre_deploy-20260112_1200.json`

**Lifecycle Triggers:**
- `pre_deploy`: Taken prior to `update` command as a safety rollback point.
- `post_deploy`: Taken immediately after successful `update` for audit verification.
- `drift_check`: Taken during scheduled drift detection jobs.
- `manual`: Ad-hoc snapshot for debugging or local development.

### Snapshot Strategy

**Why take snapshots?**
- **Immutable Record**: Provides detailed proof of the schema state at time $T$.
- **Drift Baseline**: Serves as a comparison point for future `diff` commands to detect unauthorized changes.
- **Debugging**: Instant visibility into past states without restoring full database backups.

> [!IMPORTANT]
> **Mandate**: Always generate a `post_deploy` snapshot to guarantee an observable audit trail.

**Example Snapshot Content:**

```json
{
  "databaseChangeLog": [
    {
      "changeSet": {
        "id": "generated-snapshot",
        "author": "liquibase",
        "changes": [
          {
            "createTable": {
              "tableName": "customers",
              "columns": [
                {
                  "column": {
                    "name": "id",
                    "type": "INT",
                    "constraints": {
                      "primaryKey": true
                    }
                  }
                }
              ]
            }
          }
        ]
      }
    }
  ]
}
```

### Repository Strategy

Each database has its own **GitHub repository**, owned by the team responsible for that database:

```text
github.com/org/orderdb       # Order database (owned by Orders team)
github.com/org/inventorydb   # Inventory database (owned by Inventory team)
github.com/org/admin         # Admin database (owned by DBA team)
```

**Benefits:**
- **Isolation**: Each database has independent version control and deployment
- **Ownership**: Team that owns the database owns the repo
- **Permissions**: Standard GitHub permissions control access per database
- **Cross-Platform Support**: Single repo manages all platforms where the database exists

### Cross-Platform Database Example

If a database exists on multiple platforms (e.g., `Admin` database on MSSQL, PostgreSQL, Snowflake, and MongoDB), the single repository contains all platforms:

```text
# admin-liquibase repo
.
├── platform/
│   ├── mssql/
│   │   └── database/
│   │       └── Admin/
│   │           ├── changelog/
│   │           │   ├── changelog.xml
│   │           │   └── changes/
│   │           │   └── changes/
│   │           ├── env/
│   │           └── snapshots/
│   ├── postgres/
│   │   └── database/
│   │       └── Admin/
│   │           ├── changelog/
│   │           │   ├── changelog.xml
│   │           │   └── changes/
│   │           ├── env/
│   ├── snowflake/
│   │   └── database/
│   │       └── Admin/
│   │           ├── changelog/
│   │           ├── env/
│   │           └── snapshots/
│   └── mongodb/
│       └── database/
│           └── Admin/
│               ├── changelog/
│               ├── env/
│               └── snapshots/
└── README.md
```

**Cross-Platform Benefits:**
- **Single Source of Truth**: All platforms for a database managed together
- **Coordinated Changes**: Easy to apply similar changes across platforms
- **Platform-Specific Variations**: Each platform has its own changelog for platform-specific SQL

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

### File Naming

**Master Changelog:**
```text
changelog.xml (or db.changelog-master.yaml)
```

**Formatted SQL Files:**
Enforce the `V` prefix pattern for strict ordering and traceability.

**Pattern:**
`V<timestamp>__<jira_ticket>_<description>.<database_type>.sql`

**Examples:**
```text
V202601121200__PROJ-123_create_customers_table.mssql.sql
V202601121430__PROJ-124_add_email_index.postgres.sql
```

**Rationale:**
- **`V` Prefix**: Standard for migration tools (Flyway/Liquibase) compatibility.
- **Timestamp (`YYYYMMDDHHMM[SS]`)**: Ensures chronological execution order. For multiple changes in the same timeframe, increment the minute, second, or append a sequence number to guarantee correct ASCII sort order.
- **Jira Ticket**: **Mandatory** link to requirements/audit.
- **`.databaseType.sql`**: **Required** for Liquibase 5.x+ to correctly parse Formatted SQL. Using just `.sql` may cause serialization errors.

### Formatted SQL Structure

Use **Formatted SQL** comments to define changesets within the SQL file.

```sql
--liquibase formatted sql

--changeset team-a:20260112-001-create-users context:dev labels:v1.0
CREATE TABLE users (
    id INT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100)
);
--rollback DROP TABLE users;

--changeset team-a:20260112-002-add-active-flag runOnChange:true
ALTER TABLE users ADD active BOOLEAN DEFAULT true;
--rollback ALTER TABLE users DROP COLUMN active;
```

**Why Formatted SQL?**
- **Auditability**: The file content is exactly what is executed on the database. No "black box" XML generation.
- **Portability**: If you leave Liquibase, you have valid SQL scripts (just strip the comments).
- **Control**: Full access to database-specific syntax without waiting for XML tag support.

### Properties Files

**Naming Convention:**

`<prefix>.<dbinstance>_<env>.properties.template`

**Example:**

```text
liquibase.dbinstance1_dev.properties.template
liquibase.dbinstance1_prod.properties.template
```

**Naming Rules:**

**Security:**
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
    changelogFile: "platform/postgres/database/orders/changelog/changelog.xml"
    searchPath: "${{ github.workspace }}"
```

[↑ Back to Table of Contents](#table-of-contents)

## Advanced Patterns

### Master Changelog Pattern

The master changelog orchestrates the execution order. It typically includes the baseline first, then all incremental changes.

```xml
<!-- changelog.xml -->
<databaseChangeLog
  xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                      http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-latest.xsd">

    <!-- 1. Baseline (Initial State) -->
    <include file="baseline/V0000__baseline.mssql.sql"/>

    <!-- 2. Incremental Changes (Sorted by filename/timestamp) -->
    <includeAll path="changes/"/>

</databaseChangeLog>
```

### Benefits of SQL-First Approach

- **Simplicity**: No need to maintain complex nested release directories (`releases/1.0/`).
- **Linear History**: The `V<timestamp>` naming ensures a clear, linear history of changes in the `changes/` folder.
- **Reviewability**: PR reviewers see raw SQL, making it easier to spot syntax errors or performance issues clearly.

### Baseline Strategy

For existing databases, create a baseline snapshot to avoid re-running complex historical schemas:

```bash
# Generate baseline
liquibase generate-changelog --changelog-file=baseline/V0000__baseline.posgres.sql

# Mark as applied (don't re-run)
liquibase changelog-sync
```

Master changelog includes baseline:

```yaml
### Baseline Strategy

For existing databases, create a baseline to avoid re-running complex historical schemas.

```bash
# Generate baseline
liquibase generate-changelog \
    --changelog-file=baseline/V0000__baseline.mssql.sql \
    --overwrite-output-file=true
```

**Master Changelog Integration:**

```xml
<databaseChangeLog ...>
    <include file="baseline/V0000__baseline.mssql.sql"/>
    <tagDatabase tag="baseline"/>
    <includeAll path="changes/"/>
</databaseChangeLog>
```

See [Operations Guide - Baseline Management](../../../how-to/liquibase/liquibase-operations-guide.md#baseline-management) for detailed procedures.

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

```sql
--changeset team:20260112-add-json dbms:postgresql
ALTER TABLE config ADD settings JSONB;

--changeset team:20260112-add-json dbms:mssql
ALTER TABLE config ADD settings NVARCHAR(MAX);
```

For larger divergence, use separate files in platform-specific folders.

### Contexts and Labels

Use sparingly to control conditional execution:

- **Contexts:** Filter by environment.
  ```sql
  --changeset team:seed-data context:dev
  INSERT INTO users (name) VALUES ('Test User');
  ```
- **Labels:** Tag changesets for selective deployment.
  ```sql
  --changeset team:feature-x labels:beta
  ```

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
    changelogFile: "platform/postgres/database/orders/changelog/changelog.xml"
    searchPath: "${{ github.workspace }}"
    url: ${{ secrets.DB_URL }}
    username: ${{ secrets.DB_USER }}
    password: ${{ secrets.DB_PASSWORD }}
    command: update
```


See [Operations Guide - Execution Patterns](../../../how-to/liquibase/liquibase-operations-guide.md#execution-patterns) for more examples.

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

**Start here:** [Liquibase Documentation Index](../../liquibase/README.md)

- **[Liquibase Concepts Guide](../../concepts/liquibase/liquibase-concepts.md)** — Foundational understanding (read first if new to Liquibase)
- **[Liquibase Operations Guide](../../../how-to/liquibase/liquibase-operations-guide.md)** — Day-to-day tasks: authoring, deploying, troubleshooting
- **[Liquibase Reference](../../../reference/liquibase/liquibase-reference.md)** — Command reference, glossary, limitations, troubleshooting
- **[Liquibase Secure Implementation Analysis](../../liquibase/liquibase-secure-implementation-analysis.md)** — Evaluating Pro/Secure features

[↑ Back to Table of Contents](#table-of-contents)

## Appendix: Alternative Directory Structures

The following alternative directory structures may be useful in specific scenarios.

### Application-First Organization

An **application-first** structure organizes by application name first, then platform, then database. This approach aligns with microservices and team ownership patterns:

```text
# Example: team-alpha-liquibase repo
.
├── applications/
│   ├── payments_api/
│   │   ├── postgres/
│   │   │   └── orders/
│   │   │       ├── changelog.xml
│   │   │       ├── baseline/
│   │   │       │   └── V0000__baseline.postgres.sql
│   │   │       └── changes/
│   │   │           ├── V20260112__100_init.postgres.sql
│   │   │           └── ...
│   │   └── mssql/
│   │       └── legacy_orders/
│   │           ├── changelog.xml
│   │           └── changes/...
│   └── inventory_svc/
│       ├── postgres/
│       │   └── catalog/
│       │       ├── changelog.xml
│       │       └── changes/
├── shared/                              # Git submodule: gds-liquibase-shared
│   └── modules/
│       └── dbadmin/
│           ├── V0000__dbadmin_common.sql
│           ├── postgres/
│           ├── mssql/
│           └── snowflake/
└── properties/                           # Generator scripts or local config
```

**When to use:**
- Microservices architecture where each team owns their databases
- Application teams manage their own schema changes
- Databases are tightly coupled to specific applications

### Shared Changelog Patterns

For cross-platform databases where you want to **share common changelog code** across platforms, use a **layered changelog approach** with a shared directory:

```text
# admin-liquibase repo with shared changelogs
.
├── shared/
│   └── common/
│       └── V0000__common_objects.sql     # Changes that work on all platforms
├── platform/
│   ├── mssql/
│   │   └── database/
│   │       └── Admin/
│   │           └── changelog/
│   │               └── changelog.xml
│   ├── postgres/
│   │   └── database/
│   │       └── Admin/
│   │           └── changelog/
│   │               └── changelog.xml
│   └── ...
```

**Master Changelog** includes both shared and platform-specific layers:

```xml
<!-- platform/postgres/database/Admin/changelog/changelog.xml -->
<databaseChangeLog ...>
  <!-- Layer 1: Common objects (all platforms) -->
  <include file="../../../../shared/common/V0000__common_objects.sql"/>

  <!-- Layer 2: PostgreSQL-specific objects -->
  <includeAll path="changes/"/>

</databaseChangeLog>
```

**When to use:**
- Database schema is largely identical across platforms
- Want to avoid duplicating changelog entries
- Platform differences are minimal and can be handled with `dbms` attribute

[↑ Back to Table of Contents](#table-of-contents)

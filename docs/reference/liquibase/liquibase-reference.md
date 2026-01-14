# Liquibase Reference

**🔗 [← Back to Liquibase Documentation Index](../../explanation/liquibase/README.md)** — Navigation guide for all Liquibase docs

> **Document Version:** 1.0
> **Last Updated:** January 12, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production
![Document Status](https://img.shields.io/badge/Status-Production-green)
 
> [!IMPORTANT]
> **Related Docs:** [Concepts](../../explanation/liquibase/liquibase-concepts.md) | [Architecture](../../explanation/liquibase/liquibase-architecture.md) | [Operations](../../how-to/liquibase/liquibase-operations-guide.md) | [Drift Management](../../explanation/liquibase/liquibase-drift-management.md) | [Formatted SQL](./liquibase-formatted-sql-guide.md)

This document serves as a reference for Liquibase features, limitations, configuration, and troubleshooting. Use this to look up specific commands, attributes, and error messages.

> [!NOTE]
> For foundational understanding, see the [Concepts Guide](../../explanation/liquibase/liquibase-concepts.md). For day-to-day tasks, see the [Operations Guide](../../how-to/liquibase/liquibase-operations-guide.md).

## Table of Contents

- [Edition Differences](#edition-differences)
  - [Liquibase Community](#liquibase-community)
  - [Liquibase Secure](#liquibase-secure)
- [Drift Detection Reference](#drift-detection-reference)
  - [Drift Detection Commands](#drift-detection-commands)
  - [Drift Detection Supported Objects](#drift-detection-supported-objects)
  - [diffTypes Parameter Values](#difftypes-parameter-values)
- [Liquibase Limitations](#liquibase-limitations)
  - [Schema Management](#schema-management)
  - [Other Limitations](#other-limitations)
- [MongoDB Platform Reference](#mongodb-platform-reference)
  - [Connection String](#connection-string)
  - [Extension Change Types](#extension-change-types)
  - [Example Changelog](#example-changelog)
  - [Tracking Collections](#tracking-collections)
  - [Limitations](#limitations)
- [Configuration Reference](#configuration-reference)
  - [Environment Variables](#environment-variables)
- [ChangeSet Attributes Reference](#changeset-attributes-reference)
- [Flowfile Actions Reference](#flowfile-actions-reference)
- [Performance Tuning](#performance-tuning)
- [Troubleshooting](#troubleshooting)
  - [Lock Issues](#lock-issues)
  - [Checksum Mismatches](#checksum-mismatches)
  - [Manual Interventions](#manual-interventions)
- [Glossary](#glossary)
- [References](#references)
  - [Official Documentation](#official-documentation)
  - [Internal Documentation](#internal-documentation)

## Edition Differences

### Liquibase Community

**Included:**

- Core DDL object management (tables, views, indexes, etc.)
- Standard changelog formats (YAML, JSON, XML, SQL)
- Basic drift detection (`diff`, `diffChangeLog`)
- Rollback by tag, count, or date

**Limitations:**

- ⚠️ **Stored Logic**: Limited support for procedures, functions, triggers. Requires manual SQL changeSets.
- No automated extraction of stored logic.
- No advanced policy checks or compliance reporting.

[↑ Back to Table of Contents](#table-of-contents)

### Liquibase Secure

Liquibase Secure (formerly Pro/Enterprise) adds governance, observability, and advanced automation.

**Missing Features & Community Alternatives:**

| Secure Feature | Community Alternative | Trade-off |
| :--- | :--- | :--- |
| **Flow Files** | Shell Scripts | More verbose, OS-dependent |
| **Policy Checks** | SQLFluff / Custom Linters | Manual setup, no database-awareness |
| **Drift Reporting** | `diff` command | Manual parsing of text output |
| **Targeted Rollback** | Manual Rollback SQL | Higher risk of human error |
| **Stored Logic Extraction** | Manual SQL files | Requires discipline to manage |

**Recommendation**: Start with Community. If orchestration or compliance overhead becomes too high (e.g., managing 100+ pipelines), evaluate Secure.

## Drift Detection Reference

> **📖 Concept:** For background on what drift is and why it matters, see [Understanding Database Drift](../../explanation/liquibase/liquibase-drift-management.md).
> **📋 How-to:** For step-by-step procedures, see [Operations Guide - Drift Detection](../../how-to/liquibase/liquibase-operations-guide.md#drift-detection-and-remediation).

### Drift Detection Commands

| Command | Description | Output |
|---------|-------------|--------|
| `snapshot` | Capture current database state | JSON file |
| `diff` | Compare two database states | Text report |
| `diffChangeLog` | Generate changelog from differences | XML/YAML/SQL file |
| `updateSQL` | Preview SQL without executing | SQL statements |
| `rollbackSQL` | Preview rollback SQL | SQL statements |
| `changelogSync` | Mark changesets as executed | Updates DATABASECHANGELOG |

**Snapshot Command:**

```bash
liquibase snapshot \
  --url="jdbc:postgresql://localhost:5432/mydb" \
  --schemas=app \
  --snapshot-format=json \
  --output-file=snapshots/dbinstance1_prod-manual-20260112.json
```

**Diff Command (against snapshot):**

```bash
liquibase diff \
  --url="jdbc:postgresql://localhost:5432/mydb" \
  --schemas=app \
  --referenceUrl="offline:postgresql?snapshot=snapshots/dbinstance1_prod-manual-20260112.json"
```

**Diff Command (between databases):**

```bash
liquibase diff \
  --url="jdbc:postgresql://localhost:5432/target_db" \
  --referenceUrl="jdbc:postgresql://localhost:5432/reference_db" \
  --referenceUsername=user \
  --referencePassword=pass
```

**DiffChangeLog Command:**

```bash
# Generate YAML changelog
liquibase diffChangeLog \
  --changelog-file=drift/drift_remediation.xml \
  --referenceUrl="offline:postgresql?snapshot=snapshots/dbinstance1_prod-manual-20260112.json"

# Generate platform-specific SQL
liquibase diffChangeLog \
  --changelog-file=drift/V20260112__drift_fix.postgres.sql \
  --referenceUrl="offline:postgresql?snapshot=snapshots/dbinstance1_prod-manual-20260112.json"
```

### Drift Detection Supported Objects

Liquibase can detect drift across different object types depending on the database platform and license edition.

#### SQL Server (MSSQL)

| Object Type | Community | Pro | Notes |
|-------------|:---------:|:---:|-------|
| Tables | ✅ | ✅ | Full support |
| Columns | ✅ | ✅ | Data types, nullability, defaults |
| Primary Keys | ✅ | ✅ | |
| Foreign Keys | ✅ | ✅ | |
| Indexes | ✅ | ✅ | Clustered, non-clustered, filtered |
| Unique Constraints | ✅ | ✅ | |
| Views | ✅ | ✅ | Definition changes detected |
| Sequences | ✅ | ✅ | |
| Schemas | ✅ | ✅ | |
| Check Constraints | ❌ | ✅ | Pro only |
| Stored Procedures | ❌ | ✅ | Pro only - checksum comparison |
| Functions | ❌ | ✅ | Pro only - scalar, table-valued |
| Triggers | ❌ | ✅ | Pro only |
| Synonyms | ❌ | ✅ | Pro only |
| Data (row-level) | ❌ | ✅ | Secure only - with `diffTypes=data` |

#### PostgreSQL

| Object Type | Community | Pro | Notes |
|-------------|:---------:|:---:|-------|
| Tables | ✅ | ✅ | Including partitioned tables |
| Columns | ✅ | ✅ | Data types, nullability, defaults |
| Primary Keys | ✅ | ✅ | |
| Foreign Keys | ✅ | ✅ | |
| Indexes | ✅ | ✅ | B-tree, GIN, GiST, etc. |
| Unique Constraints | ✅ | ✅ | |
| Views | ✅ | ✅ | Regular and materialized |
| Sequences | ✅ | ✅ | |
| Schemas | ✅ | ✅ | |
| Check Constraints | ❌ | ✅ | Pro only |
| Stored Procedures | ❌ | ✅ | Pro only (PostgreSQL 11+) |
| Functions | ❌ | ✅ | Pro only |
| Triggers | ❌ | ✅ | Pro only |
| Extensions | ❌ | ❌ | Not supported - manual tracking required |
| Row-Level Security | ❌ | ❌ | Not supported - manual tracking required |
| Data (row-level) | ❌ | ✅ | Pro only |

#### Snowflake

Snowflake's architecture differs from traditional RDBMS, so some object types don't exist.

| Object Type | Community | Pro | Notes |
|-------------|:---------:|:---:|-------|
| Tables | ✅ | ✅ | Regular, transient, temporary |
| Columns | ✅ | ✅ | Data types, nullability |
| Primary Keys | ✅ | ✅ | Informational only in Snowflake |
| Foreign Keys | ✅ | ✅ | Informational only in Snowflake |
| Unique Constraints | ✅ | ✅ | Informational only in Snowflake |
| Views | ✅ | ✅ | Regular and secure views |
| Sequences | ✅ | ✅ | |
| Schemas | ✅ | ✅ | |
| Stored Procedures | ❌ | ✅ | Pro only - JavaScript, SQL, Python |
| Functions (UDFs) | ❌ | ✅ | Pro only |
| Stages | ❌ | ✅ | Pro only - internal and external |
| File Formats | ❌ | ✅ | Pro only |
| Streams | ❌ | ❌ | Not supported - manual tracking required |
| Tasks | ❌ | ❌ | Not supported - manual tracking required |
| Pipes | ❌ | ❌ | Not supported - manual tracking required |
| Indexes | N/A | N/A | Snowflake doesn't use traditional indexes |
| Triggers | N/A | N/A | Snowflake doesn't support triggers |

> **Note:** Constraints in Snowflake are informational/metadata only and not enforced by the database.

#### MongoDB

MongoDB is a document database with different capabilities than relational databases.

| Object Type | Community | Pro | Notes |
|-------------|:---------:|:---:|-------|
| Collections | ✅ | ✅ | Equivalent to tables |
| Indexes | ✅ | ✅ | Single-field, compound, text, geospatial |
| Validators | ✅ | ✅ | JSON Schema validation rules |
| Views | ✅ | ✅ | Aggregation pipeline views |
| Documents (data) | ❌ | ✅ | Pro only - sample comparison |

**MongoDB Limitations:**

| Feature | Supported | Notes |
|---------|:---------:|-------|
| `diff` | ✅ | Supported in Liquibase 4.32.0+ |
| `snapshot` | ✅ | Supported in Liquibase 4.32.0+ |
| `diffChangeLog` | ❌ | **Not supported** - manual changeset required |
| `generateChangeLog` | ❌ | **Not supported** - manual changeset required |

> **Important:** Unlike relational databases, Liquibase **cannot automatically generate changelogs** from MongoDB drift. You can detect drift, but you must manually create changesets to remediate it.

#### Summary: Detection vs. Generation

| Platform | Drift Detection | Auto-Generate Changelog | Manual Changeset Needed |
|----------|:---------------:|:-----------------------:|:-----------------------:|
| SQL Server | ✅ Full | ✅ Most objects | Complex procedures |
| PostgreSQL | ✅ Full | ✅ Most objects | Extensions, RLS |
| Snowflake | ✅ Full | ✅ Most objects | Streams, Tasks, Pipes |
| MongoDB | ✅ Full | ❌ Not supported | All remediations |

### diffTypes Parameter Values

Control which objects are included in drift detection:

```bash
# Default types (Community)
liquibase diff  # tables, columns, foreignkeys, indexes, primarykeys, uniqueconstraints, views

# Specific types only
liquibase diff --diffTypes="tables,indexes"

# All types including Pro objects
liquibase diff --diffTypes="catalogs,checkconstraints,columns,data,foreignkeys,functions,indexes,primarykeys,sequences,storedprocedures,tables,triggers,uniqueconstraints,views"
```

| Value | Description | License |
|-------|-------------|---------|
| `catalogs` | Database catalogs | Community |
| `checkconstraints` | Check constraints | Pro |
| `columns` | Table columns | Community |
| `data` | Row-level data comparison | Pro |
| `databasepackages` | Oracle packages | Pro |
| `databasepackagebody` | Oracle package bodies | Pro |
| `foreignkeys` | Foreign key constraints | Community |
| `functions` | User-defined functions | Pro |
| `indexes` | Table indexes | Community |
| `primarykeys` | Primary key constraints | Community |
| `sequences` | Sequence objects | Community |
| `storedprocedures` | Stored procedures | Pro |
| `tables` | Database tables | Community |
| `triggers` | Database triggers | Pro |
| `uniqueconstraints` | Unique constraints | Community |
| `views` | Database views | Community |

[↑ Back to Table of Contents](#table-of-contents)

## Liquibase Limitations

### Schema Management

**Important**: Liquibase **does not manage database schemas** (CREATE SCHEMA).

- ❌ `generateChangeLog` will NOT create `CREATE SCHEMA` statements.
- ⚠️ **Schemas must exist before running Liquibase**.
- **Workaround**: Create schemas manually, via IAC (Terraform), or use a raw SQL changeset at the very beginning of your project.

### Other Limitations

- ❌ **Security**: Database users, roles, and grants are generally not captured.
- ❌ **SQL Server**: Extended properties/descriptions are not captured.
- ❌ **Computed Columns**: May be captured incorrectly.

[↑ Back to Table of Contents](#table-of-contents)

## MongoDB Platform Reference

MongoDB is supported via the [liquibase-mongodb](https://github.com/liquibase/liquibase-mongodb) extension.

### Connection String

MongoDB uses a connection string (not JDBC):

```properties
url=mongodb://localhost:27017/mydb
# Or with authentication
url=mongodb://user:password@host:27017/mydb?authSource=admin
```

### Extension Change Types

MongoDB uses `ext:` prefixed change types:

| Change Type | Description |
|:---|:---|
| `ext:createCollection` | Create a collection |
| `ext:dropCollection` | Drop a collection |
| `ext:createIndex` | Create an index |
| `ext:dropIndex` | Drop an index |
| `ext:insertMany` | Insert documents |
| `ext:insertOne` | Insert a single document |
| `ext:runCommand` | Run raw MongoDB command |
| `ext:adminCommand` | Run admin command |

### Example Changelog

```yaml
databaseChangeLog:
  - changeSet:
      id: 20251220-01-create-users-collection
      author: platform_ops
      changes:
        - ext:createCollection:
            collectionName: users
            options:
              validator:
                $jsonSchema:
                  bsonType: object
                  required: ["email", "created_at"]
                  properties:
                    email:
                      bsonType: string
                    created_at:
                      bsonType: date

  - changeSet:
      id: 20251220-02-create-email-index
      author: platform_ops
      changes:
        - ext:createIndex:
            collectionName: users
            keys: { email: 1 }
            options: { unique: true, name: idx_users_email }
```

### Tracking Collections

Since MongoDB has no schemas, tracking tables become collections with `liquibase_` prefix:

```properties
liquibase.database-changelog-table-name=liquibase_changelog
liquibase.database-changelog-lock-table-name=liquibase_changelog_lock
```

### Limitations

- Fewer built-in change types than relational databases
- Some operations require `ext:runCommand` with raw MongoDB syntax
- No automatic schema extraction (`generateChangeLog` limited)

[↑ Back to Table of Contents](#table-of-contents)

## Configuration Reference

### Environment Variables

| Variable | Property | Description |
| :--- | :--- | :--- |
| `LIQUIBASE_SEARCH_PATH` | `searchPath` | List of directories to search for changelogs |
| `LIQUIBASE_LOG_FORMAT` | `logFormat` | Set to `JSON` for machine-readable logs |
| `LIQUIBASE_LOG_LEVEL` | `logLevel` | Logging verbosity (`INFO`, `DEBUG`, `off`) |
| `LIQUIBASE_COMMAND_URL` | `url` | JDBC Connection URL |
| `LIQUIBASE_COMMAND_USERNAME` | `username` | Database Username |
| `LIQUIBASE_COMMAND_PASSWORD` | `password` | Database Password |
| `LIQUIBASE_LICENSE_KEY` | `licenseKey` | Pro License Key |

[↑ Back to Table of Contents](#table-of-contents)

## ChangeSet Attributes Reference

Beyond basic `id` and `author`, changesets support these advanced attributes:

| Attribute | Default | Description |
|:---|:---|:---|
| `runOnChange` | `false` | Re-execute changeset when its content changes. Use for views, procedures, or functions with `CREATE OR REPLACE` logic. |
| `runAlways` | `false` | Execute every deployment, regardless of history. Use for timestamps or data that must be refreshed. |
| `failOnError` | `true` | If `false`, continue deployment even if this changeset fails. Use cautiously. |
| `logicalFilePath` | (physical path) | Override the path stored in `DATABASECHANGELOG`. Useful when reorganizing files without breaking history. |
| `runOrder` | (natural) | Set to `first` or `last` to control execution order relative to other changesets. |
| `context` | (none) | Only run in matching contexts (e.g., `context: dev`). |
| `labels` | (none) | Tag changesets for filtering (e.g., `labels: 'db:app'`). |

**Example: runOnChange for Views**

```sql
--changeset platform-team:create-user-summary-view runOnChange:true
CREATE OR REPLACE VIEW user_summary AS
SELECT id, email, created_at FROM users WHERE active = true;
```

**Example: dbms attribute for Platform-Specific SQL**

```sql
--changeset platform-team:create-orders-table dbms:mysql
CREATE TABLE orders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY
) ENGINE=InnoDB;

--changeset platform-team:create-orders-table dbms:postgresql
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY
);
```

## Flowfile Actions Reference (Secure Only)

> **Note:** Community users should use shell scripts for orchestration. See [Operations Guide](../../how-to/liquibase/liquibase-operations-guide.md#orchestration-community-shell-scripts).

Common actions used in `liquibase.flowfile.yaml`:

- `validate`: Checks changelog for errors.
- `checks run`: Executes policy checks.
- `update`: Deploys pending changes.
- `rollback`: Rolls back changes.
- `history`: Shows deployment history.
- `status`: Shows pending changes.
- `shell`: Execute arbitrary shell commands (e.g., `echo`, `aws`).

[↑ Back to Table of Contents](#table-of-contents)

## Performance Tuning

### Handling Large Data

> [!WARNING]
> **Avoid `loadData` for bulk imports.** Liquibase's `loadData` is slow for datasets > 1000 rows.

**Recommendation:**
1.  **Native Tools:** Use database-specific bulk tools (`COPY` for Postgres, `BCP` for SQL Server, `SQLLoader` for Oracle).
2.  **External Scripts:** Wrap these calls in a shell script or custom extension.
3.  **Disable Indexing:** Drop indexes before load, recreate after.

### Transaction Management

By default, Liquibase runs each changeset in a transaction.
-   **Performance:** For massive updates, standard transactions may fill undo logs.
-   **Optimization:** Use `runInTransaction:false` for long-running operations or creating indexes concurrently.

```sql
--changeset team:add-index-concurrently runInTransaction:false
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```

### Optimizing Changelogs

-   **Split Files:** Don't keep all history in one file. Split by release or object type.
-   **IncludeAll:** Use `<includeAll>` for rapid scanning of timestamped files.
-   **Status Check:** `liquibase status --verbose` can be slow on large changelogs. Use standard `status` for quick checks.

[↑ Back to Table of Contents](#table-of-contents)

## Troubleshooting

### Lock Issues

**Symptom:** "Waiting for changelog lock..."
**Cause:** Previous deployment crashed or multiple pipelines running.
**Fix:**
```bash
liquibase releaseLocks
```

### Checksum Mismatches

**Symptom:** "Validation Failed: Checksum changed for changeset..."
**Cause:** A deployed file was modified locally.
**Fix:**
1.  **Revert:** Undo local changes to match deployed version.
2.  **New Changeset:** Add new logic in a *new* file.
3.  **Emergency:** `liquibase clearCheckSums` (Forces re-calculation).

### Slow Deployments

**Symptom:** `update` takes forever.
**Cause:** Large data operations, missing indexes, or network latency.
**Fix:**
-   Check "Performance Tuning" section.
-   Enable JSON logging to identify slow changesets.

### Deployment Hanged

**Symptom:** Process stuck without output.
**Fix:**
-   Check database active queries.
-   Verify network connectivity (VPN/Bastion).
-   Check `DATABASECHANGELOGLOCK` manually.

[↑ Back to Table of Contents](#table-of-contents)

## Glossary

- **ChangeLog**: The file (or tree of files) that defines database changes in YAML, XML, JSON, or SQL format.
- **ChangeSet**: The atomic unit of change. Includes `id`, `author`, `changes`, and optional `rollback` block.
- **Baseline**: Initial schema snapshot used when adopting Liquibase on an existing database.
- **Drift**: When the actual database schema differs from what changelogs expect.
- **Tag**: A named point-in-time marker for rollbacks (e.g., `v1.0`).
- **Flow File**: Liquibase Secure workflow file for orchestrating multi-step deployments.
- **DATABASECHANGELOG**: The tracking table Liquibase creates to record which changesets have been applied.
- **DATABASECHANGELOGLOCK**: The lock table Liquibase uses to prevent concurrent deployments.
- **Precondition**: A validation check that runs before a changeset to ensure the database is in the expected state.
- **Context**: A runtime filter to selectively execute changesets in specific environments (e.g., `dev`, `prod`).
- **Label**: A tag on a changeset for filtering during deployment (e.g., `db:app`).
- **runOnChange**: Attribute that re-executes a changeset when its content changes.
- **runAlways**: Attribute that executes a changeset on every deployment.

[↑ Back to Table of Contents](#table-of-contents)

## References

### Official Documentation

- [Liquibase Documentation](https://docs.liquibase.com/)
- [Best Practices](https://docs.liquibase.com/start/design-liquibase-project.html)

### Internal Documentation

- **[Liquibase Concepts Guide](../../explanation/liquibase/liquibase-concepts.md)**
- **[Liquibase Architecture Guide](../../explanation/liquibase/liquibase-architecture.md)**
- **[Liquibase Operations Guide](../../how-to/liquibase/liquibase-operations-guide.md)**
- **[Liquibase Reference](liquibase-reference.md)**
- **[Liquibase Formatted SQL Guide](liquibase-formatted-sql-guide.md)**

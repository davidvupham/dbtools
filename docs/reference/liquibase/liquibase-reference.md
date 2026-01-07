# Liquibase Reference

**🔗 [← Back to Liquibase Documentation Index](../../explanation/liquibase/README.md)** — Navigation guide for all Liquibase docs

> **Document Version:** 1.0
> **Last Updated:** January 6, 2026
> **Status:** Production
> **Related Docs:** [Concepts](../../explanation/concepts/liquibase/liquibase-concepts.md) | [Architecture](../../explanation/architecture/liquibase/liquibase-architecture.md) | [Operations](../../how-to/liquibase/liquibase-operations-guide.md)

This document serves as a reference for Liquibase features, limitations, configuration, and troubleshooting. Use this to look up specific commands, attributes, and error messages.

> [!NOTE]
> For foundational understanding, see the [Concepts Guide](../../explanation/concepts/liquibase/liquibase-concepts.md). For day-to-day tasks, see the [Operations Guide](../../how-to/liquibase/liquibase-operations-guide.md).

## Table of Contents

- [Edition Differences](#edition-differences)
  - [Liquibase Community](#liquibase-community)
  - [Liquibase Secure (Pro/Enterprise)](#liquibase-secure-proenterprise)
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

### Liquibase Secure (Pro/Enterprise)

**Adds to Community:**

- ✅ **Automated Stored Logic Extraction**: Generates `pro:` change types for functions, triggers, etc.
- **Drift Reporting**: Automated reports and alerts.
- **Flow Files**: Orchestration of multi-stage deployments.
- **Policy Checks**: Compliance rules to block bad patterns.
- **Targeted Rollback**: Rollback specific changesets without rolling back everything after them.

**Recommendation**: If your platforms rely heavily on stored logic (procedures/functions), Liquibase Secure significantly reduces manual effort.

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

```yaml
- changeSet:
    id: 20251220-1000-PROJ-100-create-user-summary-view
    author: platform-team
    runOnChange: true
    changes:
      - createView:
          viewName: user_summary
          selectQuery: SELECT id, email, created_at FROM users WHERE active = true
```

**Example: modifySql for Platform-Specific SQL**

Add platform-specific clauses to generated SQL:

```yaml
- changeSet:
    id: 20251220-1100-PROJ-101-create-orders-table
    author: platform-team
    changes:
      - createTable:
          tableName: orders
          columns:
            - column: { name: id, type: bigint, autoIncrement: true }
    modifySql:
      - append:
          dbms: mysql
          value: " ENGINE=InnoDB"
```

## Flowfile Actions Reference

Common actions used in `liquibase.flowfile.yaml`:

- `validate`: Checks changelog for errors.
- `checks run`: Executes policy checks.
- `update`: Deploys pending changes.
- `rollback`: Rolls back changes.
- `history`: Shows deployment history.
- `status`: Shows pending changes.
- `shell`: Execute arbitrary shell commands (e.g., `echo`, `aws`).

[↑ Back to Table of Contents](#table-of-contents)

## Troubleshooting

### Lock Issues

If a deployment crashes, the lock may remain held.

```bash
# Release stuck lock
liquibase --defaults-file properties/liquibase.dev.properties releaseLocks
```

### Checksum Mismatches

Occurs when a changeSet is edited *after* it has been deployed.
**Best Practice**: Never edit deployed changeSets. Create new ones.

```bash
# Clear checksums (use with caution - forces re-validation)
liquibase --defaults-file properties/liquibase.dev.properties clearCheckSums
```

### Manual Interventions

To mark changeSets as executed without actually running the SQL (e.g., fixing a hotfix mismatch):

```bash
liquibase --defaults-file properties/liquibase.env.properties changelogSync
```

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

- [Liquibase Architecture Guide](../../explanation/architecture/liquibase/liquibase-architecture.md): Design principles and directory structure.
- [Liquibase Operations Guide](../../how-to/liquibase/liquibase-operations-guide.md): Day-to-day procedures.

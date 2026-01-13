# Liquibase Formatted SQL Guide

**🔗 [← Back to Liquibase Concepts](../../explanation/concepts/liquibase/liquibase-concepts.md)**

> **Document Version:** 1.0
> **Last Updated:** January 12, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production
> **Related Docs:** [Concepts](../../explanation/concepts/liquibase/liquibase-concepts.md) | [Architecture](../../explanation/architecture/liquibase/liquibase-architecture.md) | [Operations](../../how-to/liquibase/liquibase-operations-guide.md) | [Reference](liquibase-reference.md)

![Liquibase Version](https://img.shields.io/badge/Liquibase-5.0%2B-blue)
![Document Status](https://img.shields.io/badge/Status-Production-green)

Liquibase **Formatted SQL** allows you to write database changelogs using standard SQL, augmented with special comments that provide Liquibase metadata (author, id, preconditions, etc.).

This is the **primary standard** for all database changesets at Global Data Services.

## Table of Contents

- [Header](#header)
- [Basic Changeset](#basic-changeset)
- [Attributes](#attributes)
- [Variable Substitution](#variable-substitution)
- [Rollbacks](#rollbacks)
- [Preconditions (SQL Guards)](#preconditions-sql-guards)
- [Stored Procedures & Logic](#stored-procedures--logic)
- [Includes & Modularity](#includes--modularity)
- [Best Practices](#best-practices)


## Header
Every Formatted SQL file **MUST** start with this header line:

```sql
--liquibase formatted sql
```

## Basic Changeset
A changeset is defined by a comment starting with `--changeset`. It must include an `author` and an `id`.

```sql
--liquibase formatted sql

--changeset alice:create-customer-table
CREATE TABLE customer (
    id INT PRIMARY KEY,
    name VARCHAR(255)
);

--changeset bob:add-email-column
ALTER TABLE customer ADD email VARCHAR(255);
```

**Syntax:** `--changeset author:id [attributes]`

> **Standard ID Format:** Use `author:id` where ID is descriptive (e.g., `team-a:20260112-add-user`) or matches the filename timestamp.

## attributes
You can add optional attributes to the changeset line to control execution behavior.

| Attribute | Description | Example |
|:---|:---|:---|
| `runOnChange` | Re-run if the SQL content changes (good for views/procedures) | `--changeset alice:1 runOnChange:true` |
| `runAlways` | Always run on every update | `--changeset alice:1 runAlways:true` |
| `context` | Only run in specific contexts (e.g., dev, test) | `--changeset alice:1 context:dev` |
| `labels` | Tag changesets for labeled deployments | `--changeset alice:1 labels:feature-a` |
| `dbms` | Only run on specific database types | `--changeset alice:1 dbms:postgresql,oracle` |
| `stripComments`| Remove SQL comments before executing (default: true) | `--changeset alice:1 stripComments:false` |
| `logicalFilePath` | Override the file path used for the checksum (useful when moving files) | `--changeset alice:1 logicalFilePath:path/to/file.sql` |
| `objectQuotingStrategy` | Control how objects are quoted (QUOTE_ALL_OBJECTS, QUOTE_ONLY_RESERVED_WORDS, LEGACY) | `--changeset alice:1 objectQuotingStrategy:QUOTE_ALL_OBJECTS` |

**Example:**
```sql
--changeset alice:create-view runOnChange:true context:dev
CREATE OR REPLACE VIEW customer_view AS SELECT * FROM customer;
```

## Variable Substitution
You can use Liquibase properties in your SQL using the `${property}` syntax.

1.  **Define Property:** In your `liquibase.properties` file or command line (`-DtableName=customer`).
2.  **Use Property:**
    ```sql
    --changeset alice:dynamic-table
    CREATE TABLE ${tableName} (
        id INT PRIMARY KEY
    );
    ```

**Note:** If you need to use a literal `${`, escape it as `\${`.

## Rollbacks
You can define how to undo a change using the `--rollback` comment. This is critical for keeping your database in a deployable state.

### Inline Rollback (Single Line)
```sql
--changeset alice:add-index
CREATE INDEX idx_email ON customer(email);
--rollback DROP INDEX idx_email;
```

### Multi-line Rollback
Use a block comment for complex rollbacks.
```sql
--changeset alice:complex-change
CREATE TABLE foo (id int);
CREATE TABLE bar (id int);

/* rollback
DROP TABLE foo;
DROP TABLE bar;
*/
```

### Empty Rollback
If a change cannot be rolled back (e.g., dropping a table), explicitly state it's empty to prevent errors.
```sql
--changeset alice:destructive-change
DROP TABLE old_legacy_table;
--rollback empty
```

## Preconditions
Preconditions allow you to control whether a changeset runs based on the database state.

**Syntax:** `--preconditions onFail:[MARK_RAN|CONTINUE|HALT|WARN] onError:[HALT|...]`

```sql
--changeset alice:add-column-if-missing
--preconditions onFail:MARK_RAN onError:HALT
--precondition-sql-check expectedResult:0 SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'customer' AND column_name = 'phone';
ALTER TABLE customer ADD phone VARCHAR(20);
```

## Stored Procedures & Logic

Managing repeatable logic (procedures, views, functions) requires a different pattern than tables.

### Idempotency Pattern

Use `runOnChange:true` combined with `CREATE OR REPLACE` syntax. This allows you to edit the SQL file in place without creating a new changeset ID.

```sql
--liquibase formatted sql

--changeset team:update-proc-calculate-total runOnChange:true splitStatements:false
CREATE OR REPLACE PROCEDURE calculate_total AS
BEGIN
  -- Logic here
END;
/
```

### File Organization

Keep these files in a dedicated directory (e.g., `database/logic/`) rather than the timestamped `changes/` folder, as they are "state" files, not "delta" files.

### Delimiters (`splitStatements:false`)

By default, Liquibase splits by `;`. For procedures, use `splitStatements:false` to send the whole block.

```sql
--changeset alice:create-complex-proc splitStatements:false
CREATE PROCEDURE foo AS ... END;
/
```

## Includes & Modularity

> **Note:** The ability to use `include` or `includeAll` **inside** a formatted SQL file is a **Liquibase Secure** feature. Community users must use the XML master changelog pattern.

**Community Edition:**
You must use an XML, YAML, or JSON "master" changelog to include your formatted SQL files.

```xml
<!-- changelog.xml -->
<databaseChangeLog ...>
  <includeAll path="changes/"/>
</databaseChangeLog>
```

**Liquibase Pro:**
You can reference other SQL files directly:
```sql
--liquibase formatted sql
--include file:other-file.sql
```

## Best Practices
1.  **File Naming**: Strictly follow `V<Timestamp>__<Jira>_<Description>.<db>.sql`.
2.  **Atomic Changesets**: Keep changesets granular. One logical change per file.
3.  **Always Define Rollbacks**: Make your deployments reversible.
4.  **Use Unique IDs**: Combine `author` and unique identifier (e.g., `team:20260112-add-table`).
5.  **Formatting**: Keep the `--changeset` line clean and readable.
6.  **Idempotency**: Use SQL guards (`IF NOT EXISTS`) instead of complex XML preconditions.

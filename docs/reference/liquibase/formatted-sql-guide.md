# Liquibase Formatted SQL Guide

**🔗 [← Back to Liquibase Concepts](../../explanation/concepts/liquibase/liquibase-concepts.md)**

Liquibase **Formatted SQL** allows you to write database changelogs using standard SQL, augmented with special comments that provide Liquibase metadata (author, id, preconditions, etc.).

This format gives you full control over the SQL while maintaining the tracking and deployment benefits of Liquibase.

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

## Multi-Statement Changesets & Stored Procedures
By default, Liquibase attempts to split statements by `;`. If you are writing a stored procedure or complex block requiring a different delimiter, use `splitStatements:false` or specifying the `endDelimiter`.

**Option 1: `splitStatements:false` (Recommended for Native Executors)**
This sends the entire block to the database as a single command.
```sql
--changeset alice:create-procedure splitStatements:false
CREATE PROCEDURE update_customer AS
BEGIN
  UPDATE customer SET updated_at = NOW();
END;
/
```

**Option 2: `endDelimiter`**
Tells Liquibase to split statements by a custom delimiter.
```sql
--changeset alice:create-procedure endDelimiter:/
CREATE PROCEDURE update_customer AS
BEGIN
  UPDATE customer SET updated_at = NOW();
END;
/
```

## Includes & Modularity
The ability to use `include` or `includeAll` **inside** a formatted SQL file is a **Liquibase Pro** feature (starting from v4.28.0).

**Community Edition:**
You must use an XML, YAML, or JSON "master" changelog to include your formatted SQL files.

```yaml
# db.changelog-master.yaml
databaseChangeLog:
  - include:
      file: changes/001-initial-schema.sql
  - include:
      file: changes/002-add-data.sql
```

**Liquibase Pro:**
You can reference other SQL files directly:
```sql
--liquibase formatted sql
--include file:other-file.sql
```

## Best Practices
1.  **Atomic Changesets:** Keep changesets granular. Avoid mixing DDL (schema) and DML (data) in the same changeset to ensure clean transaction boundaries.
2.  **Always Define Rollbacks:** Make your deployments reversible.
3.  **Use Unique IDs:** A common pattern is `YYYYMMDD-ticket-description`.
4.  **Formatting:** Keep the `--changeset` line clean and readable.
5.  **Checksums:** If you change a changeset that has already run, Liquibase will fail checkums validation. Use `<validCheckSum>` (XML/YAML) or `validCheckSum` attribute (if supported by your version) or manually clear the checksum in `DATABASECHANGELOG` to fix this, but essentially: **Don't change deployed changesets.**
6.  **Idempotency:** When using `runOnChange:true` or `runAlways:true`, write your SQL to be idempotent (e.g., `CREATE OR REPLACE VIEW`).

# Liquibase Custom Change Types (Java) Guide

**🔗 [← Back to Liquibase Concepts](../../explanation/concepts/liquibase/liquibase-concepts.md)**

When standard Liquibase change types (like `createTable` or `addColumn`) aren't enough, you can write **Java code** to execute complex logic during your database deployment.

## When to Use Custom Changes for Java

| Scenario | Recommended Approach | Why? |
|:---|:---|:---|
| **Complex Data Transformation** | `CustomTaskChange` | You need to loop through records, apply business logic, and update data conditionally. |
| **External API Integration** | `CustomTaskChange` | You need to fetch data from a REST API or encryption service to populate a column. |
| **Dynamic SQL Generation** | `CustomSqlChange` | You need to generate SQL based on the database type or environment properties (e.g., creating specific Oracle partitioning). |
| **OS Interaction** | `executeCommand` | Use the standard `executeCommand` change type (not Java) for running bash/python scripts. |

## Key Interfaces

### 1. `CustomSqlChange` (Generates SQL)
Use this when you want your Java code to **produce SQL strings**. Liquibase will then execute this SQL.

*   **Pros:** Compatible with `update-sql` (preview mode).
*   **Cons:** Cannot perform non-SQL actions (like file I/O or API calls) easily.

```java
public class CreateAuditTableChange implements CustomSqlChange {
    private String tableName;
    
    // Setters for parameters from changelog
    public void setTableName(String tableName) { this.tableName = tableName; }

    @Override
    public SqlStatement[] generateStatements(Database database) {
        return new SqlStatement[] {
            new RawSqlStatement("CREATE TABLE " + tableName + "_AUDIT (...)")
        };
    }
    
    // ... setup and confirmation methods
}
```

### 2. `CustomTaskChange` (Executes Logic)
Use this when you want your Java code to **execute directly**.

*   **Pros:** Can do anything Java can do (API calls, complex calculations, file operations).
*   **Cons:** Does NOT show up in `update-sql` output (because it doesn't return SQL).

```java
public class MaskUserDataChange implements CustomTaskChange {
    @Override
    public void execute(Database database) {
        JdbcConnection conn = (JdbcConnection) database.getConnection();
        // Run complex JDBC logic to mask data
    }
}
```

## Implementation Steps

### 1. Write the Java Class
Create a class that implements `CustomSqlChange` or `CustomTaskChange`.

```java
package com.example.db.changes;

import liquibase.change.custom.CustomTaskChange;
import liquibase.database.Database;
import liquibase.exception.CustomChangeException;
import liquibase.exception.SetupException;
import liquibase.exception.ValidationErrors;
import liquibase.resource.ResourceAccessor;

public class BackfillOrderTotals implements CustomTaskChange {

    private String targetTable;
    
    public void setTargetTable(String targetTable) {
        this.targetTable = targetTable;
    }

    @Override
    public void execute(Database database) throws CustomChangeException {
        // Logic to calculate and backfill order totals
        System.out.println("Backfilling totals for " + targetTable);
    }

    @Override
    public String getConfirmationMessage() {
        return "Backfilled order totals";
    }

    @Override
    public void setUp() throws SetupException {}

    @Override
    public ValidationErrors validate(Database database) {
        return new ValidationErrors();
    }

    @Override
    public void setFileOpener(ResourceAccessor resourceAccessor) {}
}
```

### 2. Compile and Package
Package your class into a JAR file. This JAR must be present in the Liquibase classpath when you run `liquibase update`.

### 3. Reference in Changelog
Use the `<customChange>` tag (XML/YAML/JSON).

**YAML Example:**
```yaml
databaseChangeLog:
  - changeSet:
      id: backfill-orders
      author: bob
      changes:
        - customChange:
            class: com.example.db.changes.BackfillOrderTotals
            param:
              name: targetTable
              value: orders
```

## Rollbacks (Critical)

Custom changes do **not** have automatic rollback. You must implement `CustomSqlRollback` or `CustomTaskRollback` interfaces, or provide a generic `<rollback>` block in your changeset.

**Java Interface Approach:**
```java
public class MyChange implements CustomTaskChange, CustomTaskRollback {
    @Override
    public void rollback(Database database) {
        // Undo logic
    }
}
```

**Changelog Approach (Simpler):**
```yaml
- changeSet:
    changes:
      - customChange: ...
    rollback:
      - sql: UPDATE orders SET total_amount = NULL;
```

## Best Practices
1.  **Keep Logic Isolated:** Don't rely on external application state (Spring beans, specialized contexts) unless absolutely necessary. The Liquibase runner might be a separate process (CI/CD container).
2.  **Idempotency:** Ensure your `execute()` method checks if the work is already done.
3.  **Logs:** Use Liquibase's logging system to output status.
4.  **Testing:** Write unit tests for your custom change classes.

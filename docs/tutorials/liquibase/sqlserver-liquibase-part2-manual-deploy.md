# Tutorial Part 2: Manual Liquibase Deployment Lifecycle

This Part 2 assumes you have completed **Part 1: Baseline SQL Server + Liquibase Setup** and have:

- A working SQL Server tutorial container (`mssql_liquibase_tutorial`)
- Three databases: `testdbdev`, `testdbstg`, `testdbprd`
- A Liquibase project at `/data/liquibase-tutorial` with:
  - `database/changelog/baseline/V0000__baseline.xml`
  - `database/changelog/changelog.xml` including the baseline
  - `env/liquibase.dev.properties`, `env/liquibase.stage.properties`, `env/liquibase.prod.properties`
- Baseline deployed and tagged as `baseline` in all three environments

From here we’ll walk through making changes, deploying them through dev → stage → prod, and handling rollback and drift manually.

## Step 6: Making Your First Change

Now let's make a new database change: add an `orders` table.

### Create the Change File

**Choosing between SQL and YAML format:**

- **SQL format**: Best for complex queries, views, and SQL Server-specific features
- **YAML/XML format**: Best for tables, indexes, constraints (database-agnostic)
- You can mix both formats in the same project

For this tutorial, we'll use **SQL format** for simplicity and readability.

```bash
# Create the change file
cat > /data/liquibase-tutorial/database/changelog/changes/V0001__add_orders_table.sql << 'EOF'
--changeset tutorial:V0001-add-orders-table
-- Purpose: Add orders table to track customer purchases
-- This change creates:
--   - orders table with 5 columns (order_id, customer_id, order_total, order_date, status)
--   - Primary key constraint (PK_orders)
--   - Foreign key constraint to customer table (FK_orders_customer)
--   - Two default constraints (DF_orders_date for order_date, inline default for status)

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE object_id = OBJECT_ID(N'[app].[orders]') AND type = 'U')
BEGIN
    CREATE TABLE app.orders (
        order_id INT IDENTITY(1,1) CONSTRAINT PK_orders PRIMARY KEY,
        customer_id INT NOT NULL,
        order_total DECIMAL(18,2) NOT NULL,
        order_date DATETIME2(3) NOT NULL CONSTRAINT DF_orders_date DEFAULT (SYSUTCDATETIME()),
        status NVARCHAR(50) NOT NULL DEFAULT 'pending',
        CONSTRAINT FK_orders_customer FOREIGN KEY (customer_id)
            REFERENCES app.customer(customer_id)
    );
END
GO
EOF
```

### Include the Change in `changelog.xml`

Update the master changelog to include this new change. One common pattern is to use an XML wrapper with `<sqlFile>` so you can add rollback later:

```bash
cat > /data/liquibase-tutorial/database/changelog/changelog.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <!-- Baseline: initial database state -->
    <include file="baseline/V0000__baseline.xml" relativeToChangelogFile="true"/>

    <!-- V0001: Add orders table -->
    <changeSet id="V0001-add-orders-table" author="tutorial">
        <sqlFile
            path="database/changelog/changes/V0001__add_orders_table.sql"
            relativeToChangelogFile="false"/>
    </changeSet>

</databaseChangeLog>
EOF
```

> In later steps you will refine this pattern to add explicit `<rollback>` blocks for safer deployments.

### Deploy to Development

```bash
cd /data/liquibase-tutorial

# See what will run
lb -e dev -- updateSQL

# Deploy change to development
lb -e dev -- update
```

Verify in dev:

```bash
sqlcmd-tutorial -Q "
USE testdbdev;
SELECT
    SCHEMA_NAME(schema_id) AS SchemaName,
    name AS ObjectName,
    type_desc AS ObjectType
FROM sys.objects
WHERE schema_id = SCHEMA_ID('app')
ORDER BY type_desc, name;
"
```

**Expected output:**

You should see 10 rows total. The V0001 changeset adds the `orders` table plus 3 new constraints (DF__orders__status, DF_orders_date, FK_orders_customer, PK_orders), bringing the total to 10 objects in the app schema:

```text
SchemaName  ObjectName                  ObjectType
----------- --------------------------- --------------------------
app         DF__orders__status__534...  DEFAULT_CONSTRAINT
app         DF_customer_created_at      DEFAULT_CONSTRAINT
app         DF_orders_date              DEFAULT_CONSTRAINT
app         FK_orders_customer          FOREIGN_KEY_CONSTRAINT
app         PK_customer                 PRIMARY_KEY_CONSTRAINT
app         PK_orders                   PRIMARY_KEY_CONSTRAINT
app         UQ_customer_email           UNIQUE_CONSTRAINT
app         customer                    USER_TABLE
app         orders                      USER_TABLE
app         v_customer_basic            VIEW

(10 rows affected)
```

**New objects from V0001 changeset:**

- `orders` table
- `DF__orders__status__534...` (default constraint for status column)
  - **Note:** The suffix `__534...` is a unique identifier automatically generated by SQL Server when you create an inline default constraint without explicitly naming it (`DEFAULT 'pending'` in the SQL). SQL Server ensures uniqueness by appending a hex object ID. Named constraints like `DF_orders_date` (using `CONSTRAINT DF_orders_date DEFAULT ...`) have predictable names.
- `DF_orders_date` (default constraint for order_date column, explicitly named)
- `FK_orders_customer` (foreign key to customer table)
- `PK_orders` (primary key on order_id)

**Existing baseline objects:**

- `customer` table, `v_customer_basic` view
- `DF_customer_created_at`, `PK_customer`, `UQ_customer_email` constraints

## Step 7: Promoting Changes to Staging and Production

Once the change is validated in development, promote it to staging and production.

### Deploy to Staging

```bash
cd /data/liquibase-tutorial

# Preview what will run
lb -e stage -- updateSQL

# Deploy to staging
lb -e stage -- update
```

Verify in staging:

```bash
sqlcmd-tutorial -Q "
USE testdbstg;
SELECT
    SCHEMA_NAME(schema_id) AS SchemaName,
    name AS ObjectName,
    type_desc AS ObjectType
FROM sys.objects
WHERE schema_id = SCHEMA_ID('app')
ORDER BY type_desc, name;
"
```

### Deploy to Production

```bash
cd /data/liquibase-tutorial

# Preview what will run
lb -e prod -- updateSQL

# Deploy to production
lb -e prod -- update
```

Verify in production:

```bash
sqlcmd-tutorial -Q "
USE testdbprd;
SELECT
    SCHEMA_NAME(schema_id) AS SchemaName,
    name AS ObjectName,
    type_desc AS ObjectType
FROM sys.objects
WHERE schema_id = SCHEMA_ID('app')
ORDER BY type_desc, name;
"
```

At this point all three environments have the new `orders` table.

---

From here, continue following the remaining sections of the original tutorial for:

- Adding additional changesets (V0002, V0003, V0004, …)
- Using tags (e.g., `release-v1.1`, `release-v1.2`) and querying `DATABASECHANGELOG`
- Defining `<rollback>` blocks and practicing rollback to previous releases
- Detecting and handling drift with `diff` and `diffChangeLog`

These topics build on the baseline and first change you’ve completed in Parts 1 and 2.

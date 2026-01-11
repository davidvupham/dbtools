# Tutorial Part 2: Manual Liquibase Deployment Lifecycle

This Part 2 assumes you have completed **Part 1: Baseline SQL Server + Liquibase Setup** and have:

- Three SQL Server containers running: `mssql_dev`, `mssql_stg`, `mssql_prd`
- Database `orderdb` created in each environment
- A Liquibase project at `$LIQUIBASE_TUTORIAL_DATA_DIR` with:
  - `platform/mssql/database/orderdb/changelog/baseline/V0000__baseline.mssql.sql`
  - `platform/mssql/database/orderdb/changelog/changelog.xml` including the baseline
    - `platform/mssql/database/orderdb/env/liquibase.mssql_dev.properties`, `platform/mssql/database/orderdb/env/liquibase.mssql_stg.properties`, `platform/mssql/database/orderdb/env/liquibase.mssql_prd.properties`
- Baseline deployed and tagged as `baseline` in all three environments

## Validate Part 1 Completion

Before starting Part 2, validate that Part 1 was completed successfully:

```bash
# Run the comprehensive validation script (validates all prerequisites)
$LIQUIBASE_TUTORIAL_DIR/validation/scripts/validate_liquibase_deploy.sh
```

**What the script validates (maps to prerequisites above):**

- ✅ **Containers running** - Validates containers are accessible (implicit via database connections)
- ✅ **Database `orderdb` exists** - Validates by connecting to each environment
- ✅ **Baseline file exists** - Validates `V0000__baseline.mssql.sql` exists
- ✅ **Master changelog exists** - Validates `changelog.xml` exists and includes baseline
- ✅ **Properties files** - Validates via database connections (full validation: `validate_liquibase_properties.sh`)
- ✅ **DATABASECHANGELOG table exists** - Validates in all environments (dev, stg, prd)
- ✅ **Baseline changesets tracked** - Validates ≥4 changesets in all environments
- ✅ **Baseline objects exist** - Validates app.customer table exists in all environments
- ✅ **Baseline tagged** - Validates `baseline` tag exists in all environments

**Optional: Individual validation scripts**

For granular validation of specific prerequisites:

```bash
# Containers and databases
$LIQUIBASE_TUTORIAL_DIR/validation/scripts/validate_orderdb_database.sh

# Properties files
$LIQUIBASE_TUTORIAL_DIR/validation/scripts/validate_liquibase_properties.sh

# Baseline deployment (comprehensive validation, recommended)
$LIQUIBASE_TUTORIAL_DIR/validation/scripts/validate_liquibase_deploy.sh
```

If validation fails, complete the missing steps from Part 1 before proceeding.

From here we’ll walk through making changes, deploying them through dev → stg → prd, and handling rollback and drift manually.

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
cat > $LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changes/V0001__add_orders_table.mssql.sql << 'EOF'
--liquibase formatted sql

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

> **Note:** The `IF NOT EXISTS` check ensures this changeset is **idempotent**—it can be safely run multiple times without errors. If the table already exists, the changeset will be skipped. This is a best practice for all database changes.

### Include the Change in `changelog.xml`

Update the master changelog to include this new change.

```bash
cat > $LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changelog.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <!-- Baseline: initial database state -->
    <include file="baseline/V0000__baseline.mssql.sql" relativeToChangelogFile="true"/>

    <!-- V0001: Add orders table -->
    <include file="changes/V0001__add_orders_table.mssql.sql" relativeToChangelogFile="true"/>
</databaseChangeLog>
EOF
```

### Deploy to Development

```bash
cd $LIQUIBASE_TUTORIAL_DATA_DIR

# See what will run
lb -e dev -- updateSQL

# Deploy change to development
lb -e dev -- update
```

Verify in dev:

```bash
sqlcmd-tutorial -Q "
USE orderdb;
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

You should see 10 rows total. The V0001 changeset adds the `orders` table plus 4 new constraints (DF__orders__status, DF_orders_date, FK_orders_customer, PK_orders), bringing the total to 10 objects in the app schema:

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
cd $LIQUIBASE_TUTORIAL_DATA_DIR

# Preview what will run
lb -e stg -- updateSQL

# Deploy to staging
lb -e stg -- update
```

Verify in staging:

```bash
sqlcmd-tutorial -Q "
USE orderdb;
SELECT
    SCHEMA_NAME(schema_id) AS SchemaName,
    name AS ObjectName,
    type_desc AS ObjectType
FROM sys.objects
WHERE schema_id = SCHEMA_ID('app')
ORDER BY type_desc, name;
"
```

**Expected output:** You should see the same 10 objects as in development, including the `orders` table and its constraints.

### Deploy to Production

```bash
cd $LIQUIBASE_TUTORIAL_DATA_DIR

# Preview what will run
lb -e prd -- updateSQL

# Deploy to production
lb -e prd -- update
```

Verify in production:

```bash
sqlcmd-tutorial -Q "
USE orderdb;
SELECT
    SCHEMA_NAME(schema_id) AS SchemaName,
    name AS ObjectName,
    type_desc AS ObjectType
FROM sys.objects
WHERE schema_id = SCHEMA_ID('app')
ORDER BY type_desc, name;
"
```

**Expected output:** You should see the same 10 objects as in development and staging, including the `orders` table and its constraints.

At this point all three environments have the new `orders` table.

## Step 8: Tags and Release Management

Tags create named checkpoints in your deployment history for easy rollback targeting.

### Create a Release Tag

After deploying V0001, tag the current state as a release:

```bash
cd $LIQUIBASE_TUTORIAL_DATA_DIR

# Tag all environments with the release version
lb -e dev -- tag release-v1.0
lb -e stg -- tag release-v1.0
lb -e prd -- tag release-v1.0
```

### Query DATABASECHANGELOG

View what's been deployed and when:

```bash
sqlcmd-tutorial -Q "
USE orderdb;
SELECT
    ID,
    AUTHOR,
    FILENAME,
    DATEEXECUTED,
    TAG,
    EXECTYPE
FROM DATABASECHANGELOG
ORDER BY ORDEREXECUTED DESC;
"
```

**Expected output:**

```text
ID                        AUTHOR    FILENAME                                    DATEEXECUTED             TAG           EXECTYPE
------------------------- --------- ------------------------------------------- ------------------------ ------------- --------
V0001-add-orders-table    tutorial  platform/mssql/database/orderdb/changelog/changes/V0001...sql      2025-11-16 03:15:00.000  release-v1.0  EXECUTED
<baseline entries...>                                                                                    baseline      MARK_RAN
```

---

## Step 9: Rollback Strategies

### Understanding Rollback Types

| Type | Command | Use When |
|------|---------|----------|
| **Tag-based** | `rollback <tag>` | Rolling back to a known release |
| **Count-based** | `rollbackCount <n>` | Undoing the last N changesets |
| **Date-based** | `rollbackToDate <date>` | Reverting to a point in time |

### Add Rollback Blocks to Changesets

When using Formatted SQL files, you define rollback blocks directly in the SQL file using `--rollback` comments. The `changelog.xml` file does not need rollback blocks for Formatted SQL files—the rollback instructions are embedded in the SQL file itself.

### Add Rollback to SQL File

When using Formatted SQL, you define rollbacks inline using `--rollback`. Update your `V0001__add_orders_table.mssql.sql`:

```bash
cat > $LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changes/V0001__add_orders_table.mssql.sql << 'EOF'
--liquibase formatted sql

--changeset tutorial:V0001-add-orders-table
-- Purpose: Add orders table to track customer purchases

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
--rollback DROP TABLE IF EXISTS app.orders;
--rollback GO
EOF
```

### Practice Rollback (Development Only)

> **Warning:** Only practice rollback in development. Never rollback production without proper change management.

```bash
cd $LIQUIBASE_TUTORIAL_DATA_DIR

# Preview what rollback will do
# Note: We're rolling back to 'baseline' to remove all changes after baseline
# You could also rollback to 'release-v1.0' to remove only changes after that tag
lb -e dev -- rollbackSQL baseline

# Execute rollback to baseline (removes V0001 orders table)
# This removes all changesets executed after the baseline tag
lb -e dev -- rollback baseline

# Verify the orders table is gone
sqlcmd-tutorial -Q "
USE orderdb;
SELECT name FROM sys.objects
WHERE schema_id = SCHEMA_ID('app') AND type = 'U';
"
```

### Re-apply After Rollback

```bash
# Re-deploy V0001
lb -e dev -- update

# Re-tag the release
lb -e dev -- tag release-v1.0
```

---

## Step 10: Drift Detection

Drift occurs when someone makes direct database changes outside of Liquibase. Detecting drift early prevents deployment surprises.

### Simulate Drift

Create an untracked change directly in the database:

```bash
sqlcmd-tutorial -Q "
USE orderdb;
-- Someone adds a column without using Liquibase
ALTER TABLE app.customer ADD loyalty_points INT DEFAULT 0;
"
```

### Detect Drift with diff

Compare the database against your changelog:

```bash
cd $LIQUIBASE_TUTORIAL_DATA_DIR

# Compare dev database to what Liquibase thinks it should be
lb -e dev -- diff \
    --referenceUrl="offline:mssql?changeLogFile=platform/mssql/database/orderdb/changelog/changelog.xml"
```

**Expected output will show:**

```text
Missing Column(s):
  app.customer.loyalty_points
```

### Generate a Changelog from Drift

Capture the drift as a proper changeset:

```bash
# Generate a changelog capturing the drift
lb -e dev -- diffChangeLog \
    --referenceUrl="offline:mssql?changeLogFile=platform/mssql/database/orderdb/changelog/changelog.xml" \
    --changelogFile=$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changes/V0002__drift_loyalty_points.xml
```

**Workflow after detecting drift:**
1. Review the generated changelog file
2. Edit it if needed (e.g., adjust changeset ID, add comments)
3. Include it in your master `changelog.xml` if you want to keep the drift
4. Deploy the changeset to track the drift in your version control

**Note:** In this tutorial, we'll remove the drift column to restore the original state, so we won't include this generated file. In a real scenario, you would review and decide whether to keep or revert the drift.

### Best Practice: Regular Drift Checks

Add drift detection to your CI/CD pipeline before deployments:

```bash
# In CI/CD, fail the build if drift is detected
lb -e stg -- diff --reportFile=drift-report.txt
if [ -s drift-report.txt ]; then
    echo "ERROR: Drift detected in staging!"
    cat drift-report.txt
    exit 1
fi
```

---

## Step 11: Additional Changesets

Now add more changes following the established pattern.

> **Note:** If you generated a drift detection file `V0002__drift_loyalty_points.xml` in Step 10, you have two options:
> - Remove or rename that file if you don't want to include the drift
> - Use `V0003` for the index changeset below if you want to keep the drift file
>
> For this tutorial, we'll proceed with `V0002` for the index, assuming the drift file was not included in the master changelog.

### V0002: Add Index to Orders

```bash
cat > $LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changes/V0002__add_orders_index.mssql.sql << 'EOF'
--liquibase formatted sql

--changeset tutorial:V0002-add-orders-date-index
-- Purpose: Add performance index on order_date for reporting queries

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_orders_order_date'
    AND object_id = OBJECT_ID('app.orders')
)
BEGIN
    CREATE INDEX IX_orders_order_date ON app.orders(order_date DESC);
END
GO
--rollback DROP INDEX IF EXISTS IX_orders_order_date ON app.orders;
--rollback GO
EOF
```

### Update Master Changelog

```bash
cat > $LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changelog.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <!-- Baseline -->
    <include file="baseline/V0000__baseline.mssql.sql" relativeToChangelogFile="true"/>

    <!-- V0001: Add orders table -->
    <include file="changes/V0001__add_orders_table.mssql.sql" relativeToChangelogFile="true"/>

    <!-- V0002: Add orders index -->
    <include file="changes/V0002__add_orders_index.mssql.sql" relativeToChangelogFile="true"/>

</databaseChangeLog>
EOF
```

### Deploy Through Environments

```bash
# Deploy to dev
lb -e dev -- update
lb -e dev -- tag release-v1.1

# Deploy to staging (after dev validation)
lb -e stg -- update
lb -e stg -- tag release-v1.1

# Deploy to production (after staging validation)
lb -e prd -- update
lb -e prd -- tag release-v1.1
```

---

## Summary

In Part 2, you learned:

| Topic | Key Commands |
|-------|--------------|
| **Make changes** | Create SQL files, update `changelog.xml` |
| **Deploy** | `lb -e <env> -- update` |
| **Tags** | `lb -e <env> -- tag <name>` |
| **Rollback** | `lb -e dev -- rollback <tag>` |
| **Drift detection** | `lb -e <env> -- diff` |
| **Drift capture** | `lb -e <env> -- diffChangeLog` |

## Next Steps

- **[Part 3: CI/CD Automation](./series-part3-cicd.md)** - Wire everything into GitHub Actions for automated deployments.
- **[Runner Setup Guide](./guide-runner-setup.md)** - Set up a self-hosted runner for local CI/CD testing.

### Beginner's Tutorial: Manage SQL Server database objects with Liquibase

This tutorial walks you from zero to running Liquibase changes against Microsoft SQL Server. You'll learn how to structure a project, baseline existing databases, create and modify tables, views, procedures, functions, and triggers, and safely deploy changes locally, via Docker, and in GitHub Actions.

## What is Liquibase (and why use it)?

Liquibase is a database change management tool. You store database changes (DDL/DML) as versioned "changeSets" in source control. Liquibase keeps a ledger (the DATABASECHANGELOG table) of what ran, so each environment progresses deterministically and safely.

Key benefits:

- Version-controlled changes that run once per environment
- Simple commands to apply, preview, and roll back changes
- Works with SQL Server, plus many other databases
- Baseline existing databases and track changes going forward

## Prerequisites

- A SQL Server you can connect to (local, container, or remote)
  - You need a login with permissions to create/alter objects
- One of:
  - Java 17+ and Liquibase CLI installed, plus the Microsoft SQL Server JDBC driver
  - OR Docker, to run Liquibase as a container (no local Java/driver needed)
- Git (recommended) to track changes

Links:

- Liquibase install: `https://docs.liquibase.com/start/install/home.html`
- MSSQL JDBC driver: `https://learn.microsoft.com/sql/connect/jdbc/download-microsoft-jdbc-driver-for-sql-server`

## Quickstart project layout

Create a folder and use this structure:

```text
liquibase/
  database/
    changelog/
      changelog.xml
      baseline/
        V0000__baseline.xml      # Baseline for existing databases
      changes/
        V0001__create_schema_and_basics.sql
        V0002__add_email_column.sql
        V0003__views_procs_functions_triggers.sql
  liquibase.properties
  drivers/
    mssql-jdbc-<version>.jar   # Needed only for local CLI (not for Docker)
```

## Baselining an Existing Database

If you're adopting Liquibase for a database that already has schema, tables, views, and stored procedures, you need to create a **baseline**. This captures the current state so Liquibase can track future changes.

### Step 1: Generate the Baseline from Existing Database

Use Liquibase's `generateChangeLog` command to capture the current database state:

**Working Directory Setup:**

```bash
# Create project directory structure
mkdir -p /home/gds/liquibase/database/changelog/baseline
cd /home/gds/liquibase
```

**CLI (local Java):**

```bash
liquibase generateChangeLog \
  --changelog-file=database/changelog/baseline/V0000__baseline.xml
```

**Docker (recommended):**

```bash
# From /home/gds/liquibase directory
docker run --rm \
  --network=host \
  -v /home/gds/liquibase:/workspace \
  liquibase-custom:5.0.1 \
  --url="jdbc:sqlserver://localhost:1433;databaseName=testdb;encrypt=true;trustServerCertificate=true" \
  --username="sa" \
  --password='YourStrong!Passw0rd' \
  --changelog-file=/workspace/database/changelog/baseline/V0000__baseline.xml \
  generateChangeLog
```

**Important Notes:**

- Mount your project directory (`/home/gds/liquibase`) to `/workspace` to avoid overwriting the container's Liquibase installation
- Use the custom Liquibase image (`liquibase-custom:5.0.1`) built from `/workspaces/dbtools/docker/liquibase` which includes SQL Server JDBC drivers
- Use `--network=host` to connect to SQL Server running in the dev container
- The official `liquibase/liquibase` image does NOT include SQL Server drivers by default

This creates an XML file containing all existing database objects (tables, views, stored procedures, functions, triggers, indexes, constraints, etc.).

**Troubleshooting: "No changesets to write" message**

If you see this message:

```
changelog not generated. There are no changesets to write to /workspace/database/changelog/baseline/V0000__baseline.xml changelog
```

This means the database is **empty** (no tables, views, procedures, etc.). To verify and create sample objects:

```bash
# Check what objects exist in the database
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "USE testdb; SELECT SCHEMA_NAME(schema_id) AS SchemaName, name AS ObjectName, type_desc FROM sys.objects WHERE type IN ('U','V','P','FN','IF','TF') ORDER BY type_desc, name"

# Create sample objects for testing baseline generation
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
USE testdb;

-- Create schema
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'app')
    EXEC('CREATE SCHEMA app');

-- Create table
IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE object_id = OBJECT_ID(N'[app].[customer]') AND type = 'U')
BEGIN
    CREATE TABLE app.customer (
        customer_id INT IDENTITY(1,1) CONSTRAINT PK_customer PRIMARY KEY,
        full_name NVARCHAR(200) NOT NULL,
        email NVARCHAR(320) NULL,
        phone_number NVARCHAR(20) NULL,
        created_at DATETIME2(3) NOT NULL CONSTRAINT DF_customer_created_at DEFAULT (SYSUTCDATETIME())
    );
END

-- Create view
IF OBJECT_ID(N'app.v_customer_basic', N'V') IS NOT NULL
    DROP VIEW app.v_customer_basic;

CREATE VIEW app.v_customer_basic AS
SELECT customer_id, full_name, email, created_at
FROM app.customer;

-- Create stored procedure
IF OBJECT_ID(N'app.usp_add_customer', N'P') IS NOT NULL
    DROP PROCEDURE app.usp_add_customer;

CREATE PROCEDURE app.usp_add_customer
    @full_name NVARCHAR(200),
    @email NVARCHAR(320) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO app.customer (full_name, email) VALUES (@full_name, @email);
    SELECT SCOPE_IDENTITY() AS customer_id;
END;

-- Create function
IF OBJECT_ID(N'app.fn_mask_email', N'FN') IS NOT NULL
    DROP FUNCTION app.fn_mask_email;

CREATE FUNCTION app.fn_mask_email (@email NVARCHAR(320))
RETURNS NVARCHAR(320)
AS
BEGIN
    IF @email IS NULL RETURN NULL;
    DECLARE @at INT = CHARINDEX('@', @email);
    IF @at <= 1 RETURN @email;
    RETURN CONCAT(LEFT(@email, 1), '***', SUBSTRING(@email, @at, LEN(@email)));
END;

SELECT 'Objects created successfully' AS Result;
"

# Verify objects were created
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "USE testdb; SELECT SCHEMA_NAME(schema_id) AS SchemaName, name AS ObjectName, type_desc FROM sys.objects WHERE schema_id = SCHEMA_ID('app') ORDER BY type_desc, name"

# Now run generateChangeLog again (from /home/gds/liquibase directory)
cd /home/gds/liquibase
docker run --rm \
  --network=host \
  -v /home/gds/liquibase:/workspace \
  liquibase-custom:5.0.1 \
  --url="jdbc:sqlserver://localhost:1433;databaseName=testdb;encrypt=true;trustServerCertificate=true" \
  --username="sa" \
  --password='YourStrong!Passw0rd' \
  --changelog-file=/workspace/database/changelog/baseline/V0000__baseline.xml \
  generateChangeLog
```

### Step 2: Review and Clean the Baseline

The generated baseline may include system objects or unnecessary details. Review `V0000__baseline.xml` and remove:

- System tables or objects you don't want tracked
- Unnecessary metadata (Liquibase adds its own tracking tables)
- Objects not owned by your application

**Example cleaned baseline structure:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <!-- Schema -->
    <changeSet id="baseline-schema" author="system">
        <sql>
            IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'app')
            BEGIN
                EXEC('CREATE SCHEMA app')
            END
        </sql>
    </changeSet>

    <!-- Tables -->
    <changeSet id="baseline-table-customer" author="system">
        <createTable tableName="customer" schemaName="app">
            <column name="customer_id" type="int" autoIncrement="true">
                <constraints primaryKey="true" nullable="false"/>
            </column>
            <column name="full_name" type="nvarchar(200)">
                <constraints nullable="false"/>
            </column>
            <column name="email" type="nvarchar(320)">
                <constraints nullable="true"/>
            </column>
            <column name="created_at" type="datetime2(3)" defaultValueComputed="SYSUTCDATETIME()">
                <constraints nullable="false"/>
            </column>
        </createTable>
    </changeSet>

    <!-- Views -->
    <changeSet id="baseline-view-customer-basic" author="system">
        <createView viewName="v_customer_basic" schemaName="app">
            SELECT customer_id, full_name, created_at, email
            FROM app.customer
        </createView>
    </changeSet>

    <!-- Stored Procedures -->
    <changeSet id="baseline-proc-add-customer" author="system" runOnChange="true">
        <sql splitStatements="false">
            CREATE OR ALTER PROCEDURE app.usp_add_customer
                @full_name NVARCHAR(200),
                @email NVARCHAR(320) = NULL
            AS
            BEGIN
                SET NOCOUNT ON;
                INSERT INTO app.customer (full_name, email) VALUES (@full_name, @email);
            END
        </sql>
    </changeSet>

    <!-- Functions -->
    <changeSet id="baseline-func-mask-email" author="system" runOnChange="true">
        <sql splitStatements="false">
            CREATE OR ALTER FUNCTION app.fn_mask_email (@email NVARCHAR(320))
            RETURNS NVARCHAR(320)
            AS
            BEGIN
                IF @email IS NULL RETURN NULL;
                DECLARE @at INT = CHARINDEX('@', @email);
                IF @at <= 1 RETURN @email;
                RETURN CONCAT(LEFT(@email, 1), '***', SUBSTRING(@email, @at, LEN(@email)));
            END
        </sql>
    </changeSet>

</databaseChangeLog>
```

### Step 3: Create Master Changelog Including Baseline

Update `database/changelog/changelog.xml` to include the baseline:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <!-- Baseline: existing database objects -->
    <include file="baseline/V0000__baseline.xml" relativeToChangelogFile="true"/>

    <!-- Future changes -->
    <include file="changes/V0001__add_orders_table.sql" relativeToChangelogFile="true"/>
    <include file="changes/V0002__modify_customer_email.sql" relativeToChangelogFile="true"/>
    <include file="changes/V0003__update_stored_procedure.sql" relativeToChangelogFile="true"/>
</databaseChangeLog>
```

### Step 4: Sync the Baseline to Source Database

For the **source database** (where you generated the baseline), you need to mark the baseline as already applied without actually running it:

```bash
# Mark baseline changesets as executed (don't actually run them)
liquibase changelogSync
```

This updates the DATABASECHANGELOG table to record that all baseline changesets have been applied, without actually executing them (since the objects already exist).

### Step 5: Apply Baseline to Target Database

For **target databases** (test, staging, production) that don't have the schema yet:

```bash
# Apply baseline to create all objects
liquibase update
```

This will execute all baseline changesets to create the schema, tables, views, stored procedures, and functions.

### Step 6: Verify Baseline Application

Check that Liquibase tracking tables exist and baseline is recorded:

```sql
-- Check DATABASECHANGELOG table
SELECT ID, AUTHOR, FILENAME, DATEEXECUTED, ORDEREXECUTED, EXECTYPE
FROM DATABASECHANGELOG
ORDER BY DATEEXECUTED;

-- Verify objects exist
SELECT SCHEMA_NAME(schema_id) AS SchemaName, name AS ObjectName, type_desc
FROM sys.objects
WHERE schema_id = SCHEMA_ID('app')
ORDER BY type_desc, name;
```

### Baseline Best Practices

✅ **DO:**

- Generate baseline from your most complete environment (usually production)
- Review and clean the generated baseline before committing
- Use `changelogSync` on the source database to avoid re-running existing objects
- Test baseline application on a fresh database before applying to targets
- Tag the baseline: `liquibase tag baseline-2025-11-11`

❌ **DON'T:**

- Run `update` on the source database after generating baseline (use `changelogSync` instead)
- Include Liquibase tracking tables (DATABASECHANGELOG, DATABASECHANGELOGLOCK) in baseline
- Include environment-specific data in baseline (use separate seed data changesets)
- Modify baseline changesets after they've been applied to any environment

## Making Changes After Baseline

Once the baseline is established, all future changes go in new changeset files. Here are common scenarios with step-by-step examples.

### Change 1: Add a New Table

Create `database/changelog/changes/V0001__add_orders_table.sql`:

```sql
--changeset yourname:V0001-add-orders-table
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

    CREATE NONCLUSTERED INDEX IX_orders_customer
        ON app.orders(customer_id);

    CREATE NONCLUSTERED INDEX IX_orders_date
        ON app.orders(order_date DESC);
END
--rollback IF OBJECT_ID(N'app.orders', N'U') IS NOT NULL DROP TABLE app.orders;
```

**Apply the change:**

```bash
# Preview the SQL
liquibase updateSQL

# Apply the change
liquibase update

# Tag the release
liquibase tag add-orders-table-v1.1
```

### Change 2: Modify Data Type of a Column

Scenario: Change `app.customer.email` from `NVARCHAR(320)` to `NVARCHAR(500)` to support longer emails.

Create `database/changelog/changes/V0002__modify_customer_email_length.sql`:

```sql
--changeset yourname:V0002-modify-email-length
-- Increase email column length from 320 to 500
IF EXISTS (
    SELECT 1
    FROM sys.columns c
    JOIN sys.objects o ON o.object_id = c.object_id AND o.type = 'U'
    JOIN sys.types t ON t.user_type_id = c.user_type_id
    WHERE SCHEMA_NAME(o.schema_id) = 'app'
      AND o.name = 'customer'
      AND c.name = 'email'
      AND t.name = 'nvarchar'
      AND c.max_length < 1000  -- 500 * 2 bytes for NVARCHAR
)
BEGIN
    ALTER TABLE app.customer ALTER COLUMN email NVARCHAR(500) NULL;
    PRINT 'Modified email column to NVARCHAR(500)';
END
ELSE
BEGIN
    PRINT 'Email column already NVARCHAR(500) or larger';
END
--rollback ALTER TABLE app.customer ALTER COLUMN email NVARCHAR(320) NULL;
```

**For complex data type conversions** (e.g., `VARCHAR` to `INT`), use the expand-contract pattern:

```sql
--changeset yourname:V0002-convert-phone-to-bigint-step1
-- Step 1: Add new column with correct data type
IF COL_LENGTH('app.customer', 'phone_number_new') IS NULL
BEGIN
    ALTER TABLE app.customer ADD phone_number_new BIGINT NULL;
END

-- Step 2: Migrate data with conversion
UPDATE app.customer
SET phone_number_new = TRY_CONVERT(BIGINT, REPLACE(REPLACE(phone_number, '-', ''), ' ', ''))
WHERE phone_number IS NOT NULL;

-- Step 3: Drop old column and rename new column (deploy in next release after verifying)
-- IF COL_LENGTH('app.customer', 'phone_number') IS NOT NULL
-- BEGIN
--     ALTER TABLE app.customer DROP COLUMN phone_number;
--     EXEC sp_rename 'app.customer.phone_number_new', 'phone_number', 'COLUMN';
-- END
--rollback ALTER TABLE app.customer DROP COLUMN phone_number_new;
```

### Change 3: Modify NULL Constraint of a Column

Scenario: Make `app.customer.email` required (NOT NULL).

**Important:** Before making a column NOT NULL, ensure all existing rows have values.

Create `database/changelog/changes/V0003__make_email_required.sql`:

```sql
--changeset yourname:V0003-make-email-not-null
-- Step 1: Fill any NULL values with default
UPDATE app.customer
SET email = 'noemail@example.com'
WHERE email IS NULL;

-- Step 2: Alter column to NOT NULL
IF EXISTS (
    SELECT 1
    FROM sys.columns c
    JOIN sys.objects o ON o.object_id = c.object_id AND o.type = 'U'
    WHERE SCHEMA_NAME(o.schema_id) = 'app'
      AND o.name = 'customer'
      AND c.name = 'email'
      AND c.is_nullable = 1  -- Currently allows NULL
)
BEGIN
    ALTER TABLE app.customer ALTER COLUMN email NVARCHAR(500) NOT NULL;
    PRINT 'Email column is now NOT NULL';
END
ELSE
BEGIN
    PRINT 'Email column already NOT NULL';
END
--rollback ALTER TABLE app.customer ALTER COLUMN email NVARCHAR(500) NULL;
```

**To make a NOT NULL column nullable:**

```sql
--changeset yourname:V0004-make-phone-nullable
IF EXISTS (
    SELECT 1
    FROM sys.columns c
    JOIN sys.objects o ON o.object_id = c.object_id AND o.type = 'U'
    WHERE SCHEMA_NAME(o.schema_id) = 'app'
      AND o.name = 'customer'
      AND c.name = 'phone_number'
      AND c.is_nullable = 0  -- Currently NOT NULL
)
BEGIN
    ALTER TABLE app.customer ALTER COLUMN phone_number NVARCHAR(20) NULL;
    PRINT 'Phone number column is now nullable';
END
--rollback ALTER TABLE app.customer ALTER COLUMN phone_number NVARCHAR(20) NOT NULL;
```

### Change 4: Modify a Stored Procedure

Scenario: Update `app.usp_add_customer` to include phone number parameter.

Create `database/changelog/changes/V0005__update_add_customer_proc.sql`:

```sql
--changeset yourname:V0005-update-add-customer-proc runOnChange:true
-- Update stored procedure to include phone number
IF OBJECT_ID(N'app.usp_add_customer', N'P') IS NOT NULL
    DROP PROCEDURE app.usp_add_customer;
GO

CREATE PROCEDURE app.usp_add_customer
    @full_name NVARCHAR(200),
    @email NVARCHAR(500) = NULL,
    @phone_number NVARCHAR(20) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    -- Validate inputs
    IF @full_name IS NULL OR LTRIM(RTRIM(@full_name)) = ''
    BEGIN
        THROW 50001, 'Customer name is required', 1;
    END

    -- Insert customer
    INSERT INTO app.customer (full_name, email, phone_number)
    VALUES (@full_name, @email, @phone_number);

    -- Return new customer ID
    SELECT SCOPE_IDENTITY() AS customer_id;
END
GO
--rollback DROP PROCEDURE IF EXISTS app.usp_add_customer;
```

**Key points for stored procedure changes:**

- Use `runOnChange:true` in the changeset header so Liquibase re-runs it when the file changes
- Always use `DROP ... IF EXISTS` then `CREATE`, or `CREATE OR ALTER` (SQL Server 2016+)
- Include `GO` statements to separate batches
- Test procedures thoroughly before deploying

**Alternative using CREATE OR ALTER (SQL Server 2016+):**

```sql
--changeset yourname:V0005-update-add-customer-proc runOnChange:true
CREATE OR ALTER PROCEDURE app.usp_add_customer
    @full_name NVARCHAR(200),
    @email NVARCHAR(500) = NULL,
    @phone_number NVARCHAR(20) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    IF @full_name IS NULL OR LTRIM(RTRIM(@full_name)) = ''
    BEGIN
        THROW 50001, 'Customer name is required', 1;
    END

    INSERT INTO app.customer (full_name, email, phone_number)
    VALUES (@full_name, @email, @phone_number);

    SELECT SCOPE_IDENTITY() AS customer_id;
END
--rollback DROP PROCEDURE IF EXISTS app.usp_add_customer;
```

### Change 5: Modify a View

Scenario: Update `app.v_customer_basic` to include phone number and order count.

Create `database/changelog/changes/V0006__update_customer_view.sql`:

```sql
--changeset yourname:V0006-update-customer-view runOnChange:true
-- Update customer view to include phone and order count
IF OBJECT_ID(N'app.v_customer_basic', N'V') IS NOT NULL
    DROP VIEW app.v_customer_basic;
GO

CREATE VIEW app.v_customer_basic AS
SELECT
    c.customer_id,
    c.full_name,
    c.email,
    c.phone_number,
    c.created_at,
    COUNT(o.order_id) AS order_count,
    ISNULL(SUM(o.order_total), 0) AS total_spent
FROM app.customer c
LEFT JOIN app.orders o ON o.customer_id = c.customer_id
GROUP BY
    c.customer_id,
    c.full_name,
    c.email,
    c.phone_number,
    c.created_at;
GO
--rollback DROP VIEW IF EXISTS app.v_customer_basic;
```

**Best practices for view changes:**

- Use `runOnChange:true` so the view is recreated when the definition changes
- Always drop then create (or use `CREATE OR ALTER` for SQL Server 2016+)
- Test views with sample data before deploying
- Document view dependencies (if view A depends on view B, ensure proper order)

**Alternative with CREATE OR ALTER:**

```sql
--changeset yourname:V0006-update-customer-view runOnChange:true
CREATE OR ALTER VIEW app.v_customer_basic AS
SELECT
    c.customer_id,
    c.full_name,
    c.email,
    c.phone_number,
    c.created_at,
    COUNT(o.order_id) AS order_count,
    ISNULL(SUM(o.order_total), 0) AS total_spent
FROM app.customer c
LEFT JOIN app.orders o ON o.customer_id = c.customer_id
GROUP BY
    c.customer_id,
    c.full_name,
    c.email,
    c.phone_number,
    c.created_at;
--rollback DROP VIEW IF EXISTS app.v_customer_basic;
```

### Applying All Changes

After creating all the changeset files, update your master changelog:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <!-- Baseline -->
    <include file="baseline/V0000__baseline.xml" relativeToChangelogFile="true"/>

    <!-- Changes -->
    <include file="changes/V0001__add_orders_table.sql" relativeToChangelogFile="true"/>
    <include file="changes/V0002__modify_customer_email_length.sql" relativeToChangelogFile="true"/>
    <include file="changes/V0003__make_email_required.sql" relativeToChangelogFile="true"/>
    <include file="changes/V0005__update_add_customer_proc.sql" relativeToChangelogFile="true"/>
    <include file="changes/V0006__update_customer_view.sql" relativeToChangelogFile="true"/>
</databaseChangeLog>
```

**Deployment workflow:**

```bash
# 1. Check what will be applied
liquibase status --verbose

# 2. Preview SQL (dry run)
liquibase updateSQL > deployment-preview.sql

# 3. Review the preview
cat deployment-preview.sql

# 4. Apply changes
liquibase update

# 5. Verify changes
liquibase status

# 6. Tag the release
liquibase tag release-2025-11-11
```

## Configure Liquibase

Create `liquibase.properties` at the project root:

```properties
url=jdbc:sqlserver://<HOST>:<PORT>;databaseName=<DB>
username=<USER>
password=<PASS>
changelog-file=database/changelog/changelog.xml

# Optional: for local CLI only (path to JDBC driver)
classpath=drivers
```

Tip: Don’t commit real passwords. In CI, pass values via environment variables or secrets.

## Create a master changelog

`database/changelog/changelog.xml` includes ordered change files:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <include file="changes/V0001__create_schema_and_basics.sql" relativeToChangelogFile="true"/>
    <include file="changes/V0002__add_email_column.sql" relativeToChangelogFile="true"/>
    <include file="changes/V0003__views_procs_functions_triggers.sql" relativeToChangelogFile="true"/>
</databaseChangeLog>
```

Liquibase accepts XML, YAML, JSON, or pure SQL. This tutorial uses SQL change files for clarity.

## First change: schema and a table

Create `database/changelog/changes/V0001__create_schema_and_basics.sql`:

```sql
--changeset yourname:V0001 runOnChange:false
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'app')
BEGIN
    EXEC('CREATE SCHEMA app')
END

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE object_id = OBJECT_ID(N'[app].[customer]') AND type in (N'U'))
BEGIN
    CREATE TABLE app.customer (
        customer_id INT IDENTITY(1,1) CONSTRAINT PK_customer PRIMARY KEY,
        full_name NVARCHAR(200) NOT NULL,
        created_at DATETIME2(3) NOT NULL CONSTRAINT DF_customer_created_at DEFAULT (SYSUTCDATETIME())
    );
END
```

Notes:

- The `--changeset` header uniquely identifies the change. Use a stable author (you) and ID.
- Guards (`IF NOT EXISTS`) help idempotency and clearer error messages.

## Apply the change

CLI (local Java):

```bash
liquibase update
```

Docker (no Java/driver needed):

```bash
docker run --rm -v "$PWD":/liquibase liquibase/liquibase:latest \
  --changelog-file=database/changelog/changelog.xml \
  --url="jdbc:sqlserver://<HOST>:<PORT>;databaseName=<DB>" \
  --username="<USER>" \
  --password="<PASS>" \
  update
```

Liquibase will create two tables in your database: `DATABASECHANGELOG` and `DATABASECHANGELOGLOCK`, then run your change.

## Preview without running (dry run)

```bash
liquibase updateSQL > deploy.sql
```

This prints the SQL Liquibase would execute, without applying it.

## Evolve the schema (add a column)

Create `database/changelog/changes/V0002__add_email_column.sql`:

```sql
--changeset yourname:V0002
IF COL_LENGTH('app.customer', 'email') IS NULL
BEGIN
    ALTER TABLE app.customer ADD email NVARCHAR(320) NULL;
END
```

Apply:

```bash
liquibase update
```

## Add views, procedures, functions, and triggers

Create `database/changelog/changes/V0003__views_procs_functions_triggers.sql`:

```sql
--changeset yourname:V0003
-- View
IF OBJECT_ID(N'app.v_customer_basic', N'V') IS NOT NULL
    DROP VIEW app.v_customer_basic;
GO
CREATE VIEW app.v_customer_basic AS
SELECT customer_id, full_name, created_at, email
FROM app.customer;
GO

-- Scalar function
IF OBJECT_ID(N'app.fn_mask_email', N'FN') IS NOT NULL
    DROP FUNCTION app.fn_mask_email;
GO
CREATE FUNCTION app.fn_mask_email (@email NVARCHAR(320))
RETURNS NVARCHAR(320)
AS
BEGIN
    IF @email IS NULL RETURN NULL;
    DECLARE @at INT = CHARINDEX('@', @email);
    IF @at <= 1 RETURN @email;
    RETURN CONCAT(LEFT(@email, 1), '***', SUBSTRING(@email, @at, LEN(@email)));
END;
GO

-- Stored procedure
IF OBJECT_ID(N'app.usp_add_customer', N'P') IS NOT NULL
    DROP PROCEDURE app.usp_add_customer;
GO
CREATE PROCEDURE app.usp_add_customer
    @full_name NVARCHAR(200),
    @email NVARCHAR(320) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO app.customer (full_name, email) VALUES (@full_name, @email);
END;
GO

-- Trigger
IF OBJECT_ID(N'app.tr_customer_audit', N'TR') IS NOT NULL
    DROP TRIGGER app.tr_customer_audit;
GO
CREATE TRIGGER app.tr_customer_audit
ON app.customer
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    -- example audit hook (replace with your audit table/logic)
    -- SELECT * FROM inserted;
END;
GO
```

Apply:

```bash
liquibase update
```

## Rollbacks and tags

Liquibase rollbacks are easiest when you deploy with tags.

Tag after a successful deployment:

```bash
liquibase tag --tag=release_2025_11_11
```

Roll back to a prior tag:

```bash
liquibase rollback --tag=release_2025_10_31
```

Or roll back N changeSets:

```bash
liquibase rollbackCount 1
```

If you change a SQL file post-deploy, Liquibase will detect a checksum mismatch. If you intentionally edited a change that already ran (generally avoid this), you may need:

```bash
liquibase clearCheckSums
```

## Contexts and labels (targeted changes)

You can mark a changeSet for specific environments:

```sql
--changeset yourname:seed_demo context:dev,test
INSERT INTO app.customer (full_name, email) VALUES (N'Demo User', N'demo@example.com');
```

Run with contexts:

```bash
liquibase --contexts=dev update
```

## Multiple environments (properties files)

Create `liquibase.dev.properties` and `liquibase.prod.properties` with different JDBC URLs and credentials. Then run:

```bash
liquibase --defaultsFile=liquibase.dev.properties update
liquibase --defaultsFile=liquibase.prod.properties updateSQL > prod_deploy_preview.sql
```

Never hardcode prod secrets; use environment variables or secret stores.

## GitHub Actions (quick example)

Create `.github/workflows/liquibase-update.yml`:

```yaml
name: liquibase-update
on: [workflow_dispatch]

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'

      - name: Liquibase update
        uses: liquibase/liquibase-github-action@v4
        with:
          operation: update
          changelogFile: database/changelog/changelog.xml
          url: ${{ secrets.DB_URL }}           # e.g. jdbc:sqlserver://...;databaseName=...
          username: ${{ secrets.DB_USER }}
          password: ${{ secrets.DB_PASS }}
```

Store `DB_URL`, `DB_USER`, and `DB_PASS` in repository/environment secrets. Protect production with environment approvals.

## Common troubleshooting

### Docker Volume Mount Issues

**Error: "exec: `/liquibase/docker-entrypoint.sh`: no such file or directory"**

This occurs when mounting to `/liquibase` which overwrites the container's Liquibase installation.

**Solution:** Mount to a different path like `/workspace`:

```bash
# Wrong - overwrites /liquibase in container
docker run --rm -v /home/gds/liquibase:/liquibase liquibase/liquibase:latest ...

# Correct - mount to /workspace
docker run --rm -v /home/gds/liquibase:/workspace liquibase-custom:5.0.1 \
  --changelog-file=/workspace/database/changelog/changelog.xml ...
```

### JDBC Driver Issues

**Error: "Cannot find database driver: com.microsoft.sqlserver.jdbc.SQLServerDriver"**

The official `liquibase/liquibase` image doesn't include SQL Server JDBC drivers.

**Solution:** Build and use the custom Liquibase image from this repository:

```bash
# Build custom image with SQL Server driver (from dev container)
cd /workspaces/dbtools/docker/liquibase
docker build -t liquibase-custom:5.0.1 .

# Use the custom image (from /home/gds/liquibase directory)
cd /home/gds/liquibase
docker run --rm \
  --network=host \
  -v /home/gds/liquibase:/workspace \
  liquibase-custom:5.0.1 \
  --url="jdbc:sqlserver://localhost:1433;databaseName=testdb;encrypt=true;trustServerCertificate=true" \
  --username="sa" \
  --password='YourStrong!Passw0rd' \
  --changelog-file=/workspace/database/changelog/changelog.xml \
  update
```

### Connection Issues

**Error: "The TCP/IP connection to the host localhost, port 1433 has failed"**

When running Liquibase in Docker, `localhost` refers to the container, not your host machine.

**Solutions:**

1. **Use `--network=host` (Linux - recommended for this setup):**

   ```bash
   docker run --rm --network=host \
     -v /home/gds/liquibase:/workspace \
     liquibase-custom:5.0.1 \
     --url="jdbc:sqlserver://localhost:1433;databaseName=testdb..." ...
   ```

2. **Use `--network container:mssql1` (if SQL Server is in a container named mssql1):**

   ```bash
   docker run --rm --network container:mssql1 \
     -v /home/gds/liquibase:/workspace \
     liquibase-custom:5.0.1 ...
   ```

3. **Use `host.docker.internal` (Docker Desktop on Mac/Windows):**

   ```bash
   docker run --rm \
     -v /home/gds/liquibase:/workspace \
     liquibase-custom:5.0.1 \
     --url="jdbc:sqlserver://host.docker.internal:1433;databaseName=testdb..." ...
   ```

### Bash History Expansion Issues

**Error: "bash: !Passw0rd: event not found"**

Bash tries to expand `!` in passwords when using double quotes.

**Solution:** Use single quotes around passwords:

```bash
# Wrong - bash expands !
--password="YourStrong!Passw0rd"

# Correct - single quotes prevent expansion
--password='YourStrong!Passw0rd'
```

### Empty Baseline Generation

**Message: "changelog not generated. There are no changesets to write"**

This means the database has no objects (tables, views, procedures) to baseline.

**Solution:** See the [Troubleshooting section in Step 1](#step-1-generate-the-baseline-from-existing-database) for how to verify database contents and create sample objects.

### General Issues

- **Driver not found (CLI):** ensure `drivers/mssql-jdbc-<version>.jar` exists and `classpath=drivers` is set, or use Docker.
- **Login failed:** confirm SQL auth is enabled and the login has rights to create/alter objects.
- **Locking/timeouts:** run during a maintenance window; keep changeSets small; prefer online/index-friendly operations.
- **Checksum mismatch:** avoid editing previously deployed changeSets. If necessary, use `clearCheckSums` after understanding impact.
- **"Object exists" errors:** add `IF EXISTS/IF NOT EXISTS` guards for idempotency.

## Best practices

- One logical change per changeSet; name files clearly (`V0004__add_order_table.sql`)
- Use expand/contract for backward-compatible changes (add, backfill, switch reads, then drop)
- Tag releases; preview with `updateSQL` for risky deployments
- Keep secrets out of source; use env vars or secret stores
- Add tests: consider tSQLt for unit testing stored procedures and functions

## ChangeSet cheat sheet: common SQL Server operations

For comprehensive step-by-step examples of common database changes, see the **[Making Changes After Baseline](#making-changes-after-baseline)** section, which includes detailed examples for:

1. **Add a table** - See [Change 1: Add a New Table](#change-1-add-a-new-table)
2. **Modify data type of column** - See [Change 2: Modify Data Type of a Column](#change-2-modify-data-type-of-a-column)
3. **Modify NULL constraint** - See [Change 3: Modify NULL Constraint of a Column](#change-3-modify-null-constraint-of-a-column)
4. **Modify stored procedure** - See [Change 4: Modify a Stored Procedure](#change-4-modify-a-stored-procedure)
5. **Modify view** - See [Change 5: Modify a View](#change-5-modify-a-view)

### Quick Reference: Add a Column

```sql
--changeset yourname:add-customer-phone
IF COL_LENGTH('app.customer', 'phone_number') IS NULL
BEGIN
    ALTER TABLE app.customer ADD phone_number NVARCHAR(20) NULL;
END
--rollback ALTER TABLE app.customer DROP COLUMN phone_number;
```

### Quick Reference: Delete a Column

Note: Deleting columns is destructive. Prefer expand/contract: stop writes/reads first, then drop later.

```sql
--changeset yourname:drop-customer-legacy-col
IF COL_LENGTH('app.customer', 'legacy_code') IS NOT NULL
BEGIN
    ALTER TABLE app.customer DROP COLUMN legacy_code;
END
--rollback ALTER TABLE app.customer ADD legacy_code NVARCHAR(100) NULL;
```

### Quick Reference: Drop a Table

Destructive. Ensure the table is no longer needed.

```sql
--changeset yourname:drop-temp-table
IF OBJECT_ID(N'app.temp_processing', N'U') IS NOT NULL
BEGIN
    DROP TABLE app.temp_processing;
END
--rollback CREATE TABLE app.temp_processing (id INT PRIMARY KEY, data NVARCHAR(MAX));
```

## How Liquibase integrates with GitHub for CI/CD

- Keep your SQL change logs in the GitHub repo (e.g., `database/changelog/changelog.xml` and `changes/*.sql`). The workflow checks out the repo and runs Liquibase against those files.
- Use GitHub “environments” (dev/test/prod) with secrets for JDBC URLs and credentials; protect prod with required reviewers.
- On pull requests: run `updateSQL` (dry run) to preview and validate scripts without changing the database.
- On merges or manual triggers: run `update` to apply changes environment-by-environment.

Example workflow (validation + dev deploy + protected prod deploy):

```yaml
name: liquibase-pipeline
on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]
  workflow_dispatch:

env:
  CHANGELOG: database/changelog/changelog.xml

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'
      - name: Liquibase validate and dry run
        uses: liquibase/liquibase-github-action@v4
        with:
          operation: updateSQL
          changelogFile: ${{ env.CHANGELOG }}
          url: ${{ secrets.DEV_DB_URL }}
          username: ${{ secrets.DEV_DB_USER }}
          password: ${{ secrets.DEV_DB_PASS }}

  deploy-dev:
    if: github.event_name == 'push'
    needs: validate
    runs-on: ubuntu-latest
    environment: dev
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'
      - name: Liquibase update (Dev)
        uses: liquibase/liquibase-github-action@v4
        with:
          operation: update
          changelogFile: ${{ env.CHANGELOG }}
          url: ${{ secrets.DEV_DB_URL }}
          username: ${{ secrets.DEV_DB_USER }}
          password: ${{ secrets.DEV_DB_PASS }}

  deploy-prod:
    if: github.event_name == 'workflow_dispatch'
    needs: deploy-dev
    runs-on: ubuntu-latest
    environment:
      name: prod
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'
      - name: Liquibase update (Prod)
        uses: liquibase/liquibase-github-action@v4
        with:
          operation: update
          changelogFile: ${{ env.CHANGELOG }}
          url: ${{ secrets.PROD_DB_URL }}
          username: ${{ secrets.PROD_DB_USER }}
          password: ${{ secrets.PROD_DB_PASS }}
```

Notes:

- For Docker-based execution, replace the action step with a `docker run liquibase/liquibase` invocation mounting the repo (`-v "$GITHUB_WORKSPACE":/liquibase`).
- Use contexts/labels in changeSets to apply environment-specific data or operations.

## Next steps

- Add CI linting (SQLFluff) and unit tests (tSQLt) to your pipeline
- Introduce contexts/labels for seed data and environment-specific operations
- Implement approvals for staging/production

## References

- Liquibase docs: `https://docs.liquibase.com/`
- SQL Server JDBC driver: `https://learn.microsoft.com/sql/connect/jdbc/`
- GitHub Action: `https://github.com/liquibase/liquibase-github-action`

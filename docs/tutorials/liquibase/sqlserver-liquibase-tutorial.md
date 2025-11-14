# Beginner's Tutorial: Database Change Management with Liquibase and SQL Server

## Introduction

This tutorial teaches you **database change management** from the ground up using Liquibase and Microsoft SQL Server. You'll learn what CI/CD means for databases, why it matters, and how to safely deploy schema changes across multiple environments.

**What you'll learn:**

- Core concepts: CI/CD, change management, environment promotion
- How to track and version database changes with Liquibase
- Safe deployment patterns: dev → stage → prod
- Baselining existing databases and managing incremental changes
- Real-world workflows with tables, views, stored procedures, and functions

**What you'll build:**

A complete Liquibase project that manages a customer database across three environments (dev, stage, prod) running on the same SQL Server instance.

## Table of Contents

- [Understanding CI/CD for Databases](#understanding-cicd-for-databases)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Project Structure](#project-structure)
- [Step 1: Create Three Database Environments](#step-1-create-three-database-environments)
- [Step 2: Populate Development with Existing Objects](#step-2-populate-development-with-existing-objects)
- [Step 3: Configure Liquibase for Each Environment](#step-3-configure-liquibase-for-each-environment)
- [Step 4: Generate Baseline from Development](#step-4-generate-baseline-from-development)
- [Step 5: Review and Fix the Baseline](#step-5-review-and-fix-the-baseline)
- [Step 6: Deploy Baseline Across Environments](#step-6-deploy-baseline-across-environments)
- [Step 7: Making Your First Change](#step-7-making-your-first-change)
- [Step 8: Deploy Change Across Environments](#step-8-deploy-change-across-environments)
- [Step 9: More Database Changes](#step-9-more-database-changes)
- [Step 10: Rollbacks and Tags](#step-10-rollbacks-and-tags)
- [Understanding the Deployment Pipeline](#understanding-the-deployment-pipeline)
- [Common Troubleshooting](#common-troubleshooting)
- [Best Practices](#best-practices)
- [Next Steps](#next-steps)

## Understanding CI/CD for Databases

### What is CI/CD?

**CI/CD** stands for **Continuous Integration** and **Continuous Deployment**:

- **Continuous Integration (CI)**: Automatically testing and validating changes when developers commit code
- **Continuous Deployment (CD)**: Automatically deploying validated changes through environments to production

### Why does it matter for databases?

Without CI/CD, database changes are often:

- **Manual**: Someone runs SQL scripts by hand
- **Error-prone**: Easy to run wrong script, skip steps, or apply to wrong environment
- **Untraceable**: Hard to know what ran where and when
- **Risky**: Production failures from untested changes

With CI/CD for databases, you get:

- **Version control**: Every change is tracked in Git
- **Repeatability**: Same change deploys identically across all environments
- **Safety**: Test in dev and stage before production
- **Auditability**: Complete history of what changed and when
- **Rollback capability**: Undo changes if problems occur

### What is Environment Promotion?

**Environment promotion** means deploying changes through a series of environments in order:

```
Development (dev) → Staging (stage) → Production (prod)
```

**Why this order?**

1. **Development (testdbdev)**: Where you create and test changes first
   - Break things here, it's okay!
   - Rapid iteration and experimentation
   - May have test/sample data

2. **Staging (testdbstg)**: Pre-production environment that mimics production
   - Same structure as production
   - Test the exact deployment process
   - Catch integration issues before prod

3. **Production (testdbprd)**: Real environment with real users and data
   - Only deploy after dev and stage succeed
   - Minimize risk, maximize stability
   - Apply same changes that worked in stage

### What is a Baseline?

A **baseline** is a snapshot of your database's current state when you start using Liquibase.

**Why do you need it?**

- You have existing tables, views, stored procedures already in production
- Liquibase needs to know "this is the starting point"
- Future changes build on top of the baseline

**Analogy**: Think of it like joining a conversation midway. The baseline is "everything said so far" so you can track "everything said from now on."

## Prerequisites

**Required:**

- SQL Server instance you can connect to (we'll use a dev container with SQL Server)
- Docker installed (to run Liquibase without installing Java locally)

**What we'll use:**

- SQL Server running in a dev container (accessible at `localhost:1433`)
- Docker to run Liquibase commands
- Three databases on the same server: `testdbdev`, `testdbstg`, `testdbprd`

**No need to install:**

- Java (Docker handles it)
- Liquibase CLI (Docker handles it)
- JDBC drivers (included in custom Docker image)

## Environment Setup

### Check SQL Server is Running

First, verify you can connect to SQL Server:

```bash
# Test connection (should show server name and date)
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "SELECT @@SERVERNAME AS ServerName, GETDATE() AS CurrentTime"
```

**Expected output:**

```
ServerName    CurrentTime
------------- -----------------------
6609bb8b43cc  2025-11-13 20:00:00.000
```

### Build Custom Liquibase Docker Image

The official Liquibase image doesn't include SQL Server drivers. Build a custom image:

```bash
# Navigate to Liquibase Dockerfile location
cd /workspaces/dbtools/docker/liquibase

# Build custom image with SQL Server JDBC drivers
docker build -t liquibase-custom:5.0.1 .

# Verify image was created
docker images | grep liquibase-custom
```

## Project Structure

Create a clear directory structure for your Liquibase project:

```bash
# Create project directory
mkdir -p /data/liquibase-tutorial
cd /data/liquibase-tutorial

# Create folder structure
mkdir -p database/changelog/baseline
mkdir -p database/changelog/changes
mkdir -p env
```

**What each folder means:**

```
/data/liquibase-tutorial/
├── database/
│   └── changelog/
│       ├── changelog.xml           # Master file listing all changes in order
│       ├── baseline/               # Initial database snapshot
│       │   └── V0000__baseline.xml
│       └── changes/                # Incremental changes after baseline
│           ├── V0001__add_orders_table.sql
│           ├── V0002__modify_customer_email.sql
│           └── V0003__update_stored_procedure.sql
└── env/
    ├── liquibase.dev.properties    # Development database connection
    ├── liquibase.stage.properties  # Staging database connection
    └── liquibase.prod.properties   # Production database connection
```

## Step 1: Create Three Database Environments

Create three databases on the same SQL Server to represent dev, stage, and prod:

```bash
# Create development database
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = 'testdbdev')
CREATE DATABASE testdbdev;
"

# Create staging database
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = 'testdbstg')
CREATE DATABASE testdbstg;
"

# Create production database
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = 'testdbprd')
CREATE DATABASE testdbprd;
"

# Verify all three databases exist
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
SELECT name, database_id, create_date
FROM sys.databases
WHERE name IN ('testdbdev', 'testdbstg', 'testdbprd')
ORDER BY name
"
```

**Expected output:**

```
name        database_id  create_date
----------- ------------ -----------------------
testdbdev   5            2025-11-13 20:00:00.000
testdbprd   7            2025-11-13 20:00:01.000
testdbstg   6            2025-11-13 20:00:00.500
```

**What did we just do?**

- Created three empty databases
- All on the same SQL Server instance (simulating separate environments)
- In real production, these would be on different servers/clouds

## Step 2: Populate Development with Existing Objects

Now create some database objects in **development only**. This simulates an existing database you want to start managing with Liquibase.

```bash
# Create schema, tables, views, procedures, and functions in DEVELOPMENT
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
USE testdbdev;

-- Step 1: Create schema
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'app')
    EXEC('CREATE SCHEMA app');

-- Step 2: Create customer table
IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE object_id = OBJECT_ID(N'[app].[customer]') AND type = 'U')
BEGIN
    CREATE TABLE app.customer (
        customer_id INT IDENTITY(1,1) CONSTRAINT PK_customer PRIMARY KEY,
        full_name NVARCHAR(200) NOT NULL,
        email NVARCHAR(320) NULL,
        phone_number NVARCHAR(20) NULL,
        created_at DATETIME2(3) NOT NULL CONSTRAINT DF_customer_created_at DEFAULT (SYSUTCDATETIME())
    );
    PRINT 'Created table app.customer';
END

-- Step 3: Create view
IF OBJECT_ID(N'app.v_customer_basic', N'V') IS NOT NULL
    DROP VIEW app.v_customer_basic;

CREATE VIEW app.v_customer_basic AS
SELECT customer_id, full_name, email, created_at
FROM app.customer;
PRINT 'Created view app.v_customer_basic';

-- Step 4: Create stored procedure
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
    SELECT SCOPE_IDENTITY() AS customer_id;
END;
GO
PRINT 'Created procedure app.usp_add_customer';

-- Step 5: Create function
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
PRINT 'Created function app.fn_mask_email';

-- Step 6: Insert sample data
INSERT INTO app.customer (full_name, email, phone_number)
VALUES
    (N'Alice Anderson', N'alice@example.com', N'555-0001'),
    (N'Bob Brown', N'bob@example.com', N'555-0002'),
    (N'Carol Chen', N'carol@example.com', NULL);

SELECT 'Setup complete. Created schema, table, view, procedure, function, and sample data.' AS Result;
"
```

**Verify objects were created in development:**

```bash
# List all objects in app schema (development only)
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
USE testdbdev;
SELECT
    SCHEMA_NAME(schema_id) AS SchemaName,
    name AS ObjectName,
    type_desc AS ObjectType
FROM sys.objects
WHERE schema_id = SCHEMA_ID('app')
ORDER BY type_desc, name;
"

# Check sample data
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
USE testdbdev;
SELECT customer_id, full_name, email FROM app.customer;
"
```

**What did we just do?**

- Created a complete working database in development
- Schema, table, view, stored procedure, function
- Added sample data
- Staging and production are still empty (we'll deploy to them next)

**Why only in dev?**

- This represents your "existing production database" scenario
- In real life, you'd generate baseline from production
- For this tutorial, we're using dev as our "existing" database

## Step 3: Configure Liquibase for Each Environment

Create properties files to connect Liquibase to each environment:

```bash
# Development properties
cat > /data/liquibase-tutorial/env/liquibase.dev.properties << 'EOF'
# Development Environment Connection
url=jdbc:sqlserver://localhost:1433;databaseName=testdbdev;encrypt=true;trustServerCertificate=true
username=sa
password=YourStrong!Passw0rd
changelog-file=database/changelog/changelog.xml
search-path=/workspace
logLevel=info
EOF

# Staging properties
cat > /data/liquibase-tutorial/env/liquibase.stage.properties << 'EOF'
# Staging Environment Connection
url=jdbc:sqlserver://localhost:1433;databaseName=testdbstg;encrypt=true;trustServerCertificate=true
username=sa
password=YourStrong!Passw0rd
changelog-file=database/changelog/changelog.xml
search-path=/workspace
logLevel=info
EOF

# Production properties
cat > /data/liquibase-tutorial/env/liquibase.prod.properties << 'EOF'
# Production Environment Connection
url=jdbc:sqlserver://localhost:1433;databaseName=testdbprd;encrypt=true;trustServerCertificate=true
username=sa
password=YourStrong!Passw0rd
changelog-file=database/changelog/changelog.xml
search-path=/workspace
logLevel=info
EOF

# Verify files were created
ls -la /data/liquibase-tutorial/env/
```

**What each property means:**

- `url`: JDBC connection string (notice `databaseName` differs per environment)
- `username/password`: SQL Server credentials (in real life, use secrets!)
- `changelog-file`: Master file that lists all changes
- `search-path`: Where Liquibase looks for files inside Docker container
- `logLevel`: How much detail to show (info is good for learning)

**Security note**: Never commit real passwords to Git! In production, use:

- Environment variables: `password=${DB_PASSWORD}`
- Secret management: Azure Key Vault, AWS Secrets Manager, etc.
- CI/CD platform secrets: GitHub Secrets, GitLab CI/CD variables

## Step 4: Generate Baseline from Development

Now use Liquibase to capture the current state of development as a **baseline**:

```bash
# Change to project directory
cd /data/liquibase-tutorial

# Generate baseline from development database
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  --changelog-file=/workspace/database/changelog/baseline/V0000__baseline.xml \
  generateChangeLog

# Check the generated file
cat database/changelog/baseline/V0000__baseline.xml
```

**What happened?**

- Liquibase connected to `testdbdev`
- Scanned all database objects (tables, views, indexes, constraints)
- Generated XML representing the current state
- Saved it as `V0000__baseline.xml`

**Important limitations:**

- `generateChangeLog` captures tables and views well
- Often misses stored procedures and functions (we'll add manually)
- May not include `schemaName` attribute (we'll fix)
- May not capture all constraints correctly (review carefully)
- Doesn't capture database users, roles, or permissions
- Triggers are often missed or incorrectly generated

**What to check in the generated baseline:**

1. **Schema references**: Ensure all objects have `schemaName="app"` attribute
2. **Data types**: Verify column types match exactly (especially NVARCHAR vs VARCHAR)
3. **Constraints**: Check primary keys, foreign keys, unique constraints, and defaults
4. **Missing objects**: Compare with database to find missing procedures, functions, triggers
5. **Ordering**: Ensure foreign key tables come after their referenced tables

## Step 5: Review and Fix the Baseline

The generated baseline needs manual fixes. Let's use the automated script:

```bash
# Install Python dependency if needed
pip install pyodbc

# Fix baseline automatically
python3 /workspaces/dbtools/scripts/fix-liquibase-baseline.py \
  --baseline-file /data/liquibase-tutorial/database/changelog/baseline/V0000__baseline.xml \
  --schema app \
  --add-db-objects \
  --database testdbdev \
  --password 'YourStrong!Passw0rd' \
  --backup

# Review the fixed baseline
cat /data/liquibase-tutorial/database/changelog/baseline/V0000__baseline.xml
```

**The script automatically:**

- ✅ Adds `schemaName="app"` to all tables and views
- ✅ Creates schema creation changeset at the beginning
- ✅ Extracts stored procedures from database
- ✅ Extracts functions from database
- ✅ Creates backup of original file

**The fixed baseline should look like:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog ...>
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
            ...
        </createTable>
    </changeSet>

    <!-- Views, Procedures, Functions -->
    ...
</databaseChangeLog>
```

## Step 6: Deploy Baseline Across Environments

Now create the master changelog and deploy the baseline to each environment:

### Create Master Changelog

```bash
# Create master changelog that includes baseline
cat > /data/liquibase-tutorial/database/changelog/changelog.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <!-- Baseline: initial database state -->
    <include file="baseline/V0000__baseline.xml" relativeToChangelogFile="true"/>

    <!-- Future changes will be added here -->

</databaseChangeLog>
EOF
```

### Deploy to Development (Sync Only)

Development already has these objects, so we **sync** the baseline (mark as executed without running):

```bash
cd /data/liquibase-tutorial

# Sync baseline to development (don't actually run DDL)
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  changelogSync

# Tag the baseline
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  tag baseline
```

**What is changelogSync?**

- Tells Liquibase "these changes already ran"
- Updates `DATABASECHANGELOG` table without executing SQL
- Used for existing databases when you generate a baseline

**Verify sync worked:**

```bash
# Check DATABASECHANGELOG table
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
USE testdbdev;
SELECT ID, AUTHOR, FILENAME, DATEEXECUTED, TAG
FROM DATABASECHANGELOG
ORDER BY DATEEXECUTED;
"
```

### Deploy to Staging (Full Deployment)

Staging is empty, so we **deploy** the baseline (actually run all DDL):

```bash
cd /data/liquibase-tutorial

# Preview what will run
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  updateSQL

# Deploy to staging
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  update

# Tag the baseline
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  tag baseline
```

**Verify deployment:**

```bash
# Check objects exist in staging
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
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

### Deploy to Production (Full Deployment)

Production is also empty, so we deploy the baseline:

```bash
cd /data/liquibase-tutorial

# Preview what will run
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.prod.properties \
  updateSQL

# Deploy to production
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.prod.properties \
  update

# Tag the baseline
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.prod.properties \
  tag baseline
```

**Verify deployment:**

```bash
# Check objects exist in production
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
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

**What did we accomplish?**

✅ All three environments now have identical schemas
✅ Liquibase is tracking what ran where
✅ We can now deploy future changes safely

## Step 7: Making Your First Change

Now let's make a new database change: add an `orders` table.

### Create the Change File

**Choosing between SQL and YAML format:**

- **SQL format**: Best for complex queries, stored procedures, functions, views
- **YAML/XML format**: Best for tables, indexes, constraints (database-agnostic)
- You can mix both formats in the same project

For this tutorial, we'll use **SQL format** for simplicity and readability.

```bash
# Create the change file
cat > /data/liquibase-tutorial/database/changelog/changes/V0001__add_orders_table.sql << 'EOF'
--changeset tutorial:V0001-add-orders-table
-- Purpose: Add orders table to track customer purchases
-- This change adds a new table with foreign key to customer table

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

    -- Index for lookups by customer
    CREATE NONCLUSTERED INDEX IX_orders_customer
        ON app.orders(customer_id);

    -- Index for date-based queries
    CREATE NONCLUSTERED INDEX IX_orders_date
        ON app.orders(order_date DESC);

    PRINT 'Created app.orders table with indexes';
END
ELSE
BEGIN
    PRINT 'Table app.orders already exists';
END

--rollback IF OBJECT_ID(N'app.orders', N'U') IS NOT NULL DROP TABLE app.orders;
EOF
```

**Understanding the change file:**

- `--changeset tutorial:V0001-add-orders-table`: Unique identifier
- `IF NOT EXISTS`: Makes it safe to re-run (idempotent)
- Foreign key links orders to customers
- Indexes for performance
- `--rollback`: SQL to undo this change

### Update Master Changelog

```bash
# Update changelog.xml to include the new change
cat > /data/liquibase-tutorial/database/changelog/changelog.xml << 'EOF'
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

</databaseChangeLog>
EOF
```

## Step 8: Deploy Change Across Environments

Now deploy this change through dev → stage → prod:

### Deploy to Development

```bash
cd /data/liquibase-tutorial

# Check what will be deployed (should show V0001 only)
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  status --verbose

# Preview the SQL
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  updateSQL

# Deploy to development
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  update

# Tag this release
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  tag release-v1.1
```

**Verify in development:**

```bash
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
USE testdbdev;

-- Check table exists
SELECT name, type_desc FROM sys.objects WHERE name = 'orders' AND schema_id = SCHEMA_ID('app');

-- Check indexes
SELECT i.name AS IndexName, i.type_desc
FROM sys.indexes i
JOIN sys.objects o ON i.object_id = o.object_id
WHERE o.name = 'orders' AND SCHEMA_NAME(o.schema_id) = 'app';
"
```

### Deploy to Staging

After testing in dev, promote to staging:

```bash
cd /data/liquibase-tutorial

# Preview (should be identical to what ran in dev)
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  updateSQL

# Deploy to staging
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  update

# Tag this release
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  tag release-v1.1
```

**Verify in staging:**

```bash
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
USE testdbstg;
SELECT name, type_desc FROM sys.objects WHERE name = 'orders' AND schema_id = SCHEMA_ID('app');
"
```

### Deploy to Production

After staging succeeds, deploy to production:

```bash
cd /data/liquibase-tutorial

# Preview (should be identical to dev and stage)
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.prod.properties \
  updateSQL

# Deploy to production
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.prod.properties \
  update

# Tag this release
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.prod.properties \
  tag release-v1.1
```

**Verify in production:**

```bash
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
USE testdbprd;
SELECT name, type_desc FROM sys.objects WHERE name = 'orders' AND schema_id = SCHEMA_ID('app');
"
```

**What did we just do?**

✅ Created a new change (add orders table)
✅ Deployed to dev first and tested
✅ Promoted to staging
✅ Promoted to production
✅ All three environments now have identical schemas
✅ Complete audit trail in DATABASECHANGELOG

## Step 9: More Database Changes

Let's make several more changes to demonstrate common scenarios:

### Change 2: Modify Column Length

Increase email field from 320 to 500 characters:

```bash
cat > /data/liquibase-tutorial/database/changelog/changes/V0002__increase_email_length.sql << 'EOF'
--changeset tutorial:V0002-increase-email-length
-- Purpose: Increase email column to support longer email addresses

IF EXISTS (
    SELECT 1
    FROM sys.columns c
    JOIN sys.objects o ON o.object_id = c.object_id AND o.type = 'U'
    JOIN sys.types t ON t.user_type_id = c.user_type_id
    WHERE SCHEMA_NAME(o.schema_id) = 'app'
      AND o.name = 'customer'
      AND c.name = 'email'
      AND c.max_length < 1000  -- 500 * 2 bytes for NVARCHAR
)
BEGIN
    ALTER TABLE app.customer ALTER COLUMN email NVARCHAR(500) NULL;
    PRINT 'Increased email column to NVARCHAR(500)';
END
ELSE
BEGIN
    PRINT 'Email column already NVARCHAR(500) or larger';
END

--rollback ALTER TABLE app.customer ALTER COLUMN email NVARCHAR(320) NULL;
EOF
```

### Change 3: Update Stored Procedure

Add phone number parameter to the customer creation procedure:

```bash
cat > /data/liquibase-tutorial/database/changelog/changes/V0003__update_add_customer_proc.sql << 'EOF'
--changeset tutorial:V0003-update-add-customer-proc runOnChange:true
-- Purpose: Add phone_number parameter to customer creation procedure
-- Note: runOnChange:true means this will re-execute if the changeset content changes

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

    -- Validate name is provided
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
EOF
```

**Understanding `runOnChange`:**

The `runOnChange:true` attribute is crucial for managing views, stored procedures, and functions:

- **Without `runOnChange`**: Changeset runs once, never again (normal behavior)
- **With `runOnChange:true`**: Liquibase recalculates the MD5 checksum
  - If content changed: Re-executes the changeset
  - If content unchanged: Skips execution

**When to use `runOnChange`:**

✅ Views (definition changes)
✅ Stored procedures (parameter or logic changes)
✅ Functions (signature or implementation changes)
✅ Configuration data that may need updates

❌ Tables (use ALTER TABLE in new changesets instead)
❌ One-time data migrations

**Best practice**: Always use `DROP IF EXISTS` then `CREATE` pattern for objects with `runOnChange:true`.

### Change 4: Update View

Add phone number and order statistics to customer view:

```bash
cat > /data/liquibase-tutorial/database/changelog/changes/V0004__update_customer_view.sql << 'EOF'
--changeset tutorial:V0004-update-customer-view runOnChange:true
-- Purpose: Enhance customer view with phone number and order statistics

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
EOF
```

### Update Master Changelog with All Changes

```bash
cat > /data/liquibase-tutorial/database/changelog/changelog.xml << 'EOF'
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
    <include file="changes/V0002__increase_email_length.sql" relativeToChangelogFile="true"/>
    <include file="changes/V0003__update_add_customer_proc.sql" relativeToChangelogFile="true"/>
    <include file="changes/V0004__update_customer_view.sql" relativeToChangelogFile="true"/>

</databaseChangeLog>
EOF
```

### Deploy All Changes to Development

```bash
cd /data/liquibase-tutorial

# Check what will deploy (should show V0002, V0003, V0004)
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  status --verbose

# Deploy to development
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  update

# Tag the release
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  tag release-v1.2
```

### Deploy to Staging

```bash
cd /data/liquibase-tutorial

docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  update

docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  tag release-v1.2
```

### Deploy to Production

```bash
cd /data/liquibase-tutorial

docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.prod.properties \
  update

docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.prod.properties \
  tag release-v1.2
```

**Verify all changes applied:**

```bash
# Check email column length in production
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
USE testdbprd;

-- Check email column length
SELECT c.name AS ColumnName, t.name AS DataType, c.max_length AS MaxLength
FROM sys.columns c
JOIN sys.types t ON c.user_type_id = t.user_type_id
JOIN sys.objects o ON c.object_id = o.object_id
WHERE SCHEMA_NAME(o.schema_id) = 'app'
  AND o.name = 'customer'
  AND c.name = 'email';

-- Check procedure parameters
SELECT p.name AS ProcedureName, pm.name AS ParameterName, t.name AS DataType
FROM sys.procedures p
JOIN sys.parameters pm ON p.object_id = pm.object_id
JOIN sys.types t ON pm.user_type_id = t.user_type_id
WHERE SCHEMA_NAME(p.schema_id) = 'app'
  AND p.name = 'usp_add_customer'
ORDER BY pm.parameter_id;

-- Check view definition
EXEC sp_helptext 'app.v_customer_basic';
"
```

## Step 10: Rollbacks and Tags

### Understanding Rollbacks

Rollbacks let you undo changes if something goes wrong. Tags mark specific points you can roll back to.

**View your tags:**

```bash
# List tags in development
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
USE testdbdev;
SELECT ID, TAG, DATEEXECUTED
FROM DATABASECHANGELOG
WHERE TAG IS NOT NULL
ORDER BY DATEEXECUTED;
"
```

### Rollback to a Specific Tag

```bash
cd /data/liquibase-tutorial

# Rollback development to release-v1.1 (undo changes V0002-V0004)
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  rollback release-v1.1

# Verify rollback worked
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
USE testdbdev;
SELECT ID, AUTHOR, FILENAME, DATEEXECUTED, TAG
FROM DATABASECHANGELOG
ORDER BY DATEEXECUTED DESC;
"
```

### Re-apply After Rollback

```bash
# Re-apply changes to get back to latest
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  update
```

### Rollback by Count

```bash
# Roll back last 2 changesets
docker run --rm \
  --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  rollbackCount 2
```

## Understanding Liquibase's Tracking Mechanism

Before diving into the deployment pipeline, let's understand how Liquibase tracks changes.

### The DATABASECHANGELOG Table

When Liquibase first runs, it creates two tables:

1. **DATABASECHANGELOG**: Records every changeset executed
2. **DATABASECHANGELOGLOCK**: Prevents concurrent deployments

**DATABASECHANGELOG structure:**

```sql
SELECT * FROM DATABASECHANGELOG;
```

| Column | Purpose |
|--------|----------|
| ID | Unique identifier from `--changeset` comment |
| AUTHOR | Who created the change |
| FILENAME | Path to changelog file |
| DATEEXECUTED | When it ran |
| ORDEREXECUTED | Sequence number (1, 2, 3...) |
| EXECTYPE | Type: EXECUTED, RERAN, SKIPPED |
| MD5SUM | Checksum to detect changes |
| TAG | Optional label for rollback points |

**How Liquibase decides what to run:**

1. Reads `changelog.xml` to get list of changesets
2. Queries `DATABASECHANGELOG` to see what already ran
3. Compares MD5 checksums to detect modifications
4. Runs only new changesets (not in DATABASECHANGELOG)
5. Records execution in DATABASECHANGELOG

**Why checksums matter:**

- Prevents accidental changes to deployed changesets
- If you edit a deployed changeset, Liquibase throws an error
- This protects consistency across environments

**Viewing your change history:**

```bash
# See all executed changesets in development
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
USE testdbdev;
SELECT
    ORDEREXECUTED,
    ID,
    AUTHOR,
    FILENAME,
    DATEEXECUTED,
    TAG
FROM DATABASECHANGELOG
ORDER BY ORDEREXECUTED;
"
```

## Understanding the Deployment Pipeline

### The Complete Workflow

Here's how a typical change flows from idea to production:

```
1. Developer writes change in SQL file
   ↓
2. Add to changelog.xml
   ↓
3. Deploy to testdbdev (development)
   ↓
4. Test and verify in dev
   ↓
5. Deploy to testdbstg (staging)
   ↓
6. Integration testing in staging
   ↓
7. Deploy to testdbprd (production)
   ↓
8. Monitor production, tag release
```

### Key Principles

**Same SQL, different databases:**

- The EXACT same changelog.xml deploys to all environments
- Only connection strings differ (via properties files)
- This ensures consistency and reduces errors

**Progressive deployment:**

- Never skip environments
- Always go dev → stage → prod
- Test thoroughly at each step

**Idempotent changes:**

- Changes should be safe to re-run
- Use `IF EXISTS` / `IF NOT EXISTS`
- Liquibase tracks what ran, but guards prevent errors

**Tagging for safety:**

- Tag after each successful deployment
- Tags enable precise rollbacks
- Naming convention: `release-v1.x` or date-based `release-2025-11-13`

**Audit trail:**

- `DATABASECHANGELOG` table records everything
- Who made the change (`AUTHOR`)
- When it ran (`DATEEXECUTED`)
- Checksum to detect tampering

### Automation with CI/CD

In production, you'd automate this with GitHub Actions. Here's a realistic workflow:

```yaml
# .github/workflows/liquibase-deploy.yml
name: Database Deployment Pipeline

on:
  push:
    branches: [main]
    paths:
      - 'database/**'
      - 'env/**'
  workflow_dispatch:  # Manual trigger

env:
  LIQUIBASE_VERSION: '4.20.0'

jobs:
  # Validate changesets before deploying
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate Changelog
        run: |
          docker run --rm \
            -v ${{ github.workspace }}:/workspace \
            liquibase/liquibase:${LIQUIBASE_VERSION} \
            --changelog-file=/workspace/database/changelog/changelog.xml \
            validate

  # Deploy to development (automatic)
  deploy-dev:
    needs: validate
    runs-on: ubuntu-latest
    environment: development
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Development
        env:
          DB_PASSWORD: ${{ secrets.DEV_DB_PASSWORD }}
        run: |
          docker run --rm --network=host \
            -v ${{ github.workspace }}:/workspace \
            -e DB_PASSWORD \
            liquibase-custom:5.0.1 \
            --defaults-file=/workspace/env/liquibase.dev.properties \
            --password="${DB_PASSWORD}" \
            update

      - name: Verify Deployment
        run: |
          # Run verification queries
          ./scripts/verify-deployment.sh dev

  # Deploy to staging (requires approval)
  deploy-stage:
    needs: deploy-dev
    runs-on: ubuntu-latest
    environment: staging  # GitHub environment with required reviewers
    steps:
      - uses: actions/checkout@v4

      - name: Preview Changes
        env:
          DB_PASSWORD: ${{ secrets.STAGE_DB_PASSWORD }}
        run: |
          docker run --rm --network=host \
            -v ${{ github.workspace }}:/workspace \
            -e DB_PASSWORD \
            liquibase-custom:5.0.1 \
            --defaults-file=/workspace/env/liquibase.stage.properties \
            --password="${DB_PASSWORD}" \
            status --verbose

      - name: Deploy to Staging
        env:
          DB_PASSWORD: ${{ secrets.STAGE_DB_PASSWORD }}
        run: |
          docker run --rm --network=host \
            -v ${{ github.workspace }}:/workspace \
            -e DB_PASSWORD \
            liquibase-custom:5.0.1 \
            --defaults-file=/workspace/env/liquibase.stage.properties \
            --password="${DB_PASSWORD}" \
            update

      - name: Tag Release
        env:
          DB_PASSWORD: ${{ secrets.STAGE_DB_PASSWORD }}
        run: |
          RELEASE_TAG="release-$(date +%Y%m%d-%H%M%S)"
          docker run --rm --network=host \
            -v ${{ github.workspace }}:/workspace \
            -e DB_PASSWORD \
            liquibase-custom:5.0.1 \
            --defaults-file=/workspace/env/liquibase.stage.properties \
            --password="${DB_PASSWORD}" \
            tag "${RELEASE_TAG}"

  # Deploy to production (requires approval + manual trigger)
  deploy-prod:
    needs: deploy-stage
    runs-on: ubuntu-latest
    environment: production  # Requires multiple approvers
    if: github.event_name == 'workflow_dispatch'  # Only manual
    steps:
      - uses: actions/checkout@v4

      - name: Create Rollback Script
        env:
          DB_PASSWORD: ${{ secrets.PROD_DB_PASSWORD }}
        run: |
          # Generate rollback SQL before deployment
          docker run --rm --network=host \
            -v ${{ github.workspace }}:/workspace \
            -e DB_PASSWORD \
            liquibase-custom:5.0.1 \
            --defaults-file=/workspace/env/liquibase.prod.properties \
            --password="${DB_PASSWORD}" \
            futureRollbackSQL > rollback-$(date +%Y%m%d).sql

      - name: Upload Rollback Script
        uses: actions/upload-artifact@v3
        with:
          name: rollback-script
          path: rollback-*.sql

      - name: Deploy to Production
        env:
          DB_PASSWORD: ${{ secrets.PROD_DB_PASSWORD }}
        run: |
          docker run --rm --network=host \
            -v ${{ github.workspace }}:/workspace \
            -e DB_PASSWORD \
            liquibase-custom:5.0.1 \
            --defaults-file=/workspace/env/liquibase.prod.properties \
            --password="${DB_PASSWORD}" \
            update

      - name: Verify Production Deployment
        run: |
          ./scripts/verify-deployment.sh prod

      - name: Tag Production Release
        env:
          DB_PASSWORD: ${{ secrets.PROD_DB_PASSWORD }}
        run: |
          RELEASE_TAG="prod-release-$(date +%Y%m%d-%H%M%S)"
          docker run --rm --network=host \
            -v ${{ github.workspace }}:/workspace \
            -e DB_PASSWORD \
            liquibase-custom:5.0.1 \
            --defaults-file=/workspace/env/liquibase.prod.properties \
            --password="${DB_PASSWORD}" \
            tag "${RELEASE_TAG}"

      - name: Notify Team
        if: always()
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✅ Production deployment completed successfully!'
            })
```

**Key CI/CD features:**

- ✅ Automatic validation before deployment
- ✅ Preview changes with `status --verbose`
- ✅ Environment-based secrets (no passwords in code)
- ✅ Required approvals for stage and prod
- ✅ Automatic rollback script generation
- ✅ Verification after each deployment
- ✅ Timestamped tags for audit trail
- ✅ Team notifications

## Common Troubleshooting

### Docker Volume Mount Issues

**Error**: `exec: /liquibase/docker-entrypoint.sh: no such file or directory`

**Cause**: Mounting to `/liquibase` overwrites the container's Liquibase installation

**Fix**: Mount to `/workspace` instead:

```bash
# Wrong
-v /data/liquibase-tutorial:/liquibase

# Correct
-v /data/liquibase-tutorial:/workspace
```

### JDBC Driver Not Found

**Error**: `Cannot find database driver: com.microsoft.sqlserver.jdbc.SQLServerDriver`

**Cause**: Official Liquibase image doesn't include SQL Server drivers

**Fix**: Use the custom image you built:

```bash
# Wrong
liquibase/liquibase:latest

# Correct
liquibase-custom:5.0.1
```

### Connection Refused

**Error**: `Connection refused` or `timeout`

**Cause**: Liquibase container can't reach SQL Server

**Fix**: Use `--network=host`:

```bash
docker run --rm --network=host ...
```

### Password with Special Characters

**Error**: `bash: !Passw0rd: event not found`

**Cause**: Bash interprets `!` in double quotes

**Fix**: Use single quotes:

```bash
# Wrong
--password="YourStrong!Passw0rd"

# Correct
--password='YourStrong!Passw0rd'
```

### Checksum Mismatch

**Error**: `Validation Failed: changesets have checksum mismatch`

**Cause**: You edited a changeset that already ran

**Prevention**: Never edit deployed changesets! Create new ones

**Recovery** (if you must):

```bash
docker run --rm --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  clearCheckSums
```

### Changeset Already Exists Error

**Error**: `Changeset <id> has already been executed`

**Cause**: Two changesets have the same ID

**Fix**: Ensure every changeset has a unique ID. Use timestamp-based IDs:

```sql
-- Good: Timestamp + sequence + description
--changeset tutorial:20251113-01-add-orders-table

-- Bad: Generic ID that might conflict
--changeset tutorial:001-add-table
```

### Foreign Key Constraint Failure

**Error**: `FK_orders_customer could not be created because the referenced table does not exist`

**Cause**: Changesets running out of order

**Fix**: Check your changelog includes files in correct order:

```xml
<!-- Wrong: orders before customer -->
<include file="changes/V0001__add_orders_table.sql"/>
<include file="baseline/V0000__baseline.xml"/>

<!-- Correct: baseline (with customer) before orders -->
<include file="baseline/V0000__baseline.xml"/>
<include file="changes/V0001__add_orders_table.sql"/>
```

### Locks Not Released

**Error**: `Waiting for changelog lock...`

**Cause**: Previous run didn't complete (crash, Ctrl+C, connection loss)

**Fix**: Force release the lock:

```bash
docker run --rm --network=host \
  -v /data/liquibase-tutorial:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  releaseLocks
```

**Verify lock status first:**

```bash
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
USE testdbdev;
SELECT * FROM DATABASECHANGELOGLOCK;
"
```

### Rollback SQL Not Defined

**Error**: `No rollback statement defined for changeset`

**Cause**: Trying to rollback a changeset without `--rollback` comment

**Prevention**: Always include rollback in SQL changesets:

```sql
--changeset author:id
CREATE TABLE app.products (...)

-- Required for rollback to work:
--rollback DROP TABLE app.products;
```

**Alternative**: Use `rollbackSQL` to manually specify:

```bash
liquibase rollbackSQL --tag=v1.0 > rollback-v1.0.sql
cat rollback-v1.0.sql  # Review before running
```

## Best Practices

### Use Preconditions for Safety

Preconditions validate assumptions before running changesets:

```yaml
databaseChangeLog:
  - changeSet:
      id: add-email-index
      author: team
      preConditions:
        - onFail: MARK_RAN  # Skip if condition fails
        - not:
            - indexExists:
                tableName: customer
                indexName: IX_customer_email
      changes:
        - createIndex:
            tableName: customer
            indexName: IX_customer_email
            columns:
              - column:
                  name: email
```

**Common precondition checks:**

- `tableExists`: Ensure table exists before modifying
- `columnExists`: Check column exists before altering
- `indexExists`: Prevent duplicate index creation
- `dbms`: Run only on specific database types
- `runningAs`: Verify correct database user

**onFail options:**

- `HALT`: Stop deployment (default, safest)
- `MARK_RAN`: Mark as executed but skip (for optional changes)
- `WARN`: Log warning and continue

### Changeset Design

✅ **One logical change per file**

- Add one table, modify one column, update one procedure
- Makes rollbacks easier
- Easier to review and understand

✅ **Use descriptive names**

- `V0001__add_orders_table.sql` ✓
- `V0001.sql` ✗

✅ **Include purpose comments**

- Explain WHY not just WHAT
- Future you will thank you

✅ **Always include rollback**

- Even if it's just `DROP TABLE`
- Enables safe rollback

✅ **Make changes idempotent**

- Use `IF EXISTS` / `IF NOT EXISTS`
- Safe to re-run

### Using Contexts for Conditional Deployment

Contexts let you selectively run changesets based on environment:

```sql
--changeset tutorial:V0005-add-test-data context:dev,test
-- This only runs in dev and test environments, never in production
INSERT INTO app.customer (full_name, email)
VALUES ('Test User', 'test@example.com');
```

**Running with contexts:**

```bash
# Development: runs changesets with context:dev
liquibase update --contexts=dev

# Production: skip test data by not specifying dev context
liquibase update --contexts=prod
```

**Common context patterns:**

- `dev`: Test data, debug features
- `test`: Test data for automated tests
- `prod`: Production-only changes (alerts, monitoring)
- `migration`: One-time data migrations
- `!prod`: Everything except production

**Best practice**: Use contexts sparingly. Most changesets should run everywhere.

### Deployment Workflow

✅ **Always preview before applying**

```bash
liquibase updateSQL > preview.sql
cat preview.sql  # Review before running
liquibase update
```

✅ **Tag every release**

```bash
liquibase tag release-v1.2
```

✅ **Test in dev, promote to stage, then prod**

- Never skip environments
- Same SQL everywhere

✅ **Use source control (Git)**

- Commit changelog files
- Track changes over time
- Enable collaboration

### Security

✅ **Never commit passwords to Git**

- Use environment variables
- Use secret management tools
- Template `.properties` files, gitignore actual files

✅ **Use least-privilege accounts**

- Don't use `sa` in production
- Create dedicated Liquibase user
- Grant only necessary permissions

**Example: Create dedicated Liquibase user**

```sql
-- Create Liquibase service account
CREATE LOGIN liquibase_svc WITH PASSWORD = 'SecurePassword123!';
CREATE USER liquibase_svc FOR LOGIN liquibase_svc;

-- Grant minimum necessary permissions
ALTER ROLE db_ddladmin ADD MEMBER liquibase_svc;  -- DDL operations
ALTER ROLE db_datareader ADD MEMBER liquibase_svc;  -- Read data
ALTER ROLE db_datawriter ADD MEMBER liquibase_svc;  -- Write to tracking tables

-- Grant explicit permissions if needed
GRANT CREATE TABLE TO liquibase_svc;
GRANT CREATE PROCEDURE TO liquibase_svc;
GRANT CREATE VIEW TO liquibase_svc;
```

✅ **Audit who makes changes**

- Use real names in `author` field
- Review changes in pull requests
- Require approvals for production

### Monitoring and Validation

✅ **Always verify after deployment**

Create a verification script to run after each deployment:

```bash
#!/bin/bash
# verify-deployment.sh

ENV=$1  # dev, stage, or prod
DB="testdb${ENV}"

echo "Verifying deployment to ${DB}..."

# Check last 5 executed changesets
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
USE ${DB};
SELECT TOP 5 ID, AUTHOR, DATEEXECUTED, TAG
FROM DATABASECHANGELOG
ORDER BY DATEEXECUTED DESC;
"

# Verify expected objects exist
docker exec mssql1 /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P 'YourStrong!Passw0rd' -Q "
USE ${DB};
SELECT COUNT(*) AS TableCount FROM sys.tables WHERE schema_id = SCHEMA_ID('app');
SELECT COUNT(*) AS ViewCount FROM sys.views WHERE schema_id = SCHEMA_ID('app');
SELECT COUNT(*) AS ProcCount FROM sys.procedures WHERE schema_id = SCHEMA_ID('app');
"

echo "Verification complete!"
```

✅ **Monitor deployment metrics**

Track these metrics over time:

- Number of changesets per release
- Deployment duration
- Rollback frequency
- Failed deployment rate
- Time between environments (dev → stage → prod)

✅ **Set up alerts**

Configure alerts for:

- Deployment failures
- Checksum validation failures
- Rollbacks in production
- Lock timeout issues

### Large Changes

✅ **Use expand-contract pattern**

For breaking changes (e.g., rename column):

1. **Expand**: Add new column
2. **Migrate**: Dual-write to both columns
3. **Contract**: Remove old column (later release)

✅ **Break into multiple releases**

- Don't try to do everything at once
- Allows rollback to intermediate states

### Data Migrations

When migrating data as part of schema changes, follow these patterns:

✅ **Pattern 1: Separate schema and data changes**

```xml
<!-- Release 1.5 changelog -->
<databaseChangeLog>
  <!-- Step 1: Add new column -->
  <include file="001-add-new-column.sql"/>

  <!-- Step 2: Migrate data (separate changeset) -->
  <include file="002-migrate-data.sql"/>

  <!-- Step 3: Drop old column (in next release after verification) -->
  <!-- DO NOT include in same release -->
</databaseChangeLog>
```

✅ **Pattern 2: Use transactions for data safety**

```sql
--changeset tutorial:V0010-migrate-phone-format
--rollback UPDATE app.customer SET phone_number = old_phone WHERE old_phone IS NOT NULL;

BEGIN TRANSACTION;

-- Add temporary column
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('app.customer') AND name = 'old_phone')
    ALTER TABLE app.customer ADD old_phone NVARCHAR(20) NULL;

-- Backup existing data
UPDATE app.customer
SET old_phone = phone_number
WHERE old_phone IS NULL;

-- Transform data (remove dashes from phone numbers)
UPDATE app.customer
SET phone_number = REPLACE(REPLACE(phone_number, '-', ''), ' ', '')
WHERE phone_number IS NOT NULL;

COMMIT TRANSACTION;

PRINT 'Migrated phone numbers to new format';
```

✅ **Pattern 3: Validate data after migration**

```sql
--changeset tutorial:V0011-validate-migration

-- Count records that need migration
DECLARE @invalid_count INT;
SELECT @invalid_count = COUNT(*)
FROM app.customer
WHERE phone_number LIKE '%-%' OR phone_number LIKE '% %';

-- Fail if any invalid data found
IF @invalid_count > 0
BEGIN
    DECLARE @msg NVARCHAR(200) = CONCAT('Found ', @invalid_count, ' records with invalid phone format');
    THROW 50000, @msg, 1;
END

PRINT 'Data validation passed: all phone numbers in correct format';
```

✅ **Pattern 4: Use loadData for reference data**

For loading reference data from CSV files:

```yaml
databaseChangeLog:
  - changeSet:
      id: load-countries-reference-data
      author: tutorial
      changes:
        - loadData:
            file: data/countries.csv
            tableName: countries
            schemaName: app
            columns:
              - column:
                  name: country_code
                  type: STRING
              - column:
                  name: country_name
                  type: STRING
      rollback:
        - sql: DELETE FROM app.countries WHERE country_code IN ('US', 'CA', 'MX');
```

**CSV file (`data/countries.csv`):**

```csv
country_code,country_name
US,United States
CA,Canada
MX,Mexico
```

### Common Anti-Patterns to Avoid

❌ **Don't modify deployed changesets**

```sql
-- WRONG: Editing an already-deployed changeset
--changeset tutorial:V0001-add-orders-table
CREATE TABLE app.orders (
    order_id INT,
    customer_id INT,
    order_total DECIMAL(18,2),
    status NVARCHAR(50)  -- Added this line after deployment - BREAKS CHECKSUM!
);
```

Instead, create a new changeset:

```sql
-- CORRECT: New changeset for additional column
--changeset tutorial:V0005-add-order-status
ALTER TABLE app.orders ADD status NVARCHAR(50) NULL;
```

❌ **Don't use environment-specific logic in changesets**

```sql
-- WRONG: Environment checks in SQL
IF @@SERVERNAME = 'prod-server'
    -- Do something different in prod
```

Instead, use contexts:

```sql
--changeset tutorial:V0006-add-sample-data context:dev,test
-- This only runs in dev and test
INSERT INTO app.customer VALUES (...);
```

❌ **Don't skip environments**

```
WRONG: dev → prod (skipping stage)
CORRECT: dev → stage → prod
```

❌ **Don't use SELECT * in views**

```sql
-- WRONG: Fragile view that breaks when columns added
CREATE VIEW app.v_customer_list AS
SELECT * FROM app.customer;

-- CORRECT: Explicit columns
CREATE VIEW app.v_customer_list AS
SELECT customer_id, full_name, email, created_at
FROM app.customer;
```

## Next Steps

**Level up your skills:**

1. **Add GitHub Actions**: Automate deployments
2. **Implement approval gates**: Require manual approval for prod
3. **Add database unit tests**: Use tSQLt framework
4. **Monitor deployments**: Track success/failure rates
5. **Implement blue-green deployments**: Zero-downtime releases

**Learn more:**

- [Liquibase Official Docs](https://docs.liquibase.com/)
- [SQL Server Best Practices](https://learn.microsoft.com/sql/relational-databases/)
- [Database Refactoring](https://databaserefactoring.com/)
- [CI/CD for Databases](https://www.liquibase.org/get-started/best-practices)

**Try these exercises:**

1. Add a new `products` table with foreign keys to orders
2. Create a stored procedure to calculate customer lifetime value
3. Add indexes to optimize common queries
4. Implement soft deletes (add `deleted_at` column)
5. Create an audit trigger to log changes
6. Migrate existing data from one format to another
7. Set up a GitHub Actions workflow for automated deployments
8. Practice rolling back to different tags
9. Add preconditions to prevent unsafe changes
10. Create a view that joins customers, orders, and products

## Quick Reference Guide

### Essential Liquibase Commands

**Check what will be deployed:**

```bash
liquibase status --verbose
```

**Preview SQL before running:**

```bash
liquibase updateSQL > preview.sql
```

**Deploy changes:**

```bash
liquibase update
```

**Deploy specific count of changesets:**

```bash
liquibase updateCount 3
```

**Deploy to specific tag:**

```bash
liquibase updateToTag v1.5
```

**Tag current state:**

```bash
liquibase tag release-v1.0
```

**Rollback to tag:**

```bash
liquibase rollback release-v1.0
```

**Rollback last N changes:**

```bash
liquibase rollbackCount 2
```

**Rollback to specific date:**

```bash
liquibase rollbackToDate 2025-11-13
```

**Generate rollback SQL (preview):**

```bash
liquibase rollbackSQL release-v1.0 > rollback.sql
```

**Generate future rollback script:**

```bash
liquibase futureRollbackSQL > future-rollback.sql
```

**Validate changelog:**

```bash
liquibase validate
```

**Generate baseline from existing database:**

```bash
liquibase generateChangeLog --changelog-file=baseline.xml
```

**Sync changelog (mark as executed without running):**

```bash
liquibase changelogSync
```

**Clear checksums (use with caution):**

```bash
liquibase clearCheckSums
```

**Release database lock:**

```bash
liquibase releaseLocks
```

**View change history:**

```bash
liquibase history
```

**Calculate checksum for changeset:**

```bash
liquibase calculateCheckSum <changeset-id>
```

### Common File Patterns

**SQL changeset format:**

```sql
--changeset author:unique-id
-- Description of change

SQL STATEMENTS HERE

--rollback ROLLBACK SQL HERE
```

**SQL changeset with attributes:**

```sql
--changeset author:unique-id runOnChange:true context:dev,test
-- Attributes: runOnChange, context, labels, dbms, etc.

SQL STATEMENTS HERE

--rollback ROLLBACK SQL HERE
```

**Master changelog (XML):**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <include file="baseline/baseline.xml" relativeToChangelogFile="true"/>
    <include file="changes/V0001__change.sql" relativeToChangelogFile="true"/>

</databaseChangeLog>
```

**Properties file:**

```properties
url=jdbc:sqlserver://localhost:1433;databaseName=mydb;encrypt=true;trustServerCertificate=true
username=sa
password=${DB_PASSWORD}
changelog-file=database/changelog/changelog.xml
search-path=/workspace
logLevel=info
```

### Docker Command Patterns

**Basic Liquibase command:**

```bash
docker run --rm --network=host \
  -v /path/to/project:/workspace \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  update
```

**With environment variables:**

```bash
docker run --rm --network=host \
  -v /path/to/project:/workspace \
  -e DB_PASSWORD='SecurePass123!' \
  liquibase-custom:5.0.1 \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  --password="${DB_PASSWORD}" \
  update
```

**Interactive mode for debugging:**

```bash
docker run -it --rm --network=host \
  -v /path/to/project:/workspace \
  liquibase-custom:5.0.1 \
  bash
```

### SQL Server Verification Queries

**Check executed changesets:**

```sql
SELECT
    ORDEREXECUTED,
    ID,
    AUTHOR,
    FILENAME,
    DATEEXECUTED,
    EXECTYPE,
    TAG
FROM DATABASECHANGELOG
ORDER BY ORDEREXECUTED DESC;
```

**Check lock status:**

```sql
SELECT * FROM DATABASECHANGELOGLOCK;
```

**Manually release lock (emergency only):**

```sql
UPDATE DATABASECHANGELOGLOCK SET LOCKED = 0, LOCKGRANTED = NULL, LOCKEDBY = NULL;
```

**Find changesets by tag:**

```sql
SELECT ID, AUTHOR, FILENAME, DATEEXECUTED
FROM DATABASECHANGELOG
WHERE TAG = 'release-v1.0'
ORDER BY DATEEXECUTED;
```

**Count objects by schema:**

```sql
SELECT
    SCHEMA_NAME(schema_id) AS SchemaName,
    type_desc AS ObjectType,
    COUNT(*) AS ObjectCount
FROM sys.objects
WHERE schema_id = SCHEMA_ID('app')
GROUP BY SCHEMA_NAME(schema_id), type_desc
ORDER BY type_desc;
```

### Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Connection refused | Add `--network=host` to docker run |
| JDBC driver not found | Use `liquibase-custom:5.0.1` image |
| Checksum mismatch | `liquibase clearCheckSums` (or create new changeset) |
| Lock timeout | `liquibase releaseLocks` |
| Password special chars | Use single quotes: `'Pass!word'` |
| Path issues | Mount to `/workspace` not `/liquibase` |
| Changes not detected | Check changelog.xml includes new files |
| Rollback fails | Add `--rollback` comment to changeset |

### Best Practice Checklist

- [ ] Use version control (Git) for all changelog files
- [ ] Never edit deployed changesets (create new ones instead)
- [ ] Always include rollback SQL in changesets
- [ ] Use descriptive changeset IDs (timestamp-sequence-description)
- [ ] Preview with `updateSQL` before running `update`
- [ ] Tag every release for easy rollback
- [ ] Test in dev → verify in stage → deploy to prod
- [ ] Use `runOnChange:true` for views, procedures, functions
- [ ] Include `IF EXISTS` / `IF NOT EXISTS` for idempotency
- [ ] Use contexts for environment-specific changes
- [ ] Keep passwords in secrets, not in properties files
- [ ] Verify deployment success after each environment
- [ ] Generate rollback scripts before production deployment
- [ ] Monitor DATABASECHANGELOG table regularly
- [ ] Document purpose in changeset comments
- [ ] Use preconditions for safety checks
- [ ] Separate schema and data migrations
- [ ] Use dedicated service account (not sa) in production

## References

- Liquibase Documentation: <https://docs.liquibase.com/>
- SQL Server JDBC Driver: <https://learn.microsoft.com/sql/connect/jdbc/>
- GitHub Actions: <https://github.com/liquibase/liquibase-github-action>
- Database DevOps: <https://www.liquibase.org/blog>
- This repository structure guide: `/docs/architecture/liquibase-directory-structure.md`

---

**Congratulations!** You now understand database change management, CI/CD principles, and how to safely deploy changes across environments using Liquibase. Keep practicing, and remember: always test in dev, verify in stage, then carefully deploy to production.

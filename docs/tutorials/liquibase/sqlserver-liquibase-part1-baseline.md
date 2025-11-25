# Tutorial Part 1: Baseline SQL Server + Liquibase Setup

## Environment Setup

### Step 0: Configure Environment and Aliases

Set up your environment, aliases, and the required Liquibase properties first. The helper will prompt you for:

- Tutorial scripts directory (the folder containing `scripts/`)
- Liquibase project directory (where `database/` and `env/` will live)
- SQL Server SA password (`MSSQL_LIQUIBASE_TUTORIAL_PWD`)

```bash
# Source the one-shot setup helper (env, aliases, properties)
source /path/to/your/repo/docs/tutorials/liquibase/scripts/setup_tutorial.sh
```

Tips:

- `LB_PROJECT_DIR` is where your Liquibase project (changelog/env) lives; default is `/data/liquibase-tutorial`.
- The setup script prompts for the tutorial scripts location so aliases work from anywhere.

### Start the Tutorial SQL Server Container

This tutorial uses a dedicated SQL Server container that can be safely removed after completion.

#### Build and start SQL Server container

```bash
# Navigate to the tutorial docker directory
cd "$LIQUIBASE_TUTORIAL_DIR/docker"

# Start the SQL Server container
docker compose up -d

# Verify it's running
docker ps | grep mssql_liquibase_tutorial
```

**Expected output:**

```text
mssql_liquibase_tutorial   mcr.microsoft.com/mssql/server:2022-latest   Up X seconds (healthy)   0.0.0.0:14333->1433/tcp
```

**What this does:**

- Downloads SQL Server 2025 image (if not already downloaded)
- Creates a container named `mssql_liquibase_tutorial`
- Starts SQL Server on port `1433`
- Uses the password from `$MSSQL_LIQUIBASE_TUTORIAL_PWD`
- Includes a health check to verify SQL Server is ready

**Wait for SQL Server to be ready:**

The container has a built-in health check. You can poll for the `(healthy)` status with `grep`:

```bash
# Watch the container status until it shows (healthy) (Ctrl+C to exit)
watch -n 2 "docker ps | grep 'mssql_liquibase_tutorial.*(healthy)'"
```

Or check the logs and filter for the ready message:

```bash
docker logs mssql_liquibase_tutorial 2>&1 | grep 'SQL Server is now ready for client connections'
```

#### Build Liquibase container image

The Liquibase container is a "run-once" tool (not a long-running service), so we just need to build the image:

```bash
# Navigate to the liquibase docker directory (from your repo root)
cd /path/to/your/repo/docker/liquibase

# Build the custom Liquibase image with SQL Server drivers
docker compose build

# Verify the image was created
docker images | grep liquibase

# Quick sanity check: verify the Liquibase CLI runs
# (either command is fine; -it is optional for non-interactive output)
docker run --rm liquibase:latest --version
# or
docker run -it liquibase:latest liquibase --version
```

**Note:** The Liquibase container is not meant to stay running - it executes commands and exits. We'll use `docker run` to execute Liquibase commands throughout this tutorial.

Troubleshooting:

- If you see "Cannot find database driver: com.microsoft.sqlserver.jdbc.SQLServerDriver", rebuild the image from `docker/liquibase` and re-run the version check.
- If an alias like `lb` is not found in a new shell, re-source the aliases: `source /path/to/your/repo/docs/tutorials/liquibase/scripts/setup_aliases.sh`.

### Important Note About Docker Commands

Prefer using the provided `lb` wrapper, which encapsulates the full `docker run` invocation so you don't need to know paths or Docker flags:

Heads-up: The commands below are examples to show wrapper usage. Do not run them yet. Run `lb` commands only after Step 1 (databases created) and after your properties point to those databases (created in Step 0 or Step 3). If you run them now, they will fail with connection/DB-not-found errors because the databases don’t exist yet; however, seeing Liquibase start and attempt a connection still confirms the Liquibase container image is built and accessible.

```bash
# Show status for dev
lb -e dev -- status --verbose

# Run update in stage
lb -e stage -- update
```

Note: The standalone `--` is intentional. It separates options for the `lb` wrapper (like `-e dev`) from the actual Liquibase command and its flags (for example, `status --verbose`).

Under the hood, `lb` runs Docker with the correct user, network, mounted project directory, and injects your `--defaults-file` and password.

If you prefer to run raw Docker yourself, mirror this pattern (note use of `LB_PROJECT_DIR` instead of hard-coded paths):

```bash
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v "$LB_PROJECT_DIR":/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.<ENV>.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  <LIQUIBASE_COMMAND>
```

Notes:

- The password parameter must come after the defaults file but before the Liquibase command
- Use the dedicated Docker network `liquibase_tutorial`
- Run as your user (not root) to avoid permission issues

If you see connection errors, verify the correct network and password parameter order.

### Check SQL Server is Running

Now verify you can connect to SQL Server. This test ensures your database is accessible before we start.

```bash
# Test connection (should show server name and date)
sqlcmd-tutorial -Q "SELECT @@SERVERNAME AS ServerName, GETDATE() AS CurrentTime"
```

**Expected output:**

```text
ServerName               CurrentTime
------------------------ -----------------------
mssql_liquibase_tutorial 2025-11-16 02:49:32.910
```

**Troubleshooting:**

- **Connection refused**: SQL Server might not be running. Check with `docker ps | grep mssql_liquibase_tutorial`
- **Login failed**: Password might be wrong. Verify `$MSSQL_LIQUIBASE_TUTORIAL_PWD` is set correctly

### Helper Script for sqlcmd

To simplify running SQL commands inside the tutorial SQL Server container, use the `sqlcmd-tutorial` helper (the alias is configured by `setup_aliases.sh`).

**Usage examples:**

- Run an inline query:

```bash
sqlcmd-tutorial -Q "SELECT @@SERVERNAME AS ServerName, GETDATE() AS CurrentTime;"
```

- Run a `.sql` file:

```bash
sqlcmd-tutorial create_databases.sql
```

## Project Structure

Create a clear directory structure for your Liquibase project:

```bash
# Remove existing directory if it exists from previous runs
sudo rm -rf /data/liquibase-tutorial

# Create project directory
mkdir -p /data/liquibase-tutorial
cd /data/liquibase-tutorial

# Create folder structure
mkdir -p database/changelog/baseline
mkdir -p database/changelog/changes
mkdir -p env
```

**Quick review: verify directories were created**

```bash
ls -R /data/liquibase-tutorial
```

You should see `database/changelog/baseline`, `database/changelog/changes`, and `env` in the output.

**What each folder means:**

```text
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

**About file permissions:**

All Liquibase Docker commands in this tutorial use the `--user $(id -u):$(id -g)` flag, which makes the container run as your user instead of root. This means:

- ✅ **Files and directories created by Liquibase will be owned by the user executing the dev container**
- ✅ No permission issues when editing or deleting files
- ✅ No need for `sudo chown` or `chmod 777`
- ✅ Matches production best practices

**How it works:**

```bash
--user $(id -u):$(id -g)  # Runs container as your current user ID and group ID
```

This is the recommended approach for running Docker containers that create files in mounted volumes.

## Step 1: Create Three Database Environments

Create three databases on the same SQL Server to represent dev, stage, and prod.

We've provided a SQL script that creates all three databases. Navigate to the tutorial scripts directory and run it:

```bash
# Create development, staging, and production databases
sqlcmd-tutorial create_databases.sql
```

**Verify all three databases exist:**

```bash
# Run the verification script
sqlcmd-tutorial verify_databases.sql
```

**Expected output:**

```text
name        database_id  create_date
----------- ------------ -----------------------
testdbdev   5            2025-11-14 20:00:00.000
testdbprd   7            2025-11-14 20:00:01.000
testdbstg   6            2025-11-14 20:00:00.500
```

**What did we just do?**

- Created three empty databases using `create_databases.sql`
- All on the same SQL Server instance (simulating separate environments)
- In real production, these would be on different servers/clouds
- Verified creation with `verify_databases.sql`

**Next: Create the app schema** (required before using Liquibase):

```bash
# Create app schema in all three databases
sqlcmd-tutorial create_app_schema.sql
```

**Verify schema exists in all three databases:**

```bash
# Expect to see three rows: dev/stage/prod with schema_name = app
sqlcmd-tutorial verify_app_schema.sql
```

**Expected output:**

```text
env    schema_name
-----  -----------
dev    app
stage  app
prod   app
```

**Troubleshooting:**

- If any row is missing, re-run `sqlcmd-tutorial create_app_schema.sql` and then `sqlcmd-tutorial verify_app_schema.sql`. Also verify `MSSQL_LIQUIBASE_TUTORIAL_PWD` is set.

**Why this step?** Liquibase does not manage schema creation. The `app` schema must exist before we can create tables and views within it. In production, schemas would be created through:

- Infrastructure-as-code (Terraform, ARM templates)
- Database initialization scripts
- Manual DBA processes

## Step 2: Populate Development with Existing Objects

Now create some database objects in **development only**. This simulates an existing database you want to start managing with Liquibase.

**Important**: The script assumes the `app` schema already exists (as Liquibase doesn't manage schemas). In production, schemas would be created through infrastructure scripts or database initialization.

We've provided a SQL script that creates objects in the development database:

```bash
# Create table, view, indexes, and sample data in DEVELOPMENT
# Note: Script assumes 'app' schema already exists
sqlcmd-tutorial populate_dev_database.sql
```

**Verify objects were created in development:**

```bash
# List all objects in app schema (development only)
sqlcmd-tutorial verify_dev_objects.sql

# Check sample data
sqlcmd-tutorial verify_dev_data.sql
```

**What did we just do?**

- Created a complete working database in development using `populate_dev_database.sql`
- Table `customer` with indexes and constraints, view `v_customer_basic` (in existing `app` schema)
- Added sample data (3 customer records)
- Verified with `verify_dev_objects.sql` and `verify_dev_data.sql`
- Staging and production are still empty (we'll deploy to them next)

**Note**: The `app` schema must exist before running Liquibase. In production, create schemas through infrastructure automation.

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
url=jdbc:sqlserver://mssql_liquibase_tutorial:1433;databaseName=testdbdev;encrypt=true;trustServerCertificate=true
username=sa
password=${MSSQL_LIQUIBASE_TUTORIAL_PWD}
changelog-file=database/changelog/changelog.xml
search-path=/workspace
logLevel=info
EOF

# Staging properties
cat > /data/liquibase-tutorial/env/liquibase.stage.properties << 'EOF'
# Staging Environment Connection
url=jdbc:sqlserver://mssql_liquibase_tutorial:1433;databaseName=testdbstg;encrypt=true;trustServerCertificate=true
username=sa
password=${MSSQL_LIQUIBASE_TUTORIAL_PWD}
changelog-file=database/changelog/changelog.xml
search-path=/workspace
logLevel=info
EOF

# Production properties
cat > /data/liquibase-tutorial/env/liquibase.prod.properties << 'EOF'
# Production Environment Connection
url=jdbc:sqlserver://mssql_liquibase_tutorial:1433;databaseName=testdbprd;encrypt=true;trustServerCertificate=true
username=sa
password=${MSSQL_LIQUIBASE_TUTORIAL_PWD}
changelog-file=database/changelog/changelog.xml
search-path=/workspace
logLevel=info
EOF

# Verify files were created
ls -la /data/liquibase-tutorial/env/
```

**What each property means:**

- `url`: JDBC connection string (notice `databaseName` differs per environment)
  - `jdbc:sqlserver://` - Protocol for SQL Server connections
  - `mssql_liquibase_tutorial:1433` - Server hostname (container name) and port (note: internally container uses 1433, but exposed as 14333 on host)
  - `databaseName=testdbdev` - Which database to connect to (this changes per environment)
  - `encrypt=true` - Use encrypted connection
  - `trustServerCertificate=true` - Trust the server's SSL certificate (for local dev only; in production use proper certificates)

- `username/password`: SQL Server credentials
  - `sa` = System Administrator (default SQL Server admin account)
  - `${MSSQL_LIQUIBASE_TUTORIAL_PWD}` - Environment variable containing the password (set in prerequisites)
  - **SECURITY NOTE**: In real production environments, NEVER use sa account! Create dedicated service accounts with minimal permissions.

- `changelog-file`: Master file that lists all changes
  - This is the "table of contents" for your database changes
  - Points to the XML file that includes all your changesets

- `search-path`: Where Liquibase looks for files inside Docker container
  - When we mount `/data/liquibase-tutorial` to `/workspace`, this tells Liquibase to look in `/workspace`

- `logLevel`: How much detail to show (info is good for learning)
  - `severe` - Only critical errors
  - `warning` - Warnings and errors
  - `info` - General information (recommended for learning)
  - `fine` - Detailed debugging information
  - `debug` - Very detailed debugging

**Security note**: This tutorial uses environment variables for the password, which is better than hardcoding. In production, use:

- **Secret management**: Azure Key Vault, AWS Secrets Manager, HashiCorp Vault
  - Centralized, encrypted storage for secrets
  - Automatic rotation of passwords
  - Audit logs of who accessed secrets

- **CI/CD platform secrets**: GitHub Secrets, GitLab CI/CD variables
  - Encrypted secrets stored in CI/CD platform
  - Automatically injected during pipeline execution
  - Never visible in logs or code

## Step 4: Generate Baseline from Development

Now use Liquibase to capture the current state of development as a **baseline**:

```bash
# Change to project directory
cd /data/liquibase-tutorial

# Generate baseline from development database (using lb wrapper)
# IMPORTANT: Use --schemas=app to capture only the app schema
# IMPORTANT: Use --include-schema=true to include schemaName attributes in the XML
lb -e dev -- \
  --changelog-file=/workspace/database/changelog/baseline/V0000__baseline.xml \
  --schemas=app \
  --include-schema=true \
  generateChangeLog

# Check the generated file (owned by your user, not root)
cat database/changelog/baseline/V0000__baseline.xml
```

### Quick checks

- schemaName: Verify all objects include `schemaName="app"`.

```bash
grep -n 'schemaName="app"' database/changelog/baseline/V0000__baseline.xml | head
```

- Objects captured: Spot tables, views, FKs, and indexes.

```bash
grep -nE '<createTable|<createView|<addForeignKeyConstraint|<createIndex' database/changelog/baseline/V0000__baseline.xml | head -n 20
```

- Sanity size check: Ensure it’s not trivially small.

```bash
wc -l database/changelog/baseline/V0000__baseline.xml
```

### If something looks off

- Regenerate the baseline with the exact flags (only `app` schema, include schema attributes):

```bash
lb -e dev -- \
  --changelog-file=/workspace/database/changelog/baseline/V0000__baseline.xml \
  --schemas=app \
  --include-schema=true \
  generateChangeLog
```

**What happened?**

- Liquibase connected to `testdbdev` database
- Scanned all database objects (tables, views, indexes, constraints, schemas)
- Generated XML file representing the current state
- Saved it as `V0000__baseline.xml` in the baseline folder
- **File is owned by the user executing the dev container** because we used `--user $(id -u):$(id -g)`

**What gets captured:**

- ✅ Tables and columns
- ✅ Primary keys and foreign keys
- ✅ Indexes
- ✅ Views (usually)
- ✅ Unique constraints
- ✅ Default values

**What to check in the generated baseline:**

1. **Schema attributes**: With `--include-schema=true`, all objects should have `schemaName="app"`
2. **Data types**: Verify column types match exactly (especially NVARCHAR vs VARCHAR)
3. **Constraints**: Check primary keys, foreign keys, unique constraints, and defaults
4. **Indexes**: Verify all indexes are captured correctly
5. **Ordering**: Ensure foreign key tables come after their referenced tables

**Note**: Schema creation is not captured (see Liquibase Limitations section above). Schemas must exist before running Liquibase.

## Step 5: Deploy Baseline Across Environments

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

Development already has these objects (we created them in Step 2), so we **sync** the baseline instead of deploying it. Syncing tells Liquibase "these changes already ran, don't execute them again."

**What is changelogSync?**

- **Regular update**: Executes SQL statements to create/modify database objects
- **changelogSync**: Records changes as executed WITHOUT running the SQL
- **When to use sync**: When the database already has the objects (like our dev database)
- **When to use update**: When the database is empty or missing objects (like our stage/prod databases)

**Think of it like checking items off a to-do list:**

- `update` = Do the task AND check it off
- `changelogSync` = Just check it off (task was already done)

```bash
cd /data/liquibase-tutorial

# Sync baseline to development (don't actually run DDL, just record as executed)
lb -e dev -- changelogSync

# Tag the baseline (create a named checkpoint for rollback purposes)
lb -e dev -- tag baseline
```

**What does tag do?**

- Creates a named marker in the change history
- Like bookmarking a page in a book
- Allows you to rollback to this specific point later
- Example: `liquibase rollback baseline` would undo all changes after this tag

**Why tag the baseline?**

- If future changes cause problems, you can rollback to the baseline
- Documents the "before Liquibase" state
- Useful for audit and compliance

**Verify sync worked:**

```bash
# Check DATABASECHANGELOG table
sqlcmd-tutorial -Q "
USE testdbdev;
SELECT ID, AUTHOR, FILENAME, DATEEXECUTED, TAG
FROM DATABASECHANGELOG
ORDER BY DATEEXECUTED;
"
```

### Deploy to Staging (Step 5: Baseline)

Staging is empty, so we **deploy** the baseline (actually run all DDL):

```bash
cd /data/liquibase-tutorial

# Preview what will run
lb -e stage -- updateSQL

# Deploy to staging
lb -e stage -- update

# Tag the baseline
lb -e stage -- tag baseline
```

**Verify deployment:**

```bash
# Check objects exist in staging
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

### Deploy to Production (Step 5: Baseline)

Production is also empty, so we deploy the baseline:

```bash
cd /data/liquibase-tutorial

# Preview what will run
lb -e prod -- updateSQL

# Deploy to production
lb -e prod -- update

# Tag the baseline
lb -e prod -- tag baseline
```

**Verify deployment:**

```bash
# Check objects exist in production
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

**What did we accomplish?**

✅ All three environments now have identical schemas
✅ Liquibase is tracking what ran where
✅ We can now deploy future changes safely

---

## Next Steps

Now that your baseline is in place and Liquibase is tracking changes across dev/stage/prod, choose your next path:

- **Recommended for new Liquibase users** – Continue with **Part 2: Manual Liquibase Deployment Lifecycle** (`sqlserver-liquibase-part2-manual-deploy.md`):
  - Learn how to add new changesets (V0001 and beyond).
  - Practice deploying changes manually through dev → stage → prod.
  - Experiment with tags, rollback, and drift detection before introducing automation.

- **If you already understand manual Liquibase workflows** – You can skip directly to
  **Part 3: From Local Liquibase Project to GitHub Actions CI/CD** (`sqlserver-liquibase-part3-github-actions.md`) to wire this same project into a GitHub Actions pipeline.

## Cleanup After Tutorial

When you've completed the tutorial series and want to clean up the containers and databases, you can use the cleanup helper script.

### Quick Cleanup (Recommended)

```bash
# Run the automated cleanup script
/path/to/your/repo/docs/tutorials/liquibase/scripts/cleanup_liquibase_tutorial.sh
```

**What the script does:**

- Stops and removes the `mssql_liquibase_tutorial` container
- Removes the `mssql_liquibase_tutorial_data` volume
- Removes the `liquibase_tutorial` Docker network
- Optionally removes the `/data/liquibase-tutorial` directory (with confirmation)
- Provides a summary of what was cleaned up

> You can run this script any time you want to **reset the tutorial environment** and start again from Part 1.

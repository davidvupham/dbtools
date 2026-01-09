# Tutorial Part 1: Baseline SQL Server + Liquibase Setup

<!-- markdownlint-disable MD013 -->

## Table of Contents

- [Introduction](#introduction)
  - [Goals of Part 1](#goals-of-part-1)
  - [What You'll Learn](#what-youll-learn)
  - [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
  - [Step 0: Configure Environment and Aliases](#step-0-configure-environment-and-aliases)
  - [Start the Tutorial SQL Server Container](#start-the-tutorial-sql-server-container)
  - [Build Liquibase container image](#build-liquibase-container-image)
- [Important Note About Container Commands](#important-note-about-container-commands)
  - [Check SQL Server is Running](#check-sql-server-is-running)
  - [Helper Script for sqlcmd](#helper-script-for-sqlcmd)
- [Project Structure](#project-structure)
- [Step 1: Create Three Database Environments](#step-1-create-three-database-environments)
- [Step 2: Populate Development with Existing Objects](#step-2-populate-development-with-existing-objects)
- [Step 3: Configure Liquibase for Each Environment](#step-3-configure-liquibase-for-each-environment)
- [Step 4: Generate Baseline from Development](#step-4-generate-baseline-from-development)
- [Step 5: Deploy Baseline Across Environments](#step-5-deploy-baseline-across-environments)
  - [Create Master Changelog](#create-master-changelog)
  - [Deploy to Development (Sync Only)](#deploy-to-development-sync-only)
  - [Deploy to Staging](#deploy-to-staging-step-5-baseline)
  - [Deploy to Production](#deploy-to-production-step-5-baseline)
- [Next Steps](#next-steps)
- [Cleanup After Tutorial](#cleanup-after-tutorial)

---

## Introduction

This tutorial is **Part 1** of a comprehensive series on implementing database change management with Liquibase and Microsoft SQL Server. Part 1 focuses on establishing a **baseline**—capturing the current state of an existing database and setting up Liquibase to manage future changes.

### Goals of Part 1

By the end of Part 1, you will have:

1. ✅ **Set up a complete Liquibase project structure** with proper organization for changelogs and environment configurations
2. ✅ **Created three database environments** (dev, stage, prod) to simulate a real-world multi-environment setup
3. ✅ **Generated a baseline** from an existing development database that represents your current production state
4. ✅ **Deployed the baseline** across all environments using Liquibase's sync and update commands
5. ✅ **Established Liquibase tracking** so all future changes can be safely managed and deployed

**The end result:** A fully configured Liquibase project that tracks your database schema across multiple environments, ready for incremental changes in Part 2.

### What You'll Learn

In this tutorial, you'll learn:

- **Liquibase fundamentals:**
  - What a baseline is and why it's critical for existing databases
  - How to generate a baseline from an existing database using `generateChangeLog`
  - The difference between `changelogSync` (marking changes as executed) and `update` (actually running changes)
  - How to organize changelogs in a maintainable structure

- **Multi-environment management:**
  - Setting up separate databases for dev, staging, and production
  - Configuring environment-specific Liquibase properties files
  - Deploying the same baseline to multiple environments safely

- **Best practices:**
  - Proper project structure for Liquibase changelogs
  - Using schema filtering to capture only relevant objects
  - Tagging deployments for rollback capabilities
  - Security considerations (environment variables, connection strings)

- **Docker workflow:**
  - Running Liquibase commands in Docker containers
  - Managing file permissions correctly
  - Using helper scripts and aliases for efficiency

- **Real-world scenarios:**
  - Baselining an existing database (common when adopting Liquibase)
  - Handling the "existing production database" use case
  - Setting up the foundation for incremental changes

### Prerequisites

Before starting this tutorial, you should have:

- ✅ **Docker or Podman** installed and running
  - Docker version 20.10+ recommended
  - Podman version 3.0+ (RedHat/CentOS)
  - Verify with: `docker --version` or `podman --version`

- ✅ **Bash shell** (Linux, macOS, or WSL2 on Windows)
  - Tutorial uses bash-specific syntax
  - Windows users: Use WSL2 or Git Bash

- ✅ **Basic SQL knowledge**
  - Understanding of databases, tables, schemas
  - Familiarity with SQL Server basics (helpful but not required)

- ✅ **Basic command line knowledge**
  - Navigating directories (`cd`, `ls`)
  - Running commands
  - Understanding file paths

**No prior Liquibase experience required!** This tutorial explains all concepts from the ground up.

---

## Environment Setup

### Step 0: Configure Environment and Aliases

First, set the `LIQUIBASE_TUTORIAL_DIR` environment variable to point to your repository's tutorial directory. This variable will be used throughout the tutorial.

```bash
# Set this to YOUR repository path (adjust as needed)
export LIQUIBASE_TUTORIAL_DIR="/path/to/your/repo/docs/courses/liquibase"

# Example for common locations:
# export LIQUIBASE_TUTORIAL_DIR="$HOME/src/dbtools/docs/courses/liquibase"
# export LIQUIBASE_TUTORIAL_DIR="/data/dbtools/docs/courses/liquibase"
```

**Shared Docker Host Setup:** Create your per-user project directory (one-time setup):

```bash
# Create /data/$USER directory (requires sudo)
sudo "$LIQUIBASE_TUTORIAL_DIR/scripts/setup_user_directory.sh"
```

Now source the setup script to configure aliases and properties:

```bash
# Source the setup helper (env, aliases, properties)
source "$LIQUIBASE_TUTORIAL_DIR/scripts/setup_tutorial.sh"
```

The setup script will:

- Set `LIQUIBASE_TUTORIAL_DATA_DIR` to `/data/$USER/liquibase_tutorial` (your per-user project directory)
- Create aliases: `sqlcmd-tutorial`, `lb`, `cr`
- Prompt for SQL Server password (`MSSQL_LIQUIBASE_TUTORIAL_PWD`)

### Start the Tutorial SQL Server Container

This tutorial uses a dedicated SQL Server container that can be safely removed after completion.

> **Note:** The `cr` command is a **Container Runtime** alias that auto-detects whether to use `docker` (Ubuntu/Debian) or `podman` (RHEL/Fedora) based on your operating system. It's defined in `setup_aliases.sh` and works the same as running docker/podman directly.

#### Build and start SQL Server container

```bash
# Navigate to the tutorial docker directory
cd "$LIQUIBASE_TUTORIAL_DIR/docker"

# Start the SQL Server container using the cr (container runtime) alias
# (cr auto-detects docker on Ubuntu/Debian, podman on RHEL/Fedora)
# Create data directory for SQL Server
mkdir -p "$LIQUIBASE_TUTORIAL_DATA_DIR/mssql1/mssql-data"

cr compose up -d 2>/dev/null || cr run -d --name mssql_liquibase_tutorial -h mssql1 -p 14333:1433 \
  -e ACCEPT_EULA=Y -e MSSQL_SA_PASSWORD="$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
  -e MSSQL_PID=Developer -v "$LIQUIBASE_TUTORIAL_DATA_DIR/mssql1/mssql-data":/var/opt/mssql:Z,U \
  mcr.microsoft.com/mssql/server:2025-latest

> **Note:** The `:Z,U` volume options are required for rootless Podman:
> - `:Z` - Relabels the volume for SELinux (private to this container)
> - `:U` - Recursively changes ownership to match the container user
> - Data is stored in `$LIQUIBASE_TUTORIAL_DATA_DIR/mssql-data` (e.g., `/data/$USER/liquibase_tutorial/mssql-data`)

# Verify it's running
cr ps | grep mssql_liquibase_tutorial
```

**Expected output:**

```text
mssql_liquibase_tutorial   mcr.microsoft.com/mssql/server:2025-latest   Up X seconds (healthy)   0.0.0.0:14333->1433/tcp
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
watch -n 2 "$LIQUIBASE_TUTORIAL_DIR/scripts/cr.sh ps | grep 'mssql_liquibase_tutorial'"
```

**Expected output (healthy):** Status shows "Up" and time keeps increasing:

```text
1fea5c21c7ae  mcr.microsoft.com/mssql/server:2025-latest  ...  Up About a minute  0.0.0.0:14333->1433/tcp  mssql_liquibase_tutorial
```

Or check the logs and filter for the ready message:

```bash
cr logs mssql_liquibase_tutorial 2>&1 | grep 'SQL Server is now ready for client connections'
```

#### Build Liquibase container image

The Liquibase container is a "run-once" tool (not a long-running service), so we just need to build the image:

```bash
# Navigate to the liquibase docker directory (from your repo root)
cd "${LIQUIBASE_TUTORIAL_DIR%/docs/courses/liquibase}/docker/liquibase"

# Build the custom Liquibase image with SQL Server drivers
cr build -t liquibase:latest .

# Verify the image was created
cr images | grep liquibase

# Quick sanity check: verify the Liquibase CLI runs
cr run --rm liquibase:latest --version
```

**Note:** The Liquibase container is not meant to stay running - it executes commands and exits. We'll use `docker run` (or `podman run` on RHEL) to execute Liquibase commands throughout this tutorial. The `lb` wrapper script auto-detects your container runtime.

Troubleshooting:

- If you see "Cannot find database driver: com.microsoft.sqlserver.jdbc.SQLServerDriver", rebuild the image from `docker/liquibase` and re-run the version check.
- If an alias like `lb` is not found in a new shell, re-source the aliases: `source "$LIQUIBASE_TUTORIAL_DIR/scripts/setup_aliases.sh"`.

### Important Note About Container Commands

The `lb` wrapper auto-detects your container runtime (Docker or Podman based on your OS) and encapsulates the full run invocation so you don't need to know paths or flags.

Heads-up: The commands below are examples to show wrapper usage. Do not run them yet. Run `lb` commands only after Step 1 (databases created) and after your properties point to those databases (created in Step 0 or Step 3). If you run them now, they will fail with connection/DB-not-found errors because the databases don’t exist yet; however, seeing Liquibase start and attempt a connection still confirms the Liquibase container image is built and accessible.

```bash
# Show status for dev
lb -e dev -- status --verbose

# Run update in staging
lb -e stg -- update
```

Note: The standalone `--` is intentional. It separates options for the `lb` wrapper (like `-e dev`) from the actual Liquibase command and its flags (for example, `status --verbose`).

Under the hood, `lb` runs Docker with the correct user, network, mounted project directory, and injects your `--defaults-file` and password.

If you prefer to run raw container commands yourself, mirror this pattern (note use of `LIQUIBASE_TUTORIAL_DATA_DIR` instead of hard-coded paths):

```bash
cr run --rm \
  -v "$LIQUIBASE_TUTORIAL_DATA_DIR":/data:Z,U \
  liquibase:latest \
  --defaults-file=/data/env/liquibase.<ENV>.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  <LIQUIBASE_COMMAND>
```

Notes:

- The password parameter must come after the defaults file but before the Liquibase command
- Use the dedicated Docker network `liquibase_tutorial`
- Run as your user (not root) to avoid permission issues

If you see connection errors, verify the correct network and password parameter order.

### Helper Script for sqlcmd

To simplify running SQL commands inside the tutorial SQL Server container, use the `sqlcmd-tutorial` helper (the alias is configured by `setup_aliases.sh`).

**Usage examples:**

> **Important:** The following commands are **examples only** demonstrating how to use the `sqlcmd-tutorial` alias. **Do not run them yet.** You will execute real versions later in the tutorial (database creation and verification occur in Step 1). Running them now is premature and may cause confusion.

- Run an inline query:

```bash
# EXAMPLE ONLY – DO NOT RUN YET
sqlcmd-tutorial -Q "SELECT @@SERVERNAME AS ServerName, GETDATE() AS CurrentTime;"
```

- Run a `.sql` file:

```bash
# EXAMPLE ONLY – DO NOT RUN YET
sqlcmd-tutorial create_databases.sql
```

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
mssql_dev                2026-01-07 18:35:07.160
```

**Troubleshooting:**

- **Connection refused**: SQL Server might not be running. Check with `cr ps | grep mssql_dev`
- **Login failed**: Password might be wrong. Check variable: `echo $MSSQL_LIQUIBASE_TUTORIAL_PWD`

## Project Structure

Create a clear directory structure for your Liquibase project:

> **Note:** On shared Docker hosts, the default project directory is `/data/$USER/liquibase_tutorial` (per-user isolation). The `setup_tutorial.sh` script sets `LIQUIBASE_TUTORIAL_DATA_DIR` for you. If you need to change it, export `LIQUIBASE_TUTORIAL_DATA_DIR` before running the setup script.

```bash
# Remove existing Liquibase directories if starting fresh (preserves mssql-data)
rm -rf "$LIQUIBASE_TUTORIAL_DATA_DIR/database" "$LIQUIBASE_TUTORIAL_DATA_DIR/env" 2>/dev/null

# Create project directory (uses /data/$USER by default)
mkdir -p "$LIQUIBASE_TUTORIAL_DATA_DIR"
cd "$LIQUIBASE_TUTORIAL_DATA_DIR"

# Create folder structure
mkdir -p database/changelog/baseline
mkdir -p database/changelog/changes
mkdir -p env
```

### Quick review: verify directories were created

```bash
ls -R "$LIQUIBASE_TUTORIAL_DATA_DIR/database"
```

You should see `database/changelog/baseline`, `database/changelog/changes`, and `env` in the output.

**What each folder means:**

```text
$LIQUIBASE_TUTORIAL_DATA_DIR/              # e.g., /data/$USER$/liquibase_tutorial
├── database/
│   └── changelog/
│       ├── changelog.xml           # Master file listing all changes in order
│       ├── baseline/               # Initial database snapshot
│       │   └── V0000__baseline.mssql.sql
│       └── changes/                # Incremental changes after baseline
│           ├── V0001__add_orders_table.sql
│           ├── V0002__modify_customer_email.sql
│           └── V0003__update_stored_procedure.sql
└── env/
    ├── liquibase.dev.properties    # Development database connection
    ├── liquibase.stg.properties  # Staging database connection
    └── liquibase.prd.properties   # Production database connection
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
orderdb   5            2025-11-14 20:00:00.000
orderdb   7            2025-11-14 20:00:01.000
orderdb   6            2025-11-14 20:00:00.500
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
cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/env/liquibase.dev.properties" << 'EOF'
# Development Environment Connection
url=jdbc:sqlserver://localhost:14333;databaseName=orderdb;encrypt=true;trustServerCertificate=true
username=sa
password=${MSSQL_LIQUIBASE_TUTORIAL_PWD}
changelog-file=database/changelog/changelog.xml
search-path=/data
logLevel=info
EOF

# Staging properties
cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/env/liquibase.stg.properties" << 'EOF'
# Staging Environment Connection
url=jdbc:sqlserver://localhost:14333;databaseName=orderdb;encrypt=true;trustServerCertificate=true
username=sa
password=${MSSQL_LIQUIBASE_TUTORIAL_PWD}
changelog-file=database/changelog/changelog.xml
search-path=/data
logLevel=info
EOF

# Production properties
cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/env/liquibase.prd.properties" << 'EOF'
# Production Environment Connection
url=jdbc:sqlserver://localhost:14333;databaseName=orderdb;encrypt=true;trustServerCertificate=true
username=sa
password=${MSSQL_LIQUIBASE_TUTORIAL_PWD}
changelog-file=database/changelog/changelog.xml
search-path=/data
logLevel=info
EOF

# Verify files were created
ls -la "$LIQUIBASE_TUTORIAL_DATA_DIR/env/"
```

**What each property means:**

- `url`: JDBC connection string (notice `databaseName` differs per environment)
  - `jdbc:sqlserver://` - Protocol for SQL Server connections
  - `localhost:14333` - Connect to host machine port 14333 (where container maps 1433).
  - **Note**: This requires running the Liquibase container with `--network host` (set via `LB_NETWORK=host`) so it can see `localhost` as the host machine.
  - `databaseName=orderdb` - Which database to connect to (this changes per environment)
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
  - When we mount `$LIQUIBASE_TUTORIAL_DATA_DIR` to `/data`, this tells Liquibase to look in `/data`

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
cd "$LIQUIBASE_TUTORIAL_DATA_DIR"

# Generate baseline from development database (using lb wrapper)
# IMPORTANT: Use --schemas=app to capture only the app schema
# IMPORTANT: Use --include-schema=true to include schemaName attributes in the SQL
# IMPORTANT: Use .sql extension to generate Formatted SQL
LB_NETWORK=host lb -e dev -- \
  --changelog-file=/data/database/changelog/baseline/V0000__baseline.mssql.sql \
  --schemas=app \
  --include-schema=true \
  generateChangeLog

# Check the generated file
cat database/changelog/baseline/V0000__baseline.mssql.sql
```

### Validate Generation

We have provided a script to automatically validate the baseline file format and content:

```bash
# Run validation script
$LIQUIBASE_TUTORIAL_DIR/scripts/validate_step4_baseline.sh
```

**Expected Output:**

```text
[PASS] File exists: V0000__baseline.mssql.sql
[PASS] Header matches '-- liquibase formatted sql'
[PASS] Found ... occurrences of 'app.' schema prefix
[PASS] Found CREATE TABLE app.customer
...
Step 4 VALIDATION SUCCESSFUL
```

### If something looks off

- Regenerate the baseline with the exact flags (only `app` schema, include schema attributes):

```bash
lb -e dev -- \
  --changelog-file=/data/database/changelog/baseline/V0000__baseline.mssql.sql \
  --schemas=app \
  --include-schema=true \
  generateChangeLog
```

**What happened?**

- Liquibase connected to `orderdb` database
- Scanned all database objects (tables, views, indexes, constraints, schemas)
- Generated Formatted SQL file representing the current state
- Saved it as `V0000__baseline.mssql.sql` in the baseline folder
- **File is owned by the user executing the dev container** because we used `--user $(id -u):$(id -g)`

**What gets captured:**

- ✅ Tables and columns
- ✅ Primary keys and foreign keys
- ✅ Indexes
- ✅ Views (usually)
- ✅ Unique constraints
- ✅ Default values

**What to check in the generated baseline:**

1. **Schema attributes**: With `--include-schema=true`, all objects should have `app.` prefix (e.g., `CREATE TABLE app.customer`)
2. **Data types**: Verify column types match exactly (especially NVARCHAR vs VARCHAR)
3. **Constraints**: Check primary keys, foreign keys, unique constraints, and defaults
4. **Indexes**: Verify all indexes are captured correctly
5. **Ordering**: Ensure foreign key tables come after their referenced tables

**Note**: Schema creation is not captured (see Liquibase Limitations section above). Schemas must exist before running Liquibase.

## Step 5: Deploy Baseline Across Environments

Now create the master changelog and deploy the baseline to each environment:

### Create Master Changelog

The "master changelog" (`changelog.xml`) is the single entry point Liquibase reads when you run commands like `update`, `status`, or `changelogSync`. Every environment properties file we created earlier (`changelog-file=database/changelog/changelog.xml`) points to this file, so it must exist before any deployment action.

Why not just point Liquibase directly at the baseline file? Because separating the baseline into its own file and including it from a master changelog lets you append future incremental changes (V0001, V0002, etc.) in a controlled, chronological order. The master changelog becomes your ordered "table of contents" of database evolution:

1. Include baseline (captured state of the existing DB)
2. Add new changeset files (e.g. `changes/V0001__add_orders_table.sql`)
3. Keep a stable root reference for CI/CD pipelines and tooling

Without this file, Liquibase would have no central place to aggregate future changes. Therefore creating it is required before deploying (syncing) the baseline across environments.

```bash
# Create master changelog that includes baseline
cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog/changelog.xml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <!-- Baseline: initial database state -->
    <include file="baseline/V0000__baseline.mssql.sql" relativeToChangelogFile="true"/>

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
cd "$LIQUIBASE_TUTORIAL_DATA_DIR"

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
USE orderdb;
SELECT ID, AUTHOR, FILENAME, DATEEXECUTED, TAG
FROM DATABASECHANGELOG
ORDER BY DATEEXECUTED;
"
```

### Deploy to Staging (Step 5: Baseline)

Staging is empty, so we **deploy** the baseline (actually run all DDL):

```bash
cd "$LIQUIBASE_TUTORIAL_DATA_DIR"

# Preview what will run
lb -e stg -- updateSQL

# Deploy to staging
lb -e stg -- update

# Tag the baseline
lb -e stg -- tag baseline
```

**Verify deployment:**

```bash
# Check objects exist in staging
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

### Deploy to Production (Step 5: Baseline)

Production is also empty, so we deploy the baseline:

```bash
cd "$LIQUIBASE_TUTORIAL_DATA_DIR"

# Preview what will run
lb -e prd -- updateSQL

# Deploy to production
lb -e prd -- update

# Tag the baseline
lb -e prd -- tag baseline
```

**Verify deployment:**

```bash
# Check objects exist in production
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

**What did we accomplish?**

✅ All three environments now have identical schemas
✅ Liquibase is tracking what ran where
✅ We can now deploy future changes safely

---

## Next Steps

Now that your baseline is in place and Liquibase is tracking changes across dev/stage/prod, choose your next path:

- **Recommended for new Liquibase users** – Continue with **Part 2: Manual Liquibase Deployment Lifecycle** (`series-part2-manual.md`):
  - Learn how to add new changesets (V0001 and beyond).
  - Practice deploying changes manually through dev → stage → prod.
  - Experiment with tags, rollback, and drift detection before introducing automation.

- **If you already understand manual Liquibase workflows** – You can skip directly to
  **Part 3: From Local Liquibase Project to GitHub Actions CI/CD** (`series-part3-cicd.md`) to wire this same project into a GitHub Actions pipeline.

## Cleanup After Tutorial

When you've completed the tutorial series and want to clean up the containers and databases, you can use the cleanup helper script.

### Quick Cleanup (Recommended)

```bash
# Run the automated cleanup script
"$LIQUIBASE_TUTORIAL_DIR/scripts/cleanup_liquibase_tutorial.sh"
```

**What the script does:**

- Stops and removes the `mssql_liquibase_tutorial` container
- Removes the `mssql_liquibase_tutorial_data` volume
- Removes the `liquibase_tutorial` Docker network
- Optionally removes the `$LIQUIBASE_TUTORIAL_DATA_DIR` directory (with confirmation)
- Provides a summary of what was cleaned up

> You can run this script any time you want to **reset the tutorial environment** and start again from Part 1.

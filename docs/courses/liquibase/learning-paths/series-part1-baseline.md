# Tutorial Part 1: Baseline SQL Server + Liquibase Setup

<!-- markdownlint-disable MD013 -->

## Table of Contents

- [Introduction](#introduction)
  - [Goals of Part 1](#goals-of-part-1)
  - [What You'll Learn](#what-youll-learn)
  - [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
  - [Step 0: Configure Environment and Aliases](#step-0-configure-environment-and-aliases)
  - [Before You Start: Clean Up Previous Runs](#before-you-start-clean-up-previous-runs)
  - [Start the Tutorial SQL Server Containers](#start-the-tutorial-sql-server-containers)
  - [Build Liquibase container image](#build-liquibase-container-image)
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
- [Appendix: Container Networking Details](#appendix-container-networking-details)
- [Appendix: File Permissions and User Mapping](#appendix-file-permissions-and-user-mapping)
- [Appendix: Direct SQL Server Container Commands](#appendix-direct-sql-server-container-commands)
- [Appendix: Direct Creation of Liquibase Properties Files](#appendix-direct-creation-of-liquibase-properties-files)
- [Appendix: Creating the `app` Schema with Liquibase](#appendix-creating-the-app-schema-with-liquibase)
- [Appendix: Step 2 Direct Commands (Populate Development)](#appendix-step-2-direct-commands-populate-development) — SQL commands for populating dev database
- [Appendix: Step 4 Direct Commands (Generate Baseline)](#appendix-step-4-direct-commands-generate-baseline-from-development) — `generateChangeLog` command reference
- [Appendix: Step 5 Direct Commands (Create Master Changelog)](#appendix-step-5-direct-commands-create-master-changelog) — Master changelog structure
- [Appendix: Step 5 Direct Commands (Deploy Baseline + Tag)](#appendix-step-5-direct-commands-deploy-baseline--tag) — `changelogSync`, `update`, `tag`, `snapshot` commands

---

## Introduction

This tutorial is **Part 1** of a comprehensive series on implementing database change management with Liquibase and Microsoft SQL Server. Part 1 focuses on establishing a **baseline**—capturing the current state of an existing database and setting up Liquibase to manage future changes.

### Goals of Part 1

By the end of Part 1, you will have:

1. ✅ **Set up a complete Liquibase project structure** with proper organization for changelogs and environment configurations
2. ✅ **Created three database environments** (dev, stage, prod) representing a real-world multi-environment setup
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

Set the `LIQUIBASE_TUTORIAL_DIR` environment variable to point to your repository's tutorial directory. This variable will be used throughout the tutorial.

**Option 1: Auto-detect (recommended)**

If you're inside the repository directory (or any subdirectory), use the helper script to automatically find and export the tutorial directory:

```bash
# From anywhere inside the dbtools repository:
source "$(git rev-parse --show-toplevel)/docs/courses/liquibase/scripts/find_tutorial_dir.sh"
```

The script searches for `docs/courses/liquibase` in:
- Current directory and parent directories
- Git repository root
- Common locations (`$HOME/src/dbtools`, `/data/dbtools`, etc.)

**Option 2: Manual export**

```bash
# Set this to YOUR repository path (adjust as needed)
export LIQUIBASE_TUTORIAL_DIR="/path/to/your/repo/docs/courses/liquibase"

# Example for common locations:
# export LIQUIBASE_TUTORIAL_DIR="$HOME/src/dbtools/docs/courses/liquibase"
# export LIQUIBASE_TUTORIAL_DIR="/data/dbtools/docs/courses/liquibase"
```

**Create Per-User Project Directory:** Create your per-user project directory (one-time setup):

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
- Create Liquibase properties files for dev, stg, and prd environments
- Prompt for SQL Server password (`MSSQL_LIQUIBASE_TUTORIAL_PWD`) if not already set

### Before You Start: Clean Up Previous Runs

**Important:** Before starting the tutorial, perform a complete cleanup to remove all containers, networks, and data from previous runs. This ensures you start with a completely fresh environment.

```bash
# Run complete cleanup script to remove all containers, networks, and data
"$LIQUIBASE_TUTORIAL_DIR/scripts/cleanup_tutorial.sh"
```

**What the cleanup script does:**
- Stops and removes all tutorial containers (`mssql_dev`, `mssql_stg`, `mssql_prd`, `liquibase_tutorial`)
- Removes Docker networks (`liquibase_tutorial_network`)
- **Removes the data directory** (`$LIQUIBASE_TUTORIAL_DATA_DIR`) - this deletes all databases, changelogs, configuration files, and volumes
- Provides a complete fresh start for the tutorial

The script will prompt for confirmation before removing the data directory to prevent accidental data loss.

> **Warning:** This cleanup will remove all tutorial data including databases and changelogs. Only run this if you want to start completely fresh from the beginning.

> **Note:** You can skip this step if you're certain the environment is clean, but it's recommended to run it to ensure a clean starting state.

### Start the Tutorial SQL Server Containers

This tutorial uses three dedicated SQL Server containers (one per environment) that can be safely removed after completion.

> **Note:** The `cr` command is a **Container Runtime** alias that auto-detects whether to use `docker` (Ubuntu/Debian) or `podman` (RHEL/Fedora) based on your operating system. It's defined in `setup_aliases.sh` and works the same as running docker/podman directly.

#### Build and start SQL Server containers

**Recommended: Use the step script**

```bash
# Run the automated step script
$LIQUIBASE_TUTORIAL_DIR/scripts/start_mssql_containers.sh
```

The script will:
- Start all three SQL Server containers (mssql_dev, mssql_stg, mssql_prd)
- Wait for health checks to pass
- Show container status
- Display success/fail indicators

For direct compose-based commands and port customization examples, see the appendix:
[Appendix: Direct SQL Server Container Commands](#appendix-direct-sql-server-container-commands)

#### Build Liquibase container image

The Liquibase container is a "run-once" tool (not a long-running service), so we just need to build the image:

```bash
# Navigate to the liquibase docker directory (from your repo root)
# This removes '/docs/courses/liquibase' from the path to get repo root, then goes to docker/liquibase
cd "${LIQUIBASE_TUTORIAL_DIR%/docs/courses/liquibase}/docker/liquibase"

# Build the custom Liquibase image with SQL Server drivers
cr build -t liquibase:latest .

# Verify the image was created
cr images | grep liquibase

# Quick sanity check: verify the Liquibase CLI runs
cr run --rm liquibase:latest --version
```

**Note:** The Liquibase container is not meant to stay running - it executes commands and exits. We'll use the `lb` wrapper script to run Liquibase commands throughout this tutorial. The wrapper automatically handles all container networking and configuration details for you.

> **Quick tip:** If an alias like `lb` is not found in a new shell, re-source the aliases: `source "$LIQUIBASE_TUTORIAL_DIR/scripts/setup_aliases.sh"`.
>
> For detailed information about how container networking works in this tutorial (including how the `lb` wrapper handles Docker vs Podman), see the [Appendix: Container Networking Details](#appendix-container-networking-details) at the end of this document.

### Helper Script for sqlcmd

To simplify running SQL commands inside the tutorial SQL Server container, use the `sqlcmd-tutorial` helper (the alias is configured by `setup_aliases.sh`).

**Usage examples:**

> **Important:** The following commands are **examples only** demonstrating how to use the `sqlcmd-tutorial` alias. **Do not run them yet.** You will execute real versions later in the tutorial (database creation and verification occur in Step 1). Running them now is premature and may cause confusion.

- Run an inline query:

```bash
# EXAMPLE ONLY – DO NOT RUN YET
# Note: Use -e dev/stg/prd to specify which SQL Server instance to connect to
sqlcmd-tutorial -e dev -Q "SELECT @@SERVERNAME AS ServerName, GETDATE() AS CurrentTime;"
```

- Run a `.sql` file:

```bash
# EXAMPLE ONLY – DO NOT RUN YET
sqlcmd-tutorial create_orderdb_database.sql
```

### Check SQL Server is Running

Now verify you can connect to all three SQL Server instances. This test ensures your databases are accessible before we start.

```bash
# Test connection to dev instance (should show server name and date)
sqlcmd-tutorial -e dev -Q "SELECT @@SERVERNAME AS ServerName, GETDATE() AS CurrentTime"

# Test connection to stg instance
sqlcmd-tutorial -e stg -Q "SELECT @@SERVERNAME AS ServerName, GETDATE() AS CurrentTime"

# Test connection to prd instance
sqlcmd-tutorial -e prd -Q "SELECT @@SERVERNAME AS ServerName, GETDATE() AS CurrentTime"
```

**Expected output:**

```text
ServerName               CurrentTime
------------------------ -----------------------
mssql_dev                2026-01-07 18:35:07.160

ServerName               CurrentTime
------------------------ -----------------------
mssql_stg                2026-01-07 18:35:08.245

ServerName               CurrentTime
------------------------ -----------------------
mssql_prd                2026-01-07 18:35:09.380
```

**Troubleshooting:**

- **Connection refused**: SQL Server might not be running. Check with `cr ps | grep mssql_`
- **Login failed**: Password might be wrong. Check variable: `echo $MSSQL_LIQUIBASE_TUTORIAL_PWD`

## Project Structure

Create a clear directory structure for your Liquibase project:

> **Note:** On shared Docker hosts, the default project directory is `/data/$USER/liquibase_tutorial` (per-user isolation). The `setup_tutorial.sh` script sets `LIQUIBASE_TUTORIAL_DATA_DIR` for you. If you need to change it, export `LIQUIBASE_TUTORIAL_DATA_DIR` before running the setup script.

Run the script to create the project structure:

```bash
"$LIQUIBASE_TUTORIAL_DIR/scripts/create_project_structure.sh"
```

The script will:
- Remove existing `platform` directory if starting fresh (preserves mssql-data)
- Create the project directory structure at `$LIQUIBASE_TUTORIAL_DATA_DIR`
- Create the required folders: `platform/mssql/database/orderdb/changelog/{baseline,changes}` and `platform/mssql/database/orderdb/env`

### Quick review: verify directories were created

```bash
ls -R "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb"
```

You should see `changelog/baseline`, `changelog/changes`, and `env` in the output.

**What each folder means:**

```text
$LIQUIBASE_TUTORIAL_DATA_DIR/              # e.g., /data/$USER/liquibase_tutorial
├── platform/
│   └── mssql/
│       └── database/
│           └── orderdb/
│               ├── changelog/
│               │   ├── changelog.xml           # Master file listing all changes in orderdb
│               │   ├── baseline/               # Initial database snapshot
│               │   │   └── V0000__baseline.mssql.sql
│               │   └── changes/                # Incremental changes after baseline
│               │       ├── V0001__add_orders_table.sql
│               │       ├── V0002__modify_customer_email.sql
│               │       └── V0003__update_stored_procedure.sql
│               └── env/
│                   ├── liquibase.mssql_dev.properties    # Connection to mssql_dev instance (development)
│                   ├── liquibase.mssql_stg.properties  # Connection to mssql_stg instance (staging)
│                   └── liquibase.mssql_prd.properties   # Connection to mssql_prd instance (production)
└── mssql_dev/, mssql_stg/, mssql_prd/ (SQL Server data volumes)
```

> **Note on file permissions:** All containers are configured to create files owned by your user. For details, see [Appendix: File Permissions and User Mapping](#appendix-file-permissions-and-user-mapping).

## Step 1: Create Three Database Environments

Create the `orderdb` database on each SQL Server container to represent dev, staging, and production environments.

**Recommended: Use the step script**

```bash
# Run the automated step script
$LIQUIBASE_TUTORIAL_DIR/scripts/create_orderdb_database.sh
```

The script will:
- Create `orderdb` on all three containers (mssql_dev, mssql_stg, mssql_prd)
- Create the `app` schema in each database (required for Liquibase)
- Show success/fail indicators for each container
- Display completion message

**Validate Step 1:**

```bash
# Run the validation script to verify databases and schemas were created
$LIQUIBASE_TUTORIAL_DIR/scripts/validate_orderdb_database.sh
```

The validation script checks:
- All three containers (mssql_dev, mssql_stg, mssql_prd) are running
- Each container has `orderdb` database
- Each `orderdb` has `app` schema

**What did we just do?**

- Created `orderdb` database on each SQL Server container (mssql_dev, mssql_stg, mssql_prd)
- Created the `app` schema in each database (required for Liquibase)
- Verified creation with `verify_orderdb_database.sql` and `verify_app_schema.sql`

## Step 2: Populate Development with Existing Objects

Now create some database objects in **development only**. This simulates an existing database you want to start managing with Liquibase.

```bash
# Run the automated step script
$LIQUIBASE_TUTORIAL_DIR/scripts/populate_dev_database.sh
```

The script will:
- Create `app.customer` table with indexes and constraints
- Create `app.v_customer_basic` view
- Insert sample data
- Show success/fail indicators

**Validate Step 2:**

```bash
# Run the validation script to verify objects were created
$LIQUIBASE_TUTORIAL_DIR/scripts/validate_dev_populate.sh
```

**Alternative: Direct commands**

See [Appendix: Step 2 Direct Commands (Populate Development)](#appendix-step-2-direct-commands-populate-development).

**What did we just do?**

- Created a complete working database in development using `populate_orderdb_database.sql`
- Table `customer` with indexes and constraints, view `v_customer_basic` (in existing `app` schema)
- Added sample data (3 customer records)
- Verified with `verify_orderdb_objects.sql` and `verify_orderdb_data.sql`
- Staging and production are still empty (we'll deploy to them next)

**Why only in dev?**

- This represents your "existing production database" scenario
- In real life, you'd generate baseline from production
- For this tutorial, we're using dev as our "existing" database

> **💡 Connecting to the Database**
>
> If you want to run queries manually to verify the database state:
>
> ```bash
> # Interactive SQL session to mssql_dev
> podman exec -it mssql_dev /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" -d orderdb
>
> # Or run a single query
> sqlcmd-tutorial -e dev -Q "SELECT * FROM app.customer;"
> ```
>
> In the interactive session, type `GO` after each query to execute, and `EXIT` to quit.


## Step 3: Configure Liquibase for Each Environment

Create properties files to connect Liquibase to each environment and set up the master changelog.

**Recommended: Properties files are created automatically**

If you ran `setup_tutorial.sh` in Step 0, the properties files were already created automatically. However, if you need to create them manually or want to understand the structure, you can use:

```bash
# Run the step script (creates directories, properties, and master changelog)
$LIQUIBASE_TUTORIAL_DIR/scripts/setup_liquibase_environment.sh
```

This script creates:
- Project directories (`platform/mssql/database/orderdb/changelog/baseline`, `platform/mssql/database/orderdb/changelog/changes`, `platform/mssql/database/orderdb/env/`)
- Properties files for dev, stg, prd
- Master `changelog.xml` file

**Validate Step 3:**

```bash
# Run the validation script to verify properties files
$LIQUIBASE_TUTORIAL_DIR/scripts/validate_liquibase_properties.sh
```

**Alternative: Direct creation**

See [Appendix: Direct Creation of Liquibase Properties Files](#appendix-direct-creation-of-liquibase-properties-files).

## Step 4: Generate Baseline from Development

Now use Liquibase to capture the current state of development as a **baseline**:

**Recommended: Use the step script**

```bash
# Run the automated step script
$LIQUIBASE_TUTORIAL_DIR/scripts/generate_liquibase_baseline.sh
```

The script will:
- Generate baseline from development database
- Use `--schemas=app` to capture only the app schema
- Use `--include-schema=true` to include schema names
- Save to `k`
- Show success/fail indicators
- Display preview of generated file

**Validate Step 4:**

```bash
# Run the validation script to verify baseline format and content
$LIQUIBASE_TUTORIAL_DIR/scripts/validate_liquibase_baseline.sh
```

**Alternative: Direct commands**

See [Appendix: Step 4 Direct Commands (Generate Baseline)](#appendix-step-4-direct-commands-generate-baseline-from-development).

**What happened?**

- Liquibase connected to `orderdb` database
- Scanned all database objects (tables, views, indexes, constraints, schemas)
- Generated Formatted SQL file representing the current state
- **Note:** Liquibase baselines typically do **not** generate `CREATE SCHEMA` statements (e.g., it won’t create `app`). Create schemas separately (as in Step 1) or add a dedicated changeset.
- Saved it as `V0000__baseline.mssql.sql` in the baseline folder
- File is owned by your user (no permission issues when editing)

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

**Note**: When using `generateChangeLog` to create a baseline from an existing database, Liquibase does not capture schema creation statements. The generated changelog will include objects within schemas, but not the `CREATE SCHEMA` statements themselves. If you need to create schemas via Liquibase, add a dedicated changeset (see [Appendix: Creating the `app` Schema with Liquibase](#appendix-creating-the-app-schema-with-liquibase)).

## Step 5: Deploy Baseline Across Environments

Now deploy the baseline to each environment. The master changelog (`changelog.xml`) should already exist if you ran `setup_tutorial.sh` or `setup_liquibase_environment.sh`. If not, create it first (see [Appendix: Step 5 Direct Commands (Create Master Changelog)](#appendix-step-5-direct-commands-create-master-changelog)).

```bash
$LIQUIBASE_TUTORIAL_DIR/scripts/deploy.sh --action baseline

# Optional: deploy to one or more SQL Server environments (comma-separated)
# (defaults to dev,stg,prd when omitted)
$LIQUIBASE_TUTORIAL_DIR/scripts/deploy.sh --action baseline --env dev,stg
```

The script will:
- Deploy baseline to selected environments (default: dev, stg, prd)
- For `dev`, use `changelogSync` (marks as executed without running)
- For `stg`/`prd`, use `update` (actually executes SQL)
- Tag all environments with `baseline`
  - A tag is a named marker in the change history (stored in `DATABASECHANGELOG`)
  - Useful for rollback targets later (example: `liquibase rollback baseline` rolls back changes after the tag)
- **Take a snapshot** of each environment after successful deployment (for drift detection)
- Show success/fail indicators for each environment

**Important (baseline / golden / master instance):**
If a database instance is considered the "baseline" (it already contains the objects), you **must run `changelogSync`** there so Liquibase records the baseline changesets in `DATABASECHANGELOG` **without re-running the SQL**. If you skip this and later run `update` against that database instance, Liquibase will try to execute the baseline DDL and typically fail with "object already exists" errors (or leave your changelog state out of sync).

**Validate Step 5:**

```bash
# Run the validation script to verify deployment across all environments
# Note: Ensure deploy.sh --action baseline completed successfully first
$LIQUIBASE_TUTORIAL_DIR/scripts/validate_liquibase_deploy.sh
```

**What the script does:**

- **Development**: Uses `changelogSync` because objects already exist (we created them in Step 2)
  - Records changes as executed WITHOUT running the SQL
  - Think of it as "checking items off a to-do list" without doing the work

- **Staging & Production**: Uses `update` because databases are empty
  - Actually executes the SQL statements to create objects
  - Think of it as "doing the task AND checking it off"

> If you need to create the master `changelog.xml` directly, see [Appendix: Step 5 Direct Commands (Create Master Changelog)](#appendix-step-5-direct-commands-create-master-changelog).

### Deploy to Development (Sync Only)

Development already has these objects (we created them in Step 2), so we **sync** the baseline instead of deploying it. Syncing tells Liquibase "these changes already ran, don't execute them again."

**What is changelogSync?**

- **Regular update**: Executes SQL statements to create/modify database objects
- **changelogSync**: Records changes as executed WITHOUT running the SQL
- **When to use sync**: When the database already has the objects (like our dev database)
- **When to use update**: When the database is empty or missing objects (like our stage/prod databases)

> Prefer the direct CLI approach? See [Appendix: Step 5 Direct Commands (Deploy Baseline + Tag)](#appendix-step-5-direct-commands-deploy-baseline--tag).

**What did we accomplish?**

✅ All three environments now have identical schemas
✅ Liquibase is tracking what ran where (DATABASECHANGELOG table in each environment)
✅ Baseline tagged in all environments for rollback capability
✅ We can now deploy future changes safely

---

## Quick Reference: Step Scripts Summary

For convenience, here's a summary of all step scripts used in Part 1:

| Step | Script | Purpose | Validation |
|------|--------|---------|------------|
| [0](#step-0-configure-environment-and-aliases) / [3](#step-3-configure-liquibase-for-each-environment) | `setup_liquibase_environment.sh` | Create directories, properties, changelog. **Note:** In [Step 0](#step-0-configure-environment-and-aliases), `setup_tutorial.sh` automatically creates properties files. In [Step 3](#step-3-configure-liquibase-for-each-environment), `setup_liquibase_environment.sh` is the manual option to create properties and master changelog if needed. | `validate_liquibase_properties.sh` |
| - | `start_mssql_containers.sh` | Start SQL Server containers | Manual check |
| [1](#step-1-create-three-database-environments) | `create_orderdb_database.sh` | Create orderdb on all containers | `validate_orderdb_database.sh` |
| [2](#step-2-populate-development-with-existing-objects) | `populate_dev_database.sh` | Populate dev with sample objects | `validate_dev_populate.sh` |
| [4](#step-4-generate-baseline-from-development) | `generate_liquibase_baseline.sh` | Generate baseline from dev | `validate_liquibase_baseline.sh` |
| [5](#step-5-deploy-baseline-across-environments) | `deploy.sh --action baseline` | Deploy baseline to all environments + snapshot | `validate_liquibase_deploy.sh` |

All scripts show success/fail indicators and provide clear next steps.

---

## Next Steps

Now that your baseline is in place and Liquibase is tracking changes across dev/stage/prod, choose your next path:

- **Recommended for new Liquibase users** – Continue with [**Part 2: Manual Liquibase Deployment Lifecycle**](series-part2-manual.md):
  - Learn how to add new changesets (V0001 and beyond).
  - Practice deploying changes manually through dev → stage → prod.
  - Experiment with tags, rollback, and drift detection before introducing automation.

- **If you already understand manual Liquibase workflows** – You can skip directly to
  [**Part 3: From Local Liquibase Project to GitHub Actions CI/CD**](series-part3-cicd.md) to wire this same project into a GitHub Actions pipeline.

## Cleanup After Tutorial

**Always clean up after completing the tutorial** to free up resources and ensure a clean state for future runs.

### Quick Cleanup (Recommended)

```bash
# Run the automated cleanup script
"$LIQUIBASE_TUTORIAL_DIR/scripts/cleanup_validation.sh"
```

**What the cleanup script does:**

- Stops and removes the SQL Server containers (`mssql_dev`, `mssql_stg`, `mssql_prd`)
- Removes any Liquibase containers
- Removes associated Docker networks
- Waits for ports to be released
- Optionally removes validation log files (with confirmation)
- Provides a summary of what was cleaned up

**Alternative: Full cleanup (removes data directory)**

If you want to completely remove all tutorial data (including databases and changelogs):

```bash
# Run the full cleanup script
"$LIQUIBASE_TUTORIAL_DIR/scripts/cleanup_tutorial.sh"
```

This script also:
- Removes the `$LIQUIBASE_TUTORIAL_DATA_DIR` directory (with confirmation)
- Removes all data volumes

> **Important:**
> - Run cleanup **after completing** the tutorial to free up resources
> - Run cleanup **before starting** a new tutorial run to ensure a clean environment
> - You can run cleanup scripts any time you want to **reset the tutorial environment** and start again from Part 1

---

## Appendix: Container Networking Details

Back to: [Build Liquibase container image](#build-liquibase-container-image)

This section explains how container networking works in this tutorial for readers who want to understand the technical details or need to troubleshoot connection issues.

### Architecture Overview

The tutorial uses a multi-container setup:

- **SQL Server containers** (`mssql_dev`, `mssql_stg`, `mssql_prd`): Three separate containers that expose ports to the host machine (14331, 14332, 14333 respectively)
- **Liquibase container**: A separate "run-once" container that executes Liquibase commands and exits

Since the SQL Server containers expose ports to the **host machine**, the Liquibase container needs to connect through the host's network to reach these ports.

### How the `lb` Wrapper Works

The `lb` wrapper script auto-detects your container runtime (Docker or Podman based on your OS) and handles all networking configuration automatically:

- **Docker**: Uses `--network host` with `localhost` (allows container to access host ports 14331/14332/14333 directly)
- **Podman**: Uses `--network slirp4netns` with `host.containers.internal` (special hostname that resolves to the host)

The wrapper dynamically generates the correct JDBC URL and network configuration, so the properties file `localhost` value is effectively replaced at runtime.

### Properties File vs Runtime Configuration

The properties files use `localhost` in the JDBC connection string for reference:

```properties
url=jdbc:sqlserver://localhost:14331;databaseName=orderdb;encrypt=true;trustServerCertificate=true
```

However, the `lb` wrapper overrides this at runtime by passing a `--url` parameter that uses the correct hostname for your container runtime. This means you don't need to worry about the networking details - just use the `lb` wrapper as shown in the tutorial.

### Example: Using the `lb` Wrapper

The standalone `--` in `lb` commands is intentional. It separates options for the `lb` wrapper from the actual Liquibase command:

```bash
# Show status for dev
lb -e dev -- status --verbose

# Run update in staging
lb -e stg -- update
```

In these examples:
- `-e dev` is an option for the `lb` wrapper (specifies the environment)
- `--` separates wrapper options from Liquibase commands
- `status --verbose` and `update` are the actual Liquibase commands

Under the hood, `lb` runs the container with the correct user, network, mounted project directory, and injects your `--defaults-file` and password.

### Running Raw Container Commands (Advanced)

If you prefer to run raw container commands yourself (for debugging or customization), you need to match the network configuration:

**For Docker:**

```bash
cr run --rm \
  --user "$(id -u):$(id -g)" \
  --network host \
  -v "$LIQUIBASE_TUTORIAL_DATA_DIR":/data:Z,U \
  liquibase:latest \
  --defaults-file=/data/platform/mssql/database/orderdb/env/liquibase.mssql_<ENV>.properties \
  --url="jdbc:sqlserver://localhost:<PORT>;databaseName=orderdb;encrypt=true;trustServerCertificate=true" \
  --username=sa \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  <LIQUIBASE_COMMAND>
```

**For Podman:**

```bash
cr run --rm \
  --user "$(id -u):$(id -g)" \
  --network slirp4netns:port_handler=slirp4netns \
  -v "$LIQUIBASE_TUTORIAL_DATA_DIR":/data:z,U \
  liquibase:latest \
  --defaults-file=/data/platform/mssql/database/orderdb/env/liquibase.mssql_<ENV>.properties \
  --url="jdbc:sqlserver://host.containers.internal:<PORT>;databaseName=orderdb;encrypt=true;trustServerCertificate=true" \
  --username=sa \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  <LIQUIBASE_COMMAND>
```

**Important points:**

- Replace `<PORT>` with 14331 (dev), 14332 (stg), or 14333 (prd) depending on environment
- Replace `<ENV>` with dev, stg, or prd
- The password parameter must come after the defaults file but before the Liquibase command
- The `--url` parameter overrides the URL in the properties file
- Run as your user (`--user $(id -u):$(id -g)`) to avoid permission issues

### Troubleshooting Connection Issues

If you see connection errors when using the `lb` wrapper:

1. Verify the SQL Server containers are running: `cr ps | grep mssql_`
2. Check that containers show as healthy: look for `(healthy)` status
3. Verify the correct network configuration is being used (the wrapper handles this automatically)
4. Verify the password is set: `echo $MSSQL_LIQUIBASE_TUTORIAL_PWD`

If running raw container commands, also verify:

- Network mode matches your container runtime (host for Docker, slirp4netns for Podman)
- Hostname in JDBC URL matches the network mode (`localhost` for host network, `host.containers.internal` for slirp4netns)
- Port numbers match the environment (14331/14332/14333)

### Setting SQL Server Instance Names

SQL Server containers are automatically configured with server names that match their container names (`mssql_dev`, `mssql_stg`, `mssql_prd`). This is done by setting the container hostname when the containers are created:

- **Docker Compose**: The `docker-compose.yml` file sets `hostname: mssql_dev/stg/prd` for each service
- **Podman/Docker run**: The `start_mssql_containers.sh` script uses the `--hostname` flag when creating containers

SQL Server on Linux uses the container's hostname as its `@@SERVERNAME` when it first starts, so the server name is set automatically without requiring any manual configuration.

**Verifying the server name:**

```bash
# Check server name for each environment
for env in dev stg prd; do
    echo "=== mssql_${env} ==="
    sqlcmd-tutorial -e "$env" -Q "SELECT @@SERVERNAME AS ServerName" -h -1 -W
done
```

**Expected output:** Each should show `mssql_dev`, `mssql_stg`, or `mssql_prd` respectively (not container IDs).

**Note:** If you have existing containers that were created before this fix, they may still show container IDs. To fix them, you'll need to recreate the containers (your data will persist in the volumes). Stop and remove the containers, then run `start_mssql_containers.sh` again to create them with the correct hostnames.

---

## Appendix: File Permissions and User Mapping

Back to: [Project Structure](#project-structure)

This tutorial uses different user mapping approaches for different containers to ensure files created in mounted volumes are owned by your user, avoiding permission issues.

### Liquibase Containers

Liquibase containers use the `--user $(id -u):$(id -g)` flag to run as your user instead of root:

- Files and directories created by Liquibase are owned by your user
- No permission issues when editing or deleting files
- No need for `sudo chown` or `chmod 777`
- Matches production best practices

```bash
--user $(id -u):$(id -g)  # Runs container as your current user ID and group ID
```

This flag is applied automatically by the `lb` wrapper script when running Liquibase commands.

### MSSQL Containers

MSSQL containers use the `--userns=keep-id` flag with rootless Podman (applied automatically in `start_mssql_containers.sh`):

- Ensures container UIDs map to your host user's UID namespace
- Files created by SQL Server (running as `mssql` user, UID 10001 inside the container) are owned by your user on the host
- Works seamlessly with rootless Podman (the recommended way to run Podman)
- The `:U` volume flag ensures proper ownership changes

```bash
--userns=keep-id  # Maps container UIDs to host user's UID namespace (Podman only)
```

**Note:** When using Docker, the `--userns=keep-id` flag is not needed as Docker handles user namespaces differently. The MSSQL containers will still create files with correct ownership when using Docker.

### Why Different Approaches?

SQL Server requires running as a specific user (`mssql`, UID 10001) inside the container, so we can't use `--user` to override it. Instead, we use `--userns=keep-id` to map container UIDs to your host user's namespace. Liquibase, on the other hand, can run as any user, so we use `--user` to run it directly as your user.

---

## Appendix: Direct SQL Server Container Commands

Back to: [Start the Tutorial SQL Server Containers](#start-the-tutorial-sql-server-containers)

**Alternative: Direct commands**

> **Important:** These direct commands use **default ports** (14331, 14332, 14333). If these ports are already in use, docker-compose will fail with port conflicts. For multi-user environments or when ports may be in use, first run `setup_db_container_ports.sh` to configure available ports.

```bash
# Option 1: Use default ports (14331, 14332, 14333)
# Navigate to the tutorial docker directory
cd "$LIQUIBASE_TUTORIAL_DIR/docker"
cr compose up -d mssql_dev mssql_stg mssql_prd

# Option 2: Setup dynamic ports first (recommended for multi-user environments)
# Run the port setup script to configure available ports and save them to .ports file
$LIQUIBASE_TUTORIAL_DIR/scripts/setup_db_container_ports.sh

# Source the .ports file to use the configured ports
if [[ -f "$LIQUIBASE_TUTORIAL_DATA_DIR/.ports" ]]; then
    source "$LIQUIBASE_TUTORIAL_DATA_DIR/.ports"
    export MSSQL_DEV_PORT MSSQL_STG_PORT MSSQL_PRD_PORT
fi

# Navigate to the tutorial docker directory and start containers
cd "$LIQUIBASE_TUTORIAL_DIR/docker"
cr compose up -d mssql_dev mssql_stg mssql_prd

# Option 3: Use ports from a previous run (if .ports file already exists)
# Source the existing .ports file
if [[ -f "$LIQUIBASE_TUTORIAL_DATA_DIR/.ports" ]]; then
    source "$LIQUIBASE_TUTORIAL_DATA_DIR/.ports"
    export MSSQL_DEV_PORT MSSQL_STG_PORT MSSQL_PRD_PORT
fi
cd "$LIQUIBASE_TUTORIAL_DIR/docker"
cr compose up -d mssql_dev mssql_stg mssql_prd

# Verify containers are running
cr ps | grep mssql_
```

> **Note:** The docker-compose.yml uses `:Z,U` volume options for rootless Podman compatibility:
> - `:Z` - Relabels the volume for SELinux (private to this container)
> - `:U` - Recursively changes ownership to match the container user
> - Data is stored in `$LIQUIBASE_TUTORIAL_DATA_DIR/mssql_dev/`, `mssql_stg/`, `mssql_prd/`
> - Ports can be customized by:
>   - Running `setup_db_container_ports.sh` to configure available ports (recommended)
>   - Setting `MSSQL_DEV_PORT`, `MSSQL_STG_PORT`, `MSSQL_PRD_PORT` environment variables before running docker-compose
>   - Sourcing an existing `.ports` file from a previous run

**Expected output:**

```text
mssql_dev   mssql_tutorial:latest   Up X seconds (healthy)   0.0.0.0:14331->1433/tcp
mssql_stg   mssql_tutorial:latest   Up X seconds (healthy)   0.0.0.0:14332->1433/tcp
mssql_prd   mssql_tutorial:latest   Up X seconds (healthy)   0.0.0.0:14333->1433/tcp
```

**What this does:**

- Builds/downloads SQL Server 2025 image (if not already available)
- Creates three containers: `mssql_dev`, `mssql_stg`, `mssql_prd`
- Starts SQL Server on ports 14331, 14332, 14333 respectively
- Uses the password from `$MSSQL_LIQUIBASE_TUTORIAL_PWD`
- Includes health checks to verify SQL Server is ready

**Wait for SQL Server to be ready:**

Each container has a built-in health check. You can poll for the `(healthy)` status:

```bash
# Watch the container status until all show (healthy) (Ctrl+C to exit)
watch -n 2 '"$LIQUIBASE_TUTORIAL_DIR/scripts/cr.sh" ps | grep mssql_'
```

**Expected output (healthy):** Status shows "Up" and all containers are healthy:

```text
mssql_dev  ...  Up About a minute (healthy)  0.0.0.0:14331->1433/tcp
mssql_stg  ...  Up About a minute (healthy)  0.0.0.0:14332->1433/tcp
mssql_prd  ...  Up About a minute (healthy)  0.0.0.0:14333->1433/tcp
```

Or check the logs and filter for the ready message:

```bash
cr logs mssql_dev 2>&1 | grep 'SQL Server is now ready for client connections'
```

### Step 1: Direct database and schema commands

Back to: [Step 1: Create Three Database Environments](#step-1-create-three-database-environments)

**Alternative: Direct commands**

To create databases and schemas directly for all three environments:

```bash
# Create orderdb database on each environment
sqlcmd-tutorial -e dev create_orderdb_database.sql
sqlcmd-tutorial -e stg create_orderdb_database.sql
sqlcmd-tutorial -e prd create_orderdb_database.sql

# Create app schema in each orderdb (required for Liquibase)
sqlcmd-tutorial -e dev -d orderdb create_app_schema.sql
sqlcmd-tutorial -e stg -d orderdb create_app_schema.sql
sqlcmd-tutorial -e prd -d orderdb create_app_schema.sql

# Verify orderdb exists on each environment
sqlcmd-tutorial -e dev verify_orderdb_database.sql
sqlcmd-tutorial -e stg verify_orderdb_database.sql
sqlcmd-tutorial -e prd verify_orderdb_database.sql

# Verify app schema exists in each orderdb
sqlcmd-tutorial -e dev -d orderdb verify_app_schema.sql
sqlcmd-tutorial -e stg -d orderdb verify_app_schema.sql
sqlcmd-tutorial -e prd -d orderdb verify_app_schema.sql
```

Or use a loop to run for all environments:

```bash
# Create databases and schemas for all environments
for env in dev stg prd; do
    sqlcmd-tutorial -e "$env" create_orderdb_database.sql
    sqlcmd-tutorial -e "$env" -d orderdb create_app_schema.sql
    sqlcmd-tutorial -e "$env" verify_orderdb_database.sql
    sqlcmd-tutorial -e "$env" -d orderdb verify_app_schema.sql
done
```

**Expected output:**

For database verification:
```text
instance_name      name        database_id  create_date
------------------ ----------- ------------ -----------------------
mssql_dev          orderdb     5            2025-11-14 20:00:00.000
```

For schema verification:
```text
instance_name      database_name  schema_name
------------------ -------------- -----------
mssql_dev          orderdb        app
```

## Appendix: Direct Creation of Liquibase Properties Files

Back to: [Step 3: Configure Liquibase for Each Environment](#step-3-configure-liquibase-for-each-environment)

If you prefer to create properties files manually:

```bash
# Development properties
cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/env/liquibase.mssql_dev.properties" << 'EOF'
# Development Environment Connection
url=jdbc:sqlserver://localhost:14331;databaseName=orderdb;encrypt=true;trustServerCertificate=true
username=sa
changelog-file=changelog/changelog.xml
search-path=/data/platform/mssql/database/orderdb
logLevel=info
EOF

# Staging properties
cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/env/liquibase.mssql_stg.properties" << 'EOF'
# Staging Environment Connection
url=jdbc:sqlserver://localhost:14332;databaseName=orderdb;encrypt=true;trustServerCertificate=true
username=sa
changelog-file=changelog/changelog.xml
search-path=/data/platform/mssql/database/orderdb
logLevel=info
EOF

# Production properties
cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/env/liquibase.mssql_prd.properties" << 'EOF'
# Production Environment Connection
url=jdbc:sqlserver://localhost:14333;databaseName=orderdb;encrypt=true;trustServerCertificate=true
username=sa
changelog-file=changelog/changelog.xml
search-path=/data/platform/mssql/database/orderdb
logLevel=info
EOF

# Verify files were created
ls -la "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/env/"
```

**What each property means:**

- `url`: JDBC connection string (notice port differs per environment)
  - `jdbc:sqlserver://` - Protocol for SQL Server connections
  - `localhost:14331/14332/14333` - Connect to host machine ports (dev=14331, stg=14332, prd=14333)
  - `databaseName=orderdb` - Database name (same for all environments)
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

## Appendix: Creating the `app` Schema with Liquibase

Back to: [Step 4: Generate Baseline from Development](#step-4-generate-baseline-from-development)

If you want Liquibase to create the `app` schema (instead of creating it manually in Step 1), add a small schema-creation changeset **and include it before the baseline**.

### Example: Formatted SQL changeset

Create a new file (example path/name):

```text
platform/mssql/database/orderdb/changelog/baseline/V0000a__create_app_schema.mssql.sql
```

Example contents:

```sql
-- liquibase formatted sql
-- changeset tutorial:create-app-schema
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'app')
    EXEC('CREATE SCHEMA app');
```

### Include order (important)

In your master `changelog.xml`, include the schema file **before** the generated baseline file:

```xml
<!-- Ensure schema exists before baseline creates objects in it -->
<include file="baseline/V0000a__create_app_schema.mssql.sql" relativeToChangelogFile="true"/>
<include file="baseline/V0000__baseline.mssql.sql" relativeToChangelogFile="true"/>
```

## Appendix: Step 2 Direct Commands (Populate Development)

Back to: [Step 2: Populate Development with Existing Objects](#step-2-populate-development-with-existing-objects)

This appendix shows the direct commands that `populate_dev_database.sh` executes. Step 2 uses SQL commands (not Liquibase) to populate the development database with existing objects.

### What the Helper Script Does

The `populate_dev_database.sh` script executes SQL scripts to create database objects in development. Here are the equivalent direct commands:

```bash
# Create table, view, indexes, and sample data in DEVELOPMENT
# Note: Script assumes 'app' schema already exists
sqlcmd-tutorial -e dev populate_orderdb_database.sql

# Verify objects were created in development
sqlcmd-tutorial -e dev verify_orderdb_objects.sql
sqlcmd-tutorial -e dev verify_orderdb_data.sql
```

### Understanding the Commands

| Command | Purpose |
|---------|---------|
| `sqlcmd-tutorial -e dev` | Connect to the development SQL Server container (`mssql_dev`) |
| `populate_orderdb_database.sql` | SQL script that creates `app.customer` table, indexes, view, and sample data |
| `verify_orderdb_objects.sql` | SQL script that verifies database objects exist |
| `verify_orderdb_data.sql` | SQL script that verifies sample data was inserted |

**Note:** This step does not use Liquibase commands. The purpose is to simulate an existing database that you want to start managing with Liquibase.

## Appendix: Step 4 Direct Commands (Generate Baseline from Development)

Back to: [Step 4: Generate Baseline from Development](#step-4-generate-baseline-from-development)

This appendix shows the direct Liquibase commands that `generate_liquibase_baseline.sh` executes. Understanding these commands helps you customize baseline generation for your specific needs.

### What the Helper Script Does

The `generate_liquibase_baseline.sh` script runs the Liquibase `generateChangeLog` command to capture the current database state.

### Direct Liquibase Command

```bash
# Change to project directory
cd "$LIQUIBASE_TUTORIAL_DATA_DIR"

# Generate baseline from development database
lb -e dev -- \
  --changelog-file=/data/platform/mssql/database/orderdb/changelog/baseline/V0000__baseline.mssql.sql \
  --schemas=app \
  --include-schema=true \
  generateChangeLog
```

### Command Breakdown

| Component | Description |
|-----------|-------------|
| `lb -e dev --` | Run Liquibase against the development environment. The `--` separates `lb` wrapper options from Liquibase options. |
| `generateChangeLog` | **Liquibase command** that reverse-engineers the database and creates a changelog file representing its current state. |

### Parameter Reference

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `--changelog-file` | `/data/.../V0000__baseline.mssql.sql` | Output file path. The `.sql` extension generates **Formatted SQL** format (human-readable SQL with Liquibase metadata comments). |
| `--schemas` | `app` | **Schema filter** - only capture objects in the `app` schema. Without this, Liquibase captures ALL schemas including system schemas (`dbo`, `sys`, etc.). |
| `--include-schema` | `true` | Include schema names in generated SQL (e.g., `CREATE TABLE app.customer` instead of `CREATE TABLE customer`). Essential for multi-schema databases. |
| `--overwrite-output-file` | `true` | (Optional) Replace existing baseline file if regenerating. Only needed when re-running the command. |

### Understanding the Output Format

The `generateChangeLog` command produces a **Formatted SQL** file (because of the `.sql` extension) with this structure:

```sql
-- liquibase formatted sql

-- changeset liquibase:1234567890-1
CREATE TABLE app.customer (
    customer_id INT NOT NULL,
    name NVARCHAR(100) NOT NULL,
    ...
);

-- changeset liquibase:1234567890-2
CREATE INDEX IX_customer_email ON app.customer(email);
```

Each `-- changeset` comment marks a trackable unit of change that Liquibase records in `DATABASECHANGELOG`.

### Alternative Output Formats

| Extension | Format | Use Case |
|-----------|--------|----------|
| `.sql` | Formatted SQL | Human-readable, easy to review and edit |
| `.xml` | XML changelog | Full Liquibase XML with explicit change types |
| `.yaml` | YAML changelog | More readable than XML, less verbose |
| `.json` | JSON changelog | Machine-readable, good for automation |

### Verify the Generated File

```bash
# Check the generated file exists and has content
cat platform/mssql/database/orderdb/changelog/baseline/V0000__baseline.mssql.sql

# Or use the validation script
$LIQUIBASE_TUTORIAL_DIR/scripts/validate_liquibase_baseline.sh
```

### Regenerating the Baseline

If you need to regenerate the baseline (e.g., after adding more objects to dev):

```bash
lb -e dev -- \
  --changelog-file=/data/platform/mssql/database/orderdb/changelog/baseline/V0000__baseline.mssql.sql \
  --schemas=app \
  --include-schema=true \
  --overwrite-output-file=true \
  generateChangeLog
```

**Important:** Add `--overwrite-output-file=true` when the baseline file already exists.

## Appendix: Step 5 Direct Commands (Create Master Changelog)

Back to: [Step 5: Deploy Baseline Across Environments](#step-5-deploy-baseline-across-environments)

This appendix shows how to create the master changelog file manually. The master changelog is the "table of contents" that tells Liquibase which changesets to apply and in what order.

### What the Helper Script Does

The `setup_liquibase_environment.sh` script creates the master `changelog.xml` file. Here's the equivalent direct command:

```bash
# Create master changelog that includes baseline
cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changelog.xml" << 'EOF'
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

### Understanding the Master Changelog

| Element | Purpose |
|---------|---------|
| `<databaseChangeLog>` | Root element that contains all changelog includes |
| `<include file="...">` | Includes another changelog file. Liquibase processes includes in order. |
| `relativeToChangelogFile="true"` | File paths are relative to this changelog's location (not the working directory) |

**Note:** This step creates a file structure—it does not run any Liquibase commands. The actual Liquibase commands are in the next section (Deploy Baseline + Tag).

## Appendix: Step 5 Direct Commands (Deploy Baseline + Tag)

Back to: [Step 5: Deploy Baseline Across Environments](#step-5-deploy-baseline-across-environments)

This appendix shows the direct Liquibase commands that `deploy.sh --action baseline` executes. Understanding these commands is essential for customizing deployments and troubleshooting.

### What the Helper Script Does

The `deploy.sh --action baseline` script runs different Liquibase commands depending on the environment:

- **Development**: `changelogSync` (objects already exist)
- **Staging/Production**: `update` (objects need to be created)
- **All environments**: `tag` and `snapshot` after deployment

### Liquibase Commands Reference

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `changelogSync` | Mark changesets as executed **without running SQL** | Database already has the objects (baseline scenario) |
| `updateSQL` | **Preview** the SQL that would be executed | Always run before `update` to verify changes |
| `update` | **Execute** changesets to create/modify database objects | Database is empty or missing objects |
| `tag <name>` | Create a named marker in change history | After each deployment for rollback capability |
| `snapshot` | Capture current database state for drift detection | After each deployment to enable comparisons |

### Direct Commands for Development (Sync Only)

Development already has the objects (created in Step 2), so we **sync** instead of **update**:

```bash
cd "$LIQUIBASE_TUTORIAL_DATA_DIR"

# Mark baseline as executed WITHOUT running the SQL
lb -e dev -- changelogSync

# Create a rollback marker named "baseline"
lb -e dev -- tag baseline
```

#### changelogSync Command Breakdown

```bash
lb -e dev -- changelogSync
```

| Component | Description |
|-----------|-------------|
| `lb -e dev --` | Run Liquibase against development environment |
| `changelogSync` | **Liquibase command** that records all pending changesets as executed in `DATABASECHANGELOG` without running them |

**Use Case:** When the database already contains the objects defined in your changelog (e.g., baselining an existing database).

### Direct Commands for Staging/Production (Update)

Staging and production are empty, so we **update** to actually execute the SQL:

```bash
cd "$LIQUIBASE_TUTORIAL_DATA_DIR"

# Staging: Preview first, then execute
lb -e stg -- updateSQL  # Preview the SQL
lb -e stg -- update     # Execute the SQL
lb -e stg -- tag baseline

# Production: Preview first, then execute
lb -e prd -- updateSQL  # Preview the SQL
lb -e prd -- update     # Execute the SQL
lb -e prd -- tag baseline
```

#### updateSQL Command Breakdown

```bash
lb -e stg -- updateSQL
```

| Component | Description |
|-----------|-------------|
| `lb -e stg --` | Run Liquibase against staging environment |
| `updateSQL` | **Liquibase command** that outputs the SQL that `update` would execute, without actually running it |

**Use Case:** Always preview changes before executing to catch potential issues.

#### update Command Breakdown

```bash
lb -e stg -- update
```

| Component | Description |
|-----------|-------------|
| `lb -e stg --` | Run Liquibase against staging environment |
| `update` | **Liquibase command** that executes all pending changesets and records them in `DATABASECHANGELOG` |

**Use Case:** Apply database changes to an environment.

#### tag Command Breakdown

```bash
lb -e stg -- tag baseline
```

| Component | Description |
|-----------|-------------|
| `lb -e stg --` | Run Liquibase against staging environment |
| `tag baseline` | **Liquibase command** that creates a named marker called "baseline" in `DATABASECHANGELOG` |

**Use Case:** Create rollback points. You can later run `lb -e stg -- rollback baseline` to undo all changes after this tag.

### Direct Commands for Snapshots (Drift Detection)

After deployment, take snapshots for drift detection:

```bash
# Create snapshots directory if it doesn't exist
mkdir -p "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/snapshots"

# Take snapshot of each environment
lb -e dev -- snapshot --schemas=app --snapshot-format=json \
  --output-file=/data/platform/mssql/database/orderdb/snapshots/dev_baseline_$(date +%Y%m%d_%H%M%S).json

lb -e stg -- snapshot --schemas=app --snapshot-format=json \
  --output-file=/data/platform/mssql/database/orderdb/snapshots/stg_baseline_$(date +%Y%m%d_%H%M%S).json

lb -e prd -- snapshot --schemas=app --snapshot-format=json \
  --output-file=/data/platform/mssql/database/orderdb/snapshots/prd_baseline_$(date +%Y%m%d_%H%M%S).json
```

#### snapshot Command Breakdown

```bash
lb -e dev -- snapshot --schemas=app --snapshot-format=json --output-file=/data/.../snapshot.json
```

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `snapshot` | (command) | **Liquibase command** that captures the current database structure |
| `--schemas` | `app` | Only capture objects in the `app` schema |
| `--snapshot-format` | `json` | Output format (also supports `yaml`, `txt`) |
| `--output-file` | `/data/.../snapshot.json` | Where to save the snapshot |

**Use Case:** Snapshots enable drift detection—comparing the actual database state against expected state to find unauthorized changes.

### Why Tag the Baseline?

- **Rollback capability**: If future changes cause problems, run `lb -e <env> -- rollback baseline` to undo all changes after this tag
- **Documentation**: Marks the "before Liquibase" state clearly
- **Audit trail**: Provides a clear point-in-time reference for compliance

### Verify Deployment Worked

```bash
# Check DATABASECHANGELOG table in any environment
sqlcmd-tutorial -e dev -Q "
USE orderdb;
SELECT ID, AUTHOR, FILENAME, DATEEXECUTED, TAG, EXECTYPE
FROM DATABASECHANGELOG
ORDER BY DATEEXECUTED;
"
```

**Expected output:** You should see the baseline changeset(s) with `EXECTYPE` showing `EXECUTED` (for stg/prd) or `MARK_RAN` (for dev, from `changelogSync`).

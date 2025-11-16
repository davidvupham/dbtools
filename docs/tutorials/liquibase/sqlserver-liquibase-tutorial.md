# Beginner's Tutorial: Database Change Management with Liquibase and SQL Server

## Introduction

This tutorial teaches you **database change management** from the ground up using Liquibase and Microsoft SQL Server. You'll learn what CI/CD means for databases, why it matters, and how to safely deploy schema changes across multiple environments.

**No prior knowledge required!** This guide is designed for developers who may be familiar with databases but new to:

- Database change management tools (like Liquibase)
- CI/CD (Continuous Integration/Continuous Deployment) practices
- DevOps workflows for databases
- Automated deployment pipelines

**What you'll learn:**

- Core concepts: CI/CD, change management, environment promotion (all explained in plain language)
- How to track and version database changes with Liquibase (like Git, but for your database)
- Safe deployment patterns: dev → stage → prod (test first, deploy carefully)
- Baselining existing databases and managing incremental changes
- Real-world workflows with tables, views, indexes, and constraints

**What you'll build:**

A complete Liquibase project that manages a customer database across three environments (dev, stage, prod) running on the same SQL Server instance. By the end, you'll have a working system that safely tracks and deploys database changes automatically.

**Important**: This tutorial uses **Liquibase Community edition** (free, open-source version). See the [Liquibase Implementation Guide](../../architecture/liquibase-implementation-guide.md#liquibase-community-edition) for details on Community Edition capabilities and [Liquibase Limitations](../../architecture/liquibase-implementation-guide.md#liquibase-limitations) that apply to all editions.

This tutorial focuses exclusively on objects supported by the Community edition: tables, views, indexes, and constraints - the foundation of any database schema.

## Tutorial-Specific Considerationssiderations

**For this tutorial**: We assume the `app` schema already exists in all environments (created in Step 1). See the [Liquibase Limitations documentation](../../architecture/liquibase-implementation-guide.md#liquibase-limitations) for details on why schemas must be created outside of Liquibase.

## Table of Contents

- [Glossary of Terms](#glossary-of-terms)
- [Understanding CI/CD for Databases](#understanding-cicd-for-databases)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Project Structure](#project-structure)
- [Step 1: Create Three Database Environments](#step-1-create-three-database-environments)
- [Step 2: Populate Development with Existing Objects](#step-2-populate-development-with-existing-objects)
- [Step 3: Configure Liquibase for Each Environment](#step-3-configure-liquibase-for-each-environment)
- [Step 4: Generate Baseline from Development](#step-4-generate-baseline-from-development)
- [Step 5: Deploy Baseline Across Environments](#step-5-deploy-baseline-across-environments)
- [Step 6: Making Your First Change](#step-6-making-your-first-change)
- [Step 7: Deploy Change Across Environments](#step-7-deploy-change-across-environments)
- [Step 8: More Database Changes](#step-8-more-database-changes)
- [Step 9: Rollbacks and Tags](#step-9-rollbacks-and-tags)
- [Step 10: Detecting Database Drift](#step-10-detecting-database-drift)
- [Step 11: Generating Changelogs from Differences](#step-11-generating-changelogs-from-differences)
- [Understanding the Deployment Pipeline](#understanding-the-deployment-pipeline)
- [Common Troubleshooting](#common-troubleshooting)
- [Best Practices](#best-practices)
- [Next Steps](#next-steps)

## Glossary of Terms

**New to databases, DevOps, or CI/CD?** This glossary explains all the technical terms you'll encounter in this tutorial.

### What is Liquibase?

**Liquibase** is an open-source database change management tool. Think of it as **"version control for databases"** - like Git, but for your database schema instead of code files.

**The problem Liquibase solves:**

Without Liquibase, database changes are chaotic:

- Developer creates SQL script: `add-loyalty-column.sql`
- Emails it to team or saves on shared drive
- Someone manually runs it in dev... or do they? Hard to tell
- Another person runs it in staging (maybe)
- DBA runs it in production (hopefully the same script!)
- Six months later: "Did we add that column to production? I can't remember!"

**With Liquibase:**

- Changes are tracked in files, committed to Git
- Each environment has a log of exactly what ran
- Can't accidentally run the same change twice
- Can rollback if something breaks
- Complete audit trail of who changed what and when

**Simple analogy**:

- **Without Liquibase**: Like moving houses by randomly packing boxes and hoping you remember what went where
- **With Liquibase**: Like using a detailed inventory list that tracks every item, which box it's in, and where it goes in the new house

**How it works in 30 seconds:**

1. You write a database change in a "changeset" (SQL or YAML file)
2. Add it to a "changelog" (master list of all changes)
3. Run `liquibase update`
4. Liquibase:
   - Checks what changes already ran (stored in DATABASECHANGELOG table)
   - Runs only new changes
   - Records what it did
5. Repeat for each environment (dev, stage, prod)

**What makes Liquibase special:**

- **Database-agnostic**: Works with SQL Server, PostgreSQL, MySQL, Oracle, and 30+ other databases
- **Safe**: Prevents running changes twice, validates checksums, supports rollbacks
- **Auditable**: Complete history of every change in DATABASECHANGELOG table
- **Flexible**: Write changes in SQL, XML, YAML, or JSON format
- **Free**: Open-source with enterprise support available

### Database Terms

- **Schema**: A container/namespace for database objects like tables, views, procedures. Think of it as a folder organizing related database objects. Example: `app.customer` means the `customer` table in the `app` schema.

- **DDL (Data Definition Language)**: SQL commands that define database structure (CREATE TABLE, ALTER TABLE, DROP TABLE, CREATE VIEW, etc.). These change the schema, not the data.

- **DML (Data Manipulation Language)**: SQL commands that work with data (INSERT, UPDATE, DELETE, SELECT). These change the data, not the schema.

- **Stored Procedure**: Pre-written SQL code stored in the database that you can call repeatedly. Like a function in programming. *Note: This tutorial focuses on objects supported by Liquibase Community Edition and does not use stored procedures.*

- **Function**: A database object that returns a value and can be used in SELECT statements. *Note: This tutorial focuses on objects supported by Liquibase Community Edition and does not use functions.*

- **View**: A saved query that looks like a table. Doesn't store data itself, just retrieves it. Useful for simplifying complex queries or hiding sensitive columns.

- **Index**: A data structure that speeds up queries, like an index in a book. Without it, the database scans every row. With it, lookups are fast.

- **Foreign Key**: A link between two tables. Ensures data consistency. Example: `orders.customer_id` references `customer.customer_id` (you can't create an order for a non-existent customer).

- **Primary Key**: Unique identifier for each row in a table. Like a Social Security Number - each person has exactly one, and no two people share the same one.

- **Constraint**: A rule enforced by the database (e.g., "email cannot be null", "customer_id must be unique", "order_total must be positive").

### Liquibase Terms

- **Liquibase**: An open-source tool for database change management. Tracks what changes have been applied to which databases.

- **Changeset**: A single database change (add table, modify column, create view). The fundamental unit of change in Liquibase. Each changeset has a unique ID.

- **Changelog**: An XML, YAML, or SQL file that lists changesets in order. Like a recipe - step 1, step 2, step 3.

- **Master Changelog**: The main changelog file that includes other changelog files. Acts as a table of contents.

- **Baseline**: A snapshot of your database's existing structure when you start using Liquibase. Represents "everything that exists before we started tracking changes."

- **DATABASECHANGELOG**: A table Liquibase creates to track which changesets have been executed. Like a logbook recording what changes ran when.

- **DATABASECHANGELOGLOCK**: A table Liquibase uses to prevent multiple deployments from running simultaneously. Prevents conflicts.

- **Checksum**: A calculated hash of a changeset's content. If the content changes, the checksum changes. Liquibase uses this to detect if someone modified an already-deployed changeset.

- **Tag**: A named marker in the changelog history. Like a bookmark. Allows you to rollback to specific points. Example: tag `release-v1.0` marks your first production release.

- **Rollback**: Undo changes by running reverse SQL. Example: if you created a table, rollback drops it.

- **Precondition**: A check that runs before a changeset executes. Example: "only create this index if it doesn't already exist."

- **Context**: A label that controls when a changeset runs. Example: changesets with `context:dev` only run in development, not production.

### CI/CD Terms

- **CI (Continuous Integration)**: Automatically testing changes when code is committed. Catches bugs early.

- **CD (Continuous Deployment)**: Automatically deploying code changes through environments to production after tests pass.

- **Pipeline**: An automated sequence of steps (build, test, deploy). Changes flow through the pipeline like an assembly line.

- **Environment**: A separate instance of your application/database. Common environments: dev (development), test, stage (staging), prod (production).

- **Deployment**: The process of applying changes to an environment. Moving code/database changes from version control to a running system.

- **Rollback**: Reversing a deployment to a previous version. Like an "undo" button for production changes.

- **Promotion**: Moving a change from one environment to the next (dev → stage → prod). Only promote after testing succeeds.

- **Idempotent**: A change that can be run multiple times safely with the same result. Example: "CREATE TABLE IF NOT EXISTS" is idempotent; "CREATE TABLE" (without IF NOT EXISTS) is not.

### Docker Terms

- **Docker**: A platform for running applications in isolated containers. Packages software with all its dependencies.

- **Container**: A lightweight, isolated environment for running applications. Like a virtual machine but faster and smaller.

- **Image**: A template for creating containers. Like a blueprint or a snapshot you can spin up multiple times.

- **Volume Mount**: Sharing a folder between your computer and a Docker container. Changes in one appear in the other. Example: `-v /data/liquibase-tutorial:/workspace`

- **Network**: How Docker containers communicate. `--network=host` makes the container use your computer's network (easier for local dev).

### DevOps Terms

- **Version Control**: Tracking changes to files over time (usually with Git). Like "track changes" in Word, but much more powerful.

- **Git**: A version control system. Tracks who changed what and when. Enables collaboration and rollback.

- **Commit**: Saving your changes to version control with a message describing what you changed.

- **Repository (Repo)**: A collection of files tracked by version control. Contains your code, database changes, documentation, etc.

- **Pull Request (PR)**: A request to merge your changes into the main codebase. Team reviews your changes before accepting.

- **Branch**: A parallel version of your code. Like a sandbox where you can experiment without affecting the main codebase.

- **Secrets Management**: Securely storing sensitive information (passwords, API keys). Never put passwords in code!

- **Audit Trail**: A complete history of what changed, when, and who changed it. Essential for compliance and debugging.

### Miscellaneous Terms

- **JDBC (Java Database Connectivity)**: The Java standard for connecting to databases. Liquibase uses JDBC to talk to SQL Server, PostgreSQL, Oracle, etc.

- **CLI (Command Line Interface)**: Text-based way to interact with software (opposite of GUI - Graphical User Interface). Example: `liquibase update`

- **SA (System Administrator)**: The default admin account in SQL Server. Has full permissions. Don't use in production (security risk).

- **SSL/TLS Certificate**: Encryption certificate for secure connections. `trustServerCertificate=true` skips certificate validation (OK for local dev, not for production).

- **Port**: A network endpoint for connections. SQL Server's default port is 1433. Like apartment numbers - the server is the building, the port is the specific apartment.

**Pro tip**: Bookmark this glossary! Refer back to it whenever you encounter an unfamiliar term.

### What is CI/CD?

**CI/CD** stands for **Continuous Integration** and **Continuous Deployment**. These are software development practices that help teams deliver changes faster and more safely.

**Breaking it down:**

- **Continuous Integration (CI)**: Automatically testing and validating changes when developers commit code
  - Think of it as an automatic quality checker
  - Every time you make a change, automated tests verify it works
  - Catches problems early, before they reach production

- **Continuous Deployment (CD)**: Automatically deploying validated changes through environments to production
  - Once changes pass tests, they move through environments automatically
  - Reduces manual errors and speeds up releases
  - Ensures consistent deployment process every time

**Simple analogy**: Imagine baking bread in a factory. CI is like the quality inspector checking each batch of dough before baking. CD is the automated conveyor belt that moves good batches through the oven, cooling, and packaging stages. Without automation, someone might accidentally skip a step or use the wrong temperature.

### Why does it matter for databases?

**The old way (manual database changes):**

Imagine you need to add a new column to a table. Without CI/CD, you might:

1. Write SQL script in a text file
2. Email it to someone or save on shared drive
3. Manually connect to database
4. Copy-paste the SQL and run it
5. Hope you ran it on the right environment
6. Try to remember if you already ran it in staging
7. Forget to run it in production (production breaks!)

**Problems with manual approach:**

- **Manual**: Someone runs SQL scripts by hand (error-prone, time-consuming)
- **Inconsistent**: Different process each time, easy to make mistakes
- **Untraceable**: Hard to know what ran where and when ("Did we add that column to production?")
- **Risky**: Production failures from untested changes or wrong scripts
- **No rollback**: If something breaks, hard to undo changes
- **Team confusion**: Multiple people making changes without coordination

**The new way (with CI/CD for databases):**

With Liquibase and CI/CD, the same scenario becomes:

1. Write SQL change in a version-controlled file
2. Commit to Git (version control system)
3. Automated pipeline runs the change in dev first
4. Tests verify it works
5. Change automatically deploys to staging
6. After approval, automatically deploys to production
7. Complete history of what ran where

**Benefits with CI/CD for databases:**

- **Version control**: Every change is tracked in Git (like tracking document history in Google Docs)
- **Repeatability**: Same change deploys identically across all environments (no "it works on my machine" problems)
- **Safety**: Test in dev and stage before production (catch issues early)
- **Auditability**: Complete history of what changed, when, and who made the change
- **Rollback capability**: Undo changes if problems occur (like "undo" button for databases)
- **Team collaboration**: Everyone sees the same changes, no surprises
- **Automation**: Less manual work, fewer mistakes

### What is Environment Promotion?

**Environment promotion** means deploying changes through a series of environments in order, testing at each stage before moving forward.

**The standard path:**

```
Development (dev) → Staging (stage) → Production (prod)
```

**Why this order? Think of it like testing a new recipe:**

1. **Development (testdbdev)**: Your kitchen at home where you experiment
   - Break things here, it's okay! This is your learning space
   - Rapid iteration and experimentation
   - May have test/sample data (fake customers, test orders)
   - If you mess up, only you are affected
   - **Example**: You're testing if adding a new "loyalty_points" column works correctly

2. **Staging (testdbstg)**: A practice kitchen identical to the restaurant
   - Same structure as production (simulates real environment)
   - Test the exact deployment process you'll use in production
   - Catch integration issues before prod (does it work with real-world data volumes?)
   - Last chance to find problems
   - **Example**: You verify the loyalty_points column works with realistic customer data and doesn't slow down queries

3. **Production (testdbprd)**: The actual restaurant serving real customers
   - Only deploy after dev and stage succeed
   - Minimize risk, maximize stability
   - Apply the exact same changes that worked in stage
   - Real users, real data, no room for error
   - **Example**: Your actual customers now have loyalty_points tracking their purchases

**Why not skip to production?**

- **Risk**: No testing means high chance of breaking production
- **No safety net**: If it fails, real users are affected immediately
- **Debugging nightmare**: Hard to diagnose issues under pressure
- **Rollback complexity**: Harder to safely undo changes

**The golden rule**: If it doesn't work in dev, don't promote it. If it doesn't work in stage, definitely don't deploy to production!

### What is a Baseline?

A **baseline** is a snapshot of your database's current state when you start using Liquibase. It's your starting point for tracking changes.

**Why do you need it?**

Most real-world scenarios involve existing databases:

- You have existing tables, views, indexes, and constraints already in production
- These objects were created before you started using Liquibase
- Liquibase needs to know "this is the starting point" so it can track "everything from now on"
- Without a baseline, Liquibase would try to create objects that already exist (causing errors)

**Analogy**: Think of it like joining a book club midway through the year:

- The baseline is like getting a summary of "all books discussed so far this year"
- Now you can track "all books discussed from this point forward"
- Without the baseline, you might try to discuss a book the club already finished

**Real example:**

Your production database already has:

- `customer` table (created 2 years ago)
- `orders` table (created 1 year ago)
- `v_customer_orders` view (created 6 months ago)
- Various indexes and constraints (created over time)

When you start using Liquibase:

1. **Generate baseline**: Liquibase scans production, creates a snapshot of all these objects
2. **Mark as executed**: Tells Liquibase "I know these exist, don't try to recreate them"
3. **Future changes**: From now on, Liquibase tracks new changes (new tables, modifications, etc.)

**Without a baseline:**

- Liquibase tries to create `customer` table → Error! Table already exists
- Deployment fails, production breaks
- Team panics

**With a baseline:**

- Liquibase knows these objects exist
- Only applies new changes
- Smooth deployment

## Prerequisites

**Required:**

- Docker installed (to run SQL Server and Liquibase)
- Environment variable `MSSQL_LIQUIBASE_TUTORIAL_PWD` set with SQL Server SA password (use a password WITHOUT exclamation marks to avoid shell issues)

**What we'll use:**

- Dedicated SQL Server container for this tutorial (accessible at `localhost:14333`)
  - **Container name**: `mssql_liquibase_tutorial`
  - **Port**: 14333 (different from default 1433 to avoid conflicts with other SQL Server instances)
  - **Why dedicated?** This tutorial uses a separate SQL Server instance that can be safely removed after completion
- Docker to run Liquibase commands
  - **What's Docker?** A tool that packages software in "containers" - think of it as a lightweight virtual machine that runs programs in isolation
- Three databases on the same server: `testdbdev`, `testdbstg`, `testdbprd`
  - **Why three on same server?** For this tutorial, we simulate three separate environments on one server to keep it simple. In real production, these would be on separate servers/cloud instances

**No need to install:**

- Java (Docker handles it)
  - **Why Java?** Liquibase is written in Java, but you don't need to install Java because the Docker container includes it
- Liquibase CLI (Docker handles it)
  - **What's CLI?** Command Line Interface - the text-based way to run Liquibase commands
- JDBC drivers (included in Liquibase Docker image)
  - **What's JDBC?** Java Database Connectivity - the driver that lets Java programs (like Liquibase) talk to SQL Server

### Set Up Environment Variable

**IMPORTANT**: Before starting, set the SQL Server SA password as an environment variable.

```bash
# Set the SQL Server SA password (required for tutorial)
# IMPORTANT: Use a password WITHOUT exclamation marks (!) to avoid shell interpolation issues
export MSSQL_LIQUIBASE_TUTORIAL_PWD='YourStrong@Passw0rd'

# Verify it's set
echo $MSSQL_LIQUIBASE_TUTORIAL_PWD
```

**Password requirements:**

- At least 8 characters
- Contains uppercase and lowercase letters
- Contains numbers
- Contains special characters (avoid exclamation marks for shell compatibility)

**Why use an environment variable?**

- Keeps passwords out of command history
- Makes it easy to change the password in one place
- Better security practice than hardcoding passwords

**Verify prerequisites:**

```bash
# Verify Docker is installed
docker --version
```

**Expected output:**

```
Docker version 229.x.x
```

## Environment Setup

### Step 0: Start the Tutorial SQL Server Container

This tutorial uses a dedicated SQL Server container that can be safely removed after completion.

#### Build and start SQL Server container

```bash
# Navigate to the tutorial docker directory
cd /workspaces/dbtools/docs/tutorials/liquibase/docker

# Start the SQL Server container
docker compose up -d

# Verify it's running
docker ps | grep mssql_liquibase_tutorial
```

**Expected output:**

```
mssql_liquibase_tutorial   mcr.microsoft.com/mssql/server:2022-latest   Up X seconds (healthy)   0.0.0.0:14333->1433/tcp
```

**What this does:**

- Downloads SQL Server 2022 image (if not already downloaded)
- Creates a container named `mssql_liquibase_tutorial`
- Starts SQL Server on port `1433`
- Uses the password from `$MSSQL_LIQUIBASE_TUTORIAL_PWD`
- Includes a health check to verify SQL Server is ready

**Wait for SQL Server to be ready:**

The container has a built-in health check. Wait until the status shows `(healthy)`:

```bash
# Watch the container status (Ctrl+C to exit)
watch -n 2 'docker ps | grep mssql_liquibase_tutorial'
```

Look for: `Up X seconds (healthy)`

Alternatively, check the logs:

```bash
docker logs mssql_liquibase_tutorial --tail 20
```

Look for: `SQL Server is now ready for client connections`

#### Build Liquibase container image

The Liquibase container is a "run-once" tool (not a long-running service), so we just need to build the image:

```bash
# Navigate to the liquibase docker directory
cd /workspaces/dbtools/docker/liquibase

# Build the custom Liquibase image with SQL Server drivers
docker compose build

# Verify the image was created
docker images | grep liquibase
```

**Expected output:**

```
liquibase       latest    abc123def456   Just now   500MB
```

**Note:** The Liquibase container is not meant to stay running - it executes commands and exits. We'll use `docker run` to execute Liquibase commands throughout this tutorial.

### Important Note About Docker Commands

Throughout this tutorial, all `docker run` commands for Liquibase follow this pattern:

```bash
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.<ENV>.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  <LIQUIBASE_COMMAND>
```

**Critical points:**

- `--user $(id -u):$(id -g)` - Run container as your user (not root) to avoid permission issues
- `--network=liquibase_tutorial` - Use the dedicated Docker network (NOT `--network=host`)
- `--password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}"` - Pass password on command line (environment variable substitution doesn't work in properties files)
- The password parameter must come AFTER the properties file but BEFORE the Liquibase command

**If you see connection errors**, verify you're using the correct network and passing the password parameter.

### Check SQL Server is Running

Now verify you can connect to SQL Server. This test ensures your database is accessible before we start.

```bash
# Test connection (should show server name and date)
sqlcmd-tutorial -Q "SELECT @@SERVERNAME AS ServerName, GETDATE() AS CurrentTime"
```

**Expected output:**

```
ServerName               CurrentTime
------------------------ -----------------------
mssql_liquibase_tutorial 2025-11-16 02:49:32.910
```

**Troubleshooting:**

- **Connection refused**: SQL Server might not be running. Check with `docker ps | grep mssql_liquibase_tutorial`
- **Login failed**: Password might be wrong. Verify `$MSSQL_LIQUIBASE_TUTORIAL_PWD` is set correctly

### Helper Script for sqlcmd

To simplify running SQL commands inside the tutorial SQL Server container, this guide uses a helper script located at `sqlcmd-tutorial`.

**Create an alias for easier use:**

```bash
alias sqlcmd-tutorial='sqlcmd-tutorial'
```

**Usage examples:**

- Run an inline query:

```bash
sqlcmd-tutorial -Q "SELECT @@SERVERNAME AS ServerName, GETDATE() AS CurrentTime;"
```

- Run a `.sql` file:

```bash
sqlcmd-tutorial 01_create_databases.sql
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
sqlcmd-tutorial 01_create_databases.sql
```

**Verify all three databases exist:**

```bash
# Run the verification script
sqlcmd-tutorial 02_verify_databases.sql
```

**Expected output:**

```
name        database_id  create_date
----------- ------------ -----------------------
testdbdev   5            2025-11-14 20:00:00.000
testdbprd   7            2025-11-14 20:00:01.000
testdbstg   6            2025-11-14 20:00:00.500
```

**What did we just do?**

- Created three empty databases using `01_create_databases.sql`
- All on the same SQL Server instance (simulating separate environments)
- In real production, these would be on different servers/clouds
- Verified creation with `02_verify_databases.sql`

**Next: Create the app schema** (required before using Liquibase):

```bash
# Create app schema in all three databases
sqlcmd-tutorial 02a_create_app_schema.sql
```

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
sqlcmd-tutorial 03_populate_dev_database.sql
```

**Verify objects were created in development:**

```bash
# List all objects in app schema (development only)
sqlcmd-tutorial 04_verify_dev_objects.sql

# Check sample data
sqlcmd-tutorial 05_verify_dev_data.sql
```

**What did we just do?**

- Created a complete working database in development using `03_populate_dev_database.sql`
- Table `customer` with indexes and constraints, view `v_customer_basic` (in existing `app` schema)
- Added sample data (3 customer records)
- Verified with `04_verify_dev_objects.sql` and `05_verify_dev_data.sql`
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

# Generate baseline from development database
# IMPORTANT: Use --schemas=app to capture objects in the app schema
# IMPORTANT: Use --include-schema=true to include schemaName attributes in the XML
# IMPORTANT: Use --user flag to run as your user (not root)
# IMPORTANT: Use --network=liquibase_tutorial (not --network=host)
# IMPORTANT: Pass password on command line since env var substitution doesn't work in properties file
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  --changelog-file=/workspace/database/changelog/baseline/V0000__baseline.xml \
  --schemas=app \
  --include-schema=true \
  generateChangeLog

# Check the generated file (owned by your user, not root)
cat database/changelog/baseline/V0000__baseline.xml
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
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  changelogSync

# Tag the baseline (create a named checkpoint for rollback purposes)
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  tag baseline
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

### Deploy to Staging (Full Deployment)

Staging is empty, so we **deploy** the baseline (actually run all DDL):

```bash
cd /data/liquibase-tutorial

# Preview what will run
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  updateSQL

# Deploy to staging
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  update

# Tag the baseline
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  tag baseline
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

### Deploy to Production (Full Deployment)

Production is also empty, so we deploy the baseline:

```bash
cd /data/liquibase-tutorial

# Preview what will run
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.prod.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  updateSQL

# Deploy to production
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.prod.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  update

# Tag the baseline
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.prod.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  tag baseline
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

**Important Note about Rollbacks with SQL Format:**

For rollbacks to work with SQL files, we need to use **XML wrappers with `<sqlFile>` tags** instead of direct `<include>` tags. This tutorial uses this approach to demonstrate working rollbacks.

**The approach we're using (XML wrapper with sqlFile):**

```xml
<changeSet id="V0001-add-orders-table" author="tutorial">
    <sqlFile path="changes/V0001__add_orders_table.sql" relativeToChangelogFile="true"/>
    <rollback>
        DROP TABLE IF EXISTS app.orders;
    </rollback>
</changeSet>
```

**Why this works:**

- The `<sqlFile>` tag executes the SQL file for the forward migration
- The `<rollback>` block defines explicit SQL to undo the change
- Liquibase can execute the rollback when needed

**Alternative approach (not used in this tutorial):**

```xml
<changeSet id="V0001-add-orders-table" author="tutorial">
    <createTable tableName="orders" schemaName="app">
        <!-- table definition -->
    </createTable>
    <rollback>
        <dropTable tableName="orders" schemaName="app"/>
    </rollback>
</changeSet>
```

This tutorial uses the XML wrapper approach to demonstrate working rollbacks in Step 9.

### Update Master Changelog

We'll use XML wrappers with `<sqlFile>` tags to enable rollback support:

```bash
# Update changelog.xml with XML wrappers for rollback support
cat > /data/liquibase-tutorial/database/changelog/changelog.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <!-- Baseline -->
    <include file="baseline/V0000__baseline.xml" relativeToChangelogFile="true"/>

    <!-- Changes with rollback support -->
    <changeSet id="V0001-add-orders-table" author="tutorial">
        <sqlFile path="changes/V0001__add_orders_table.sql" relativeToChangelogFile="true"/>
        <rollback>
            DROP TABLE IF EXISTS app.orders;
        </rollback>
    </changeSet>

</databaseChangeLog>
EOF
```

**What changed:** Instead of using `<include file="changes/V0001.sql" />`, we use a `<changeSet>` with `<sqlFile>` and an explicit `<rollback>` block. This enables Liquibase to execute rollbacks when needed.

## Step 7: Deploy Change Across Environments

Now deploy this change through dev → stage → prod:

### Deploy to Development

```bash
cd /data/liquibase-tutorial

# Check what will be deployed (should show V0001 only)
docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  status --verbose

# Preview the SQL
docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  updateSQL

# Deploy to development
docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  update

# Tag this release
docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  tag release-v1.1
```

**Verify in development:**

```bash
sqlcmd-tutorial -Q "
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
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  updateSQL

# Deploy to staging
docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  update

# Tag this release
docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  tag release-v1.1
```

**Verify in staging:**

```bash
sqlcmd-tutorial -Q "
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
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.prod.properties \
  updateSQL

# Deploy to production
docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.prod.properties \
  update

# Tag this release
docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.prod.properties \
  tag release-v1.1
```

**Verify in production:**

```bash
sqlcmd-tutorial -Q "
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

## Step 8: More Database Changes

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

### Change 3: Add Index for Performance

Add an index on the `created_at` column for date-based queries:

```bash
cat > /data/liquibase-tutorial/database/changelog/changes/V0003__add_customer_date_index.sql << 'EOF'
--changeset tutorial:V0003-add-customer-date-index
-- Purpose: Add index on created_at for faster date-based queries

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes i
    JOIN sys.objects o ON i.object_id = o.object_id
    WHERE o.name = 'customer'
      AND SCHEMA_NAME(o.schema_id) = 'app'
      AND i.name = 'IX_customer_created_at'
)
BEGIN
    CREATE NONCLUSTERED INDEX IX_customer_created_at
        ON app.customer(created_at DESC);
    PRINT 'Created index IX_customer_created_at';
END
ELSE
BEGIN
    PRINT 'Index IX_customer_created_at already exists';
END

--rollback DROP INDEX IF EXISTS IX_customer_created_at ON app.customer;
EOF
```

### Change 4: Update View

Update the customer view to include order statistics:

```bash
cat > /data/liquibase-tutorial/database/changelog/changes/V0004__update_customer_view.sql << 'EOF'
--changeset tutorial:V0004-update-customer-view runOnChange:true
-- Purpose: Enhance customer view with order statistics

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

**Understanding `runOnChange`:**

The `runOnChange:true` attribute is crucial for managing views:

- **Without `runOnChange`**: Changeset runs once, never again (normal behavior)
- **With `runOnChange:true`**: Liquibase recalculates the MD5 checksum
  - If content changed: Re-executes the changeset
  - If content unchanged: Skips execution

**When to use `runOnChange`:**

✅ Views (definition changes)
✅ Configuration data that may need updates

❌ Tables (use ALTER TABLE in new changesets instead)
❌ One-time data migrations

**Best practice**: Always use `DROP IF EXISTS` then `CREATE` pattern for objects with `runOnChange:true`.

### Update Master Changelog with All Changes

We'll continue using XML wrappers with explicit rollback blocks:

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

    <!-- Changes with rollback support -->
    <changeSet id="V0001-add-orders-table" author="tutorial">
        <sqlFile path="changes/V0001__add_orders_table.sql" relativeToChangelogFile="true"/>
        <rollback>
            DROP TABLE IF EXISTS app.orders;
        </rollback>
    </changeSet>

    <changeSet id="V0002-increase-email-length" author="tutorial">
        <sqlFile path="changes/V0002__increase_email_length.sql" relativeToChangelogFile="true"/>
        <rollback>
            ALTER TABLE app.customer ALTER COLUMN email NVARCHAR(320) NULL;
        </rollback>
    </changeSet>

    <changeSet id="V0003-add-customer-date-index" author="tutorial">
        <sqlFile path="changes/V0003__add_customer_date_index.sql" relativeToChangelogFile="true"/>
        <rollback>
            DROP INDEX IF EXISTS IX_customer_created_at ON app.customer;
        </rollback>
    </changeSet>

    <changeSet id="V0004-update-customer-view" author="tutorial">
        <sqlFile path="changes/V0004__update_customer_view.sql" relativeToChangelogFile="true"/>
        <rollback>
            EXEC('CREATE VIEW app.v_customer_basic AS
                SELECT customer_id, full_name, email, phone_number, created_at
                FROM app.customer;')
        </rollback>
    </changeSet>

</databaseChangeLog>
EOF
```

**What we added:** Each change now has an explicit `<rollback>` block that defines how to undo the change. This enables actual rollback functionality in Step 9.

### Deploy All Changes to Development

```bash
cd /data/liquibase-tutorial

# Check what will deploy (should show V0002, V0003, V0004)
docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  status --verbose

# Deploy to development
docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  update

# Tag the release
docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  tag release-v1.2
```

### Deploy to Staging

```bash
cd /data/liquibase-tutorial

docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  update

docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  tag release-v1.2
```

### Deploy to Production

```bash
cd /data/liquibase-tutorial

docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.prod.properties \
  update

docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.prod.properties \
  tag release-v1.2
```

**Verify all changes applied:**

```bash
# Check email column length in production
sqlcmd-tutorial -Q "
USE testdbprd;

-- Check email column length
SELECT c.name AS ColumnName, t.name AS DataType, c.max_length AS MaxLength
FROM sys.columns c
JOIN sys.types t ON c.user_type_id = t.user_type_id
JOIN sys.objects o ON c.object_id = o.object_id
WHERE SCHEMA_NAME(o.schema_id) = 'app'
  AND o.name = 'customer'
  AND c.name = 'email';

-- Check indexes
SELECT i.name AS IndexName, i.type_desc, c.name AS ColumnName
FROM sys.indexes i
JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
JOIN sys.objects o ON i.object_id = o.object_id
WHERE SCHEMA_NAME(o.schema_id) = 'app'
  AND o.name = 'customer'
  AND i.name LIKE 'IX_%'
ORDER BY i.name, ic.key_ordinal;

-- Check view definition
EXEC sp_helptext 'app.v_customer_basic';
"
```

## Step 9: Tags and Deployment History

### Understanding Tags and Rollbacks

Tags mark specific points in your deployment history, creating named checkpoints. Since we're using XML wrappers with explicit `<rollback>` blocks, Liquibase can actually perform automated rollbacks.

### View Deployment History and Tags

```bash
# List all tags in development
sqlcmd-tutorial -Q "
USE testdbdev;
SELECT ID, TAG, DATEEXECUTED
FROM DATABASECHANGELOG
WHERE TAG IS NOT NULL
ORDER BY DATEEXECUTED;
"
```

**Expected output:**

```text
ID                  TAG              DATEEXECUTED
------------------- ---------------- -----------------------
1763262317859-4     baseline         2025-11-16 03:07:33.607
V0001-add-orders-table  release-v1.1     2025-11-16 03:56:16.180
V0004-update-customer-view  release-v1.2     2025-11-16 04:03:23.403
```

**What each tag represents:**

- **baseline**: Initial database state when we started using Liquibase
- **release-v1.1**: After adding orders table (V0001)
- **release-v1.2**: After adding email length, date index, and view update (V0002-V0004)

### View Complete Deployment History

```bash
# See all executed changesets across all environments
sqlcmd-tutorial -Q "
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

**This shows:**

- Chronological order of all changes (ORDEREXECUTED)
- What changed (ID, FILENAME)
- When it was deployed (DATEEXECUTED)
- Which release it belonged to (TAG)

### Compare Deployment Status Across Environments

```bash
# Development status
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  status --verbose

# Staging status
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  status --verbose

# Production status
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.prod.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  status --verbose
```

**If all environments are synchronized:**

```text
Liquibase is up to date
```

**If an environment is behind:**

```text
1 change sets have not been applied to <database>
     changes/V0005__add_new_feature.sql::raw::includeAll
```

### Understanding Deployment State

```bash
# View DATABASECHANGELOG table directly to see deployment history
sqlcmd-tutorial -Q "
USE testdbdev;

-- Count changesets by tag
SELECT
    COALESCE(TAG, 'untagged') AS ReleaseTag,
    COUNT(*) AS ChangesetCount
FROM DATABASECHANGELOG
GROUP BY TAG
ORDER BY MIN(DATEEXECUTED);
"
```

**Expected output:**

```text
ReleaseTag       ChangesetCount
---------------- --------------
untagged         3              (baseline changesets 1-3)
baseline         1              (baseline changeset 4)
release-v1.1     1              (V0001)
untagged         2              (V0002, V0003)
release-v1.2     1              (V0004)
```

### Demonstrate Rollback to Previous Release

Now that we have explicit `<rollback>` blocks in our changesets, we can actually roll back changes:

```bash
cd /data/liquibase-tutorial

# First, let's see what changes would be rolled back
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  rollbackSQL release-v1.1

# Actually perform the rollback
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  rollback release-v1.1
```

**What happens:**

- Liquibase rolls back all changes after `release-v1.1` tag
- This removes V0002, V0003, V0004 changes
- The database returns to release-v1.1 state
- Rollback SQL from `<rollback>` blocks is executed

**Verify rollback worked:**

```bash
# Check DATABASECHANGELOG - V0002, V0003, V0004 should be removed
sqlcmd-tutorial -Q "
USE testdbdev;
SELECT ID, AUTHOR, FILENAME, TAG
FROM DATABASECHANGELOG
ORDER BY ORDEREXECUTED;
"

# Verify schema changes were undone
# Email should be back to NVARCHAR(320)
sqlcmd-tutorial -Q "
USE testdbdev;
SELECT c.name AS column_name, t.name AS type_name, c.max_length
FROM sys.columns c
JOIN sys.types t ON c.user_type_id = t.user_type_id
WHERE object_id = OBJECT_ID('app.customer')
  AND c.name = 'email';
"

# IX_customer_created_at index should be gone
sqlcmd-tutorial -Q "
USE testdbdev;
SELECT name FROM sys.indexes WHERE object_id = OBJECT_ID('app.customer');
"

# View should be back to basic version (no order stats)
sqlcmd-tutorial -Q "
USE testdbdev;
EXEC sp_helptext 'app.v_customer_basic';
"
```

### Roll Forward Again

After demonstrating rollback, let's re-apply the changes:

```bash
# Re-deploy the changes
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  update

# Re-tag as release-v1.2
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  tag release-v1.2
```

**This demonstrates:**

- ✅ Rollback capability with explicit `<rollback>` blocks
- ✅ Ability to roll forward again after rollback
- ✅ Full bidirectional change management

### Alternative: Rollback by Count

You can also roll back a specific number of changesets:

```bash
# Roll back the last 2 changesets (V0003, V0004)
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  rollbackCount 2
```

### Real-World Rollback Strategy

While automated rollbacks work with our XML wrapper approach, here's how to handle rollback scenarios in production:

#### Strategy 1: Test rollbacks in non-production first

```bash
# Always test rollback in development/staging first
docker run ... --defaults-file=liquibase.dev.properties rollback <tag>

# Verify the database is in expected state
# Then apply rollback to production if needed
```

#### Strategy 2: Forward-fix (often preferred)

Instead of rolling back, create a new changeset that fixes the issue:

```bash
# If V0005 caused a problem, create V0006 to fix it
cat > database/changelog/changes/V0006__fix_v0005_issue.sql << 'EOF'
--changeset tutorial:V0006-fix-v0005-issue
-- Revert the problematic change from V0005
ALTER TABLE app.customer DROP COLUMN IF EXISTS problematic_column;
EOF
```

**Why forward-fix is often preferred:**

- ✅ Maintains full audit trail
- ✅ Can include additional fixes in same changeset
- ✅ Less risk than running untested rollback in production
- ✅ Matches how code deployments work (deploy a fix, not revert)

#### Strategy 3: Manual rollback script for critical changes

Create explicit rollback scripts for testing:

```bash
# Create rollback script for release-v1.2
cat > rollback_release_v1.2.sql << 'EOF'
-- Manual rollback script for release-v1.2 (V0002-V0004)
-- For testing purposes only

USE testdbdev;

-- Matches the <rollback> blocks in changelog.xml
-- Undo V0004: Drop enhanced view, recreate basic version
EXEC('DROP VIEW IF EXISTS app.v_customer_basic;
CREATE VIEW app.v_customer_basic AS
SELECT customer_id, full_name, email, phone_number, created_at
FROM app.customer;')

-- Undo V0003: Drop date index
DROP INDEX IF EXISTS IX_customer_created_at ON app.customer;

-- Undo V0002: Restore email to NVARCHAR(320)
ALTER TABLE app.customer ALTER COLUMN email NVARCHAR(320) NULL;

PRINT 'Rolled back release-v1.2 changes';
EOF
```

#### Strategy 4: Database restore (last resort)

For catastrophic issues, restore from backup to a tagged release point.

## Understanding Liquibase's Tracking Mechanism

Before diving into the deployment pipeline, let's understand how Liquibase tracks changes. This is the "magic" that makes automated deployments work.

### How Liquibase Knows What to Run

**The core problem**: When you deploy database changes, how does Liquibase know:

- What has already been applied?
- What still needs to run?
- Whether a changeset was modified after deployment?

**The solution**: Two special tracking tables that Liquibase creates automatically.

### The DATABASECHANGELOG Table

When Liquibase first runs against a database, it creates a table called `DATABASECHANGELOG`. This table is like a logbook recording every change ever applied to the database.

**DATABASECHANGELOG structure:**

```sql
-- View the change history
SELECT * FROM DATABASECHANGELOG;
```

**What each column means:**

| Column | Purpose | Example |
|--------|---------|---------|
| **ID** | Unique identifier from `--changeset` comment | `V0001-add-orders-table` |
| **AUTHOR** | Who created the change | `tutorial` |
| **FILENAME** | Path to changelog file | `changes/V0001__add_orders_table.sql` |
| **DATEEXECUTED** | When it ran | `2025-11-13 14:30:00` |
| **ORDEREXECUTED** | Sequence number (1, 2, 3...) | `5` |
| **EXECTYPE** | How it ran: EXECUTED, RERAN, SKIPPED | `EXECUTED` |
| **MD5SUM** | Checksum to detect modifications | `8:d41d8cd98f00b204e980` |
| **DESCRIPTION** | What changed | `createTable tableName=orders` |
| **TAG** | Optional label for rollback points | `release-v1.0` |
| **LIQUIBASE** | Liquibase version that ran it | `5.0.1` |

**How Liquibase decides what to run (step by step):**

1. **Read the master changelog** (`changelog.xml`) to get the complete list of changesets
   - Example: baseline, V0001, V0002, V0003

2. **Query DATABASECHANGELOG** to see what already ran in this database
   - Example: baseline and V0001 exist in the table

3. **Compare checksums** to detect if deployed changesets were modified
   - Calculates MD5 hash of changeset content
   - Compares to stored MD5SUM in DATABASECHANGELOG
   - If different → ERROR! Someone modified a deployed changeset

4. **Calculate what needs to run**: Changes in changelog but NOT in DATABASECHANGELOG
   - Example: V0002 and V0003 need to run

5. **Execute new changesets** in order
   - Runs V0002 first, then V0003
   - Records each execution in DATABASECHANGELOG

6. **Update tracking table** after each successful changeset
   - Inserts row with ID, AUTHOR, DATEEXECUTED, MD5SUM, etc.

**Why checksums matter:**

Checksums protect against dangerous modifications:

```sql
-- Original changeset (already deployed)
--changeset tutorial:V0001-add-orders-table
CREATE TABLE app.orders (
    order_id INT PRIMARY KEY,
    customer_id INT
);
```

If someone later edits it:

```sql
-- Modified changeset (DANGEROUS!)
--changeset tutorial:V0001-add-orders-table
CREATE TABLE app.orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_total DECIMAL(18,2)  -- Added this line
);
```

**What happens:**

1. Liquibase recalculates checksum → different from stored value
2. Throws error: "Validation Failed: changesets have checksum mismatch"
3. Deployment stops before causing problems

**Why this matters:**

- Dev already has the table without `order_total` column
- Stage might have it (if you ran the modified version there)
- Prod definitely doesn't have it
- Now your environments are inconsistent (disaster!)

**The right way**: Create a new changeset:

```sql
--changeset tutorial:V0002-add-order-total
ALTER TABLE app.orders ADD order_total DECIMAL(18,2);
```

**Viewing your change history:**

```bash
# See all executed changesets in development
sqlcmd-tutorial -Q "
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

**Example output:**

```
ORDEREXECUTED  ID                           AUTHOR    FILENAME                              DATEEXECUTED         TAG
1              baseline-schema              system    baseline/V0000__baseline.xml          2025-11-13 10:00:00  baseline
2              baseline-table-customer      system    baseline/V0000__baseline.xml          2025-11-13 10:00:01  baseline
3              V0001-add-orders-table       tutorial  changes/V0001__add_orders_table.sql   2025-11-13 11:30:00  release-v1.1
```

### The DATABASECHANGELOGLOCK Table

The second table Liquibase creates is `DATABASECHANGELOGLOCK`. This table prevents two deployments from running simultaneously.

**Why do we need a lock?**

Imagine two scenarios without locking:

- **Scenario 1**: Two developers deploy at the same time → Both try to create the same table → Error!
- **Scenario 2**: Automated pipeline and manual deployment run simultaneously → Changes apply in wrong order → Database corruption!

**How the lock works:**

1. Before any deployment, Liquibase tries to acquire the lock
   - Sets `LOCKED = 1` in DATABASECHANGELOGLOCK table
   - Records who acquired it (LOCKEDBY) and when (LOCKGRANTED)

2. If lock is already held, Liquibase waits
   - Checks every few seconds if lock is released
   - Times out after a few minutes (prevents infinite waiting)

3. After deployment completes, Liquibase releases the lock
   - Sets `LOCKED = 0`
   - Clears LOCKEDBY and LOCKGRANTED

**View lock status:**

```sql
SELECT * FROM DATABASECHANGELOGLOCK;
```

**Normal state (unlocked):**

```
ID  LOCKED  LOCKGRANTED  LOCKEDBY
1   0       NULL         NULL
```

**Locked state (deployment in progress):**

```
ID  LOCKED  LOCKGRANTED              LOCKEDBY
1   1       2025-11-13 14:30:00.000  mycomputer (192.168.1.100)
```

**When locks get stuck:**

Sometimes deployments fail (server crash, network disconnect, Ctrl+C) and the lock doesn't get released.

**Symptoms:**

- Liquibase shows: "Waiting for changelog lock..."
- Hangs indefinitely

**Fix:**

```bash
# Force release the lock
docker run --rm --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  releaseLocks
```

**Manual fix (emergency only):**

```sql
UPDATE DATABASECHANGELOGLOCK
SET LOCKED = 0, LOCKGRANTED = NULL, LOCKEDBY = NULL
WHERE ID = 1;
```

**Important**: Only force-release if you're CERTAIN no deployment is actually running!

## Step 10: Detecting Database Drift

### What is Database Drift?

**Database drift** occurs when the actual database schema differs from what's tracked in version control. This can happen when:

- Someone makes manual changes directly in the database (bypassing Liquibase)
- An emergency hotfix is applied without updating changelogs
- Environments get out of sync (dev differs from stage/prod)
- Unauthorized changes are made to production

**Why drift is dangerous:**

- ❌ Environments are inconsistent (code works in dev, fails in prod)
- ❌ Deployments may fail or behave unexpectedly
- ❌ Audit trail is incomplete (can't prove compliance)
- ❌ Team doesn't know the true state of databases
- ❌ Rollbacks won't work correctly

**The solution**: Liquibase's `diff` command detects drift by comparing two databases.

### Simulating Database Drift

Let's intentionally create drift to demonstrate detection. We'll make a manual change to staging that bypasses Liquibase:

```bash
# Make an unauthorized change to staging (simulating drift)
docker exec -it mssql_liquibase_tutorial /opt/mssql-tools18/bin/sqlcmd \
  -C -S localhost -U SA -P "${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  -Q "
USE testdbstg;

-- Add a column that's NOT in our changelog (drift!)
ALTER TABLE app.customer ADD loyalty_tier NVARCHAR(20) NULL;

-- Add an index that's NOT in our changelog (drift!)
CREATE NONCLUSTERED INDEX IX_customer_loyalty_tier
ON app.customer(loyalty_tier);

PRINT 'Created drift in staging database';
"
```

**What we just did:**

- Added `loyalty_tier` column to staging
- Created an index on that column
- These changes are NOT tracked in our changelog files
- Development and production don't have these objects
- Staging has "drifted" from version control

### Detecting Drift with diff Command

Now use Liquibase's `diff` command to detect the differences:

```bash
cd /data/liquibase-tutorial

# Compare staging (target) to development (reference)
# This shows what's different in staging vs development
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  diff \
  --reference-url="jdbc:sqlserver://mssql_liquibase_tutorial:1433;databaseName=testdbdev;encrypt=true;trustServerCertificate=true" \
  --reference-username=sa \
  --reference-password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}"
```

**Expected output showing drift:**

```text
Diff Results:
Reference Database: SA @ jdbc:sqlserver://mssql_liquibase_tutorial:1433;databaseName=testdbdev
Comparison Database: SA @ jdbc:sqlserver://mssql_liquibase_tutorial:1433;databaseName=testdbstg

Compared Schemas: app
Product Name: EQUAL
Product Version: EQUAL

Missing Column(s): NONE

Unexpected Column(s):
     app.customer.loyalty_tier

Changed Column(s): NONE

Missing Index(s): NONE

Unexpected Index(s):
     IX_customer_loyalty_tier UNIQUE ON app.customer(loyalty_tier)

Changed Index(s): NONE
```

**Understanding the output:**

- **Reference Database**: The "source of truth" (development)
- **Comparison Database**: The database being checked (staging)
- **Unexpected Column(s)**: Objects in staging that DON'T exist in development = DRIFT!
- **Unexpected Index(s)**: Additional objects found in staging = DRIFT!
- **Missing Column(s)**: Would show objects in dev but NOT in staging

**This tells us:**

- ✅ Drift detected successfully
- ✅ Staging has 1 extra column: `loyalty_tier`
- ✅ Staging has 1 extra index: `IX_customer_loyalty_tier`
- ⚠️ These changes are NOT in version control
- ⚠️ Deployments might overwrite or conflict with these changes

### What to Do When Drift is Detected

When drift is found, you have three options:

**Option 1: Remove the drift (preferred for unauthorized changes)**

```bash
# Manually remove the drifted objects
docker exec -it mssql_liquibase_tutorial /opt/mssql-tools18/bin/sqlcmd \
  -C -S localhost -U SA -P "${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  -Q "
USE testdbstg;
DROP INDEX IF EXISTS IX_customer_loyalty_tier ON app.customer;
ALTER TABLE app.customer DROP COLUMN IF EXISTS loyalty_tier;
PRINT 'Removed drift from staging';
"
```

**Option 2: Incorporate the drift into version control** - Create a changelog entry for the valid change (see Step 11)

**Option 3: Use diffChangeLog to auto-generate the changeset** (see Step 11)

## Step 11: Generating Changelogs from Differences

### What is diffChangeLog?

While `diff` *detects* differences, `diffChangeLog` *generates* a changelog file that captures those differences as deployable changesets.

**Use cases:**

- Converting drift back into version control
- Reverse-engineering an existing database
- Syncing environments that got out of sync
- Creating baseline from production database

### Generate Changelog from Drift

Let's generate a changelog that captures the drift we created in staging:

```bash
cd /data/liquibase-tutorial

# Generate changelog capturing the drift in staging
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  --changelog-file=/workspace/database/changelog/drift-captured-$(date +%Y%m%d).xml \
  diffChangeLog \
  --reference-url="jdbc:sqlserver://mssql_liquibase_tutorial:1433;databaseName=testdbdev;encrypt=true;trustServerCertificate=true" \
  --reference-username=sa \
  --reference-password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}"
```

**What this does:**

1. Compares staging (target) to development (reference)
2. Finds all differences (the drift)
3. Generates XML changesets to make development match staging
4. Saves to `drift-captured-YYYYMMDD.xml`

**View the generated changelog:**

```bash
cat database/changelog/drift-captured-*.xml
```

**What we see:**

- ✅ Auto-generated changesets capturing the drift
- ✅ Column addition with correct data type
- ✅ Index creation with correct name and structure
- ✅ Ready to version control and deploy

### Clean Up the Drift (For Tutorial Continuation)

Now remove the drift we created so the tutorial environments are synchronized:

```bash
# Remove the drift from staging
docker exec -it mssql_liquibase_tutorial /opt/mssql-tools18/bin/sqlcmd \
  -C -S localhost -U SA -P "${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  -Q "
USE testdbstg;
DROP INDEX IF EXISTS IX_customer_loyalty_tier ON app.customer;
ALTER TABLE app.customer DROP COLUMN IF EXISTS loyalty_tier;
PRINT 'Removed drift from staging';
"

# Verify drift is gone
docker run --rm \
  --user $(id -u):$(id -g) \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.stage.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  diff \
  --reference-url="jdbc:sqlserver://mssql_liquibase_tutorial:1433;databaseName=testdbdev;encrypt=true;trustServerCertificate=true" \
  --reference-username=sa \
  --reference-password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}"
```

**What you've learned:**

- ✅ How to detect database drift with `diff`
- ✅ How to generate changelogs from differences with `diffChangeLog`
- ✅ How to compare environments and identify unauthorized changes
- ✅ How to reverse-engineer databases into version control
- ✅ Best practices for handling drift in production

## Understanding the Deployment Pipeline

### The Complete Workflow

Here's how a typical change flows from idea to production. Understanding this workflow is essential for safe, professional database change management.

**The journey of a database change:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Developer writes change                                │
│ - Create SQL file: V0005__add_loyalty_points.sql               │
│ - Write DDL: ALTER TABLE customer ADD loyalty_points INT       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Add to master changelog with rollback                  │
│ - Edit changelog.xml                                            │
│ - Add changeSet with sqlFile and explicit rollback block       │
│ - <changeSet id="V0005-add-loyalty-points" author="...">       │
│     <sqlFile path="changes/V0005__..."/>                        │
│     <rollback>ALTER TABLE customer DROP COLUMN loyalty_points  │
│     </rollback>                                                 │
│ - Commit to Git version control                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Deploy to Development (testdbdev)                      │
│ - Run: liquibase --defaults-file=dev.properties update         │
│ - Adds loyalty_points column to dev database                   │
│ - Records change in DATABASECHANGELOG                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: Test and verify in dev                                 │
│ - Run queries to check column exists                           │
│ - Test application with new column                             │
│ - Insert test data with loyalty points                         │
│ - Fix any issues, repeat steps 1-4 if needed                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: Deploy to Staging (testdbstg)                          │
│ - Run: liquibase --defaults-file=stage.properties update       │
│ - EXACT SAME SQL runs in staging as ran in dev                 │
│ - Staging now has loyalty_points column                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: Integration testing in staging                         │
│ - Test with realistic data volumes                             │
│ - Check query performance                                      │
│ - Verify application integration                               │
│ - Run full test suite                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 7: Get approval for production (if required)              │
│ - Team lead reviews changes                                    │
│ - Security team approves                                       │
│ - Schedule deployment window                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 8: Deploy to Production (testdbprd)                       │
│ - Run: liquibase --defaults-file=prod.properties update        │
│ - EXACT SAME SQL runs in production                            │
│ - Production now has loyalty_points column                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 9: Monitor and tag release                                │
│ - Monitor application for errors                               │
│ - Check database performance metrics                           │
│ - Tag release: liquibase tag release-v1.5                      │
│ - Document deployment in change log                            │
│ - Notify team of successful deployment                         │
└─────────────────────────────────────────────────────────────────┘
```

**What if something goes wrong?**

At any step, if problems are detected:

- **In dev**: Fix the issue, create new changeset, redeploy
- **In staging**: Rollback, fix issue, redeploy from dev
- **In production**: Rollback immediately using tagged release

### Key Principles

Understanding these principles will help you avoid common pitfalls and deploy changes safely.

#### 1. Same SQL, Different Databases

**The golden rule**: The EXACT same `changelog.xml` file deploys to all environments. Only connection strings differ (via properties files).

**Why this matters:**

```
WRONG APPROACH:
- changelog-dev.xml (different file for dev)
- changelog-stage.xml (different file for stage)
- changelog-prod.xml (different file for prod)
→ Results: Environments drift apart, inconsistencies, bugs

CORRECT APPROACH:
- changelog.xml (ONE file for all environments)
- liquibase.dev.properties (different connection)
- liquibase.stage.properties (different connection)
- liquibase.prod.properties (different connection)
→ Results: Environments stay identical, consistent behavior
```

**Real example of why this matters:**

Developer creates a table in dev:

```sql
CREATE TABLE app.orders (order_id INT, total DECIMAL(10,2));
```

If you manually type this into staging, you might make a typo:

```sql
CREATE TABLE app.orders (order_id INT, total DECIMAL(18,2));  -- Oops! Different precision!
```

Now dev and staging have different schemas. Queries that work in dev might fail in staging. Production might get either version (chaos!).

With Liquibase, the same file deploys everywhere → guaranteed consistency.

#### 2. Progressive Deployment (Never Skip Environments)

**Always follow the path**: dev → stage → prod

**Why each step matters:**

| Environment | Purpose | What You Catch |
|-------------|---------|----------------|
| **Development** | Rapid iteration | Syntax errors, basic logic bugs, schema conflicts |
| **Staging** | Production simulation | Performance issues, data volume problems, integration bugs |
| **Production** | Real users | Nothing! You caught everything in dev and stage |

**Real story of what happens when you skip:**

Team is under pressure, decides to skip staging "just this once":

1. Change works perfectly in dev (small dataset, 100 rows)
2. Deploy directly to production
3. Production has 10 million rows
4. Query takes 5 minutes instead of 1 second (missing index!)
5. Application times out, customers can't place orders
6. Revenue lost, team works all night fixing it

**The fix**: If they'd deployed to staging (with production-like data volume), they would have caught the performance issue before customers were affected.

#### 3. Idempotent Changes (Safe to Re-run)

**Idempotent** means "can be run multiple times with the same result."

**Not idempotent (dangerous):**

```sql
--changeset tutorial:V0005-add-column
ALTER TABLE app.customer ADD loyalty_points INT;
```

**What happens if run twice:**

1. First run: Creates column → Success ✓
2. Second run: Error! Column already exists → Deployment fails ✗

**Idempotent (safe):**

```sql
--changeset tutorial:V0005-add-column
IF NOT EXISTS (
    SELECT 1 FROM sys.columns
    WHERE object_id = OBJECT_ID('app.customer')
    AND name = 'loyalty_points'
)
BEGIN
    ALTER TABLE app.customer ADD loyalty_points INT;
    PRINT 'Added loyalty_points column';
END
ELSE
BEGIN
    PRINT 'Column loyalty_points already exists';
END
```

**What happens if run twice:**

1. First run: Creates column → Success ✓
2. Second run: Skips creation (column exists) → Success ✓

**Why idempotency matters:**

- Network failure might cause partial deployment → safe to retry
- Manual testing might run changeset → production deployment still works
- Rollback and re-apply scenarios → no errors

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
          docker run --rm --network=liquibase_tutorial \
            -v ${{ github.workspace }}:/workspace \
            -e DB_PASSWORD \
            liquibase:latest \
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
          docker run --rm --network=liquibase_tutorial \
            -v ${{ github.workspace }}:/workspace \
            -e DB_PASSWORD \
            liquibase:latest \
            --defaults-file=/workspace/env/liquibase.stage.properties \
            --password="${DB_PASSWORD}" \
            status --verbose

      - name: Deploy to Staging
        env:
          DB_PASSWORD: ${{ secrets.STAGE_DB_PASSWORD }}
        run: |
          docker run --rm --network=liquibase_tutorial \
            -v ${{ github.workspace }}:/workspace \
            -e DB_PASSWORD \
            liquibase:latest \
            --defaults-file=/workspace/env/liquibase.stage.properties \
            --password="${DB_PASSWORD}" \
            update

      - name: Tag Release
        env:
          DB_PASSWORD: ${{ secrets.STAGE_DB_PASSWORD }}
        run: |
          RELEASE_TAG="release-$(date +%Y%m%d-%H%M%S)"
          docker run --rm --network=liquibase_tutorial \
            -v ${{ github.workspace }}:/workspace \
            -e DB_PASSWORD \
            liquibase:latest \
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
          docker run --rm --network=liquibase_tutorial \
            -v ${{ github.workspace }}:/workspace \
            -e DB_PASSWORD \
            liquibase:latest \
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
          docker run --rm --network=liquibase_tutorial \
            -v ${{ github.workspace }}:/workspace \
            -e DB_PASSWORD \
            liquibase:latest \
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
          docker run --rm --network=liquibase_tutorial \
            -v ${{ github.workspace }}:/workspace \
            -e DB_PASSWORD \
            liquibase:latest \
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
liquibase:latest
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
docker run --rm --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
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
docker run --rm --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  releaseLocks
```

**Verify lock status first:**

```bash
sqlcmd-tutorial -Q "
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
sqlcmd-tutorial -Q "
USE ${DB};
SELECT TOP 5 ID, AUTHOR, DATEEXECUTED, TAG
FROM DATABASECHANGELOG
ORDER BY DATEEXECUTED DESC;
"

# Verify expected objects exist
sqlcmd-tutorial -Q "
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

## Common Change Scenarios Reference

This section provides examples for all common database change operations supported by Liquibase Community Edition.

### Scenario 1: Add Column to Existing Table

**Use case:** Add new field to track data

```sql
--changeset yourname:add-customer-phone
IF COL_LENGTH('app.customer', 'phone_number') IS NULL
BEGIN
    ALTER TABLE app.customer ADD phone_number NVARCHAR(20) NULL;
END
```

**Rollback block in changelog.xml:**

```xml
<changeSet id="add-customer-phone" author="yourname">
    <sqlFile path="changes/V0005__add_phone_column.sql" relativeToChangelogFile="true"/>
    <rollback>
        ALTER TABLE app.customer DROP COLUMN IF EXISTS phone_number;
    </rollback>
</changeSet>
```

### Scenario 2: Drop Column from Table

**Use case:** Remove obsolete or redundant column

⚠️ **Warning:** Destructive operation! Consider expand/contract pattern:

1. Stop writes to column (deploy code change first)
2. Wait for read traffic to stop referencing it
3. Then drop the column

```sql
--changeset yourname:drop-legacy-column
IF COL_LENGTH('app.customer', 'legacy_code') IS NOT NULL
BEGIN
    ALTER TABLE app.customer DROP COLUMN legacy_code;
END
```

**Rollback (limited - data will be lost):**

```xml
<changeSet id="drop-legacy-column" author="yourname">
    <sqlFile path="changes/V0006__drop_legacy_column.sql" relativeToChangelogFile="true"/>
    <rollback>
        -- Can recreate column structure but NOT data
        ALTER TABLE app.customer ADD legacy_code NVARCHAR(100) NULL;
    </rollback>
</changeSet>
```

### Scenario 3: Drop Table

**Use case:** Remove obsolete table

⚠️ **Extreme caution:** All data will be lost!

```sql
--changeset yourname:drop-obsolete-table
IF OBJECT_ID('app.legacy_orders', 'U') IS NOT NULL
BEGIN
    -- Drop foreign keys first
    IF OBJECT_ID('FK_legacy_orders_customer', 'F') IS NOT NULL
        ALTER TABLE app.legacy_orders DROP CONSTRAINT FK_legacy_orders_customer;

    DROP TABLE app.legacy_orders;
END
```

**Rollback (structure only, data lost):**

```xml
<changeSet id="drop-obsolete-table" author="yourname">
    <sqlFile path="changes/V0007__drop_table.sql" relativeToChangelogFile="true"/>
    <rollback>
        -- Can recreate table structure but NOT data
        CREATE TABLE app.legacy_orders (
            order_id INT IDENTITY(1,1) PRIMARY KEY,
            customer_id INT NOT NULL
        );
    </rollback>
</changeSet>
```

### Scenario 4: Change Column Data Type

**Use case:** Expand varchar size, change int to bigint, etc.

```sql
--changeset yourname:expand-email-size
-- Expanding from NVARCHAR(320) to NVARCHAR(500)
IF EXISTS (
    SELECT 1 FROM sys.columns c
    JOIN sys.types t ON c.user_type_id = t.user_type_id
    WHERE object_id = OBJECT_ID('app.customer')
      AND c.name = 'email'
      AND t.name = 'nvarchar'
      AND c.max_length < 1000  -- 500 * 2 bytes
)
BEGIN
    ALTER TABLE app.customer ALTER COLUMN email NVARCHAR(500) NULL;
END
```

**Rollback:**

```xml
<rollback>
    ALTER TABLE app.customer ALTER COLUMN email NVARCHAR(320) NULL;
</rollback>
```

### Scenario 5: Change Column Nullability

**Use case:** Make optional field required (or vice versa)

**Making column NOT NULL (requires data cleanup first):**

```sql
--changeset yourname:make-email-required
-- Step 1: Fill NULL values with placeholder
UPDATE app.customer
SET email = 'noemail@example.com'
WHERE email IS NULL;

-- Step 2: Make column NOT NULL
IF EXISTS (
    SELECT 1 FROM sys.columns
    WHERE object_id = OBJECT_ID('app.customer')
      AND name = 'email'
      AND is_nullable = 1
)
BEGIN
    ALTER TABLE app.customer ALTER COLUMN email NVARCHAR(320) NOT NULL;
END
```

**Making column NULL (safe):**

```sql
--changeset yourname:make-phone-optional
IF EXISTS (
    SELECT 1 FROM sys.columns
    WHERE object_id = OBJECT_ID('app.customer')
      AND name = 'phone_number'
      AND is_nullable = 0
)
BEGIN
    ALTER TABLE app.customer ALTER COLUMN phone_number NVARCHAR(20) NULL;
END
```

### Scenario 6: Add/Drop Index

**Add index:**

```sql
--changeset yourname:add-email-index
IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE object_id = OBJECT_ID('app.customer')
      AND name = 'IX_customer_email'
)
BEGIN
    CREATE NONCLUSTERED INDEX IX_customer_email
    ON app.customer(email)
    WHERE email IS NOT NULL;  -- Filtered index
END
```

**Drop index:**

```sql
--changeset yourname:drop-unused-index
IF EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE object_id = OBJECT_ID('app.customer')
      AND name = 'IX_customer_old_field'
)
BEGIN
    DROP INDEX IX_customer_old_field ON app.customer;
END
```

### Scenario 7: Add/Drop Foreign Key Constraint

**Add foreign key:**

```sql
--changeset yourname:add-fk-orders-customer
IF NOT EXISTS (
    SELECT 1 FROM sys.foreign_keys
    WHERE name = 'FK_orders_customer'
)
BEGIN
    ALTER TABLE app.orders
    ADD CONSTRAINT FK_orders_customer
    FOREIGN KEY (customer_id)
    REFERENCES app.customer(customer_id);
END
```

**Drop foreign key:**

```sql
--changeset yourname:drop-obsolete-fk
IF EXISTS (
    SELECT 1 FROM sys.foreign_keys
    WHERE name = 'FK_old_constraint'
)
BEGIN
    ALTER TABLE app.orders DROP CONSTRAINT FK_old_constraint;
END
```

### Scenario 8: Modify Stored Procedure

**Use case:** Update business logic

```sql
--changeset yourname:update-add-customer-proc runOnChange:true
-- runOnChange:true means this will re-run if the MD5 checksum changes

IF OBJECT_ID('app.usp_add_customer', 'P') IS NOT NULL
    DROP PROCEDURE app.usp_add_customer;
GO

CREATE PROCEDURE app.usp_add_customer
    @full_name NVARCHAR(200),
    @email NVARCHAR(500) = NULL,  -- Updated from 320
    @phone NVARCHAR(20) = NULL     -- Added new parameter
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO app.customer (full_name, email, phone_number)
    VALUES (@full_name, @email, @phone);

    SELECT SCOPE_IDENTITY() AS customer_id;
END;
GO
```

**Rollback (previous version):**

```xml
<rollback>
    EXEC('DROP PROCEDURE IF EXISTS app.usp_add_customer;
    CREATE PROCEDURE app.usp_add_customer
        @full_name NVARCHAR(200),
        @email NVARCHAR(320) = NULL
    AS
    BEGIN
        INSERT INTO app.customer (full_name, email) VALUES (@full_name, @email);
        SELECT SCOPE_IDENTITY() AS customer_id;
    END;')
</rollback>
```

### Scenario 9: Modify Function

**Use case:** Update calculation logic

```sql
--changeset yourname:update-mask-email-func runOnChange:true
IF OBJECT_ID('app.fn_mask_email', 'FN') IS NOT NULL
    DROP FUNCTION app.fn_mask_email;
GO

CREATE FUNCTION app.fn_mask_email (@email NVARCHAR(500))
RETURNS NVARCHAR(500)
AS
BEGIN
    IF @email IS NULL RETURN NULL;
    DECLARE @at INT = CHARINDEX('@', @email);
    IF @at <= 1 RETURN @email;
    -- Enhanced: show first 3 chars instead of 1
    RETURN CONCAT(LEFT(@email, 3), '***', SUBSTRING(@email, @at, LEN(@email)));
END;
GO
```

### Scenario 10: Data Migration/Update

**Use case:** Transform existing data

```sql
--changeset yourname:normalize-phone-numbers
-- Standardize phone format from various formats to xxx-xxx-xxxx

UPDATE app.customer
SET phone_number =
    CASE
        WHEN phone_number LIKE '(%' THEN
            -- (555) 123-4567 -> 555-123-4567
            REPLACE(REPLACE(REPLACE(phone_number, '(', ''), ')', ''), ' ', '-')
        WHEN phone_number LIKE '+1%' THEN
            -- +1-555-123-4567 -> 555-123-4567
            SUBSTRING(phone_number, 4, LEN(phone_number))
        ELSE phone_number
    END
WHERE phone_number IS NOT NULL
  AND phone_number NOT LIKE '___-___-____';
```

**Rollback:** Usually not possible for data migrations. Consider keeping backup or creating reverse transformation.

### Scenario 11: Add Default Value to Existing Column

```sql
--changeset yourname:add-default-status
IF NOT EXISTS (
    SELECT 1 FROM sys.default_constraints
    WHERE parent_object_id = OBJECT_ID('app.orders')
      AND parent_column_id = (
          SELECT column_id FROM sys.columns
          WHERE object_id = OBJECT_ID('app.orders')
            AND name = 'status'
      )
)
BEGIN
    ALTER TABLE app.orders
    ADD CONSTRAINT DF_orders_status DEFAULT 'pending' FOR status;
END
```

### Scenario 12: Rename Column

**Use case:** Improve naming clarity

⚠️ **Coordination required:** Code must be updated simultaneously

```sql
--changeset yourname:rename-customer-name
IF COL_LENGTH('app.customer', 'name') IS NOT NULL
    AND COL_LENGTH('app.customer', 'full_name') IS NULL
BEGIN
    EXEC sp_rename 'app.customer.name', 'full_name', 'COLUMN';
END
```

### Scenario 13: Database Drift - Objects Not in Deployment

**The Problem:** Target database has objects that aren't in your Liquibase changelog. This happens when:

- Developers create objects manually in dev/stage/prod
- Legacy scripts were run before Liquibase adoption
- Hotfix applied directly to production during outage
- Different teams managing different schemas

**Detection Methods:**

**Method 1: Compare schemas manually**

```bash
# In dev - see what Liquibase thinks should exist
docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  status --verbose

# In database - see what actually exists
docker exec mssql_liquibase_tutorial /opt/mssql-tools18/bin/sqlcmd \
  -C -S localhost -U SA -P "${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  -d testdbdev -Q "
SELECT
    SCHEMA_NAME(schema_id) AS SchemaName,
    name AS ObjectName,
    type_desc AS ObjectType,
    create_date AS Created
FROM sys.objects
WHERE schema_id = SCHEMA_ID('app')
  AND type IN ('U', 'V', 'P', 'FN', 'IF', 'TF')
ORDER BY type_desc, name;
"
```

**Method 2: Generate changelog from database**

```bash
# Generate what SHOULD be in changelog based on actual database
docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  --changelog-file=/workspace/drift/actual_database.xml \
  generateChangeLog

# Compare drift/actual_database.xml with database/changelog/changelog.xml
# Any objects in actual_database.xml but not in changelog.xml = drift
```

**Method 3: Use diffChangeLog (recommended)**

```bash
# Compare database against your changelog
docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  --changelog-file=/workspace/drift/database_drift.xml \
  diffChangeLog

# Review drift/database_drift.xml to see what's different
```

**Resolution Strategies:**

**Strategy 1: Bring Liquibase changelog up to date**

If the extra object SHOULD exist (it was a valid change made outside Liquibase):

```bash
# Option A: Sync specific changeset to tracking table
cat > /data/liquibase-tutorial/database/changelog/sync/manual_changes.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <changeSet id="sync-manual-hotfix-table" author="ops-team">
        <preConditions onFail="MARK_RAN">
            <tableExists tableName="emergency_log"/>
        </preConditions>
        <!-- Empty changeset - object already exists, just track it -->
        <sql>SELECT 'Syncing existing emergency_log table' AS msg;</sql>
    </changeSet>

</databaseChangeLog>
EOF

# Add to master changelog
# Then run changelogSync to mark as executed without running
docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  changelogSync
```

**Strategy 2: Remove unwanted drift**

If the object should NOT exist (accidental creation, testing leftover):

```sql
--changeset ops-team:remove-drift-objects
-- Remove objects that shouldn't be in this environment

-- Drop test table that was accidentally created
IF OBJECT_ID('app.test_table', 'U') IS NOT NULL
BEGIN
    PRINT 'Removing drift: dropping test_table';
    DROP TABLE app.test_table;
END

-- Drop procedure that was manually created
IF OBJECT_ID('app.debug_proc', 'P') IS NOT NULL
BEGIN
    PRINT 'Removing drift: dropping debug_proc';
    DROP PROCEDURE app.debug_proc;
END
```

**Strategy 3: Make deployment idempotent to tolerate drift**

Use IF EXISTS checks so deployments work regardless of drift:

```sql
--changeset yourname:create-orders-safe
-- This works whether orders exists or not
IF OBJECT_ID('app.orders', 'U') IS NULL
BEGIN
    CREATE TABLE app.orders (
        order_id INT IDENTITY(1,1) PRIMARY KEY,
        customer_id INT NOT NULL
    );
END
ELSE
BEGIN
    PRINT 'Table app.orders already exists, skipping creation';
END
```

**Strategy 4: Use preconditions to require specific state**

Make deployment fail if drift is detected:

```xml
<changeSet id="strict-deployment" author="yourname">
    <preConditions onFail="HALT">
        <!-- Ensure no drift - table must NOT exist -->
        <not>
            <tableExists tableName="legacy_table"/>
        </not>
        <!-- Ensure expected state - customer table MUST exist -->
        <tableExists tableName="customer"/>
    </preConditions>
    <sqlFile path="changes/V0010__add_feature.sql"/>
</changeSet>
```

### Scenario 14: Database Drift - Objects Are Different

**The Problem:** Object exists in both changelog and database, but they're different. Common scenarios:

1. **Column added manually:** `customer` table has `middle_name` column in prod but not in changelog
2. **Index created manually:** Performance team added index directly in production
3. **Procedure modified:** Hotfix changed stored procedure logic
4. **Data type changed:** Column changed from INT to BIGINT outside Liquibase

**Detection:**

```bash
# Use diff to compare reference (changelog) vs target (database)
docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  diff

# Output shows differences like:
# Reference Database: Empty (your changelog)
# Target Database: testdbdev
# - Column app.customer.middle_name (present in target, missing in reference)
# - Index IX_customer_middle_name (present in target, missing in reference)
```

**Resolution Strategies:**

**Strategy 1: Update changelog to match reality**

If the manual change was correct and should be preserved:

```sql
--changeset ops-team:add-missing-middle-name
-- Sync changelog with manual change made in production
IF COL_LENGTH('app.customer', 'middle_name') IS NULL
BEGIN
    ALTER TABLE app.customer ADD middle_name NVARCHAR(100) NULL;
END
ELSE
BEGIN
    PRINT 'Column middle_name already exists (manual change), now tracked';
END
```

**Strategy 2: Revert manual change, apply proper changeset**

If the change should go through proper process:

```sql
-- Step 1: Revert the manual change
--changeset ops-team:revert-manual-middle-name
IF COL_LENGTH('app.customer', 'middle_name') IS NOT NULL
BEGIN
    ALTER TABLE app.customer DROP COLUMN middle_name;
END

-- Step 2: Apply it properly through Liquibase
--changeset dev-team:add-middle-name-properly
IF COL_LENGTH('app.customer', 'middle_name') IS NULL
BEGIN
    ALTER TABLE app.customer ADD middle_name NVARCHAR(100) NULL;
END
```

**Strategy 3: Use runOnChange for procedures/views**

For stored logic that might change outside Liquibase:

```sql
--changeset yourname:usp-add-customer runOnChange:true
-- runOnChange:true = re-run if definition changes

IF OBJECT_ID('app.usp_add_customer', 'P') IS NOT NULL
    DROP PROCEDURE app.usp_add_customer;
GO

CREATE PROCEDURE app.usp_add_customer
    @full_name NVARCHAR(200),
    @email NVARCHAR(500) = NULL,
    @middle_name NVARCHAR(100) = NULL  -- New parameter
AS
BEGIN
    INSERT INTO app.customer (full_name, email, middle_name)
    VALUES (@full_name, @email, @middle_name);
    SELECT SCOPE_IDENTITY() AS customer_id;
END;
GO
```

**When Liquibase detects the procedure changed** (MD5 checksum different):

- Without `runOnChange`: Deployment FAILS with checksum mismatch
- With `runOnChange`: Re-executes the changeset, updating the procedure

**Strategy 4: Detect drift in CI/CD pipeline**

Prevent drift by checking before deployment:

```bash
#!/bin/bash
# drift-check.sh - Run before deploying to production

echo "Checking for drift in production..."

# Generate changelog from production database
docker run --rm \
  --network=liquibase_tutorial \
  -v /data/liquibase-tutorial:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.prod.properties \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  --changelog-file=/workspace/drift/prod_actual.xml \
  generateChangeLog

# Compare with expected state
diff database/changelog/changelog.xml drift/prod_actual.xml

if [ $? -ne 0 ]; then
    echo "ERROR: Drift detected in production!"
    echo "Production database has objects not in changelog."
    echo "Review drift/prod_actual.xml and resolve before deploying."
    exit 1
fi

echo "No drift detected. Safe to deploy."
```

### Real-World Drift Scenarios

**Scenario A: Emergency hotfix applied to production**

**What happened:**

- Production outage at 2am
- DBA manually adds index to fix slow query
- System recovered, incident closed
- Index not in Liquibase changelog

**Resolution:**

```sql
--changeset ops-team:document-emergency-index
-- Emergency index added during incident INC-2024-1156
-- Adding to changelog to prevent drift

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE object_id = OBJECT_ID('app.customer')
      AND name = 'IX_customer_email_emergency'
)
BEGIN
    CREATE NONCLUSTERED INDEX IX_customer_email_emergency
    ON app.customer(email)
    WHERE email IS NOT NULL;
END
ELSE
BEGIN
    PRINT 'Emergency index already exists, now tracked in changelog';
END

-- Note: Consider if this should be permanent or temporary
```

**Scenario B: Developer tested directly in dev database**

**What happened:**

- Developer creates `app.test_data` table in dev to test theory
- Forgets to drop it
- Deployment to stage fails because table exists

**Resolution:**

```sql
--changeset cleanup:remove-test-tables
-- Remove temporary test objects created outside Liquibase

DECLARE @tables TABLE (name NVARCHAR(128));
INSERT INTO @tables (name)
SELECT name FROM sys.tables
WHERE schema_id = SCHEMA_ID('app')
  AND name LIKE 'test_%'
  AND object_id NOT IN (
      -- Exclude any test tables that should exist
      SELECT object_id FROM sys.tables WHERE 0=1
  );

DECLARE @name NVARCHAR(128);
DECLARE cur CURSOR FOR SELECT name FROM @tables;
OPEN cur;
FETCH NEXT FROM cur INTO @name;

WHILE @@FETCH_STATUS = 0
BEGIN
    EXEC('DROP TABLE app.' + @name);
    PRINT 'Removed test table: app.' + @name;
    FETCH NEXT FROM cur INTO @name;
END

CLOSE cur;
DEALLOCATE cur;
```

**Scenario C: Different data in different environments**

**What happened:**

- Production has customer data
- Staging has test data
- Dev has sample data
- All should have same SCHEMA, different DATA

**Resolution:** This is expected! Liquibase manages schema, not data (usually).

```sql
--changeset yourname:add-status-column
-- Schema change: add column (same in all environments)
IF COL_LENGTH('app.customer', 'status') IS NULL
BEGIN
    ALTER TABLE app.customer ADD status NVARCHAR(50) DEFAULT 'active';
END

-- Data migration: update existing rows
-- This runs in ALL environments (prod, stage, dev)
UPDATE app.customer
SET status = 'active'
WHERE status IS NULL;

-- Environment-specific data (if needed)
-- Use contexts to run only in specific environments
```

**Best Practices for Drift Prevention:**

1. **Disable direct database access in prod** (except emergencies)
2. **Use read-only replicas for queries**
3. **Require all changes through Liquibase**
4. **Run drift detection in CI/CD**
5. **Document emergency change process**
6. **Reconcile drift weekly** (automated report)
7. **Use database change approval workflow**

### Scenario 14: Add Computed Column

```sql
--changeset yourname:add-computed-column
IF COL_LENGTH('app.customer', 'display_name') IS NULL
BEGIN
    ALTER TABLE app.customer
    ADD display_name AS (
        CASE
            WHEN email IS NOT NULL THEN full_name + ' (' + email + ')'
            ELSE full_name
        END
    ) PERSISTED;  -- PERSISTED stores value, non-persisted computes on read
END
```

### Scenario 15: Add Unique Constraint

```sql
--changeset yourname:add-unique-email
IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE object_id = OBJECT_ID('app.customer')
      AND name = 'UQ_customer_email'
)
BEGIN
    ALTER TABLE app.customer
    ADD CONSTRAINT UQ_customer_email UNIQUE (email);
END
```

### Scenario 16: Add Check Constraint

```sql
--changeset yourname:add-check-total-positive
IF NOT EXISTS (
    SELECT 1 FROM sys.check_constraints
    WHERE name = 'CK_orders_total_positive'
)
BEGIN
    ALTER TABLE app.orders
    ADD CONSTRAINT CK_orders_total_positive
    CHECK (total_amount > 0);
END
```

## Liquibase Community vs Pro Scenarios

### ✅ Community Edition Supports (All scenarios above)

- DDL changes (tables, views, indexes, constraints)
- Stored procedures, functions, triggers
- Data migrations (INSERT, UPDATE, DELETE)
- Rollbacks (with explicit SQL)
- Tags and checkpoints
- Preconditions
- Multiple environments

### ❌ Pro Edition Only

- Stored logic diff and merge
- Advanced rollback for data changes
- Targeted rollback (specific changesets)
- Quality checks (table without primary key, etc.)
- Drift detection (finding manual changes)
- Native Oracle, DB2 support

**All scenarios in this tutorial work with Community Edition!**

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
2. Create a computed column to calculate customer age from birthdate
3. Add indexes to optimize common queries (e.g., email lookups)
4. Implement soft deletes (add `deleted_at` column with index)
5. Create a view that aggregates order statistics by month
6. Migrate existing data from one format to another (e.g., normalize phone numbers)
7. Set up a GitHub Actions workflow for automated deployments
8. Practice rolling back to different tags
9. Add preconditions to prevent unsafe changes
10. Create a view that joins customers, orders, and products with aggregations

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
docker run --rm --network=liquibase_tutorial \
  -v /path/to/project:/workspace \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  update
```

**With environment variables:**

```bash
docker run --rm --network=liquibase_tutorial \
  -v /path/to/project:/workspace \
  -e DB_PASSWORD='SecurePass123!' \
  liquibase:latest \
  --defaults-file=/workspace/env/liquibase.dev.properties \
  --password="${DB_PASSWORD}" \
  update
```

**Interactive mode for debugging:**

```bash
docker run -it --rm --network=liquibase_tutorial \
  -v /path/to/project:/workspace \
  liquibase:latest \
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
| JDBC driver not found | Use `liquibase:latest` image |
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

## Cleanup After Tutorial

When you've completed the tutorial and want to clean up the containers and databases, we've provided a convenient cleanup script.

### Quick Cleanup (Recommended)

```bash
# Run the automated cleanup script
/workspaces/dbtools/docs/tutorials/liquibase/scripts/cleanup_liquibase_tutorial.sh
```

**What the script does:**

- Stops and removes the `mssql_liquibase_tutorial` container
- Removes the `mssql_liquibase_tutorial_data` volume
- Removes the `liquibase_tutorial` network
- Optionally removes the `/data/liquibase-tutorial` directory (with confirmation)
- Provides a summary of what was cleaned up

### Manual Cleanup (Alternative)

If you prefer to clean up manually:

#### Stop and Remove MSSQL Container

```bash
# Navigate to the tutorial docker directory
cd /workspaces/dbtools/docs/tutorials/liquibase/docker

# Stop and remove the SQL Server container using docker compose
docker compose down

# Verify the container is stopped and removed
docker ps -a | grep mssql_liquibase_tutorial
```

**What this does:**

- `docker compose down` - Stops and removes containers, networks, and optionally volumes
- The container `mssql_liquibase_tutorial` will be removed
- **Important:** Use `docker compose down -v` to also remove the volume (deletes all database data)

#### Remove Liquibase Container (if running)

Since Liquibase is a run-once tool, it typically doesn't leave containers running. However, if any exist:

```bash
# Remove any stopped liquibase containers
docker ps -a | grep liquibase
docker rm $(docker ps -a -q --filter "ancestor=liquibase:latest")
```

#### Remove Docker Volumes and Networks

```bash
# Remove the tutorial volume
docker volume rm mssql_liquibase_tutorial_data

# Remove the tutorial network
docker network rm liquibase_tutorial
```

### About Docker Images

**Note:** The Docker images will remain on your system even after removing the containers. This is intentional and allows you to quickly restart containers without rebuilding.

**To see the images:**

```bash
docker images | grep -E "liquibase|mssql_liquibase_tutorial"
```

**Expected output:**

```
liquibase                    latest          abc123def456   X hours ago    500MB
mssql_liquibase_tutorial     latest          def789ghi012   X hours ago    1.5GB
```

**If you want to remove the images as well (optional):**

```bash
# Remove the liquibase image (only if not used by other projects)
docker rmi liquibase:latest

# Remove the tutorial SQL Server image
docker rmi mssql_liquibase_tutorial:latest
```

**Warning:** Only remove images if you're certain you won't need them again. You'll need to rebuild them (which takes time) if you want to run the tutorial again.

### Clean Up Tutorial Files (optional)

If you want to remove the tutorial project files:

```bash
# Remove the tutorial directory
rm -rf /data/liquibase-tutorial
```

**Summary:**

- Containers: Stopped and removed with `docker compose down`
- Images: Remain on your system (can be manually removed with commands above)
- Tutorial files: Can be manually deleted from `/data/liquibase-tutorial`

## References

- Liquibase Documentation: <https://docs.liquibase.com/>
- SQL Server JDBC Driver: <https://learn.microsoft.com/sql/connect/jdbc/>
- GitHub Actions: <https://github.com/liquibase/liquibase-github-action>
- Database DevOps: <https://www.liquibase.org/blog>
- This repository structure guide: `/docs/architecture/liquibase-directory-structure.md`

---

**Congratulations!** You now understand database change management, CI/CD principles, and how to safely deploy changes across environments using Liquibase. Keep practicing, and remember: always test in dev, verify in stage, then carefully deploy to production.

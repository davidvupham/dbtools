# End-to-End Tutorial: SQL Server + Liquibase from Local Containers to GitHub Actions CI/CD

## Table of Contents

- [Who This Tutorial Is For](#who-this-tutorial-is-for)
- [How This Tutorial Relates to the Other Two](#how-this-tutorial-relates-to-the-other-two)
- [Prerequisites](#prerequisites)
- [Phase 1: Local Environment Using the Helper Scripts](#phase-1-local-environment-using-the-helper-scripts)
  - [Step 1: Run the One-Time Setup Helper](#step-1-run-the-one-time-setup-helper)
  - [Step 2: Start the Tutorial SQL Server and Liquibase Image](#step-2-start-the-tutorial-sql-server-and-liquibase-image)
  - [Step 3: Create Dev/Stage/Prod Databases and `app` Schema](#step-3-create-devstageprod-databases-and-app-schema)
  - [Step 4: Create the Liquibase Project and Baseline](#step-4-create-the-liquibase-project-and-baseline)
  - [Step 5: Deploy Baseline to All Environments](#step-5-deploy-baseline-to-all-environments)
- [Phase 2: From Local Project to GitHub Repository](#phase-2-from-local-project-to-github-repository)
  - [Step 6: Create a GitHub Repository](#step-6-create-a-github-repository)
  - [Step 7: Add Liquibase Project Files to Git](#step-7-add-liquibase-project-files-to-git)
  - [Step 8: Push the Project to GitHub](#step-8-push-the-project-to-github)
- [Phase 3: CI/CD with GitHub Actions](#phase-3-cicd-with-github-actions)
  - [Step 9: Decide Where Your Databases Live for CI/CD](#step-9-decide-where-your-databases-live-for-cicd)
  - [Step 10: Configure GitHub Secrets](#step-10-configure-github-secrets)
  - [Step 11: First CI Workflow – Deploy to Development](#step-11-first-ci-workflow--deploy-to-development)
  - [Step 12: Multi-Environment Pipeline (Dev → Staging → Production)](#step-12-multi-environment-pipeline-dev--staging--production)
- [Phase 4: Integrating Local Helper Scripts with CI/CD Practices](#phase-4-integrating-local-helper-scripts-with-cicd-practices)
  - [Step 13: Using `lb` and `sqlcmd-tutorial` Alongside GitHub Actions](#step-13-using-lb-and-sqlcmd-tutorial-alongside-github-actions)
  - [Step 14: Recommended Daily Workflow](#step-14-recommended-daily-workflow)
- [Phase 5: Best Practices and Improvements](#phase-5-best-practices-and-improvements)
  - [Security and Accounts](#security-and-accounts)
  - [Rollback and Safety](#rollback-and-safety)
  - [Drift Detection and Environments](#drift-detection-and-environments)
  - [Where to Go Deeper](#where-to-go-deeper)

---

## Who This Tutorial Is For

This tutorial is for developers and DBAs who:

- Want to **start locally** with SQL Server + Liquibase using the **helper scripts and dedicated tutorial container** from the 3-part local tutorial series.
- Then **add a proper CI/CD pipeline in GitHub Actions** that deploys those same Liquibase changes to dev/staging/production databases.

It assumes you are comfortable with basic Git and GitHub, but you can be new to Liquibase, CI/CD, and GitHub Actions.

---

## How This Tutorial Relates to the Other Tutorials

This tutorial is a 3-part series:

- [sqlserver-liquibase-part1-baseline.md](./sqlserver-liquibase-part1-baseline.md)
  - Local-only foundation: containers + helper scripts + project structure.
  - Establishes a baseline and explains core Liquibase concepts.

- [sqlserver-liquibase-part2-manual-deploy.md](./sqlserver-liquibase-part2-manual-deploy.md)
  - Local workflow for making changes and deploying manually.
  - Reinforces changeset discipline, rollback thinking, and safe iteration.

- [sqlserver-liquibase-part3-github-actions.md](./sqlserver-liquibase-part3-github-actions.md)
  - Adds CI/CD patterns and GitHub Actions concepts on top of the local project.
  - Introduces environment promotion and automation practices.

**This document (local → GitHub Actions end-to-end)** builds on those three parts and gives you a single, opinionated “start local → push to GitHub → CI/CD” flow.

If you have not run Part 1 at least once, skim it first; this tutorial will reference the same helper scripts and container setup.

---

## Prerequisites

- **Local tools**
  - Docker installed and working (`docker --version`)
  - Git installed
  - Bash shell (Linux, WSL, or macOS)
- **GitHub**
  - GitHub account
  - Ability to create repositories and configure Actions secrets
- **From the first Liquibase tutorial**
  - The helper scripts under
    `docs/tutorials/liquibase/scripts/` (for example `setup_tutorial.sh`, `cleanup_liquibase_tutorial.sh`, etc.)

> This tutorial assumes the repo containing these docs is already cloned locally and accessible via a path like `/path/to/your/repo`.

---

## Phase 1: Local Environment Using the Helper Scripts

This phase walks you through the local container + helper-script setup you’ll use throughout the rest of this tutorial.

### Step 1: Run the One-Time Setup Helper

From your cloned repo:

```bash
cd /path/to/your/repo/docs/tutorials/liquibase

# Source the one-shot setup helper (env, aliases, properties)
source scripts/setup_tutorial.sh
```

This script:

- Exports `LIQUIBASE_TUTORIAL_DIR` and (optionally) `LB_PROJECT_DIR` (default `/data/liquibase-tutorial`).
- Configures aliases like:
  - `sqlcmd-tutorial` – wrapper for `sqlcmd` into the tutorial SQL Server container.
  - `lb` – wrapper that runs the Liquibase Docker image with the right mounts, user, and properties.

You can always re-source this script in a new shell if aliases disappear.

### Step 2: Start the Tutorial SQL Server and Liquibase Image

Start the tutorial SQL Server container and Liquibase image using the helper structure:

```bash
# Start the dedicated SQL Server tutorial container
cd "$LIQUIBASE_TUTORIAL_DIR/docker"
docker compose up -d

# Verify it is running and healthy
docker ps | grep mssql_liquibase_tutorial
```

You should see `mssql_liquibase_tutorial` listening on host port `14333` and marked `(healthy)`.

**Expected output:**

```text
mssql_liquibase_tutorial   mcr.microsoft.com/mssql/server:2025-latest   Up X seconds (healthy)   0.0.0.0:14333->1433/tcp
```

**What this does:**

- Downloads the SQL Server 2022 image (if not already present).
- Creates a container named `mssql_liquibase_tutorial`.
- Starts SQL Server on port `1433` (exposed as `14333` on the host).
- Uses the password from `$MSSQL_LIQUIBASE_TUTORIAL_PWD`.
- Includes a health check so Docker reports when SQL Server is ready.

To wait for the container to become healthy, you can watch the status:

```bash
# Watch the container status (Ctrl+C to exit)
watch -n 2 'docker ps | grep mssql_liquibase_tutorial'
```

Next, build the Liquibase Docker image (if you have not already):

```bash
cd /path/to/your/repo/docker/liquibase
# Build the Liquibase Docker image used by the local helper (`lb`) and CI/CD
docker compose build

# Sanity check: run Liquibase inside the container to verify the image works
docker run --rm liquibase:latest --version
```

> The `lb` wrapper (defined as a shell alias that calls `lb.sh` in `docs/tutorials/liquibase/scripts/`) uses this image under the hood, so you do not need to remember the full `docker run` invocations or call `lb.sh` directly.

If you see `Cannot find database driver: com.microsoft.sqlserver.jdbc.SQLServerDriver`, rebuild the image from `docker/liquibase` and re-run the version check.
If an alias like `lb` is not found in a new shell, re-source the aliases script (for example `source scripts/setup_tutorial.sh` or `setup_aliases.sh`).

### Step 3: Create Dev/Stage/Prod Databases and `app` Schema

Create three databases on the tutorial SQL Server instance and the `app` schema:

```bash
# From anywhere (after sourcing setup_tutorial.sh)

# Create dev/stage/prod databases
sqlcmd-tutorial create_databases.sql
sqlcmd-tutorial verify_databases.sql

# Create the app schema in all three
sqlcmd-tutorial create_app_schema.sql
sqlcmd-tutorial verify_app_schema.sql
```

At this point you should have:

- SQL Server container: `mssql_liquibase_tutorial`
- Databases: `testdbdev`, `testdbstg`, `testdbprd`
- Shared schema: `app` in all three databases.

### Step 4: Create the Liquibase Project and Baseline

Now create the Liquibase project structure:

```bash
sudo rm -rf /data/liquibase-tutorial
mkdir -p /data/liquibase-tutorial
cd /data/liquibase-tutorial

mkdir -p database/changelog/baseline
mkdir -p database/changelog/changes
mkdir -p env
```

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

Then:

1. Populate **development** (`testdbdev`) with the tutorial objects using the provided scripts:

```bash
# Create table, view, indexes, and sample data in DEVELOPMENT
# Note: Script assumes 'app' schema already exists
sqlcmd-tutorial populate_dev_database.sql

# Verify objects were created in development
sqlcmd-tutorial verify_dev_objects.sql
sqlcmd-tutorial verify_dev_data.sql
```

1. Create `env/liquibase.dev.properties`, `env/liquibase.stage.properties`, and `env/liquibase.prod.properties`:

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

1. Generate the **baseline** changelog from dev using the `lb` helper:

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

1. Create `database/changelog/changelog.xml` that includes the baseline (and later includes incremental changes):

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

### Step 5: Deploy Baseline to All Environments

Deploy the baseline to all environments:

- **Development**: sync the baseline (no DDL executed; just mark as executed):

```bash
cd /data/liquibase-tutorial
lb -e dev -- changelogSync
lb -e dev -- tag baseline
```

- **Staging and Production**: actually deploy the baseline:

```bash
lb -e stage -- update
lb -e stage -- tag baseline

lb -e prod -- update
lb -e prod -- tag baseline
```

You now have:

- A **version-controlled project root** at `/data/liquibase-tutorial`.
- Three aligned environments (dev/stage/prod) managed by Liquibase.
- Helper commands (`lb`, `sqlcmd-tutorial`) for all local operations.

Everything up to here establishes your local baseline (dev/stage/prod databases + a Liquibase project). The rest of this document adds GitHub Actions CI/CD on top of that state.

---

## Phase 2: From Local Project to GitHub Repository

### Step 6: Create a GitHub Repository

On GitHub:

1. Click **“New repository”**.
2. Name it something like `sqlserver-liquibase-demo` or `liquibase-github-actions-demo`.
3. Choose **Private** (recommended for database projects).
4. Do **not** initialize with README or `.gitignore` (we already have them locally).

Copy the repository URL (HTTPS or SSH).

### Step 7: Add Liquibase Project Files to Git

You will now treat `/data/liquibase-tutorial` as a Git repository that you push to GitHub:

```bash
cd /data/liquibase-tutorial

git init
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git  # or SSH URL
git branch -M main
```

Create a minimal `.gitignore` if you do not already have one here:

```bash
cat > .gitignore << 'EOF'
# Liquibase local configuration (contains passwords)
liquibase.properties
env/liquibase.*.properties

# IDE files
.vscode/
.idea/
*.swp

# OS files
.DS_Store
Thumbs.db

# Liquibase runtime files
liquibase.log
*.lock

# Local databases or temp files
*.db
*.sqlite
EOF
```

Then add the project files:

```bash
git add database env .gitignore README.md 2>/dev/null || true
git add database env .gitignore

git commit -m "Initial commit: Liquibase SQL Server tutorial project"
```

> Keep **passwords and environment-specific properties out of Git**. CI/CD will use GitHub Secrets instead.

### Step 8: Push the Project to GitHub

```bash
git push -u origin main
```

Verify on GitHub that you see:

- `database/changelog/...`
- `env/` (without hard-coded passwords; use environment variables or secrets rather than committing passwords)
- `.gitignore` and `README.md`.

---

## Phase 3: CI/CD with GitHub Actions (Self-Hosted Runner in Docker)

This phase adapts the CI/CD structure from `sqlserver-liquibase-github-actions-tutorial.md`, but assumes you are running a **self-hosted GitHub Actions runner inside a Docker container** on the same Docker network as your tutorial SQL Server container.

### Step 9: Where the Databases Live for CI/CD

For this combined tutorial we will:

- Use the **existing tutorial SQL Server container** `mssql_liquibase_tutorial` as the CI/CD target for dev/stage/prod.
- Run the GitHub Actions **runner itself in a Docker container**, attached to the same Docker network (for example `liquibase_tutorial`).
- Use JDBC URLs that point at `mssql_liquibase_tutorial:1433` (inside the Docker network), not at a public cloud endpoint.

> In real production you would typically move the databases to managed services (Azure SQL, RDS SQL Server, etc.) and use GitHub-hosted runners. The self-hosted runner in Docker is ideal for learning and for private environments that GitHub-hosted runners cannot reach.

### Step 9a: Set Up a Self-Hosted Runner in a Docker Container

1. **Create a personal access token (PAT)** (once per machine) with at least `repo` scope, following GitHub’s “self-hosted runner” instructions.
2. **Create a registration token** for the runner from your repo’s **Settings → Actions → Runners → New self-hosted runner** page.
3. **Create a Docker network if you do not already have one shared with the tutorial containers** (this tutorial uses `liquibase_tutorial`):

```bash
docker network create liquibase_tutorial 2>/dev/null || true
```

1. Ensure your `mssql_liquibase_tutorial` container is attached to that network (it should be if you followed the first tutorial’s `docker compose` file).

2. **Run a self-hosted runner container** attached to the same network. One common pattern is to use the official Actions runner image and environment variables:

```bash
docker run -d --restart unless-stopped \
  --name liquibase-actions-runner \
  --network liquibase_tutorial \
  -e REPO_URL="https://github.com/YOUR_ORG/YOUR_REPO" \
  -e RUNNER_NAME="liquibase-tutorial-runner" \
  -e RUNNER_WORKDIR="/runner/_work" \
  -e RUNNER_LABELS="self-hosted,liquibase-tutorial" \
  -e RUNNER_TOKEN="YOUR_REGISTRATION_TOKEN" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  ghcr.io/actions/actions-runner:latest
```

Key points:

- The runner container joins the **same Docker network** as `mssql_liquibase_tutorial`.
- The **label** `liquibase-tutorial` lets you target this runner from workflows.
- Mounting `/var/run/docker.sock` is optional if you need the runner to start other containers; for basic Liquibase CLI use you can omit it.

1. In the Actions UI, you should now see a **self-hosted runner** registered for your repo with labels like `self-hosted`, `linux`, and `liquibase-tutorial`.

### Step 10: Configure GitHub Secrets

In your new Liquibase repo on GitHub:

1. Go to **Settings → Secrets and variables → Actions**.
2. Add the following **repository secrets** (matching the three environments you created in Phase 1, but pointing at real CI/CD databases):

For each environment (dev, stage, prod):

- `DEV_DB_URL`, `DEV_DB_USERNAME`, `DEV_DB_PASSWORD`
- `STAGE_DB_URL`, `STAGE_DB_USERNAME`, `STAGE_DB_PASSWORD`
- `PROD_DB_URL`, `PROD_DB_USERNAME`, `PROD_DB_PASSWORD`

These `*_DB_PASSWORD` secrets will be mapped into the **same environment variable** used by the local tutorial helpers, `MSSQL_LIQUIBASE_TUTORIAL_PWD`, so local commands and CI/CD follow the same pattern.

Example JDBC URLs (adapt from the GitHub Actions tutorial):

- Azure SQL:

```text
jdbc:sqlserver://dev-sql.database.windows.net:1433;
  databaseName=myapp_dev;
  encrypt=true;
  trustServerCertificate=false;
  loginTimeout=30;
  connectRetryCount=3;
```

- Local tutorial SQL Server (for the self-hosted runner in Docker):

```text
jdbc:sqlserver://mssql_liquibase_tutorial:1433;
  databaseName=testdbdev;
  encrypt=true;
  trustServerCertificate=true;
  loginTimeout=30;
```

> For actual production, avoid using `sa`; create a dedicated **Liquibase service account** with only the permissions it needs (described in [Phase 5](#security-and-accounts)).

### Step 11: First CI Workflow – Deploy to Development (Self-Hosted)

Create `.github/workflows/deploy-dev.yml` in your repo with a minimal workflow that targets the self-hosted runner container:

```yaml
name: Deploy to Development

on:
  push:
    branches:
      - main
    paths:
      - 'database/**'
  workflow_dispatch:

jobs:
  deploy-dev:
    name: Deploy to Development Database
    runs-on: self-hosted
    labels: [ liquibase-tutorial ]

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Java
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '11'

      - name: Set up Liquibase
        uses: liquibase/setup-liquibase@v2
        with:
          version: '4.32.0'
          edition: 'oss'

      - name: Deploy database changes to DEV
        env:
          # Map GitHub secret into the same env var used by local helper scripts
          MSSQL_LIQUIBASE_TUTORIAL_PWD: ${{ secrets.DEV_DB_PASSWORD }}
        run: |
          liquibase update \
            --changelog-file=database/changelog/changelog.xml \
            --url="${{ secrets.DEV_DB_URL }}" \
            --username="${{ secrets.DEV_DB_USERNAME }}" \
            --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}"

      - name: Show deployment history
        env:
          MSSQL_LIQUIBASE_TUTORIAL_PWD: ${{ secrets.DEV_DB_PASSWORD }}
        run: |
          liquibase history \
            --changelog-file=database/changelog/changelog.xml \
            --url="${{ secrets.DEV_DB_URL }}" \
            --username="${{ secrets.DEV_DB_USERNAME }}" \
            --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}"
```

Commit and push:

```bash
git add .github/workflows/deploy-dev.yml
git commit -m "Add initial GitHub Actions workflow for DEV deployment"
git push
```

On GitHub:

- Go to the **Actions** tab and watch the “Deploy to Development” workflow run on your next push.

### Step 12: Multi-Environment Pipeline (Dev → Staging → Production)

Now replace the single-env workflow with a pipeline similar to the one in `sqlserver-liquibase-github-actions-tutorial.md`, but still targeting the self-hosted runner container.

Create `.github/workflows/deploy-pipeline.yml`:

```yaml
name: Database Deployment Pipeline

on:
  push:
    branches:
      - main
    paths:
      - 'database/**'
  workflow_dispatch:

jobs:
  deploy-dev:
    name: Deploy to Development
    runs-on: self-hosted
    labels: [ liquibase-tutorial ]
    environment: development

    steps:
      - uses: actions/checkout@v4

      - name: Set up Java
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '11'

      - name: Set up Liquibase
        uses: liquibase/setup-liquibase@v2
        with:
          version: '4.32.0'
          edition: 'oss'

      - name: Deploy to development
        env:
          MSSQL_LIQUIBASE_TUTORIAL_PWD: ${{ secrets.DEV_DB_PASSWORD }}
        run: |
          liquibase update \
            --changelog-file=database/changelog/changelog.xml \
            --url="${{ secrets.DEV_DB_URL }}" \
            --username="${{ secrets.DEV_DB_USERNAME }}" \
            --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}"

      - name: Verify dev deployment
        env:
          MSSQL_LIQUIBASE_TUTORIAL_PWD: ${{ secrets.DEV_DB_PASSWORD }}
        run: |
          liquibase status --verbose \
            --changelog-file=database/changelog/changelog.xml \
            --url="${{ secrets.DEV_DB_URL }}" \
            --username="${{ secrets.DEV_DB_USERNAME }}" \
            --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}"

  deploy-staging:
    name: Deploy to Staging
    runs-on: self-hosted
    labels: [ liquibase-tutorial ]
    needs: deploy-dev
    environment: staging

    steps:
      - uses: actions/checkout@v4

      - name: Set up Java
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '11'

      - name: Set up Liquibase
        uses: liquibase/setup-liquibase@v2
        with:
          version: '4.32.0'
          edition: 'oss'

      - name: Deploy to staging
        env:
          MSSQL_LIQUIBASE_TUTORIAL_PWD: ${{ secrets.STAGE_DB_PASSWORD }}
        run: |
          liquibase update \
            --changelog-file=database/changelog/changelog.xml \
            --url="${{ secrets.STAGE_DB_URL }}" \
            --username="${{ secrets.STAGE_DB_USERNAME }}" \
            --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}"

  deploy-production:
    name: Deploy to Production
    runs-on: self-hosted
    labels: [ liquibase-tutorial ]
    needs: deploy-staging
    environment: production   # configure approvals & branches in GitHub Environments

    steps:
      - uses: actions/checkout@v4

      - name: Set up Java
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '11'

      - name: Set up Liquibase
        uses: liquibase/setup-liquibase@v2
        with:
          version: '4.32.0'
          edition: 'oss'

      - name: Deploy to production
        env:
          MSSQL_LIQUIBASE_TUTORIAL_PWD: ${{ secrets.PROD_DB_PASSWORD }}
        run: |
          liquibase update \
            --changelog-file=database/changelog/changelog.xml \
            --url="${{ secrets.PROD_DB_URL }}" \
            --username="${{ secrets.PROD_DB_USERNAME }}" \
            --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}"

      - name: Tag production deployment
        env:
          MSSQL_LIQUIBASE_TUTORIAL_PWD: ${{ secrets.PROD_DB_PASSWORD }}
        run: |
          liquibase tag "release-${{ github.run_number }}" \
            --changelog-file=database/changelog/changelog.xml \
            --url="${{ secrets.PROD_DB_URL }}" \
            --username="${{ secrets.PROD_DB_USERNAME }}" \
            --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}"
```

Then:

1. In GitHub, configure **Environments** (`development`, `staging`, `production`) under **Settings → Environments**.
2. For `production`, require:
   - At least one **required reviewer**.
   - (Optionally) a **wait timer** (for example 5 minutes).
3. Commit and push `deploy-pipeline.yml`.

You now have a pipeline that:

- Runs on pushes to `main` that touch `database/**`.
- Deploys in order: dev → stage → prod.
- Uses GitHub Environment protection rules for production approvals.
- Executes entirely on your **self-hosted runner container**, which talks to the `mssql_liquibase_tutorial` SQL Server container over the shared `liquibase_tutorial` Docker network.

> To adapt this pipeline later for a cloud SQL Server and GitHub-hosted runners, change `runs-on` back to `ubuntu-latest` and update the JDBC URLs and secrets to point at your cloud databases.

---

## Phase 4: Integrating Local Helper Scripts with CI/CD Practices

### Step 13: Using `lb` and `sqlcmd-tutorial` Alongside GitHub Actions

Even after you add CI/CD, the helper scripts in this tutorial remain extremely valuable:

- **`lb` wrapper**
  - Local “single command” runner for Liquibase against `testdbdev`, `testdbstg`, `testdbprd`.
  - Mirrors the same `changelog.xml` that CI/CD uses.
  - Perfect for:
    - Trying new changesets quickly.
    - Running `status`, `updateSQL`, or `rollback` locally.

- **`sqlcmd-tutorial`**
  - Convenient way to inspect schema and data in the tutorial SQL Server container.
  - Lets you verify what CI/CD is doing by reproducing operations locally.

> Best practice: treat the **local helper scripts + tutorial container** as your **sandbox** and GitHub Actions + real SQL Server as your **pipeline**. Both should always use the **same changelog and changeset discipline**.

### Step 14: Recommended Daily Workflow

1. **Create or modify a changeset locally**
   - Edit `database/changelog/changes/V00xx__description.sql`.
   - Update `changelog.xml` (using the XML wrapper + `<sqlFile>` + `<rollback>` pattern from the first tutorial).

2. **Test locally with helper scripts**
   - Use `lb -e dev -- status --verbose`, `lb -e dev -- update`, `lb -e dev -- rollback ...`.
   - Use `sqlcmd-tutorial` to inspect results.

3. **Commit and push**
   - `git add database/changelog`
   - `git commit -m "Describe your change"`
   - `git push origin main` or open a PR.

4. **CI/CD takes over**
   - GitHub Actions pipeline validates and deploys through dev → stage → prod.
   - Production deployments require approval via the `production` environment.

5. **If something goes wrong**

- Use the rollback guidance in [sqlserver-liquibase-part2-manual-deploy.md](./sqlserver-liquibase-part2-manual-deploy.md) and [sqlserver-liquibase-part3-github-actions.md](./sqlserver-liquibase-part3-github-actions.md).

---

## Phase 5: Best Practices and Improvements

This section summarizes best practices and tightens a few areas so the end-to-end flow is safer and more consistent.

### Security and Accounts

- **Avoid `sa` for anything beyond tutorials**
  - For the tutorial container, using `sa` is acceptable.
  - For CI/CD (especially production), create a **service account**:
    - Minimal required permissions (DDL but not `sysadmin`).
    - Rotation policy for its password.
    - Stored only in GitHub Secrets / Vault, never in Git.

- **Secret hygiene**
  - Keep `liquibase.properties` and environment-specific property files out of Git.
  - Use GitHub Secrets (and environment secrets where appropriate).
  - Never echo secrets to logs in Actions.

### Rollback and Safety

- Prefer **tag-based rollbacks** for releases and use **count/date** only when you understand the implications.
- Always define explicit `<rollback>` blocks in `changelog.xml` when you use SQL files.
- For destructive operations (drop table/column), use **two-phase migrations** and document in comments that data cannot be restored.

### Drift Detection and Environments

- Use the `diff` and `diffChangeLog` commands to:
  - Detect manual changes in dev/stage/prod.
  - Reverse-engineer drift into proper changesets when appropriate.
  - Clean up or formalize hotfixes done under pressure.

- Never skip the **dev → staging → production** promotion path:
  - CI/CD should mirror your manual promotion process (dev → stage → prod).
  - Production workflows should always be gated by approvals and/or scheduled windows.

### Where to Go Deeper

For more detail on any single area:

- **Local architecture, rollback strategies, drift detection, and advanced change scenarios**
  See [sqlserver-liquibase-part1-baseline.md](./sqlserver-liquibase-part1-baseline.md) for the local baseline setup.

- **Cloud-facing GitHub Actions workflows, environment protection, and secrets**
  See `sqlserver-liquibase-github-actions-tutorial.md`.

This tutorial is designed to be your **end-to-end “happy path”**: start with the containerized helper-based environment, build a robust Liquibase project, and then wire it into a production-grade GitHub Actions pipeline.

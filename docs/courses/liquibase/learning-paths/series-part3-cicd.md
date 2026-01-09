# Tutorial Part 3: From Local Liquibase Project to GitHub Actions CI/CD

## Table of Contents

- [Prerequisites](#prerequisites)
- [Phase 2: From Local Project to GitHub Repository](#phase-2-from-local-project-to-github-repository)
  - [Step 6: Create a GitHub Repository](#step-6-create-a-github-repository)
  - [Step 7: Initialize Git and Push Initial Project (First Person Only)](#step-7-initialize-git-and-push-initial-project-first-person-only)
  - [Step 8: Create Your Personal Branch (All Learners)](#step-8-create-your-personal-branch-all-learners)
- [Phase 3: CI/CD with GitHub Actions (Self-Hosted Runner in Docker)](#phase-3-cicd-with-github-actions-self-hosted-runner-in-docker)
  - [Step 9: Where the Databases Live for CI/CD](#step-9-where-the-databases-live-for-cicd)
  - [Step 10: Set Up a Self-Hosted Runner in a Docker Container](#step-10-set-up-a-self-hosted-runner-in-a-docker-container)
  - [Step 11: Configure GitHub Secrets](#step-11-configure-github-secrets)
  - [Step 12: First CI Workflow – Deploy to Development (Self-Hosted)](#step-12-first-ci-workflow--deploy-to-development-self-hosted)
  - [Step 13: Multi-Environment Pipeline (Dev → Stg → Prd)](#step-13-multi-environment-pipeline-dev--stg--prd)
- [Phase 4: Integrating Local Helper Scripts with CI/CD Practices](#phase-4-integrating-local-helper-scripts-with-cicd-practices)
  - [Step 14: Using lb and sqlcmd-tutorial Alongside GitHub Actions](#step-14-using-lb-and-sqlcmd-tutorial-alongside-github-actions)
  - [Step 15: Recommended Daily Workflow (Branch-Based)](#step-15-recommended-daily-workflow-branch-based)
- [Phase 5: Best Practices and Improvements](#phase-5-best-practices-and-improvements)

## Prerequisites

- Complete **Part 1: Baseline SQL Server + Liquibase Setup** (`series-part1-baseline.md`).
- (Recommended) Complete **Part 2: Manual Liquibase Deployment Lifecycle** (`series-part2-manual.md`) so you are comfortable deploying and rolling back changes manually before automating them.

This Part 3 assumes you already have:

- A local Liquibase project at `$LIQUIBASE_TUTORIAL_DATA_DIR` with:
  - `database/changelog/baseline/V0000__baseline.mssql.sql`
  - `database/changelog/changelog.xml` that includes the baseline and any subsequent changes
  - `env/liquibase.dev.properties`, `env/liquibase.stg.properties`, `env/liquibase.prd.properties`
- Baseline deployed to dev/stg/prd and tagged appropriately (for example `baseline`, `release-v1.x`).

From here, this tutorial focuses only on:

- Moving the project into Git and pushing to GitHub.
- Configuring secrets and runners.
- Defining GitHub Actions workflows to deploy the same changelog to dev/stg/prd.
- Integrating local helper scripts with CI/CD best practices.

The sections and content below mirror the **Phase 2+** material from the original combined tutorial.

## Phase 2: From Local Project to GitHub Repository

### Step 6: Create a GitHub Repository

> **Multi-User Tutorial Setup:**
> This tutorial assumes a **branch-based approach** where multiple people share one repository and each person works in their own branch.
>
> **Setup for branch-based tutorials:**
>
> - One instructor or first learner creates the base repository
> - Each subsequent learner will be added as a collaborator
> - Each person creates their own feature branch (e.g., `tutorial-alice`, `tutorial-bob`)
> - Workflows trigger on individual branches, not `main`
> - GitHub Secrets can be shared across all learners
>
> **Alternative approaches** (not covered in detail here):
>
> - **Fork-based**: Each learner forks the repo to their own account
> - **Separate repositories**: Each person creates their own uniquely-named repo

**If you are the first person or instructor:**

On GitHub:

1. Click **"New repository"**.
2. Name it `sqlserver-liquibase-demo` or `liquibase-github-actions-demo`.
3. Choose **Private** (recommended for database projects).
4. Do **not** initialize with README or `.gitignore` (we already have them locally).
5. After creating the repo, add collaborators:
   - Go to **Settings → Collaborators**
   - Add each learner by their GitHub username

**If you are joining an existing tutorial repo:**

1. Accept the collaboration invitation email from GitHub
2. Clone the repository:

   ```bash
   # Clone to your data directory
   # Replace ORG_NAME with your GitHub organization or username
   git clone https://github.com/ORG_NAME/sqlserver-liquibase-demo.git "$LIQUIBASE_TUTORIAL_DATA_DIR"
   cd "$LIQUIBASE_TUTORIAL_DATA_DIR"
   ```

3. Skip to **Step 8** to create your personal branch

### Step 7: Initialize Git and Push Initial Project (First Person Only)

**If you are the first person setting up the repository:**

Treat your Liquibase project directory as a Git repository:

```bash
cd "$LIQUIBASE_TUTORIAL_DATA_DIR"

git init
# Replace ORG_NAME with your GitHub organization or username
git remote add origin https://github.com/ORG_NAME/sqlserver-liquibase-demo.git
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

Push to GitHub:

```bash
git push -u origin main
```

Verify on GitHub that you see:

- `database/changelog/...`
- `env/` (without hard-coded passwords; use environment variables or secrets rather than committing passwords)
- `.gitignore` and `README.md`

#### Important: Protect the main branch

On GitHub:

1. Go to **Settings → Branches**
2. Add a branch protection rule for `main`:
   - Require pull request reviews before merging (optional for tutorials)
   - Restrict who can push (recommend: only the instructor/first person)

This prevents accidental pushes to `main` from learners.

### Step 8: Create Your Personal Branch (All Learners)

**Everyone (including the first person) should now create a personal branch:**

```bash
cd "$LIQUIBASE_TUTORIAL_DATA_DIR"

# Replace 'yourname' with your actual name or initials
export TUTORIAL_USER="yourname"  # e.g., alice, bob, dvp

git checkout -b "tutorial-${TUTORIAL_USER}"
git push -u origin "tutorial-${TUTORIAL_USER}"
```

From now on, **all your work happens in your personal branch**, not in `main`.

---

## Phase 3: CI/CD with GitHub Actions (Self-Hosted Runner in Docker)

This phase adapts the CI/CD structure from the earlier GitHub Actions tutorial, but assumes you are running a **self-hosted GitHub Actions runner inside a Docker container** on the same Docker network as your tutorial SQL Server container.

### Step 9: Where the Databases Live for CI/CD

For this combined tutorial we will:

- Use the **existing tutorial SQL Server containers** (`mssql_dev`, `mssql_stg`, `mssql_prd`) as the CI/CD targets.
- Run the GitHub Actions **runner itself in a Docker container**, attached to the host network or connected to the SQL Server containers.
- Use JDBC URLs that point to the appropriate container (e.g., `mssql_dev:1433`, `mssql_stg:1433`, `mssql_prd:1433` when inside Docker, or `localhost:PORT` when using host networking).

> **Note:** Part 1 creates three separate SQL Server containers on different ports. For CI/CD with self-hosted runners, you'll configure secrets to connect to each environment's container. The self-hosted runner in Docker is ideal for learning.

### Step 10: Set Up a Self-Hosted Runner in a Docker Container

> **If you already completed this:** If you followed README.md "Path 4: Self-Hosted Runner" and set up your runner environment, you can skip this step—just verify your runner shows as "Online" in GitHub Settings → Actions → Runners.
>
> **Execution timing:** Complete the actions below now (before pushing any workflow files in Steps 12–13). The runner must be online and your secrets defined or initial workflow runs will queue indefinitely. If you are only reading ahead, you may delay the runner start until just before adding `.github/workflows`, but do not push workflow YAML until the runner shows as "Online" in GitHub.
>
> **Detailed guide:** For comprehensive setup instructions including Docker/WSL installation, see [Self-Hosted GitHub Actions Runners Guide](./guide-runner-setup.md).

- [ ] **Create a personal access token (PAT)** (once per machine) with at least `repo` scope, following GitHub's "self-hosted runner" instructions.
- [ ] **Create a registration token** for the runner from your repo’s **Settings → Actions → Runners → New self-hosted runner** page. (This short‑lived token is different from the PAT and is used only during runner registration.)
- [ ] **Create a Docker network** if you do not already have one shared with the tutorial containers (this tutorial uses `liquibase_tutorial`):

   ```bash
   #!/usr/bin/env bash
   # Idempotent network creation: only create if absent
   if ! docker network inspect liquibase_tutorial >/dev/null 2>&1; then
     docker network create liquibase_tutorial
     echo "Created docker network liquibase_tutorial"
   else
     echo "Docker network liquibase_tutorial already exists"
   fi
   ```

- [ ] **Ensure your SQL Server containers are accessible** (they should be if you followed Part 1's `docker compose` file). The containers `mssql_dev`, `mssql_stg`, and `mssql_prd` should be running on ports defined by `MSSQL_DEV_PORT`, `MSSQL_STG_PORT`, and `MSSQL_PRD_PORT` (defaults: 14331, 14332, 14333).

- [ ] **Run a self-hosted runner container** attached to the same network. One common pattern is to use the official Actions runner image and environment variables:

   ```bash
   # Replace placeholders before running:
   # - ORG_NAME: Your GitHub organization or username
   # - YOUR_REGISTRATION_TOKEN: Token from GitHub Settings → Actions → Runners → New self-hosted runner
   docker run -d --restart unless-stopped \
     --name liquibase-actions-runner \
     --network liquibase_tutorial \
     -e REPO_URL="https://github.com/ORG_NAME/sqlserver-liquibase-demo" \
     -e RUNNER_NAME="liquibase-tutorial-runner" \
     -e RUNNER_WORKDIR="/runner/_work" \
     -e RUNNER_LABELS="self-hosted,liquibase-tutorial" \
     -e RUNNER_TOKEN="YOUR_REGISTRATION_TOKEN" \
     -v /var/run/docker.sock:/var/run/docker.sock \
     ghcr.io/actions/actions-runner:latest
   ```

   **Important:** Replace the placeholders:
   - `ORG_NAME`: Your GitHub organization or username hosting the repository
   - `YOUR_REGISTRATION_TOKEN`: The registration token from GitHub (Settings → Actions → Runners → New self-hosted runner)

   Note: Remove the docker.sock mount if the runner does not need to start other containers.

Key points:

- The runner container should have network access to your SQL Server containers (either via host network or Docker networking).
- The **label** `liquibase-tutorial` lets you target this runner from workflows.
- Mounting `/var/run/docker.sock` is optional if you need the runner to start other containers; for basic Liquibase CLI use you can omit it.
- After it starts, in the Actions UI you should see a **self-hosted runner** registered with labels like `self-hosted`, `linux`, and `liquibase-tutorial`. Only proceed to add workflow YAML files once it appears as Online.

#### Quick Setup Alternative

If you prefer to set up the runner now without all the detail, follow the comprehensive guide: **[Self-Hosted GitHub Actions Runners Guide](./guide-runner-setup.md)**

That guide covers Docker/WSL installation, SQL Server setup, runner configuration, network connectivity, and troubleshooting.

#### Verification Checklist

Before proceeding to Step 11, verify:

- [ ] **SQL Server containers** `mssql_dev`, `mssql_stg`, and `mssql_prd` are running
- [ ] **Runner container** is running and can access the SQL Server ports
- [ ] **GitHub shows runner as "Online"** in Settings → Actions → Runners
- [ ] Runner has appropriate labels (e.g., `self-hosted`, `liquibase-tutorial`)

**Test connectivity:**

```bash
# Verify containers are running
docker ps | grep mssql_

# Check runner logs
docker logs <your-runner-container-name> | tail -20
```

Once your runner shows as **Online** in GitHub, proceed to Step 11.

### Step 11: Configure GitHub Secrets

In your new Liquibase repo on GitHub:

1. Go to **Settings → Secrets and variables → Actions**.
2. Add the following **repository secrets** (matching the three environments you created in Part 1, but pointing at real CI/CD databases or your tutorial SQL Server):

For each environment (dev, stg, prd):

- `DEV_DB_URL`, `DEV_DB_USERNAME`, `DEV_DB_PASSWORD`
- `STG_DB_URL`, `STG_DB_USERNAME`, `STG_DB_PASSWORD`
- `PRD_DB_URL`, `PRD_DB_USERNAME`, `PRD_DB_PASSWORD`

These `*_DB_PASSWORD` secrets will be mapped into the **same environment variable** used by the local tutorial helpers, `MSSQL_LIQUIBASE_TUTORIAL_PWD`, so the pattern from Part 1 stays consistent between local commands and CI/CD.

Example JDBC URLs:

- Azure SQL:

```text
jdbc:sqlserver://dev-sql.database.windows.net:1433;
  databaseName=myapp_dev;
  encrypt=true;
  trustServerCertificate=false;
  loginTimeout=30;
  connectRetryCount=3;
```

- Local tutorial SQL Server (for the self-hosted runner):

```text
# DEV environment (mssql_dev container)
# Note: Replace the port number (14331) with your actual MSSQL_DEV_PORT value
jdbc:sqlserver://localhost:14331;
  databaseName=orderdb;
  encrypt=true;
  trustServerCertificate=true;
  loginTimeout=30;

# STG environment (mssql_stg container)
# Note: Replace the port number (14332) with your actual MSSQL_STG_PORT value
jdbc:sqlserver://localhost:14332;
  databaseName=orderdb;
  encrypt=true;
  trustServerCertificate=true;
  loginTimeout=30;

# PRD environment (mssql_prd container)
# Note: Replace the port number (14333) with your actual MSSQL_PRD_PORT value
jdbc:sqlserver://localhost:14333;
  databaseName=orderdb;
  encrypt=true;
  trustServerCertificate=true;
  loginTimeout=30;
```

> For actual production, avoid using `sa`; create a dedicated **Liquibase service account** with only the permissions it needs (see the best practices section below).

### Step 12: First CI Workflow – Deploy to Development (Self-Hosted)

Create `.github/workflows/deploy-dev.yml` in your repo with a minimal workflow that targets the self-hosted runner container:

> **Branch-based trigger:** This workflow triggers on pushes to branches matching `tutorial-*`, so each learner's branch will trigger their own deployments.

```yaml
name: Deploy to Development

on:
  push:
    branches:
      - 'tutorial-*'  # Triggers on all tutorial branches
    paths:
      - 'database/**'
  workflow_dispatch:

jobs:
  deploy-dev:
    name: Deploy to Development Database
    runs-on: [self-hosted, liquibase-tutorial]

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

### Step 13: Multi-Environment Pipeline (Dev → Stg → Prd)

Now replace the single-env workflow with a pipeline that promotes changes through dev → stg → prd.

Create `.github/workflows/deploy-pipeline.yml`:

> **Branch-based trigger:** Each learner's branch triggers their own pipeline execution.

```yaml
name: Database Deployment Pipeline

on:
  push:
    branches:
      - 'tutorial-*'  # Triggers on all tutorial branches
    paths:
      - 'database/**'
  workflow_dispatch:

jobs:
  deploy-dev:
    name: Deploy to Development
    runs-on: [self-hosted, liquibase-tutorial]
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
    runs-on: [self-hosted, liquibase-tutorial]
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
          MSSQL_LIQUIBASE_TUTORIAL_PWD: ${{ secrets.STG_DB_PASSWORD }}
        run: |
          liquibase update \
            --changelog-file=database/changelog/changelog.xml \
            --url="${{ secrets.STG_DB_URL }}" \
            --username="${{ secrets.STG_DB_USERNAME }}" \
            --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}"

  deploy-production:
    name: Deploy to Production
    runs-on: [self-hosted, liquibase-tutorial]
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
          MSSQL_LIQUIBASE_TUTORIAL_PWD: ${{ secrets.PRD_DB_PASSWORD }}
        run: |
          liquibase update \
            --changelog-file=database/changelog/changelog.xml \
            --url="${{ secrets.PRD_DB_URL }}" \
            --username="${{ secrets.PRD_DB_USERNAME }}" \
            --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}"

      - name: Tag production deployment
        env:
          MSSQL_LIQUIBASE_TUTORIAL_PWD: ${{ secrets.PRD_DB_PASSWORD }}
        run: |
          liquibase tag "release-${{ github.run_number }}" \
            --changelog-file=database/changelog/changelog.xml \
            --url="${{ secrets.PRD_DB_URL }}" \
            --username="${{ secrets.PRD_DB_USERNAME }}" \
            --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}"
```

Then:

1. In GitHub, configure **Environments** (`development`, `staging`, `production`) under **Settings → Environments**.
2. For `production`, require:
   - At least one **required reviewer**.
   - (Optionally) a **wait timer** (for example 5 minutes).
3. Commit and push `deploy-pipeline.yml`.

You now have a pipeline that:

- Runs on pushes to any tutorial branch (`tutorial-*`) that touch `database/**`.
- Deploys in order: dev → stg → prd.
- Uses GitHub Environment protection rules for production approvals.
- Executes entirely on your **self-hosted runner container**, which talks to the `mssql_dev`, `mssql_stg`, and `mssql_prd` SQL Server containers over the shared Docker network.

> To adapt this pipeline later for a cloud SQL Server and GitHub-hosted runners, change `runs-on` back to `ubuntu-latest` and update the JDBC URLs and secrets to point at your cloud databases.

---

## Phase 4: Integrating Local Helper Scripts with CI/CD Practices

### Step 14: Using `lb` and `sqlcmd-tutorial` Alongside GitHub Actions

Even after you add CI/CD, the helper scripts from Part 1 remain extremely valuable:

- **`lb` wrapper**
  - Local "single command" runner for Liquibase against dev, stg, and prd environments (all using the `orderdb` database).
  - Mirrors the same `changelog.xml` that CI/CD uses.
  - Perfect for:
    - Trying new changesets quickly.
    - Running `status`, `updateSQL`, or `rollback` locally.

- **`sqlcmd-tutorial`**
  - Convenient way to inspect schema and data in the tutorial SQL Server container.
  - Lets you verify what CI/CD is doing by reproducing operations locally.

> Best practice: treat the **local helper scripts + tutorial container** as your **sandbox** and GitHub Actions + real SQL Server as your **pipeline**. Both should always use the **same changelog and changeset discipline**.
>
> **In the branch-based approach:** Each learner works independently in their own branch. Your local testing and CI/CD both operate on your personal `tutorial-yourname` branch.

### Step 15: Recommended Daily Workflow (Branch-Based)

1. **Create or modify a changeset locally**
   - Edit `database/changelog/changes/V00xx__description.sql`.
   - Update `changelog.xml` (using the XML wrapper + `<sqlFile>` + `<rollback>` pattern from the manual tutorial).

2. **Test locally with helper scripts**
   - Use `lb -e dev -- status --verbose`, `lb -e dev -- update`, `lb -e dev -- rollback ...`.
   - Use `sqlcmd-tutorial` to inspect results.

3. **Commit and push to your personal branch**

   ```bash
   git add database/changelog
   git commit -m "V00xx: Describe your change"
   git push origin "tutorial-${TUTORIAL_USER}"
   ```

4. **CI/CD takes over**
   - GitHub Actions pipeline validates and deploys through dev → stage → prod.
   - Production deployments require approval via the `production` environment.
   - **Each learner's workflow runs independently** based on their branch.

5. **If something goes wrong**
   - Use the rollback strategies and workflows from the more detailed GitHub Actions tutorial and from the rollback section in the manual Liquibase tutorial.

6. **(Optional) Merge to main after successful deployment**
   - After your changeset successfully deploys to production in your branch pipeline:

   ```bash
   # Create a pull request from your branch to main
   gh pr create --base main --head "tutorial-${TUTORIAL_USER}" \
     --title "Changeset V00xx: Description" \
     --body "Tested and deployed successfully in my tutorial branch"
   ```

   - This keeps `main` as a clean record of all validated changes from all learners.

---

## Phase 5: Best Practices and Improvements

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

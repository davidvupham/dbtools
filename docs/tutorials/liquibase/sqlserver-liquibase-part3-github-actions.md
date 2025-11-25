# Tutorial Part 3: From Local Liquibase Project to GitHub Actions CI/CD

> **Prerequisites**
> - Complete **Part 1: Baseline SQL Server + Liquibase Setup** (`sqlserver-liquibase-part1-baseline.md`).
> - (Recommended) Complete **Part 2: Manual Liquibase Deployment Lifecycle** (`sqlserver-liquibase-part2-manual-deploy.md`) so you are comfortable deploying and rolling back changes manually before automating them.

This Part 3 assumes you already have:

- A local Liquibase project at `/data/liquibase-tutorial` with:
  - `database/changelog/baseline/V0000__baseline.xml`
  - `database/changelog/changelog.xml` that includes the baseline and any subsequent changes
  - `env/liquibase.dev.properties`, `env/liquibase.stage.properties`, `env/liquibase.prod.properties`
- Baseline deployed to dev/stage/prod and tagged appropriately (for example `baseline`, `release-v1.x`).

From here, this tutorial focuses only on:

- Moving the project into Git and pushing to GitHub.
- Configuring secrets and runners.
- Defining GitHub Actions workflows to deploy the same changelog to dev/stage/prod.
- Integrating local helper scripts with CI/CD best practices.

The sections and content below mirror the **Phase 2+** material from the original combined tutorial.

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

This phase adapts the CI/CD structure from the earlier GitHub Actions tutorial, but assumes you are running a **self-hosted GitHub Actions runner inside a Docker container** on the same Docker network as your tutorial SQL Server container.

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

4. Ensure your `mssql_liquibase_tutorial` container is attached to that network (it should be if you followed the first tutorial’s `docker compose` file).
5. **Run a self-hosted runner container** attached to the same network. One common pattern is to use the official Actions runner image and environment variables:

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

6. In the Actions UI, you should now see a **self-hosted runner** registered for your repo with labels like `self-hosted`, `linux`, and `liquibase-tutorial`.

### Step 10: Configure GitHub Secrets

In your new Liquibase repo on GitHub:

1. Go to **Settings → Secrets and variables → Actions**.
2. Add the following **repository secrets** (matching the three environments you created in Part 1, but pointing at real CI/CD databases or your tutorial SQL Server):

For each environment (dev, stage, prod):

- `DEV_DB_URL`, `DEV_DB_USERNAME`, `DEV_DB_PASSWORD`
- `STAGE_DB_URL`, `STAGE_DB_USERNAME`, `STAGE_DB_PASSWORD`
- `PROD_DB_URL`, `PROD_DB_USERNAME`, `PROD_DB_PASSWORD`

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

- Local tutorial SQL Server (for the self-hosted runner in Docker):

```text
jdbc:sqlserver://mssql_liquibase_tutorial:1433;
  databaseName=testdbdev;
  encrypt=true;
  trustServerCertificate=true;
  loginTimeout=30;
```

> For actual production, avoid using `sa`; create a dedicated **Liquibase service account** with only the permissions it needs (see the best practices section below).

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

Now replace the single-env workflow with a pipeline that promotes changes through dev → stage → prod.

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

Even after you add CI/CD, the helper scripts from Part 1 remain extremely valuable:

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
   - Update `changelog.xml` (using the XML wrapper + `<sqlFile>` + `<rollback>` pattern from the manual tutorial).

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
   - Use the rollback strategies and workflows from the more detailed GitHub Actions tutorial and from the rollback section in the manual Liquibase tutorial.

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

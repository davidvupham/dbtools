# SQL Server Database CI/CD with Liquibase and GitHub Actions

## Table of Contents

- [Introduction](#introduction)
- [What You'll Learn](#what-youll-learn)
- [Prerequisites](#prerequisites)
- [Tutorial Overview](#tutorial-overview)
- [Part 1: Local Setup](#part-1-local-setup)
- [Part 2: GitHub Repository Setup](#part-2-github-repository-setup)
- [Part 3: Configure GitHub Secrets](#part-3-configure-github-secrets)
- [Part 4: Create Your First Workflow](#part-4-create-your-first-workflow)
- [Part 5: Set Up Environments](#part-5-set-up-environments)
- [Part 6: Multi-Environment Deployment Pipeline](#part-6-multi-environment-deployment-pipeline)
- [Part 7: Making Database Changes](#part-7-making-database-changes)
- [Part 8: Advanced Workflows](#part-8-advanced-workflows)
- [Part 9: Monitoring and Troubleshooting](#part-9-monitoring-and-troubleshooting)
- [Part 10: Production Best Practices](#part-10-production-best-practices)
- [Part 11: Advanced Rollback Strategies](#part-11-advanced-rollback-strategies)
- [Tutorial Complete](#tutorial-complete)
- [Next Steps](#next-steps)
- [Quick Reference](#quick-reference)
- [Troubleshooting](#troubleshooting)
- [Appendix](#appendix)

## Introduction

This tutorial teaches you how to implement **automated database CI/CD** using Liquibase and GitHub Actions with Microsoft SQL Server. You'll learn to safely deploy schema changes across multiple environments (dev → staging → production) using industry-standard automation practices.

### What is CI/CD for Databases?

**CI/CD** (Continuous Integration/Continuous Deployment) means automating the process of testing and deploying changes. For databases, this means:

- **Continuous Integration**: Automatically validate database changes when code is committed
- **Continuous Deployment**: Automatically deploy validated changes to your environments

**Traditional Approach** (Manual):

```
Developer writes SQL
    ↓
Manually connect to dev database
    ↓
Manually run SQL
    ↓
Test manually
    ↓
Repeat for staging
    ↓
Repeat for production
    ↓
Hope nothing breaks!
```

**CI/CD Approach** (Automated):

```
Developer writes changelog
    ↓
Commit and push to GitHub
    ↓
GitHub Actions automatically:
  - Validates changelog
  - Deploys to dev
  - Runs tests
  - Waits for approval
  - Deploys to staging
  - Waits for approval
  - Deploys to production
    ↓
Team receives notification
```

### Why Use GitHub Actions?

1. **Built into GitHub**: No separate CI/CD server to manage
2. **Free tier**: Generous free tier for public and private repositories
3. **Easy to learn**: Simple YAML syntax
4. **Integrated**: Seamless integration with pull requests, issues, releases
5. **Secure**: Built-in secrets management
6. **No infrastructure**: GitHub provides the runners (servers)

## What You'll Learn

### Core Concepts

- ✅ **GitHub Actions fundamentals**: Workflows, jobs, steps, runners
- ✅ **Secrets management**: Securely storing database credentials
- ✅ **Environment protection**: Approval gates for production
- ✅ **Liquibase automation**: Running Liquibase in CI/CD
- ✅ **SQL Server specifics**: Connection strings, authentication, firewall rules

### Practical Skills

- ✅ Creating GitHub Actions workflows
- ✅ Setting up multi-environment pipelines
- ✅ Implementing approval workflows
- ✅ Handling failures and rollbacks
- ✅ Monitoring deployments
- ✅ Troubleshooting common issues

### Real-World Patterns

- ✅ Dev → Staging → Production pipeline
- ✅ Pull request validation
- ✅ Manual deployment triggers
- ✅ Environment-specific configuration
- ✅ Audit trails and compliance

## Prerequisites

### Required Knowledge

- ✅ Basic Git commands (commit, push, pull)
- ✅ Basic SQL knowledge
- ✅ Familiarity with GitHub (repositories, commits)
- ✅ Basic understanding of databases

### No Prior Experience Needed

- ❌ GitHub Actions (we'll teach you from scratch)
- ❌ Liquibase (we'll cover the basics)
- ❌ CI/CD concepts (everything explained)
- ❌ DevOps experience

### Required Tools and Accounts

1. **GitHub Account**: Free account at <https://github.com>
2. **SQL Server Database**: One of:
   - Azure SQL Database (free tier available)
   - Local SQL Server (Docker or installed)
   - AWS RDS SQL Server
   - On-premises SQL Server (with internet access)
3. **Text Editor**: Visual Studio Code (recommended) or any editor
4. **Git**: Installed locally for committing changes

### Database Requirements

Your SQL Server database(s) must:

- ✅ Be accessible from the internet (for GitHub Actions runners)
- ✅ Have a user account with appropriate permissions
- ✅ Allow connections on port 1433 (default SQL Server port)

**🎯 Alternative: Self-Hosted Runners**

If your database is **NOT accessible from the internet**, or you want to **learn locally with zero costs**:

✅ **Use Self-Hosted GitHub Actions Runners**

- Complete guide: [setup-self-hosted-runner-docker-liquibase-tutorial.md](../setup-self-hosted-runner-docker-liquibase-tutorial.md)
- Run GitHub Actions on your local machine (WSL + Docker)
- Direct access to local SQL Server (no firewall needed)
- Unlimited free runner minutes
- Perfect for learning and testing
- 2-3 hours setup time

**This tutorial works with BOTH:**

- **GitHub-hosted runners** (cloud, requires internet-accessible database)
- **Self-hosted runners** (local, works with any database)

Choose self-hosted if:

- You have SQL Server running locally
- You want to avoid Azure SQL setup initially
- You want unlimited free testing
- Your database is on a private network

### Recommended (Optional)

- SQL Server Management Studio (SSMS) or Azure Data Studio
- Docker Desktop (for local testing)

## Tutorial Overview

This tutorial is divided into parts that build on each other:

### Part 1: Local Setup (30 minutes)

- Set up local development environment
- Create Liquibase project structure
- Test Liquibase locally

### Part 2: GitHub Repository Setup (15 minutes)

- Create GitHub repository
- Organize project structure
- Push initial code

### Part 3: Configure Secrets (20 minutes)

- Set up repository secrets
- Configure environment-specific secrets
- Security best practices

### Part 4: First Workflow (30 minutes)

- Create simple deployment workflow
- Test with development environment
- Understand workflow execution

### Part 5: Environments (30 minutes)

- Set up GitHub Environments
- Configure approval gates
- Add environment secrets

### Part 6: Multi-Environment Pipeline (45 minutes)

- Build dev → staging → production pipeline
- Implement approval workflow
- Test end-to-end deployment

### Part 7: Making Changes (30 minutes)

- Add database changes
- Trigger automated deployment
- Monitor workflow execution

### Part 8: Advanced Workflows (45 minutes)

- Pull request validation
- Manual deployment triggers
- Rollback procedures

### Part 9: Monitoring (20 minutes)

- View deployment history
- Troubleshoot failures
- Set up notifications

### Part 10: Production Best Practices (30 minutes)

- Security hardening
- Deployment best practices
- Performance optimization

### Part 11: Advanced Rollback Strategies (45 minutes)

- Rollback methods (tag, count, date)
- Automated rollback on failure
- Emergency procedures
- Rollback testing

### Part 12 (Optional): Self-Hosted Runners (2-3 hours setup)

- Security hardening
- Performance optimization
- Compliance and auditing

**Total Time**: Approximately 4-5 hours (can be completed over multiple sessions)

## Part 1: Local Setup

Before automating with GitHub Actions, let's set up Liquibase locally and understand how it works.

### Step 1.1: Create Project Directory

```bash
# Create project directory
mkdir liquibase-github-actions-demo
cd liquibase-github-actions-demo

# Create Liquibase project structure
mkdir -p database/changelog/baseline
mkdir -p database/changelog/changes
mkdir -p .github/workflows
```

**Directory Structure:**

```
liquibase-github-actions-demo/
├── database/
│   └── changelog/
│       ├── changelog.xml           # Master changelog file
│       ├── baseline/               # Initial database snapshot
│       └── changes/                # Incremental changes
├── .github/
│   └── workflows/                  # GitHub Actions workflows
├── liquibase.properties            # Liquibase configuration
└── README.md                       # Project documentation
```

### Step 1.2: Create Liquibase Properties File

Create `liquibase.properties` for local development:

```bash
cat > liquibase.properties << 'EOF'
# Liquibase Configuration
# Note: This file is for LOCAL development only
# GitHub Actions will use environment variables and secrets

# Changelog location
changelog-file=database/changelog/changelog.xml

# Database connection (UPDATE THESE VALUES)
url=jdbc:sqlserver://localhost:1433;databaseName=mydatabase;encrypt=true;trustServerCertificate=true
username=sa
password=YourPasswordHere

# Liquibase settings
logLevel=INFO
EOF
```

**Important**: Add `liquibase.properties` to `.gitignore` (we'll create this next) so you don't commit passwords!

### Step 1.3: Create .gitignore

```bash
cat > .gitignore << 'EOF'
# Liquibase local configuration (contains passwords)
liquibase.properties

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

# Test databases
*.db
*.sqlite
EOF
```

### Step 1.4: Create Master Changelog

Create the master changelog file that will reference all changes:

```bash
cat > database/changelog/changelog.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <!-- Include baseline snapshot -->
    <include file="database/changelog/baseline/V0000__baseline.xml"/>

    <!-- Include incremental changes -->
    <includeAll path="database/changelog/changes/" relativeToChangelogFile="false"/>

</databaseChangeLog>
EOF
```

**What this does:**

- `<include>`: Includes the baseline snapshot (initial database state)
- `<includeAll>`: Automatically includes all files in the `changes/` directory

### Step 1.5: Create Baseline Changelog

Create an initial database schema (baseline):

```bash
cat > database/changelog/baseline/V0000__baseline.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <changeSet id="V0000-001" author="tutorial">
        <comment>Create customers table</comment>
        <createTable tableName="customers">
            <column name="customer_id" type="INT" autoIncrement="true">
                <constraints primaryKey="true" nullable="false"/>
            </column>
            <column name="first_name" type="NVARCHAR(100)">
                <constraints nullable="false"/>
            </column>
            <column name="last_name" type="NVARCHAR(100)">
                <constraints nullable="false"/>
            </column>
            <column name="email" type="NVARCHAR(255)">
                <constraints nullable="false" unique="true"/>
            </column>
            <column name="created_at" type="DATETIME" defaultValueComputed="GETDATE()">
                <constraints nullable="false"/>
            </column>
        </createTable>
    </changeSet>

    <changeSet id="V0000-002" author="tutorial">
        <comment>Create index on customers email</comment>
        <createIndex indexName="idx_customers_email" tableName="customers">
            <column name="email"/>
        </createIndex>
    </changeSet>

</databaseChangeLog>
EOF
```

**What this creates:**

- A `customers` table with basic fields
- An index on the email column
- Automatic timestamps

### Step 1.6: Test Locally (Optional but Recommended)

If you have Liquibase installed locally or Docker:

**With Docker:**

```bash
# Test validation
docker run --rm \
  -v "$(pwd):/workspace" \
  liquibase/liquibase:4.32.0 \
  --changelog-file=database/changelog/changelog.xml \
  validate

# Expected output: "No validation errors found"
```

**With local Liquibase:**

```bash
# Make sure liquibase.properties has correct database connection
liquibase validate
# Expected output: "No validation errors found"
```

**Note**: If you don't have Liquibase installed locally, that's okay! We'll test everything in GitHub Actions.

### Step 1.7: Create README

```bash
cat > README.md << 'EOF'
# Liquibase Database CI/CD with GitHub Actions

This project demonstrates automated database deployments using Liquibase and GitHub Actions with SQL Server.

## Project Structure

```

├── database/
│   └── changelog/
│       ├── changelog.xml          # Master changelog
│       ├── baseline/              # Initial schema
│       └── changes/               # Incremental changes
├── .github/
│   └── workflows/                 # CI/CD workflows
└── README.md

```

## Environments

- **Development**: Automatic deployment on push to main
- **Staging**: Automatic deployment after dev succeeds
- **Production**: Manual approval required

## Making Changes

1. Create a new changelog file in `database/changelog/changes/`
2. Commit and push to GitHub
3. GitHub Actions will automatically deploy to dev and staging
4. Approve production deployment when ready

## Local Development

See `liquibase.properties.example` for local configuration template.

EOF
```

### Step 1.8: Verify Local Structure

Check that everything is in place:

```bash
# List all files
find . -type f | grep -v ".git"

# Expected output:
# ./.gitignore
# ./README.md
# ./liquibase.properties
# ./database/changelog/changelog.xml
# ./database/changelog/baseline/V0000__baseline.xml
```

✅ **Checkpoint**: You now have a complete Liquibase project structure ready for GitHub!

## Part 2: GitHub Repository Setup

Now let's get this project into GitHub.

### Step 2.1: Initialize Git Repository

```bash
cd liquibase-github-actions-demo

# Initialize git
git init

# Add all files
git add .

# Make initial commit
git commit -m "Initial commit: Liquibase project structure"
```

### Step 2.2: Create GitHub Repository

1. **Go to GitHub**: <https://github.com>
2. **Click** the "+" icon → "New repository"
3. **Repository name**: `liquibase-github-actions-demo`
4. **Description**: "Database CI/CD with Liquibase and GitHub Actions"
5. **Visibility**: Choose Private (recommended for database projects)
6. **Do NOT initialize** with README, .gitignore, or license (we already have these)
7. **Click** "Create repository"

### Step 2.3: Push to GitHub

GitHub will show you commands. Follow them:

```bash
# Add GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/liquibase-github-actions-demo.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

### Step 2.4: Verify Repository

1. Go to your repository on GitHub
2. You should see:
   - `database/` directory
   - `.github/` directory
   - `README.md`
   - `.gitignore`
   - **No `liquibase.properties`** (correctly ignored)

✅ **Checkpoint**: Your code is now on GitHub!

## Part 3: Configure GitHub Secrets

Secrets store sensitive information like database passwords securely.

### Step 3.1: Understand Secret Types

GitHub has two types of secrets:

1. **Repository Secrets**: Available to all workflows in the repository
2. **Environment Secrets**: Specific to an environment (dev, staging, production)

We'll start with repository secrets and add environment secrets later.

### Step 3.2: Gather Database Information

For each environment, collect:

- Database server address
- Database name
- Username
- Password

**Example:**

| Environment | Server | Database | Username |
|-------------|--------|----------|----------|
| Development | dev-sql.database.windows.net | myapp_dev | liquibase_user |
| Staging | stg-sql.database.windows.net | myapp_stg | liquibase_user |
| Production | prd-sql.database.windows.net | myapp_prd | liquibase_user |

### Step 3.3: Configure Azure SQL Firewall (If Using Azure SQL)

**IMPORTANT:** If you're using Azure SQL Database, GitHub Actions runners need firewall access.

#### Understanding the Issue

GitHub Actions runners use **dynamic IP addresses** that change with each workflow run. Azure SQL Database blocks connections by default, so you need to allow GitHub Actions to connect.

#### Option 1: Allow Azure Services (Recommended for Development)

**Pros:** Simple, works immediately
**Cons:** Less secure (allows any Azure service)

**Steps:**

1. Go to **Azure Portal** → **SQL Database** → **Your database**
2. Click **Set server firewall** (or **Networking** in the left menu)
3. Under **Exceptions**:
   - ✅ Check **"Allow Azure services and resources to access this server"**
4. Click **Save**

**What this does:** Allows any Azure service (including GitHub Actions runners, which run on Azure) to connect.

#### Option 2: Use Service Tags with Private Link (Enterprise/Production)

**Pros:** More secure, IP-restricted
**Cons:** More complex, requires Azure networking setup

**Steps:**

1. Set up **Azure Private Link** for your SQL Database
2. Use **GitHub-hosted runners** with **Service Tags** (requires Azure Virtual Network)
3. Configure **Network Security Groups** to allow GitHub Actions IPs

**Details:** See [Azure SQL Private Link documentation](https://learn.microsoft.com/en-us/azure/azure-sql/database/private-endpoint-overview)

#### Option 3: Self-Hosted Runners (Advanced)

**Pros:** Full control, static IP, most secure
**Cons:** Infrastructure to maintain

**Steps:**

1. Set up self-hosted GitHub Actions runner on-premises or in Azure
2. Add runner's IP to Azure SQL firewall rules
3. Update workflows to use `runs-on: self-hosted`

**Details:** See [Self-Hosted Runners guide](https://docs.github.com/en/actions/hosting-your-own-runners)

#### Recommended Approach

| Environment | Recommended Solution | Why |
|-------------|---------------------|-----|
| **Development** | Allow Azure Services | Simple, fast iteration |
| **Staging** | Allow Azure Services or Service Tags | Balance of security and simplicity |
| **Production** | Self-Hosted Runners or Private Link | Maximum security, audit control |

#### Verify Firewall Configuration

Test connectivity from GitHub Actions:

```yaml
# Add to your workflow as a test step
- name: Test database connectivity
  run: |
    sqlcmd -S ${{ secrets.DEV_DB_URL }} \
      -U ${{ secrets.DEV_DB_USERNAME }} \
      -P ${{ secrets.DEV_DB_PASSWORD }} \
      -Q "SELECT @@VERSION"
```

**Expected result:** Should connect successfully and show SQL Server version.

**If connection fails:**

- Check firewall rules are saved
- Verify "Allow Azure services" is enabled
- Check connection string is correct
- Verify username/password are correct

#### Connection String Parameters for Azure SQL

For Azure SQL Database, use these connection string parameters:

```
jdbc:sqlserver://YOUR_SERVER.database.windows.net:1433;
  databaseName=YOUR_DATABASE;
  encrypt=true;                      # REQUIRED for Azure SQL
  trustServerCertificate=false;      # Validate SSL certificate
  loginTimeout=30;                   # Timeout in seconds
  connectRetryCount=3;               # Retry failed connections
  connectRetryInterval=10            # Wait 10 seconds between retries
```

**Key parameters explained:**

- `encrypt=true`: Required by Azure SQL (enforces SSL/TLS encryption)
- `trustServerCertificate=false`: Validates server certificate (recommended for Azure)
- `loginTimeout=30`: Prevents hanging on connection issues
- `connectRetryCount` and `connectRetryInterval`: Handles transient network issues

#### Troubleshooting Common Firewall Issues

**Error:** `Cannot open server 'xxx' requested by the login. Client with IP address 'xxx.xxx.xxx.xxx' is not allowed to access the server.`

**Solution:**

1. Note the IP address in the error message
2. Go to Azure Portal → SQL Database → Networking
3. Under **Firewall rules**, click **Add client IP**
4. Add the IP from the error message (temporary for testing)
5. Or enable "Allow Azure services" for permanent solution

**Error:** `Login timeout expired`

**Solution:**

1. Check firewall rules are correct
2. Verify connection string has correct server name
3. Ensure database name is correct
4. Check if SQL Server is running

### Step 3.4: Add Repository Secrets

1. **Go to your repository** on GitHub
2. **Click** "Settings" tab
3. **Click** "Secrets and variables" → "Actions" (in left sidebar)
4. **Click** "New repository secret"

Add these secrets:

#### Secret 1: `DEV_DB_URL`

```
Name: DEV_DB_URL
Value: jdbc:sqlserver://YOUR_DEV_SERVER:1433;databaseName=YOUR_DEV_DATABASE;encrypt=true;trustServerCertificate=false;loginTimeout=30;connectRetryCount=3
```

**Example for Azure SQL:**

```
jdbc:sqlserver://dev-sql.database.windows.net:1433;databaseName=myapp_dev;encrypt=true;trustServerCertificate=false;loginTimeout=30;connectRetryCount=3
```

**Example for On-Premises SQL:**

```
jdbc:sqlserver://sqlserver.company.local:1433;databaseName=myapp_dev;encrypt=true;trustServerCertificate=true;loginTimeout=30
```

#### Secret 2: `DEV_DB_USERNAME`

```
Name: DEV_DB_USERNAME
Value: liquibase_user
```

#### Secret 3: `DEV_DB_PASSWORD`

```
Name: DEV_DB_PASSWORD
Value: YourActualPassword123!
```

Repeat for staging and production:

**Staging Secrets:**

- `STAGE_DB_URL`
- `STAGE_DB_USERNAME`
- `STAGE_DB_PASSWORD`

**Production Secrets:**

- `PROD_DB_URL`
- `PROD_DB_USERNAME`
- `PROD_DB_PASSWORD`

### Step 3.5: Verify Secrets

After adding all secrets:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. You should see 9 secrets:
   - `DEV_DB_URL`
   - `DEV_DB_USERNAME`
   - `DEV_DB_PASSWORD`
   - `STAGE_DB_URL`
   - `STAGE_DB_USERNAME`
   - `STAGE_DB_PASSWORD`
   - `PROD_DB_URL`
   - `PROD_DB_USERNAME`
   - `PROD_DB_PASSWORD`

**Important**: Secret values are hidden. You can update them but cannot view them again.

### Step 3.6: Connection String Details

#### For Azure SQL Database

```
jdbc:sqlserver://YOUR_SERVER.database.windows.net:1433;databaseName=YOUR_DATABASE;encrypt=true;trustServerCertificate=false;loginTimeout=30
```

#### For Local/On-Premises SQL Server

```
jdbc:sqlserver://YOUR_SERVER:1433;databaseName=YOUR_DATABASE;encrypt=true;trustServerCertificate=true;loginTimeout=30
```

**Key Differences:**

- Azure SQL: `trustServerCertificate=false` (validate SSL certificate)
- On-premises: `trustServerCertificate=true` (skip certificate validation)

✅ **Checkpoint**: Database credentials are securely stored in GitHub!

## Part 4: Create Your First Workflow

Now let's create a simple workflow that deploys to development.

### Step 4.1: Understand Workflow Basics

A workflow is a YAML file that defines:

- **When** to run (trigger events)
- **What** to run (jobs and steps)
- **Where** to run (runner type)

Basic structure:

```yaml
name: Workflow Name

on:
  # When to trigger
  push:
    branches:
      - main

jobs:
  job-name:
    runs-on: ubuntu-latest  # Where to run

    steps:
      - name: Step 1
        # What to do
```

### Step 4.2: Create Development Deployment Workflow

Create the workflow file:

```bash
# Make sure you're in project root
cd liquibase-github-actions-demo

# Create workflow directory (if not exists)
mkdir -p .github/workflows

# Create workflow file
cat > .github/workflows/deploy-dev.yml << 'EOF'
name: Deploy to Development

# Trigger on push to main branch
on:
  push:
    branches:
      - main
    paths:
      - 'database/**'  # Only trigger if database files change

# Also allow manual trigger
  workflow_dispatch:

jobs:
  deploy-dev:
    name: Deploy to Development Database
    runs-on: ubuntu-latest

    steps:
      # Step 1: Get the code
      - name: Checkout repository
        uses: actions/checkout@v3

      # Step 2: Set up Java (required by Liquibase)
      - name: Set up Java
        uses: actions/setup-java@v3
        with:
          distribution: 'temurin'
          java-version: '11'

      # Step 3: Set up Liquibase
      - name: Set up Liquibase
        uses: liquibase/setup-liquibase@v2
        with:
          version: '4.32.0'
          edition: 'oss'

      # Step 4: Run Liquibase update
      - name: Deploy database changes
        run: |
          liquibase update \
            --changelog-file=database/changelog/changelog.xml \
            --url="${{ secrets.DEV_DB_URL }}" \
            --username="${{ secrets.DEV_DB_USERNAME }}" \
            --password="${{ secrets.DEV_DB_PASSWORD }}"

      # Step 5: Show deployment status
      - name: Show deployment history
        run: |
          liquibase history \
            --url="${{ secrets.DEV_DB_URL }}" \
            --username="${{ secrets.DEV_DB_USERNAME }}" \
            --password="${{ secrets.DEV_DB_PASSWORD }}"
EOF
```

**What each part does:**

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'database/**'
```

- **Trigger**: Runs when code is pushed to `main` branch AND database files changed

```yaml
  workflow_dispatch:
```

- **Manual Trigger**: Allows you to manually run this workflow from GitHub UI

```yaml
runs-on: ubuntu-latest
```

- **Runner**: Uses Ubuntu Linux server provided by GitHub

```yaml
uses: actions/checkout@v3
```

- **Action**: Checks out your repository code

```yaml
uses: liquibase/setup-liquibase@v2
```

- **Action**: Installs Liquibase on the runner

```yaml
${{ secrets.DEV_DB_URL }}
```

- **Secret Reference**: Uses the secret you configured earlier

### Step 4.3: Commit and Push Workflow

```bash
# Add workflow file
git add .github/workflows/deploy-dev.yml

# Commit
git commit -m "Add development deployment workflow"

# Push to GitHub
git push origin main
```

### Step 4.4: Watch Workflow Execute

1. **Go to GitHub repository**
2. **Click** "Actions" tab
3. You should see "Deploy to Development" workflow running
4. **Click** on the workflow run to see details

**Workflow Execution View:**

```
Deploy to Development
  Deploy to Development Database
    ✓ Checkout repository
    ✓ Set up Java
    ✓ Set up Liquibase
    ✓ Deploy database changes
    ✓ Show deployment history
```

### Step 4.5: Verify Deployment

Connect to your development database and verify:

```sql
-- Check Liquibase tracking tables were created
SELECT * FROM DATABASECHANGELOG ORDER BY DATEEXECUTED DESC;

-- Check your table was created
SELECT * FROM customers;

-- Verify indexes
SELECT
    i.name AS index_name,
    t.name AS table_name
FROM sys.indexes i
JOIN sys.tables t ON i.object_id = t.object_id
WHERE t.name = 'customers';
```

**Expected Results:**

- `DATABASECHANGELOG` table exists with 2 entries
- `customers` table exists with correct schema
- Index `idx_customers_email` exists

### Step 4.6: Manual Trigger Test

Let's manually trigger the workflow:

1. Go to **Actions** tab
2. Click **Deploy to Development** workflow (left sidebar)
3. Click **Run workflow** button (right side)
4. Select branch: `main`
5. Click **Run workflow**

The workflow runs again! This is useful for:

- Testing workflows
- Re-running deployments
- Manual deployments without code changes

✅ **Checkpoint**: You've successfully automated development deployments!

## Part 5: Set Up Environments

Environments provide approval gates and environment-specific secrets.

### Step 5.1: Understand GitHub Environments

**Environments** let you:

- ✅ Require manual approval before deployment
- ✅ Store environment-specific secrets
- ✅ Restrict which branches can deploy
- ✅ Add deployment protection rules
- ✅ Track deployment history

### Step 5.2: Create Development Environment

1. Go to **Settings** tab
2. Click **Environments** (left sidebar)
3. Click **New environment**
4. Name: `development`
5. Click **Configure environment**

**Configuration:**

- ❌ **Don't add** required reviewers (dev should deploy automatically)
- ❌ **Don't add** wait timer
- ✅ **Leave** deployment branches unrestricted
- Click **Save protection rules**

### Step 5.3: Create Staging Environment

1. Click **New environment**
2. Name: `staging`
3. Click **Configure environment**

**Configuration:**

- ❌ **Don't add** required reviewers (auto-deploy after dev)
- ❌ **Don't add** wait timer
- Click **Save protection rules**

### Step 5.4: Create Production Environment

1. Click **New environment**
2. Name: `production`
3. Click **Configure environment**

**Configuration:**

- ✅ **Check** "Required reviewers"
- ✅ **Add** yourself as a reviewer (minimum 1 reviewer)
- ✅ **Check** "Wait timer" (optional)
  - Set to `5` minutes (gives you time to verify staging)
- ✅ **Deployment branches**: Select "Selected branches"
  - Add rule: `main` (only deploy from main branch)
- Click **Save protection rules**

**What this means:**

- Production deployments MUST be approved
- Must wait 5 minutes after staging
- Can only deploy from `main` branch

### Step 5.5: Add Environment Secrets (Optional)

You can move secrets from repository level to environment level for better organization.

**For Development Environment:**

1. Go to **Settings** → **Environments** → **development**
2. Scroll to **Environment secrets**
3. Click **Add secret**

Add:

- `DB_URL` → (same value as `DEV_DB_URL`)
- `DB_USERNAME` → (same value as `DEV_DB_USERNAME`)
- `DB_PASSWORD` → (same value as `DEV_DB_PASSWORD`)

Repeat for staging and production.

**Benefits:**

- Cleaner secret names (just `DB_URL` instead of `DEV_DB_URL`)
- Environment-scoped (can't accidentally use wrong secret)
- Better organization

**Note**: For this tutorial, we'll continue using repository secrets (`DEV_DB_URL`, etc.) for simplicity.

### Step 5.6: Verify Environment Setup

Go to **Settings** → **Environments**. You should see:

| Environment | Protection Rules |
|-------------|------------------|
| development | None |
| staging | None |
| production | Required reviewers: 1, Wait timer: 5 minutes |

✅ **Checkpoint**: Environments configured with production protection!

## Part 6: Multi-Environment Deployment Pipeline

Now let's create a workflow that deploys through all environments.

### Step 6.1: Understand Pipeline Flow

```
Code pushed to main
    ↓
Deploy to Development (automatic)
    ↓
Deploy to Staging (automatic)
    ↓
[WAIT 5 MINUTES]
    ↓
[APPROVAL REQUIRED]
    ↓
Deploy to Production (after approval)
```

### Step 6.2: Create Pipeline Workflow

Create a new workflow file:

```bash
cat > .github/workflows/deploy-pipeline.yml << 'EOF'
name: Database Deployment Pipeline

on:
  push:
    branches:
      - main
    paths:
      - 'database/**'
  workflow_dispatch:

jobs:
  # Job 1: Deploy to Development
  deploy-dev:
    name: Deploy to Development
    runs-on: ubuntu-latest
    environment: development

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Java
        uses: actions/setup-java@v3
        with:
          distribution: 'temurin'
          java-version: '11'

      - name: Set up Liquibase
        uses: liquibase/setup-liquibase@v2
        with:
          version: '4.32.0'
          edition: 'oss'

      - name: Deploy to development
        run: |
          echo "Deploying to DEVELOPMENT..."
          liquibase update \
            --changelog-file=database/changelog/changelog.xml \
            --url="${{ secrets.DEV_DB_URL }}" \
            --username="${{ secrets.DEV_DB_USERNAME }}" \
            --password="${{ secrets.DEV_DB_PASSWORD }}"

      - name: Verify deployment
        run: |
          echo "Deployment history:"
          liquibase history --count=5 \
            --url="${{ secrets.DEV_DB_URL }}" \
            --username="${{ secrets.DEV_DB_USERNAME }}" \
            --password="${{ secrets.DEV_DB_PASSWORD }}"

  # Job 2: Deploy to Staging (after dev succeeds)
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: deploy-dev  # Wait for dev to complete
    environment: staging

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Java
        uses: actions/setup-java@v3
        with:
          distribution: 'temurin'
          java-version: '11'

      - name: Set up Liquibase
        uses: liquibase/setup-liquibase@v2
        with:
          version: '4.32.0'
          edition: 'oss'

      - name: Deploy to staging
        run: |
          echo "Deploying to STAGING..."
          liquibase update \
            --changelog-file=database/changelog/changelog.xml \
            --url="${{ secrets.STAGE_DB_URL }}" \
            --username="${{ secrets.STAGE_DB_USERNAME }}" \
            --password="${{ secrets.STAGE_DB_PASSWORD }}"

      - name: Verify deployment
        run: |
          echo "Deployment history:"
          liquibase history --count=5 \
            --url="${{ secrets.STAGE_DB_URL }}" \
            --username="${{ secrets.STAGE_DB_USERNAME }}" \
            --password="${{ secrets.STAGE_DB_PASSWORD }}"

  # Job 3: Deploy to Production (requires approval)
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: deploy-staging  # Wait for staging to complete
    environment: production  # Requires approval (configured in Step 5)

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Java
        uses: actions/setup-java@v3
        with:
          distribution: 'temurin'
          java-version: '11'

      - name: Set up Liquibase
        uses: liquibase/setup-liquibase@v2
        with:
          version: '4.32.0'
          edition: 'oss'

      - name: Deploy to production
        run: |
          echo "Deploying to PRODUCTION..."
          liquibase update \
            --changelog-file=database/changelog/changelog.xml \
            --url="${{ secrets.PROD_DB_URL }}" \
            --username="${{ secrets.PROD_DB_USERNAME }}" \
            --password="${{ secrets.PROD_DB_PASSWORD }}"

      - name: Tag deployment
        run: |
          echo "Tagging production deployment..."
          liquibase tag "release-${{ github.run_number }}" \
            --url="${{ secrets.PROD_DB_URL }}" \
            --username="${{ secrets.PROD_DB_USERNAME }}" \
            --password="${{ secrets.PROD_DB_PASSWORD }}"

      - name: Verify deployment
        run: |
          echo "Production deployment complete!"
          liquibase history --count=10 \
            --url="${{ secrets.PROD_DB_URL }}" \
            --username="${{ secrets.PROD_DB_USERNAME }}" \
            --password="${{ secrets.PROD_DB_PASSWORD }}"
EOF
```

**Key Features:**

```yaml
needs: deploy-dev
```

- **Dependency**: This job waits for `deploy-dev` to complete successfully

```yaml
environment: production
```

- **Protection**: Triggers approval requirement we configured in Step 5

```yaml
liquibase tag "release-${{ github.run_number }}"
```

- **Tagging**: Creates a tag in the database for easy rollback

### Step 6.3: Delete Old Workflow

We now have a better workflow. Remove the old one:

```bash
# Delete old workflow
git rm .github/workflows/deploy-dev.yml

# Commit
git commit -m "Replace simple workflow with multi-environment pipeline"
```

### Step 6.4: Commit and Push Pipeline

```bash
# Add new pipeline workflow
git add .github/workflows/deploy-pipeline.yml

# Commit
git commit -m "Add multi-environment deployment pipeline"

# Push
git push origin main
```

### Step 6.5: Watch Pipeline Execute

1. Go to **Actions** tab on GitHub
2. Click on "Database Deployment Pipeline" run

You'll see the pipeline flow:

```
deploy-dev ✓ (completed)
    ↓
deploy-staging ✓ (completed)
    ↓
deploy-production ⏸ (waiting for approval)
```

### Step 6.6: Approve Production Deployment

After 5 minutes (wait timer), you'll see:

1. **Yellow notification**: "deploy-production is waiting for approval"
2. **Click** "Review deployments"
3. **Check** "production"
4. **Click** "Approve and deploy"

Watch production deployment complete!

### Step 6.7: Verify All Environments

Check all three databases have the same schema:

**Development:**

```sql
SELECT COUNT(*) FROM DATABASECHANGELOG; -- Should match across all envs
```

**Staging:**

```sql
SELECT COUNT(*) FROM DATABASECHANGELOG; -- Should match
```

**Production:**

```sql
SELECT COUNT(*) FROM DATABASECHANGELOG; -- Should match
SELECT * FROM DATABASECHANGELOGLOCK; -- Check locks
```

✅ **Checkpoint**: Multi-environment pipeline working with approvals!

## Part 7: Making Database Changes

Let's make a real database change and watch it flow through the pipeline.

### Step 7.1: Create New Changelog File

Create a new change to add a `phone` column to customers:

```bash
cat > database/changelog/changes/V0001__add_customer_phone.sql << 'EOF'
--liquibase formatted sql

--changeset tutorial:V0001-001
--comment: Add phone column to customers table
ALTER TABLE customers
ADD phone NVARCHAR(20) NULL;
GO

--changeset tutorial:V0001-002
--comment: Add index on customer phone
CREATE INDEX idx_customers_phone ON customers(phone);
GO

--rollback DROP INDEX idx_customers_phone ON customers;
--rollback ALTER TABLE customers DROP COLUMN phone;
EOF
```

**What's new here:**

```sql
--liquibase formatted sql
```

- **Format**: Tells Liquibase this is a SQL file (not XML)

```sql
--changeset tutorial:V0001-001
```

- **Changeset ID**: Unique identifier for this change
- Format: `author:id`

```sql
--rollback DROP INDEX...
```

- **Rollback**: SQL to undo this change if needed

### Step 7.2: Commit and Push

```bash
# Add new changelog
git add database/changelog/changes/V0001__add_customer_phone.sql

# Commit with descriptive message
git commit -m "Add phone column to customers table"

# Push to trigger pipeline
git push origin main
```

### Step 7.3: Watch Automated Deployment

1. Go to **Actions** tab
2. Click on the new workflow run
3. Watch it progress:

```
deploy-dev ⏳ Running...
    ↓
    ✓ Complete
    ↓
deploy-staging ⏳ Running...
    ↓
    ✓ Complete
    ↓
deploy-production ⏸ Waiting for approval...
```

### Step 7.4: Verify in Development

While staging is deploying, check development:

```sql
-- Verify phone column exists
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'customers'
AND COLUMN_NAME = 'phone';

-- Expected: phone, nvarchar, YES

-- Verify index exists
SELECT name FROM sys.indexes
WHERE object_id = OBJECT_ID('customers')
AND name = 'idx_customers_phone';

-- Expected: idx_customers_phone
```

### Step 7.5: Verify in Staging

After staging deployment completes:

```sql
-- Same verification as dev
SELECT COLUMN_NAME, DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'customers'
AND COLUMN_NAME = 'phone';
```

### Step 7.6: Approve Production

After wait timer expires:

1. Click **Review deployments**
2. Review the changes in staging
3. If satisfied, **Approve and deploy**

### Step 7.7: Verify in Production

After production deployment:

```sql
-- Verify change in production
SELECT COLUMN_NAME, DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'customers'
AND COLUMN_NAME = 'phone';

-- Check deployment tag
SELECT * FROM DATABASECHANGELOG
WHERE TAG IS NOT NULL
ORDER BY DATEEXECUTED DESC;

-- Should show: release-<run_number>
```

### Step 7.8: View Deployment History

GitHub provides deployment history:

1. Go to **Settings** → **Environments** → **production**
2. Scroll down to **Deployment history**
3. You'll see:
   - When deployed
   - Who approved
   - Which commit
   - Workflow run link

✅ **Checkpoint**: Successfully deployed a database change through the pipeline!

## Part 8: Advanced Workflows

Let's add more sophisticated workflows for real-world scenarios.

### Step 8.1: Pull Request Validation

Create a workflow that validates changes before merging:

```bash
cat > .github/workflows/validate-pr.yml << 'EOF'
name: Validate Pull Request

on:
  pull_request:
    branches:
      - main
    paths:
      - 'database/**'

jobs:
  validate:
    name: Validate Database Changes
    runs-on: ubuntu-latest

    steps:
      - name: Checkout PR code
        uses: actions/checkout@v3

      - name: Set up Java
        uses: actions/setup-java@v3
        with:
          distribution: 'temurin'
          java-version: '11'

      - name: Set up Liquibase
        uses: liquibase/setup-liquibase@v2
        with:
          version: '4.32.0'

      - name: Validate changelog syntax
        run: |
          echo "Validating changelog syntax..."
          liquibase validate \
            --changelog-file=database/changelog/changelog.xml

      - name: Generate SQL preview
        run: |
          echo "Generating SQL preview..."
          liquibase update-sql \
            --changelog-file=database/changelog/changelog.xml \
            --url="${{ secrets.DEV_DB_URL }}" \
            --username="${{ secrets.DEV_DB_USERNAME }}" \
            --password="${{ secrets.DEV_DB_PASSWORD }}" \
            > sql-preview.sql

      - name: Upload SQL preview
        uses: actions/upload-artifact@v3
        with:
          name: sql-preview
          path: sql-preview.sql

      - name: Check for pending changes
        run: |
          echo "Checking for pending changes..."
          liquibase status --verbose \
            --changelog-file=database/changelog/changelog.xml \
            --url="${{ secrets.DEV_DB_URL }}" \
            --username="${{ secrets.DEV_DB_USERNAME }}" \
            --password="${{ secrets.DEV_DB_PASSWORD }}"

      - name: Validation Summary
        run: |
          echo "✅ Changelog syntax is valid"
          echo "✅ SQL preview generated"
          echo "✅ Changes ready for deployment"
          echo ""
          echo "To view generated SQL, download the 'sql-preview' artifact"
EOF
```

**What this does:**

- Runs on every pull request
- Validates changelog syntax
- Generates SQL preview
- Shows pending changes
- Does NOT deploy (safe for PRs)

### Step 8.2: Manual Deployment Workflow

Create a workflow for manual deployments with environment selection:

```bash
cat > .github/workflows/manual-deploy.yml << 'EOF'
name: Manual Deployment

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options:
          - development
          - staging
          - production
      changelog_tag:
        description: 'Deploy up to this tag (optional)'
        required: false
        type: string

jobs:
  deploy:
    name: Deploy to ${{ inputs.environment }}
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Java
        uses: actions/setup-java@v3
        with:
          distribution: 'temurin'
          java-version: '11'

      - name: Set up Liquibase
        uses: liquibase/setup-liquibase@v2
        with:
          version: '4.32.0'

      - name: Set database credentials
        id: set-db
        run: |
          case "${{ inputs.environment }}" in
            development)
              echo "db_url=${{ secrets.DEV_DB_URL }}" >> $GITHUB_OUTPUT
              echo "db_user=${{ secrets.DEV_DB_USERNAME }}" >> $GITHUB_OUTPUT
              echo "db_pass=${{ secrets.DEV_DB_PASSWORD }}" >> $GITHUB_OUTPUT
              ;;
            staging)
              echo "db_url=${{ secrets.STAGE_DB_URL }}" >> $GITHUB_OUTPUT
              echo "db_user=${{ secrets.STAGE_DB_USERNAME }}" >> $GITHUB_OUTPUT
              echo "db_pass=${{ secrets.STAGE_DB_PASSWORD }}" >> $GITHUB_OUTPUT
              ;;
            production)
              echo "db_url=${{ secrets.PROD_DB_URL }}" >> $GITHUB_OUTPUT
              echo "db_user=${{ secrets.PROD_DB_USERNAME }}" >> $GITHUB_OUTPUT
              echo "db_pass=${{ secrets.PROD_DB_PASSWORD }}" >> $GITHUB_OUTPUT
              ;;
          esac

      - name: Deploy to ${{ inputs.environment }}
        run: |
          echo "Deploying to ${{ inputs.environment }}..."

          if [ -n "${{ inputs.changelog_tag }}" ]; then
            echo "Deploying up to tag: ${{ inputs.changelog_tag }}"
            liquibase update-to-tag \
              --tag="${{ inputs.changelog_tag }}" \
              --changelog-file=database/changelog/changelog.xml \
              --url="${{ steps.set-db.outputs.db_url }}" \
              --username="${{ steps.set-db.outputs.db_user }}" \
              --password="${{ steps.set-db.outputs.db_pass }}"
          else
            echo "Deploying all pending changes"
            liquibase update \
              --changelog-file=database/changelog/changelog.xml \
              --url="${{ steps.set-db.outputs.db_url }}" \
              --username="${{ steps.set-db.outputs.db_user }}" \
              --password="${{ steps.set-db.outputs.db_pass }}"
          fi

      - name: Deployment summary
        run: |
          echo "Deployment to ${{ inputs.environment }} complete!"
          liquibase history --count=10 \
            --url="${{ steps.set-db.outputs.db_url }}" \
            --username="${{ steps.set-db.outputs.db_user }}" \
            --password="${{ steps.set-db.outputs.db_pass }}"
EOF
```

**What this does:**

- Allows manual trigger with environment selection
- Optionally deploy up to a specific tag
- Uses conditional logic to select correct credentials
- Still respects environment protection rules

### Step 8.3: Test Manual Deployment

1. Go to **Actions** tab
2. Click **Manual Deployment** (left sidebar)
3. Click **Run workflow**
4. Select:
   - Environment: `development`
   - Changelog tag: (leave empty)
5. Click **Run workflow**

Watch it deploy!

### Step 8.4: Test Pull Request Validation

Create a test pull request:

```bash
# Create feature branch
git checkout -b feature/add-customer-status

# Add a new change
cat > database/changelog/changes/V0002__add_customer_status.sql << 'EOF'
--liquibase formatted sql

--changeset tutorial:V0002-001
--comment: Add status column to customers
ALTER TABLE customers
ADD status NVARCHAR(20) NOT NULL DEFAULT 'active';
GO

--changeset tutorial:V0002-002
--comment: Add check constraint on status
ALTER TABLE customers
ADD CONSTRAINT chk_customer_status CHECK (status IN ('active', 'inactive', 'suspended'));
GO

--rollback ALTER TABLE customers DROP CONSTRAINT chk_customer_status;
--rollback ALTER TABLE customers DROP COLUMN status;
EOF

# Commit
git add database/changelog/changes/V0002__add_customer_status.sql
git commit -m "Add status column to customers"

# Push to GitHub
git push origin feature/add-customer-status
```

On GitHub:

1. Go to **Pull requests** tab
2. Click **New pull request**
3. Base: `main`, Compare: `feature/add-customer-status`
4. Click **Create pull request**

Watch the validation workflow run! It will:

- ✅ Validate syntax
- ✅ Generate SQL preview
- ✅ Show in PR checks

After validation passes, merge the PR to trigger the deployment pipeline.

### Step 8.5: Commit Advanced Workflows

```bash
# Switch back to main
git checkout main

# Pull latest (includes merged PR)
git pull origin main

# Add workflow files
git add .github/workflows/validate-pr.yml
git add .github/workflows/manual-deploy.yml

# Commit
git commit -m "Add PR validation and manual deployment workflows"

# Push
git push origin main
```

✅ **Checkpoint**: Advanced workflows configured for real-world scenarios!

## Part 9: Monitoring and Troubleshooting

Learn how to monitor deployments and fix issues.

### Step 9.1: View Workflow Runs

**See all runs:**

1. Go to **Actions** tab
2. You'll see list of all workflow runs
3. Filter by:
   - Workflow name (left sidebar)
   - Branch
   - Status (success/failure/in progress)

**See run details:**

1. Click on any workflow run
2. View:
   - Trigger (who, what commit)
   - Duration
   - Jobs and their status
   - Logs for each step

### Step 9.2: View Deployment History

**Environment deployments:**

1. Go to **Settings** → **Environments**
2. Click on environment name
3. Scroll to **Deployment history**

You'll see:

- Deployment status
- Who approved (for production)
- When deployed
- Which commit
- Link to workflow run

### Step 9.3: Read Workflow Logs

To view detailed logs:

1. Go to **Actions** → Click workflow run
2. Click job name (e.g., "Deploy to Production")
3. Click step name (e.g., "Deploy to production")
4. View full output

**Look for:**

```
Liquibase Community 4.32.0 by Liquibase
Running Changeset: database/changelog/changes/V0001__add_customer_phone.sql::V0001-001::tutorial
Changeset database/changelog/changes/V0001__add_customer_phone.sql::V0001-001::tutorial ran successfully in 123ms
```

### Step 9.4: Download Artifacts

Some workflows create artifacts (files):

1. Go to workflow run
2. Scroll down to **Artifacts**
3. Click artifact name to download
4. Example: `sql-preview` from PR validation

### Step 9.5: Common Issues and Solutions

#### Issue 1: Connection Failed

**Error:**

```
Could not connect to database: Connection refused
```

**Solutions:**

1. Verify database is running and accessible
2. Check firewall allows GitHub Actions IP ranges
3. Verify connection string in secrets
4. Test connection locally with same credentials

#### Issue 2: Authentication Failed

**Error:**

```
Login failed for user 'liquibase_user'
```

**Solutions:**

1. Verify username and password in secrets
2. Check user exists in database
3. Verify user has correct permissions
4. Check password doesn't contain special characters causing issues

#### Issue 3: Changeset Already Ran

**Error:**

```
Changeset database/changelog/changes/V0001__add_customer_phone.sql::V0001-001::tutorial has already been run
```

**This is actually NORMAL!** Liquibase tracks what's been deployed. This happens when:

- Re-running workflow on same environment
- No new changes to deploy

**Not an error** - workflow should still succeed.

#### Issue 4: Validation Failed

**Error:**

```
Could not find file 'database/changelog/changelog.xml'
```

**Solutions:**

1. Verify file path is correct
2. Check `actions/checkout@v3` step is included
3. Ensure path uses forward slashes (/) not backslashes (\)

#### Issue 5: Secret Not Found

**Error:**

```
Error: secret DEV_DB_URL not found
```

**Solutions:**

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Verify secret name matches exactly (case-sensitive)
3. Check secret is not environment-specific when using repository secret
4. Add the secret if missing

### Step 9.6: Enable Failure Notifications

Get notified when deployments fail:

**Email** (built-in):

1. Go to your GitHub profile
2. Click **Settings** → **Notifications**
3. Ensure "Actions" is enabled

**Slack** (requires setup):

Add to workflow:

```yaml
- name: Notify on failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "❌ Database deployment failed",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Deployment Failed*\n• Workflow: ${{ github.workflow }}\n• Environment: production\n• Triggered by: ${{ github.actor }}\n• <${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View run>"
            }
          }
        ]
      }
```

### Step 9.7: View Database Deployment History

Connect to your database and query Liquibase tables:

```sql
-- View all deployed changesets
SELECT
    ID,
    AUTHOR,
    FILENAME,
    DATEEXECUTED,
    TAG,
    DEPLOYMENT_ID
FROM DATABASECHANGELOG
ORDER BY DATEEXECUTED DESC;

-- View deployment tags
SELECT DISTINCT TAG, DATEEXECUTED
FROM DATABASECHANGELOG
WHERE TAG IS NOT NULL
ORDER BY DATEEXECUTED DESC;

-- Count deployments
SELECT COUNT(DISTINCT DEPLOYMENT_ID) as total_deployments
FROM DATABASECHANGELOG;
```

✅ **Checkpoint**: You can now monitor and troubleshoot deployments!

## Part 10: Production Best Practices

Final recommendations for production use.

### Step 10.1: Security Hardening

#### Use Environment Secrets

Move secrets from repository to environment level:

1. **Settings** → **Environments** → **production**
2. Add environment-specific secrets
3. Update workflow to use environment secrets

**Benefit**: Production secrets only accessible to production environment.

#### Rotate Secrets Regularly

Create a schedule:

- Development: Quarterly
- Staging: Quarterly
- Production: Monthly (or after any suspected compromise)

#### Use Service Accounts

Create dedicated database accounts:

```sql
-- Create service account
CREATE LOGIN liquibase_deployer WITH PASSWORD = 'SecurePassword123!';
CREATE USER liquibase_deployer FOR LOGIN liquibase_deployer;

-- Grant minimal permissions
GRANT CREATE TABLE TO liquibase_deployer;
GRANT ALTER ON SCHEMA::dbo TO liquibase_deployer;
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::dbo TO liquibase_deployer;

-- DO NOT GRANT db_owner or sysadmin!
```

#### Enable Audit Logging

```yaml
- name: Log deployment
  run: |
    cat << EOF > deployment-log.json
    {
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "environment": "production",
      "triggered_by": "${{ github.actor }}",
      "commit": "${{ github.sha }}",
      "workflow_run": "${{ github.run_id }}"
    }
    EOF

- name: Upload audit log
  uses: actions/upload-artifact@v3
  with:
    name: deployment-audit-log
    path: deployment-log.json
    retention-days: 365  # Keep for 1 year
```

### Step 10.2: Deployment Best Practices

#### Always Use Tags

Tag every production deployment:

```yaml
- name: Tag production deployment
  run: |
    liquibase tag "v${{ github.run_number }}-$(date +%Y%m%d)" \
      --url="${{ secrets.PROD_DB_URL }}"
```

**Benefits:**

- Easy rollback: `liquibase rollback v123-20250115`
- Audit trail: Know exactly what's deployed
- Troubleshooting: Link issues to specific deployments

#### Implement Health Checks

Add post-deployment verification:

```yaml
- name: Post-deployment health check
  run: |
    # Check database is accessible
    sqlcmd -S $SERVER -U $USER -P $PASS -Q "SELECT 1"

    # Verify critical tables exist
    sqlcmd -Q "SELECT COUNT(*) FROM customers"

    # Run application smoke tests
    curl -f https://api.example.com/health
```

#### Use Deployment Windows

For production, deploy during maintenance windows:

```yaml
on:
  schedule:
    # Deploy Sundays at 2 AM UTC
    - cron: '0 2 * * 0'
  workflow_dispatch:  # Still allow manual
```

#### Require Multiple Approvers

For critical systems:

1. **Settings** → **Environments** → **production**
2. **Required reviewers**: Add 2-3 people
3. Ensures no single person can deploy to production

### Step 10.3: Performance Optimization

#### Cache Dependencies

```yaml
- name: Cache Liquibase
  uses: actions/cache@v3
  with:
    path: |
      ~/.liquibase
      ~/.m2/repository
    key: ${{ runner.os }}-liquibase-${{ hashFiles('**/liquibase.properties') }}
```

**Impact**: Reduces workflow time by 20-30%.

#### Conditional Execution

Only run workflows when needed:

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'database/**'      # Only if database changes
      - '.github/workflows/**'  # Or workflow changes
```

#### Parallel Deployments

For independent databases:

```yaml
jobs:
  deploy-db1:
    runs-on: ubuntu-latest
    steps: [...]

  deploy-db2:
    runs-on: ubuntu-latest
    steps: [...]

  # Both run in parallel
```

### Step 10.4: Compliance and Auditing

#### Maintain Changelog Discipline

**Good changelog naming:**

```
V0001__add_customer_table.sql
V0002__add_order_table.sql
V0003__modify_customer_email.sql
```

**Bad naming:**

```
change.sql
fix.sql
update2.sql
```

#### Document Every Change

```sql
--liquibase formatted sql

--changeset john.doe:V0005-001
--comment: Add phone column to support mobile notifications
--comment: Ticket: JIRA-1234
--comment: Approved by: Jane Smith
--comment: Rollback plan: See ROLLBACK.md
ALTER TABLE customers ADD phone NVARCHAR(20);
```

#### Track Deployment Metrics

```yaml
- name: Record metrics
  run: |
    echo "deployment_timestamp=$(date +%s)" >> metrics.txt
    echo "environment=production" >> metrics.txt
    echo "changesets_deployed=$(liquibase history --count)" >> metrics.txt
```

### Step 10.5: Disaster Recovery

#### Test Rollbacks

Regularly test rollback procedures:

```bash
# In non-production environment
liquibase rollback-count 1
# Verify
liquibase status
# Re-deploy
liquibase update
```

#### Maintain Backups

Before production deployment:

```yaml
- name: Backup database
  run: |
    # Azure SQL example
    az sql db create --name prod-backup-$(date +%Y%m%d)

    # Or use SQL Server backup
    sqlcmd -Q "BACKUP DATABASE [mydb] TO DISK = '/backup/pre-deploy-$(date +%Y%m%d).bak'"
```

#### Document Recovery Procedures

Create `ROLLBACK.md`:

```markdown
# Rollback Procedures

## Quick Rollback (Last Deployment)
```bash
liquibase rollback-count 1
```

## Rollback to Specific Tag

```bash
liquibase rollback v123-20250115
```

## Database Restore

```bash
az sql db restore --name prod-backup-20250115
```

## Emergency Contacts

- DBA On-Call: +1-555-0123
- DevOps Lead: +1-555-0456

```

### Step 10.6: Team Processes

#### Code Review for Database Changes

Require pull request reviews:

1. **Settings** → **Branches**
2. **Add rule** for `main` branch
3. **Require pull request reviews before merging**: 1 review
4. **Require status checks**: Validate Pull Request

#### Document Workflow

Update README with team processes:

```markdown
## Deployment Process

1. Create feature branch
2. Add changelog in `database/changelog/changes/`
3. Create pull request
4. Wait for validation and review
5. Merge to main (deploys to dev/staging automatically)
6. Approve production deployment (within 24 hours)

## Approval Process

Production deployments require:
- ✅ Successful staging deployment
- ✅ 1 approval from senior engineer
- ✅ Verification in staging
- ✅ Deployment window compliance
```

#### Schedule Reviews

Regular team reviews:

- Weekly: Review failed deployments
- Monthly: Review approval patterns
- Quarterly: Review security practices

✅ **Checkpoint**: Production-ready with best practices!

## Part 11: Advanced Rollback Strategies

One of the most critical aspects of production database CI/CD is the ability to **safely and quickly rollback** when things go wrong. This section covers comprehensive rollback strategies and automation.

### Why Rollback Strategies Matter

**Production incident example:**

```
3:00 AM: New deployment breaks critical customer-facing feature
3:01 AM: Alerts start firing
3:05 AM: On-call engineer needs to rollback FAST
```

**With proper rollback strategy:**

```
✅ Automated rollback triggered: 2 minutes
✅ Service restored: 3 minutes
✅ Total downtime: 3 minutes
```

**Without proper rollback strategy:**

```
❌ Find deployment details: 10 minutes
❌ Figure out rollback commands: 15 minutes
❌ Manually execute rollback: 10 minutes
❌ Total downtime: 35+ minutes
❌ Stressed engineer, angry customers
```

### Step 11.1: Understanding Liquibase Rollback Options

Liquibase provides multiple rollback methods. Here's when to use each:

#### Option 1: Rollback by Tag

**Best for: Production deployments**

```bash
# Tag during deployment
liquibase tag "production-v123-20250120"

# Rollback to tag
liquibase rollback "production-v123-20250120"
```

**Pros:**

- ✅ Semantic and meaningful
- ✅ Easy to understand ("rollback to last known good")
- ✅ Works across multiple changesets
- ✅ Can rollback multiple deployments at once

**Cons:**

- ❌ Requires discipline to tag every deployment
- ❌ Must remember tag naming convention

**Use when:**

- Rolling back a full release
- Need to restore to a known good state
- Multiple changesets deployed together

#### Option 2: Rollback by Count

**Best for: Quick fixes and single changeset rollbacks**

```bash
# Rollback last 1 changeset
liquibase rollback-count 1

# Rollback last 3 changesets
liquibase rollback-count 3
```

**Pros:**

- ✅ Simple and fast
- ✅ No tag required
- ✅ Good for immediate "undo"

**Cons:**

- ❌ Easy to miscount
- ❌ Dangerous if other deployments happened in between
- ❌ No semantic meaning

**Use when:**

- Just deployed and immediately need to undo
- Only 1-2 changesets to undo
- You're certain what was deployed

#### Option 3: Rollback by Date

**Best for: Emergency rollbacks to a specific time**

```bash
# Rollback all changes after a specific date/time
liquibase rollback-to-date "2025-01-20 14:30:00"
```

**Pros:**

- ✅ Time-based is intuitive
- ✅ Good for "restore to yesterday"
- ✅ Works without tags

**Cons:**

- ❌ Timezone confusion
- ❌ Requires knowing exact deployment time
- ❌ Can be imprecise

**Use when:**

- Need to restore to a specific time
- Don't have tag information
- Emergency scenario

#### Comparison Table

| Method | Speed | Safety | Precision | Production Ready |
|--------|-------|--------|-----------|------------------|
| **Tag** | ⚡⚡⚡ | ✅ High | 🎯 Exact | ✅ Recommended |
| **Count** | ⚡⚡⚡ | ⚠️ Medium | 🎯 Exact | ⚠️ Use with caution |
| **Date** | ⚡⚡ | ⚠️ Medium | ⚠️ Approximate | ⚠️ Emergency only |

**Recommendation: Use tags for all production deployments.**

### Step 11.2: Automated Rollback on Failure

Add automatic rollback to your deployment workflow:

```yaml
# .github/workflows/deploy-with-rollback.yml
name: Deploy with Automatic Rollback

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options:
          - development
          - staging
          - production

jobs:
  deploy-with-rollback:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Liquibase
        uses: liquibase/setup-liquibase@v2
        with:
          version: '4.32.0'

      # Get current state before deployment
      - name: Record pre-deployment state
        id: pre-state
        run: |
          # Get the last deployment tag
          LAST_TAG=$(liquibase history \
            --url="${{ secrets[format('{0}_DB_URL', inputs.environment)] }}" \
            --username="${{ secrets[format('{0}_DB_USERNAME', inputs.environment)] }}" \
            --password="${{ secrets[format('{0}_DB_PASSWORD', inputs.environment)] }}" \
            --format=json | jq -r '.[0].tag // "no-tag"')

          echo "last_tag=$LAST_TAG" >> $GITHUB_OUTPUT
          echo "📍 Pre-deployment tag: $LAST_TAG"

      # Tag the current state as "before" marker
      - name: Create pre-deployment tag
        run: |
          TAG_NAME="before-deploy-${{ github.run_number }}"
          liquibase tag "$TAG_NAME" \
            --url="${{ secrets[format('{0}_DB_URL', inputs.environment)] }}" \
            --username="${{ secrets[format('{0}_DB_USERNAME', inputs.environment)] }}" \
            --password="${{ secrets[format('{0}_DB_PASSWORD', inputs.environment)] }}"

          echo "::notice::Created safety tag: $TAG_NAME"

      # Attempt deployment
      - name: Deploy changes
        id: deploy
        run: |
          liquibase update \
            --url="${{ secrets[format('{0}_DB_URL', inputs.environment)] }}" \
            --username="${{ secrets[format('{0}_DB_USERNAME', inputs.environment)] }}" \
            --password="${{ secrets[format('{0}_DB_PASSWORD', inputs.environment)] }}" \
            --changelog-file=database/changelog/changelog.xml
        continue-on-error: true

      # Tag successful deployment
      - name: Tag successful deployment
        if: steps.deploy.outcome == 'success'
        run: |
          TAG_NAME="deploy-${{ github.run_number }}-$(date +%Y%m%d-%H%M%S)"
          liquibase tag "$TAG_NAME" \
            --url="${{ secrets[format('{0}_DB_URL', inputs.environment)] }}" \
            --username="${{ secrets[format('{0}_DB_USERNAME', inputs.environment)] }}" \
            --password="${{ secrets[format('{0}_DB_PASSWORD', inputs.environment)] }}"

          echo "::notice::✅ Deployment successful. Tagged as: $TAG_NAME"

      # Run post-deployment health checks
      - name: Run health checks
        if: steps.deploy.outcome == 'success'
        id: health-check
        run: |
          echo "Running health checks..."

          # Check database connectivity
          liquibase status \
            --url="${{ secrets[format('{0}_DB_URL', inputs.environment)] }}" \
            --username="${{ secrets[format('{0}_DB_USERNAME', inputs.environment)] }}" \
            --password="${{ secrets[format('{0}_DB_PASSWORD', inputs.environment)] }}"

          # Verify critical tables exist
          # Add your specific health check queries here
          echo "✅ Health checks passed"
        continue-on-error: true

      # AUTOMATIC ROLLBACK on deployment failure
      - name: Rollback on deployment failure
        if: steps.deploy.outcome == 'failure'
        run: |
          echo "❌ Deployment failed. Initiating automatic rollback..."

          TAG_NAME="before-deploy-${{ github.run_number }}"
          liquibase rollback "$TAG_NAME" \
            --url="${{ secrets[format('{0}_DB_URL', inputs.environment)] }}" \
            --username="${{ secrets[format('{0}_DB_USERNAME', inputs.environment)] }}" \
            --password="${{ secrets[format('{0}_DB_PASSWORD', inputs.environment)] }}"

          echo "::warning::🔄 Rolled back to tag: $TAG_NAME"

      # AUTOMATIC ROLLBACK on health check failure
      - name: Rollback on health check failure
        if: steps.deploy.outcome == 'success' && steps.health-check.outcome == 'failure'
        run: |
          echo "❌ Health checks failed. Initiating automatic rollback..."

          TAG_NAME="before-deploy-${{ github.run_number }}"
          liquibase rollback "$TAG_NAME" \
            --url="${{ secrets[format('{0}_DB_URL', inputs.environment)] }}" \
            --username="${{ secrets[format('{0}_DB_USERNAME', inputs.environment)] }}" \
            --password="${{ secrets[format('{0}_DB_PASSWORD', inputs.environment)] }}"

          echo "::warning::🔄 Rolled back to tag: $TAG_NAME due to health check failure"

      # Final status
      - name: Report deployment status
        run: |
          if [ "${{ steps.deploy.outcome }}" == "success" ] && [ "${{ steps.health-check.outcome }}" == "success" ]; then
            echo "::notice::✅ Deployment completed successfully"
            exit 0
          else
            echo "::error::❌ Deployment failed and was rolled back"
            exit 1
          fi
```

**What this workflow does:**

1. **Records current state** before deployment
2. **Creates safety tag** to rollback to
3. **Attempts deployment** with error handling
4. **Tags successful** deployments for future reference
5. **Runs health checks** to verify deployment
6. **Automatically rolls back** if deployment or health checks fail
7. **Reports status** clearly

### Step 11.3: Manual Rollback Workflow

Create a dedicated rollback workflow for manual intervention:

```yaml
# .github/workflows/manual-rollback.yml
name: Manual Database Rollback

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to rollback'
        required: true
        type: choice
        options:
          - development
          - staging
          - production

      rollback_method:
        description: 'Rollback method'
        required: true
        type: choice
        options:
          - tag
          - count
          - date

      rollback_value:
        description: 'Value (tag name, count number, or date YYYY-MM-DD HH:MM:SS)'
        required: true
        type: string

      reason:
        description: 'Reason for rollback'
        required: true
        type: string

jobs:
  rollback:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Liquibase
        uses: liquibase/setup-liquibase@v2
        with:
          version: '4.32.0'

      # Show current deployment history
      - name: Show deployment history
        run: |
          echo "📜 Recent deployment history:"
          liquibase history --count=10 \
            --url="${{ secrets[format('{0}_DB_URL', inputs.environment)] }}" \
            --username="${{ secrets[format('{0}_DB_USERNAME', inputs.environment)] }}" \
            --password="${{ secrets[format('{0}_DB_PASSWORD', inputs.environment)] }}"

      # Generate rollback SQL (preview)
      - name: Preview rollback SQL
        id: preview
        run: |
          echo "🔍 Previewing rollback changes..."

          case "${{ inputs.rollback_method }}" in
            tag)
              liquibase rollback-sql "${{ inputs.rollback_value }}" \
                --url="${{ secrets[format('{0}_DB_URL', inputs.environment)] }}" \
                --username="${{ secrets[format('{0}_DB_USERNAME', inputs.environment)] }}" \
                --password="${{ secrets[format('{0}_DB_PASSWORD', inputs.environment)] }}" \
                --changelog-file=database/changelog/changelog.xml \
                > rollback-preview.sql
              ;;
            count)
              liquibase rollback-count-sql "${{ inputs.rollback_value }}" \
                --url="${{ secrets[format('{0}_DB_URL', inputs.environment)] }}" \
                --username="${{ secrets[format('{0}_DB_USERNAME', inputs.environment)] }}" \
                --password="${{ secrets[format('{0}_DB_PASSWORD', inputs.environment)] }}" \
                --changelog-file=database/changelog/changelog.xml \
                > rollback-preview.sql
              ;;
            date)
              liquibase rollback-to-date-sql "${{ inputs.rollback_value }}" \
                --url="${{ secrets[format('{0}_DB_URL', inputs.environment)] }}" \
                --username="${{ secrets[format('{0}_DB_USERNAME', inputs.environment)] }}" \
                --password="${{ secrets[format('{0}_DB_PASSWORD', inputs.environment)] }}" \
                --changelog-file=database/changelog/changelog.xml \
                > rollback-preview.sql
              ;;
          esac

          echo "Rollback SQL preview:"
          cat rollback-preview.sql

      # Upload preview for review
      - name: Upload rollback preview
        uses: actions/upload-artifact@v3
        with:
          name: rollback-preview-sql
          path: rollback-preview.sql

      # Execute rollback
      - name: Execute rollback
        run: |
          echo "🔄 Executing rollback..."
          echo "Method: ${{ inputs.rollback_method }}"
          echo "Value: ${{ inputs.rollback_value }}"
          echo "Reason: ${{ inputs.reason }}"

          case "${{ inputs.rollback_method }}" in
            tag)
              liquibase rollback "${{ inputs.rollback_value }}" \
                --url="${{ secrets[format('{0}_DB_URL', inputs.environment)] }}" \
                --username="${{ secrets[format('{0}_DB_USERNAME', inputs.environment)] }}" \
                --password="${{ secrets[format('{0}_DB_PASSWORD', inputs.environment)] }}" \
                --changelog-file=database/changelog/changelog.xml
              ;;
            count)
              liquibase rollback-count "${{ inputs.rollback_value }}" \
                --url="${{ secrets[format('{0}_DB_URL', inputs.environment)] }}" \
                --username="${{ secrets[format('{0}_DB_USERNAME', inputs.environment)] }}" \
                --password="${{ secrets[format('{0}_DB_PASSWORD', inputs.environment)] }}" \
                --changelog-file=database/changelog/changelog.xml
              ;;
            date)
              liquibase rollback-to-date "${{ inputs.rollback_value }}" \
                --url="${{ secrets[format('{0}_DB_URL', inputs.environment)] }}" \
                --username="${{ secrets[format('{0}_DB_USERNAME', inputs.environment)] }}" \
                --password="${{ secrets[format('{0}_DB_PASSWORD', inputs.environment)] }}" \
                --changelog-file=database/changelog/changelog.xml
              ;;
          esac

          echo "::notice::✅ Rollback completed successfully"

      # Verify post-rollback state
      - name: Verify rollback
        run: |
          echo "✅ Verifying post-rollback state..."
          liquibase status \
            --url="${{ secrets[format('{0}_DB_URL', inputs.environment)] }}" \
            --username="${{ secrets[format('{0}_DB_USERNAME', inputs.environment)] }}" \
            --password="${{ secrets[format('{0}_DB_PASSWORD', inputs.environment)] }}"

      # Log rollback for audit
      - name: Log rollback
        run: |
          cat << EOF > rollback-audit.json
          {
            "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
            "environment": "${{ inputs.environment }}",
            "method": "${{ inputs.rollback_method }}",
            "value": "${{ inputs.rollback_value }}",
            "reason": "${{ inputs.reason }}",
            "executed_by": "${{ github.actor }}",
            "workflow_run": "${{ github.run_id }}"
          }
          EOF

          cat rollback-audit.json

      - name: Upload audit log
        uses: actions/upload-artifact@v3
        with:
          name: rollback-audit-log
          path: rollback-audit.json
          retention-days: 365  # Keep for 1 year

      # Notify team
      - name: Notify team
        run: |
          echo "📧 Rollback notification:"
          echo "Environment: ${{ inputs.environment }}"
          echo "Executed by: ${{ github.actor }}"
          echo "Reason: ${{ inputs.reason }}"
          echo "Status: ✅ Completed"
          # Add Slack/email notification here
```

### Step 11.4: Rollback Testing Workflow

**Test rollback procedures BEFORE you need them:**

```yaml
# .github/workflows/test-rollback.yml
name: Test Rollback Procedures

on:
  schedule:
    # Test rollback every Monday at 10 AM
    - cron: '0 10 * * 1'
  workflow_dispatch:

jobs:
  test-rollback:
    runs-on: ubuntu-latest
    environment: development  # Always test in dev

    steps:
      - uses: actions/checkout@v3
      - uses: liquibase/setup-liquibase@v2

      # Deploy test changeset
      - name: Deploy test changeset
        run: |
          echo "Deploying test changeset..."
          cat > test-changeset.xml << 'EOF'
          <?xml version="1.0" encoding="UTF-8"?>
          <databaseChangeLog
              xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                  http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.3.xsd">

              <changeSet id="rollback-test-${{ github.run_number }}" author="ci">
                  <createTable tableName="rollback_test_${{ github.run_number }}">
                      <column name="id" type="int"/>
                  </createTable>
                  <rollback>
                      <dropTable tableName="rollback_test_${{ github.run_number }}"/>
                  </rollback>
              </changeSet>
          </databaseChangeLog>
          EOF

          liquibase update \
            --changelog-file=test-changeset.xml \
            --url="${{ secrets.DEV_DB_URL }}" \
            --username="${{ secrets.DEV_DB_USERNAME }}" \
            --password="${{ secrets.DEV_DB_PASSWORD }}"

      # Verify deployment
      - name: Verify test table exists
        run: |
          sqlcmd -S ${{ secrets.DEV_SERVER }} \
            -U ${{ secrets.DEV_DB_USERNAME }} \
            -P ${{ secrets.DEV_DB_PASSWORD }} \
            -Q "SELECT name FROM sys.tables WHERE name = 'rollback_test_${{ github.run_number }}'"

      # Test rollback
      - name: Test rollback
        run: |
          echo "Testing rollback..."
          liquibase rollback-count 1 \
            --changelog-file=test-changeset.xml \
            --url="${{ secrets.DEV_DB_URL }}" \
            --username="${{ secrets.DEV_DB_USERNAME }}" \
            --password="${{ secrets.DEV_DB_PASSWORD }}"

      # Verify rollback worked
      - name: Verify rollback
        run: |
          TABLE_COUNT=$(sqlcmd -S ${{ secrets.DEV_SERVER }} \
            -U ${{ secrets.DEV_DB_USERNAME }} \
            -P ${{ secrets.DEV_DB_PASSWORD }} \
            -Q "SELECT COUNT(*) FROM sys.tables WHERE name = 'rollback_test_${{ github.run_number }}'" \
            -h -1)

          if [ "$TABLE_COUNT" -eq "0" ]; then
            echo "::notice::✅ Rollback test PASSED - table was successfully removed"
            exit 0
          else
            echo "::error::❌ Rollback test FAILED - table still exists"
            exit 1
          fi

      # Report results
      - name: Report test results
        if: always()
        run: |
          if [ $? -eq 0 ]; then
            echo "✅ Rollback procedures are working correctly"
          else
            echo "❌ Rollback procedures failed - investigate immediately"
          fi
```

### Step 11.5: Emergency Rollback Runbook

Create a runbook for emergencies:

```markdown
# Emergency Rollback Runbook

## When to Use This
- Production deployment caused critical issues
- Need to rollback immediately
- Manual intervention required

## Prerequisites
- Access to GitHub Actions
- Production approval permissions
- Knowledge of last successful deployment

## Step-by-Step Emergency Rollback

### Step 1: Identify Last Good State (1 minute)

1. Go to **Actions** → **Workflows** → **Database CI/CD Pipeline**
2. Find last successful production deployment
3. Note the tag name (e.g., `production-v123-20250115`)

**Alternative:** Check database directly
```sql
SELECT TOP 1 TAG, DATEEXECUTED
FROM DATABASECHANGELOG
WHERE TAG IS NOT NULL
ORDER BY DATEEXECUTED DESC
```

### Step 2: Trigger Rollback Workflow (30 seconds)

1. Go to **Actions** → **Manual Database Rollback**
2. Click **Run workflow**
3. Fill in:
   - Environment: `production`
   - Rollback method: `tag`
   - Value: `production-v123-20250115`  (from Step 1)
   - Reason: Brief description of issue
4. Click **Run workflow**

### Step 3: Monitor Rollback (2-3 minutes)

1. Watch workflow progress
2. Check for successful completion
3. Verify health checks pass

### Step 4: Verify Application (2 minutes)

1. Test critical functionality
2. Check error rates in monitoring
3. Verify customer-facing features

### Step 5: Communicate (1 minute)

1. Post in #incidents channel
2. Notify stakeholders
3. Update status page

**Total time: ~7 minutes from decision to completion**

## Troubleshooting

### Rollback Fails

If rollback fails:

```bash
# Option 1: Try rollback-to-date
liquibase rollback-to-date "2025-01-15 10:00:00"

# Option 2: Rollback by count (if you know how many changesets)
liquibase rollback-count 3

# Option 3: Manual SQL rollback (last resort)
# Execute rollback SQL from deployment preview
```

### Health Checks Still Failing

1. Check database connectivity
2. Verify rollback completed successfully
3. May need additional cleanup

### Need DBA Help

Contact: DBA on-call +1-555-0123

```

### Step 11.6: Best Practices for Rollback-Friendly Changes

Not all database changes can be automatically rolled back. Write changes that support rollback:

#### ✅ Easily Rollback-able Changes

```xml
<!-- Adding a column (can be dropped) -->
<changeSet id="1" author="dev">
    <addColumn tableName="users">
        <column name="email" type="varchar(255)"/>
    </addColumn>
    <rollback>
        <dropColumn tableName="users" columnName="email"/>
    </rollback>
</changeSet>

<!-- Adding an index (can be dropped) -->
<changeSet id="2" author="dev">
    <createIndex tableName="users" indexName="idx_email">
        <column name="email"/>
    </createIndex>
    <rollback>
        <dropIndex tableName="users" indexName="idx_email"/>
    </rollback>
</changeSet>
```

#### ⚠️ Difficult to Rollback Changes

```xml
<!-- Dropping a column (data loss!) -->
<changeSet id="3" author="dev">
    <dropColumn tableName="users" columnName="legacy_field"/>
    <!-- Rollback requires re-adding column, but data is LOST -->
    <rollback>
        <addColumn tableName="users">
            <column name="legacy_field" type="varchar(255)"/>
        </addColumn>
        <!-- Cannot restore data! -->
    </rollback>
</changeSet>
```

**Solution: Two-phase migration**

```xml
<!-- Phase 1: Deprecate (don't drop yet) -->
<changeSet id="3a" author="dev">
    <addColumn tableName="users">
        <column name="legacy_field_deprecated" type="bit" defaultValueBoolean="true"/>
    </addColumn>
    <comment>Mark legacy_field as deprecated, prepare for removal</comment>
</changeSet>

<!-- Phase 2 (next release): Drop after confirming not needed -->
<changeSet id="3b" author="dev">
    <dropColumn tableName="users" columnName="legacy_field"/>
</changeSet>
```

#### Best Practice Checklist

- [ ] Always provide explicit `<rollback>` blocks
- [ ] Test rollback in dev before production
- [ ] Avoid data-destructive changes (DROP TABLE, DROP COLUMN)
- [ ] Use two-phase migrations for breaking changes
- [ ] Document why rollback isn't possible (if applicable)

### Step 11.7: Monitoring Rollback Health

Track rollback metrics:

```yaml
- name: Record rollback metrics
  run: |
    cat << EOF > rollback-metrics.json
    {
      "rollback_count": 1,
      "environment": "${{ inputs.environment }}",
      "time_to_rollback_seconds": ${{ job.duration }},
      "triggered_by": "${{ github.actor }}",
      "success": true
    }
    EOF

    # Send to monitoring system
    curl -X POST https://metrics.example.com/rollbacks \
      -H "Content-Type: application/json" \
      -d @rollback-metrics.json
```

**Key metrics to track:**

- Rollback frequency (goal: <1% of deployments)
- Time to rollback (goal: <5 minutes)
- Rollback success rate (goal: 100%)
- Reason for rollbacks (identify patterns)

✅ **Checkpoint**: You now have comprehensive rollback strategies and automation!

## Tutorial Complete

🎉 **Congratulations!** You've successfully implemented automated database CI/CD with Liquibase and GitHub Actions!

### What You've Learned

✅ **GitHub Actions Fundamentals**

- Created workflows with YAML
- Used secrets for sensitive data
- Configured environments with protection rules
- Implemented approval gates

✅ **Liquibase Automation**

- Automated database deployments
- Validated changelogs in CI/CD
- Tagged deployments for rollback
- Tracked deployment history

✅ **CI/CD Best Practices**

- Multi-environment pipeline (dev → staging → production)
- Pull request validation
- Manual deployment workflows
- Security hardening

✅ **SQL Server Integration**

- Configured JDBC connection strings
- Set up database authentication
- Implemented deployment workflows

### What You've Built

A complete CI/CD pipeline that:

```
Developer commits database change
    ↓
Validated in pull request
    ↓
Reviewed by team
    ↓
Merged to main
    ↓
Automatically deployed to dev
    ↓
Automatically deployed to staging
    ↓
Awaits approval (5 min wait timer)
    ↓
Approved by authorized person
    ↓
Deployed to production
    ↓
Tagged for rollback
    ↓
Audit trail recorded
```

### Deployment Metrics

After completing this tutorial, you've:

- Created 3 GitHub Environments
- Configured 9 secrets
- Built 4 workflows
- Deployed to 3 environments
- Implemented approval gates
- Set up audit logging

## Next Steps

### Level 1: Enhance Your Pipeline

1. **Add Slack Notifications**
   - Notify team on deployments
   - Alert on failures
   - Request approvals in Slack

2. **Implement Automated Tests**
   - SQL syntax validation
   - Data integrity checks
   - Application smoke tests

3. **Add Rollback Workflow**
   - One-click rollback
   - Automated testing after rollback
   - Notification on rollback

### Level 2: Advanced Topics

1. **Self-Hosted Runners**
   - Deploy to private networks
   - Use company infrastructure
   - Reduce costs for high volume

2. **Multiple Database Support**
   - Deploy to multiple databases
   - Use matrix strategy
   - Parallel deployments

3. **Advanced Liquibase Features**
   - Contexts and labels
   - Preconditions
   - Custom checks

### Level 3: Enterprise Features

1. **Liquibase Pro**
   - Stored procedures
   - Functions
   - Advanced rollback

2. **Compliance and Governance**
   - Change approval workflows
   - Automated compliance checks
   - Audit reporting

3. **Advanced Monitoring**
   - Deployment dashboards
   - Performance metrics
   - Alerting and paging

### Recommended Resources

**GitHub Actions:**

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Actions Marketplace](https://github.com/marketplace?type=actions)

**Liquibase:**

- [Liquibase Documentation](https://docs.liquibase.com/)
- [Liquibase Best Practices](https://www.liquibase.org/get-started/best-practices)
- [Liquibase Community Forum](https://forum.liquibase.org/)

**SQL Server:**

- [Azure SQL Database](https://learn.microsoft.com/en-us/azure/azure-sql/)
- [SQL Server on Linux](https://learn.microsoft.com/en-us/sql/linux/)

**DevOps:**

- [Database DevOps](https://www.atlassian.com/devops/database)
- [CI/CD Best Practices](https://www.atlassian.com/continuous-delivery)

## Quick Reference

### Common Workflows

#### Trigger Manual Deployment

1. Go to **Actions** tab
2. Click **Manual Deployment**
3. Click **Run workflow**
4. Select environment
5. Click **Run workflow**

#### Approve Production Deployment

1. Go to **Actions** tab
2. Click workflow run waiting for approval
3. Click **Review deployments**
4. Check **production**
5. Click **Approve and deploy**

#### View Deployment History

```sql
SELECT
    FILENAME,
    DATEEXECUTED,
    DEPLOYMENT_ID,
    TAG
FROM DATABASECHANGELOG
ORDER BY DATEEXECUTED DESC;
```

### Common Commands

#### Validate Changelog

```bash
liquibase validate --changelog-file=database/changelog/changelog.xml
```

#### Preview SQL

```bash
liquibase update-sql --changelog-file=database/changelog/changelog.xml
```

#### Rollback Last Change

```bash
liquibase rollback-count 1
```

#### Tag Current State

```bash
liquibase tag "v1.0.0"
```

### Troubleshooting Checklist

❓ **Workflow not triggering?**

- ✅ Check trigger conditions (`on:` section)
- ✅ Verify file paths in `paths:` filter
- ✅ Check branch name matches

❓ **Connection failed?**

- ✅ Verify secrets are configured
- ✅ Check database firewall rules
- ✅ Test connection string locally

❓ **Approval not required?**

- ✅ Verify environment protection rules
- ✅ Check environment name matches workflow
- ✅ Verify reviewers are specified

❓ **Deployment failed?**

- ✅ Check workflow logs
- ✅ Verify database permissions
- ✅ Test changelog locally

## Troubleshooting

### GitHub Actions Issues

#### Workflow Not Running

**Symptom**: Pushed code but workflow didn't trigger

**Checks:**

1. Verify workflow file is in `.github/workflows/`
2. Check YAML syntax (use YAML validator)
3. Verify trigger conditions match:

   ```yaml
   on:
     push:
       branches:
         - main  # Must push to this branch
       paths:
         - 'database/**'  # Must change files in this path
   ```

#### Secret Not Working

**Symptom**: `Error: secret DB_URL not found`

**Fixes:**

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Verify secret name matches exactly (case-sensitive!)
3. Check you're using correct syntax: `${{ secrets.SECRET_NAME }}`
4. If using environment secrets, verify environment name matches

### Database Connection Issues

#### Connection Refused

**Symptom**: `Could not connect to database`

**Checks:**

1. Database is running and accessible
2. Firewall allows connections from internet
3. Connection string is correct
4. Port is correct (default 1433 for SQL Server)

**For Azure SQL:**

```bash
# Add GitHub Actions IP ranges to firewall
az sql server firewall-rule create \
  --resource-group myResourceGroup \
  --server myserver \
  --name AllowGitHubActions \
  --start-ip-address 13.64.0.0 \
  --end-ip-address 13.107.255.255
```

#### Authentication Failed

**Symptom**: `Login failed for user`

**Checks:**

1. Username and password are correct in secrets
2. User exists in database
3. User has necessary permissions:

   ```sql
   -- Grant permissions
   GRANT CREATE TABLE TO liquibase_user;
   GRANT ALTER TO liquibase_user;
   GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::dbo TO liquibase_user;
   ```

### Liquibase Issues

#### Changeset Already Ran

**Symptom**: `Changeset has already been run`

**This is NORMAL!** Liquibase tracks deployed changes. This happens when:

- Re-running workflow without new changes
- Changeset already deployed to this environment

**Not an error** - workflow should still succeed with exit code 0.

#### Validation Failed

**Symptom**: `Could not parse changelog`

**Fixes:**

1. Check XML/SQL syntax
2. Verify file encoding (UTF-8)
3. Test locally: `liquibase validate`
4. Check file paths are correct

### Need Help?

**Community Resources:**

- [GitHub Community Forum](https://github.com/orgs/community/discussions)
- [Liquibase Forum](https://forum.liquibase.org/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/github-actions+liquibase)

**Documentation:**

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Liquibase Docs](https://docs.liquibase.com/)

## Appendix

### A. Repository Structure

Final project structure:

```
liquibase-github-actions-demo/
├── .github/
│   └── workflows/
│       ├── deploy-pipeline.yml      # Multi-environment pipeline
│       ├── validate-pr.yml          # Pull request validation
│       └── manual-deploy.yml        # Manual deployment
├── database/
│   └── changelog/
│       ├── changelog.xml            # Master changelog
│       ├── baseline/
│       │   └── V0000__baseline.xml  # Initial schema
│       └── changes/
│           ├── V0001__add_customer_phone.sql
│           └── V0002__add_customer_status.sql
├── .gitignore
├── README.md
└── liquibase.properties             # Local dev only (gitignored)
```

### B. Workflow Files Reference

#### deploy-pipeline.yml

Full multi-environment deployment with approval gates.

**Triggers:**

- Push to `main` branch with database changes
- Manual trigger

**Jobs:**

- `deploy-dev`: Deploy to development (automatic)
- `deploy-staging`: Deploy to staging (after dev succeeds)
- `deploy-production`: Deploy to production (requires approval)

#### validate-pr.yml

Validates database changes in pull requests.

**Triggers:**

- Pull request to `main` branch with database changes

**Jobs:**

- `validate`: Validate syntax, generate SQL preview

#### manual-deploy.yml

Manual deployment with environment selection.

**Triggers:**

- Manual only

**Jobs:**

- `deploy`: Deploy to selected environment

### C. SQL Server Connection Strings

#### Azure SQL Database

```
jdbc:sqlserver://SERVER.database.windows.net:1433;databaseName=DATABASE;encrypt=true;trustServerCertificate=false;loginTimeout=30
```

#### Local/On-Premises SQL Server

```
jdbc:sqlserver://SERVER:1433;databaseName=DATABASE;encrypt=true;trustServerCertificate=true;loginTimeout=30
```

#### With Azure AD Authentication

```
jdbc:sqlserver://SERVER.database.windows.net:1433;databaseName=DATABASE;encrypt=true;authentication=ActiveDirectoryPassword
```

### D. Security Checklist

Before going to production:

- ✅ All secrets configured (no hardcoded passwords)
- ✅ Production environment requires approval
- ✅ Deployment branches restricted to `main`
- ✅ Database user has minimal permissions (not db_owner)
- ✅ Firewall rules configured
- ✅ Audit logging enabled
- ✅ Backup strategy in place
- ✅ Rollback procedures documented
- ✅ Team trained on approval process
- ✅ Emergency contacts documented

### E. Glossary

**CI/CD**: Continuous Integration/Continuous Deployment - automated testing and deployment

**Workflow**: Automated process defined in YAML file

**Job**: Set of steps that run on the same runner

**Step**: Individual task within a job

**Runner**: Server that executes your workflows

**Secret**: Encrypted variable for sensitive data

**Environment**: Deployment target with protection rules

**Changeset**: Individual database change in Liquibase

**Changelog**: File containing changesets

**Baseline**: Initial database snapshot

---

**Tutorial Version**: 1.0
**Last Updated**: November 2025
**Tested With**:

- Liquibase 4.32.0
- GitHub Actions (ubuntu-latest)
- SQL Server 2022 / Azure SQL Database

**Feedback**: Open an issue on GitHub or contact the database team.

---

**You're now ready to implement professional database CI/CD!** 🚀

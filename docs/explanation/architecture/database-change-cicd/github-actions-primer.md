# GitHub Actions Primer: Understanding CI/CD for Beginners

## Table of Contents

- [What is GitHub Actions?](#what-is-github-actions)
- [Why Use GitHub Actions?](#why-use-github-actions)
- [Core Concepts](#core-concepts)
- [Understanding Workflows](#understanding-workflows)
- [Working with Secrets](#working-with-secrets)
- [Environments and Protection Rules](#environments-and-protection-rules)
- [Common Workflow Patterns](#common-workflow-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

## What is GitHub Actions?

**GitHub Actions** is a CI/CD (Continuous Integration/Continuous Deployment) platform built directly into GitHub. It automates tasks in your software development lifecycle without requiring external tools or services.

### What is CI/CD?

**CI/CD** stands for:

- **Continuous Integration (CI)**: Automatically testing and validating code changes as they're committed
- **Continuous Deployment (CD)**: Automatically deploying validated changes to your environments

**In simple terms**: Instead of manually running tests, building software, or deploying database changes every time you make a change, GitHub Actions does it automatically when you push code to your repository.

### Real-World Example

**Without GitHub Actions:**
1. Developer makes a database schema change
2. Developer manually connects to dev database
3. Developer manually runs Liquibase update
4. Developer manually tests the change
5. Developer manually connects to staging database
6. Developer manually runs Liquibase update again
7. Developer manually tests in staging
8. Developer repeats for production
9. If something goes wrong, developer must manually rollback

**With GitHub Actions:**
1. Developer makes a database schema change
2. Developer commits and pushes to GitHub
3. GitHub Actions automatically:
   - Validates the changelog
   - Deploys to dev environment
   - Runs tests
   - (After approval) deploys to staging
   - Runs tests
   - (After approval) deploys to production
4. Developer receives notification of success or failure

## Why Use GitHub Actions?

### Benefits

1. **Automation**: Eliminate repetitive manual tasks
2. **Consistency**: Same process every time, reducing human error
3. **Speed**: Deployments happen in minutes instead of hours
4. **Safety**: Built-in approval gates prevent accidental production changes
5. **Visibility**: See exactly what changed, when, and by whom
6. **No Infrastructure**: No need to set up Jenkins, TeamCity, or other CI/CD servers
7. **Free tier**: Generous free tier for public and private repositories

### When to Use GitHub Actions

✅ **Good Use Cases:**
- Automated testing of database changes
- Multi-environment deployments (dev → stage → prod)
- Enforcing code review before production changes
- Running database migrations on schedule
- Validating changelog syntax
- Generating documentation

❌ **When NOT to Use:**
- One-off manual database fixes (use local tools)
- Learning Liquibase basics (start locally first)
- Emergency hotfixes requiring immediate action
- When you need to see real-time output during development

## Core Concepts

### 1. Workflows

A **workflow** is an automated process defined in a YAML file. Workflows are stored in your repository at `.github/workflows/`.

**Example**: A workflow that deploys database changes whenever code is pushed to the `main` branch.

```yaml
name: Deploy Database Changes
on:
  push:
    branches:
      - main
```

### 2. Events

An **event** is something that triggers a workflow to run.

**Common Events:**
- `push`: Code is pushed to a branch
- `pull_request`: A pull request is opened or updated
- `workflow_dispatch`: Manual trigger from GitHub UI
- `schedule`: Run on a schedule (like a cron job)

**Example:**

```yaml
on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
  workflow_dispatch:  # Allows manual trigger
```

### 3. Jobs

A **job** is a set of steps that execute on the same runner. Workflows can have multiple jobs that run in parallel or sequentially.

**Example:**

```yaml
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Check changelog syntax
        run: liquibase validate

  deploy:
    needs: validate  # Wait for validate job to complete
    runs-on: ubuntu-latest
    steps:
      - name: Deploy changes
        run: liquibase update
```

### 4. Steps

**Steps** are individual tasks within a job. Each step can:
- Run a command
- Use a pre-built action from the GitHub Marketplace
- Run a script

**Example:**

```yaml
steps:
  - name: Checkout code
    uses: actions/checkout@v3

  - name: Set up Liquibase
    uses: liquibase/setup-liquibase@v2
    with:
      version: '4.32.0'

  - name: Deploy database changes
    run: liquibase update --changelog-file=changelog.xml
```

### 5. Runners

A **runner** is a server that executes your workflows. GitHub provides hosted runners (free tier available) or you can use self-hosted runners.

**Available Runners:**
- `ubuntu-latest` (most common)
- `windows-latest`
- `macos-latest`

### 6. Actions

**Actions** are reusable units of code that can be shared and used in workflows. They're like functions in programming.

**Popular Actions:**
- `actions/checkout@v3`: Checks out your repository code
- `actions/setup-java@v3`: Installs Java
- `liquibase/setup-liquibase@v2`: Installs Liquibase

## Understanding Workflows

### Basic Workflow Structure

```yaml
name: Workflow Name

on:
  # Events that trigger this workflow
  push:
    branches:
      - main

jobs:
  job-name:
    runs-on: ubuntu-latest

    steps:
      - name: Step 1
        uses: some/action@v1

      - name: Step 2
        run: echo "Hello World"
```

### Complete Example: Liquibase Deployment

```yaml
name: Liquibase Database Deployment

# Trigger on push to main or manual trigger
on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  deploy-dev:
    name: Deploy to Development
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
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

      - name: Run Liquibase Update
        run: |
          liquibase update \
            --changelog-file=database/changelog/changelog.xml \
            --url=${{ secrets.DEV_DB_URL }} \
            --username=${{ secrets.DEV_DB_USERNAME }} \
            --password=${{ secrets.DEV_DB_PASSWORD }}
```

### Workflow Execution Flow

```
Trigger Event (push/PR/manual)
    ↓
Workflow starts
    ↓
Job 1 starts on runner
    ↓
Step 1: Checkout code
    ↓
Step 2: Set up Java
    ↓
Step 3: Set up Liquibase
    ↓
Step 4: Run Liquibase update
    ↓
Job completes
    ↓
Workflow completes
    ↓
Notification sent (email/Slack)
```

## Working with Secrets

**Secrets** store sensitive information like database passwords, API keys, and tokens securely.

### Why Use Secrets?

❌ **NEVER do this:**

```yaml
- name: Connect to database
  run: liquibase update --password=MyPassword123
```

✅ **ALWAYS do this:**

```yaml
- name: Connect to database
  run: liquibase update --password=${{ secrets.DB_PASSWORD }}
```

### How to Add Secrets

1. **Navigate to Repository Settings:**
   - Go to your GitHub repository
   - Click **Settings** tab
   - Click **Secrets and variables** → **Actions**

2. **Add a New Secret:**
   - Click **New repository secret**
   - Name: `DB_PASSWORD`
   - Value: `YourActualPassword123`
   - Click **Add secret**

3. **Use in Workflow:**

```yaml
- name: Deploy to database
  run: |
    liquibase update \
      --url=${{ secrets.DB_URL }} \
      --username=${{ secrets.DB_USERNAME }} \
      --password=${{ secrets.DB_PASSWORD }}
```

### Secret Best Practices

✅ **Do:**
- Use secrets for ALL sensitive data
- Use descriptive names: `PROD_DB_PASSWORD` not just `PASSWORD`
- Create separate secrets for each environment
- Rotate secrets regularly

❌ **Don't:**
- Print secrets in logs: `echo ${{ secrets.PASSWORD }}`
- Commit secrets to version control
- Share secrets between environments
- Use the same password for dev, staging, and production

### Secret Naming Convention

```yaml
# Development environment
DEV_DB_URL
DEV_DB_USERNAME
DEV_DB_PASSWORD

# Staging environment
STAGE_DB_URL
STAGE_DB_USERNAME
STAGE_DB_PASSWORD

# Production environment
PROD_DB_URL
PROD_DB_USERNAME
PROD_DB_PASSWORD
```

## Environments and Protection Rules

**Environments** in GitHub Actions provide a way to organize deployments and add protection rules.

### What are Environments?

Environments represent deployment targets like:
- `development`
- `staging`
- `production`

### Why Use Environments?

1. **Approval Gates**: Require manual approval before deploying to production
2. **Environment Secrets**: Different credentials for each environment
3. **Deployment History**: See what was deployed where and when
4. **Branch Restrictions**: Only deploy from specific branches

### Creating an Environment

1. **Navigate to Repository Settings:**
   - Go to **Settings** → **Environments**

2. **Create Environment:**
   - Click **New environment**
   - Name: `production`
   - Configure protection rules

3. **Add Protection Rules:**
   - ✅ **Required reviewers**: Require 1-2 people to approve
   - ✅ **Wait timer**: Wait X minutes before deploying
   - ✅ **Deployment branches**: Only deploy from `main` branch

### Using Environments in Workflows

```yaml
jobs:
  deploy-dev:
    name: Deploy to Development
    runs-on: ubuntu-latest
    environment: development  # No approval required

    steps:
      - name: Deploy to dev
        run: liquibase update --url=${{ secrets.DB_URL }}

  deploy-prod:
    name: Deploy to Production
    needs: deploy-dev  # Must complete dev deployment first
    runs-on: ubuntu-latest
    environment: production  # Requires approval

    steps:
      - name: Deploy to production
        run: liquibase update --url=${{ secrets.DB_URL }}
```

### Deployment Flow with Environments

```
Code pushed to main
    ↓
Deploy to dev (automatic)
    ↓
Deploy to staging (automatic)
    ↓
[PAUSE - REQUIRES APPROVAL]
    ↓
Reviewer approves
    ↓
Deploy to production
```

### Environment-Specific Secrets

Each environment can have its own secrets:

**Development Environment:**
- `DB_URL`: `jdbc:sqlserver://dev-server:1433;databaseName=mydb_dev`
- `DB_USERNAME`: `dev_user`
- `DB_PASSWORD`: `dev_password`

**Production Environment:**
- `DB_URL`: `jdbc:sqlserver://prod-server:1433;databaseName=mydb_prod`
- `DB_USERNAME`: `prod_user`
- `DB_PASSWORD`: `prod_password_very_secure`

Same secret name, different values per environment!

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}  # 'development' or 'production'

    steps:
      - name: Deploy
        run: |
          liquibase update \
            --url=${{ secrets.DB_URL }} \
            --username=${{ secrets.DB_USERNAME }} \
            --password=${{ secrets.DB_PASSWORD }}
```

## Common Workflow Patterns

### Pattern 1: Deploy on Push to Main

**Use Case**: Automatically deploy to dev whenever code is pushed to main.

```yaml
name: Auto Deploy to Dev

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: development

    steps:
      - uses: actions/checkout@v3
      - uses: liquibase/setup-liquibase@v2
      - name: Deploy
        run: liquibase update --url=${{ secrets.DB_URL }}
```

### Pattern 2: Manual Deployment with Environment Selection

**Use Case**: Manually trigger deployment to any environment.

```yaml
name: Manual Deployment

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        type: choice
        options:
          - development
          - staging
          - production

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}

    steps:
      - uses: actions/checkout@v3
      - uses: liquibase/setup-liquibase@v2
      - name: Deploy to ${{ inputs.environment }}
        run: liquibase update --url=${{ secrets.DB_URL }}
```

### Pattern 3: Validation on Pull Request

**Use Case**: Validate changelog syntax before merging.

```yaml
name: Validate Changelog

on:
  pull_request:
    branches:
      - main

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - uses: liquibase/setup-liquibase@v2
      - name: Validate changelog
        run: liquibase validate
```

### Pattern 4: Multi-Environment Pipeline

**Use Case**: Deploy through dev → staging → production with approvals.

```yaml
name: Multi-Environment Pipeline

on:
  push:
    branches:
      - main

jobs:
  deploy-dev:
    runs-on: ubuntu-latest
    environment: development
    steps:
      - uses: actions/checkout@v3
      - uses: liquibase/setup-liquibase@v2
      - run: liquibase update --url=${{ secrets.DB_URL }}

  deploy-staging:
    needs: deploy-dev
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v3
      - uses: liquibase/setup-liquibase@v2
      - run: liquibase update --url=${{ secrets.DB_URL }}

  deploy-prod:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production  # Requires approval
    steps:
      - uses: actions/checkout@v3
      - uses: liquibase/setup-liquibase@v2
      - run: liquibase update --url=${{ secrets.DB_URL }}
```

## Best Practices

### 1. Start Simple

Begin with a single environment workflow, then add complexity:

```yaml
# Start here
name: Simple Deploy
on: push
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: liquibase update
```

Then evolve to multi-environment, approvals, notifications, etc.

### 2. Use Descriptive Names

❌ **Bad:**

```yaml
jobs:
  job1:
    steps:
      - name: Step 1
```

✅ **Good:**

```yaml
jobs:
  deploy-to-production:
    steps:
      - name: Checkout repository code
      - name: Deploy database changes to production
```

### 3. Add Comments

```yaml
# This workflow deploys database changes to all environments
# Dev and staging deploy automatically
# Production requires manual approval
name: Database Deployment Pipeline
```

### 4. Use Workflow Status Checks

```yaml
jobs:
  deploy:
    steps:
      - name: Deploy changes
        run: liquibase update

      # If deployment fails, the workflow stops here
      # This prevents bad changes from progressing
```

### 5. Enable Notifications

Configure notifications so you know when:
- ✅ Deployment succeeds
- ❌ Deployment fails
- ⏸️ Approval required

**Options:**
- Email (built-in)
- Slack integration
- Microsoft Teams integration
- GitHub mobile app notifications

### 6. Test Locally First

Before pushing to GitHub:

```bash
# Test your changelog locally
liquibase validate
liquibase update --url=jdbc:sqlserver://localhost:1433;...
```

### 7. Use Caching

Speed up workflows by caching dependencies:

```yaml
- name: Cache Liquibase
  uses: actions/cache@v3
  with:
    path: ~/.liquibase
    key: ${{ runner.os }}-liquibase-${{ hashFiles('**/liquibase.properties') }}
```

### 8. Implement Least Privilege

Only grant the minimum permissions needed:

```yaml
permissions:
  contents: read  # Can read code
  # No write permissions
```

### 9. Use Environment Protection

For production:
- ✅ Require 2 approvers
- ✅ Add a 5-minute wait timer
- ✅ Only allow deploys from `main` branch
- ✅ Limit who can approve

### 10. Monitor and Review

Regularly review:
- Deployment history
- Failed deployments
- Approval patterns
- Secret rotation

## Troubleshooting

### Workflow Not Triggering

**Problem**: Pushed code but workflow didn't run.

**Solutions:**

1. Check the workflow file is in `.github/workflows/`
2. Verify YAML syntax: Use a YAML validator
3. Check the trigger branch matches:

```yaml
on:
  push:
    branches:
      - main  # Make sure you pushed to 'main'
```

### Secret Not Found

**Problem**: `Error: secret DB_PASSWORD not found`

**Solutions:**

1. Verify secret name matches exactly (case-sensitive)
2. Check secret is added to repository (Settings → Secrets)
3. For environment-specific secrets, ensure environment name matches

### Connection Failed

**Problem**: `Error: Cannot connect to database`

**Solutions:**

1. Verify connection string in secret
2. Check database allows connections from GitHub IP ranges
3. Ensure firewall rules allow external access
4. Test connection string locally first

### Permission Denied

**Problem**: `Error: Permission denied`

**Solutions:**

1. Check database user has necessary permissions
2. Verify `username` and `password` secrets are correct
3. Ensure database user can connect from external IPs

### Approval Not Working

**Problem**: Production deployment doesn't require approval

**Solutions:**

1. Verify environment protection rules are configured
2. Check environment name in workflow matches exactly
3. Ensure reviewers are specified

## Next Steps

Now that you understand GitHub Actions basics, you're ready to:

1. **Set up your first workflow**: Start with a simple dev deployment
2. **Add environments**: Configure dev, staging, production
3. **Implement approvals**: Add protection rules for production
4. **Integrate with Liquibase**: Follow the SQL Server + Liquibase tutorial

### Recommended Learning Path

1. ✅ Read this primer (you are here!)
2. ➡️ Follow: [SQL Server + Liquibase + GitHub Actions Tutorial](../../../../tutorials/liquibase/sqlserver-liquibase-github-actions-tutorial.md)
3. ➡️ Review: [GitHub Actions Best Practices for Liquibase](../../../../best-practices/liquibase/github-actions.md)
4. ➡️ Explore: [GitHub Actions Documentation](https://docs.github.com/en/actions)

### Additional Resources

- **GitHub Actions Documentation**: https://docs.github.com/en/actions
- **Liquibase GitHub Actions**: https://github.com/liquibase/setup-liquibase
- **GitHub Actions Marketplace**: https://github.com/marketplace?type=actions
- **YAML Syntax Guide**: https://yaml.org/

---

**You're now ready to implement CI/CD for your databases!** The concepts you learned here apply not just to Liquibase, but to any automated workflow in GitHub Actions.

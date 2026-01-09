# End-to-End Tutorial: SQL Server + Liquibase from Local Containers to GitHub Actions CI/CD

## Table of Contents

- [Who This Tutorial Is For](#who-this-tutorial-is-for)
- [How This Tutorial Relates to the Other Tutorials](#how-this-tutorial-relates-to-the-other-tutorials)
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
- [Phase 3: CI/CD with GitHub Actions (Self-Hosted Runner)](#phase-3-cicd-with-github-actions-self-hosted-runner-in-docker)
  - [Step 9: Where the Databases Live for CI/CD](#step-9-where-the-databases-live-for-cicd)
  - [Step 10: Configure GitHub Secrets](#step-10-configure-github-secrets)
  - [Step 11: First CI Workflow – Deploy to Development (Self-Hosted)](#step-11-first-ci-workflow--deploy-to-development-self-hosted)
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

- [series-part1-baseline.md](./series-part1-baseline.md)
  - Local-only foundation: containers + helper scripts + project structure.
  - Establishes a baseline and explains core Liquibase concepts.

- [series-part2-manual.md](./series-part2-manual.md)
  - Local workflow for making changes and deploying manually.
  - Reinforces changeset discipline, rollback thinking, and safe iteration.

- [series-part3-cicd.md](./series-part3-cicd.md)
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
  - **(RHEL/CentOS Only)**: Ensure Docker is installed (use `dnf` repo) and if SELinux is enforcing, use `:z` on bind mounts (included in examples).
- **GitHub**
  - GitHub account
  - Ability to create repositories and configure Actions secrets
- **From the first Liquibase tutorial**
  - The helper scripts under
    `docs/courses/liquibase/scripts/` (for example `setup_tutorial.sh`, `cleanup_liquibase_tutorial.sh`, etc.)

> This tutorial assumes the repo containing these docs is already cloned locally and accessible via a path like `/path/to/your/repo`.

---

## Phase 1: Local Environment Using the Helper Scripts

This phase establishes your local Liquibase project with baseline deployment. **Follow Part 1 of the series tutorial** which provides detailed step-by-step instructions.

### Quick Start: Use Part 1 Tutorial

**Complete [Part 1: Baseline SQL Server + Liquibase Setup](./series-part1-baseline.md)** to:

1. ✅ Set up environment and aliases (Step 0)
2. ✅ Start SQL Server containers (Step 2)
3. ✅ Create databases and schemas (Step 1)
4. ✅ Populate development database (Step 2)
5. ✅ Generate baseline changelog (Step 4)
6. ✅ Deploy baseline to all environments (Step 5)

**Recommended approach:** Use the reusable scripts from `scripts/` directory:

```bash
# Set tutorial directory
export LIQUIBASE_TUTORIAL_DIR="/path/to/your/repo/docs/courses/liquibase"

# Source setup to configure aliases
source "$LIQUIBASE_TUTORIAL_DIR/scripts/setup_tutorial.sh"

# Run setup scripts in order
"$LIQUIBASE_TUTORIAL_DIR/scripts/setup_liquibase_environment.sh"
"$LIQUIBASE_TUTORIAL_DIR/scripts/start_mssql_containers.sh"
"$LIQUIBASE_TUTORIAL_DIR/scripts/create_orderdb_databases.sh"
"$LIQUIBASE_TUTORIAL_DIR/scripts/populate_dev_database.sh"
"$LIQUIBASE_TUTORIAL_DIR/scripts/generate_liquibase_baseline.sh"
"$LIQUIBASE_TUTORIAL_DIR/scripts/deploy_liquibase_baseline.sh"
```

> **Note:** These scripts are reusable across all tutorials. See [Scripts README](../scripts/README.md) for details.

**What you'll have after Phase 1:**

- Three SQL Server containers (`mssql_dev`, `mssql_stg`, `mssql_prd`) with `orderdb` database
- Liquibase project at `$LIQUIBASE_TUTORIAL_DATA_DIR` with baseline deployed
- Helper commands (`lb`, `sqlcmd-tutorial`) configured
- All environments tagged with `baseline`

**For detailed explanations** of each step, concepts, and troubleshooting, see [Part 1: Baseline](./series-part1-baseline.md).

Once Phase 1 is complete, proceed to Phase 2 to push your project to GitHub.

---

## Phase 2: From Local Project to GitHub Repository

This phase moves your local Liquibase project into Git and GitHub. **Follow Part 3 of the series tutorial** which covers this in detail.

### Quick Start: Use Part 3 Tutorial

**Follow [Part 3: From Local Liquibase Project to GitHub Actions CI/CD](./series-part3-cicd.md), starting at "Phase 2: From Local Project to GitHub Repository":**

- **Step 6:** Create a GitHub Repository
- **Step 7:** Initialize Git and Push Initial Project (if you're the first person)
- **Step 8:** Create Your Personal Branch (if working in a multi-user setup)

**Key steps:**

1. Create a GitHub repository (private recommended)
2. Initialize Git in `$LIQUIBASE_TUTORIAL_DATA_DIR`
3. Create `.gitignore` to exclude properties files with passwords
4. Commit and push your Liquibase project

> **Important:** Never commit `env/liquibase.*.properties` files that contain passwords. CI/CD will use GitHub Secrets instead.

**For detailed instructions** including `.gitignore` template and multi-user branch setup, see [Part 3, Phase 2](./series-part3-cicd.md#phase-2-from-local-project-to-github-repository).

---

## Phase 3: CI/CD with GitHub Actions (Self-Hosted Runner)

This phase sets up automated CI/CD pipelines using GitHub Actions. **Follow Part 3 of the series tutorial** which provides comprehensive CI/CD setup instructions.

### Quick Start: Use Part 3 Tutorial

**Follow [Part 3: From Local Liquibase Project to GitHub Actions CI/CD](./series-part3-cicd.md), starting at "Phase 3: CI/CD with GitHub Actions":**

- **Step 9:** Where the Databases Live for CI/CD
- **Step 10:** Set Up a Self-Hosted Runner in a Docker Container
- **Step 11:** Configure GitHub Secrets
- **Step 12:** First CI Workflow – Deploy to Development (Self-Hosted)
- **Step 13:** Multi-Environment Pipeline (Dev → Stg → Prd)

**Key steps:**

1. **Set up self-hosted runner** (Step 10)
   - Create Docker network for runner and SQL Server containers
   - Run GitHub Actions runner container
   - Verify runner appears as "Online" in GitHub

2. **Configure GitHub Secrets** (Step 11)
   - Add `DEV_DB_URL`, `DEV_DB_USERNAME`, `DEV_DB_PASSWORD`
   - Add `STG_DB_URL`, `STG_DB_USERNAME`, `STG_DB_PASSWORD`
   - Add `PRD_DB_URL`, `PRD_DB_USERNAME`, `PRD_DB_PASSWORD`
   - Use JDBC URLs pointing to your SQL Server containers

3. **Create workflows** (Steps 12-13)
   - Single-environment workflow for development
   - Multi-environment pipeline (dev → staging → production)
   - Configure GitHub Environments with approval gates

**For detailed instructions** including:
- Self-hosted runner setup and troubleshooting
- Workflow YAML examples
- Environment protection rules
- Branch-based workflows for multi-user setups

See [Part 3, Phase 3](./series-part3-cicd.md#phase-3-cicd-with-github-actions-self-hosted-runner-in-docker).

> **Note:** Part 3 uses three separate SQL Server containers (`mssql_dev`, `mssql_stg`, `mssql_prd`) which matches the setup from Part 1. The runner connects to these containers via Docker networking.

---

## Phase 4: Integrating Local Helper Scripts with CI/CD Practices

This phase covers best practices for using local helper scripts alongside CI/CD. **Follow Part 3 of the series tutorial** for detailed guidance.

### Quick Start: Use Part 3 Tutorial

**Follow [Part 3: From Local Liquibase Project to GitHub Actions CI/CD](./series-part3-cicd.md), starting at "Phase 4: Integrating Local Helper Scripts with CI/CD Practices":**

- **Step 14:** Using `lb` and `sqlcmd-tutorial` Alongside GitHub Actions
- **Step 15:** Recommended Daily Workflow (Branch-Based)

**Key concepts:**

- **Local helper scripts** (`lb`, `sqlcmd-tutorial`) remain valuable for:
  - Testing changesets locally before committing
  - Running `status`, `updateSQL`, or `rollback` commands
  - Inspecting schema and data in containers
  - Debugging issues before they reach CI/CD

- **Daily workflow:**
  1. Create/modify changeset locally
  2. Test with helper scripts (`lb -e dev -- update`, etc.)
  3. Commit and push to trigger CI/CD
  4. Monitor pipeline execution
  5. Handle rollbacks if needed (see Part 2)

> **Best practice:** Treat local helper scripts + containers as your **sandbox** and GitHub Actions as your **pipeline**. Both should use the same changelog and changeset discipline.

**For detailed workflow examples** including branch-based workflows for multi-user setups, see [Part 3, Phase 4](./series-part3-cicd.md#phase-4-integrating-local-helper-scripts-with-cicd-practices).

---

## Phase 5: Best Practices and Improvements

This section summarizes best practices for production use. **See Part 3 of the series tutorial** for detailed best practices.

### Quick Reference: Best Practices

**Follow [Part 3: From Local Liquibase Project to GitHub Actions CI/CD](./series-part3-cicd.md), "Phase 5: Best Practices and Improvements":**

- **Security and Accounts**
  - Avoid `sa` account for production
  - Create dedicated service accounts with minimal permissions
  - Use GitHub Secrets for all credentials
  - Never commit passwords to Git

- **Rollback and Safety**
  - Prefer tag-based rollbacks
  - Always define explicit rollback blocks
  - Use two-phase migrations for destructive operations

- **Drift Detection and Environments**
  - Use `diff` and `diffChangeLog` commands regularly
  - Never skip dev → staging → production promotion path
  - Gate production deployments with approvals

**For comprehensive best practices** including security guidelines, rollback strategies, and drift detection workflows, see [Part 3, Phase 5](./series-part3-cicd.md#phase-5-best-practices-and-improvements).

### Where to Go Deeper

- **Local setup, baseline, and manual workflows:** [Part 1](./series-part1-baseline.md) and [Part 2](./series-part2-manual.md)
- **CI/CD automation and best practices:** [Part 3](./series-part3-cicd.md)
- **Advanced scenarios:** See individual tutorial parts for detailed explanations

---

## Summary

This end-to-end guide provides a **navigation path** through the modular tutorial series:

1. **Phase 1:** Complete [Part 1](./series-part1-baseline.md) to set up local environment and baseline
2. **Phase 2:** Follow [Part 3, Phase 2](./series-part3-cicd.md#phase-2-from-local-project-to-github-repository) to push project to GitHub
3. **Phase 3:** Follow [Part 3, Phase 3](./series-part3-cicd.md#phase-3-cicd-with-github-actions-self-hosted-runner-in-docker) to set up CI/CD
4. **Phase 4:** Follow [Part 3, Phase 4](./series-part3-cicd.md#phase-4-integrating-local-helper-scripts-with-cicd-practices) for daily workflow
5. **Phase 5:** Review [Part 3, Phase 5](./series-part3-cicd.md#phase-5-best-practices-and-improvements) for best practices

**All tutorials use the same reusable scripts** from `scripts/` directory, ensuring consistency across the entire course.

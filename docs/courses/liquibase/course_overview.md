# Liquibase Course Overview

## Course Description

This comprehensive course teaches database change management using Liquibase with Microsoft SQL Server. You'll learn to version control your database schema, deploy changes safely across environments, and integrate database CI/CD into your workflow.

## Learning Objectives

By completing this course, you will be able to:

1. **Set up a Liquibase project** with proper structure and multi-environment configurations
2. **Generate a baseline** from an existing database
3. **Create and deploy changesets** using Formatted SQL
4. **Implement rollback strategies** for safe deployments
5. **Detect and handle drift** between environments
6. **Integrate with CI/CD** using GitHub Actions

## Target Audience

- Database administrators transitioning to DevOps practices
- Developers responsible for database schema changes
- DevOps engineers implementing database CI/CD
- Teams adopting infrastructure-as-code for databases

## Prerequisites

- Docker or Podman installed
- Basic SQL knowledge
- Command line familiarity
- Git basics (for Part 3)

## Course Structure

| Part | Title | Topics |
|------|-------|--------|
| **1** | [Baseline Setup](./learning-paths/series-part1-baseline.md) | Environment setup, baseline generation, multi-env deploy |
| **2** | [Manual Lifecycle](./learning-paths/series-part2-manual.md) | Changesets, rollbacks, drift detection, tags |
| **3** | [CI/CD Automation](./learning-paths/series-part3-cicd.md) | GitHub Actions, secrets, multi-env workflows |

## Supplemental Guides

- [Self-Hosted Runner Setup](./learning-paths/guide-runner-setup.md) - Detailed runner configuration
- [End-to-End Pipeline](./learning-paths/guide-end-to-end-pipeline.md) - Complete local-to-CI workflow

## Quick Start

```bash
# 1. Set tutorial directory
export LIQUIBASE_TUTORIAL_DIR="/path/to/repo/docs/courses/liquibase"

# 2. Run setup
source "$LIQUIBASE_TUTORIAL_DIR/scripts/setup_tutorial.sh"

# 3. Start containers
$LIQUIBASE_TUTORIAL_DIR/scripts/start_mssql_containers.sh

# 4. Validate environment
$LIQUIBASE_TUTORIAL_DIR/scripts/validate_tutorial.sh
```

## Technology Stack

- **Database:** Microsoft SQL Server 2025
- **Migration Tool:** Liquibase 4.x (4.32.0+)
- **Containers:** Docker/Podman
- **CI/CD:** GitHub Actions (Part 3)
- **Changelog Format:** Formatted SQL

## Support

- See the [Troubleshooting Guide](./troubleshooting.md) for common issues
- Check container logs: `podman logs mssql_dev`
- Validate environment: `./scripts/validate_tutorial.sh`

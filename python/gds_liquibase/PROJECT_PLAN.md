# GDS Liquibase CI/CD Implementation Project Plan

## Table of Contents

- [Executive Summary](#executive-summary)
- [1. Project Overview](#1-project-overview)
  - [1.1 Objectives](#11-objectives)
  - [1.2 Scope](#12-scope)
  - [1.3 Success Criteria](#13-success-criteria)
- [2. Technology Stack](#2-technology-stack)
  - [2.1 Core Technologies](#21-core-technologies)
  - [2.2 GitHub Actions Integration](#22-github-actions-integration)
- [3. Architecture & Design](#3-architecture--design)
  - [3.1 Package Structure](#31-package-structure)
  - [3.2 Containerization Architecture](#32-containerization-architecture)
  - [3.3 GitHub Actions Workflows](#33-github-actions-workflows)
  - [3.4 Database Support Matrix](#34-database-support-matrix)
- [4. Implementation Phases](#4-implementation-phases)
  - [Phase 1: Foundation & Setup (Week 1-2)](#phase-1-foundation--setup-week-1-2)
  - [Phase 2: GitHub Actions Workflows (Week 3-4)](#phase-2-github-actions-workflows-week-3-4)
  - [Phase 3: Python Wrapper Implementation (Week 5-6)](#phase-3-python-wrapper-implementation-week-5-6)
  - [Phase 4: Testing & Documentation (Week 7-8)](#phase-4-testing--documentation-week-7-8)
- [5. Best Practices Implementation](#5-best-practices-implementation)
  - [5.1 Changelog Organization](#51-changelog-organization)
  - [5.2 Changeset Best Practices](#52-changeset-best-practices)
  - [5.3 Naming Conventions](#53-naming-conventions)
  - [5.4 Security Best Practices](#54-security-best-practices)
  - [5.5 Deployment Strategies](#55-deployment-strategies)
- [6. Integration with Existing Packages](#6-integration-with-existing-packages)
  - [6.1 GDS Package Integration](#61-gds-package-integration)
  - [6.2 Shared Configuration](#62-shared-configuration)
- [7. Monitoring & Observability](#7-monitoring--observability)
  - [7.1 Deployment Metrics](#71-deployment-metrics)
  - [7.2 Logging Strategy](#72-logging-strategy)
  - [7.3 Alerting](#73-alerting)
- [8. Risk Management](#8-risk-management)
  - [8.1 Identified Risks](#81-identified-risks)
  - [8.2 Rollback Plan](#82-rollback-plan)
- [9. Timeline & Milestones](#9-timeline--milestones)
  - [Week 1-2: Foundation](#week-1-2-foundation)
  - [Week 3-4: GitHub Actions](#week-3-4-github-actions)
  - [Week 5-6: Python Implementation](#week-5-6-python-implementation)
  - [Week 7-8: Testing & Documentation](#week-7-8-testing--documentation)
  - [Week 9: Review & Refinement](#week-9-review--refinement)
  - [Week 10: Production Readiness](#week-10-production-readiness)
- [10. Success Metrics](#10-success-metrics)
  - [10.1 Technical Metrics](#101-technical-metrics)
  - [10.2 Process Metrics](#102-process-metrics)
- [11. Future Enhancements](#11-future-enhancements)
  - [Phase 2 Enhancements (Post-Launch)](#phase-2-enhancements-post-launch)
- [12. References](#12-references)
  - [12.1 Official Documentation](#121-official-documentation)
  - [12.2 Key Research Findings](#122-key-research-findings)
  - [12.3 Existing GitHub Actions Examples](#123-existing-github-actions-examples)
- [13. Appendix](#13-appendix)
  - [A. Sample Changelog](#a-sample-changelog)
  - [B. Sample liquibase.properties](#b-sample-liquibaseproperties)
  - [C. GitHub Secrets Required](#c-github-secrets-required)
  - [D. MongoDB-Specific Configuration](#d-mongodb-specific-configuration)
  - [E. Containerization & Kubernetes Deployment](#e-containerization--kubernetes-deployment)
- [Document Control](#document-control)

---

## Executive Summary

This document outlines a comprehensive plan to implement database change management CI/CD using Liquibase with GitHub Actions for the dbtools repository. The implementation will provide automated, reliable, and auditable database schema versioning and deployment across multiple database platforms (PostgreSQL, MSSQL, MongoDB, Snowflake).

**Project Goal**: Create a production-ready Liquibase integration package (`gds_liquibase`) that enables automated database change management through GitHub Actions workflows.

---

## 1. Project Overview

### 1.1 Objectives

- **Primary**: Implement Liquibase-based database change management with GitHub Actions CI/CD
- **Secondary**: Integrate with existing gds_* database packages
- **Tertiary**: Establish best practices for database versioning and deployment automation

### 1.2 Scope

**In Scope**:

- Liquibase wrapper Python package (gds_liquibase)
- GitHub Actions workflows for database migrations
- Support for PostgreSQL, MSSQL, Snowflake, MongoDB databases
- Changelog management and validation
- Rollback capabilities
- Multi-environment deployment (dev, staging, production)
- Containerized Liquibase execution (Docker)
- Kubernetes deployment with Helm charts
- Kubernetes CronJob and Job-based migration execution

**Out of Scope**:

- Manual deployment processes
- Legacy database migration tools
- Custom container orchestration platforms (non-Kubernetes)

### 1.3 Success Criteria

1. Automated changelog validation on pull requests
2. Successful database deployments to dev/staging/production environments
3. Zero-downtime deployment capability
4. Complete audit trail of all database changes
5. Rollback capability for all changes
6. Integration with existing gds_postgres, gds_mssql, gds_snowflake packages

---

## 2. Technology Stack

### 2.1 Core Technologies

- **Liquibase**: Version 5.0.0+ (Community or Secure Edition)
- **GitHub Actions**: Official `liquibase/setup-liquibase@v2` action
- **Python**: 3.8+ for wrapper utilities
- **Database Drivers**: Platform-specific JDBC drivers
- **Container Runtime**: Docker for containerized execution
- **Container Orchestration**: Kubernetes 1.24+
- **Package Manager**: Helm 3.x for Kubernetes deployments
- **Base Images**:
  - `liquibase/liquibase:5.0` (official Liquibase container)
  - `python:3.11-slim` (for custom wrapper images)

### 2.2 GitHub Actions Integration

Based on research of `liquibase/setup-liquibase` repository:

**Key Features**:

- Intelligent caching for faster workflow runs
- Cross-platform support (Linux, Windows, macOS)
- Support for both Community and Secure editions
- Automatic path transformation for GitHub Actions compatibility
- Environment variable support for secure credential management

**Recommended Action Version**: `@v2` (automatically receives non-breaking updates)

---

## 3. Architecture & Design

### 3.1 Package Structure

```
gds_liquibase/
├── gds_liquibase/
│   ├── __init__.py
│   ├── changelog_manager.py      # Changelog generation and management
│   ├── migration_runner.py       # Python wrapper for Liquibase commands
│   ├── validator.py              # Changelog validation utilities
│   ├── rollback_manager.py       # Rollback strategy implementation
│   └── config.py                 # Configuration management
├── tests/
│   ├── test_changelog_manager.py
│   ├── test_migration_runner.py
│   ├── test_validator.py
│   └── fixtures/
│       └── sample_changelogs/
├── examples/
│   ├── basic_migration/
│   ├── multi_environment/
│   └── rollback_scenarios/
├── docs/
│   ├── QUICKSTART.md
│   ├── BEST_PRACTICES.md
│   ├── CHANGELOG_GUIDE.md
│   └── TROUBLESHOOTING.md
├── changelogs/                   # Default changelog directory
│   ├── dev/
│   ├── staging/
│   └── production/
├── liquibase.properties          # Liquibase configuration template
├── pyproject.toml
├── setup.py
├── MANIFEST.in
└── README.md
```

### 3.2 Containerization Architecture

#### 3.2.1 Docker Container Structure

```dockerfile
# Multi-stage build for optimized Liquibase container
FROM liquibase/liquibase:5.0 as liquibase-base

# Add database drivers and extensions
FROM liquibase-base
WORKDIR /liquibase

# Copy changelogs
COPY changelogs/ /liquibase/changelogs/

# Copy liquibase properties
COPY liquibase.properties /liquibase/

# Install additional drivers if needed
RUN lpm add postgresql mongodb mssql snowflake --global

# Set entrypoint
ENTRYPOINT ["liquibase"]
CMD ["--help"]
```

#### 3.2.2 Kubernetes Deployment Patterns

**Deployment Options**:

1. **Kubernetes Job**: One-time migration execution
2. **Kubernetes CronJob**: Scheduled validation/status checks
3. **Init Container**: Run migrations before application deployment
4. **Helm Chart**: Packaged deployment with configurable values

**Helm Chart Structure**:

```
helm/
├── liquibase/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── values-dev.yaml
│   ├── values-staging.yaml
│   ├── values-production.yaml
│   └── templates/
│       ├── configmap.yaml          # Liquibase properties
│       ├── secret.yaml             # Database credentials
│       ├── job-migrate.yaml        # Migration job
│       ├── job-rollback.yaml       # Rollback job
│       ├── cronjob-validate.yaml   # Scheduled validation
│       ├── serviceaccount.yaml     # RBAC service account
│       └── _helpers.tpl            # Template helpers
```

### 3.3 GitHub Actions Workflows

#### 3.3.1 Workflow Files Structure

```
.github/workflows/
├── liquibase-validate.yml        # Validate changelogs on PR
├── liquibase-deploy-dev.yml      # Auto-deploy to dev on merge to main
├── liquibase-deploy-staging.yml  # Deploy to staging (manual trigger)
├── liquibase-deploy-prod.yml     # Deploy to production (manual trigger)
├── liquibase-rollback.yml        # Rollback workflow (manual trigger)
├── liquibase-status.yml          # Check migration status
├── liquibase-diff.yml            # Generate diff reports
├── docker-build.yml              # Build and push container images
└── k8s-deploy-helm.yml           # Deploy to Kubernetes via Helm
```

### 3.4 Database Support Matrix

| Database | Driver | Liquibase Support | Priority |
|----------|--------|-------------------|----------|
| PostgreSQL | org.postgresql:postgresql | Native | High |
| MSSQL | com.microsoft.sqlserver:mssql-jdbc | Native | High |
| Snowflake | net.snowflake:snowflake-jdbc | Native | High |
| MongoDB | org.mongodb:mongodb-driver-sync | Extension (liquibase-mongodb) | High |
| H2 (Testing) | com.h2database:h2 | Native | Medium |

---

## 4. Implementation Phases

### Phase 1: Foundation & Setup (Week 1-2)

#### 4.1 Package Scaffolding

**Tasks**:

1. Create Python package structure
2. Set up `pyproject.toml` with dependencies
3. Create initial module files
4. Configure testing framework (pytest)

**Deliverables**:

- Functional Python package installable via pip
- Basic test suite structure
- Documentation templates

#### 4.2 Liquibase Integration Layer

**Tasks**:

1. Create `migration_runner.py` with subprocess wrappers for Liquibase commands
2. Implement configuration management for database connections
3. Add support for environment-specific properties files
4. Create utility functions for common operations

**Key Methods**:

- `run_update()` - Apply pending changes
- `run_validate()` - Validate changelog
- `run_status()` - Check migration status
- `run_rollback()` - Rollback changes
- `generate_changelog()` - Generate changelog from existing database

---

### Phase 2: GitHub Actions Workflows (Week 3-4)

#### 4.3 Workflow Development

**4.3.1 Changelog Validation Workflow**

Validates changelogs on pull requests and generates SQL previews.

📄 **See**: [`examples/workflows/liquibase-validate.yml`](examples/workflows/liquibase-validate.yml)

**4.3.2 Development Deployment Workflow**

Automatically deploys changes to development environment on push to main branch.

📄 **See**: [`examples/workflows/liquibase-deploy-dev.yml`](examples/workflows/liquibase-deploy-dev.yml)

**4.3.3 Production Deployment Workflow**

Manual workflow for production deployments with validation and backup tags.

📄 **See**: [`examples/workflows/liquibase-deploy-prod.yml`](examples/workflows/liquibase-deploy-prod.yml)

Key features:

- Manual trigger with workflow_dispatch
- Pre-deployment validation
- Automatic backup tag creation
        env:
          DB_URL: ${{ secrets.PROD_DB_URL }}
          DB_USERNAME: ${{ secrets.PROD_DB_USERNAME }}
          DB_PASSWORD: ${{ secrets.PROD_DB_PASSWORD }}
        run: |
          liquibase tag "backup-before-${{ github.event.inputs.deployment_tag }}" \
            --url=$DB_URL \
            --username=$DB_USERNAME \
            --password=$DB_PASSWORD

      - name: Deploy Changes
        env:
          DB_URL: ${{ secrets.PROD_DB_URL }}
          DB_USERNAME: ${{ secrets.PROD_DB_USERNAME }}
          DB_PASSWORD: ${{ secrets.PROD_DB_PASSWORD }}
        run: |
          liquibase update \
            --changelog-file=${{ github.event.inputs.changelog_file }} \
            --url=$DB_URL \
            --username=$DB_USERNAME \
            --password=$DB_PASSWORD

      - name: Tag Deployment
        env:
          DB_URL: ${{ secrets.PROD_DB_URL }}
          DB_USERNAME: ${{ secrets.PROD_DB_USERNAME }}
          DB_PASSWORD: ${{ secrets.PROD_DB_PASSWORD }}
        run: |
          liquibase tag "${{ github.event.inputs.deployment_tag }}" \
            --url=$DB_URL \
            --username=$DB_USERNAME \
            --password=$DB_PASSWORD

      - name: Verify Deployment
        env:
          DB_URL: ${{ secrets.PROD_DB_URL }}
          DB_USERNAME: ${{ secrets.PROD_DB_USERNAME }}
          DB_PASSWORD: ${{ secrets.PROD_DB_PASSWORD }}
        run: |
          liquibase status --verbose \
            --changelog-file=${{ github.event.inputs.changelog_file }} \
            --url=$DB_URL \
            --username=$DB_USERNAME \
            --password=$DB_PASSWORD

```

**4.3.4 Rollback Workflow**

Rollback database changes to a previous tagged state.

📄 **See**: [`examples/workflows/liquibase-rollback.yml`](examples/workflows/liquibase-rollback.yml)

Key features:
- Environment selection (dev/staging/prod)
- Generates rollback SQL preview
- Uploads SQL as artifact before execution

---

### Phase 3: Python Wrapper Implementation (Week 5-6)

#### 4.4 Core Module Development

**4.4.1 Configuration Management (`config.py`)**

Manages Liquibase configuration from properties files or environment variables.

📄 **See**: [`examples/python/liquibase_config.py`](examples/python/liquibase_config.py)

Key features:
- Load from liquibase.properties file
- Load from environment variables
- Convert to command-line arguments

**4.4.2 Migration Runner (`migration_runner.py`)**

Python wrapper for executing Liquibase commands.

📄 **See**: [`examples/python/migration_runner.py`](examples/python/migration_runner.py)

Key methods:
- `update()` - Apply pending changes
- `rollback(tag)` - Rollback to tag
- `validate()` - Validate changelogs
- `status()` - Get migration status
- `tag(name)` - Tag current state
- `diff()` - Compare databases

    def status(self, verbose: bool = False) -> subprocess.CompletedProcess:
        """Get migration status."""
        args = self._build_base_args()
        args.append('status')

        if verbose:
            args.append('--verbose')

        return self._execute(args)

    def generate_changelog(self, output_file: Path) -> subprocess.CompletedProcess:
        """Generate changelog from existing database."""
        args = self._build_base_args()
        args.extend(['generate-changelog', f'--changelog-file={output_file}'])

        return self._execute(args)

    def diff_changelog(self, reference_url: str,
                       output_file: Path) -> subprocess.CompletedProcess:
        """Generate diff changelog between databases."""
        args = self._build_base_args()
        args.extend([
            'diff-changelog',
            f'--reference-url={reference_url}',
            f'--changelog-file={output_file}'
        ])

        return self._execute(args)

    def _build_base_args(self) -> List[str]:
        """Build base Liquibase arguments from config."""
        # Implementation
        pass

    def _execute(self, args: List[str]) -> subprocess.CompletedProcess:
        """Execute Liquibase command."""
        logger.info(f"Executing: {' '.join(args)}")

        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            logger.error(f"Liquibase command failed: {result.stderr}")
            raise LiquibaseExecutionError(result.stderr)

        logger.info(f"Command output: {result.stdout}")
        return result

    @staticmethod
    def _find_liquibase() -> str:
        """Find liquibase executable in PATH."""
        # Implementation
        pass
```

**4.4.3 Changelog Manager (`changelog_manager.py`)**

```python
"""Changelog file management and generation."""
from pathlib import Path
from typing import List, Optional
import xml.etree.ElementTree as ET
from datetime import datetime

class ChangelogManager:
    """Manage Liquibase changelog files."""

    def __init__(self, changelog_dir: Path):
        self.changelog_dir = changelog_dir
        self.master_changelog = changelog_dir / 'db.changelog-master.xml'

    def create_changeset(self, author: str, description: str,
                        changes: List[Dict]) -> Path:
        """Create a new changeset file."""
        # Implementation
        pass

    def add_changeset_to_master(self, changeset_file: Path) -> None:
        """Add changeset reference to master changelog."""
        # Implementation
        pass

    def validate_changelog_structure(self) -> bool:
        """Validate changelog XML structure."""
        # Implementation
        pass

    def organize_by_release(self, release_version: str) -> None:
        """Organize changesets into release-specific directories."""
        # Implementation
        pass
```

---

### Phase 4: Testing & Documentation (Week 7-8)

#### 4.5 Testing Strategy

**4.5.1 Unit Tests**

- Test each Python module in isolation
- Mock Liquibase subprocess calls
- Validate configuration parsing
- Test changelog generation

**4.5.2 Integration Tests**

- Test against real H2 database
- Validate full migration workflows
- Test rollback scenarios
- Verify multi-database support

**4.5.3 GitHub Actions Workflow Tests**

- Test workflows in isolated repository
- Validate secret handling
- Test environment-specific deployments
- Verify rollback procedures

#### 4.6 Documentation

**Required Documentation**:

1. **README.md** - Package overview and quick start
2. **QUICKSTART.md** - Step-by-step getting started guide
3. **BEST_PRACTICES.md** - Liquibase best practices and patterns
4. **CHANGELOG_GUIDE.md** - How to write effective changelogs
5. **WORKFLOW_GUIDE.md** - GitHub Actions workflow documentation
6. **TROUBLESHOOTING.md** - Common issues and solutions
7. **API_REFERENCE.md** - Python API documentation

---

## 5. Best Practices Implementation

### 5.1 Changelog Organization

**Directory Structure**:

```
changelogs/
├── db.changelog-master.xml          # Master changelog (includes all others)
├── releases/
│   ├── v1.0/
│   │   ├── v1.0.0-changelog.xml
│   │   ├── v1.0.1-changelog.xml
│   │   └── rollback/
│   │       └── v1.0.0-rollback.xml
│   ├── v1.1/
│   │   └── v1.1.0-changelog.xml
│   └── v2.0/
│       └── v2.0.0-changelog.xml
├── hotfixes/
│   └── hotfix-2024-01-15.xml
└── baseline/
    └── initial-schema.xml
```

### 5.2 Changeset Best Practices

1. **One Logical Change Per Changeset**
   - Each changeset should represent a single, atomic change
   - Makes rollback more predictable

2. **Always Include Rollback Information**
   - Provide explicit rollback commands when possible
   - Use `<rollback>` tags in XML changelogs

3. **Use Contexts and Labels**
   - `contexts`: Environment-specific changes (dev, staging, prod)
   - `labels`: Feature-specific groupings

4. **Version Control Everything**
   - Store all changelogs in Git
   - Never modify deployed changesets (create new ones instead)

5. **Preconditions**
   - Use preconditions to verify database state before applying changes
   - Prevents applying changes to incorrect environments

### 5.3 Naming Conventions

**Changeset IDs**: `{YYYYMMDD}-{sequence}-{description}`

- Example: `20240115-001-create-users-table`

**Tags**: `{environment}-{version}-{timestamp}`

- Example: `production-v1.2.0-20240115-143000`

**Authors**: Use consistent author names (email addresses recommended)

- Example: `david.pham@example.com`

### 5.4 Security Best Practices

1. **Secret Management**
   - Store all database credentials in GitHub Secrets
   - Never commit credentials to repository
   - Use environment-specific secrets

2. **Database Connection Security**
   - Use SSL/TLS for database connections
   - Implement connection string encryption
   - Rotate credentials regularly

3. **Access Control**
   - Use GitHub environment protection rules
   - Require approvals for production deployments
   - Implement branch protection rules

### 5.5 Deployment Strategies

**Blue-Green Deployments**:

- Maintain two identical production environments
- Deploy to inactive environment first
- Switch traffic after validation

**Canary Deployments**:

- Deploy to subset of production servers
- Monitor for issues before full rollout

**Backward Compatibility**:

- Ensure schema changes don't break running application code
- Use expand-contract pattern for breaking changes

---

## 6. Integration with Existing Packages

### 6.1 GDS Package Integration

**Integration Points**:

1. **gds_postgres**
   - Use connection parameters from gds_postgres config
   - Integrate migration status into database health checks

2. **gds_mssql**
   - Support MSSQL-specific changelog types
   - Integrate with existing MSSQL connection pooling

3. **gds_snowflake**
   - Handle Snowflake-specific schema objects
   - Account for Snowflake's unique transaction model

4. **gds_mongodb**
   - Support MongoDB-specific changelog operations (collections, indexes, validators)
   - Use liquibase-mongodb extension for NoSQL change tracking
   - Handle document schema evolution patterns

### 6.2 Shared Configuration

Create unified configuration that works across all packages:

```python
# Example: Using gds_postgres with gds_liquibase
from gds_postgres import PostgresDatabase
from gds_liquibase import LiquibaseMigrationRunner, LiquibaseConfig

# Get connection from existing package
db = PostgresDatabase.from_env()

# Create Liquibase config using existing connection
liquibase_config = LiquibaseConfig(
    changelog_file='changelogs/db.changelog-master.xml',
    url=db.get_jdbc_url(),
    username=db.config.username,
    password=db.config.password,
    driver='org.postgresql.Driver'
)

# Run migrations
runner = LiquibaseMigrationRunner(liquibase_config)
runner.update()
```

#### MongoDB Integration Example

```python
# Example: Using gds_mongodb with gds_liquibase
from gds_mongodb import MongoDatabase
from gds_liquibase import LiquibaseMigrationRunner, LiquibaseConfig

# Get connection from existing package
mongo_db = MongoDatabase.from_env()

# Create Liquibase config for MongoDB (requires extension JARs)
liquibase_config = LiquibaseConfig(
    changelog_file='changelogs/mongodb/db.changelog-master.xml',
    url=mongo_db.get_connection_string(),
    username=mongo_db.config.username,
    password=mongo_db.config.password,
    classpath='mongodb-driver.jar:bson.jar:liquibase-mongodb.jar'
)

# Run migrations
runner = LiquibaseMigrationRunner(liquibase_config)
runner.update()

# Verify collection creation
print(f"Collections: {mongo_db.list_collection_names()}")
```

---

## 7. Monitoring & Observability

### 7.1 Deployment Metrics

**Track**:

- Deployment frequency
- Deployment success rate
- Rollback frequency
- Time to deploy
- Number of pending changesets

### 7.2 Logging Strategy

**GitHub Actions Logs**:

- Structured logging for all Liquibase commands
- SQL preview generation for auditing
- Deployment artifact retention

**Database Audit Trail**:

- DATABASECHANGELOG table tracks all deployments
- DATABASECHANGELOGLOCK prevents concurrent deployments
- Custom audit tables for additional metadata

### 7.3 Alerting

**Alert On**:

- Failed deployments
- Rollback executions
- Deployment duration exceeding threshold
- Changelog validation failures

---

## 8. Risk Management

### 8.1 Identified Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Failed production deployment | High | Automated rollback, staging environment testing |
| Data loss during migration | Critical | Automated backups before deployment, test rollback |
| Concurrent deployments | High | Database lock mechanism, GitHub environment protection |
| Incorrect changelog ordering | Medium | Automated validation, changelog review process |
| Missing database drivers | Medium | LPM automation, driver verification in workflows |

### 8.2 Rollback Plan

1. **Automated Rollback Trigger**: If deployment fails
2. **Manual Rollback Workflow**: For post-deployment issues
3. **Backup Restoration**: Last resort for data corruption
4. **Communication Protocol**: Notify stakeholders of rollback

---

## 9. Timeline & Milestones

### Week 1-2: Foundation

- ✅ Create gds_liquibase package structure
- ✅ Set up development environment
- ✅ Create initial Python modules
- ✅ Set up testing framework

### Week 3-4: GitHub Actions

- Create validation workflow
- Create deployment workflows (dev, staging, prod)
- Create rollback workflow
- Test workflows in isolated environment

### Week 5-6: Python Implementation

- Complete migration runner
- Implement changelog manager
- Create configuration management
- Add multi-database support

### Week 7-8: Testing & Documentation

- Write comprehensive tests
- Create user documentation
- Create developer documentation
- Conduct integration testing

### Week 9: Review & Refinement

- Code review and refinement
- Security audit
- Performance optimization
- Documentation review

### Week 10: Production Readiness

- Production environment setup
- Team training
- Phased rollout plan
- Go-live checklist

---

## 10. Success Metrics

### 10.1 Technical Metrics

- **Deployment Success Rate**: >95%
- **Rollback Success Rate**: 100%
- **Deployment Duration**: <5 minutes for typical changes
- **Changelog Validation**: 100% validated before merge

### 10.2 Process Metrics

- **Time to Deploy**: Reduced by 70% vs manual process
- **Change Failure Rate**: <5%
- **Mean Time to Recovery**: <15 minutes
- **Audit Compliance**: 100% of changes tracked

---

## 11. Future Enhancements

### Phase 2 Enhancements (Post-Launch)

1. **Liquibase Secure Edition**
   - Quality checks integration
   - Advanced reporting
   - Compliance features

2. **Database Drift Detection**
   - Automated schema comparison
   - Drift alerts and reporting

3. **Self-Service Deployments**
   - Developer-initiated deployments to dev environment
   - Automated promotion pipelines

4. **Advanced Monitoring**
   - Custom Grafana dashboards
   - Performance impact analysis
   - Change correlation with application metrics

5. **Multi-Region Support**
   - Coordinated deployments across regions
   - Region-specific changelog management

---

## 12. References

### 12.1 Official Documentation

- [Liquibase Documentation](https://docs.liquibase.com/)
- [Liquibase Best Practices](https://docs.liquibase.com/concepts/bestpractices.html)
- [setup-liquibase GitHub Action](https://github.com/liquibase/setup-liquibase)

### 12.2 Key Research Findings

**From liquibase/setup-liquibase Repository**:

- Use official `liquibase/setup-liquibase@v2` action (not deprecated legacy actions)
- Leverage automatic caching for faster workflow runs
- Use relative paths for changelog files (e.g., `changelog.xml` not `/liquibase/changelog.xml`)
- Set `LIQUIBASE_LICENSE_KEY` as environment variable for Secure edition
- Use Liquibase Package Manager (LPM) for driver installation in Community edition 5.0+
- Follow semantic versioning for action versions (`@v2` for auto-updates)

**Best Practices Identified**:

1. Always validate changelogs in CI before merging
2. Generate rollback SQL for audit trail
3. Use tags for deployment tracking
4. Implement environment protection rules in GitHub
5. Use contexts for environment-specific changes
6. Store generated SQL artifacts for review
7. Implement automated backup before production deployments

### 12.3 Existing GitHub Actions Examples

**Validation Pattern**:

```yaml
- uses: liquibase/setup-liquibase@v2
- run: liquibase validate --changelog-file=changelog.xml
- run: liquibase update-sql > preview.sql
```

**Deployment Pattern**:

```yaml
- uses: liquibase/setup-liquibase@v2
- name: Create backup tag
  run: liquibase tag "backup-$(date +%Y%m%d-%H%M%S)"
- name: Deploy
  run: liquibase update --changelog-file=changelog.xml
```

**Multi-Environment Pattern**:

```yaml
strategy:
  matrix:
    environment: [dev, staging]
```

---

## 13. Appendix

### A. Sample Changelog

**PostgreSQL Example Changelog**:

📄 **See**: [`examples/changelogs/db.changelog-master.xml`](examples/changelogs/db.changelog-master.xml)

Demonstrates:

- Creating tables with constraints
- Adding indexes
- Using preConditions
- Defining rollback operations

### B. Sample liquibase.properties

**PostgreSQL Configuration**:

📄 **See**: [`examples/config/liquibase.properties`](examples/config/liquibase.properties)

### C. GitHub Secrets Required

**Per Environment**:

- `{ENV}_DB_URL` - Database JDBC URL
- `{ENV}_DB_USERNAME` - Database username
- `{ENV}_DB_PASSWORD` - Database password

**Optional**:

- `LIQUIBASE_LICENSE_KEY` - For Secure edition features
- `SLACK_WEBHOOK_URL` - For deployment notifications

### D. MongoDB-Specific Configuration

**MongoDB Connection String**:

📄 **See**: [`examples/config/liquibase-mongodb.properties`](examples/config/liquibase-mongodb.properties)

**Sample MongoDB Changelog**:

📄 **See**: [`examples/changelogs/mongodb-changelog.xml`](examples/changelogs/mongodb-changelog.xml)

Demonstrates:

- Creating collections with schema validation
- Creating indexes (unique and non-unique)
- MongoDB-specific extensions
- Rollback operations for collections
                [
                    {
                        username: "admin",
                        email: "admin@example.com",
                        role: "admin",
                        createdAt: new Date()
                    }
                ]
            </ext:documents>
        </ext:insertMany>

        <rollback>
            <ext:runCommand>
                { delete: "users", deletes: [{ q: { username: "admin" }, limit: 1 }] }
            </ext:runCommand>
        </rollback>
    </changeSet>

</databaseChangeLog>
```

**MongoDB GitHub Actions Workflow Example**:

```yaml
name: MongoDB Migration - Development

on:
  push:
    branches:
      - main
    paths:
      - 'changelogs/mongodb/**'

jobs:
  deploy-mongodb-dev:
    runs-on: ubuntu-latest
    environment: development
    steps:
      - uses: actions/checkout@v4

      - uses: liquibase/setup-liquibase@v2
        with:
          version: '5.0.0'
          edition: 'community'

      - name: Install MongoDB Driver and Extension
        run: |
          # Install MongoDB driver
          wget -O mongodb-driver.jar https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-sync/4.11.1/mongodb-driver-sync-4.11.1.jar

          # Install MongoDB BSON library
          wget -O bson.jar https://repo1.maven.org/maven2/org/mongodb/bson/4.11.1/bson-4.11.1.jar

          # Install Liquibase MongoDB extension
          wget -O liquibase-mongodb.jar https://repo1.maven.org/maven2/org/liquibase/ext/liquibase-mongodb/4.25.0/liquibase-mongodb-4.25.0.jar

      - name: Validate MongoDB Changelog
        env:
          MONGO_URL: ${{ secrets.DEV_MONGO_URL }}
          MONGO_USERNAME: ${{ secrets.DEV_MONGO_USERNAME }}
          MONGO_PASSWORD: ${{ secrets.DEV_MONGO_PASSWORD }}
        run: |
          liquibase validate \
            --classpath=mongodb-driver.jar:bson.jar:liquibase-mongodb.jar \
            --changelog-file=changelogs/mongodb/db.changelog-master.xml \
            --url=$MONGO_URL \
            --username=$MONGO_USERNAME \
            --password=$MONGO_PASSWORD

      - name: Deploy MongoDB Changes
        env:
          MONGO_URL: ${{ secrets.DEV_MONGO_URL }}
          MONGO_USERNAME: ${{ secrets.DEV_MONGO_USERNAME }}
          MONGO_PASSWORD: ${{ secrets.DEV_MONGO_PASSWORD }}
        run: |
          liquibase update \
            --classpath=mongodb-driver.jar:bson.jar:liquibase-mongodb.jar \
            --changelog-file=changelogs/mongodb/db.changelog-master.xml \
            --url=$MONGO_URL \
            --username=$MONGO_USERNAME \
            --password=$MONGO_PASSWORD

      - name: Tag Deployment
        env:
          MONGO_URL: ${{ secrets.DEV_MONGO_URL }}
          MONGO_USERNAME: ${{ secrets.DEV_MONGO_USERNAME }}
          MONGO_PASSWORD: ${{ secrets.DEV_MONGO_PASSWORD }}
        run: |
          liquibase tag "dev-mongodb-$(date +%Y%m%d-%H%M%S)" \
            --classpath=mongodb-driver.jar:bson.jar:liquibase-mongodb.jar \
            --url=$MONGO_URL \
            --username=$MONGO_USERNAME \
            --password=$MONGO_PASSWORD
```

**MongoDB Python Integration Example**:

```python
# Example: Using gds_mongodb with gds_liquibase
from gds_mongodb import MongoDatabase
from gds_liquibase import LiquibaseMigrationRunner, LiquibaseConfig

# Get connection from existing package
mongo_db = MongoDatabase.from_env()

# Create Liquibase config for MongoDB
liquibase_config = LiquibaseConfig(
    changelog_file='changelogs/mongodb/db.changelog-master.xml',
    url=mongo_db.get_connection_string(),
    username=mongo_db.config.username,
    password=mongo_db.config.password,
    classpath='mongodb-driver.jar:bson.jar:liquibase-mongodb.jar'
)

# Run migrations
runner = LiquibaseMigrationRunner(liquibase_config)
runner.update()

# Check status
status = runner.status(verbose=True)
print(status.stdout)
```

**MongoDB-Specific Best Practices**:

1. **Schema Validation**: Use MongoDB's JSON Schema validation in changesets
2. **Index Management**: Always create indexes for frequently queried fields
3. **Document Evolution**: Plan for backward-compatible schema changes
4. **Sharding Considerations**: Account for shard key when creating collections
5. **Replica Set Awareness**: Test migrations against replica sets
6. **Transaction Support**: Use multi-document transactions when available (MongoDB 4.0+)

### E. Containerization & Kubernetes Deployment

#### Docker Container Setup

**Existing Docker Implementation**: This repository already includes a production-ready Liquibase Docker image in `docker/liquibase/`.

**Key Features**:

- Base image: `eclipse-temurin:21-jre` (Java 21 LTS)
- Liquibase version: 5.0.1 (configurable via build args)
- Pre-installed JDBC drivers:
  - Microsoft SQL Server (13.2.1)
  - PostgreSQL (42.7.8)
  - Snowflake (3.27.1)
  - MongoDB (3.12.14) with liquibase-mongodb extension (5.0.1)
- Comprehensive educational documentation
- Example changelogs for PostgreSQL

**Build the Custom Image**:

```bash
# From repository root
docker build -t liquibase-custom:latest docker/liquibase

# With custom version
docker build \
  --build-arg LIQUIBASE_VERSION=5.0.2 \
  --build-arg MSSQL_DRIVER_VERSION=13.2.2 \
  -t liquibase-custom:5.0.2 \
  docker/liquibase

# Tag for registry
docker tag liquibase-custom:latest ghcr.io/davidvupham/dbtools-liquibase:latest

# Push to registry
docker push ghcr.io/davidvupham/dbtools-liquibase:latest
```

**Quick Start**:

```bash
# Verify installation
docker run --rm liquibase-custom:latest --version

# Run update against local database
docker run --rm \
  -v $(pwd)/changelogs:/liquibase/changelog \
  liquibase-custom:latest \
  --url=jdbc:postgresql://host.docker.internal:5432/mydb \
  --username=dbuser \
  --password=dbpass \
  --changelog-file=/liquibase/changelog/db.changelog-master.yaml \
  update
```

**Documentation**: See `docker/liquibase/README.md` and `docker/liquibase/liquibase-docker-operations-guide.md` for:

- Complete build instructions
- Health check procedures
- Rollback workflows
- Production best practices
- Troubleshooting guide

#### Helm Chart Implementation

**Chart.yaml**:

📄 **See**: [`examples/helm/Chart.yaml`](examples/helm/Chart.yaml)

**values.yaml**:

📄 **See**: [`examples/helm/values.yaml`](examples/helm/values.yaml)

Key configuration options:

- Liquibase command and changelog file
- Database connection settings
- Job and CronJob configuration
- Resource limits and security context
- Monitoring and observability settings
- Migration strategies (Job, Init Container, CronJob)

**values-production.yaml** (Production overrides):

```yaml
image:
  tag: "1.0.0"  # Use specific version in production

liquibase:
  command: "update"
  logLevel: "WARNING"

database:
  existingSecret: "liquibase-db-credentials"

job:
  backoffLimit: 1  # Less retries in production
  activeDeadlineSeconds: 300  # Shorter timeout

pod:
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 500m
      memory: 512Mi

  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchExpressions:
              - key: app
                operator: In
                values:
                  - liquibase-migrations
          topologyKey: kubernetes.io/hostname

cronjob:
  enabled: true
  schedule: "0 3 * * *"  # Daily validation at 3 AM

monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
```

**templates/job-migrate.yaml**:

```yaml
{{- if .Values.migration.job.enabled }}
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "liquibase-migrations.fullname" . }}-migrate
  labels:
    {{- include "liquibase-migrations.labels" . | nindent 4 }}
    app.kubernetes.io/component: migration
  annotations:
    {{- toYaml .Values.job.annotations | nindent 4 }}
spec:
  backoffLimit: {{ .Values.job.backoffLimit }}
  activeDeadlineSeconds: {{ .Values.job.activeDeadlineSeconds }}
  ttlSecondsAfterFinished: {{ .Values.job.ttlSecondsAfterFinished }}
  template:
    metadata:
      labels:
        {{- include "liquibase-migrations.selectorLabels" . | nindent 8 }}
        app.kubernetes.io/component: migration
      annotations:
        {{- toYaml .Values.pod.annotations | nindent 8 }}
    spec:
      serviceAccountName: {{ include "liquibase-migrations.serviceAccountName" . }}
      restartPolicy: {{ .Values.job.restartPolicy }}
      securityContext:
        {{- toYaml .Values.pod.securityContext | nindent 8 }}
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      containers:
      - name: liquibase
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        args:
          - {{ .Values.liquibase.command }}
          - --changelog-file={{ .Values.liquibase.changelogFile }}
          {{- if .Values.liquibase.contexts }}
          - --contexts={{ .Values.liquibase.contexts }}
          {{- end }}
          {{- if .Values.liquibase.labels }}
          - --labels={{ .Values.liquibase.labels }}
          {{- end }}
          - --log-level={{ .Values.liquibase.logLevel }}
          {{- range .Values.liquibase.extraArgs }}
          - {{ . }}
          {{- end }}
        env:
          - name: LIQUIBASE_COMMAND_URL
            valueFrom:
              secretKeyRef:
                name: {{ .Values.database.existingSecret | default (printf "%s-db" (include "liquibase-migrations.fullname" .)) }}
                key: jdbcUrl
          - name: LIQUIBASE_COMMAND_USERNAME
            valueFrom:
              secretKeyRef:
                name: {{ .Values.database.existingSecret | default (printf "%s-db" (include "liquibase-migrations.fullname" .)) }}
                key: {{ .Values.database.existingSecretUsernameKey }}
          - name: LIQUIBASE_COMMAND_PASSWORD
            valueFrom:
              secretKeyRef:
                name: {{ .Values.database.existingSecret | default (printf "%s-db" (include "liquibase-migrations.fullname" .)) }}
                key: {{ .Values.database.existingSecretPasswordKey }}
        resources:
          {{- toYaml .Values.pod.resources | nindent 10 }}
        volumeMounts:
          - name: config
            mountPath: /liquibase/liquibase.properties
            subPath: liquibase.properties
      volumes:
        - name: config
          configMap:
            name: {{ include "liquibase-migrations.fullname" . }}-config
      {{- with .Values.pod.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.pod.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.pod.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
{{- end }}
```

**templates/secret.yaml**:

```yaml
{{- if not .Values.database.existingSecret }}
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "liquibase-migrations.fullname" . }}-db
  labels:
    {{- include "liquibase-migrations.labels" . | nindent 4 }}
type: Opaque
stringData:
  jdbcUrl: {{ .Values.database.jdbcUrl | default (printf "jdbc:%s://%s:%s/%s%s" .Values.database.type .Values.database.host (.Values.database.port | toString) .Values.database.name .Values.database.connectionParams) }}
  username: {{ .Values.database.username }}
  password: {{ .Values.database.password }}
{{- end }}
```

**templates/cronjob-validate.yaml**:

```yaml
{{- if .Values.cronjob.enabled }}
apiVersion: batch/v1
kind: CronJob
metadata:
  name: {{ include "liquibase-migrations.fullname" . }}-validate
  labels:
    {{- include "liquibase-migrations.labels" . | nindent 4 }}
    app.kubernetes.io/component: validation
spec:
  schedule: {{ .Values.cronjob.schedule | quote }}
  successfulJobsHistoryLimit: {{ .Values.cronjob.successfulJobsHistoryLimit }}
  failedJobsHistoryLimit: {{ .Values.cronjob.failedJobsHistoryLimit }}
  concurrencyPolicy: {{ .Values.cronjob.concurrencyPolicy }}
  suspend: {{ .Values.cronjob.suspend }}
  jobTemplate:
    spec:
      template:
        metadata:
          labels:
            {{- include "liquibase-migrations.selectorLabels" . | nindent 12 }}
            app.kubernetes.io/component: validation
        spec:
          serviceAccountName: {{ include "liquibase-migrations.serviceAccountName" . }}
          restartPolicy: Never
          containers:
          - name: liquibase
            image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
            imagePullPolicy: {{ .Values.image.pullPolicy }}
            args:
              - validate
              - --changelog-file={{ .Values.liquibase.changelogFile }}
            env:
              - name: LIQUIBASE_COMMAND_URL
                valueFrom:
                  secretKeyRef:
                    name: {{ .Values.database.existingSecret | default (printf "%s-db" (include "liquibase-migrations.fullname" .)) }}
                    key: jdbcUrl
              - name: LIQUIBASE_COMMAND_USERNAME
                valueFrom:
                  secretKeyRef:
                    name: {{ .Values.database.existingSecret | default (printf "%s-db" (include "liquibase-migrations.fullname" .)) }}
                    key: {{ .Values.database.existingSecretUsernameKey }}
              - name: LIQUIBASE_COMMAND_PASSWORD
                valueFrom:
                  secretKeyRef:
                    name: {{ .Values.database.existingSecret | default (printf "%s-db" (include "liquibase-migrations.fullname" .)) }}
                    key: {{ .Values.database.existingSecretPasswordKey }}
            resources:
              {{- toYaml .Values.pod.resources | nindent 14 }}
{{- end }}
```

#### Kubernetes Deployment Workflows

**GitHub Actions: Build and Push Container**:

```yaml
name: Build and Push Liquibase Container

on:
  push:
    branches:
      - main
    paths:
      - 'Dockerfile'
      - 'changelogs/**'
      - '.github/workflows/docker-build.yml'
  release:
    types: [published]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/liquibase-migrations

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64

      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ steps.meta.outputs.version }}
```

**GitHub Actions: Deploy to Kubernetes with Helm**:

```yaml
name: Deploy to Kubernetes via Helm

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
      migration_action:
        description: 'Migration action'
        required: true
        type: choice
        options:
          - update
          - rollback
          - validate
          - status
      image_tag:
        description: 'Container image tag'
        required: true
        default: 'latest'

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment }}

    steps:
      - uses: actions/checkout@v4

      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG }}

      - name: Install Helm
        uses: azure/setup-helm@v3
        with:
          version: '3.12.0'

      - name: Deploy with Helm
        run: |
          helm upgrade --install liquibase-migrations ./helm/liquibase \
            --namespace ${{ github.event.inputs.environment }} \
            --create-namespace \
            --values ./helm/liquibase/values-${{ github.event.inputs.environment }}.yaml \
            --set image.tag=${{ github.event.inputs.image_tag }} \
            --set liquibase.command=${{ github.event.inputs.migration_action }} \
            --set database.existingSecret=liquibase-db-credentials-${{ github.event.inputs.environment }} \
            --wait \
            --timeout 10m

      - name: Check Job Status
        run: |
          kubectl wait --for=condition=complete \
            --timeout=600s \
            job/liquibase-migrations-migrate \
            -n ${{ github.event.inputs.environment }}

      - name: Get Job Logs
        if: always()
        run: |
          kubectl logs \
            -l app.kubernetes.io/component=migration \
            -n ${{ github.event.inputs.environment }} \
            --tail=100

      - name: Notify on Failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "Liquibase migration failed in ${{ github.event.inputs.environment }}",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": ":x: *Migration Failed*\n*Environment:* ${{ github.event.inputs.environment }}\n*Action:* ${{ github.event.inputs.migration_action }}\n*Image:* ${{ github.event.inputs.image_tag }}"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

#### Deployment Commands

**Install Helm Chart**:

```bash
# Add Helm repository (if using one)
helm repo add liquibase https://charts.example.com
helm repo update

# Install to development
helm install liquibase-dev ./helm/liquibase \
  --namespace development \
  --create-namespace \
  --values ./helm/liquibase/values-dev.yaml

# Install to production
helm install liquibase-prod ./helm/liquibase \
  --namespace production \
  --create-namespace \
  --values ./helm/liquibase/values-production.yaml

# Upgrade existing installation
helm upgrade liquibase-prod ./helm/liquibase \
  --namespace production \
  --values ./helm/liquibase/values-production.yaml \
  --set image.tag=1.0.1

# Rollback to previous version
helm rollback liquibase-prod 1 --namespace production

# Uninstall
helm uninstall liquibase-prod --namespace production
```

**Run One-Time Migration Job**:

```bash
# Using kubectl
kubectl create job --from=cronjob/liquibase-migrations-validate \
  liquibase-manual-migration-$(date +%s) \
  -n production

# Using Helm with custom values
helm upgrade --install liquibase-migration ./helm/liquibase \
  --namespace production \
  --set liquibase.command=update \
  --set image.tag=1.0.1 \
  --wait
```

**Monitor Migration Jobs**:

```bash
# Watch job status
kubectl get jobs -n production -w

# Get job details
kubectl describe job liquibase-migrations-migrate -n production

# View logs
kubectl logs -l app.kubernetes.io/component=migration -n production --follow

# Check pod events
kubectl get events -n production --sort-by='.lastTimestamp'
```

#### Best Practices for Kubernetes Deployments

1. **Use Init Containers for Application Dependencies**

   ```yaml
   initContainers:
   - name: liquibase-migration
     image: ghcr.io/your-org/liquibase-migrations:1.0.0
     args: ["update"]
   ```

2. **Implement Health Checks**
   - Validate before deployment
   - Run status checks after migration
   - Monitor DATABASECHANGELOG table

3. **Resource Management**
   - Set appropriate CPU/memory limits
   - Use resource quotas per namespace
   - Monitor resource usage

4. **Security**
   - Use Kubernetes Secrets for credentials
   - Enable RBAC for service accounts
   - Run as non-root user
   - Scan container images for vulnerabilities

5. **Observability**
   - Export logs to centralized logging
   - Create Prometheus metrics for job completion
   - Set up alerts for failed migrations
   - Track migration duration

6. **Backup Before Migration**

   ```yaml
   # Add pre-migration hook
   annotations:
     helm.sh/hook: pre-upgrade
     helm.sh/hook-weight: "-5"
   ```

---

## Document Control

- **Version**: 1.2
- **Created**: 2024-01-15
- **Last Updated**: 2025-11-16
- **Author**: Database DevOps Team
- **Status**: Draft - MongoDB & Kubernetes Support Added
- **Next Review**: Upon completion of Phase 1

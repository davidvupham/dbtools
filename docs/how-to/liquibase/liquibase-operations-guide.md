# Liquibase Operations Guide

**🔗 [← Back to Liquibase Documentation Index](../../explanation/liquibase/README.md)** — Navigation guide for all Liquibase docs

> **Document Version:** 1.0
> **Last Updated:** January 12, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production
> **Related Docs:** [Concepts](../../explanation/concepts/liquibase/liquibase-concepts.md) | [Architecture](../../explanation/architecture/liquibase/liquibase-architecture.md) | [Reference](../../reference/liquibase/liquibase-reference.md) | [Formatted SQL](../../reference/liquibase/liquibase-formatted-sql-guide.md)

![Liquibase Version](https://img.shields.io/badge/Liquibase-5.0%2B-blue)
![Document Status](https://img.shields.io/badge/Status-Production-green)

This guide covers day-to-day tasks: writing changesets, deploying changes, handling rollbacks, testing, and troubleshooting.

> [!IMPORTANT]
> **Prerequisites:** Understand basic Liquibase concepts (Changelog, Changeset, Change Types). See [Concepts Guide](../../explanation/concepts/liquibase/liquibase-concepts.md) if you're new to Liquibase.

> [!NOTE]
> Examples use the **Global Data Services (GDS)** team, but these procedures apply to **all teams**.

## Table of Contents

- [Authoring Changes](#authoring-changes)
  - [ChangeSet Best Practices](#changeset-best-practices)
  - [Using Preconditions (SQL Guards)](#using-preconditions-sql-guards)
  - [Contexts and Labels](#contexts-and-labels)
  - [Platform-Specific Changes](#platform-specific-changes)
  - [Shared Modules](#shared-modules)
  - [Reference Data](#reference-data)
- [Baseline Management](#baseline-management)
  - [Creating a Baseline (Initial Adoption)](#creating-a-baseline-initial-adoption)
  - [Baseline Reset (Consolidation)](#baseline-reset-consolidation)
- [Security & Secrets Management](#security--secrets-management)
- [Execution Patterns](#execution-patterns)
  - [Dry-Run Validation](#dry-run-validation)
  - [Multi-Database Platform Deployment](#multi-database-platform-deployment)
  - [Drift Detection and Remediation](#drift-detection-and-remediation)
  - [Using Flow Files (Advanced)](#using-flow-files-advanced)
  - [Running Quality Checks (Pro)](#running-quality-checks-pro)
  - [Structured Logging](#structured-logging)
- [Docker Execution](#docker-execution)
- [Rollback Strategy](#rollback-strategy)
  - [Using Tags (Recommended)](#using-tags-recommended)
  - [Using Count](#using-count)
- [Testing Strategy](#testing-strategy)
  - [1. Changelog Validation](#1-changelog-validation)
  - [2. Ephemeral Database Testing](#2-ephemeral-database-testing)
  - [3. Rollback Testing](#3-rollback-testing)
- [Migration from Legacy](#migration-from-legacy)
  - [Adopting This Structure](#adopting-this-structure)

## Authoring Changes

### ChangeSet Best Practices

1. **File Naming**: Use `V<Timestamp>__<Jira>_<Description>.<databaseType>.sql` strictly.
   - Example: `V202601121030__PROJ-45_add_user_table.postgres.sql`
2. **Changeset ID**: Use `author:id` format (e.g., `team-a:20260112-add-user`).
3. **Granularity**: One logical change per file/changeset.
4. **Rollback**: Always provide explicit `--rollback` SQL comments.
5. **Idempotency**: Use SQL guards (`IF NOT EXISTS`) or `runOnChange:true`.
6. **Formatted SQL**: Use `--liquibase formatted sql` header.

### Using Preconditions (SQL Guards)

In Formatted SQL, prefer native SQL guards (idempotency) over XML preconditions where possible:

**Example: Safe Table Creation (PostgreSQL)**

```sql
--liquibase formatted sql

--changeset team:20260112-create-users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE
);
--rollback DROP TABLE IF EXISTS users;
```

**Example: Safe Column Addition (SQL Server)**

```sql
--liquibase formatted sql

--changeset team:20260112-add-column
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('users') AND name = 'email_verified')
BEGIN
    ALTER TABLE users ADD email_verified BIT DEFAULT 0;
END
--rollback ALTER TABLE users DROP COLUMN email_verified;
```

### Contexts and Labels

- **Minimize use**: Keep schema changes environment-agnostic.
- **Contexts**: Use `context:dev` for test data.
- **Labels**: Use for deployment filtering.

Example in Formatted SQL:

```sql
--changeset team:seed-dev-data context:dev
INSERT INTO users (username) VALUES ('test_user');
--rollback DELETE FROM users WHERE username = 'test_user';
```

### Platform-Specific Changes

Use `dbms` attribute in SQL comments for platform deltas:

```sql
--changeset team:add-json-col dbms:postgresql
ALTER TABLE config ADD settings JSONB;

--changeset team:add-json-col dbms:mssql
ALTER TABLE config ADD settings NVARCHAR(MAX);
```

For larger divergence, use separate files in platform-specific folders.

#### MongoDB-Specific Patterns

MongoDB uses extension change types (`ext:`) for collections and indexes. Use JSON or YAML changesets as Formatted SQL does not support NoSQL syntax native execution in the same way.

```yaml
- changeSet:
    id: 20251116-01-create-collection
    changes:
      - ext:createCollection:
          collectionName: users
```

### Shared Modules

Reusable patterns go in `shared/modules/` and can be included from any database master:

```xml
<include file="../../shared/modules/audit/V0000__audit_schema.sql"/>
```

### Reference Data

Store CSVs in `shared/data/reference/` and load with `loadData`:

Store CSVs in `shared/data/reference/` and load with `loadData` using a YAML/XML wrapper, as Formatted SQL cannot easily load local CSVs without database-specific `COPY` commands.

```yaml
- changeSet:
    id: seed-countries
    changes:
      - loadData:
          file: ../../shared/data/reference/countries.csv
          tableName: countries
```

[↑ Back to Table of Contents](#table-of-contents)

## Baseline Management

**What is a Baseline?**
A baseline is an initial schema snapshot capturing the existing database state before Liquibase management begins.

### Creating a Baseline (Initial Adoption)

```bash
# Generate baseline from existing database
liquibase \
  --defaults-file=properties/liquibase.prod.properties \
  --changelog-file=applications/payments_api/postgres/orders/baseline/V0000__baseline.postgres.sql \
  generateChangeLog
```

**Applying Baseline to Existing Database:**
Mark it as executed without running the SQL (since schema already exists):

```bash
liquibase \
  --defaults-file=properties/liquibase.prod.properties \
  --changelog-file=applications/payments_api/postgres/orders/baseline/V0000__baseline.postgres.sql \
  changelogSync

# Tag it
liquibase \
  --defaults-file=properties/liquibase.prod.properties \
  --changelog-file=applications/payments_api/postgres/orders/changelog.xml \
  tag baseline
```

### Baseline Reset (Consolidation)

Over time, changelogs accumulate. For new database instances, you can consolidate into a new baseline to speed up deployments.

**When to Consolidate:**

- After major releases (e.g., v2.0)
- When changelog history exceeds 50+ changesets
- Before provisioning many new instances

**Procedure:**

1. **Generate a new baseline** from production:

    ```bash
    liquibase \
      --defaults-file=properties/liquibase.prod.properties \
      --changelog-file=applications/payments_api/postgres/orders/baseline/V0000__baseline_v2.postgres.sql \
      generateChangeLog
    ```

2. **Create a new master changelog** referencing the consolidated baseline:

    ```xml
    <!-- changelog.xml -->
    <databaseChangeLog ...>
      <include file="baseline/V0000__baseline_v2.sql"/>
      <!-- Future changes go here -->
      <includeAll path="changes/"/>
    </databaseChangeLog>
    ```

3. **For new instances**: Restore from a DB snapshot or run the consolidated baseline.

4. **Mark baseline as applied** (if restored from snapshot):

    ```bash
    liquibase \
      --defaults-file=properties/liquibase.new-instance.properties \
      --changelog-file=applications/payments_api/postgres/orders/changelog.xml \
      changelogSync
    ```

[↑ Back to Table of Contents](#table-of-contents)

## Security & Secrets Management

Security is paramount when automating database changes. **Never commit credentials to source control.**

### Credential Handling

1.  **Environment Variables (Recommended)**
    Liquibase automatically reads standard environment variables. Set these in your CI/CD runner:

    ```bash
    export LIQUIBASE_COMMAND_URL="jdbc:postgresql://db-prod:5432/myapp"
    export LIQUIBASE_COMMAND_USERNAME="liquibase_user"
    export LIQUIBASE_COMMAND_PASSWORD="secure_password_from_vault"
    ```

2.  **HashiCorp Vault (Enterprise/Secure)**
    For enterprise environments, the **HashiCorp Vault Extension** is the standard for injecting secrets directly into Liquibase.

    *   **Community Alternative:** Use the `vault` CLI in your CI pipeline to fetch secrets and export them as environment variables (Option 1).

### Search Path Security

Limit `LIQUIBASE_SEARCH_PATH` to your specific changelog directory to prevent loading malicious files from `/tmp` or other unsecured locations.

[↑ Back to Table of Contents](#table-of-contents)

## Execution Patterns

### Dry-Run Validation

Always validate before applying:

```bash
```bash
liquibase \
  --defaults-file properties/liquibase.dev.properties \
  --changelog-file platforms/postgres/databases/app/changelog.xml \
  updateSQL
```

### Multi-Database Platform Deployment

Loop through all databases for a platform:

```bash
set -euo pipefail
platform=postgres
for db in app analytics; do
  cf="platforms/$platform/databases/$db/changelog.xml"

  # Apply
  liquibase --defaults-file properties/liquibase.dev.properties \
    --changelog-file "$cf" update
done
```

### Drift Detection and Remediation

> **📖 Concept:** For background on what drift is and why it matters, see [Understanding Database Drift](../../explanation/liquibase/drift-management.md).

Drift occurs when database changes are made outside of Liquibase. Detecting and handling drift is critical for maintaining environment consistency.

#### Capture a Baseline Snapshot

Before you can detect drift, capture a "known good" snapshot after each deployment:

```bash
# Capture snapshot after deployment
liquibase \
  --defaults-file=properties/liquibase.prod.properties \
  snapshot \
  --schemas=app \
  --snapshot-format=json \
  --output-file=snapshots/dbinstance1_prod-post_deploy-$(date +%Y%m%d_%H%M).json
```

**When to capture snapshots:**
- After every successful deployment
- Before and after maintenance windows
- At release milestones

#### Detect Drift Against Snapshot

Compare your current database against the baseline snapshot:

```bash
# Compare database to snapshot (recommended)
liquibase \
  --defaults-file=properties/liquibase.prod.properties \
  diff \
  --schemas=app \
  --referenceUrl="offline:postgresql?snapshot=snapshots/dbinstance1_prod-post_deploy-20260112_1200.json"
```

#### Detect Drift Between Environments

Compare two live databases:

```bash
liquibase \
  --defaults-file=properties/liquibase.stage.properties \
  diff \
  --schemas=app \
  --referenceUrl="${PROD_JDBC_URL}" \
  --referenceUsername="${PROD_DB_USER}" \
  --referencePassword="${PROD_DB_PASSWORD}"
```

#### Generate Remediation Changelog

If drift is detected and you want to capture it as a changeset:

```bash
# Generate XML changelog from drift
liquibase \
  --defaults-file=properties/liquibase.prod.properties \
  diffChangeLog \
  --schemas=app \
  --changelog-file=drift/db.changelog-drift-$(date +%Y%m%d).yaml \
  --referenceUrl="offline:postgresql?snapshot=snapshots/prod_baseline_20260112.json"

# Or generate SQL format (platform-specific)
liquibase \
  --defaults-file=properties/liquibase.prod.properties \
  diffChangeLog \
  --schemas=app \
  --changelog-file=drift/db.changelog-drift-$(date +%Y%m%d).postgresql.sql \
  --referenceUrl="offline:postgresql?snapshot=snapshots/prod_baseline_20260112.json"
```

> **Note:** Review generated changelogs before deploying. Some objects (stored procedures, triggers) may need manual adjustment.

#### Remediation Strategies

**Option 1: Revert the Drift**

If drift was unintended, manually reverse it:

```sql
-- Example: Remove unexpected column
ALTER TABLE app.customer DROP COLUMN loyalty_points;

-- Example: Restore missing index
CREATE INDEX IX_orders_date ON app.orders(order_date DESC);
```

Then verify:

```bash
liquibase diff --schemas=app \
  --referenceUrl="offline:postgresql?snapshot=snapshots/prod_baseline_20260112.json"
# Should show no differences
```

**Option 2: Accept the Drift**

If drift is legitimate, capture and sync:

```bash
# 1. Generate changelog from drift
liquibase diffChangeLog \
  --changelog-file=drift/db.changelog-captured-drift.yaml \
  --referenceUrl="offline:postgresql?snapshot=snapshots/prod_baseline_20260112.json"

# 2. Review and add to master changelog
# Edit drift/db.changelog-captured-drift.yaml as needed

# 3. Mark as already deployed (since it exists in DB)
liquibase \
  --changelog-file=drift/db.changelog-captured-drift.yaml \
  changelogSync
```

#### Preview SQL for Audit

Always capture the SQL for audit and compliance:

```bash
# Preview deployment SQL (for approval/audit)
liquibase \
  --defaults-file=properties/liquibase.prod.properties \
  --changelog-file=changelog.xml \
  updateSQL > audit/deployment_$(date +%Y%m%d_%H%M%S).sql

# Preview rollback SQL
liquibase \
  --defaults-file=properties/liquibase.prod.properties \
  --changelog-file=changelog.xml \
  rollbackSQL v1.0 > audit/rollback_$(date +%Y%m%d_%H%M%S).sql
```

#### CI/CD Integration

Add drift detection to your pipeline:

```bash
#!/bin/bash
# pre-deployment-check.sh

# Find latest post_deploy snapshot
SNAPSHOT=$(ls -t snapshots/*-post_deploy-*.json | head -1)

# Run diff and capture output
DRIFT_OUTPUT=$(liquibase diff \
  --defaults-file=properties/liquibase.prod.properties \
  --schemas=app \
  --referenceUrl="offline:postgresql?snapshot=$SNAPSHOT" 2>&1)

# Check for drift
if echo "$DRIFT_OUTPUT" | grep -qE "Missing|Unexpected|Changed"; then
  echo "ERROR: Drift detected in production!"
  echo "$DRIFT_OUTPUT"
  exit 1
fi

echo "No drift detected. Proceeding with deployment."
```

For supported objects by platform, see [Reference - Drift Detection Supported Objects](../../reference/liquibase/liquibase-reference.md#drift-detection-supported-objects).

### Orchestration (Community: Shell Scripts)

For Community Edition, use robust shell scripts to chain commands (Validate -> Quality Check -> Update).

**Example `deploy.sh`:**

```bash
#!/bin/bash
set -euo pipefail

changelog="changelog.xml"

# 1. Validation
echo "Validating changelog..."
liquibase --changelog-file="$changelog" validate

# 2. Quality Checks (see below)
echo "Running Linter..."
sqlfluff lint database/changes/*.sql

# 3. Deployment
echo "Deploying..."
liquibase --changelog-file="$changelog" update
```

> **Note:** **Liquibase Secure** users can use **Flow Files** for cross-platform orchestration without aggressive shell scripting.

### Quality Checks (Community: SQLFluff)

Instead of Liquibase Pro's Policy Checks, usage **[SQLFluff](https://sqlfluff.com/)** or similar linters to enforce SQL standards (naming conventions, casing, etc.) in your CI/CD pipeline.

**Example `sqlfluff` run:**

```bash
pip install sqlfluff
sqlfluff lint platforms/postgres/changes/ --dialect postgres
```

> **Liquibase Secure Alternative:** Use `liquibase checks run` for database-aware policy checks (e.g., detecting `GRANT` statements or large table drops).

### Structured Logging

Enable JSON logging for observability systems:

```bash
export LIQUIBASE_LOG_FORMAT=JSON
liquibase update
```

[↑ Back to Table of Contents](#table-of-contents)

## Docker Execution

Run Liquibase in Docker by mounting the repository root and setting `LIQUIBASE_SEARCH_PATH`:

```bash
docker run --rm \
  --network devcontainer-network \
  -v $(pwd):/liquibase/changelog:ro \
  -e LIQUIBASE_SEARCH_PATH=/liquibase/changelog \
  liquibase:latest \
  --defaults-file properties/liquibase.dev.properties \
  --changelog-file platforms/postgres/databases/app/changelog.xml \
  update
```

[↑ Back to Table of Contents](#table-of-contents)

## Rollback Strategy

### Using Tags (Recommended)

Roll back to a specific release tag:

```bash
liquibase --defaults-file properties/liquibase.prod.properties \
  --changelog-file platforms/postgres/databases/app/changelog.xml \
  rollback v1.0
```

### Using Count

Roll back last N changeSets:

```bash
liquibase ... rollbackCount 3
```

[↑ Back to Table of Contents](#table-of-contents)

## Testing Strategy

### 1. Unit Testing (Validation)

Run static analysis on every commit to catch syntax errors early.

```bash
# Verify XML/YAML/SQL validity
liquibase --changelog-file="$changelog" validate
```

### 2. Integration Testing with Testcontainers

For robust testing, spin up an ephemeral, identical database version using **Testcontainers** (Java/Go/Python).

**Pattern:**
1.  **Start Container:** Spin up `postgres:15-alpine` (or your target DB).
2.  **Deploy Schema:** Run `liquibase update` against the container.
3.  **Run Tests:** Execute application integration tests against this schema.
4.  **Teardown:** Docker container is destroyed automatically.

**Why?** Prevents "it works on my machine" issues and tests destructively without risk.

### 3. Dry-Run Verification

Before applying to Production, execute a dry run request:

```bash
# 1. Update Testing Rollback (Verifies rollback SQL works)
liquibase updateTestingRollback

# 2. Preview SQL (Manual Review)
liquibase updateSQL
```

[↑ Back to Table of Contents](#table-of-contents)

## Migration from Legacy

### Adopting This Structure

**Phase 1: Assessment**
Inventory all databases and identify which need baselines.

**Phase 2: Setup Infrastructure**
Create directory structure and property templates.

**Phase 3: Pilot Database**

1. Generate baseline.
2. Review and clean up.
3. Create master changelog.
4. Sync to existing environments (`changelogSync`).
5. Make first incremental change.

**Phase 4: Rollout**
Repeat for all databases, prioritizing by risk (lowest first).

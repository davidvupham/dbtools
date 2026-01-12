# Liquibase Operations Guide

**🔗 [← Back to Liquibase Documentation Index](../../explanation/liquibase/README.md)** — Navigation guide for all Liquibase docs

> **Document Version:** 2.0
> **Last Updated:** January 6, 2026
> **Status:** Production
> **Related Docs:** [Concepts](../../explanation/concepts/liquibase/liquibase-concepts.md) | [Architecture](../../explanation/architecture/liquibase/liquibase-architecture.md) | [Reference](../../reference/liquibase/liquibase-reference.md)

This guide covers day-to-day tasks: writing changesets, deploying changes, handling rollbacks, testing, and troubleshooting.

> [!IMPORTANT]
> **Prerequisites:** Understand basic Liquibase concepts (Changelog, Changeset, Change Types). See [Concepts Guide](../../explanation/concepts/liquibase/liquibase-concepts.md) if you're new to Liquibase.

> [!NOTE]
> Examples use the **Global Data Services (GDS)** team, but these procedures apply to **all teams**.

## Table of Contents

- [Authoring Changes](#authoring-changes)
  - [ChangeSet Best Practices](#changeset-best-practices)
  - [Using Preconditions](#using-preconditions)
  - [Contexts and Labels](#contexts-and-labels)
  - [Platform-Specific Changes](#platform-specific-changes)
  - [Shared Modules](#shared-modules)
  - [Reference Data](#reference-data)
- [Baseline Management](#baseline-management)
  - [Creating a Baseline (Initial Adoption)](#creating-a-baseline-initial-adoption)
  - [Baseline Reset (Consolidation)](#baseline-reset-consolidation)
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

1. **Unique IDs**: Use format `YYYYMMDD-HHMM-JIRA-description` (e.g., `20251113-1030-PROJ-45-add-user-table`)
2. **Author**: Include team/person for traceability
3. **Granularity**: One logical change per changeSet (one table, one index, etc.)
4. **Rollback**: Always provide explicit rollback for production safety
5. **Idempotency**: Use preconditions when needed to safely re-run
6. **DDL vs DML**: Keep schema changes (DDL) separate from data changes (DML) for cleaner rollbacks

### Using Preconditions

Preconditions validate the database state before executing a changeset. Use them to:

- Prevent duplicate table/column creation
- Check if objects exist before modifying
- Make changesets safely re-runnable

**Common Precondition Types:**

| Type | Purpose |
|:---|:---|
| `tableExists` | Check if table exists |
| `columnExists` | Check if column exists |
| `not` | Invert a condition |
| `sqlCheck` | Run SQL returning expected result |

**Example: Safe Column Addition**

```yaml
- changeSet:
    id: 20251220-1000-PROJ-100-add-email-verified
    author: platform-team
    preconditions:
      onFail: MARK_RAN
      - not:
          - columnExists:
              tableName: users
              columnName: email_verified
    changes:
      - addColumn:
          tableName: users
          columns:
            - column: { name: email_verified, type: boolean, defaultValueBoolean: false }
```

**onFail Options:**

| Option | Behavior |
|:---|:---|
| `HALT` | Stop deployment (default) |
| `WARN` | Log warning, continue |
| `MARK_RAN` | Skip changeset, mark as executed |
| `CONTINUE` | Skip silently |

### Contexts and Labels

- **Minimize use**: Keep schema changes environment-agnostic
- **Data seeds only**: Use `context: dev` for dev-only test data
- **Labels for filtering**: `labels: 'db:app,platform:postgres'` for multi-DB deployments

Example:

```yaml
databaseChangeLog:
  - changeSet:
      id: 20251114-01-seed-dev-data
      author: team
      context: dev
      changes:
        - loadData:
            file: ../../shared/data/reference/sample_users.csv
            tableName: users
```

### Platform-Specific Changes

Use `dbms` attribute for small platform deltas:

```yaml
- changeSet:
    id: 20251113-02-add-json-column
    dbms: postgresql
    changes:
      - addColumn:
          tableName: config
          columns:
            - column: { name: settings, type: jsonb }
```

For larger divergence, use separate files in platform-specific folders.

#### MongoDB-Specific Patterns

MongoDB uses extension change types (`ext:`) for collections and indexes. Use JSON schema changeSets for validation.

```yaml
- changeSet:
    id: 20251116-01-create-collection
    changes:
      - ext:createCollection:
          collectionName: users
```

### Shared Modules

Reusable patterns go in `shared/modules/` and can be included from any database master:

```yaml
- include:
    file: ../../shared/modules/audit/db.changelog-audit.yaml
```

### Reference Data

Store CSVs in `shared/data/reference/` and load with `loadData`:

```yaml
- changeSet:
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
  --changelog-file=applications/payments_api/postgres/orders/baseline/db.changelog-baseline-2025-11-14.yaml \
  generateChangeLog
```

**Applying Baseline to Existing Database:**
Mark it as executed without running the SQL (since schema already exists):

```bash
liquibase \
  --defaults-file=properties/liquibase.prod.properties \
  --changelog-file=applications/payments_api/postgres/orders/baseline/db.changelog-baseline.yaml \
  changelogSync

# Tag it
liquibase \
  --defaults-file=properties/liquibase.prod.properties \
  --changelog-file=applications/payments_api/postgres/orders/db.changelog-master.yaml \
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
      --changelog-file=applications/payments_api/postgres/orders/baseline/db.changelog-baseline-v2.yaml \
      generateChangeLog
    ```

2. **Create a new master changelog** referencing the consolidated baseline:

    ```yaml
    # db.changelog-master-v2.yaml
    databaseChangeLog:
      - include:
          file: baseline/db.changelog-baseline-v2.yaml
      # Future changes go here
      - include:
          file: releases/2.1/db.changelog-2.1.yaml
    ```

3. **For new instances**: Restore from a DB snapshot or run the consolidated baseline.

4. **Mark baseline as applied** (if restored from snapshot):

    ```bash
    liquibase \
      --defaults-file=properties/liquibase.new-instance.properties \
      --changelog-file=applications/payments_api/postgres/orders/db.changelog-master-v2.yaml \
      changelogSync
    ```

[↑ Back to Table of Contents](#table-of-contents)

## Execution Patterns

### Dry-Run Validation

Always validate before applying:

```bash
liquibase \
  --defaults-file properties/liquibase.dev.properties \
  --changelog-file platforms/postgres/databases/app/db.changelog-master.yaml \
  updateSQL
```

### Multi-Database Platform Deployment

Loop through all databases for a platform:

```bash
set -euo pipefail
platform=postgres
for db in app analytics; do
  cf="platforms/$platform/databases/$db/db.changelog-master.yaml"

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
  --output-file=snapshots/prod_baseline_$(date +%Y%m%d).json
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
  --referenceUrl="offline:postgresql?snapshot=snapshots/prod_baseline_20260112.json"
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
  --changelog-file=db.changelog-master.yaml \
  updateSQL > audit/deployment_$(date +%Y%m%d_%H%M%S).sql

# Preview rollback SQL
liquibase \
  --defaults-file=properties/liquibase.prod.properties \
  --changelog-file=db.changelog-master.yaml \
  rollbackSQL v1.0 > audit/rollback_$(date +%Y%m%d_%H%M%S).sql
```

#### CI/CD Integration

Add drift detection to your pipeline:

```bash
#!/bin/bash
# pre-deployment-check.sh

# Find latest snapshot
SNAPSHOT=$(ls -t snapshots/prod_*.json | head -1)

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

### Using Flow Files (Advanced)

Run standardized workflows (validate -> checks -> update) using a flow file:

```bash
liquibase flow --flow-file=liquibase.flowfile.yaml
```

### Running Quality Checks (Pro)

Analyze your changelog for policy violations before deploying:

```bash
liquibase checks run \
  --changelog-file=db.changelog-master.yaml \
  --checks-scope=changelog
```

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
  --changelog-file platforms/postgres/databases/app/db.changelog-master.yaml \
  update
```

[↑ Back to Table of Contents](#table-of-contents)

## Rollback Strategy

### Using Tags (Recommended)

Roll back to a specific release tag:

```bash
liquibase --defaults-file properties/liquibase.prod.properties \
  --changelog-file platforms/postgres/databases/app/db.changelog-master.yaml \
  rollback v1.0
```

### Using Count

Roll back last N changeSets:

```bash
liquibase ... rollbackCount 3
```

[↑ Back to Table of Contents](#table-of-contents)

## Testing Strategy

### 1. Changelog Validation

Validate syntax in CI/CD:

```bash
liquibase --changelog-file="$changelog" validate
```

### 2. Ephemeral Database Testing

Test changes on temporary databases:

1. Create temp DB.
2. Run `liquibase update`.
3. Run unit tests.
4. Drop temp DB.

### 3. Rollback Testing

Deploy → Tag → Deploy New → Rollback → Verify State.

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

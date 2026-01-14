# Liquibase Drift Management - Tutorial Guide

<!-- markdownlint-disable MD013 -->

> **📚 Main Documentation:** This guide provides tutorial-specific examples using the course helper scripts. For comprehensive documentation using standard Liquibase commands:
>
> - **[Understanding Database Drift](../../../explanation/liquibase/liquibase-drift-management.md)** - Concepts: What drift is and why it matters
> - **[Operations Guide - Drift Detection](../../../how-to/liquibase/liquibase-operations-guide.md#drift-detection-and-remediation)** - How-to: Step-by-step procedures
> - **[Reference - Drift Detection](../../../reference/liquibase/liquibase-reference.md#drift-detection-reference)** - Reference: Commands and supported objects

## Table of Contents

- [Quick Reference](#quick-reference)
- [Tutorial: Detecting Drift](#tutorial-detecting-drift)
  - [Step 1: Ensure You Have a Snapshot](#step-1-ensure-you-have-a-snapshot)
  - [Step 2: Simulate Drift](#step-2-simulate-drift)
  - [Step 3: Detect the Drift](#step-3-detect-the-drift)
- [Tutorial: Remediating Drift](#tutorial-remediating-drift)
  - [Option A: Revert the Drift](#option-a-revert-the-drift)
  - [Option B: Accept the Drift](#option-b-accept-the-drift)
- [Tutorial: SQL Generation for Audit](#tutorial-sql-generation-for-audit)
- [Using Direct Liquibase Commands](#using-direct-liquibase-commands)

---

## Quick Reference

| Task | Tutorial Script | Direct Liquibase Command |
|------|-----------------|--------------------------|
| Capture snapshot | `deploy.sh --action update` (auto) | `liquibase snapshot --snapshot-format=json` |
| Detect drift | `detect_drift.sh --dbi mssql_dev` | `liquibase diff --referenceUrl="offline:mssql?snapshot=..."` |
| Generate remediation | `generate_drift_changelog.sh` | `liquibase diffChangeLog --changelog-file=...` |
| Preview SQL | `lb -e dev -- updateSQL` | `liquibase updateSQL` |

---

## Tutorial: Detecting Drift

This tutorial uses the course helper scripts. For production use, see [Using Direct Liquibase Commands](#using-direct-liquibase-commands).

### Step 1: Ensure You Have a Snapshot

The `deploy.sh` script automatically captures snapshots after each deployment:

```bash
# Check existing snapshots
ls -lt $LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/snapshots/

# If no snapshots exist, deploy to create one
$LIQUIBASE_TUTORIAL_DIR/scripts/deploy.sh --action update --dbi mssql_dev
```

### Step 2: Simulate Drift

Create drift by making changes outside of Liquibase:

```bash
# Add an unexpected column
sqlcmd-tutorial -S mssql_dev -Q "
USE orderdb;
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('app.customer') AND name = 'loyalty_points')
    ALTER TABLE app.customer ADD loyalty_points INT DEFAULT 0;
"
```

### Step 3: Detect the Drift

```bash
# Run drift detection
$LIQUIBASE_TUTORIAL_DIR/scripts/detect_drift.sh --dbi mssql_dev
```

**Expected output:**

```text
========================================
Drift Summary
========================================

▲ UNEXPECTED (in database, not in snapshot):
  [Column(s)] app.customer.loyalty_points

========================================
⚠  DRIFT DETECTED
========================================
```

---

## Tutorial: Remediating Drift

### Option A: Revert the Drift

If the drift was unintended:

```bash
# Remove the unauthorized column
sqlcmd-tutorial -S mssql_dev -Q "
USE orderdb;
IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('app.customer') AND name = 'loyalty_points')
    ALTER TABLE app.customer DROP COLUMN loyalty_points;
"

# Verify drift is resolved
$LIQUIBASE_TUTORIAL_DIR/scripts/detect_drift.sh --dbi mssql_dev
# Expected: ✓ NO DRIFT - database matches snapshot
```

### Option B: Accept the Drift

If the drift is legitimate and should be tracked:

```bash
# Generate a changelog capturing the drift
$LIQUIBASE_TUTORIAL_DIR/scripts/generate_drift_changelog.sh -e dev \
    -o platform/mssql/database/orderdb/changelog/changes/V0003__captured_drift.xml

# Review the generated file
cat $LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changes/V0003__captured_drift.xml

# Mark as already deployed (since it exists in DB)
lb -e dev -- changelogSync --changelog-file=changelog/changes/V0003__captured_drift.xml
```

---

## Tutorial: SQL Generation for Audit

Preview the SQL that will be executed (for audit and approval):

```bash
# Preview deployment SQL
lb -e dev -- updateSQL

# Save to file for audit records
lb -e dev -- updateSQL > audit_deployment_$(date +%Y%m%d).sql

# Preview rollback SQL
lb -e dev -- rollbackSQL baseline
```

---

## Using Direct Liquibase Commands

For production environments outside this tutorial, use direct Liquibase commands without the helper scripts.

### Capture Snapshot

```bash
liquibase \
  --defaults-file=liquibase.properties \
  snapshot \
  --schemas=app \
  --snapshot-format=json \
  --output-file=snapshots/baseline_$(date +%Y%m%d).json
```

### Detect Drift

```bash
liquibase \
  --defaults-file=liquibase.properties \
  diff \
  --schemas=app \
  --referenceUrl="offline:mssql?snapshot=snapshots/baseline_20260112.json"
```

### Generate Remediation Changelog

```bash
# XML format
liquibase \
  --defaults-file=liquibase.properties \
  diffChangeLog \
  --schemas=app \
  --changelog-file=drift/captured_drift.xml \
  --referenceUrl="offline:mssql?snapshot=snapshots/baseline_20260112.json"

# SQL format (platform-specific)
liquibase \
  --defaults-file=liquibase.properties \
  diffChangeLog \
  --schemas=app \
  --changelog-file=drift/captured_drift.mssql.sql \
  --referenceUrl="offline:mssql?snapshot=snapshots/baseline_20260112.json"
```

### Preview SQL for Audit

```bash
liquibase \
  --defaults-file=liquibase.properties \
  --changelog-file=db.changelog-master.yaml \
  updateSQL > audit/deployment_$(date +%Y%m%d).sql
```

### Sync Without Running

```bash
liquibase \
  --defaults-file=liquibase.properties \
  --changelog-file=drift/captured_drift.xml \
  changelogSync
```

---

## Related Documentation

### Main Documentation (Diátaxis Structure)

| Type | Document | Description |
|------|----------|-------------|
| **Explanation** | [Understanding Database Drift](../../../explanation/liquibase/liquibase-drift-management.md) | What drift is, why it matters, conceptual strategies |
| **How-to** | [Operations Guide - Drift Detection](../../../how-to/liquibase/liquibase-operations-guide.md#drift-detection-and-remediation) | Step-by-step procedures with direct commands |
| **Reference** | [Drift Detection Reference](../../../reference/liquibase/liquibase-reference.md#drift-detection-reference) | Commands, supported objects by platform, diffTypes |

### Tutorial Series

- [Part 2: Manual Lifecycle - Step 10: Drift Detection](./series-part2-manual.md#step-10-drift-detection) - Drift detection in the tutorial context
- [Part 3: CI/CD Automation](./series-part3-cicd.md) - Automated drift detection in pipelines

#!/bin/bash
# Part 2 Tutorial Validation Script
# Executes all steps in Part 2 tutorial and captures output for review

set -e  # Exit on error
set -o pipefail  # Capture pipe failures

# Output files for results
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
VALIDATION_LOG="${LIQUIBASE_TUTORIAL_DIR:-/tmp}/tutorial_part2_validation_${TIMESTAMP}.log"
VALIDATION_REPORT="${LIQUIBASE_TUTORIAL_DIR:-/tmp}/tutorial_part2_validation_report_${TIMESTAMP}.md"
ISSUES_LOG="${LIQUIBASE_TUTORIAL_DIR:-/tmp}/tutorial_part2_issues_${TIMESTAMP}.log"

# Track issues and fixes
ISSUES_FOUND=0
FIXES_APPLIED=0
STEP_FAILURES=()

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$VALIDATION_LOG"
}

# Function to log section header
log_section() {
    echo "" | tee -a "$VALIDATION_LOG"
    echo "========================================" | tee -a "$VALIDATION_LOG"
    echo "SECTION: $*" | tee -a "$VALIDATION_LOG"
    echo "========================================" | tee -a "$VALIDATION_LOG"
    echo "" | tee -a "$VALIDATION_LOG"
}

# Function to execute command and capture output
execute_step() {
    local step_name="$1"
    local command="$2"
    local expected_result="${3:-0}"  # Default expected exit code is 0

    log_section "$step_name"
    log "Executing: $command"

    if eval "$command" >> "$VALIDATION_LOG" 2>&1; then
        local exit_code=$?
        if [ $exit_code -eq $expected_result ]; then
            log "✓ SUCCESS: $step_name"
            return 0
        else
            log "✗ UNEXPECTED EXIT CODE: $step_name (got $exit_code, expected $expected_result)"
            STEP_FAILURES+=("$step_name (exit code: $exit_code)")
            ((ISSUES_FOUND++))
            return $exit_code
        fi
    else
        local exit_code=$?
        log "✗ FAILED: $step_name (exit code: $exit_code)"
        STEP_FAILURES+=("$step_name (exit code: $exit_code)")
        ((ISSUES_FOUND++))
        return $exit_code
    fi
}

# Function to verify command output contains expected text
verify_output() {
    local step_name="$1"
    local command="$2"
    local expected_text="$3"

    log "Verifying: $step_name"
    log "Command: $command"
    log "Expected text: $expected_text"

    local output
    output=$(eval "$command" 2>&1 | tee -a "$VALIDATION_LOG")

    if echo "$output" | grep -q "$expected_text"; then
        log "✓ VERIFIED: $step_name contains expected text"
        return 0
    else
        log "✗ VERIFICATION FAILED: $step_name - expected text not found"
        log "Actual output: $output"
        STEP_FAILURES+=("$step_name (verification failed)")
        ((ISSUES_FOUND++))
        return 1
    fi
}

# Initialize report
cat > "$VALIDATION_REPORT" << EOF
# Tutorial Part 2 Validation Report

**Date:** $(date)
**Environment:** Ubuntu Linux
**Tutorial:** Part 2: Manual Liquibase Deployment Lifecycle

## Executive Summary

This report documents the validation of all steps in the Part 2 tutorial, including:
- Step execution results
- Issues found and fixes applied
- Grammar and spelling corrections
- Clarity and instruction improvements

---

## Validation Results

EOF

log "Starting Part 2 tutorial validation"
log "Log file: $VALIDATION_LOG"
log "Report file: $VALIDATION_REPORT"
log "Issues log: $ISSUES_LOG"

# ============================================================================
# PRE-VALIDATION: Check Prerequisites
# ============================================================================
log_section "Pre-Validation: Check Prerequisites"

# Check if LIQUIBASE_TUTORIAL_DIR is set
if [ -z "${LIQUIBASE_TUTORIAL_DIR:-}" ]; then
    export LIQUIBASE_TUTORIAL_DIR="/home/dpham/src/dbtools/docs/courses/liquibase"
    log "Set LIQUIBASE_TUTORIAL_DIR to: $LIQUIBASE_TUTORIAL_DIR"
fi

# Source setup script
if [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/setup_tutorial.sh" ]; then
    log "Sourcing setup_tutorial.sh"
    export MSSQL_LIQUIBASE_TUTORIAL_PWD="${MSSQL_LIQUIBASE_TUTORIAL_PWD:-TestPassword123!}"
    # Source in a way that captures errors
    if ! source "$LIQUIBASE_TUTORIAL_DIR/scripts/setup_tutorial.sh" >> "$VALIDATION_LOG" 2>&1; then
        log "⚠ Warning: setup_tutorial.sh had issues (may be normal if already sourced)"
    fi
else
    log "✗ ERROR: setup_tutorial.sh not found"
    ((ISSUES_FOUND++))
fi

# Check if LIQUIBASE_TUTORIAL_DATA_DIR is set
if [ -z "${LIQUIBASE_TUTORIAL_DATA_DIR:-}" ]; then
    export LIQUIBASE_TUTORIAL_DATA_DIR="/data/$(whoami)/liquibase_tutorial"
    log "Set LIQUIBASE_TUTORIAL_DATA_DIR to: $LIQUIBASE_TUTORIAL_DATA_DIR"
fi

log "LIQUIBASE_TUTORIAL_DATA_DIR=$LIQUIBASE_TUTORIAL_DATA_DIR"

# Check if containers are running
log "Checking if SQL Server containers are running..."
if docker ps --format '{{.Names}}' | grep -qE '^mssql_(dev|stg|prd)$'; then
    log "✓ SQL Server containers are running"
    docker ps --format 'table {{.Names}}\t{{.Status}}' | grep mssql_ >> "$VALIDATION_LOG" 2>&1 || true
else
    log "✗ ERROR: SQL Server containers not running. Part 1 must be completed first."
    log "Expected containers: mssql_dev, mssql_stg, mssql_prd"
    ((ISSUES_FOUND++))
    STEP_FAILURES+=("Prerequisites: SQL Server containers not running")
fi

# Check if baseline exists
if [ -f "$LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog/baseline/V0000__baseline.mssql.sql" ]; then
    log "✓ Baseline file exists"
else
    log "✗ ERROR: Baseline file not found. Part 1 must be completed first."
    ((ISSUES_FOUND++))
    STEP_FAILURES+=("Prerequisites: Baseline file missing")
fi

# Check if changelog.xml exists
if [ -f "$LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog/changelog.xml" ]; then
    log "✓ Changelog.xml exists"
else
    log "✗ ERROR: changelog.xml not found. Part 1 must be completed first."
    ((ISSUES_FOUND++))
    STEP_FAILURES+=("Prerequisites: changelog.xml missing")
fi

# ============================================================================
# STEP 6: Making Your First Change
# ============================================================================
log_section "Step 6: Making Your First Change"

# Create V0001 change file
log "Creating V0001__add_orders_table.mssql.sql"
mkdir -p "$LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog/changes"

cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog/changes/V0001__add_orders_table.mssql.sql" << 'EOF'
--liquibase formatted sql

--changeset tutorial:V0001-add-orders-table
-- Purpose: Add orders table to track customer purchases
-- This change creates:
--   - orders table with 5 columns (order_id, customer_id, order_total, order_date, status)
--   - Primary key constraint (PK_orders)
--   - Foreign key constraint to customer table (FK_orders_customer)
--   - Two default constraints (DF_orders_date for order_date, inline default for status)

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE object_id = OBJECT_ID(N'[app].[orders]') AND type = 'U')
BEGIN
    CREATE TABLE app.orders (
        order_id INT IDENTITY(1,1) CONSTRAINT PK_orders PRIMARY KEY,
        customer_id INT NOT NULL,
        order_total DECIMAL(18,2) NOT NULL,
        order_date DATETIME2(3) NOT NULL CONSTRAINT DF_orders_date DEFAULT (SYSUTCDATETIME()),
        status NVARCHAR(50) NOT NULL DEFAULT 'pending',
        CONSTRAINT FK_orders_customer FOREIGN KEY (customer_id)
            REFERENCES app.customer(customer_id)
    );
END
GO
EOF

if [ -f "$LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog/changes/V0001__add_orders_table.mssql.sql" ]; then
    log "✓ V0001 change file created"
else
    log "✗ ERROR: Failed to create V0001 change file"
    ((ISSUES_FOUND++))
fi

# Update changelog.xml
log "Updating changelog.xml to include V0001"
cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog/changelog.xml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <!-- Baseline: initial database state -->
    <include file="baseline/V0000__baseline.mssql.sql" relativeToChangelogFile="true"/>

    <!-- V0001: Add orders table -->
    <include file="changes/V0001__add_orders_table.mssql.sql" relativeToChangelogFile="true"/>
</databaseChangeLog>
EOF

# Deploy to Development
log "Deploying to Development"
cd "$LIQUIBASE_TUTORIAL_DATA_DIR"

execute_step "Preview updateSQL for dev" "lb -e dev -- updateSQL"
execute_step "Deploy to dev" "lb -e dev -- update"

# Verify in dev
log "Verifying deployment in dev"
verify_output "Verify orders table in dev" \
    "sqlcmd-tutorial -Q \"USE orderdb; SELECT COUNT(*) AS TableCount FROM sys.objects WHERE schema_id = SCHEMA_ID('app') AND type = 'U' AND name = 'orders';\"" \
    "1"

# ============================================================================
# STEP 7: Promoting Changes to Staging and Production
# ============================================================================
log_section "Step 7: Promoting Changes to Staging and Production"

# Deploy to Staging
execute_step "Preview updateSQL for stg" "lb -e stg -- updateSQL"
execute_step "Deploy to stg" "lb -e stg -- update"

# Verify in staging
verify_output "Verify orders table in stg" \
    "sqlcmd-tutorial -Q \"USE orderdb; SELECT COUNT(*) AS TableCount FROM sys.objects WHERE schema_id = SCHEMA_ID('app') AND type = 'U' AND name = 'orders';\"" \
    "1"

# Deploy to Production
execute_step "Preview updateSQL for prd" "lb -e prd -- updateSQL"
execute_step "Deploy to prd" "lb -e prd -- update"

# Verify in production
verify_output "Verify orders table in prd" \
    "sqlcmd-tutorial -Q \"USE orderdb; SELECT COUNT(*) AS TableCount FROM sys.objects WHERE schema_id = SCHEMA_ID('app') AND type = 'U' AND name = 'orders';\"" \
    "1"

# ============================================================================
# STEP 8: Tags and Release Management
# ============================================================================
log_section "Step 8: Tags and Release Management"

# Create release tags
execute_step "Tag dev as release-v1.0" "lb -e dev -- tag release-v1.0"
execute_step "Tag stg as release-v1.0" "lb -e stg -- tag release-v1.0"
execute_step "Tag prd as release-v1.0" "lb -e prd -- tag release-v1.0"

# Query DATABASECHANGELOG
log "Querying DATABASECHANGELOG"
sqlcmd-tutorial -Q "
USE orderdb;
SELECT
    ID,
    AUTHOR,
    FILENAME,
    DATEEXECUTED,
    TAG,
    EXECTYPE
FROM DATABASECHANGELOG
ORDER BY ORDEREXECUTED DESC;
" >> "$VALIDATION_LOG" 2>&1

# ============================================================================
# STEP 9: Rollback Strategies
# ============================================================================
log_section "Step 9: Rollback Strategies"

# Add rollback to V0001 file
log "Adding rollback block to V0001 file"
cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog/changes/V0001__add_orders_table.mssql.sql" << 'EOF'
--liquibase formatted sql

--changeset tutorial:V0001-add-orders-table
-- Purpose: Add orders table to track customer purchases

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE object_id = OBJECT_ID(N'[app].[orders]') AND type = 'U')
BEGIN
    CREATE TABLE app.orders (
        order_id INT IDENTITY(1,1) CONSTRAINT PK_orders PRIMARY KEY,
        customer_id INT NOT NULL,
        order_total DECIMAL(18,2) NOT NULL,
        order_date DATETIME2(3) NOT NULL CONSTRAINT DF_orders_date DEFAULT (SYSUTCDATETIME()),
        status NVARCHAR(50) NOT NULL DEFAULT 'pending',
        CONSTRAINT FK_orders_customer FOREIGN KEY (customer_id)
            REFERENCES app.customer(customer_id)
    );
END
GO
--rollback DROP TABLE IF EXISTS app.orders;
--rollback GO
EOF

# Practice rollback (dev only)
log "Practicing rollback in dev (development only)"
execute_step "Preview rollbackSQL" "lb -e dev -- rollbackSQL baseline"
execute_step "Execute rollback to baseline" "lb -e dev -- rollback baseline"

# Verify orders table is gone
verify_output "Verify orders table removed after rollback" \
    "sqlcmd-tutorial -Q \"USE orderdb; SELECT COUNT(*) AS TableCount FROM sys.objects WHERE schema_id = SCHEMA_ID('app') AND type = 'U' AND name = 'orders';\"" \
    "0"

# Re-apply after rollback
log "Re-applying V0001 after rollback"
execute_step "Re-deploy V0001" "lb -e dev -- update"
execute_step "Re-tag release-v1.0" "lb -e dev -- tag release-v1.0"

# ============================================================================
# STEP 10: Drift Detection
# ============================================================================
log_section "Step 10: Drift Detection"

# Simulate drift
log "Simulating drift by adding column directly to database"
sqlcmd-tutorial -Q "
USE orderdb;
-- Someone adds a column without using Liquibase
ALTER TABLE app.customer ADD loyalty_points INT DEFAULT 0;
" >> "$VALIDATION_LOG" 2>&1

# Detect drift with diff
log "Detecting drift with diff command"
execute_step "Detect drift" "lb -e dev -- diff --referenceUrl='offline:mssql?changeLogFile=database/changelog/changelog.xml'"

# Generate changelog from drift
log "Generating changelog from drift"
mkdir -p "$LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog/changes"
execute_step "Generate diffChangeLog" \
    "lb -e dev -- diffChangeLog --referenceUrl='offline:mssql?changeLogFile=database/changelog/changelog.xml' --changelogFile=$LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog/changes/V0002__drift_loyalty_points.xml"

# Remove the drift column to restore state
log "Removing drift column to restore state"
sqlcmd-tutorial -Q "
USE orderdb;
ALTER TABLE app.customer DROP COLUMN loyalty_points;
" >> "$VALIDATION_LOG" 2>&1

# ============================================================================
# STEP 11: Additional Changesets
# ============================================================================
log_section "Step 11: Additional Changesets"

# Create V0002 index file
log "Creating V0002__add_orders_index.mssql.sql"
cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog/changes/V0002__add_orders_index.mssql.sql" << 'EOF'
--liquibase formatted sql

--changeset tutorial:V0002-add-orders-date-index
-- Purpose: Add performance index on order_date for reporting queries

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_orders_order_date'
    AND object_id = OBJECT_ID('app.orders')
)
BEGIN
    CREATE INDEX IX_orders_order_date ON app.orders(order_date DESC);
END
GO
--rollback DROP INDEX IF EXISTS IX_orders_order_date ON app.orders;
--rollback GO
EOF

# Update master changelog
log "Updating master changelog to include V0002"
cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog/changelog.xml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <!-- Baseline -->
    <include file="baseline/V0000__baseline.mssql.sql" relativeToChangelogFile="true"/>

    <!-- V0001: Add orders table -->
    <include file="changes/V0001__add_orders_table.mssql.sql" relativeToChangelogFile="true"/>

    <!-- V0002: Add orders index -->
    <include file="changes/V0002__add_orders_index.mssql.sql" relativeToChangelogFile="true"/>

</databaseChangeLog>
EOF

# Deploy through environments
execute_step "Deploy V0002 to dev" "lb -e dev -- update"
execute_step "Tag dev as release-v1.1" "lb -e dev -- tag release-v1.1"
execute_step "Deploy V0002 to stg" "lb -e stg -- update"
execute_step "Tag stg as release-v1.1" "lb -e stg -- tag release-v1.1"
execute_step "Deploy V0002 to prd" "lb -e prd -- update"
execute_step "Tag prd as release-v1.1" "lb -e prd -- tag release-v1.1"

# ============================================================================
# Final Summary
# ============================================================================
log_section "Validation Summary"

log "Total issues found: $ISSUES_FOUND"
log "Total fixes applied: $FIXES_APPLIED"

if [ ${#STEP_FAILURES[@]} -gt 0 ]; then
    log "Step failures:"
    for failure in "${STEP_FAILURES[@]}"; do
        log "  - $failure"
    done
fi

log ""
log "Validation complete. Review log file: $VALIDATION_LOG"
log "Review report file: $VALIDATION_REPORT"

# Append summary to report
cat >> "$VALIDATION_REPORT" << EOF

## Summary

- **Total Issues Found:** $ISSUES_FOUND
- **Total Fixes Applied:** $FIXES_APPLIED
- **Validation Log:** $VALIDATION_LOG

---

## Step Failures

EOF

if [ ${#STEP_FAILURES[@]} -gt 0 ]; then
    for failure in "${STEP_FAILURES[@]}"; do
        echo "- $failure" >> "$VALIDATION_REPORT"
    done
else
    echo "No step failures detected." >> "$VALIDATION_REPORT"
fi

cat >> "$VALIDATION_REPORT" << EOF

---

## Detailed Results

See the validation log file for detailed execution output: \`$VALIDATION_LOG\`

---

## Issues and Fixes

This section will be populated with grammar/spelling corrections and clarity improvements found during validation.

EOF

echo ""
echo "========================================"
echo "Part 2 Validation Complete!"
echo "========================================"
echo "Log: $VALIDATION_LOG"
echo "Report: $VALIDATION_REPORT"
echo ""

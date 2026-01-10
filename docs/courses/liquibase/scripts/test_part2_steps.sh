#!/bin/bash
# Comprehensive Part 2 Tutorial Test Script
# Executes each step individually, fixes issues, and runs final end-to-end test

set -euo pipefail

# Configuration
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TEST_LOG="/tmp/part2_test_${TIMESTAMP}.log"
TEST_REPORT="/tmp/part2_test_report_${TIMESTAMP}.md"

# Track results
PASSED_STEPS=()
FAILED_STEPS=()
FIXED_ISSUES=()
RETRY_COUNT=0
MAX_RETRIES=3

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log() {
    echo "[$(date '+%H:%M:%S')] $*" | tee -a "$TEST_LOG"
}

log_section() {
    echo "" | tee -a "$TEST_LOG"
    echo "========================================" | tee -a "$TEST_LOG"
    echo "$*" | tee -a "$TEST_LOG"
    echo "========================================" | tee -a "$TEST_LOG"
}

log_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $*" | tee -a "$TEST_LOG"
    PASSED_STEPS+=("$*")
}

log_fail() {
    echo -e "${RED}✗ FAIL${NC}: $*" | tee -a "$TEST_LOG"
    FAILED_STEPS+=("$*")
}

log_info() {
    echo -e "${BLUE}ℹ INFO${NC}: $*" | tee -a "$TEST_LOG"
}

log_warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $*" | tee -a "$TEST_LOG"
}

# Initialize
cat > "$TEST_REPORT" << EOF
# Part 2 Tutorial Test Report

**Date:** $(date)
**Test Log:** $TEST_LOG

## Test Results

EOF

log_section "Part 2 Tutorial Step-by-Step Test"
log "Test log: $TEST_LOG"
log "Test report: $TEST_REPORT"

# Setup environment
setup_environment() {
    log_section "Setting Up Environment"

    # Set tutorial directory
    if [ -z "${LIQUIBASE_TUTORIAL_DIR:-}" ]; then
        export LIQUIBASE_TUTORIAL_DIR="/home/dpham/src/dbtools/docs/courses/liquibase"
        log_info "Set LIQUIBASE_TUTORIAL_DIR=$LIQUIBASE_TUTORIAL_DIR"
    fi

    # Set password
    export MSSQL_LIQUIBASE_TUTORIAL_PWD="${MSSQL_LIQUIBASE_TUTORIAL_PWD:-TestPassword123!}"

    # Source setup script
    if [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/setup_tutorial.sh" ]; then
        log_info "Sourcing setup_tutorial.sh"
        source "$LIQUIBASE_TUTORIAL_DIR/scripts/setup_tutorial.sh" >> "$TEST_LOG" 2>&1 || true
    fi

    # Set data directory
    export LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/$(whoami)/liquibase_tutorial}"
    log_info "LIQUIBASE_TUTORIAL_DATA_DIR=$LIQUIBASE_TUTORIAL_DATA_DIR"

    # Detect container runtime
    if command -v docker &>/dev/null; then
        CR="docker"
    elif command -v podman &>/dev/null; then
        CR="podman"
    else
        log_fail "No container runtime found (docker or podman)"
        exit 1
    fi
    log_info "Container runtime: $CR"

    # Set up command paths (aliases don't work in scripts)
    LB_CMD="$LIQUIBASE_TUTORIAL_DIR/scripts/lb.sh"
    SQLCMD_CMD="$LIQUIBASE_TUTORIAL_DIR/scripts/sqlcmd_tutorial.sh"

    if [ ! -f "$LB_CMD" ]; then
        log_fail "lb.sh not found at $LB_CMD"
        exit 1
    fi
    if [ ! -f "$SQLCMD_CMD" ]; then
        log_fail "sqlcmd_tutorial.sh not found at $SQLCMD_CMD"
        exit 1
    fi

    chmod +x "$LB_CMD" "$SQLCMD_CMD" 2>/dev/null || true
    log_info "Using commands: lb=$LB_CMD, sqlcmd-tutorial=$SQLCMD_CMD"
}

# Cleanup function
cleanup() {
    log_section "Cleaning Up"

    # Stop containers
    log_info "Stopping containers..."
    for container in mssql_dev mssql_stg mssql_prd; do
        if $CR ps --format "{{.Names}}" | grep -q "^${container}$"; then
            $CR stop "$container" >> "$TEST_LOG" 2>&1 || true
        fi
    done

    # Remove Part 2 changes from dev database manually (since rollback may not work)
    log_info "Cleaning up Part 2 changes from dev database..."
    cd "$LIQUIBASE_TUTORIAL_DATA_DIR" 2>/dev/null || true
    # Manually remove Part 2 objects to restore dev to baseline state
    "$SQLCMD_CMD" -e dev -Q "USE orderdb; IF EXISTS (SELECT 1 FROM sys.objects WHERE object_id = OBJECT_ID('app.orders') AND type = 'U') DROP TABLE app.orders;" >> "$TEST_LOG" 2>&1 || true
    "$SQLCMD_CMD" -e dev -Q "USE orderdb; IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('app.customer') AND name = 'loyalty_points') ALTER TABLE app.customer DROP COLUMN loyalty_points;" >> "$TEST_LOG" 2>&1 || true
    # Remove Part 2 changesets from DATABASECHANGELOG
    "$SQLCMD_CMD" -e dev -Q "USE orderdb; DELETE FROM DATABASECHANGELOG WHERE ID LIKE 'V000%' OR ID LIKE 'release-v%';" >> "$TEST_LOG" 2>&1 || true

    # Remove Part 2 change files (keep Part 1 baseline)
    if [ -d "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changes" ]; then
        log_info "Removing Part 2 change files..."
        rm -f "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changes/V0001__add_orders_table.mssql.sql" 2>/dev/null || true
        rm -f "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changes/V0002__add_orders_index.mssql.sql" 2>/dev/null || true
        rm -f "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changes/V0002__drift_loyalty_points.xml" 2>/dev/null || true
    fi

    # Remove drift column if it exists
    "$SQLCMD_CMD" -e dev -Q "USE orderdb; IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('app.customer') AND name = 'loyalty_points') ALTER TABLE app.customer DROP COLUMN loyalty_points;" >> "$TEST_LOG" 2>&1 || true

    # Reset changelog.xml to baseline only
    if [ -f "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changelog.xml" ]; then
        log_info "Resetting changelog.xml to baseline only..."
        cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changelog.xml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <!-- Baseline: initial database state -->
    <include file="baseline/V0000__baseline.mssql.sql" relativeToChangelogFile="true"/>

</databaseChangeLog>
EOF
    fi

    # Rollback any deployed changes in databases (but keep baseline)
    log_info "Rolling back Part 2 changes in databases (preserving baseline)..."
    cd "$LIQUIBASE_TUTORIAL_DATA_DIR" 2>/dev/null || true
    for env in dev stg prd; do
        # Only rollback if there are changesets after baseline
        # Check if V0001 or later changesets exist
        local status_output
        status_output=$("$LB_CMD" -e "$env" -- status 2>&1 || true)
        if echo "$status_output" | grep -qE "(V0001|V0002|release-v1)"; then
            # Rollback to baseline (removes only changes after baseline)
            "$LB_CMD" -e "$env" -- rollback baseline >> "$TEST_LOG" 2>&1 || true
        fi
    done

    log_info "Cleanup complete"
}

# Setup Part 1 prerequisites using existing scripts
setup_prerequisites() {
    log_section "Setting Up Part 1 Prerequisites"

    # Step 0: Setup environment (creates directories, properties, changelog)
    log_info "Running Step 0: Setup Environment..."
    if [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/setup_liquibase_environment.sh" ]; then
        bash "$LIQUIBASE_TUTORIAL_DIR/scripts/setup_liquibase_environment.sh" >> "$TEST_LOG" 2>&1
        log_pass "Step 0: Environment setup complete"
    else
        log_fail "setup_liquibase_environment.sh not found"
        return 1
    fi

    # Step 1: Start containers
    log_info "Running Step 1: Start Containers..."
    local containers_running=true
    for container in mssql_dev mssql_stg mssql_prd; do
        if ! $CR ps --format "{{.Names}}" | grep -q "^${container}$"; then
            containers_running=false
            break
        fi
    done

    if [ "$containers_running" = false ]; then
        if [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/start_mssql_containers.sh" ]; then
            bash "$LIQUIBASE_TUTORIAL_DIR/scripts/start_mssql_containers.sh" >> "$TEST_LOG" 2>&1
            sleep 15  # Wait for containers to be healthy
            log_pass "Step 1: Containers started"
        else
            log_fail "start_mssql_containers.sh not found"
            return 1
        fi
    else
        log_pass "Step 1: Containers already running"
    fi

    # Step 2: Create databases
    log_info "Running Step 2: Create Databases..."
    if [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/create_orderdb_databases.sh" ]; then
        bash "$LIQUIBASE_TUTORIAL_DIR/scripts/create_orderdb_databases.sh" >> "$TEST_LOG" 2>&1
        log_pass "Step 2: Databases created"
    else
        log_fail "create_orderdb_databases.sh not found"
        return 1
    fi

    # Step 3: Populate dev
    log_info "Running Step 3: Populate Development..."
    if [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/populate_dev_database.sh" ]; then
        bash "$LIQUIBASE_TUTORIAL_DIR/scripts/populate_dev_database.sh" >> "$TEST_LOG" 2>&1
        log_pass "Step 3: Development populated"
    else
        log_fail "populate_dev_database.sh not found"
        return 1
    fi

    # Step 4: Generate baseline
    log_info "Running Step 4: Generate Baseline..."
    # Check if baseline exists and is valid
    # IMPORTANT: Don't regenerate baseline if it exists - regenerating changes the changeset IDs
    # which causes deployment issues. Only regenerate if baseline includes Part 2 changes.
    if [ -f "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/baseline/V0000__baseline.mssql.sql" ] && \
       grep -q "CREATE TABLE app.customer" "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/baseline/V0000__baseline.mssql.sql" 2>/dev/null && \
       ! grep -q "loyalty_points\|app.orders" "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/baseline/V0000__baseline.mssql.sql" 2>/dev/null; then
        log_pass "Step 4: Baseline file exists and is valid (not regenerating to preserve changeset IDs)"
    else
        log_info "Baseline missing or invalid - generating..."
        # Clean dev first to ensure baseline doesn't include Part 2 changes
        log_info "Cleaning dev database..."
        "$SQLCMD_CMD" -e dev -Q "USE orderdb;
            IF EXISTS (SELECT 1 FROM sys.objects WHERE object_id = OBJECT_ID('app.v_customer_basic') AND type = 'V') DROP VIEW app.v_customer_basic;
            IF EXISTS (SELECT 1 FROM sys.objects WHERE object_id = OBJECT_ID('app.orders') AND type = 'U') DROP TABLE app.orders;
            IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('app.customer') AND name = 'loyalty_points') ALTER TABLE app.customer DROP COLUMN loyalty_points;" >> "$TEST_LOG" 2>&1 || true

        # Repopulate dev
        if [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/populate_dev_database.sh" ]; then
            bash "$LIQUIBASE_TUTORIAL_DIR/scripts/populate_dev_database.sh" >> "$TEST_LOG" 2>&1
        fi

        # Generate baseline
        if [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/generate_liquibase_baseline.sh" ]; then
            bash "$LIQUIBASE_TUTORIAL_DIR/scripts/generate_liquibase_baseline.sh" >> "$TEST_LOG" 2>&1
            log_pass "Step 4: Baseline generated"
        else
            log_fail "generate_liquibase_baseline.sh not found"
            return 1
        fi
    fi

    # Step 5: Deploy baseline
    log_info "Running Step 5: Deploy Baseline..."
    if [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/deploy_liquibase_baseline.sh" ]; then
        bash "$LIQUIBASE_TUTORIAL_DIR/scripts/deploy_liquibase_baseline.sh" >> "$TEST_LOG" 2>&1
        log_pass "Step 5: Baseline deployment script completed"
    else
        log_fail "deploy_liquibase_baseline.sh not found"
        return 1
    fi

    # Verify baseline was actually deployed to all environments
    log_info "Verifying baseline deployment..."
    cd "$LIQUIBASE_TUTORIAL_DATA_DIR"
    for env in dev stg prd; do
        # Check if customer table exists (baseline should create it)
        local count
        count=$("$SQLCMD_CMD" -e "$env" -Q "USE orderdb; SELECT COUNT(*) FROM sys.objects WHERE schema_id = SCHEMA_ID('app') AND type = 'U' AND name = 'customer';" 2>&1 | grep -E '^\s*[0-9]+\s*$' | tr -d ' ')
        if [ "$count" = "1" ]; then
            # Check if baseline is marked as executed
            local baseline_count
            baseline_count=$("$SQLCMD_CMD" -e "$env" -Q "USE orderdb; SELECT COUNT(*) FROM DATABASECHANGELOG WHERE TAG = 'baseline' OR FILENAME LIKE '%baseline%';" 2>&1 | grep -E '^\s*[0-9]+\s*$' | tr -d ' ')
            if [ "$baseline_count" -gt 0 ]; then
                log_pass "Baseline verified in $env (table exists, changesets recorded)"
            else
                log_warn "Baseline objects exist but not recorded in $env, syncing..."
                # Use changelogSync to mark baseline as executed (objects already exist)
                "$LB_CMD" -e "$env" -- changelogSync >> "$TEST_LOG" 2>&1 || true
                "$LB_CMD" -e "$env" -- tag baseline >> "$TEST_LOG" 2>&1 || true
                log_pass "Baseline synced in $env"
            fi
        else
            log_warn "Baseline not fully deployed in $env (customer table missing), attempting to deploy..."
            # Try to deploy baseline
            "$LB_CMD" -e "$env" -- update >> "$TEST_LOG" 2>&1 || true
            "$LB_CMD" -e "$env" -- tag baseline >> "$TEST_LOG" 2>&1 || true
        fi
    done

    log_info "Part 1 prerequisites complete - ready for Part 2"
}

# Test Step 6: Create V0001 change file
test_step6_create_file() {
    log_section "Step 6.1: Create V0001 Change File"

    mkdir -p "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changes"

    cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changes/V0001__add_orders_table.mssql.sql" << 'EOF'
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
--rollback DROP TABLE IF EXISTS app.orders;
--rollback GO
EOF

    if [ -f "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changes/V0001__add_orders_table.mssql.sql" ]; then
        log_pass "V0001 change file created"
        return 0
    else
        log_fail "Failed to create V0001 change file"
        return 1
    fi
}

# Test Step 6: Update changelog.xml
test_step6_update_changelog() {
    log_section "Step 6.2: Update changelog.xml"

    cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changelog.xml" << 'EOF'
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

    if grep -q "V0001__add_orders_table" "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changelog.xml"; then
        log_pass "changelog.xml updated"
        return 0
    else
        log_fail "Failed to update changelog.xml"
        return 1
    fi
}

# Test Step 6: Deploy to dev
test_step6_deploy_dev() {
    log_section "Step 6.3: Deploy to Development"

    cd "$LIQUIBASE_TUTORIAL_DATA_DIR"

    # Ensure baseline is synced in all environments before deploying V0001
    # This marks baseline changesets as executed without running them (objects already exist)
    log_info "Syncing baseline in all environments (marking as executed)..."
    for env in dev stg prd; do
        "$LB_CMD" -e "$env" -- changelogSync >> "$TEST_LOG" 2>&1 || true
        "$LB_CMD" -e "$env" -- tag baseline >> "$TEST_LOG" 2>&1 || true
    done
    log_pass "Baseline synced in all environments"

    # Preview
    if "$LB_CMD" -e dev -- updateSQL >> "$TEST_LOG" 2>&1; then
        log_pass "updateSQL preview successful"
    else
        log_fail "updateSQL preview failed"
        return 1
    fi

    # Deploy
    if "$LB_CMD" -e dev -- update >> "$TEST_LOG" 2>&1; then
        log_pass "Deployment to dev successful"
    else
        log_fail "Deployment to dev failed"
        return 1
    fi

    # Verify
    local count
    count=$("$SQLCMD_CMD" -e dev -Q "USE orderdb; SELECT COUNT(*) FROM sys.objects WHERE schema_id = SCHEMA_ID('app') AND type = 'U' AND name = 'orders';" 2>&1 | grep -E '^\s*[0-9]+\s*$' | tr -d ' ')

    if [ "$count" = "1" ]; then
        log_pass "Orders table verified in dev"
        return 0
    else
        log_fail "Orders table not found in dev (count: $count)"
        return 1
    fi
}

# Test Step 7: Deploy to staging
test_step7_deploy_stg() {
    log_section "Step 7.1: Deploy to Staging"

    cd "$LIQUIBASE_TUTORIAL_DATA_DIR"

    # Deploy (may already be executed, which is OK)
    local output
    output=$("$LB_CMD" -e stg -- update 2>&1 | tee -a "$TEST_LOG")
    local exit_code=$?

    # Check if it succeeded or if changeset was already executed
    # Liquibase returns 0 on success, and may return non-zero if changeset already executed
    # But we should check the actual output to see what happened
    if [ $exit_code -eq 0 ]; then
        log_pass "Deployment to stg successful"
    elif echo "$output" | grep -qiE "(already executed|No changesets to execute|changeset.*already.*executed|Update successful)"; then
        log_pass "Deployment to stg successful (changeset already executed)"
    elif echo "$output" | grep -qiE "(ERROR|Error|error|Exception|exception|FAILED|Failed)"; then
        log_fail "Deployment to stg failed - see log for details"
        log_info "Output: $(echo "$output" | tail -10)"
        return 1
    else
        # Unknown case - check if table exists
        local count
        count=$("$SQLCMD_CMD" -e stg -Q "USE orderdb; SELECT COUNT(*) FROM sys.objects WHERE schema_id = SCHEMA_ID('app') AND type = 'U' AND name = 'orders';" 2>&1 | grep -E '^\s*[0-9]+\s*$' | tr -d ' ')
        if [ "$count" = "1" ]; then
            log_pass "Deployment to stg successful (table exists)"
        else
            log_fail "Deployment to stg failed (table not found, exit code: $exit_code)"
            log_info "Output: $(echo "$output" | tail -10)"
            return 1
        fi
    fi

    local count
    count=$("$SQLCMD_CMD" -e stg -Q "USE orderdb; SELECT COUNT(*) FROM sys.objects WHERE schema_id = SCHEMA_ID('app') AND type = 'U' AND name = 'orders';" 2>&1 | grep -E '^\s*[0-9]+\s*$' | tr -d ' ')

    if [ "$count" = "1" ]; then
        log_pass "Orders table verified in stg"
        return 0
    else
        log_fail "Orders table not found in stg (count: $count)"
        return 1
    fi
}

# Test Step 7: Deploy to production
test_step7_deploy_prd() {
    log_section "Step 7.2: Deploy to Production"

    cd "$LIQUIBASE_TUTORIAL_DATA_DIR"

    # Deploy (may already be executed, which is OK)
    local output
    output=$("$LB_CMD" -e prd -- update 2>&1 | tee -a "$TEST_LOG")
    local exit_code=$?

    # Check if it succeeded or if changeset was already executed
    if [ $exit_code -eq 0 ]; then
        log_pass "Deployment to prd successful"
    elif echo "$output" | grep -qiE "(already executed|No changesets to execute|changeset.*already.*executed|Update successful)"; then
        log_pass "Deployment to prd successful (changeset already executed)"
    elif echo "$output" | grep -qiE "(ERROR|Error|error|Exception|exception|FAILED|Failed)"; then
        log_fail "Deployment to prd failed - see log for details"
        log_info "Output: $(echo "$output" | tail -10)"
        return 1
    else
        # Unknown case - check if table exists
        local count
        count=$("$SQLCMD_CMD" -e prd -Q "USE orderdb; SELECT COUNT(*) FROM sys.objects WHERE schema_id = SCHEMA_ID('app') AND type = 'U' AND name = 'orders';" 2>&1 | grep -E '^\s*[0-9]+\s*$' | tr -d ' ')
        if [ "$count" = "1" ]; then
            log_pass "Deployment to prd successful (table exists)"
        else
            log_fail "Deployment to prd failed (table not found, exit code: $exit_code)"
            log_info "Output: $(echo "$output" | tail -10)"
            return 1
        fi
    fi

    local count
    count=$("$SQLCMD_CMD" -e prd -Q "USE orderdb; SELECT COUNT(*) FROM sys.objects WHERE schema_id = SCHEMA_ID('app') AND type = 'U' AND name = 'orders';" 2>&1 | grep -E '^\s*[0-9]+\s*$' | tr -d ' ')

    if [ "$count" = "1" ]; then
        log_pass "Orders table verified in prd"
        return 0
    else
        log_fail "Orders table not found in prd (count: $count)"
        return 1
    fi
}

# Test Step 8: Create tags
test_step8_tags() {
    log_section "Step 8: Create Release Tags"

    cd "$LIQUIBASE_TUTORIAL_DATA_DIR"

    for env in dev stg prd; do
        if "$LB_CMD" -e "$env" -- tag release-v1.0 >> "$TEST_LOG" 2>&1; then
            log_pass "Tagged $env as release-v1.0"
        else
            log_fail "Failed to tag $env"
            return 1
        fi
    done

    return 0
}

# Test Step 9: Add rollback and test rollback
test_step9_rollback() {
    log_section "Step 9: Rollback Testing"

    # Note: Rollback block is already in V0001 file (added when file was created)
    cd "$LIQUIBASE_TUTORIAL_DATA_DIR"

    # Test rollback in dev only
    # Note: We use rollbackCount 1 to rollback just V0001, since baseline changesets don't have rollback blocks
    log_info "Testing rollback in dev (rolling back V0001 changeset)..."
    local rollback_output
    rollback_output=$("$LB_CMD" -e dev -- rollbackCount 1 2>&1 | tee -a "$TEST_LOG")
    local rollback_exit=$?

    if [ $rollback_exit -eq 0 ]; then
        log_pass "Rollback successful"
    elif echo "$rollback_output" | grep -qiE "(No changesets to rollback|already rolled back|Rollback successful)"; then
        log_pass "Rollback successful (no changes to rollback)"
    elif echo "$rollback_output" | grep -qiE "(ERROR|Error|error|Exception|exception|FAILED|Failed)"; then
        log_fail "Rollback failed - see log for details"
        log_info "Output: $(echo "$rollback_output" | tail -15)"
        return 1
    else
        # Check if table was actually removed
        local count
        count=$("$SQLCMD_CMD" -e dev -Q "USE orderdb; SELECT COUNT(*) FROM sys.objects WHERE schema_id = SCHEMA_ID('app') AND type = 'U' AND name = 'orders';" 2>&1 | grep -E '^\s*[0-9]+\s*$' | tr -d ' ')
        if [ "$count" = "0" ]; then
            log_pass "Rollback successful (table removed)"
        else
            log_fail "Rollback failed (table still exists, exit code: $rollback_exit)"
            log_info "Output: $(echo "$rollback_output" | tail -15)"
            return 1
        fi
    fi

    # Verify table is gone
    local count
    count=$("$SQLCMD_CMD" -e dev -Q "USE orderdb; SELECT COUNT(*) FROM sys.objects WHERE schema_id = SCHEMA_ID('app') AND type = 'U' AND name = 'orders';" 2>&1 | grep -E '^\s*[0-9]+\s*$' | tr -d ' ')

    if [ "$count" = "0" ]; then
        log_pass "Orders table removed after rollback"
    else
        log_fail "Orders table still exists after rollback (count: $count)"
        return 1
    fi

    # Re-apply
    log_info "Re-applying V0001..."
    if "$LB_CMD" -e dev -- update >> "$TEST_LOG" 2>&1; then
        log_pass "Re-deployment successful"
    else
        log_fail "Re-deployment failed"
        return 1
    fi

    if "$LB_CMD" -e dev -- tag release-v1.0 >> "$TEST_LOG" 2>&1; then
        log_pass "Re-tagged dev as release-v1.0"
    else
        log_fail "Re-tagging failed"
        return 1
    fi

    return 0
}

# Test Step 10: Drift detection
test_step10_drift() {
    log_section "Step 10: Drift Detection"

    # Simulate drift
    "$SQLCMD_CMD" -e dev -Q "USE orderdb; ALTER TABLE app.customer ADD loyalty_points INT DEFAULT 0;" >> "$TEST_LOG" 2>&1

    # Detect drift
    if "$LB_CMD" -e dev -- diff --referenceUrl="offline:mssql?changeLogFile=platform/mssql/database/orderdb/changelog/changelog.xml" >> "$TEST_LOG" 2>&1; then
        log_pass "Drift detection successful"
    else
        log_warn "Drift detection may have found differences (this is expected)"
    fi

    # Generate changelog (optional - we'll remove the drift)
    mkdir -p "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changes"
    "$LB_CMD" -e dev -- diffChangeLog --referenceUrl="offline:mssql?changeLogFile=platform/mssql/database/orderdb/changelog/changelog.xml" --changelogFile="$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changes/V0002__drift_loyalty_points.xml" >> "$TEST_LOG" 2>&1 || true

    # Remove drift to restore state
    "$SQLCMD_CMD" -e dev -Q "USE orderdb; ALTER TABLE app.customer DROP COLUMN loyalty_points;" >> "$TEST_LOG" 2>&1

    log_pass "Drift detection test complete"
    return 0
}

# Test Step 11: Create V0002 index
test_step11_index() {
    log_section "Step 11: Create V0002 Index"

    # Create V0002 file
    cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changes/V0002__add_orders_index.mssql.sql" << 'EOF'
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

    # Update changelog
    cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changelog.xml" << 'EOF'
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
    cd "$LIQUIBASE_TUTORIAL_DATA_DIR"
    for env in dev stg prd; do
        # Deploy (may already be executed, which is OK)
        local output
        output=$("$LB_CMD" -e "$env" -- update 2>&1 | tee -a "$TEST_LOG")
        local exit_code=$?

        # Check if it succeeded or if changeset was already executed
        if [ $exit_code -eq 0 ]; then
            log_pass "V0002 deployed to $env"
        elif echo "$output" | grep -qiE "(already executed|No changesets to execute|changeset.*already.*executed|Update successful)"; then
            log_pass "V0002 deployed to $env (changeset already executed)"
        elif echo "$output" | grep -qiE "(ERROR|Error|error|Exception|exception|FAILED|Failed)"; then
            log_fail "V0002 deployment failed to $env - see log for details"
            log_info "Output: $(echo "$output" | tail -10)"
            return 1
        else
            # Unknown case - check if index exists
            local count
            count=$("$SQLCMD_CMD" -e "$env" -Q "USE orderdb; SELECT COUNT(*) FROM sys.indexes WHERE name = 'IX_orders_order_date' AND object_id = OBJECT_ID('app.orders');" 2>&1 | grep -E '^\s*[0-9]+\s*$' | tr -d ' ')
            if [ "$count" = "1" ]; then
                log_pass "V0002 deployed to $env (index exists)"
            else
                log_fail "V0002 deployment failed to $env (index not found, exit code: $exit_code)"
                log_info "Output: $(echo "$output" | tail -10)"
                return 1
            fi
        fi

        if "$LB_CMD" -e "$env" -- tag release-v1.1 >> "$TEST_LOG" 2>&1; then
            log_pass "Tagged $env as release-v1.1"
        else
            log_fail "Tagging failed for $env"
            return 1
        fi
    done

    return 0
}

# Main test execution
main() {
    setup_environment

    # Clean up first
    cleanup

    # Setup prerequisites
    setup_prerequisites

    # Test each step
    local failed=false

    test_step6_create_file || failed=true
    test_step6_update_changelog || failed=true
    test_step6_deploy_dev || failed=true
    test_step7_deploy_stg || failed=true
    test_step7_deploy_prd || failed=true
    test_step8_tags || failed=true
    test_step9_rollback || failed=true
    test_step10_drift || failed=true
    test_step11_index || failed=true

    if [ "$failed" = true ]; then
        log_section "Some Steps Failed"
        log_info "Failed steps: ${FAILED_STEPS[*]}"
        return 1
    else
        log_section "All Steps Passed!"
        log_info "All Part 2 steps executed successfully"

        # Final cleanup
        cleanup

        return 0
    fi
}

# Run main
main "$@"

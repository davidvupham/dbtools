#!/bin/bash
# Full Tutorial Validation Script
# Executes all steps in Part 1 tutorial and captures output for review

set -e  # Exit on error
set -o pipefail  # Capture pipe failures

# Output file for all results
VALIDATION_LOG="${LIQUIBASE_TUTORIAL_DIR:-/tmp}/tutorial_validation_$(date +%Y%m%d_%H%M%S).log"
VALIDATION_REPORT="${LIQUIBASE_TUTORIAL_DIR:-/tmp}/tutorial_validation_report_$(date +%Y%m%d_%H%M%S).md"

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

    log_section "$step_name"
    log "Executing: $command"

    if eval "$command" >> "$VALIDATION_LOG" 2>&1; then
        log "✓ SUCCESS: $step_name"
        return 0
    else
        local exit_code=$?
        log "✗ FAILED: $step_name (exit code: $exit_code)"
        return $exit_code
    fi
}

# Initialize report
cat > "$VALIDATION_REPORT" << 'EOF'
# Tutorial Part 1 Validation Report

**Date:** $(date)
**Environment:** Ubuntu Linux
**Tutorial:** Part 1: Baseline SQL Server + Liquibase Setup

## Executive Summary

This report documents the validation of all steps in the Part 1 tutorial, including:
- Step execution results
- Issues found and fixes applied
- Grammar and spelling corrections
- Clarity and instruction improvements

---

## Validation Results

EOF

log "Starting full tutorial validation"
log "Log file: $VALIDATION_LOG"
log "Report file: $VALIDATION_REPORT"

# Track issues
ISSUES_FOUND=0
FIXES_APPLIED=0

# ============================================================================
# PRE-VALIDATION: Clean up any existing containers/resources
# ============================================================================
log_section "Pre-Validation: Cleanup Previous Runs"

CLEANUP_SCRIPT="${LIQUIBASE_TUTORIAL_DIR}/scripts/cleanup_validation.sh"
if [ -f "$CLEANUP_SCRIPT" ]; then
    log "Running cleanup script to ensure clean environment..."
    # Run cleanup non-interactively (skip log file removal prompt)
    export MSSQL_LIQUIBASE_TUTORIAL_PWD="${MSSQL_LIQUIBASE_TUTORIAL_PWD:-TestPassword123!}"
    echo "n" | bash "$CLEANUP_SCRIPT" >> "$VALIDATION_LOG" 2>&1 || log "Warning: Cleanup script had issues (may be normal if nothing to clean)"
    log "✓ Cleanup complete"
else
    log "⚠ Cleanup script not found, attempting manual cleanup..."
    # Manual cleanup fallback
    cd "${LIQUIBASE_TUTORIAL_DIR}/docker" 2>/dev/null || true
    export MSSQL_LIQUIBASE_TUTORIAL_PWD="${MSSQL_LIQUIBASE_TUTORIAL_PWD:-TestPassword123!}"
    docker compose down -v >> "$VALIDATION_LOG" 2>&1 || true
    docker ps -a --filter "name=mssql_" --format "{{.Names}}" | xargs -r docker rm -f >> "$VALIDATION_LOG" 2>&1 || true
    log "✓ Manual cleanup complete"
fi

# Wait a moment for ports to be released
sleep 2

# Step 0: Environment Setup
log_section "Step 0: Configure Environment and Aliases"

if [ -z "$LIQUIBASE_TUTORIAL_DIR" ]; then
    log "Setting LIQUIBASE_TUTORIAL_DIR"
    export LIQUIBASE_TUTORIAL_DIR="/home/dpham/src/dbtools/docs/courses/liquibase"
fi

log "LIQUIBASE_TUTORIAL_DIR=$LIQUIBASE_TUTORIAL_DIR"

# Check if setup scripts exist
if [ ! -f "$LIQUIBASE_TUTORIAL_DIR/scripts/setup_user_directory.sh" ]; then
    log "✗ ERROR: setup_user_directory.sh not found"
    ((ISSUES_FOUND++))
else
    log "✓ setup_user_directory.sh exists"
fi

if [ ! -f "$LIQUIBASE_TUTORIAL_DIR/scripts/setup_tutorial.sh" ]; then
    log "✗ ERROR: setup_tutorial.sh not found"
    ((ISSUES_FOUND++))
else
    log "✓ setup_tutorial.sh exists"
fi

# Source setup script (non-interactive mode)
if [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/setup_tutorial.sh" ]; then
    log "Sourcing setup_tutorial.sh"
    # Set password for non-interactive execution
    export MSSQL_LIQUIBASE_TUTORIAL_PWD="${MSSQL_LIQUIBASE_TUTORIAL_PWD:-TestPassword123!}"
    source "$LIQUIBASE_TUTORIAL_DIR/scripts/setup_tutorial.sh" >> "$VALIDATION_LOG" 2>&1 || log "Warning: setup_tutorial.sh had issues"
fi

# Step 1: Start Containers
log_section "Step 1: Start SQL Server Containers"

if [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/start_mssql_containers.sh" ]; then
    execute_step "Start Containers" "$LIQUIBASE_TUTORIAL_DIR/scripts/start_mssql_containers.sh"
    CONTAINER_START_RESULT=$?
else
    log "✗ ERROR: start_mssql_containers.sh not found"
    ((ISSUES_FOUND++))
    CONTAINER_START_RESULT=1
fi

# Wait for containers to be healthy
if [ $CONTAINER_START_RESULT -eq 0 ]; then
    log "Waiting for containers to be healthy..."
    sleep 10
    docker ps | grep mssql_ >> "$VALIDATION_LOG" 2>&1 || true
fi

# Step 2: Build Liquibase Image
log_section "Step 2: Build Liquibase Container Image"

LIQUIBASE_DOCKER_DIR="${LIQUIBASE_TUTORIAL_DIR%/docs/courses/liquibase}/docker/liquibase"
if [ -d "$LIQUIBASE_DOCKER_DIR" ]; then
    log "Building Liquibase image from $LIQUIBASE_DOCKER_DIR"
    cd "$LIQUIBASE_DOCKER_DIR"
    execute_step "Build Liquibase Image" "docker build -t liquibase:latest ."
else
    log "✗ ERROR: Liquibase docker directory not found: $LIQUIBASE_DOCKER_DIR"
    ((ISSUES_FOUND++))
fi

# Step 3: Create Project Structure
log_section "Step 3: Create Project Structure"

if [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/setup_liquibase_environment.sh" ]; then
    execute_step "Setup Environment" "$LIQUIBASE_TUTORIAL_DIR/scripts/setup_liquibase_environment.sh"
else
    log "✗ ERROR: setup_liquibase_environment.sh not found"
    ((ISSUES_FOUND++))
fi

# Step 4: Create Databases
log_section "Step 4: Create Three Database Environments"

if [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/create_orderdb_database.sh" ]; then
    execute_step "Create Databases" "$LIQUIBASE_TUTORIAL_DIR/scripts/create_orderdb_database.sh"
    CREATE_DB_RESULT=$?

    if [ $CREATE_DB_RESULT -eq 0 ] && [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/validate_orderdb_database.sh" ]; then
        execute_step "Validate Databases" "$LIQUIBASE_TUTORIAL_DIR/scripts/validate_orderdb_database.sh"
    fi
else
    log "✗ ERROR: create_orderdb_database.sh not found"
    ((ISSUES_FOUND++))
fi

# Step 5: Populate Development
log_section "Step 5: Populate Development with Existing Objects"

if [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/populate_dev_database.sh" ]; then
    execute_step "Populate Dev" "$LIQUIBASE_TUTORIAL_DIR/scripts/populate_dev_database.sh"
    POPULATE_RESULT=$?

    if [ $POPULATE_RESULT -eq 0 ] && [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/validate_dev_populate.sh" ]; then
        execute_step "Validate Populate" "$LIQUIBASE_TUTORIAL_DIR/scripts/validate_dev_populate.sh"
    fi
else
    log "✗ ERROR: populate_dev_database.sh not found"
    ((ISSUES_FOUND++))
fi

# Step 6: Generate Baseline
log_section "Step 6: Generate Baseline from Development"

if [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/generate_liquibase_baseline.sh" ]; then
    execute_step "Generate Baseline" "$LIQUIBASE_TUTORIAL_DIR/scripts/generate_liquibase_baseline.sh"
    BASELINE_RESULT=$?

    if [ $BASELINE_RESULT -eq 0 ] && [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/validate_liquibase_baseline.sh" ]; then
        execute_step "Validate Baseline" "$LIQUIBASE_TUTORIAL_DIR/scripts/validate_liquibase_baseline.sh"
    fi
else
    log "✗ ERROR: generate_liquibase_baseline.sh not found"
    ((ISSUES_FOUND++))
fi

# Step 7: Deploy Baseline
log_section "Step 7: Deploy Baseline Across Environments"

if [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/deploy_liquibase_baseline.sh" ]; then
    execute_step "Deploy Baseline" "$LIQUIBASE_TUTORIAL_DIR/scripts/deploy_liquibase_baseline.sh"
    DEPLOY_RESULT=$?

    if [ $DEPLOY_RESULT -eq 0 ] && [ -f "$LIQUIBASE_TUTORIAL_DIR/scripts/validate_liquibase_deploy.sh" ]; then
        execute_step "Validate Deployment" "$LIQUIBASE_TUTORIAL_DIR/scripts/validate_liquibase_deploy.sh --db mssql_dev,mssql_stg,mssql_prd"
    fi
else
    log "✗ ERROR: deploy_liquibase_baseline.sh not found"
    ((ISSUES_FOUND++))
fi

# Final Summary
log_section "Validation Summary"

log "Total issues found: $ISSUES_FOUND"
log "Total fixes applied: $FIXES_APPLIED"
log ""
log "Validation complete. Review log file: $VALIDATION_LOG"
log "Review report file: $VALIDATION_REPORT"

# ============================================================================
# POST-VALIDATION: Clean up containers and resources
# ============================================================================
log_section "Post-Validation: Cleanup"

log "Cleaning up containers and resources after validation..."

CLEANUP_SCRIPT="${LIQUIBASE_TUTORIAL_DIR}/scripts/cleanup_validation.sh"
if [ -f "$CLEANUP_SCRIPT" ]; then
    log "Running cleanup script..."
    export MSSQL_LIQUIBASE_TUTORIAL_PWD="${MSSQL_LIQUIBASE_TUTORIAL_PWD:-TestPassword123!}"
    # Run cleanup non-interactively (skip log file removal prompt)
    echo "n" | bash "$CLEANUP_SCRIPT" >> "$VALIDATION_LOG" 2>&1 || log "Warning: Cleanup script had issues"
    log "✓ Cleanup complete"
else
    log "⚠ Cleanup script not found, attempting manual cleanup..."
    # Manual cleanup fallback
    cd "${LIQUIBASE_TUTORIAL_DIR}/docker" 2>/dev/null || true
    export MSSQL_LIQUIBASE_TUTORIAL_PWD="${MSSQL_LIQUIBASE_TUTORIAL_PWD:-TestPassword123!}"
    docker compose down -v >> "$VALIDATION_LOG" 2>&1 || true
    docker ps -a --filter "name=mssql_" --format "{{.Names}}" | xargs -r docker rm -f >> "$VALIDATION_LOG" 2>&1 || true
    log "✓ Manual cleanup complete"
fi

log ""
log "========================================"
log "Validation and cleanup complete!"
log "========================================"

# Append summary to report
cat >> "$VALIDATION_REPORT" << EOF

## Summary

- **Total Issues Found:** $ISSUES_FOUND
- **Total Fixes Applied:** $FIXES_APPLIED
- **Validation Log:** $VALIDATION_LOG

---

## Detailed Results

See the validation log file for detailed execution output: \`$VALIDATION_LOG\`

EOF

echo ""
echo "========================================"
echo "Validation Complete!"
echo "========================================"
echo "Log: $VALIDATION_LOG"
echo "Report: $VALIDATION_REPORT"
echo ""
echo "Containers and resources have been cleaned up."
echo "You can review the log and report files above."

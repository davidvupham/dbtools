#!/usr/bin/env bash
################################################################################
# test_part2_manual.sh - Complete End-to-End Test for Tutorial Part 2
################################################################################
#
# PURPOSE:
#   This script provides a complete, automated test of all steps in the
#   Tutorial Part 2: Manual Liquibase Deployment Lifecycle. It can either
#   run Part 1 first or use an existing Part 1 environment.
#
# WHAT IT TESTS:
#   - Validate Part 1 Completion
#   - Step 6: Making your first change (create orders table)
#   - Step 7: Promoting changes to staging and production
#   - Step 8: Tags and release management
#   - Step 9: Rollback strategies
#   - Step 10: Drift detection
#   - Step 11: Additional changesets (V0002 index)
#   - Cleanup after testing
#
# USAGE:
#   ./test_part2_manual.sh [options]
#
# OPTIONS:
#   -o, --output <dir>    Output directory for test results (default: /tmp)
#   -k, --keep-env        Keep containers running after test (skip cleanup)
#   -p, --password <pwd>  Use specific password instead of random
#   -v, --verbose         Show verbose output (don't suppress command output)
#   --skip-part1          Skip Part 1 setup (assume Part 1 already complete)
#   -h, --help            Show this help message
#
# OUTPUT:
#   Test results are written to: <output_dir>/liquibase_part2_test_YYYYMMDD_HHMMSS.log
#
# EXIT CODES:
#   0 - All tests passed
#   1 - One or more tests failed
#   2 - Invalid arguments
#
################################################################################

set -euo pipefail

# Script directory and tutorial root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TUTORIAL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

################################################################################
# Configuration
################################################################################

OUTPUT_DIR="/tmp"
KEEP_ENV=false
CUSTOM_PASSWORD=""
VERBOSE=false
SKIP_PART1=false
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TEST_START_TIME=$(date '+%Y-%m-%d %H:%M:%S')

################################################################################
# Helper Functions
################################################################################

print_help() {
    sed -n '/^# PURPOSE:/,/^# EXIT CODES:/p' "$0" | sed 's/^# //' | sed 's/^#$//'
    echo "  0 - All tests passed"
    echo "  1 - One or more tests failed"
    echo "  2 - Invalid arguments"
}

# Generate a random password that meets SQL Server complexity requirements
generate_random_password() {
    local length=${1:-16}
    local upper=$(tr -dc 'A-Z' < /dev/urandom | head -c 3)
    local lower=$(tr -dc 'a-z' < /dev/urandom | head -c 3)
    local digit=$(tr -dc '0-9' < /dev/urandom | head -c 3)
    local special=$(tr -dc '@#$%&*_=' < /dev/urandom | head -c 2)
    local filler=$(tr -dc 'A-Za-z0-9' < /dev/urandom | head -c $((length - 11)))
    local password="${upper}${lower}${digit}${special}${filler}"
    password=$(echo "$password" | fold -w1 | shuf | tr -d '\n')
    echo "$password"
}

# Log function that writes to both terminal and log file
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"

    case "$level" in
        INFO) echo -e "${BLUE}[$timestamp]${NC} ${CYAN}[INFO]${NC} $message" ;;
        PASS) echo -e "${BLUE}[$timestamp]${NC} ${GREEN}[PASS]${NC} $message" ;;
        FAIL) echo -e "${BLUE}[$timestamp]${NC} ${RED}[FAIL]${NC} $message" ;;
        WARN) echo -e "${BLUE}[$timestamp]${NC} ${YELLOW}[WARN]${NC} $message" ;;
        STEP) echo -e "${BLUE}[$timestamp]${NC} ${CYAN}[STEP]${NC} $message" ;;
        *) echo -e "${BLUE}[$timestamp]${NC} $message" ;;
    esac
}

log_section() {
    local section="$1"
    echo "" >> "$LOG_FILE"
    echo "================================================================================" >> "$LOG_FILE"
    echo "SECTION: $section" >> "$LOG_FILE"
    echo "================================================================================" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"

    echo ""
    echo -e "${CYAN}================================================================================${NC}"
    echo -e "${CYAN}SECTION: $section${NC}"
    echo -e "${CYAN}================================================================================${NC}"
    echo ""
}

abort_test() {
    local failed_step="$1"

    log "FAIL" "Aborting test due to failure in: $failed_step"
    log "INFO" "Later steps depend on this step - cannot continue"

    if [[ "$KEEP_ENV" == "false" ]]; then
        echo "" >> "$LOG_FILE"
        log "INFO" "Cleaning up after failure..."

        for container in mssql_dev mssql_stg mssql_prd liquibase_tutorial; do
            if $CR_CMD ps -a --format "{{.Names}}" 2>/dev/null | grep -q "^${container}$"; then
                $CR_CMD rm -f "$container" >> "$LOG_FILE" 2>&1 || true
            fi
        done

        $CR_CMD network rm liquibase_tutorial_network >> "$LOG_FILE" 2>&1 || true

        if [[ -d "$LIQUIBASE_TUTORIAL_DATA_DIR" ]]; then
            rm -rf "$LIQUIBASE_TUTORIAL_DATA_DIR" 2>/dev/null || sudo rm -rf "$LIQUIBASE_TUTORIAL_DATA_DIR" 2>/dev/null || true
            log "INFO" "Removed test data directory"
        fi

        log "INFO" "Cleanup complete"
    else
        log "INFO" "Keeping test environment for debugging (--keep-env specified)"
        log "INFO" "Data directory: $LIQUIBASE_TUTORIAL_DATA_DIR"
    fi

    print_test_summary
    exit 1
}

print_test_summary() {
    local summary_end_time=$(date '+%Y-%m-%d %H:%M:%S')
    local total_tests=$((TESTS_PASSED + TESTS_FAILED))

    cat >> "$LOG_FILE" << SUMMARY_EOF

================================================================================
TEST SUMMARY
================================================================================

Test Started:     $TEST_START_TIME
Test Completed:   $summary_end_time

Results:
  Total Tests:    $total_tests
  Passed:         $TESTS_PASSED
  Failed:         $TESTS_FAILED

SUMMARY_EOF

    if [[ ${#FAILED_TESTS[@]} -gt 0 ]]; then
        echo "Failed Tests:" >> "$LOG_FILE"
        for failed_test in "${FAILED_TESTS[@]}"; do
            echo "  - $failed_test" >> "$LOG_FILE"
        done
    fi

    cat >> "$LOG_FILE" << SUMMARY_EOF

================================================================================
END OF TEST REPORT
================================================================================
SUMMARY_EOF

    echo ""
    echo -e "${CYAN}================================================================================${NC}"
    echo -e "${CYAN}TEST SUMMARY${NC}"
    echo -e "${CYAN}================================================================================${NC}"
    echo ""
    echo -e "Test Started:     ${BLUE}$TEST_START_TIME${NC}"
    echo -e "Test Completed:   ${BLUE}$summary_end_time${NC}"
    echo ""
    echo -e "Results:"
    echo -e "  Total Tests:    ${BLUE}$total_tests${NC}"
    echo -e "  Passed:         ${GREEN}$TESTS_PASSED${NC}"
    echo -e "  Failed:         ${RED}$TESTS_FAILED${NC}"
    echo ""

    if [[ ${#FAILED_TESTS[@]} -gt 0 ]]; then
        echo -e "${RED}Failed Tests:${NC}"
        for failed_test in "${FAILED_TESTS[@]}"; do
            echo -e "  ${RED}- $failed_test${NC}"
        done
        echo ""
    fi

    echo -e "Test Results:     ${CYAN}$LOG_FILE${NC}"
    echo ""

    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}================================================================================${NC}"
        echo -e "${GREEN}ALL TESTS PASSED${NC}"
        echo -e "${GREEN}================================================================================${NC}"
    else
        echo -e "${RED}================================================================================${NC}"
        echo -e "${RED}TEST FAILED - SEE LOG FOR DETAILS${NC}"
        echo -e "${RED}================================================================================${NC}"
    fi
}

run_test() {
    local test_name="$1"
    local command="$2"
    local start_time=$(date +%s)

    log "STEP" "Running: $test_name"
    echo "Command: $command" >> "$LOG_FILE"

    local output_file=$(mktemp)
    local exit_code=0

    if [[ "$VERBOSE" == "true" ]]; then
        if eval "$command" 2>&1 | tee -a "$output_file"; then
            exit_code=0
        else
            exit_code=$?
        fi
    else
        if eval "$command" >> "$output_file" 2>&1; then
            exit_code=0
        else
            exit_code=$?
        fi
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo "--- BEGIN OUTPUT: $test_name ---" >> "$LOG_FILE"
    cat "$output_file" >> "$LOG_FILE"
    echo "--- END OUTPUT: $test_name (exit code: $exit_code, duration: ${duration}s) ---" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"

    if [[ $exit_code -eq 0 ]]; then
        log "PASS" "$test_name (${duration}s)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        rm -f "$output_file"
        return 0
    else
        log "FAIL" "$test_name (exit code: $exit_code, ${duration}s)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        FAILED_TESTS+=("$test_name")

        echo -e "${RED}--- Failure output (last 30 lines) ---${NC}"
        tail -30 "$output_file"
        echo -e "${RED}--- End of failure output ---${NC}"
        echo ""

        rm -f "$output_file"
        abort_test "$test_name"
    fi
}

run_check() {
    local check_name="$1"
    local condition="$2"

    echo "--- CHECK: $check_name ---" >> "$LOG_FILE"
    echo "Condition: $condition" >> "$LOG_FILE"

    local output
    output=$(eval "$condition" 2>&1) && local result=0 || local result=$?

    if [[ $result -eq 0 ]]; then
        echo "Result: PASS" >> "$LOG_FILE"
        [[ -n "$output" ]] && echo "Output: $output" >> "$LOG_FILE"
        echo "" >> "$LOG_FILE"
        log "PASS" "$check_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo "Result: FAIL (exit code: $result)" >> "$LOG_FILE"
        [[ -n "$output" ]] && echo "Output: $output" >> "$LOG_FILE"
        echo "" >> "$LOG_FILE"
        log "FAIL" "$check_name"

        echo -e "${RED}--- Check failed: $check_name ---${NC}"
        echo -e "${RED}Condition: $condition${NC}"
        [[ -n "$output" ]] && echo -e "${RED}Output: $output${NC}"
        echo ""

        TESTS_FAILED=$((TESTS_FAILED + 1))
        FAILED_TESTS+=("$check_name")
        abort_test "$check_name"
    fi
}

detect_container_runtime() {
    if command -v podman &>/dev/null; then
        echo "podman"
    elif command -v docker &>/dev/null; then
        echo "docker"
    else
        echo ""
    fi
}

################################################################################
# Argument Parsing
################################################################################

while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -k|--keep-env)
            KEEP_ENV=true
            shift
            ;;
        -p|--password)
            CUSTOM_PASSWORD="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --skip-part1)
            SKIP_PART1=true
            shift
            ;;
        -h|--help)
            print_help
            exit 0
            ;;
        *)
            echo -e "${RED}ERROR: Unknown option: $1${NC}" >&2
            print_help
            exit 2
            ;;
    esac
done

################################################################################
# Initialization
################################################################################

mkdir -p "$OUTPUT_DIR"
LOG_FILE="${OUTPUT_DIR}/liquibase_part2_test_${TIMESTAMP}.log"

TESTS_PASSED=0
TESTS_FAILED=0
declare -a FAILED_TESTS=()

CR_CMD=$(detect_container_runtime)
if [[ -z "$CR_CMD" ]]; then
    echo -e "${RED}ERROR: No container runtime found (docker or podman required)${NC}" >&2
    exit 1
fi

if [[ -n "$CUSTOM_PASSWORD" ]]; then
    TEST_PASSWORD="$CUSTOM_PASSWORD"
else
    TEST_PASSWORD=$(generate_random_password 16)
fi

export LIQUIBASE_TUTORIAL_DIR="$TUTORIAL_ROOT"
export LIQUIBASE_TUTORIAL_DATA_DIR="/data/${USER}/liquibase_tutorial_test_${TIMESTAMP}"
export MSSQL_LIQUIBASE_TUTORIAL_PWD="$TEST_PASSWORD"

################################################################################
# Write Test Header
################################################################################

cat > "$LOG_FILE" << EOF
================================================================================
LIQUIBASE TUTORIAL PART 2 - AUTOMATED TEST REPORT
================================================================================

Test Started:     $TEST_START_TIME
Test Timestamp:   $TIMESTAMP
Container Runtime: $CR_CMD
Output File:      $LOG_FILE

Environment:
  LIQUIBASE_TUTORIAL_DIR:      $LIQUIBASE_TUTORIAL_DIR
  LIQUIBASE_TUTORIAL_DATA_DIR: $LIQUIBASE_TUTORIAL_DATA_DIR
  Password Length:             ${#TEST_PASSWORD} characters

Test Options:
  Keep Environment: $KEEP_ENV
  Verbose Mode:     $VERBOSE
  Skip Part 1:      $SKIP_PART1
  Custom Password:  $([[ -n "$CUSTOM_PASSWORD" ]] && echo "Yes" || echo "No (randomly generated)")

================================================================================
TEST EXECUTION LOG
================================================================================

EOF

echo ""
echo -e "${GREEN}================================================================================${NC}"
echo -e "${GREEN}LIQUIBASE TUTORIAL PART 2 - AUTOMATED TEST${NC}"
echo -e "${GREEN}================================================================================${NC}"
echo ""
echo -e "Test Started:     ${CYAN}$TEST_START_TIME${NC}"
echo -e "Container Runtime: ${CYAN}$CR_CMD${NC}"
echo -e "Output File:      ${CYAN}$LOG_FILE${NC}"
echo -e "Data Directory:   ${CYAN}$LIQUIBASE_TUTORIAL_DATA_DIR${NC}"
echo -e "Skip Part 1:      ${CYAN}$SKIP_PART1${NC}"
echo ""

################################################################################
# PART 1 SETUP (unless --skip-part1)
################################################################################

if [[ "$SKIP_PART1" == "false" ]]; then
    log_section "Part 1 Setup"

    log "INFO" "Running Part 1 test to set up environment..."

    # Run Part 1 test with --keep-env to preserve the environment for Part 2
    run_test "Run Part 1 test" "\"$SCRIPT_DIR/test_part1_baseline.sh\" --keep-env -p \"$TEST_PASSWORD\" -o \"$OUTPUT_DIR\""

    # Source the port configuration from Part 1
    PORTS_FILE="$LIQUIBASE_TUTORIAL_DATA_DIR/.ports"
    if [[ -f "$PORTS_FILE" ]]; then
        source "$PORTS_FILE"
        log "INFO" "Using ports from Part 1: DEV=$MSSQL_DEV_PORT, STG=$MSSQL_STG_PORT, PRD=$MSSQL_PRD_PORT"
    fi
else
    log_section "Skip Part 1 - Validate Existing Environment"

    # When skipping Part 1, we need to find an existing environment
    # Check for environment variables or use defaults
    if [[ -z "${LIQUIBASE_TUTORIAL_DATA_DIR:-}" ]]; then
        export LIQUIBASE_TUTORIAL_DATA_DIR="/data/${USER}/liquibase_tutorial"
    fi

    if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
        echo -e "${RED}ERROR: MSSQL_LIQUIBASE_TUTORIAL_PWD must be set when using --skip-part1${NC}" >&2
        exit 1
    fi

    # Source port configuration if it exists
    PORTS_FILE="$LIQUIBASE_TUTORIAL_DATA_DIR/.ports"
    if [[ -f "$PORTS_FILE" ]]; then
        source "$PORTS_FILE"
        log "INFO" "Using ports: DEV=$MSSQL_DEV_PORT, STG=$MSSQL_STG_PORT, PRD=$MSSQL_PRD_PORT"
    else
        export MSSQL_DEV_PORT=${MSSQL_DEV_PORT:-14331}
        export MSSQL_STG_PORT=${MSSQL_STG_PORT:-14332}
        export MSSQL_PRD_PORT=${MSSQL_PRD_PORT:-14333}
        log "INFO" "Using default ports: DEV=$MSSQL_DEV_PORT, STG=$MSSQL_STG_PORT, PRD=$MSSQL_PRD_PORT"
    fi
fi

################################################################################
# Validate Part 1 Completion
################################################################################

log_section "Validate Part 1 Completion"

run_test "Validate Part 1 baseline deployment" \
    "\"$SCRIPT_DIR/validate_liquibase_deploy.sh\" --dbi mssql_dev,mssql_stg,mssql_prd"

################################################################################
# Step 6: Making Your First Change
################################################################################

log_section "Step 6: Making Your First Change"

# Create the orders table changelog
run_test "Create orders table changelog" "\"$SCRIPT_DIR/create_orders_table_changelog.sh\""

# Deploy to development
run_test "Deploy V0001 to development" \
    "\"$SCRIPT_DIR/deploy.sh\" --action update --dbi mssql_dev"

# Validate development deployment
run_test "Validate development deployment" \
    "\"$SCRIPT_DIR/validate_app_schema_objects.sh\" --dbi mssql_dev"

################################################################################
# Step 7: Promoting Changes to Staging and Production
################################################################################

log_section "Step 7: Promoting Changes to Staging and Production"

# Deploy to staging
run_test "Deploy V0001 to staging" \
    "\"$SCRIPT_DIR/deploy.sh\" --action update --dbi mssql_stg"

run_test "Validate staging deployment" \
    "\"$SCRIPT_DIR/validate_app_schema_objects.sh\" --dbi mssql_stg"

# Deploy to production
run_test "Deploy V0001 to production" \
    "\"$SCRIPT_DIR/deploy.sh\" --action update --dbi mssql_prd"

run_test "Validate production deployment" \
    "\"$SCRIPT_DIR/validate_app_schema_objects.sh\" --dbi mssql_prd"

################################################################################
# Step 8: Tags and Release Management
################################################################################

log_section "Step 8: Tags and Release Management"

# Create release tags
run_test "Tag development as release-v1.1" \
    "\"$SCRIPT_DIR/lb.sh\" --dbi mssql_dev -- tag release-v1.1"

run_test "Tag staging as release-v1.1" \
    "\"$SCRIPT_DIR/lb.sh\" --dbi mssql_stg -- tag release-v1.1"

run_test "Tag production as release-v1.1" \
    "\"$SCRIPT_DIR/lb.sh\" --dbi mssql_prd -- tag release-v1.1"

# Query DATABASECHANGELOG
run_test "Query DATABASECHANGELOG on development" \
    "\"$SCRIPT_DIR/query_databasechangelog.sh\" --dbi mssql_dev"

################################################################################
# Step 9: Rollback Strategies
################################################################################

log_section "Step 9: Rollback Strategies"

# Add rollback to V0001
run_test "Add rollback block to V0001" \
    "\"$SCRIPT_DIR/add_rollback_to_orders_table.sh\""

# Practice rollback in development
run_test "Rollback to baseline in development" \
    "\"$SCRIPT_DIR/deploy.sh\" --action rollback --dbi mssql_dev --tag baseline"

# Verify rollback
run_test "Query DATABASECHANGELOG after rollback" \
    "\"$SCRIPT_DIR/query_databasechangelog.sh\" --dbi mssql_dev"

# Re-apply after rollback
run_test "Re-deploy V0001 to development" \
    "\"$SCRIPT_DIR/deploy.sh\" --action update --dbi mssql_dev"

# Re-tag the release
run_test "Re-tag development as release-v1.1" \
    "\"$SCRIPT_DIR/lb.sh\" --dbi mssql_dev -- tag release-v1.1"

# Verify re-application
run_test "Query DATABASECHANGELOG after re-deploy" \
    "\"$SCRIPT_DIR/query_databasechangelog.sh\" --dbi mssql_dev"

################################################################################
# Step 10: Drift Detection
################################################################################

log_section "Step 10: Drift Detection"

# Take a fresh snapshot before simulating drift
run_test "Take pre-drift snapshot" \
    "\"$SCRIPT_DIR/lb.sh\" --dbi mssql_dev -- snapshot --schemas=app --snapshot-format=json --output-file=\"$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/snapshots/mssql_dev_pre_drift_${TIMESTAMP}.json\""

# Simulate drift: Type 1 - Unexpected (new column)
log "INFO" "Simulating drift: adding loyalty_points column..."
run_test "Simulate drift: add loyalty_points column" \
    "$CR_CMD exec mssql_dev /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P \"\$MSSQL_LIQUIBASE_TUTORIAL_PWD\" -d orderdb -Q \"IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('app.customer') AND name = 'loyalty_points') ALTER TABLE app.customer ADD loyalty_points INT DEFAULT 0;\""

# Verify drift column was added
run_test "Verify loyalty_points column added" \
    "\"$SCRIPT_DIR/query_table_columns.sh\" -e dev -h loyalty_points app.customer"

# Simulate drift: Type 2 - Changed (modified column)
run_test "Simulate drift: modify first_name column size" \
    "$CR_CMD exec mssql_dev /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P \"\$MSSQL_LIQUIBASE_TUTORIAL_PWD\" -d orderdb -Q \"ALTER TABLE app.customer ALTER COLUMN first_name NVARCHAR(150);\""

# Simulate drift: Type 3 - Missing (drop index)
run_test "Simulate drift: drop IX_orders_order_date index" \
    "$CR_CMD exec mssql_dev /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P \"\$MSSQL_LIQUIBASE_TUTORIAL_PWD\" -d orderdb -Q \"IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_orders_order_date' AND object_id = OBJECT_ID('app.orders')) DROP INDEX IX_orders_order_date ON app.orders;\""

# Detect drift
run_test "Detect drift" \
    "\"$SCRIPT_DIR/detect_drift.sh\" --dbi mssql_dev"

# Generate changelog from drift (but we won't use it)
run_test "Generate drift changelog" \
    "\"$SCRIPT_DIR/generate_drift_changelog.sh\" --dbi mssql_dev -o platform/mssql/database/orderdb/changelog/changes/V0002__captured_drift.xml"

# Revert the simulated drift
run_test "Revert drift" \
    "\"$SCRIPT_DIR/revert_drift.sh\" --dbi mssql_dev"

# Verify drift is resolved
run_test "Verify no drift after revert" \
    "\"$SCRIPT_DIR/detect_drift.sh\" --dbi mssql_dev"

################################################################################
# Step 11: Additional Changesets
################################################################################

log_section "Step 11: Additional Changesets"

# Create V0002 index changelog
run_test "Create orders index changelog (V0002)" \
    "\"$SCRIPT_DIR/create_orders_index_changelog.sh\""

# Deploy to development
run_test "Deploy V0002 to development" \
    "\"$SCRIPT_DIR/deploy.sh\" --action update --dbi mssql_dev"

run_test "Tag development as release-v1.2" \
    "\"$SCRIPT_DIR/lb.sh\" --dbi mssql_dev -- tag release-v1.2"

# Validate development
run_test "Validate development after V0002" \
    "\"$SCRIPT_DIR/validate_app_schema_objects.sh\" --dbi mssql_dev"

run_test "Query DATABASECHANGELOG on development" \
    "\"$SCRIPT_DIR/query_databasechangelog.sh\" --dbi mssql_dev"

# Deploy to staging
run_test "Deploy V0002 to staging" \
    "\"$SCRIPT_DIR/deploy.sh\" --action update --dbi mssql_stg"

run_test "Tag staging as release-v1.2" \
    "\"$SCRIPT_DIR/lb.sh\" --dbi mssql_stg -- tag release-v1.2"

# Deploy to production
run_test "Deploy V0002 to production" \
    "\"$SCRIPT_DIR/deploy.sh\" --action update --dbi mssql_prd"

run_test "Tag production as release-v1.2" \
    "\"$SCRIPT_DIR/lb.sh\" --dbi mssql_prd -- tag release-v1.2"

# Final validation across all environments
run_test "Validate all environments after V0002" \
    "\"$SCRIPT_DIR/validate_app_schema_objects.sh\" --dbi mssql_dev,mssql_stg,mssql_prd"

run_test "Query DATABASECHANGELOG on all environments" \
    "\"$SCRIPT_DIR/query_databasechangelog.sh\" --dbi mssql_dev,mssql_stg,mssql_prd"

################################################################################
# CLEANUP (unless --keep-env specified)
################################################################################

if [[ "$KEEP_ENV" == "false" ]]; then
    log_section "Post-Test Cleanup"

    log "INFO" "Cleaning up test environment..."

    for container in mssql_dev mssql_stg mssql_prd liquibase_tutorial; do
        if $CR_CMD ps -a --format "{{.Names}}" 2>/dev/null | grep -q "^${container}$"; then
            $CR_CMD rm -f "$container" >> "$LOG_FILE" 2>&1 || true
            log "INFO" "Removed container: $container"
        fi
    done

    if $CR_CMD network ls --format "{{.Name}}" 2>/dev/null | grep -q "^liquibase_tutorial_network$"; then
        $CR_CMD network rm liquibase_tutorial_network >> "$LOG_FILE" 2>&1 || true
        log "INFO" "Removed network: liquibase_tutorial_network"
    fi

    if [[ -d "$LIQUIBASE_TUTORIAL_DATA_DIR" ]]; then
        rm -rf "$LIQUIBASE_TUTORIAL_DATA_DIR" 2>/dev/null || sudo rm -rf "$LIQUIBASE_TUTORIAL_DATA_DIR"
        log "INFO" "Removed test data directory: $LIQUIBASE_TUTORIAL_DATA_DIR"
    fi

    log "INFO" "Cleanup complete"
else
    log "INFO" "Keeping test environment (--keep-env specified)"
    log "INFO" "Data directory: $LIQUIBASE_TUTORIAL_DATA_DIR"
    log "INFO" "To clean up manually, run:"
    log "INFO" "  $CR_CMD rm -f mssql_dev mssql_stg mssql_prd"
    log "INFO" "  rm -rf $LIQUIBASE_TUTORIAL_DATA_DIR"
fi

################################################################################
# TEST SUMMARY
################################################################################

print_test_summary
exit 0

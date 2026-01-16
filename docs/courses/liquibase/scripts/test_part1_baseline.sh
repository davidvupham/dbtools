#!/usr/bin/env bash
################################################################################
# test_part1_baseline.sh - Complete End-to-End Test for Tutorial Part 1
################################################################################
#
# PURPOSE:
#   This script provides a complete, automated test of all steps in the
#   Tutorial Part 1: Baseline SQL Server + Liquibase Setup. It generates
#   a random SQL Server password for testing and writes all results to
#   a timestamped output file.
#
# WHAT IT TESTS:
#   - Step 0: Environment setup and configuration
#   - Container startup (SQL Server instances)
#   - Liquibase container image build
#   - Step 1: Create three database environments
#   - Step 2: Populate development with existing objects
#   - Step 3: Configure Liquibase for each environment
#   - Step 4: Generate baseline from development
#   - Step 5: Deploy baseline across all environments
#   - Validation of all steps
#   - Cleanup after testing
#
# USAGE:
#   ./test_part1_baseline.sh [options]
#
# OPTIONS:
#   -o, --output <dir>    Output directory for test results (default: /tmp)
#   -k, --keep-env        Keep containers running after test (skip cleanup)
#   -p, --password <pwd>  Use specific password instead of random
#   -v, --verbose         Show verbose output (don't suppress command output)
#   -h, --help            Show this help message
#
# OUTPUT:
#   Test results are written to: <output_dir>/liquibase_part1_test_YYYYMMDD_HHMMSS.log
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
# Requirements: 8+ chars, uppercase, lowercase, number, special char
generate_random_password() {
    local length=${1:-16}
    local password=""

    # Use /dev/urandom for randomness, filter for alphanumeric + special chars
    # Ensure complexity: at least one upper, lower, digit, special
    local upper=$(tr -dc 'A-Z' < /dev/urandom | head -c 3)
    local lower=$(tr -dc 'a-z' < /dev/urandom | head -c 3)
    local digit=$(tr -dc '0-9' < /dev/urandom | head -c 3)
    # Use safe special chars (avoid ! which can cause shell issues)
    local special=$(tr -dc '@#$%&*_=' < /dev/urandom | head -c 2)
    local filler=$(tr -dc 'A-Za-z0-9' < /dev/urandom | head -c $((length - 11)))

    # Combine and shuffle
    password="${upper}${lower}${digit}${special}${filler}"
    # Shuffle the password characters
    password=$(echo "$password" | fold -w1 | shuf | tr -d '\n')

    echo "$password"
}

# Log function that writes to both terminal and log file
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Write to log file
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"

    # Write to terminal with colors
    case "$level" in
        INFO)
            echo -e "${BLUE}[$timestamp]${NC} ${CYAN}[INFO]${NC} $message"
            ;;
        PASS)
            echo -e "${BLUE}[$timestamp]${NC} ${GREEN}[PASS]${NC} $message"
            ;;
        FAIL)
            echo -e "${BLUE}[$timestamp]${NC} ${RED}[FAIL]${NC} $message"
            ;;
        WARN)
            echo -e "${BLUE}[$timestamp]${NC} ${YELLOW}[WARN]${NC} $message"
            ;;
        STEP)
            echo -e "${BLUE}[$timestamp]${NC} ${CYAN}[STEP]${NC} $message"
            ;;
        *)
            echo -e "${BLUE}[$timestamp]${NC} $message"
            ;;
    esac
}

# Log a section header
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

# Abort the test due to a failure
# Performs cleanup and prints summary before exiting
abort_test() {
    local failed_step="$1"

    log "FAIL" "Aborting test due to failure in: $failed_step"
    log "INFO" "Later steps depend on this step - cannot continue"

    # Perform cleanup unless --keep-env was specified
    if [[ "$KEEP_ENV" == "false" ]]; then
        echo "" >> "$LOG_FILE"
        echo "Performing cleanup after failure..." >> "$LOG_FILE"

        log "INFO" "Cleaning up after failure..."

        # Stop and remove containers
        for container in mssql_dev mssql_stg mssql_prd liquibase_tutorial; do
            if $CR_CMD ps -a --format "{{.Names}}" 2>/dev/null | grep -q "^${container}$"; then
                $CR_CMD rm -f "$container" >> "$LOG_FILE" 2>&1 || true
            fi
        done

        # Remove Docker network if it exists
        $CR_CMD network rm liquibase_tutorial_network >> "$LOG_FILE" 2>&1 || true

        # Remove test data directory
        if [[ -d "$LIQUIBASE_TUTORIAL_DATA_DIR" ]]; then
            rm -rf "$LIQUIBASE_TUTORIAL_DATA_DIR" 2>/dev/null || sudo rm -rf "$LIQUIBASE_TUTORIAL_DATA_DIR" 2>/dev/null || true
            log "INFO" "Removed test data directory"
        fi

        log "INFO" "Cleanup complete"
    else
        log "INFO" "Keeping test environment for debugging (--keep-env specified)"
        log "INFO" "Data directory: $LIQUIBASE_TUTORIAL_DATA_DIR"
        log "INFO" "To clean up manually, run:"
        log "INFO" "  $CR_CMD rm -f mssql_dev mssql_stg mssql_prd"
        log "INFO" "  rm -rf $LIQUIBASE_TUTORIAL_DATA_DIR"
    fi

    # Print summary and exit
    print_test_summary
    exit 1
}

# Print test summary (used by both normal completion and abort)
print_test_summary() {
    local summary_end_time=$(date '+%Y-%m-%d %H:%M:%S')
    local total_tests=$((TESTS_PASSED + TESTS_FAILED))

    # Write summary to log file
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

    # Print summary to terminal
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

# Execute a test step and track results
# Arguments: $1=step_name, $2=command
# On failure: aborts the test (later steps depend on this one)
# All output (stdout + stderr) is captured to the log file for troubleshooting
run_test() {
    local test_name="$1"
    local command="$2"
    local start_time=$(date +%s)

    log "STEP" "Running: $test_name"
    echo "Command: $command" >> "$LOG_FILE"

    # Execute command, capturing all output (stdout + stderr)
    local output_file=$(mktemp)
    local exit_code=0

    if [[ "$VERBOSE" == "true" ]]; then
        # Verbose: show on terminal AND capture to log
        if eval "$command" 2>&1 | tee -a "$output_file"; then
            exit_code=0
        else
            exit_code=$?
        fi
    else
        # Non-verbose: capture all output silently
        if eval "$command" >> "$output_file" 2>&1; then
            exit_code=0
        else
            exit_code=$?
        fi
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    # Always append full output to log file for troubleshooting
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

        # Show failure context on terminal (last 30 lines)
        echo -e "${RED}--- Failure output (last 30 lines) ---${NC}"
        tail -30 "$output_file"
        echo -e "${RED}--- End of failure output ---${NC}"
        echo ""

        rm -f "$output_file"
        # Abort - later steps depend on this one succeeding
        abort_test "$test_name"
    fi
}

# Check if a condition is true
# Arguments: $1=check_name, $2=condition (bash expression that returns true/false)
# On failure: aborts the test (later steps depend on this one)
# The condition and any output are logged for troubleshooting
run_check() {
    local check_name="$1"
    local condition="$2"

    # Log the condition being tested
    echo "--- CHECK: $check_name ---" >> "$LOG_FILE"
    echo "Condition: $condition" >> "$LOG_FILE"

    # Capture output from the condition evaluation
    local output
    output=$(eval "$condition" 2>&1) && local result=0 || local result=$?

    if [[ $result -eq 0 ]]; then
        echo "Result: PASS" >> "$LOG_FILE"
        if [[ -n "$output" ]]; then
            echo "Output: $output" >> "$LOG_FILE"
        fi
        echo "" >> "$LOG_FILE"
        log "PASS" "$check_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo "Result: FAIL (exit code: $result)" >> "$LOG_FILE"
        if [[ -n "$output" ]]; then
            echo "Output: $output" >> "$LOG_FILE"
        fi
        echo "" >> "$LOG_FILE"
        log "FAIL" "$check_name"

        # Show failure details on terminal
        echo -e "${RED}--- Check failed: $check_name ---${NC}"
        echo -e "${RED}Condition: $condition${NC}"
        if [[ -n "$output" ]]; then
            echo -e "${RED}Output: $output${NC}"
        fi
        echo ""

        TESTS_FAILED=$((TESTS_FAILED + 1))
        FAILED_TESTS+=("$check_name")
        # Abort - later steps depend on this one succeeding
        abort_test "$check_name"
    fi
}

# Detect container runtime
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

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Set up log file
LOG_FILE="${OUTPUT_DIR}/liquibase_part1_test_${TIMESTAMP}.log"

# Initialize test counters
TESTS_PASSED=0
TESTS_FAILED=0
declare -a FAILED_TESTS=()

# Detect container runtime
CR_CMD=$(detect_container_runtime)
if [[ -z "$CR_CMD" ]]; then
    echo -e "${RED}ERROR: No container runtime found (docker or podman required)${NC}" >&2
    exit 1
fi

# Generate or use provided password
if [[ -n "$CUSTOM_PASSWORD" ]]; then
    TEST_PASSWORD="$CUSTOM_PASSWORD"
else
    TEST_PASSWORD=$(generate_random_password 16)
fi

# Set up test environment
export LIQUIBASE_TUTORIAL_DIR="$TUTORIAL_ROOT"
export LIQUIBASE_TUTORIAL_DATA_DIR="/data/${USER}/liquibase_tutorial_test_${TIMESTAMP}"
export MSSQL_LIQUIBASE_TUTORIAL_PWD="$TEST_PASSWORD"

################################################################################
# Write Test Header
################################################################################

cat > "$LOG_FILE" << EOF
================================================================================
LIQUIBASE TUTORIAL PART 1 - AUTOMATED TEST REPORT
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
  Custom Password:  $([[ -n "$CUSTOM_PASSWORD" ]] && echo "Yes" || echo "No (randomly generated)")

================================================================================
TEST EXECUTION LOG
================================================================================

EOF

echo ""
echo -e "${GREEN}================================================================================${NC}"
echo -e "${GREEN}LIQUIBASE TUTORIAL PART 1 - AUTOMATED TEST${NC}"
echo -e "${GREEN}================================================================================${NC}"
echo ""
echo -e "Test Started:     ${CYAN}$TEST_START_TIME${NC}"
echo -e "Container Runtime: ${CYAN}$CR_CMD${NC}"
echo -e "Output File:      ${CYAN}$LOG_FILE${NC}"
echo -e "Data Directory:   ${CYAN}$LIQUIBASE_TUTORIAL_DATA_DIR${NC}"
echo ""

################################################################################
# PRE-TEST CLEANUP
################################################################################

log_section "Pre-Test Cleanup"

log "INFO" "Cleaning up any existing containers and data..."

# Stop and remove any existing tutorial containers
for container in mssql_dev mssql_stg mssql_prd liquibase_tutorial; do
    if $CR_CMD ps -a --format "{{.Names}}" 2>/dev/null | grep -q "^${container}$"; then
        $CR_CMD rm -f "$container" >> "$LOG_FILE" 2>&1 || true
        log "INFO" "Removed existing container: $container"
    fi
done

# Remove Docker network if it exists
if $CR_CMD network ls --format "{{.Name}}" 2>/dev/null | grep -q "^liquibase_tutorial_network$"; then
    $CR_CMD network rm liquibase_tutorial_network >> "$LOG_FILE" 2>&1 || true
    log "INFO" "Removed existing network: liquibase_tutorial_network"
fi

# Remove test data directory if it exists
if [[ -d "$LIQUIBASE_TUTORIAL_DATA_DIR" ]]; then
    rm -rf "$LIQUIBASE_TUTORIAL_DATA_DIR" 2>/dev/null || sudo rm -rf "$LIQUIBASE_TUTORIAL_DATA_DIR"
    log "INFO" "Removed existing test data directory: $LIQUIBASE_TUTORIAL_DATA_DIR"
fi

# Create fresh data directory for this test
mkdir -p "$LIQUIBASE_TUTORIAL_DATA_DIR"
log "INFO" "Created fresh data directory: $LIQUIBASE_TUTORIAL_DATA_DIR"

# Wait for ports to be released
log "INFO" "Waiting for ports to be released..."
sleep 3

################################################################################
# TEST: Step 0 - Environment Configuration
################################################################################

log_section "Step 0: Environment Configuration"

run_check "LIQUIBASE_TUTORIAL_DIR is set" "[[ -n \"\$LIQUIBASE_TUTORIAL_DIR\" ]]"
run_check "LIQUIBASE_TUTORIAL_DATA_DIR is set" "[[ -n \"\$LIQUIBASE_TUTORIAL_DATA_DIR\" ]]"
run_check "MSSQL_LIQUIBASE_TUTORIAL_PWD is set" "[[ -n \"\$MSSQL_LIQUIBASE_TUTORIAL_PWD\" ]]"
run_check "Tutorial directory exists" "[[ -d \"\$LIQUIBASE_TUTORIAL_DIR\" ]]"
run_check "Scripts directory exists" "[[ -d \"\$LIQUIBASE_TUTORIAL_DIR/scripts\" ]]"

# Create project structure
run_test "Create project structure" "\"$SCRIPT_DIR/create_project_structure.sh\""

run_check "Changelog directory exists" "[[ -d \"\$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog\" ]]"
run_check "Baseline directory exists" "[[ -d \"\$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/baseline\" ]]"
run_check "Changes directory exists" "[[ -d \"\$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changes\" ]]"
run_check "Env directory exists" "[[ -d \"\$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/env\" ]]"

################################################################################
# TEST: Start SQL Server Containers
################################################################################

log_section "Start SQL Server Containers"

run_test "Start MSSQL containers" "\"$SCRIPT_DIR/start_mssql_containers.sh\""

# Wait additional time for SQL Server to fully initialize
log "INFO" "Waiting for SQL Server to initialize (30 seconds)..."
sleep 30

# Verify containers are running
for container in mssql_dev mssql_stg mssql_prd; do
    run_check "Container $container is running" "$CR_CMD ps --format '{{.Names}}' | grep -q '^${container}$'"
done

# Test SQL Server connectivity
log "INFO" "Testing SQL Server connectivity..."

# Source port configuration
PORTS_FILE="$LIQUIBASE_TUTORIAL_DATA_DIR/.ports"
if [[ -f "$PORTS_FILE" ]]; then
    source "$PORTS_FILE"
    log "INFO" "Using ports: DEV=$MSSQL_DEV_PORT, STG=$MSSQL_STG_PORT, PRD=$MSSQL_PRD_PORT"
else
    export MSSQL_DEV_PORT=14331
    export MSSQL_STG_PORT=14332
    export MSSQL_PRD_PORT=14333
    log "INFO" "Using default ports: DEV=$MSSQL_DEV_PORT, STG=$MSSQL_STG_PORT, PRD=$MSSQL_PRD_PORT"
fi

for container in mssql_dev mssql_stg mssql_prd; do
    run_check "SQL Server $container accepts connections" \
        "$CR_CMD exec $container /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P \"\$MSSQL_LIQUIBASE_TUTORIAL_PWD\" -Q 'SELECT 1' -b -o /dev/null 2>/dev/null"
done

################################################################################
# TEST: Build Liquibase Container Image
################################################################################

log_section "Build Liquibase Container Image"

LIQUIBASE_DOCKER_DIR="${TUTORIAL_ROOT}/docker/liquibase"

run_check "Liquibase Dockerfile exists" "[[ -f \"\$LIQUIBASE_DOCKER_DIR/Dockerfile\" ]]"
run_test "Build Liquibase image" "$CR_CMD build -t liquibase:latest \"$LIQUIBASE_DOCKER_DIR\""
run_check "Liquibase image exists" "$CR_CMD images --format '{{.Repository}}:{{.Tag}}' | grep -q 'liquibase:latest'"

# Verify Liquibase runs
run_test "Verify Liquibase CLI" "$CR_CMD run --rm liquibase:latest --version"

################################################################################
# TEST: Step 1 - Create Three Database Environments
################################################################################

log_section "Step 1: Create Three Database Environments"

run_test "Create orderdb databases" "\"$SCRIPT_DIR/create_orderdb_database.sh\""

# Validate databases were created (uses tutorial's validation script)
run_test "Validate orderdb creation" "\"$SCRIPT_DIR/validate_orderdb_database.sh\""

################################################################################
# TEST: Step 2 - Populate Development with Existing Objects
################################################################################

log_section "Step 2: Populate Development with Existing Objects"

run_test "Populate development database" "\"$SCRIPT_DIR/populate_dev_database.sh\""

# Validate population (uses tutorial's validation script)
run_test "Validate development population" "\"$SCRIPT_DIR/validate_dev_populate.sh\""

################################################################################
# TEST: Step 3 - Configure Liquibase for Each Environment
################################################################################

log_section "Step 3: Configure Liquibase for Each Environment"

run_test "Setup Liquibase environment" "\"$SCRIPT_DIR/setup_liquibase_environment.sh\""

# Validate properties files (uses tutorial's validation script)
run_test "Validate Liquibase properties" "\"$SCRIPT_DIR/validate_liquibase_properties.sh\""

################################################################################
# TEST: Step 4 - Generate Baseline from Development
################################################################################

log_section "Step 4: Generate Baseline from Development"

run_test "Generate Liquibase baseline" "\"$SCRIPT_DIR/generate_liquibase_baseline.sh\""

# Validate baseline (uses tutorial's validation script)
run_test "Validate Liquibase baseline" "\"$SCRIPT_DIR/validate_liquibase_baseline.sh\""

################################################################################
# TEST: Step 5 - Deploy Baseline Across Environments
################################################################################

log_section "Step 5: Deploy Baseline Across Environments"

run_test "Deploy baseline to all environments" \
    "\"$SCRIPT_DIR/deploy.sh\" --action baseline --dbi mssql_dev,mssql_stg,mssql_prd"

# Validate deployment (uses tutorial's validation script)
run_test "Validate baseline deployment" \
    "\"$SCRIPT_DIR/validate_liquibase_deploy.sh\" --dbi mssql_dev,mssql_stg,mssql_prd"

################################################################################
# TEST: Final Validation
################################################################################

log_section "Final Validation"

# Run the comprehensive validation script
run_test "Run full validation" "\"$SCRIPT_DIR/validate_tutorial.sh\""

################################################################################
# CLEANUP (unless --keep-env specified)
################################################################################

if [[ "$KEEP_ENV" == "false" ]]; then
    log_section "Post-Test Cleanup"

    log "INFO" "Cleaning up test environment..."

    # Stop and remove containers
    for container in mssql_dev mssql_stg mssql_prd liquibase_tutorial; do
        if $CR_CMD ps -a --format "{{.Names}}" 2>/dev/null | grep -q "^${container}$"; then
            $CR_CMD rm -f "$container" >> "$LOG_FILE" 2>&1 || true
            log "INFO" "Removed container: $container"
        fi
    done

    # Remove Docker network if it exists
    if $CR_CMD network ls --format "{{.Name}}" 2>/dev/null | grep -q "^liquibase_tutorial_network$"; then
        $CR_CMD network rm liquibase_tutorial_network >> "$LOG_FILE" 2>&1 || true
        log "INFO" "Removed network: liquibase_tutorial_network"
    fi

    # Remove test data directory
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

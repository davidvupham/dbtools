#!/usr/bin/env bash
# Test Dynamic Port Assignment
# Comprehensive test script for dynamic port discovery feature
#
# Usage:
#   ./test_dynamic_ports.sh [test_mode]
#   test_mode: full (default), quick, cleanup

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_MODE="${1:-full}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test environment setup
TEST_DATA_DIR="${TEST_DATA_DIR:-/tmp/test_liquibase_ports}"
TEST_PASSWORD="${MSSQL_LIQUIBASE_TUTORIAL_PWD:-TestPassword123!}"
export MSSQL_LIQUIBASE_TUTORIAL_PWD="$TEST_PASSWORD"
export LIQUIBASE_TUTORIAL_DATA_DIR="$TEST_DATA_DIR"

# Cleanup function
cleanup() {
    echo
    echo "========================================"
    echo "Cleaning up test environment..."
    echo "========================================"

    # Stop port blockers
    if [[ -f "$SCRIPT_DIR/test_block_ports.sh" ]]; then
        "$SCRIPT_DIR/test_block_ports.sh" stop || true
    fi

    # Stop and remove test containers
    if command -v podman &>/dev/null; then
        podman stop mssql_dev mssql_stg mssql_prd 2>/dev/null || true
        podman rm -f mssql_dev mssql_stg mssql_prd 2>/dev/null || true
    fi
    if command -v docker &>/dev/null; then
        docker stop mssql_dev mssql_stg mssql_prd 2>/dev/null || true
        docker rm -f mssql_dev mssql_stg mssql_prd 2>/dev/null || true
    fi

    # Clean up test data directory if in quick mode
    if [[ "$TEST_MODE" == "cleanup" ]]; then
        if [[ -d "$TEST_DATA_DIR" ]] && [[ "$TEST_DATA_DIR" == /tmp/test_* ]]; then
            echo "Removing test data directory: $TEST_DATA_DIR"
            rm -rf "$TEST_DATA_DIR" || true
        fi
    fi

    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

trap cleanup EXIT INT TERM

# Test 1: Block default ports
test_block_ports() {
    echo "========================================"
    echo "Test 1: Block Default Ports"
    echo "========================================"

    if [[ ! -f "$SCRIPT_DIR/test_block_ports.sh" ]]; then
        echo -e "${RED}ERROR: test_block_ports.sh not found${NC}"
        return 1
    fi

    echo "Starting port blockers on ports 14331-14333..."
    "$SCRIPT_DIR/test_block_ports.sh" start

    echo
    echo "Verifying ports are blocked..."
    "$SCRIPT_DIR/test_block_ports.sh" status

    echo -e "${GREEN}✓ Test 1 passed: Ports blocked${NC}"
    echo
}

# Test 2: Run start script and verify port discovery
test_port_discovery() {
    echo "========================================"
    echo "Test 2: Dynamic Port Discovery"
    echo "========================================"

    # Ensure data directory exists
    mkdir -p "$TEST_DATA_DIR"

    # Remove any existing .ports file
    rm -f "$TEST_DATA_DIR/.ports"

    echo "Running start_mssql_containers.sh..."
    echo "Test data directory: $TEST_DATA_DIR"
    echo

    if ! "$SCRIPT_DIR/start_mssql_containers.sh"; then
        echo -e "${RED}ERROR: start_mssql_containers.sh failed${NC}"
        return 1
    fi

    echo
    echo -e "${GREEN}✓ Test 2 passed: Script executed successfully${NC}"
    echo
}

# Test 3: Verify .ports file
test_ports_file() {
    echo "========================================"
    echo "Test 3: Verify .ports File"
    echo "========================================"

    local ports_file="$TEST_DATA_DIR/.ports"

    if [[ ! -f "$ports_file" ]]; then
        echo -e "${RED}ERROR: .ports file not found at $ports_file${NC}"
        return 1
    fi

    echo "Reading .ports file:"
    cat "$ports_file"
    echo

    # Source the file and check variables
    source "$ports_file"

    if [[ -z "${MSSQL_DEV_PORT:-}" ]] || [[ -z "${MSSQL_STG_PORT:-}" ]] || [[ -z "${MSSQL_PRD_PORT:-}" ]]; then
        echo -e "${RED}ERROR: Missing port variables in .ports file${NC}"
        return 1
    fi

    echo "Port assignments:"
    echo "  DEV: $MSSQL_DEV_PORT"
    echo "  STG: $MSSQL_STG_PORT"
    echo "  PRD: $MSSQL_PRD_PORT"
    echo

    # Verify ports are NOT the default blocked ports
    if [[ "$MSSQL_DEV_PORT" == "14331" ]] || [[ "$MSSQL_STG_PORT" == "14332" ]] || [[ "$MSSQL_PRD_PORT" == "14333" ]]; then
        echo -e "${RED}ERROR: Script did not find alternate ports!${NC}"
        echo "Ports still using defaults (14331-14333) which should be blocked"
        return 1
    fi

    # Verify ports are consecutive
    if [[ "$MSSQL_STG_PORT" -ne $((MSSQL_DEV_PORT + 1)) ]] || [[ "$MSSQL_PRD_PORT" -ne $((MSSQL_STG_PORT + 1)) ]]; then
        echo -e "${YELLOW}WARNING: Ports are not consecutive (this may be OK if ports were found incrementally)${NC}"
        echo "  Expected consecutive, got: $MSSQL_DEV_PORT, $MSSQL_STG_PORT, $MSSQL_PRD_PORT"
    fi

    echo -e "${GREEN}✓ Test 3 passed: .ports file created with alternate ports${NC}"
    echo "  Assigned ports: $MSSQL_DEV_PORT, $MSSQL_STG_PORT, $MSSQL_PRD_PORT (not 14331-14333)"
    echo
}

# Test 4: Verify containers are using correct ports
test_container_ports() {
    echo "========================================"
    echo "Test 4: Verify Container Ports"
    echo "========================================"

    source "$TEST_DATA_DIR/.ports"

    local cr_cmd=""
    if command -v podman &>/dev/null; then
        cr_cmd="podman"
    elif command -v docker &>/dev/null; then
        cr_cmd="docker"
    else
        echo -e "${RED}ERROR: No container runtime found${NC}"
        return 1
    fi

    echo "Checking container port mappings..."

    for container in mssql_dev mssql_stg mssql_prd; do
        case "$container" in
            mssql_dev) expected_port="$MSSQL_DEV_PORT" ;;
            mssql_stg) expected_port="$MSSQL_STG_PORT" ;;
            mssql_prd) expected_port="$MSSQL_PRD_PORT" ;;
        esac

        # Check if container is running
        if ! $cr_cmd ps --format "{{.Names}}" 2>/dev/null | grep -q "^${container}$"; then
            echo -e "${RED}ERROR: Container $container is not running${NC}"
            return 1
        fi

        # Check port mapping
        if $cr_cmd ps --format "{{.Ports}}" 2>/dev/null | grep "^${container}" | grep -q ":${expected_port}->"; then
            echo -e "  ${GREEN}✓${NC} $container: port $expected_port mapped correctly"
        else
            echo -e "  ${RED}✗${NC} $container: port mapping not found for $expected_port"
            $cr_cmd ps --format "{{.Names}} {{.Ports}}" 2>/dev/null | grep "^${container}"
            return 1
        fi
    done

    echo -e "${GREEN}✓ Test 4 passed: All containers using correct ports${NC}"
    echo
}

# Main test execution
main() {
    echo "========================================"
    echo "Dynamic Port Assignment Test Suite"
    echo "========================================"
    echo "Test mode: $TEST_MODE"
    echo "Test data directory: $TEST_DATA_DIR"
    echo "Test password: [hidden]"
    echo

    if [[ "$TEST_MODE" == "cleanup" ]]; then
        cleanup
        exit 0
    fi

    # Run tests
    test_block_ports || exit 1
    test_port_discovery || exit 1
    test_ports_file || exit 1
    test_container_ports || exit 1

    echo "========================================"
    echo -e "${GREEN}All Tests Passed!${NC}"
    echo "========================================"
    echo
    echo "Summary:"
    source "$TEST_DATA_DIR/.ports"
    echo "  • Default ports (14331-14333) were blocked"
    echo "  • Script found alternate ports: $MSSQL_DEV_PORT, $MSSQL_STG_PORT, $MSSQL_PRD_PORT"
    echo "  • .ports file created correctly"
    echo "  • Containers are using the correct port mappings"
    echo
    echo "Next steps:"
    echo "  1. Test dependent scripts (lb.sh, setup_liquibase_environment.sh)"
    echo "  2. Test full tutorial flow with dynamic ports"
    echo "  3. Run cleanup: $0 cleanup"
}

main "$@"

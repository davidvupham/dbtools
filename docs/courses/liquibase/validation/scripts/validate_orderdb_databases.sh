#!/bin/bash
# Validate OrderDB Databases
# Validates that orderdb exists on all three SQL Server containers
# Reusable across all tutorial parts

set -u

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Validating OrderDB Databases"
echo "========================================"
echo

if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
    echo -e "${RED}ERROR: MSSQL_LIQUIBASE_TUTORIAL_PWD not set${NC}"
    exit 1
fi

FAILURES=0

pass() { echo -e "[${GREEN}PASS${NC}] $1"; }
fail() { echo -e "[${RED}FAIL${NC}] $1"; FAILURES=$((FAILURES+1)); }
warn() { echo -e "[${YELLOW}WARN${NC}] $1"; }

# Detect container runtime
if command -v docker &>/dev/null && docker compose version &>/dev/null; then
    CR_CMD="docker"
elif command -v podman &>/dev/null; then
    CR_CMD="podman"
else
    fail "No container runtime found (docker or podman)"
    exit 1
fi

# Check containers are running
echo "Checking containers are running..."
for container in mssql_dev mssql_stg mssql_prd; do
    if $CR_CMD ps --format "{{.Names}}" | grep -q "^${container}$"; then
        status=$($CR_CMD inspect "$container" --format='{{.State.Status}}' 2>/dev/null)
        if [[ "$status" == "running" ]]; then
            pass "Container $container is running"
        else
            fail "Container $container is not running (status: $status)"
        fi
    else
        fail "Container $container not found"
    fi
done

echo
echo "Checking databases exist..."
# Check database on each container
for container in mssql_dev mssql_stg mssql_prd; do
    echo -n "  Checking $container... "
    # Use -h -1 to suppress headers, -W to remove trailing spaces, and filter out empty lines and status messages
    result=$($CR_CMD exec "$container" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
        -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
        -Q "SELECT name FROM sys.databases WHERE name = 'orderdb';" \
        -h -1 -W 2>&1 | grep -E "^orderdb$" | head -1)

    if [[ "$result" == "orderdb" ]]; then
        pass "$container has orderdb database"
    else
        # Try alternative check - count databases
        db_count=$($CR_CMD exec "$container" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
            -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
            -Q "SELECT COUNT(*) FROM sys.databases WHERE name = 'orderdb';" \
            -h -1 -W 2>&1 | grep -E "^[[:space:]]*1[[:space:]]*$" | wc -l)

        if [[ "$db_count" -gt 0 ]]; then
            pass "$container has orderdb database (verified via count)"
        else
            fail "$container missing orderdb database"
            echo "    Actual result: ${result:-empty}"
        fi
    fi
done

echo
echo "========================================"
if [[ "$FAILURES" -eq 0 ]]; then
    echo -e "${GREEN}VALIDATION SUCCESSFUL${NC}"
    echo "========================================"
    echo
    echo "Expected output summary:"
    echo "  ✓ All three containers (mssql_dev, mssql_stg, mssql_prd) are running"
    echo "  ✓ Each container has 'orderdb' database"
    echo
    exit 0
else
    echo -e "${RED}VALIDATION FAILED ($FAILURES errors)${NC}"
    echo "========================================"
    echo
    echo "To fix:"
    echo "  1. Ensure containers are running: docker ps | grep mssql_"
    echo "  2. Run create_orderdb_databases.sh to create databases"
    echo
    exit 1
fi

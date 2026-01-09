#!/usr/bin/env bash
# Validation Script - Validate Tutorial Setup
# Validates that all tutorial components are correctly configured

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "Liquibase Tutorial - Validation"
echo "========================================"
echo

LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"
PASS_COUNT=0
FAIL_COUNT=0

check() {
    local name="$1"
    local result="$2"
    if [[ "$result" == "true" ]]; then
        echo -e "[${GREEN}PASS${NC}] $name"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo -e "[${RED}FAIL${NC}] $name"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

echo "Environment:"
check "LIQUIBASE_TUTORIAL_DATA_DIR set" "$([[ -n "${LIQUIBASE_TUTORIAL_DATA_DIR:-}" ]] && echo true || echo false)"
check "MSSQL_LIQUIBASE_TUTORIAL_PWD set" "$([[ -n "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]] && echo true || echo false)"
check "Data directory exists" "$([[ -d "$LIQUIBASE_TUTORIAL_DATA_DIR" ]] && echo true || echo false)"

# Detect container runtime
if command -v docker &>/dev/null && docker compose version &>/dev/null; then
    CR_CMD="docker"
elif command -v podman &>/dev/null; then
    CR_CMD="podman"
else
    CR_CMD=""
fi

echo
echo "Containers:"
if [[ -n "$CR_CMD" ]]; then
    for container in mssql_dev mssql_stg mssql_prd; do
        status=$($CR_CMD ps --filter "name=$container" --filter "health=healthy" --format "{{.Names}}" 2>/dev/null || true)
        check "$container healthy" "$([[ "$status" == "$container" ]] && echo true || echo false)"
    done
else
    echo -e "[${YELLOW}SKIP${NC}] Container checks (no runtime found)"
fi

echo
echo "Databases:"
if [[ -n "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" && -n "$CR_CMD" ]]; then
    for container in mssql_dev mssql_stg mssql_prd; do
        result=$($CR_CMD exec "$container" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
            -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
            -Q "SELECT name FROM sys.databases WHERE name = 'orderdb'" 2>/dev/null | grep -c orderdb || true)
        check "orderdb on $container" "$([[ "$result" -ge 1 ]] && echo true || echo false)"
    done
else
    echo -e "[${YELLOW}SKIP${NC}] Database checks (password not set or no runtime)"
fi

echo
echo "Files:"
check "liquibase.dev.properties" "$([[ -f "$LIQUIBASE_TUTORIAL_DATA_DIR/env/liquibase.dev.properties" ]] && echo true || echo false)"
check "liquibase.stg.properties" "$([[ -f "$LIQUIBASE_TUTORIAL_DATA_DIR/env/liquibase.stg.properties" ]] && echo true || echo false)"
check "liquibase.prd.properties" "$([[ -f "$LIQUIBASE_TUTORIAL_DATA_DIR/env/liquibase.prd.properties" ]] && echo true || echo false)"
check "changelog.xml" "$([[ -f "$LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog/changelog.xml" ]] && echo true || echo false)"
check "V0000__baseline.mssql.sql" "$([[ -f "$LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog/baseline/V0000__baseline.mssql.sql" ]] && echo true || echo false)"

echo
echo "========================================"
if [[ $FAIL_COUNT -eq 0 ]]; then
    echo -e "${GREEN}All checks passed!${NC} ($PASS_COUNT passed)"
else
    echo -e "${RED}Some checks failed!${NC} ($PASS_COUNT passed, $FAIL_COUNT failed)"
    exit 1
fi
echo "========================================"

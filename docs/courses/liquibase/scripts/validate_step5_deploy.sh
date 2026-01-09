#!/bin/bash
# Validation script for Step 5: Deploy Baseline Across Environments
# Validates that baseline is deployed to all environments and tracked in Liquibase

set -u

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Validating Step 5: Deploy Baseline"
echo "========================================"
echo

if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
    echo -e "${RED}ERROR: MSSQL_LIQUIBASE_TUTORIAL_PWD not set${NC}"
    exit 1
fi

LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"

FAILURES=0

pass() { echo -e "[${GREEN}PASS${NC}] $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; FAILURES=$((FAILURES+1)); }

# Detect container runtime
if command -v docker &>/dev/null && docker compose version &>/dev/null; then
    CR_CMD="docker"
    NETWORK_ARGS="--network=host"
    DB_HOST="localhost"
elif command -v podman &>/dev/null; then
    CR_CMD="podman"
    NETWORK_ARGS="--network slirp4netns:port_handler=slirp4netns"
    DB_HOST="host.containers.internal"
else
    fail "No container runtime found (docker or podman)"
    exit 1
fi

echo "Checking Liquibase tracking tables..."
echo

# Check each environment
for env in dev stg prd; do
    port=$((14331 + $(echo "dev stg prd" | tr ' ' '\n' | grep -n "^${env}$" | cut -d: -f1) - 1))
    
    echo "Checking $env environment (port $port)..."
    
    # Check DATABASECHANGELOG table exists
    result=$($CR_CMD run --rm $NETWORK_ARGS \
        -v "${LIQUIBASE_TUTORIAL_DATA_DIR}:/data" \
        liquibase:latest \
        --url="jdbc:sqlserver://${DB_HOST}:${port};databaseName=orderdb;encrypt=true;trustServerCertificate=true" \
        --username=sa \
        --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
        --defaults-file="/data/env/liquibase.${env}.properties" \
        --changelog-file=database/changelog/changelog.xml \
        status --verbose 2>&1)
    
    # Check if baseline is tracked
    if echo "$result" | grep -q "baseline\|MARK_RAN\|EXECUTED" || echo "$result" | grep -qi "0 change.*have not been applied"; then
        pass "  $env: Baseline tracked in DATABASECHANGELOG"
    else
        # Check if table exists at all
        table_check=$($CR_CMD exec "mssql_${env}" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
            -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
            -d orderdb \
            -Q "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'DATABASECHANGELOG';" \
            -h -1 -W 2>&1 | grep -v "^$" | tail -1)
        
        if [[ "$table_check" == "1" ]]; then
            fail "  $env: DATABASECHANGELOG exists but baseline not tracked"
        else
            fail "  $env: DATABASECHANGELOG table not found"
        fi
    fi
    
    # Check objects exist in database (baseline was actually applied)
    echo -n "    Checking baseline objects exist... "
    customer_exists=$($CR_CMD exec "mssql_${env}" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
        -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
        -d orderdb \
        -Q "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'app' AND TABLE_NAME = 'customer';" \
        -h -1 -W 2>&1 | grep -v "^$" | tail -1)
    
    if [[ "$customer_exists" == "1" ]]; then
        pass "app.customer table exists"
    else
        fail "app.customer table missing (baseline not deployed)"
    fi
    
    # Check for baseline tag
    echo -n "    Checking baseline tag... "
    tag_check=$($CR_CMD exec "mssql_${env}" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
        -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
        -d orderdb \
        -Q "SELECT TOP 1 TAG FROM DATABASECHANGELOG WHERE TAG = 'baseline';" \
        -h -1 -W 2>&1 | grep -v "^$" | tail -1)
    
    if [[ "$tag_check" == "baseline" ]]; then
        pass "Baseline tag found"
    else
        fail "Baseline tag not found (run: lb -e $env -- tag baseline)"
    fi
    
    echo
done

echo "========================================"
if [[ "$FAILURES" -eq 0 ]]; then
    echo -e "${GREEN}Step 5 VALIDATION SUCCESSFUL${NC}"
    echo "========================================"
    echo
    echo "Expected output summary:"
    echo "  ✓ DATABASECHANGELOG table exists in all environments"
    echo "  ✓ Baseline changesets tracked in all environments"
    echo "  ✓ Baseline objects (app.customer) exist in all environments"
    echo "  ✓ Baseline tag created in all environments"
    echo
    echo "For dev: Changes marked as EXECUTED (changelogSync)"
    echo "For stg/prd: Changes executed (update)"
    echo
    exit 0
else
    echo -e "${RED}Step 5 VALIDATION FAILED ($FAILURES errors)${NC}"
    echo "========================================"
    echo
    echo "To fix:"
    echo "  1. Dev: lb -e dev -- changelogSync && lb -e dev -- tag baseline"
    echo "  2. Stg: lb -e stg -- update && lb -e stg -- tag baseline"
    echo "  3. Prd: lb -e prd -- update && lb -e prd -- tag baseline"
    echo
    exit 1
fi

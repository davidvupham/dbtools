#!/bin/bash
# Validate Development Database Population
# Validates that development database has required objects and sample data
# Reusable across all tutorial parts

set -u

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Validating Development Database Population"
echo "========================================"
echo

if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
    echo -e "${RED}ERROR: MSSQL_LIQUIBASE_TUTORIAL_PWD not set${NC}"
    exit 1
fi

FAILURES=0

pass() { echo -e "[${GREEN}PASS${NC}] $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; FAILURES=$((FAILURES+1)); }

# Detect container runtime
if command -v docker &>/dev/null && docker compose version &>/dev/null; then
    CR_CMD="docker"
elif command -v podman &>/dev/null; then
    CR_CMD="podman"
else
    fail "No container runtime found (docker or podman)"
    exit 1
fi

echo "Checking development database objects..."
echo

# Check app schema exists
echo -n "  Checking app schema... "
result=$($CR_CMD exec mssql_dev /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
    -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
    -d orderdb \
    -Q "SELECT name FROM sys.schemas WHERE name = 'app';" \
    -h -1 -W 2>&1 | grep -v "^$" | tail -1)

if [[ "$result" == "app" ]]; then
    pass "app schema exists"
else
    fail "app schema not found"
fi

# Check customer table exists
echo -n "  Checking customer table... "
result=$($CR_CMD exec mssql_dev /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
    -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
    -d orderdb \
    -Q "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'app' AND TABLE_NAME = 'customer';" \
    -h -1 -W 2>&1 | grep -v "^$" | tail -1)

if [[ "$result" == "customer" ]]; then
    pass "app.customer table exists"
else
    fail "app.customer table not found"
fi

# Check customer table columns
echo -n "  Checking customer table columns... "
columns=$($CR_CMD exec mssql_dev /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
    -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
    -d orderdb \
    -Q "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'app' AND TABLE_NAME = 'customer' ORDER BY ORDINAL_POSITION;" \
    -h -1 -W 2>&1 | grep -v "^$" | grep -v "column_name" | tr '\n' ',')

if echo "$columns" | grep -q "customer_id" && echo "$columns" | grep -q "full_name" && echo "$columns" | grep -q "email"; then
    pass "Customer table has required columns"
else
    fail "Customer table missing required columns (expected: customer_id, full_name, email, phone_number, created_at)"
fi

# Check view exists
echo -n "  Checking v_customer_basic view... "
result=$($CR_CMD exec mssql_dev /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
    -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
    -d orderdb \
    -Q "SELECT name FROM sys.views WHERE schema_id = SCHEMA_ID('app') AND name = 'v_customer_basic';" \
    -h -1 -W 2>&1 | grep -v "^$" | tail -1)

if [[ "$result" == "v_customer_basic" ]]; then
    pass "app.v_customer_basic view exists"
else
    fail "app.v_customer_basic view not found"
fi

# Check sample data
echo -n "  Checking sample data... "
row_count=$($CR_CMD exec mssql_dev /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
    -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
    -d orderdb \
    -Q "SELECT COUNT(*) FROM app.customer;" \
    -h -1 -W 2>&1 | grep -v "^$" | grep -v "^-" | tail -1)

if [[ "$row_count" -ge "3" ]]; then
    pass "Sample data exists ($row_count rows in app.customer)"
else
    fail "Insufficient sample data (found $row_count rows, expected >= 3)"
fi

# Check indexes
echo -n "  Checking indexes... "
index_count=$($CR_CMD exec mssql_dev /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
    -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
    -d orderdb \
    -Q "SELECT COUNT(*) FROM sys.indexes i INNER JOIN sys.objects o ON i.object_id = o.object_id WHERE o.schema_id = SCHEMA_ID('app') AND o.name = 'customer';" \
    -h -1 -W 2>&1 | grep -v "^$" | grep -v "^-" | tail -1)

if [[ "$index_count" -ge "1" ]]; then
    pass "Indexes exist on customer table ($index_count found)"
else
    fail "No indexes found on customer table"
fi

echo
echo "========================================"
if [[ "$FAILURES" -eq 0 ]]; then
    echo -e "${GREEN}VALIDATION SUCCESSFUL${NC}"
    echo "========================================"
    echo
    echo "Expected output summary:"
    echo "  ✓ app schema exists"
    echo "  ✓ app.customer table exists with required columns"
    echo "  ✓ app.v_customer_basic view exists"
    echo "  ✓ Sample data exists (>= 3 rows)"
    echo "  ✓ Indexes exist on customer table"
    echo
    exit 0
else
    echo -e "${RED}VALIDATION FAILED ($FAILURES errors)${NC}"
    echo "========================================"
    echo
    echo "To fix:"
    echo "  1. Ensure mssql_dev container is running"
    echo "  2. Run populate_dev_database.sh to create objects"
    echo "  3. Or manually run: sqlcmd-tutorial populate_orderdb_database.sql"
    echo
    exit 1
fi

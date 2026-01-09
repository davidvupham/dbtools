#!/bin/bash
set -u

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Path to Baseline
BASELINE_FILE="${LIQUIBASE_TUTORIAL_DATA_DIR:?variable not set}/database/changelog/baseline/V0000__baseline.mssql.sql"

echo "Validating Step 4: Baseline Generation"
echo "Target File: $BASELINE_FILE"
echo "---------------------------------------------------"

FAILURES=0

pass() { echo -e "[${GREEN}PASS${NC}] $1"; }
fail() { echo -e "[${RED}FAIL${NC}] $1"; FAILURES=$((FAILURES+1)); }

# 1. Existence Check
if [[ -f "$BASELINE_FILE" ]]; then
    pass "File exists: V0000__baseline.mssql.sql"
else
    fail "File not found: V0000__baseline.mssql.sql"
    exit 1
fi

# 2. Formatted SQL Header Check
if grep -q "\-\- liquibase formatted sql" "$BASELINE_FILE"; then
    pass "Header matches '-- liquibase formatted sql'"
else
    fail "Header missing or incorrect. Expected '-- liquibase formatted sql'"
fi

# 3. Schema Check (app. prefix)
COUNT_SCHEMA=$(grep -c "app\." "$BASELINE_FILE")
if [[ "$COUNT_SCHEMA" -gt 0 ]]; then
    pass "Found $COUNT_SCHEMA occurrences of 'app.' schema prefix"
else
    fail "No usage of 'app.' schema found. Did you forget --schemas=app or --include-schema=true?"
fi

# 4. Object Checks
# Check Table
if grep -q "CREATE TABLE app.customer" "$BASELINE_FILE"; then
    pass "Found CREATE TABLE app.customer"
else
    fail "Missing CREATE TABLE app.customer"
fi

# Check View
if grep -q "CREATE VIEW app.v_customer_basic" "$BASELINE_FILE"; then
    pass "Found CREATE VIEW app.v_customer_basic"
else
    fail "Missing CREATE VIEW app.v_customer_basic"
fi

# Check Index
if grep -q "INDEX IX_customer_name" "$BASELINE_FILE"; then
    pass "Found INDEX IX_customer_name"
else
    fail "Missing INDEX IX_customer_name"
fi

# 5. Changeset Check
COUNT_CHANGESETS=$(grep -c "\-\- changeset" "$BASELINE_FILE")
if [[ "$COUNT_CHANGESETS" -ge 4 ]]; then
    pass "Found $COUNT_CHANGESETS changesets (Expected >= 4)"
else
    fail "Found minimal changesets ($COUNT_CHANGESETS). Expected at least 4."
fi

echo "---------------------------------------------------"
if [[ "$FAILURES" -eq 0 ]]; then
    echo -e "${GREEN}Step 4 VALIDATION SUCCESSFUL${NC}"
    echo "========================================"
    echo
    echo "Expected output summary:"
    echo "  ✓ Baseline file exists: V0000__baseline.mssql.sql"
    echo "  ✓ Contains '-- liquibase formatted sql' header"
    echo "  ✓ Uses 'app.' schema prefix for all objects"
    echo "  ✓ Contains CREATE TABLE app.customer"
    echo "  ✓ Contains CREATE VIEW app.v_customer_basic"
    echo "  ✓ Contains INDEX definitions"
    echo "  ✓ Contains multiple changesets (>= 4)"
    echo
    exit 0
else
    echo -e "${RED}Step 4 VALIDATION FAILED ($FAILURES errors)${NC}"
    echo "========================================"
    echo
    echo "To fix:"
    echo "  1. Ensure Step 2 completed (dev database populated)"
    echo "  2. Run step05_generate_baseline.sh"
    echo "  3. Or manually run: lb -e dev -- generateChangeLog --schemas=app --include-schema=true"
    echo
    exit 1
fi

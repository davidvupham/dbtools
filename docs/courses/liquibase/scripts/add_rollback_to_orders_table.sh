#!/usr/bin/env bash
# Add Rollback to Orders Table
# Adds rollback blocks to V0001 orders table changelog file
# Reusable across all tutorial parts

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "Liquibase Tutorial - Add Rollback to Orders Table"
echo "========================================"
echo

LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"
export LIQUIBASE_TUTORIAL_DATA_DIR

CHANGE_FILE="$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changes/V0001__add_orders_table.mssql.sql"

# Check if V0001 change file exists
if [[ ! -f "$CHANGE_FILE" ]]; then
    echo -e "${RED}ERROR: V0001 change file not found at $CHANGE_FILE${NC}"
    echo "Please run create_orders_table_changelog.sh first"
    exit 1
fi

# Check if file is readable
if [[ ! -r "$CHANGE_FILE" ]]; then
    echo -e "${RED}ERROR: Cannot read file: $CHANGE_FILE${NC}"
    exit 1
fi

# Check if file is writable
if [[ ! -w "$CHANGE_FILE" ]]; then
    echo -e "${RED}ERROR: Cannot write to file: $CHANGE_FILE${NC}"
    exit 1
fi

# Check if rollback already exists (idempotency)
if grep -q "--rollback DROP TABLE IF EXISTS app.orders" "$CHANGE_FILE"; then
    echo -e "${YELLOW}Rollback already exists in file${NC}"
    echo -e "${GREEN}✓ Done${NC}"
    echo
    echo "========================================"
    echo -e "${GREEN}Rollback Already Present${NC}"
    echo "========================================"
    echo "File: $CHANGE_FILE"
    echo
    exit 0
fi

# Add rollback to V0001 change file
echo -n "Adding rollback to V0001 change file... "

# Ensure file ends with newline before appending (handle edge case)
if [[ -s "$CHANGE_FILE" ]]; then
    # Read last byte to check if file ends with newline
    LAST_CHAR=$(tail -c1 "$CHANGE_FILE" 2>/dev/null || echo "")
    if [[ "$LAST_CHAR" != "" ]] && [[ "$LAST_CHAR" != $'\n' ]]; then
        # File doesn't end with newline, add one
        echo "" >> "$CHANGE_FILE"
    fi
fi

# Append rollback section
{
    echo "--rollback DROP TABLE IF EXISTS app.orders;"
    echo "--rollback GO"
} >> "$CHANGE_FILE"

# Validate that rollback was added
if grep -q "--rollback DROP TABLE IF EXISTS app.orders" "$CHANGE_FILE"; then
    echo -e "${GREEN}✓ Done${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
    echo "Rollback section was not added successfully"
    exit 1
fi

echo
echo "========================================"
echo -e "${GREEN}Rollback Added${NC}"
echo "========================================"
echo "Updated file: $CHANGE_FILE"
echo
echo "Next: Practice rollback in development with 'lb -e dev -- rollbackSQL baseline'"

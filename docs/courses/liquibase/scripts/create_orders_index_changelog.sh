#!/usr/bin/env bash
# Create Orders Index Changelog
# Creates V0002 change file for orders index and updates master changelog.xml
# Reusable across all tutorial parts

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "Liquibase Tutorial - Create Orders Index Changelog"
echo "========================================"
echo

LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"
export LIQUIBASE_TUTORIAL_DATA_DIR

CHANGES_DIR="$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changes"
CHANGELOG_FILE="$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changelog.xml"
CHANGE_FILE="$CHANGES_DIR/V0002__add_orders_index.mssql.sql"

# Check if changelog.xml exists (required for updating)
if [[ ! -f "$CHANGELOG_FILE" ]]; then
    echo -e "${RED}ERROR: changelog.xml not found at $CHANGELOG_FILE${NC}"
    echo "Please run setup_liquibase_environment.sh first"
    exit 1
fi

# Create changes directory if it doesn't exist
echo -n "Creating changes directory... "
if mkdir -p "$CHANGES_DIR" 2>/dev/null; then
    echo -e "${GREEN}✓ Done${NC}"
elif sudo mkdir -p "$CHANGES_DIR" 2>/dev/null; then
    sudo chown -R "$USER:$USER" "$CHANGES_DIR" 2>/dev/null || true
    echo -e "${GREEN}✓ Done${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
    echo "Cannot create directory: $CHANGES_DIR"
    exit 1
fi

# Check if directory is writable
if [[ ! -w "$CHANGES_DIR" ]]; then
    echo -e "${YELLOW}Warning: Directory not writable, attempting to fix permissions...${NC}"
    sudo chown -R "$USER:$USER" "$CHANGES_DIR" 2>/dev/null || {
        echo -e "${RED}ERROR: Cannot write to directory: $CHANGES_DIR${NC}"
        exit 1
    }
fi

# Check if V0001 exists (should be deployed first)
V0001_FILE="$CHANGES_DIR/V0001__add_orders_table.mssql.sql"
if [[ ! -f "$V0001_FILE" ]]; then
    echo -e "${YELLOW}WARNING: V0001 change file not found${NC}"
    echo "V0002 should be created after V0001"
fi

# Create V0002 change file
echo -n "Creating V0002 change file... "
cat > "$CHANGE_FILE" << 'EOF'
--liquibase formatted sql

--changeset tutorial:V0002-add-orders-date-index
-- Purpose: Add performance index on order_date for reporting queries

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_orders_order_date'
    AND object_id = OBJECT_ID('app.orders')
)
BEGIN
    CREATE INDEX IX_orders_order_date ON app.orders(order_date DESC);
END
GO
--rollback DROP INDEX IF EXISTS IX_orders_order_date ON app.orders;
--rollback GO
EOF

if [[ -f "$CHANGE_FILE" ]]; then
    echo -e "${GREEN}✓ Done${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
    exit 1
fi

# Ensure parent directory is owned by user so new file will be owned by user
CHANGELOG_DIR="$(dirname "$CHANGELOG_FILE")"
if [[ -d "$CHANGELOG_DIR" ]] && [[ ! -O "$CHANGELOG_DIR" ]]; then
    echo -e "${YELLOW}Warning: changelog directory not owned by user, fixing ownership...${NC}"
    sudo chown -R "$USER:$USER" "$CHANGELOG_DIR" 2>/dev/null || {
        echo -e "${RED}ERROR: Cannot fix ownership of changelog directory: $CHANGELOG_DIR${NC}"
        exit 1
    }
fi

# Update master changelog.xml
echo -n "Updating master changelog.xml... "
# Save current umask
OLD_UMASK=$(umask)
# Set umask for group-writable files (664)
umask 0002
cat > "$CHANGELOG_FILE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <!-- Baseline -->
    <include file="baseline/V0000__baseline.mssql.sql" relativeToChangelogFile="true"/>

    <!-- V0001: Add orders table -->
    <include file="changes/V0001__add_orders_table.mssql.sql" relativeToChangelogFile="true"/>

    <!-- V0002: Add orders index -->
    <include file="changes/V0002__add_orders_index.mssql.sql" relativeToChangelogFile="true"/>

</databaseChangeLog>
EOF
# Restore original umask
umask "$OLD_UMASK"

if grep -q "V0002__add_orders_index" "$CHANGELOG_FILE"; then
    echo -e "${GREEN}✓ Done${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
    exit 1
fi

echo
echo "========================================"
echo -e "${GREEN}Orders Index Changelog Created${NC}"
echo "========================================"
echo "Change file:  $CHANGE_FILE"
echo "Changelog:    $CHANGELOG_FILE"
echo
echo "Next: Deploy to development with 'lb -e dev -- update'"

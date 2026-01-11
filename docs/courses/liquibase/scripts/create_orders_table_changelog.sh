#!/usr/bin/env bash
# Create Orders Table Changelog
# Creates V0001 change file for orders table and updates master changelog.xml
# Reusable across all tutorial parts

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "Liquibase Tutorial - Create Orders Table Changelog"
echo "========================================"
echo

LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"
export LIQUIBASE_TUTORIAL_DATA_DIR

CHANGES_DIR="$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changes"
CHANGELOG_FILE="$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changelog.xml"
CHANGE_FILE="$CHANGES_DIR/V0001__add_orders_table.mssql.sql"

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

# Create V0001 change file
echo -n "Creating V0001 change file... "
cat > "$CHANGE_FILE" << 'EOF'
--liquibase formatted sql

--changeset tutorial:V0001-add-orders-table
-- Purpose: Add orders table to track customer purchases
-- This change creates:
--   - orders table with 5 columns (order_id, customer_id, order_total, order_date, status)
--   - Primary key constraint (PK_orders)
--   - Foreign key constraint to customer table (FK_orders_customer)
--   - Two default constraints (DF_orders_date for order_date, inline default for status)

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE object_id = OBJECT_ID(N'[app].[orders]') AND type = 'U')
BEGIN
    CREATE TABLE app.orders (
        order_id INT IDENTITY(1,1) CONSTRAINT PK_orders PRIMARY KEY,
        customer_id INT NOT NULL,
        order_total DECIMAL(18,2) NOT NULL,
        order_date DATETIME2(3) NOT NULL CONSTRAINT DF_orders_date DEFAULT (SYSUTCDATETIME()),
        status NVARCHAR(50) NOT NULL DEFAULT 'pending',
        CONSTRAINT FK_orders_customer FOREIGN KEY (customer_id)
            REFERENCES app.customer(customer_id)
    );
END
GO
EOF

if [[ -f "$CHANGE_FILE" ]]; then
    echo -e "${GREEN}✓ Done${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
    exit 1
fi

# Update master changelog.xml
echo -n "Updating master changelog.xml... "
cat > "$CHANGELOG_FILE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

    <!-- Baseline: initial database state -->
    <include file="baseline/V0000__baseline.mssql.sql" relativeToChangelogFile="true"/>

    <!-- V0001: Add orders table -->
    <include file="changes/V0001__add_orders_table.mssql.sql" relativeToChangelogFile="true"/>

</databaseChangeLog>
EOF

if grep -q "V0001__add_orders_table" "$CHANGELOG_FILE"; then
    echo -e "${GREEN}✓ Done${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
    exit 1
fi

echo
echo "========================================"
echo -e "${GREEN}Orders Table Changelog Created${NC}"
echo "========================================"
echo "Change file:  $CHANGE_FILE"
echo "Changelog:    $CHANGELOG_FILE"
echo
echo "Next: Deploy to development with 'lb -e dev -- update'"

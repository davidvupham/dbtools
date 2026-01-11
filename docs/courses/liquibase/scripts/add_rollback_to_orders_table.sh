#!/usr/bin/env bash
# Add Rollback to Orders Table
# Adds rollback blocks to V0001 orders table changelog file
# Reusable across all tutorial parts

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
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

# Update V0001 change file to include rollback
echo -n "Adding rollback to V0001 change file... "
cat > "$CHANGE_FILE" << 'EOF'
--liquibase formatted sql

--changeset tutorial:V0001-add-orders-table
-- Purpose: Add orders table to track customer purchases

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
--rollback DROP TABLE IF EXISTS app.orders;
--rollback GO
EOF

if grep -q "--rollback DROP TABLE IF EXISTS app.orders" "$CHANGE_FILE"; then
    echo -e "${GREEN}✓ Done${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
    exit 1
fi

echo
echo "========================================"
echo -e "${GREEN}Rollback Added${NC}"
echo "========================================"
echo "Updated file: $CHANGE_FILE"
echo
echo "Next: Practice rollback in development with 'lb -e dev -- rollbackSQL baseline'"

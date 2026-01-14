#!/bin/bash
################################################################################
# revert_drift.sh - Revert Simulated Database Drift
################################################################################
#
# PURPOSE:
#   Reverts the simulated database drift changes created during the tutorial.
#   This includes:
#   - Removing the loyalty_points column from app.customer
#   - Restoring first_name column to NVARCHAR(100) NOT NULL
#   - Recreating the IX_orders_order_date index
#
# USAGE:
#   revert_drift.sh --dbi <instances>
#
# OPTIONS:
#   -d, --dbi <instances>    Target database instance(s) - comma-separated (required)
#                           Values: mssql_dev, mssql_stg, mssql_prd
#   -h, --help              Show this help message
#
# EXAMPLES:
#   revert_drift.sh --dbi mssql_dev
#   revert_drift.sh --dbi mssql_dev,mssql_stg,mssql_prd
#
################################################################################

set -u

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SQLCMD="$SCRIPT_DIR/sqlcmd_tutorial.sh"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

################################################################################
# Helper Functions
################################################################################

print_usage() {
    cat <<'EOF'
Usage:
  revert_drift.sh --dbi <instances>

Options:
  -d, --dbi <instances>    Target database instance(s) - comma-separated (required)
                          Values: mssql_dev, mssql_stg, mssql_prd
  -h, --help              Show this help message

Examples:
  revert_drift.sh --dbi mssql_dev
  revert_drift.sh --dbi mssql_dev,mssql_stg,mssql_prd
EOF
}

# Get human-readable instance name
pretty_instance() {
    case "$1" in
        mssql_dev) echo "Development (mssql_dev)" ;;
        mssql_stg) echo "Staging (mssql_stg)" ;;
        mssql_prd) echo "Production (mssql_prd)" ;;
        *)         echo "$1" ;;
    esac
}

################################################################################
# Parse Arguments
################################################################################

INSTANCES=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--dbi)
            INSTANCES="$2"
            shift 2
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option: $1${NC}" >&2
            print_usage
            exit 1
            ;;
    esac
done

################################################################################
# Validate Arguments
################################################################################

if [[ -z "$INSTANCES" ]]; then
    echo -e "${RED}Error: --dbi is required${NC}" >&2
    print_usage
    exit 1
fi

# Parse comma-separated instances into array
IFS=',' read -ra TARGET_INSTANCES <<< "$INSTANCES"

# Validate each instance
VALID_INSTANCES="mssql_dev mssql_stg mssql_prd"
for instance in "${TARGET_INSTANCES[@]}"; do
    if [[ ! " $VALID_INSTANCES " =~ " $instance " ]]; then
        echo -e "${RED}Error: Invalid instance '$instance'. Valid values: mssql_dev, mssql_stg, mssql_prd${NC}" >&2
        exit 1
    fi
done

################################################################################
# Revert Drift Function
################################################################################

revert_instance() {
    local instance="$1"
    local pretty_name
    pretty_name=$(pretty_instance "$instance")
    local failures=0

    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}Reverting drift on: $pretty_name${NC}"
    echo -e "${CYAN}========================================${NC}"

    # Type 1: Remove the unexpected column (must drop default constraint first)
    echo ""
    echo -e "${YELLOW}[Type 1] Removing loyalty_points column...${NC}"
    if "$SQLCMD" -S "$instance" -Q "
USE orderdb;
DECLARE @constraint_name NVARCHAR(200);
SELECT @constraint_name = dc.name 
FROM sys.default_constraints dc
JOIN sys.columns c ON dc.parent_object_id = c.object_id AND dc.parent_column_id = c.column_id
WHERE c.object_id = OBJECT_ID('app.customer') AND c.name = 'loyalty_points';

IF @constraint_name IS NOT NULL
    EXEC('ALTER TABLE app.customer DROP CONSTRAINT ' + @constraint_name);

IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('app.customer') AND name = 'loyalty_points')
    ALTER TABLE app.customer DROP COLUMN loyalty_points;
" 2>&1; then
        echo -e "${GREEN}✓ Type 1 completed${NC}"
    else
        echo -e "${RED}✗ Type 1 failed${NC}"
        ((failures++))
    fi

    # Type 2: Restore the original column size (must drop/recreate index first)
    echo ""
    echo -e "${YELLOW}[Type 2] Restoring first_name column definition...${NC}"
    if "$SQLCMD" -S "$instance" -Q "
USE orderdb;
-- Drop the index that depends on first_name
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_customer_name' AND object_id = OBJECT_ID('app.customer'))
    DROP INDEX IX_customer_name ON app.customer;

-- Update any NULL values
UPDATE app.customer SET first_name = '' WHERE first_name IS NULL;

-- Restore original column definition
ALTER TABLE app.customer ALTER COLUMN first_name NVARCHAR(100) NOT NULL;

-- Recreate the index
CREATE INDEX IX_customer_name ON app.customer(last_name, first_name);
" 2>&1; then
        echo -e "${GREEN}✓ Type 2 completed${NC}"
    else
        echo -e "${RED}✗ Type 2 failed${NC}"
        ((failures++))
    fi

    # Type 3: Recreate the missing index
    echo ""
    echo -e "${YELLOW}[Type 3] Recreating IX_orders_order_date index...${NC}"
    if "$SQLCMD" -S "$instance" -Q "
USE orderdb;
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_orders_order_date' AND object_id = OBJECT_ID('app.orders'))
    CREATE INDEX IX_orders_order_date ON app.orders(order_date DESC);
" 2>&1; then
        echo -e "${GREEN}✓ Type 3 completed${NC}"
    else
        echo -e "${RED}✗ Type 3 failed${NC}"
        ((failures++))
    fi

    return $failures
}

################################################################################
# Main Execution
################################################################################

TOTAL_FAILURES=0

for instance in "${TARGET_INSTANCES[@]}"; do
    if ! revert_instance "$instance"; then
        ((TOTAL_FAILURES++))
    fi
done

# Summary
echo ""
echo "========================================"
echo "Summary"
echo "========================================"

if [[ $TOTAL_FAILURES -eq 0 ]]; then
    echo -e "${GREEN}All drift reversions completed successfully.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Verify drift has been resolved:"
    echo "     \$LIQUIBASE_TUTORIAL_DIR/scripts/detect_drift.sh --dbi ${TARGET_INSTANCES[*]// /,}"
    exit 0
else
    echo -e "${RED}$TOTAL_FAILURES instance(s) had failures during reversion.${NC}"
    exit 1
fi

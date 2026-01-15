#!/usr/bin/env bash
# Generate Liquibase Baseline
# Generates baseline changelog from development database using Liquibase
# Reusable across all tutorial parts

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "========================================"
echo "Liquibase Tutorial - Generate Baseline"
echo "========================================"
echo

LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"
export LIQUIBASE_TUTORIAL_DATA_DIR

if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
    echo -e "${RED}ERROR: MSSQL_LIQUIBASE_TUTORIAL_PWD not set${NC}"
    exit 1
fi
export MSSQL_LIQUIBASE_TUTORIAL_PWD

echo "Generating baseline from mssql_dev..."
echo

# Use lb.sh wrapper to run Liquibase generateChangeLog
# IMPORTANT: Use --include-schema=true to include schema names in SQL (app. prefix)
"$SCRIPT_DIR/lb.sh" --dbi mssql_dev -- \
    --changelog-file=/data/platform/mssql/database/orderdb/changelog/baseline/V0000__baseline.mssql.sql \
    --schemas=app \
    --include-schema=true \
    --overwrite-output-file=true \
    generateChangeLog 2>&1

# Verify baseline was created
if [[ -f "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/baseline/V0000__baseline.mssql.sql" ]]; then
    echo
    echo "========================================"
    echo -e "${GREEN}Baseline Generated${NC}"
    echo "========================================"
    echo "Baseline generated at:"
    echo "  $LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/baseline/V0000__baseline.mssql.sql"
    echo
    echo "Preview (first 20 lines):"
    head -20 "$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/baseline/V0000__baseline.mssql.sql"
    echo
    echo "Next: Run deploy_liquibase_baseline.sh"
else
    echo -e "${RED}✗ Failed to generate baseline${NC}"
    exit 1
fi

#!/usr/bin/env bash
# Create OrderDB Databases
# Creates orderdb database and app schema on all SQL Server containers
# Reusable across all tutorial parts

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "Liquibase Tutorial - Create OrderDB Databases"
echo "========================================"
echo

if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
    echo -e "${RED}ERROR: MSSQL_LIQUIBASE_TUTORIAL_PWD not set${NC}"
    exit 1
fi

# Detect container runtime
if command -v docker &>/dev/null && docker compose version &>/dev/null; then
    CR_CMD="docker"
elif command -v podman &>/dev/null; then
    CR_CMD="podman"
else
    echo -e "${RED}ERROR: No container runtime found${NC}"
    exit 1
fi

# Create database and app schema on each container
for container in mssql_dev mssql_stg mssql_prd; do
    echo -n "Creating orderdb on $container... "
    result=$($CR_CMD exec "$container" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
        -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
        -Q "IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'orderdb') CREATE DATABASE orderdb; SELECT name FROM sys.databases WHERE name = 'orderdb';" 2>&1)

    if echo "$result" | grep -q "orderdb"; then
        echo -e "${GREEN}✓ Done${NC}"
    else
        echo -e "${RED}✗ Failed${NC}"
        echo "$result"
        exit 1
    fi

    # Create app schema in orderdb (required before Liquibase can create objects)
    echo -n "Creating app schema on $container... "
    result=$($CR_CMD exec "$container" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
        -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
        -d orderdb \
        -Q "IF NOT EXISTS (SELECT name FROM sys.schemas WHERE name = 'app') EXEC('CREATE SCHEMA app'); SELECT name FROM sys.schemas WHERE name = 'app';" 2>&1)

    if echo "$result" | grep -q "app"; then
        echo -e "${GREEN}✓ Done${NC}"
    else
        echo -e "${YELLOW}⚠ Warning: Schema creation may have failed${NC}"
        echo "$result"
    fi
done

echo
echo "========================================"
echo -e "${GREEN}Databases Created${NC}"
echo "========================================"
echo "Database 'orderdb' created on all environments"
echo
echo "Next: Run populate_dev_database.sh"

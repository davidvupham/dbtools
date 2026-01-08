#!/usr/bin/env bash
# Tutorial Setup Script - Step 03: Create Databases
# Creates orderdb database on all SQL Server containers

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "========================================"
echo "Liquibase Tutorial - Step 03: Create Databases"
echo "========================================"
echo

if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
    echo -e "${RED}ERROR: MSSQL_LIQUIBASE_TUTORIAL_PWD not set${NC}"
    exit 1
fi

# Create database on each container
for container in mssql_dev mssql_stg mssql_prd; do
    echo -n "Creating orderdb on $container... "
    result=$(podman exec "$container" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
        -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
        -Q "IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'orderdb') CREATE DATABASE orderdb; SELECT name FROM sys.databases WHERE name = 'orderdb';" 2>&1)
    
    if echo "$result" | grep -q "orderdb"; then
        echo -e "${GREEN}✓ Done${NC}"
    else
        echo -e "${RED}✗ Failed${NC}"
        echo "$result"
        exit 1
    fi
done

echo
echo "========================================"
echo -e "${GREEN}Step 03 Complete${NC}"
echo "========================================"
echo "Database 'orderdb' created on all environments"
echo
echo "Next: Run step04_populate_dev.sh"

#!/usr/bin/env bash
# Tutorial Setup Script - Step 04: Populate Development
# Creates sample objects in development database for baseline

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "========================================"
echo "Liquibase Tutorial - Step 04: Populate Development"
echo "========================================"
echo

if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
    echo -e "${RED}ERROR: MSSQL_LIQUIBASE_TUTORIAL_PWD not set${NC}"
    exit 1
fi

# SQL to create sample objects
SQL_SCRIPT=$(cat << 'EOSQL'
USE orderdb;
GO

-- Create app schema
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'app')
    EXEC('CREATE SCHEMA app');
GO

-- Create customer table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'customer' AND schema_id = SCHEMA_ID('app'))
BEGIN
    CREATE TABLE app.customer (
        customer_id INT IDENTITY(1,1) CONSTRAINT PK_customer PRIMARY KEY,
        first_name NVARCHAR(100) NOT NULL,
        last_name NVARCHAR(100) NOT NULL,
        email NVARCHAR(255) NOT NULL CONSTRAINT UQ_customer_email UNIQUE,
        created_at DATETIME2(3) NOT NULL CONSTRAINT DF_customer_created_at DEFAULT (SYSUTCDATETIME())
    );
    PRINT 'Created table: app.customer';
END
ELSE
    PRINT 'Table app.customer already exists';
GO

-- Create customer view
IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'v_customer_basic' AND schema_id = SCHEMA_ID('app'))
BEGIN
    EXEC('CREATE VIEW app.v_customer_basic AS SELECT customer_id, first_name, last_name FROM app.customer');
    PRINT 'Created view: app.v_customer_basic';
END
ELSE
    PRINT 'View app.v_customer_basic already exists';
GO

-- Verify objects
SELECT 'Created objects:' AS Status;
SELECT TABLE_SCHEMA + '.' + TABLE_NAME AS ObjectName, TABLE_TYPE 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'app';
GO
EOSQL
)

echo "Creating sample objects in mssql_dev..."
echo

# Detect container runtime
if command -v docker &>/dev/null && docker compose version &>/dev/null; then
    CR_CMD="docker"
elif command -v podman &>/dev/null; then
    CR_CMD="podman"
else
    echo -e "${RED}ERROR: No container runtime found${NC}"
    exit 1
fi

result=$(echo "$SQL_SCRIPT" | $CR_CMD exec -i mssql_dev /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" 2>&1)
echo "$result"

if echo "$result" | grep -q "app.customer"; then
    echo
    echo "========================================"
    echo -e "${GREEN}Step 04 Complete${NC}"
    echo "========================================"
    echo "Development database populated with:"
    echo "  - app.customer table"
    echo "  - app.v_customer_basic view"
    echo
    echo "Next: Run step05_generate_baseline.sh"
else
    echo -e "${RED}✗ Failed to create objects${NC}"
    exit 1
fi

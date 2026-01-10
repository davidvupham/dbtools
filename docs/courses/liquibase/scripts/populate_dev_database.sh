#!/usr/bin/env bash
# Populate Development Database
# Creates sample objects in development database for baseline
# Reusable across all tutorial parts

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "========================================"
echo "Liquibase Tutorial - Populate Development Database"
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

-- Create index on customer name (for search optimization)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_customer_name' AND object_id = OBJECT_ID('app.customer'))
BEGIN
    CREATE NONCLUSTERED INDEX IX_customer_name ON app.customer (last_name, first_name);
    PRINT 'Created index: IX_customer_name';
END
ELSE
    PRINT 'Index IX_customer_name already exists';
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

-- Reset and insert sample data (idempotent)
DELETE FROM app.customer;
INSERT INTO app.customer (first_name, last_name, email)
VALUES 
    ('Alice', 'Johnson', 'alice.johnson@example.com'),
    ('Bob', 'Smith', 'bob.smith@example.com'),
    ('Carol', 'Williams', 'carol.williams@example.com');
PRINT 'Inserted sample data: 3 rows';
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

echo "Using container runtime: $CR_CMD"
echo "$SQL_SCRIPT" | $CR_CMD exec -i mssql_dev /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" 2>&1 || true

# Verify objects exist (idempotent check)
echo
echo "Verifying database objects..."

verify_result=$($CR_CMD exec mssql_dev /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
    -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
    -d orderdb \
    -Q "SET NOCOUNT ON; SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'app' AND TABLE_NAME IN ('customer', 'v_customer_basic');" \
    -h -1 -W 2>&1 | grep -E '^[0-9]+$' | head -1)

if [[ "$verify_result" == "2" ]]; then
    echo
    echo "========================================"
    echo -e "${GREEN}Development Database Ready${NC}"
    echo "========================================"
    echo "Objects in orderdb:"
    echo "  ✓ app.customer table"
    echo "  ✓ IX_customer_name index"
    echo "  ✓ app.v_customer_basic view"
    echo
    echo "Next: Run generate_liquibase_baseline.sh"
else
    echo -e "${RED}✗ Failed to verify objects (found $verify_result of 2 expected)${NC}"
    exit 1
fi

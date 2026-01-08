#!/usr/bin/env bash
# Tutorial Setup Script - Step 01: Environment Setup
# Creates directories and configures environment for Liquibase tutorial

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TUTORIAL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Liquibase Tutorial - Step 01: Setup"
echo "========================================"
echo

# Determine data directory
LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"
export LIQUIBASE_TUTORIAL_DATA_DIR

echo "Data directory: $LIQUIBASE_TUTORIAL_DATA_DIR"

# Create directories
echo -n "Creating directories... "
if mkdir -p "$LIQUIBASE_TUTORIAL_DATA_DIR"/{mssql_dev,mssql_stg,mssql_prd,database/changelog/{baseline,changes},env} 2>/dev/null; then
    echo -e "${GREEN}✓ Done${NC}"
else
    echo -e "${YELLOW}Using sudo...${NC}"
    sudo mkdir -p "$LIQUIBASE_TUTORIAL_DATA_DIR"/{mssql_dev,mssql_stg,mssql_prd,database/changelog/{baseline,changes},env}
    sudo chown -R "$USER:$USER" "$LIQUIBASE_TUTORIAL_DATA_DIR"
    echo -e "${GREEN}✓ Done${NC}"
fi

# Prompt for password if not set
if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
    echo
    echo "SQL Server password not set."
    read -sp "Enter password for SQL Server (min 8 chars, mixed case, number, special): " MSSQL_LIQUIBASE_TUTORIAL_PWD
    echo
fi
export MSSQL_LIQUIBASE_TUTORIAL_PWD

# Create properties files for each environment
echo -n "Creating Liquibase properties files... "
for env in dev stg prd; do
    port=$((14331 + $(echo "dev stg prd" | tr ' ' '\n' | grep -n "^${env}$" | cut -d: -f1) - 1))
    cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/env/liquibase.${env}.properties" << EOF
# ${env^^} Environment - Liquibase Properties
url=jdbc:sqlserver://localhost:${port};databaseName=orderdb;encrypt=true;trustServerCertificate=true
username=sa
changelog-file=database/changelog/changelog.xml
search-path=/data
logLevel=info
EOF
done
echo -e "${GREEN}✓ Done${NC}"

# Create master changelog
echo -n "Creating master changelog... "
cat > "$LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog/changelog.xml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-latest.xsd">

    <!-- Baseline from existing database -->
    <include file="database/changelog/baseline/V0000__baseline.mssql.sql" />

    <!-- Incremental changes -->
    <!-- <include file="database/changelog/changes/V0001__add_orders_table.sql" /> -->

</databaseChangeLog>
EOF
echo -e "${GREEN}✓ Done${NC}"

# Summary
echo
echo "========================================"
echo -e "${GREEN}Step 01 Complete${NC}"
echo "========================================"
echo "Data directory:  $LIQUIBASE_TUTORIAL_DATA_DIR"
echo "Properties:      $LIQUIBASE_TUTORIAL_DATA_DIR/env/"
echo "Changelogs:      $LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog/"
echo
echo "Next: Run step02_start_containers.sh"

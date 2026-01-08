#!/usr/bin/env bash
# Tutorial Setup Script - Step 05: Generate Baseline
# Generates baseline changelog from development database using Liquibase

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TUTORIAL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCKER_DIR="$TUTORIAL_ROOT/docker"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "Liquibase Tutorial - Step 05: Generate Baseline"
echo "========================================"
echo

LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"
export LIQUIBASE_TUTORIAL_DATA_DIR

if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
    echo -e "${RED}ERROR: MSSQL_LIQUIBASE_TUTORIAL_PWD not set${NC}"
    exit 1
fi
export MSSQL_LIQUIBASE_TUTORIAL_PWD

# Detect container runtime
if command -v podman &>/dev/null; then
    CR_CMD="podman"
else
    CR_CMD="docker"
fi

echo "Generating baseline from mssql_dev..."
echo

# Run Liquibase generateChangeLog
$CR_CMD run --rm \
    --network slirp4netns:port_handler=slirp4netns \
    -v "${LIQUIBASE_TUTORIAL_DATA_DIR}:/data:z,U" \
    liquibase:latest \
    --url="jdbc:sqlserver://host.containers.internal:14331;databaseName=orderdb;encrypt=true;trustServerCertificate=true" \
    --username=sa \
    --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
    --changelog-file=/data/database/changelog/baseline/V0000__baseline.mssql.sql \
    --schemas=app \
    --overwrite-output-file=true \
    generateChangeLog 2>&1

# Verify baseline was created
if [[ -f "$LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog/baseline/V0000__baseline.mssql.sql" ]]; then
    echo
    echo "========================================"
    echo -e "${GREEN}Step 05 Complete${NC}"
    echo "========================================"
    echo "Baseline generated at:"
    echo "  $LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog/baseline/V0000__baseline.mssql.sql"
    echo
    echo "Preview (first 20 lines):"
    head -20 "$LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog/baseline/V0000__baseline.mssql.sql"
    echo
    echo "Next: Run step06_deploy_baseline.sh"
else
    echo -e "${RED}✗ Failed to generate baseline${NC}"
    exit 1
fi

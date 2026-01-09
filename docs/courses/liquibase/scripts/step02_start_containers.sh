#!/usr/bin/env bash
# Tutorial Setup Script - Step 02: Start Containers
# Starts all SQL Server containers for dev, stg, prd environments

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TUTORIAL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCKER_DIR="$TUTORIAL_ROOT/docker"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "Liquibase Tutorial - Step 02: Start Containers"
echo "========================================"
echo

# Check required environment
# Note: docker-compose.yml has a fallback to /data/liquibase_tutorial, but we prefer per-user isolation
LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"
export LIQUIBASE_TUTORIAL_DATA_DIR

# Validate data directory doesn't use the generic fallback from docker-compose.yml
if [[ "$LIQUIBASE_TUTORIAL_DATA_DIR" == "/data/liquibase_tutorial" ]]; then
    echo -e "${YELLOW}WARNING: Using generic data directory (not per-user)${NC}"
    echo "For multi-user support, run step01_setup_environment.sh first"
    echo "or export LIQUIBASE_TUTORIAL_DATA_DIR=\"/data/\${USER}/liquibase_tutorial\""
    echo
fi

if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
    echo -e "${RED}ERROR: MSSQL_LIQUIBASE_TUTORIAL_PWD not set${NC}"
    echo "Run step01_setup_environment.sh first or export the password"
    exit 1
fi
export MSSQL_LIQUIBASE_TUTORIAL_PWD

# Detect container runtime
if command -v podman-compose &>/dev/null; then
    COMPOSE_CMD="podman-compose"
    CR_CMD="podman"
elif command -v ~/.local/bin/podman-compose &>/dev/null; then
    COMPOSE_CMD="$HOME/.local/bin/podman-compose"
    CR_CMD="podman"
elif command -v docker &>/dev/null && docker compose version &>/dev/null; then
    COMPOSE_CMD="docker compose"
    CR_CMD="docker"
elif command -v docker-compose &>/dev/null; then
    COMPOSE_CMD="docker-compose"
    CR_CMD="docker"
else
    echo -e "${RED}ERROR: No container compose tool found${NC}"
    exit 1
fi

echo "Using: $COMPOSE_CMD"
echo "Data directory: $LIQUIBASE_TUTORIAL_DATA_DIR"
echo

# Start containers
echo "Starting SQL Server containers..."
cd "$DOCKER_DIR"
$COMPOSE_CMD up -d mssql_dev mssql_stg mssql_prd 2>&1

# Wait for health checks
echo
echo "Waiting for containers to become healthy..."
for i in {1..30}; do
    healthy_count=$($CR_CMD ps --filter "health=healthy" --format "{{.Names}}" 2>/dev/null | grep -c "mssql_" || true)
    if [[ "$healthy_count" -eq 3 ]]; then
        echo -e "${GREEN}All containers healthy!${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Show status
echo
echo "Container Status:"
$CR_CMD ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null | grep -E "NAMES|mssql_"

echo
echo "========================================"
echo -e "${GREEN}Step 02 Complete${NC}"
echo "========================================"
echo "Containers running on ports:"
echo "  mssql_dev: localhost:14331"
echo "  mssql_stg: localhost:14332"
echo "  mssql_prd: localhost:14333"
echo
echo "Next: Run step03_create_databases.sh"

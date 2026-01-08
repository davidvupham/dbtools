#!/usr/bin/env bash
# Tutorial Cleanup Script
# Removes all containers, volumes, and data created by the tutorial

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TUTORIAL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "Liquibase Tutorial - Cleanup"
echo "========================================"
echo

LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"

echo -e "${YELLOW}WARNING: This will remove all tutorial containers and data!${NC}"
echo "Data directory: $LIQUIBASE_TUTORIAL_DATA_DIR"
echo
read -p "Are you sure? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo

# Stop and remove containers
echo "Stopping and removing containers..."
for container in mssql_dev mssql_stg mssql_prd liquibase_tutorial; do
    if podman ps -a --format "{{.Names}}" | grep -q "^${container}$"; then
        podman rm -f "$container" 2>/dev/null && echo "  Removed: $container" || true
    fi
done

# Remove network
echo "Removing network..."
podman network rm liquibase_tutorial_network 2>/dev/null && echo "  Removed: liquibase_tutorial_network" || true

# Remove data directory
if [[ -d "$LIQUIBASE_TUTORIAL_DATA_DIR" ]]; then
    echo "Removing data directory..."
    if rm -rf "$LIQUIBASE_TUTORIAL_DATA_DIR" 2>/dev/null; then
        echo "  Removed: $LIQUIBASE_TUTORIAL_DATA_DIR"
    else
        echo "  Using sudo..."
        sudo rm -rf "$LIQUIBASE_TUTORIAL_DATA_DIR"
        echo "  Removed: $LIQUIBASE_TUTORIAL_DATA_DIR"
    fi
fi

echo
echo "========================================"
echo -e "${GREEN}Cleanup Complete${NC}"
echo "========================================"
echo "All tutorial resources have been removed."

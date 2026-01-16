#!/usr/bin/env bash
# Tutorial Cleanup Script
# Removes all containers, volumes, and data created by the tutorial
# This is the FULL cleanup - use cleanup_validation.sh for container-only cleanup

set -euo pipefail

# Parse arguments
FORCE=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        -f|--force)
            FORCE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [-f|--force]"
            echo "  -f, --force    Skip confirmation prompt"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TUTORIAL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Detect container runtime (podman or docker)
if command -v podman &>/dev/null; then
    CR_CMD="podman"
elif command -v docker &>/dev/null; then
    CR_CMD="docker"
else
    echo -e "${RED}ERROR: Neither podman nor docker found${NC}"
    exit 1
fi

echo "========================================"
echo "Liquibase Tutorial - Full Cleanup"
echo "========================================"
echo
echo "Container runtime: $CR_CMD"

LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"

echo -e "${YELLOW}WARNING: This will remove all tutorial containers AND data!${NC}"
echo "Data directory: $LIQUIBASE_TUTORIAL_DATA_DIR"
echo

if [[ "$FORCE" != "true" ]]; then
    read -p "Are you sure? (y/N): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "Cleanup cancelled."
        exit 0
    fi
fi

echo

# Stop and remove containers
echo "Stopping and removing containers..."
for container in mssql_dev mssql_stg mssql_prd liquibase_tutorial; do
    if $CR_CMD ps -a --format "{{.Names}}" 2>/dev/null | grep -q "^${container}$"; then
        $CR_CMD rm -f "$container" 2>/dev/null && echo "  Removed: $container" || true
    fi
done

# Remove network
echo "Removing network..."
$CR_CMD network rm liquibase_tutorial_network 2>/dev/null && echo "  Removed: liquibase_tutorial_network" || true

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

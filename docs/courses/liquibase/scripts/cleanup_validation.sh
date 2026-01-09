#!/bin/bash
# Cleanup script for validation runs
# Stops and removes all containers, networks, and cleans up ports

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TUTORIAL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCKER_DIR="$TUTORIAL_DIR/docker"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Validation Cleanup Script${NC}"
echo -e "${YELLOW}========================================${NC}"
echo

# Set password for docker-compose (required even for down)
export MSSQL_LIQUIBASE_TUTORIAL_PWD="${MSSQL_LIQUIBASE_TUTORIAL_PWD:-TestPassword123!}"

# Step 1: Stop and remove containers via docker-compose
echo -e "${YELLOW}Step 1: Stopping containers via docker-compose...${NC}"
if [ -f "$DOCKER_DIR/docker-compose.yml" ]; then
    cd "$DOCKER_DIR"
    docker compose down -v 2>&1 || true
    echo -e "${GREEN}✓ Docker compose cleanup complete${NC}"
else
    echo -e "${YELLOW}⚠ docker-compose.yml not found${NC}"
fi

# Step 2: Remove any remaining mssql containers
echo
echo -e "${YELLOW}Step 2: Removing any remaining mssql containers...${NC}"
CONTAINERS=$(docker ps -a --filter "name=mssql_" --format "{{.Names}}" 2>/dev/null || true)
if [ -n "$CONTAINERS" ]; then
    echo "$CONTAINERS" | xargs -r docker rm -f 2>&1 || true
    echo -e "${GREEN}✓ Removed remaining containers${NC}"
else
    echo -e "${GREEN}✓ No containers to remove${NC}"
fi

# Step 3: Remove any remaining liquibase containers
echo
echo -e "${YELLOW}Step 3: Removing any remaining liquibase containers...${NC}"
CONTAINERS=$(docker ps -a --filter "name=liquibase" --format "{{.Names}}" 2>/dev/null || true)
if [ -n "$CONTAINERS" ]; then
    echo "$CONTAINERS" | xargs -r docker rm -f 2>&1 || true
    echo -e "${GREEN}✓ Removed remaining containers${NC}"
else
    echo -e "${GREEN}✓ No containers to remove${NC}"
fi

# Step 4: Remove networks
echo
echo -e "${YELLOW}Step 4: Removing networks...${NC}"
NETWORKS=$(docker network ls --filter "name=liquibase" --filter "name=docker_default" --format "{{.ID}}" 2>/dev/null || true)
if [ -n "$NETWORKS" ]; then
    echo "$NETWORKS" | xargs -r docker network rm 2>&1 || true
    echo -e "${GREEN}✓ Removed networks${NC}"
else
    echo -e "${GREEN}✓ No networks to remove${NC}"
fi

# Step 5: Wait for ports to be released
echo
echo -e "${YELLOW}Step 5: Waiting for ports to be released...${NC}"
for port in 14331 14332 14333; do
    for i in {1..10}; do
        if ! netstat -tuln 2>/dev/null | grep -q ":$port " && ! ss -tuln 2>/dev/null | grep -q ":$port "; then
            echo -e "${GREEN}✓ Port $port is free${NC}"
            break
        fi
        if [ $i -eq 10 ]; then
            echo -e "${YELLOW}⚠ Port $port may still be in use (TIME_WAIT state)${NC}"
        else
            sleep 1
        fi
    done
done

# Step 6: Clean up validation log files (optional)
# Check if running non-interactively (stdin not a TTY or CI environment)
if [ ! -t 0 ] || [ -n "${CI:-}" ] || [ -n "${NON_INTERACTIVE:-}" ]; then
    # Non-interactive mode: keep log files by default
    echo -e "${YELLOW}⚠ Running non-interactively, keeping validation log files${NC}"
else
    # Interactive mode: prompt user
    echo
    read -p "Remove validation log files? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f "$TUTORIAL_DIR"/tutorial_validation_*.log 2>/dev/null || true
        rm -f "$TUTORIAL_DIR"/tutorial_validation_report_*.md 2>/dev/null || true
        echo -e "${GREEN}✓ Removed validation log files${NC}"
    else
        echo -e "${YELLOW}⚠ Keeping validation log files${NC}"
    fi
fi

echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cleanup Complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo
echo "Current state:"
echo "  Containers: $(docker ps -a --format '{{.Names}}' | wc -l) total"
echo "  Networks: $(docker network ls --format '{{.Name}}' | wc -l) total"
echo
echo "You can now run a fresh validation."

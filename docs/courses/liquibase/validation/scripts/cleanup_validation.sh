#!/bin/bash
# Cleanup script for validation runs
# Stops and removes all containers, networks, images, and cleans up ports

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

# Detect container runtime (podman or docker)
if command -v podman &>/dev/null; then
    CR_CMD="podman"
elif command -v docker &>/dev/null; then
    CR_CMD="docker"
else
    echo -e "${RED}ERROR: Neither podman nor docker found${NC}"
    exit 1
fi

# Set password for docker-compose (required even for down)
export MSSQL_LIQUIBASE_TUTORIAL_PWD="${MSSQL_LIQUIBASE_TUTORIAL_PWD:-TestPassword123!}"

# Step 1: Stop and remove containers via docker-compose
echo -e "${YELLOW}Step 1: Stopping containers via docker-compose...${NC}"
if [ -f "$DOCKER_DIR/docker-compose.yml" ]; then
    cd "$DOCKER_DIR"
    if [[ "$CR_CMD" == "podman" ]]; then
        # Try podman-compose if available
        if command -v podman-compose &>/dev/null || command -v ~/.local/bin/podman-compose &>/dev/null; then
            COMPOSE_CMD="${HOME}/.local/bin/podman-compose"
            [ -x "$COMPOSE_CMD" ] || COMPOSE_CMD="podman-compose"
            $COMPOSE_CMD down -v 2>&1 || true
        else
            echo -e "${YELLOW}⚠ podman-compose not found, skipping compose cleanup${NC}"
        fi
    else
        $CR_CMD compose down -v 2>&1 || true
    fi
    echo -e "${GREEN}✓ Docker compose cleanup complete${NC}"
else
    echo -e "${YELLOW}⚠ docker-compose.yml not found${NC}"
fi

# Step 2: Remove any remaining mssql containers
echo
echo -e "${YELLOW}Step 2: Removing any remaining mssql containers...${NC}"
CONTAINERS=$($CR_CMD ps -a --filter "name=mssql_" --format "{{.Names}}" 2>/dev/null || true)
if [ -n "$CONTAINERS" ]; then
    echo "$CONTAINERS" | xargs -r $CR_CMD rm -f 2>&1 || true
    echo -e "${GREEN}✓ Removed remaining containers${NC}"
else
    echo -e "${GREEN}✓ No containers to remove${NC}"
fi

# Step 3: Remove any remaining liquibase containers
echo
echo -e "${YELLOW}Step 3: Removing any remaining liquibase containers...${NC}"
CONTAINERS=$($CR_CMD ps -a --filter "name=liquibase" --format "{{.Names}}" 2>/dev/null || true)
if [ -n "$CONTAINERS" ]; then
    echo "$CONTAINERS" | xargs -r $CR_CMD rm -f 2>&1 || true
    echo -e "${GREEN}✓ Removed remaining containers${NC}"
else
    echo -e "${GREEN}✓ No containers to remove${NC}"
fi

# Step 4: Remove networks
echo
echo -e "${YELLOW}Step 4: Removing networks...${NC}"
NETWORKS=$($CR_CMD network ls --filter "name=liquibase" --filter "name=docker_default" --format "{{.ID}}" 2>/dev/null || true)
if [ -n "$NETWORKS" ]; then
    echo "$NETWORKS" | xargs -r $CR_CMD network rm 2>&1 || true
    echo -e "${GREEN}✓ Removed networks${NC}"
else
    echo -e "${GREEN}✓ No networks to remove${NC}"
fi

# Step 5: Remove tutorial images
echo
echo -e "${YELLOW}Step 5: Removing tutorial images...${NC}"
TUTORIAL_IMAGES=("mssql_tutorial:latest" "liquibase:latest")
REMOVED_COUNT=0
for image in "${TUTORIAL_IMAGES[@]}"; do
    if $CR_CMD image exists "$image" 2>/dev/null; then
        $CR_CMD rmi "$image" 2>&1 || true
        echo -e "${GREEN}✓ Removed image: $image${NC}"
        REMOVED_COUNT=$((REMOVED_COUNT + 1))
    fi
done
if [ $REMOVED_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ No tutorial images to remove${NC}"
fi

# Step 6: Wait for ports to be released
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

# Step 7: Clean up validation log files (optional)
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
echo "  Containers: $($CR_CMD ps -a --format '{{.Names}}' 2>/dev/null | wc -l) total"
echo "  Networks: $($CR_CMD network ls --format '{{.Name}}' 2>/dev/null | wc -l) total"
echo "  Images: $($CR_CMD images --format '{{.Repository}}:{{.Tag}}' 2>/dev/null | wc -l) total"
echo
echo "You can now run a fresh validation."

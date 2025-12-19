#!/bin/bash
# cleanup_liquibase_tutorial.sh
# Clean up MSSQL Docker container and all tutorial files used in the Liquibase tutorial
# This script safely removes all resources created during the tutorial

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="mssql_liquibase_tutorial"
VOLUME_NAME="mssql_liquibase_tutorial_data"
NETWORK_NAME="liquibase_tutorial"
# Respect LB_PROJECT_DIR if set; fallback to default path
TUTORIAL_DIR="${LB_PROJECT_DIR:-/data/liquibase-tutorial}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_LIQUIBASE_TUTORIAL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DOCKER_COMPOSE_DIR="${LIQUIBASE_TUTORIAL_DIR:-${DEFAULT_LIQUIBASE_TUTORIAL_DIR}}/docker"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Liquibase Tutorial Cleanup Script${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Function to check if container exists
container_exists() {
    docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"
}

# Function to check if volume exists
volume_exists() {
    docker volume ls --format '{{.Name}}' | grep -q "^${VOLUME_NAME}$"
}

# Function to check if network exists
network_exists() {
    docker network ls --format '{{.Name}}' | grep -q "^${NETWORK_NAME}$"
}

# 1. Stop and remove the MSSQL container
echo -e "\n${YELLOW}Step 1: Stopping and removing MSSQL container${NC}"
if container_exists; then
    echo "  Stopping container: ${CONTAINER_NAME}"
    docker stop "${CONTAINER_NAME}" 2>/dev/null || true
    echo "  Removing container: ${CONTAINER_NAME}"
    docker rm "${CONTAINER_NAME}" 2>/dev/null || true
    print_status "Container removed"
else
    print_warning "Container '${CONTAINER_NAME}' not found (already removed)"
fi

# 2. Remove the Docker volume
echo -e "\n${YELLOW}Step 2: Removing Docker volume${NC}"
if volume_exists; then
    echo "  Removing volume: ${VOLUME_NAME}"
    docker volume rm "${VOLUME_NAME}" 2>/dev/null || true
    print_status "Volume removed"
else
    print_warning "Volume '${VOLUME_NAME}' not found (already removed)"
fi

# 3. Remove the Docker network
echo -e "\n${YELLOW}Step 3: Removing Docker network${NC}"
if network_exists; then
    echo "  Removing network: ${NETWORK_NAME}"
    docker network rm "${NETWORK_NAME}" 2>/dev/null || true
    print_status "Network removed"
else
    print_warning "Network '${NETWORK_NAME}' not found (already removed)"
fi

# 4. Remove tutorial directory
echo -e "\n${YELLOW}Step 4: Removing tutorial directory${NC}"
if [ -d "${TUTORIAL_DIR}" ]; then
    echo "  Removing directory: ${TUTORIAL_DIR}"
    read -p "  This will delete all files in ${TUTORIAL_DIR}. Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "${TUTORIAL_DIR}"
        print_status "Tutorial directory removed"
    else
        print_warning "Skipped directory removal (user cancelled)"
    fi
else
    print_warning "Tutorial directory '${TUTORIAL_DIR}' not found (already removed)"
fi

# 5. Summary
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Cleanup Summary${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "The following resources have been cleaned up:"
echo "  - Container: ${CONTAINER_NAME}"
echo "  - Volume: ${VOLUME_NAME}"
echo "  - Network: ${NETWORK_NAME}"
echo "  - Directory: ${TUTORIAL_DIR} (if confirmed)"
echo ""
echo -e "${YELLOW}Note:${NC} Docker images are NOT removed by this script."
echo "To view images:"
echo "  docker images | grep -E 'liquibase|mssql'"
echo ""
echo "To remove images (optional):"
echo "  docker rmi liquibase:latest"
echo "  docker rmi mcr.microsoft.com/mssql/server:2025-latest"
echo ""
print_status "Cleanup complete!"

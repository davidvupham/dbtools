#!/usr/bin/env bash
# Start MSSQL Containers
# Starts all SQL Server containers for dev, stg, prd environments
# Reusable across all tutorial parts

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
echo "Liquibase Tutorial - Start MSSQL Containers"
echo "========================================"
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

# Check for existing containers and warn
EXISTING=$($CR_CMD ps -a --filter "name=mssql_" --format "{{.Names}}" 2>/dev/null | wc -l)
if [ "$EXISTING" -gt 0 ]; then
    echo -e "${YELLOW}Warning: Found existing mssql containers${NC}"
    echo "If you encounter port conflicts, run cleanup first:"
    echo "  $TUTORIAL_ROOT/validation/scripts/cleanup_validation.sh"
    echo
fi

# Check required environment
# Note: docker-compose.yml has a fallback to /data/liquibase_tutorial, but we prefer per-user isolation
LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"
export LIQUIBASE_TUTORIAL_DATA_DIR

# Validate data directory doesn't use the generic fallback from docker-compose.yml
if [[ "$LIQUIBASE_TUTORIAL_DATA_DIR" == "/data/liquibase_tutorial" ]]; then
    echo -e "${YELLOW}WARNING: Using generic data directory (not per-user)${NC}"
    echo "For multi-user support, run setup_liquibase_environment.sh first"
    echo "or export LIQUIBASE_TUTORIAL_DATA_DIR=\"/data/\${USER}/liquibase_tutorial\""
    echo
fi

if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
    echo -e "${RED}ERROR: MSSQL_LIQUIBASE_TUTORIAL_PWD not set${NC}"
    echo "Run setup_liquibase_environment.sh first or export the password"
    exit 1
fi
export MSSQL_LIQUIBASE_TUTORIAL_PWD

# Detect OS to determine if we should use podman run directly (for RHEL/WSL2)
USE_PODMAN_RUN=false
if [[ -f /etc/os-release ]]; then
    source /etc/os-release
    # Check for RHEL, CentOS, Fedora, Rocky, AlmaLinux
    if [[ "$ID" == "rhel" ]] || [[ "$ID" == "centos" ]] || [[ "$ID" == "fedora" ]] || \
       [[ "$ID" == "rocky" ]] || [[ "$ID" == "almalinux" ]] || \
       [[ "$ID_LIKE" =~ (rhel|centos|fedora|rocky|almalinux) ]]; then
        if [[ "$CR_CMD" == "podman" ]]; then
            USE_PODMAN_RUN=true
            echo -e "${YELLOW}Detected RHEL/CentOS/Fedora with Podman - using podman run directly${NC}"
            echo "This avoids podman-compose networking issues in WSL2"
            echo
        fi
    fi
fi

# Build SQL Server image if it doesn't exist
MSSQL_IMAGE="mssql_tutorial:latest"
if ! $CR_CMD image exists "$MSSQL_IMAGE" 2>/dev/null; then
    echo "Building SQL Server image..."
    cd "$DOCKER_DIR"
    # Use docker format for Podman to support HEALTHCHECK instruction
    if [[ "$CR_CMD" == "podman" ]]; then
        $CR_CMD build --format docker -t "$MSSQL_IMAGE" -f ../../../../docker/mssql/Dockerfile ../../../../docker/mssql
    else
        $CR_CMD build -t "$MSSQL_IMAGE" -f ../../../../docker/mssql/Dockerfile ../../../../docker/mssql
    fi
    echo
fi

echo "Data directory: $LIQUIBASE_TUTORIAL_DATA_DIR"
echo

# Start containers
echo "Starting SQL Server containers..."

if [[ "$USE_PODMAN_RUN" == "true" ]]; then
    # Use podman run directly for RHEL/WSL2
    mkdir -p "$LIQUIBASE_TUTORIAL_DATA_DIR/mssql_dev" \
             "$LIQUIBASE_TUTORIAL_DATA_DIR/mssql_stg" \
             "$LIQUIBASE_TUTORIAL_DATA_DIR/mssql_prd"
    
    # Remove existing containers if they exist
    $CR_CMD rm -f mssql_dev mssql_stg mssql_prd 2>/dev/null || true
    
    # Start dev container
    echo "Starting mssql_dev on port 14331..."
    $CR_CMD run -d --name mssql_dev \
        --hostname mssql_dev \
        -p 14331:1433 \
        -e ACCEPT_EULA=Y \
        -e MSSQL_SA_PASSWORD="$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
        -e MSSQL_PID=Developer \
        -v "$LIQUIBASE_TUTORIAL_DATA_DIR/mssql_dev:/var/opt/mssql:Z,U" \
        "$MSSQL_IMAGE" 2>&1
    
    # Start staging container
    echo "Starting mssql_stg on port 14332..."
    $CR_CMD run -d --name mssql_stg \
        --hostname mssql_stg \
        -p 14332:1433 \
        -e ACCEPT_EULA=Y \
        -e MSSQL_SA_PASSWORD="$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
        -e MSSQL_PID=Developer \
        -v "$LIQUIBASE_TUTORIAL_DATA_DIR/mssql_stg:/var/opt/mssql:Z,U" \
        "$MSSQL_IMAGE" 2>&1
    
    # Start production container
    echo "Starting mssql_prd on port 14333..."
    $CR_CMD run -d --name mssql_prd \
        --hostname mssql_prd \
        -p 14333:1433 \
        -e ACCEPT_EULA=Y \
        -e MSSQL_SA_PASSWORD="$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
        -e MSSQL_PID=Developer \
        -v "$LIQUIBASE_TUTORIAL_DATA_DIR/mssql_prd:/var/opt/mssql:Z,U" \
        "$MSSQL_IMAGE" 2>&1
else
    # Use compose for other platforms
    # Detect container compose tool
    if command -v podman-compose &>/dev/null; then
        COMPOSE_CMD="podman-compose"
    elif command -v ~/.local/bin/podman-compose &>/dev/null; then
        COMPOSE_CMD="$HOME/.local/bin/podman-compose"
    elif command -v docker &>/dev/null && docker compose version &>/dev/null; then
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &>/dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        echo -e "${RED}ERROR: No container compose tool found${NC}"
        exit 1
    fi
    
    echo "Using: $COMPOSE_CMD"
    cd "$DOCKER_DIR"
    $COMPOSE_CMD up -d mssql_dev mssql_stg mssql_prd 2>&1
fi

# Wait for containers to be ready
echo
echo "Waiting for SQL Server to be ready..."
if [[ "$USE_PODMAN_RUN" == "true" ]]; then
    # For podman run, wait for SQL Server to accept connections
    for container in mssql_dev mssql_stg mssql_prd; do
        echo -n "Waiting for $container to be ready..."
        for i in {1..30}; do
            if $CR_CMD exec "$container" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
                -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" -Q "SELECT 1" -b -o /dev/null 2>/dev/null; then
                echo -e " ${GREEN}✓ Ready${NC}"
                break
            fi
            if [[ $i -eq 30 ]]; then
                echo -e " ${YELLOW}⚠ Timeout (SQL Server may still be starting)${NC}"
            else
                echo -n "."
                sleep 2
            fi
        done
    done
else
    # For compose, use health check status
    for i in {1..30}; do
        healthy_count=$($CR_CMD ps --filter "health=healthy" --format "{{.Names}}" 2>/dev/null | grep -c "mssql_" || true)
        if [[ "$healthy_count" -eq 3 ]]; then
            echo -e "${GREEN}All containers healthy!${NC}"
            break
        fi
        echo -n "."
        sleep 2
    done
fi

# Show status
echo
echo "Container Status:"
$CR_CMD ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null | grep -E "NAMES|mssql_"

echo
echo "========================================"
echo -e "${GREEN}Containers Started${NC}"
echo "========================================"
echo "Containers running on ports:"
echo "  mssql_dev: localhost:14331"
echo "  mssql_stg: localhost:14332"
echo "  mssql_prd: localhost:14333"
echo
echo "Next: Run create_orderdb_databases.sh"

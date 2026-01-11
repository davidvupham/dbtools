#!/usr/bin/env bash
# Start MSSQL Containers
# Starts all SQL Server containers for dev, stg, prd environments
# Reusable across all tutorial parts
#
# Multi-user support:
# - Dynamically configures available ports starting from 14331
# - Saves assigned ports to $LIQUIBASE_TUTORIAL_DATA_DIR/.ports
# - Other scripts source this file to discover the correct ports

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TUTORIAL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCKER_DIR="$TUTORIAL_ROOT/docker"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# =============================================================================
# Port Management Functions
# =============================================================================

# Check if a port is available
is_port_available() {
    local port=$1
    
    # Check if container runtime is using this port
    if command -v podman &>/dev/null; then
        if podman ps --format '{{.Ports}}' 2>/dev/null | grep -q "0.0.0.0:${port}->"; then
            return 1
        fi
    fi
    if command -v docker &>/dev/null; then
        if docker ps --format '{{.Ports}}' 2>/dev/null | grep -q "0.0.0.0:${port}->"; then
            return 1
        fi
    fi
    
    # Check using ss (most common on Linux)
    if command -v ss &>/dev/null; then
        if ss -tuln 2>/dev/null | grep -q ":${port} "; then
            return 1
        fi
    # Fallback to netstat
    elif command -v netstat &>/dev/null; then
        if netstat -tuln 2>/dev/null | grep -q ":${port} "; then
            return 1
        fi
    # Fallback to lsof
    elif command -v lsof &>/dev/null; then
        if lsof -i":${port}" -sTCP:LISTEN -t >/dev/null 2>&1; then
            return 1
        fi
    fi
    
    return 0
}

# Find N consecutive available ports starting from a base port
# Usage: find_available_ports <start_port> <count>
# Returns: space-separated list of available ports
find_available_ports() {
    local start_port=${1:-14331}
    local count=${2:-3}
    local max_attempts=100
    local port=$start_port
    local found_ports=()
    
    for ((attempt=0; attempt<max_attempts; attempt++)); do
        found_ports=()
        local all_available=true
        
        # Check if 'count' consecutive ports are available
        for ((i=0; i<count; i++)); do
            local check_port=$((port + i))
            if is_port_available "$check_port"; then
                found_ports+=("$check_port")
            else
                all_available=false
                # Skip to the next port after the unavailable one
                port=$((check_port + 1))
                break
            fi
        done
        
        if [[ "$all_available" == "true" ]]; then
            echo "${found_ports[*]}"
            return 0
        fi
    done
    
    echo "ERROR: Could not find $count consecutive available ports after $max_attempts attempts" >&2
    return 1
}

# write_ports_file function is now in setup_db_container_ports.sh and will be available after sourcing

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

# =============================================================================
# Determine Ports to Use
# =============================================================================

# Default ports (used as fallback)
MSSQL_DEV_PORT=${MSSQL_DEV_PORT:-14331}
MSSQL_STG_PORT=${MSSQL_STG_PORT:-14332}
MSSQL_PRD_PORT=${MSSQL_PRD_PORT:-14333}

# Source the port setup script to get write_ports_file function
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETUP_PORTS_SCRIPT="$SCRIPT_DIR/setup_db_container_ports.sh"

# Source setup_db_container_ports.sh to get write_ports_file function (even if not using dynamic ports)
if [[ -f "$SETUP_PORTS_SCRIPT" ]]; then
    source "$SETUP_PORTS_SCRIPT"
else
    echo -e "${YELLOW}WARNING: setup_db_container_ports.sh not found at $SETUP_PORTS_SCRIPT${NC}"
    # Define a fallback write_ports_file function (matches new multi-platform signature)
    write_ports_file() {
        local platform=$1
        shift
        local container_port_map=("$@")
        local ports_file="$LIQUIBASE_TUTORIAL_DATA_DIR/.ports"
        local ports_content="# Auto-generated by start_mssql_containers.sh
# Source this file to get the port assignments for this user's tutorial environment
# Platform: ${platform}
"
        # Extract ports from container:port pairs
        for entry in "${container_port_map[@]}"; do
            local container="${entry%%:*}"
            local port="${entry#*:}"
            # Convert container name to var name (mssql_dev -> MSSQL_DEV_PORT)
            local var_name=$(echo "${container}" | tr '[:lower:]' '[:upper:]')_PORT
            ports_content+="${var_name}=${port}"$'\n'
        done
        
        if echo "$ports_content" > "$ports_file" 2>/dev/null; then
            echo -e "${GREEN}✓ Saved port assignments to $ports_file${NC}"
        elif sudo bash -c "cat > '$ports_file' && chown $USER:$USER '$ports_file'" <<< "$ports_content" 2>/dev/null; then
            echo -e "${GREEN}✓ Saved port assignments to $ports_file (using sudo)${NC}"
        else
            echo -e "${YELLOW}⚠ Could not write port assignments to $ports_file${NC}"
        fi
    }
fi

# For Podman on RHEL (shared host), setup available ports dynamically
if [[ "$USE_PODMAN_RUN" == "true" ]]; then
    # Use setup_mssql_ports function from setup_db_container_ports.sh
    setup_mssql_ports 14331 false false || {
        echo -e "${RED}ERROR: Failed to setup ports${NC}"
        exit 1
    }
    # Ports are now exported from setup_mssql_ports
else
    # For Docker/WSL2, check if ports file exists and use it, otherwise use defaults
    PORTS_FILE="$LIQUIBASE_TUTORIAL_DATA_DIR/.ports"
    if [[ -f "$PORTS_FILE" ]]; then
        source "$PORTS_FILE"
        echo "Using ports from $PORTS_FILE: $MSSQL_DEV_PORT, $MSSQL_STG_PORT, $MSSQL_PRD_PORT"
    else
        echo "Using default ports: $MSSQL_DEV_PORT, $MSSQL_STG_PORT, $MSSQL_PRD_PORT"
        echo "  (Run $SETUP_PORTS_SCRIPT to configure available ports if these are in use)"
    fi
    export MSSQL_DEV_PORT MSSQL_STG_PORT MSSQL_PRD_PORT
fi
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
    echo "Starting mssql_dev on port $MSSQL_DEV_PORT..."
    $CR_CMD run -d --name mssql_dev \
        --hostname mssql_dev \
        --userns=keep-id \
        -p "${MSSQL_DEV_PORT}:1433" \
        -e ACCEPT_EULA=Y \
        -e MSSQL_SA_PASSWORD="$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
        -e MSSQL_PID=Developer \
        -v "$LIQUIBASE_TUTORIAL_DATA_DIR/mssql_dev:/var/opt/mssql:Z,U" \
        "$MSSQL_IMAGE" 2>&1
    
    # Start staging container
    echo "Starting mssql_stg on port $MSSQL_STG_PORT..."
    $CR_CMD run -d --name mssql_stg \
        --hostname mssql_stg \
        --userns=keep-id \
        -p "${MSSQL_STG_PORT}:1433" \
        -e ACCEPT_EULA=Y \
        -e MSSQL_SA_PASSWORD="$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
        -e MSSQL_PID=Developer \
        -v "$LIQUIBASE_TUTORIAL_DATA_DIR/mssql_stg:/var/opt/mssql:Z,U" \
        "$MSSQL_IMAGE" 2>&1
    
    # Start production container
    echo "Starting mssql_prd on port $MSSQL_PRD_PORT..."
    $CR_CMD run -d --name mssql_prd \
        --hostname mssql_prd \
        --userns=keep-id \
        -p "${MSSQL_PRD_PORT}:1433" \
        -e ACCEPT_EULA=Y \
        -e MSSQL_SA_PASSWORD="$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
        -e MSSQL_PID=Developer \
        -v "$LIQUIBASE_TUTORIAL_DATA_DIR/mssql_prd:/var/opt/mssql:Z,U" \
        "$MSSQL_IMAGE" 2>&1
    
    # Save port assignments for other scripts to discover
    write_ports_file "mssql" "mssql_dev:$MSSQL_DEV_PORT" "mssql_stg:$MSSQL_STG_PORT" "mssql_prd:$MSSQL_PRD_PORT"
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
    
    # Save port assignments for other scripts to discover
    write_ports_file "mssql" "mssql_dev:$MSSQL_DEV_PORT" "mssql_stg:$MSSQL_STG_PORT" "mssql_prd:$MSSQL_PRD_PORT"
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
echo "  mssql_dev: localhost:$MSSQL_DEV_PORT"
echo "  mssql_stg: localhost:$MSSQL_STG_PORT"
echo "  mssql_prd: localhost:$MSSQL_PRD_PORT"
echo
echo "Port assignments saved to: $LIQUIBASE_TUTORIAL_DATA_DIR/.ports"
echo "Other scripts will automatically discover these ports."
echo
echo "Next: Run create_orderdb_database.sh"

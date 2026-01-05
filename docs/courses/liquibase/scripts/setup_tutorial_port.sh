#!/bin/bash
# setup_tutorial_port.sh
# Finds an available port for the Liquibase tutorial SQL Server and sets it as an environment variable

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Liquibase Tutorial Port Setup${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# Function to check if a port is available
is_port_available() {
    local port=$1
    
    # Check if Docker is using this port
    if command -v docker &> /dev/null; then
        if docker ps --format '{{.Ports}}' 2>/dev/null | grep -q "0.0.0.0:${port}->"; then
            return 1  # Port is in use by Docker
        fi
    fi
    
    # Check using lsof if available (most reliable)
    if command -v lsof &> /dev/null; then
        ! lsof -i":${port}" -sTCP:LISTEN -t >/dev/null 2>&1
    # Check if port is in use using ss
    elif command -v ss &> /dev/null; then
        ! ss -tuln | grep -q ":${port} "
    # Check using netstat
    elif command -v netstat &> /dev/null; then
        ! netstat -tuln | grep -q ":${port} "
    else
        # Fallback: try to bind to the port
        ! timeout 1 bash -c "cat < /dev/null > /dev/tcp/127.0.0.1/${port}" 2>/dev/null
    fi
}

# Function to find an available port
find_available_port() {
    local start_port=${1:-14333}
    local max_attempts=100
    local port=$start_port
    
    echo "Searching for available port starting from ${start_port}..." >&2
    
    for ((i=0; i<max_attempts; i++)); do
        if is_port_available $port; then
            echo $port
            return 0
        fi
        echo "  Port ${port} is in use, trying next..." >&2
        ((port++))
    done
    
    # If no port found in range, return error
    return 1
}

# Check if we're running in bash
if [ -z "$BASH_VERSION" ]; then
    echo -e "${RED}Error: This script must be run with bash${NC}"
    exit 1
fi

# Default starting port (14333 to avoid conflict with default SQL Server port 1433)
DEFAULT_START_PORT=14333

# Check if user provided a starting port
START_PORT=${1:-$DEFAULT_START_PORT}

echo "Looking for available port (starting from ${START_PORT})..."
echo ""

# Find available port
AVAILABLE_PORT=$(find_available_port $START_PORT)

if [ $? -ne 0 ] || [ -z "$AVAILABLE_PORT" ]; then
    echo -e "${RED}Error: Could not find an available port after checking 100 ports starting from ${START_PORT}${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Found available port: ${AVAILABLE_PORT}${NC}"
echo ""

# Set the environment variable
export MSSQL_LIQUIBASE_TUTORIAL_PORT=$AVAILABLE_PORT

# Also add to current shell session (if sourced)
echo "MSSQL_LIQUIBASE_TUTORIAL_PORT=$AVAILABLE_PORT"

# Provide instructions for making it persistent
echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Port Configuration Complete${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo "Environment variable set:"
echo "  MSSQL_LIQUIBASE_TUTORIAL_PORT=${AVAILABLE_PORT}"
echo ""
echo -e "${YELLOW}To use this port in your current shell session, run:${NC}"
echo -e "  ${GREEN}export MSSQL_LIQUIBASE_TUTORIAL_PORT=${AVAILABLE_PORT}${NC}"
echo ""
echo -e "${YELLOW}Or source this script to set the variable automatically:${NC}"
echo -e "  ${GREEN}source $0${NC}"
echo ""
echo -e "${YELLOW}To make this persistent across sessions, add to your ~/.bashrc:${NC}"
echo -e "  ${GREEN}echo 'export MSSQL_LIQUIBASE_TUTORIAL_PORT=${AVAILABLE_PORT}' >> ~/.bashrc${NC}"
echo ""
echo "The SQL Server container will be accessible at: localhost:${AVAILABLE_PORT}"
echo ""

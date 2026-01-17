#!/bin/bash
#
# Container Course Environment Setup Script
# This script verifies and sets up the environment for the containers course
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Container Course Environment Setup        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Function to print status
print_status() {
    if [ "$1" = "ok" ]; then
        echo -e "  [${GREEN}✓${NC}] $2"
    elif [ "$1" = "warn" ]; then
        echo -e "  [${YELLOW}!${NC}] $2"
    else
        echo -e "  [${RED}✗${NC}] $2"
    fi
}

# Function to check command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to get version
get_version() {
    "$1" --version 2>/dev/null | head -n1 || echo "unknown"
}

echo -e "${BLUE}1. Checking Container Runtimes${NC}"
echo ""

# Check Docker
if command_exists docker; then
    docker_version=$(docker --version 2>/dev/null | cut -d' ' -f3 | tr -d ',')
    if docker info &>/dev/null; then
        print_status "ok" "Docker installed and running (version: $docker_version)"
        DOCKER_OK=true
    else
        print_status "warn" "Docker installed but not running or permission denied"
        DOCKER_OK=false
    fi
else
    print_status "warn" "Docker not installed"
    DOCKER_OK=false
fi

# Check Podman
if command_exists podman; then
    podman_version=$(podman --version 2>/dev/null | cut -d' ' -f3)
    if podman info &>/dev/null; then
        print_status "ok" "Podman installed and running (version: $podman_version)"
        PODMAN_OK=true
    else
        print_status "warn" "Podman installed but not accessible"
        PODMAN_OK=false
    fi
else
    print_status "warn" "Podman not installed"
    PODMAN_OK=false
fi

# At least one must be available
if [ "$DOCKER_OK" = true ] || [ "$PODMAN_OK" = true ]; then
    print_status "ok" "At least one container runtime is available"
else
    print_status "fail" "No container runtime available!"
    echo ""
    echo "Please install Docker or Podman:"
    echo "  Docker: https://docs.docker.com/get-docker/"
    echo "  Podman: https://podman.io/getting-started/installation"
    exit 1
fi

echo ""
echo -e "${BLUE}2. Checking Additional Tools${NC}"
echo ""

# Check curl
if command_exists curl; then
    print_status "ok" "curl available"
else
    print_status "warn" "curl not installed (some labs require it)"
fi

# Check git
if command_exists git; then
    print_status "ok" "git available"
else
    print_status "warn" "git not installed"
fi

# Check jq
if command_exists jq; then
    print_status "ok" "jq available (JSON processing)"
else
    print_status "warn" "jq not installed (optional, for JSON formatting)"
fi

echo ""
echo -e "${BLUE}3. Testing Container Functionality${NC}"
echo ""

# Test running a container
if [ "$DOCKER_OK" = true ]; then
    RUNTIME="docker"
elif [ "$PODMAN_OK" = true ]; then
    RUNTIME="podman"
fi

echo "Testing with: $RUNTIME"

# Pull and run hello-world
if $RUNTIME run --rm hello-world &>/dev/null; then
    print_status "ok" "Successfully ran test container"
else
    print_status "fail" "Failed to run test container"
fi

# Test port publishing
echo "Testing port publishing..."
$RUNTIME run -d --name test-nginx -p 18080:80 nginx:alpine &>/dev/null
sleep 2
if curl -s http://localhost:18080 &>/dev/null; then
    print_status "ok" "Port publishing works"
else
    print_status "warn" "Port publishing may have issues"
fi
$RUNTIME rm -f test-nginx &>/dev/null

# Test volume mounting
echo "Testing volume mounting..."
mkdir -p /tmp/container-test
echo "test" > /tmp/container-test/file.txt
if $RUNTIME run --rm -v /tmp/container-test:/data alpine cat /data/file.txt &>/dev/null; then
    print_status "ok" "Volume mounting works"
else
    print_status "warn" "Volume mounting may have issues"
fi
rm -rf /tmp/container-test

echo ""
echo -e "${BLUE}4. System Information${NC}"
echo ""

# OS Information
echo "  Operating System: $(uname -s) $(uname -r)"
echo "  Architecture: $(uname -m)"

# Memory
if command_exists free; then
    total_mem=$(free -h | awk '/^Mem:/{print $2}')
    echo "  Total Memory: $total_mem"
fi

# Disk space for Docker/Podman
if [ "$DOCKER_OK" = true ]; then
    docker_root=$(docker info 2>/dev/null | grep "Docker Root Dir" | awk '{print $NF}')
    if [ -n "$docker_root" ]; then
        disk_free=$(df -h "$docker_root" 2>/dev/null | awk 'NR==2{print $4}')
        echo "  Docker disk free: $disk_free"
    fi
fi

echo ""
echo -e "${BLUE}5. Recommendations${NC}"
echo ""

# Memory recommendation
if command_exists free; then
    total_mem_mb=$(free -m | awk '/^Mem:/{print $2}')
    if [ "$total_mem_mb" -lt 4096 ]; then
        print_status "warn" "Less than 4GB RAM - some exercises may be slow"
    else
        print_status "ok" "Sufficient memory available"
    fi
fi

# Docker group (Linux only)
if [ "$(uname -s)" = "Linux" ] && [ "$DOCKER_OK" = true ]; then
    if groups | grep -q docker; then
        print_status "ok" "User is in docker group"
    else
        print_status "warn" "User not in docker group - may need sudo"
        echo "         Run: sudo usermod -aG docker \$USER"
    fi
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo -e "${GREEN}Environment setup complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo ""
echo "You can now start the course at:"
echo "  docs/courses/containers/README.md"
echo ""
echo "Quick start:"
echo "  $RUNTIME run hello-world"
echo ""

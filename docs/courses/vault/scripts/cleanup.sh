#!/bin/bash
# HashiCorp Vault Course - Cleanup Script
#
# This script removes all course Docker containers and volumes.
#
# Usage:
#   ./cleanup.sh           # Stop and remove containers
#   ./cleanup.sh --all     # Also remove volumes (data loss!)

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="${SCRIPT_DIR}/../docker"
REMOVE_VOLUMES=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --all)
            REMOVE_VOLUMES=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--all]"
            echo ""
            echo "Options:"
            echo "  --all      Also remove Docker volumes (permanent data loss!)"
            echo "  --help     Show this help message"
            exit 0
            ;;
    esac
done

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

cleanup_dev_environment() {
    print_header "Cleaning Up Development Environment"

    cd "$DOCKER_DIR"

    if [ -f "docker-compose.dev.yml" ]; then
        echo "Stopping dev containers..."
        docker compose -f docker-compose.dev.yml down 2>/dev/null || true
        print_success "Dev containers stopped"

        if [ "$REMOVE_VOLUMES" = true ]; then
            echo "Removing dev volumes..."
            docker compose -f docker-compose.dev.yml down -v 2>/dev/null || true
            print_success "Dev volumes removed"
        fi
    fi
}

cleanup_ha_environment() {
    print_header "Cleaning Up HA Environment"

    cd "$DOCKER_DIR"

    if [ -f "docker-compose.ha.yml" ]; then
        echo "Stopping HA containers..."
        docker compose -f docker-compose.ha.yml down 2>/dev/null || true
        print_success "HA containers stopped"

        if [ "$REMOVE_VOLUMES" = true ]; then
            echo "Removing HA volumes..."
            docker compose -f docker-compose.ha.yml down -v 2>/dev/null || true
            print_success "HA volumes removed"
        fi
    fi
}

cleanup_orphan_containers() {
    print_header "Cleaning Up Orphan Containers"

    # Remove any vault-related containers that might be orphaned
    local containers=$(docker ps -a --filter "name=vault" --format "{{.Names}}" 2>/dev/null || true)

    if [ -n "$containers" ]; then
        echo "Found orphan containers: $containers"
        docker rm -f $containers 2>/dev/null || true
        print_success "Orphan containers removed"
    else
        print_success "No orphan containers found"
    fi
}

cleanup_networks() {
    print_header "Cleaning Up Networks"

    # Remove course-specific networks
    local networks="vault-network vault-cluster"

    for network in $networks; do
        if docker network ls --format "{{.Name}}" | grep -q "^${network}$"; then
            docker network rm "$network" 2>/dev/null || true
            print_success "Removed network: $network"
        fi
    done
}

print_summary() {
    print_header "Cleanup Complete!"

    echo -e "${GREEN}Removed:${NC}"
    echo "  - All course Docker containers"
    echo "  - Course Docker networks"

    if [ "$REMOVE_VOLUMES" = true ]; then
        echo "  - All course Docker volumes (data deleted)"
    else
        echo ""
        echo -e "${YELLOW}Note: Volumes were preserved. Use --all to remove them.${NC}"
    fi

    echo ""
    echo "To start fresh, run: ./setup-dev-environment.sh"
}

# Main execution
main() {
    print_header "Vault Course - Cleanup"

    if [ "$REMOVE_VOLUMES" = true ]; then
        print_warning "This will delete all course data including secrets!"
        echo ""
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Cancelled."
            exit 0
        fi
    fi

    cleanup_dev_environment
    cleanup_ha_environment
    cleanup_orphan_containers
    cleanup_networks
    print_summary
}

main "$@"

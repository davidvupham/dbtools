#!/bin/bash
# HashiCorp Vault Course - HA Cluster Setup
#
# This script sets up a 3-node Vault HA cluster for Module 4 Track C exercises.
#
# Usage:
#   ./setup-ha-cluster.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="${SCRIPT_DIR}/../docker"

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

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_prerequisites() {
    print_header "Checking Prerequisites"

    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_success "Docker is installed"

    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available"
        exit 1
    fi
    print_success "Docker Compose is available"
}

start_cluster() {
    print_header "Starting Vault HA Cluster"

    cd "$DOCKER_DIR"

    # Stop any existing containers
    docker compose -f docker-compose.ha.yml down 2>/dev/null || true

    # Start the cluster
    docker compose -f docker-compose.ha.yml up -d

    # Wait for containers to be running
    echo "Waiting for containers to start..."
    sleep 5
    print_success "Cluster containers started"
}

initialize_vault() {
    print_header "Initializing Vault Cluster"

    # Check if already initialized
    local status=$(docker exec vault-1 vault status -format=json 2>/dev/null | jq -r '.initialized' || echo "false")

    if [ "$status" = "true" ]; then
        print_warning "Vault is already initialized"
        return 0
    fi

    # Initialize Vault
    echo "Initializing Vault (this generates root keys)..."
    local init_output=$(docker exec vault-1 vault operator init -key-shares=1 -key-threshold=1 -format=json)

    # Extract keys
    UNSEAL_KEY=$(echo "$init_output" | jq -r '.unseal_keys_b64[0]')
    ROOT_TOKEN=$(echo "$init_output" | jq -r '.root_token')

    # Save keys to file
    echo "Unseal Key: $UNSEAL_KEY" > "${SCRIPT_DIR}/../.vault-keys"
    echo "Root Token: $ROOT_TOKEN" >> "${SCRIPT_DIR}/../.vault-keys"
    chmod 600 "${SCRIPT_DIR}/../.vault-keys"

    print_success "Vault initialized"
    print_warning "Keys saved to: ${SCRIPT_DIR}/../.vault-keys"
    echo ""
    echo "  Unseal Key: $UNSEAL_KEY"
    echo "  Root Token: $ROOT_TOKEN"
}

unseal_cluster() {
    print_header "Unsealing Vault Cluster"

    # Read unseal key
    if [ -f "${SCRIPT_DIR}/../.vault-keys" ]; then
        UNSEAL_KEY=$(grep "Unseal Key:" "${SCRIPT_DIR}/../.vault-keys" | cut -d' ' -f3)
    else
        print_error "No keys file found. Run initialization first."
        exit 1
    fi

    # Unseal vault-1
    echo "Unsealing vault-1..."
    docker exec vault-1 vault operator unseal "$UNSEAL_KEY"
    print_success "vault-1 unsealed"

    # Wait for raft to sync
    sleep 3

    # Unseal vault-2
    echo "Unsealing vault-2..."
    docker exec vault-2 vault operator unseal "$UNSEAL_KEY"
    print_success "vault-2 unsealed"

    # Unseal vault-3
    echo "Unsealing vault-3..."
    docker exec vault-3 vault operator unseal "$UNSEAL_KEY"
    print_success "vault-3 unsealed"
}

check_cluster_status() {
    print_header "Cluster Status"

    echo "vault-1:"
    docker exec vault-1 vault status 2>/dev/null || print_warning "vault-1 status unavailable"
    echo ""

    echo "vault-2:"
    docker exec vault-2 vault status 2>/dev/null || print_warning "vault-2 status unavailable"
    echo ""

    echo "vault-3:"
    docker exec vault-3 vault status 2>/dev/null || print_warning "vault-3 status unavailable"
}

show_raft_members() {
    print_header "Raft Cluster Members"

    if [ -f "${SCRIPT_DIR}/../.vault-keys" ]; then
        ROOT_TOKEN=$(grep "Root Token:" "${SCRIPT_DIR}/../.vault-keys" | cut -d' ' -f3)
        docker exec -e VAULT_TOKEN="$ROOT_TOKEN" vault-1 vault operator raft list-peers
    else
        print_warning "Cannot show raft members - no root token available"
    fi
}

print_summary() {
    print_header "HA Cluster Setup Complete!"

    echo -e "${GREEN}Cluster Nodes:${NC}"
    echo "  - vault-1: http://localhost:8200 (Active)"
    echo "  - vault-2: http://localhost:8202 (Standby)"
    echo "  - vault-3: http://localhost:8204 (Standby)"
    echo ""

    if [ -f "${SCRIPT_DIR}/../.vault-keys" ]; then
        ROOT_TOKEN=$(grep "Root Token:" "${SCRIPT_DIR}/../.vault-keys" | cut -d' ' -f3)
        echo -e "${GREEN}Environment Variables:${NC}"
        echo "  export VAULT_ADDR='http://localhost:8200'"
        echo "  export VAULT_TOKEN='$ROOT_TOKEN'"
    fi
    echo ""

    echo -e "${GREEN}PostgreSQL:${NC}"
    echo "  Host: localhost:5432"
    echo "  Database: appdb"
    echo "  User: postgres / Password: postgres"
    echo ""

    echo -e "${GREEN}Useful Commands:${NC}"
    echo "  vault operator raft list-peers     # Show cluster members"
    echo "  vault operator step-down           # Force leader election"
    echo "  docker exec vault-1 vault status   # Check node status"
}

# Main execution
main() {
    print_header "Vault Course - HA Cluster Setup"

    check_prerequisites
    start_cluster
    initialize_vault
    unseal_cluster
    check_cluster_status
    show_raft_members
    print_summary
}

main "$@"

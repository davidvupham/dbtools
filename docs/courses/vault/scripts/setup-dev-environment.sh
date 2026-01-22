#!/bin/bash
# HashiCorp Vault Course - Development Environment Setup
#
# This script sets up a complete Vault development environment for the course.
# It starts Vault in dev mode and configures common secrets engines and auth methods.
#
# Usage:
#   ./setup-dev-environment.sh
#   ./setup-dev-environment.sh --with-database  # Include PostgreSQL setup

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="${SCRIPT_DIR}/../docker"
VAULT_ADDR="${VAULT_ADDR:-http://localhost:8200}"
VAULT_TOKEN="${VAULT_TOKEN:-dev-root-token}"
WITH_DATABASE=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --with-database)
            WITH_DATABASE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--with-database]"
            echo ""
            echo "Options:"
            echo "  --with-database  Also start PostgreSQL for database secrets labs"
            echo "  --help, -h       Show this help message"
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

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_success "Docker is installed"

    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available"
        exit 1
    fi
    print_success "Docker Compose is available"

    # Check Vault CLI (optional)
    if command -v vault &> /dev/null; then
        print_success "Vault CLI is installed"
    else
        print_warning "Vault CLI not found - you can install it or use docker exec"
    fi
}

start_vault() {
    print_header "Starting Vault Development Server"

    cd "$DOCKER_DIR"

    # Check if already running
    if docker ps --format '{{.Names}}' | grep -q "^vault-dev$"; then
        print_warning "Vault container is already running"
        return 0
    fi

    # Start services
    if [ "$WITH_DATABASE" = true ]; then
        print_success "Starting Vault with PostgreSQL..."
        docker compose -f docker-compose.dev.yml up -d
    else
        print_success "Starting Vault only..."
        docker compose -f docker-compose.dev.yml up -d vault
    fi

    # Wait for Vault to be ready
    echo "Waiting for Vault to be ready..."
    for i in {1..30}; do
        if docker exec vault-dev vault status &> /dev/null; then
            print_success "Vault is ready!"
            break
        fi
        sleep 1
    done
}

configure_secrets_engines() {
    print_header "Configuring Secrets Engines"

    # Export for vault commands
    export VAULT_ADDR
    export VAULT_TOKEN

    # Enable KV v2 secrets engine at secret/
    echo "Enabling KV v2 at secret/..."
    docker exec -e VAULT_TOKEN="$VAULT_TOKEN" vault-dev \
        vault secrets enable -path=secret -version=2 kv 2>/dev/null || true
    print_success "KV v2 enabled at secret/"

    # Enable KV v1 for comparison exercises
    echo "Enabling KV v1 at kv-v1/..."
    docker exec -e VAULT_TOKEN="$VAULT_TOKEN" vault-dev \
        vault secrets enable -path=kv-v1 -version=1 kv 2>/dev/null || true
    print_success "KV v1 enabled at kv-v1/"

    # Enable Transit secrets engine
    echo "Enabling Transit at transit/..."
    docker exec -e VAULT_TOKEN="$VAULT_TOKEN" vault-dev \
        vault secrets enable transit 2>/dev/null || true
    print_success "Transit enabled at transit/"

    # Create a default encryption key
    docker exec -e VAULT_TOKEN="$VAULT_TOKEN" vault-dev \
        vault write -f transit/keys/my-app-key 2>/dev/null || true
    print_success "Created transit key: my-app-key"
}

configure_database_engine() {
    if [ "$WITH_DATABASE" = false ]; then
        return 0
    fi

    print_header "Configuring Database Secrets Engine"

    # Wait for PostgreSQL to be ready
    echo "Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
        if docker exec vault-postgres pg_isready -U postgres &> /dev/null; then
            print_success "PostgreSQL is ready!"
            break
        fi
        sleep 1
    done

    # Enable database secrets engine
    echo "Enabling database secrets engine..."
    docker exec -e VAULT_TOKEN="$VAULT_TOKEN" vault-dev \
        vault secrets enable database 2>/dev/null || true
    print_success "Database engine enabled"

    # Configure PostgreSQL connection
    echo "Configuring PostgreSQL connection..."
    docker exec -e VAULT_TOKEN="$VAULT_TOKEN" vault-dev \
        vault write database/config/postgres \
        plugin_name=postgresql-database-plugin \
        allowed_roles="readonly,readwrite" \
        connection_url="postgresql://{{username}}:{{password}}@vault-postgres:5432/appdb?sslmode=disable" \
        username="vault_admin" \
        password="vault_admin_password"
    print_success "PostgreSQL connection configured"

    # Create readonly role
    echo "Creating readonly role..."
    docker exec -e VAULT_TOKEN="$VAULT_TOKEN" vault-dev \
        vault write database/roles/readonly \
        db_name=postgres \
        creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}' IN ROLE readonly_role;" \
        default_ttl="1h" \
        max_ttl="24h"
    print_success "Created database role: readonly"

    # Create readwrite role
    echo "Creating readwrite role..."
    docker exec -e VAULT_TOKEN="$VAULT_TOKEN" vault-dev \
        vault write database/roles/readwrite \
        db_name=postgres \
        creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}' IN ROLE readwrite_role;" \
        default_ttl="1h" \
        max_ttl="24h"
    print_success "Created database role: readwrite"
}

configure_auth_methods() {
    print_header "Configuring Authentication Methods"

    # Enable userpass auth
    echo "Enabling userpass auth..."
    docker exec -e VAULT_TOKEN="$VAULT_TOKEN" vault-dev \
        vault auth enable userpass 2>/dev/null || true
    print_success "Userpass auth enabled"

    # Create sample users
    echo "Creating sample users..."
    docker exec -e VAULT_TOKEN="$VAULT_TOKEN" vault-dev \
        vault write auth/userpass/users/alice password=alice123 policies=default
    docker exec -e VAULT_TOKEN="$VAULT_TOKEN" vault-dev \
        vault write auth/userpass/users/bob password=bob123 policies=default
    print_success "Created users: alice, bob"

    # Enable AppRole auth
    echo "Enabling AppRole auth..."
    docker exec -e VAULT_TOKEN="$VAULT_TOKEN" vault-dev \
        vault auth enable approle 2>/dev/null || true
    print_success "AppRole auth enabled"

    # Create sample AppRole
    docker exec -e VAULT_TOKEN="$VAULT_TOKEN" vault-dev \
        vault write auth/approle/role/my-app \
        token_policies=default \
        token_ttl=1h \
        token_max_ttl=4h
    print_success "Created AppRole: my-app"
}

create_sample_secrets() {
    print_header "Creating Sample Secrets"

    # Create sample KV secrets
    docker exec -e VAULT_TOKEN="$VAULT_TOKEN" vault-dev \
        vault kv put secret/app/config \
        database_url="postgres://localhost:5432/appdb" \
        api_key="sample-api-key-12345" \
        debug_mode="true"
    print_success "Created secret: secret/app/config"

    docker exec -e VAULT_TOKEN="$VAULT_TOKEN" vault-dev \
        vault kv put secret/app/credentials \
        username="app_user" \
        password="app_password_secure"
    print_success "Created secret: secret/app/credentials"
}

print_summary() {
    print_header "Setup Complete!"

    echo -e "${GREEN}Environment Variables:${NC}"
    echo "  export VAULT_ADDR='$VAULT_ADDR'"
    echo "  export VAULT_TOKEN='$VAULT_TOKEN'"
    echo ""

    echo -e "${GREEN}Enabled Secrets Engines:${NC}"
    echo "  - KV v2: secret/"
    echo "  - KV v1: kv-v1/"
    echo "  - Transit: transit/"
    if [ "$WITH_DATABASE" = true ]; then
        echo "  - Database: database/"
    fi
    echo ""

    echo -e "${GREEN}Enabled Auth Methods:${NC}"
    echo "  - Userpass (users: alice/alice123, bob/bob123)"
    echo "  - AppRole (role: my-app)"
    echo ""

    echo -e "${GREEN}Web UI:${NC}"
    echo "  http://localhost:8200/ui (Token: $VAULT_TOKEN)"
    echo ""

    if [ "$WITH_DATABASE" = true ]; then
        echo -e "${GREEN}PostgreSQL:${NC}"
        echo "  Host: localhost:5432"
        echo "  Database: appdb"
        echo "  User: postgres / Password: postgres"
        echo "  Adminer: http://localhost:8080"
        echo ""
    fi

    echo -e "${GREEN}Quick Test:${NC}"
    echo "  vault kv get secret/app/config"
    echo "  vault login -method=userpass username=alice password=alice123"
}

# Main execution
main() {
    print_header "Vault Course - Development Environment Setup"

    check_prerequisites
    start_vault
    configure_secrets_engines
    configure_database_engine
    configure_auth_methods
    create_sample_secrets
    print_summary
}

main "$@"

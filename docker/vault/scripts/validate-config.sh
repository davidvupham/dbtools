#!/usr/bin/env bash
# Validate HashiCorp Vault Docker configuration
# Checks syntax, security settings, and best practices

# Note: Not using set -e because we want to continue on errors
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HVAULT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== HashiCorp Vault Configuration Validator ==="
echo "Directory: $HVAULT_DIR"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() {
    echo -e "${GREEN}✓${NC} $1"
}

fail() {
    echo -e "${RED}✗${NC} $1"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

ERRORS=0
WARNINGS=0

echo "1. Checking required files..."
for file in docker-compose.yml Dockerfile config/vault.hcl scripts/init-vault.sh scripts/unseal-vault.sh; do
    if [ -f "$HVAULT_DIR/$file" ]; then
        pass "$file exists"
    else
        fail "$file missing"
        ((ERRORS++))
    fi
done
echo ""

echo "2. Validating Docker Compose syntax..."
if docker-compose -f "$HVAULT_DIR/docker-compose.yml" config > /dev/null 2>&1; then
    pass "docker-compose.yml syntax valid"
else
    fail "docker-compose.yml syntax invalid"
    ((ERRORS++))
fi

if docker-compose -f "$HVAULT_DIR/docker-compose.dev.yml" config > /dev/null 2>&1; then
    pass "docker-compose.dev.yml syntax valid"
else
    fail "docker-compose.dev.yml syntax invalid"
    ((ERRORS++))
fi
echo ""

echo "3. Checking security configurations..."

# Check for IPC_LOCK capability
if grep -q "IPC_LOCK" "$HVAULT_DIR/docker-compose.yml"; then
    pass "IPC_LOCK capability configured"
else
    fail "IPC_LOCK capability missing"
    ((ERRORS++))
fi

# Check for capability dropping
if grep -q "cap_drop" "$HVAULT_DIR/docker-compose.yml" && grep -q "ALL" "$HVAULT_DIR/docker-compose.yml"; then
    pass "Capabilities dropped (ALL)"
else
    warn "Not dropping all capabilities"
    ((WARNINGS++))
fi

# Check for no-new-privileges
if grep -q "no-new-privileges" "$HVAULT_DIR/docker-compose.yml"; then
    pass "no-new-privileges configured"
else
    fail "no-new-privileges not configured"
    ((ERRORS++))
fi

# Check for ulimits
if grep -q "ulimits:" "$HVAULT_DIR/docker-compose.yml"; then
    pass "ulimits configured"
else
    fail "ulimits not configured"
    ((ERRORS++))
fi

# Check for healthcheck
if grep -q "healthcheck:" "$HVAULT_DIR/docker-compose.yml"; then
    pass "Healthcheck configured"
else
    warn "Healthcheck not configured"
    ((WARNINGS++))
fi
echo ""

echo "4. Checking Vault configuration..."

# Check mlock setting
if grep -q "disable_mlock = false" "$HVAULT_DIR/config/vault.hcl"; then
    pass "Memory locking enabled (disable_mlock = false)"
else
    fail "Memory locking disabled (security risk)"
    ((ERRORS++))
fi

# Check UI setting
if grep -q "ui.*=.*true" "$HVAULT_DIR/config/vault.hcl"; then
    pass "UI enabled"
else
    warn "UI not enabled"
    ((WARNINGS++))
fi

# Check for TLS
if grep -q "tls_disable.*=.*1" "$HVAULT_DIR/config/vault.hcl"; then
    warn "TLS disabled (OK for development, required for production)"
    ((WARNINGS++))
fi
echo ""

echo "5. Checking scripts..."

# Check script permissions
for script in init-vault.sh unseal-vault.sh; do
    if [ -x "$HVAULT_DIR/scripts/$script" ]; then
        pass "$script is executable"
    else
        fail "$script is not executable"
        ((ERRORS++))
    fi
done

# Check for bash shebang
for script in init-vault.sh unseal-vault.sh; do
    if head -n 1 "$HVAULT_DIR/scripts/$script" | grep -q "bash"; then
        pass "$script has bash shebang"
    else
        fail "$script missing bash shebang"
        ((ERRORS++))
    fi
done
echo ""

echo "6. Checking policy files..."
for policy in admin-policy.hcl readonly-policy.hcl app-policy.hcl; do
    if [ -f "$HVAULT_DIR/policies/$policy" ]; then
        pass "$policy exists"
    else
        warn "$policy missing"
        ((WARNINGS++))
    fi
done
echo ""

echo "7. Checking documentation..."
for doc in README.md OPERATIONS.md SECURITY_CHECKLIST.md; do
    if [ -f "$HVAULT_DIR/$doc" ]; then
        pass "$doc exists"
    else
        warn "$doc missing"
        ((WARNINGS++))
    fi
done
echo ""

echo "=== Validation Summary ==="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}Validation passed with $WARNINGS warning(s)${NC}"
    exit 0
else
    echo -e "${RED}Validation failed with $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    exit 1
fi

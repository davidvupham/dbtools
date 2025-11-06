#!/bin/bash
# Test script for Vault AppRole authentication with various configurations
# This helps diagnose whether namespace headers or custom mount points are needed

set -e  # Exit on error

# Load environment variables from .env if it exists
if [ -f .env ]; then
    echo "Loading environment from .env file..."
    source .env
elif [ -f .env.example ]; then
    echo "⚠️  Warning: .env not found, using .env.example"
    echo "⚠️  Please create .env from .env.example with actual values"
    source .env.example
else
    echo "❌ Error: Neither .env nor .env.example found"
    exit 1
fi

# Validate required variables
if [ -z "${VAULT_ADDR}" ]; then
    echo "❌ Error: VAULT_ADDR not set"
    exit 1
fi

if [ -z "${VAULT_ROLE_ID}" ]; then
    echo "❌ Error: VAULT_ROLE_ID not set"
    exit 1
fi

if [ -z "${VAULT_SECRET_ID}" ]; then
    echo "❌ Error: VAULT_SECRET_ID not set"
    exit 1
fi

# Display configuration
echo "=========================================="
echo "Vault AppRole Authentication Test"
echo "=========================================="
echo "VAULT_ADDR:       ${VAULT_ADDR}"
echo "VAULT_NAMESPACE:  ${VAULT_NAMESPACE:-<not set>}"
echo "VAULT_ROLE_ID:    ${VAULT_ROLE_ID:0:8}...${VAULT_ROLE_ID: -4}"
echo "VAULT_SECRET_ID:  ${VAULT_SECRET_ID:0:8}...${VAULT_SECRET_ID: -4}"
echo ""

# Function to test login and display results
test_login() {
    local test_name="$1"
    local url="$2"
    shift 2
    local headers=("$@")

    echo "=========================================="
    echo "Test: ${test_name}"
    echo "=========================================="
    echo "URL: ${url}"

    if [ ${#headers[@]} -gt 0 ]; then
        echo "Headers:"
        for header in "${headers[@]}"; do
            echo "  - ${header}"
        done
    else
        echo "Headers: (none)"
    fi
    echo ""

    # Build curl command
    local curl_cmd="curl -k -s -w \"\n\nHTTP Status: %{http_code}\n\" -X POST"
    curl_cmd="${curl_cmd} \"${url}\""
    curl_cmd="${curl_cmd} -H \"Content-Type: application/json\""

    # Add custom headers
    for header in "${headers[@]}"; do
        curl_cmd="${curl_cmd} -H \"${header}\""
    done

    curl_cmd="${curl_cmd} -d '{\"role_id\":\"${VAULT_ROLE_ID}\",\"secret_id\":\"${VAULT_SECRET_ID}\"}'"

    echo "Command:"
    echo "${curl_cmd}"
    echo ""
    echo "Response:"
    echo "------------------------------------------"

    # Execute and capture result
    eval "${curl_cmd}" | if command -v jq &> /dev/null; then
        jq '.' 2>/dev/null || cat
    else
        cat
    fi

    echo ""
    echo ""
}

# Test 1: Basic - No namespace, default mount point
test_login \
    "Basic (No namespace, default mount)" \
    "${VAULT_ADDR}/v1/auth/approle/login"

# Test 2: With namespace header (this is what works!)
if [ -n "${VAULT_NAMESPACE}" ]; then
    test_login \
        "With Namespace Header (REQUIRED for Vault Enterprise)" \
        "${VAULT_ADDR}/v1/auth/approle/login" \
        "X-Vault-Namespace: ${VAULT_NAMESPACE}"
else
    echo "=========================================="
    echo "Skipping: Namespace test (VAULT_NAMESPACE not set)"
    echo "=========================================="
    echo ""
fi

echo ""
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "✓ All tests completed"
echo ""
echo "Success indicators:"
echo "  - HTTP Status: 200"
echo "  - Response contains 'client_token' field"
echo "  - Response contains 'auth' object"
echo ""
echo "Failure indicators:"
echo "  - HTTP Status: 403 → Permission denied (wrong credentials or missing namespace)"
echo "  - HTTP Status: 404 → Wrong mount point or AppRole not enabled"
echo "  - HTTP Status: 400 → Malformed request"
echo ""
echo "Next Steps:"
echo "  1. Identify which test succeeded"
echo "  2. Note the configuration (namespace required for Vault Enterprise)"
echo "  3. Ensure VAULT_NAMESPACE is set in your .env file"
echo "=========================================="

#!/usr/bin/env bash
# Initialize and configure a new Vault server
# This script should be run once after Vault is deployed

set -e

# Configuration
VAULT_ADDR="${VAULT_ADDR:-http://localhost:8200}"
INIT_OUTPUT_FILE="${INIT_OUTPUT_FILE:-/tmp/vault-init-keys.json}"
AUDIT_LOG_PATH="${AUDIT_LOG_PATH:-/vault/logs/audit/audit.log}"

echo "=== Vault Initialization Script ==="
echo "Vault Address: $VAULT_ADDR"
echo ""

# Check if Vault is accessible
echo "Checking Vault status..."
if ! vault status > /dev/null 2>&1; then
    echo "Error: Cannot connect to Vault at $VAULT_ADDR"
    echo "Please ensure Vault is running and accessible"
    exit 1
fi

# Check if Vault is already initialized
if vault status 2>&1 | grep -q "Initialized.*true"; then
    echo "Vault is already initialized"
    exit 0
fi

echo "Initializing Vault..."
echo "Using 5 key shares with threshold of 3"

# Initialize Vault
vault operator init \
    -key-shares=5 \
    -key-threshold=3 \
    -format=json > "$INIT_OUTPUT_FILE"

echo ""
echo "=== IMPORTANT: Vault Initialization Complete ==="
echo ""
echo "Unseal keys and root token have been saved to: $INIT_OUTPUT_FILE"
echo ""
echo "CRITICAL SECURITY NOTICE:"
echo "1. Store the unseal keys in separate, secure locations"
echo "2. Never store all keys together"
echo "3. Distribute keys to different trusted operators"
echo "4. Store the root token securely and revoke it after initial setup"
echo "5. Delete $INIT_OUTPUT_FILE after securely storing the keys"
echo ""

# Extract root token for next steps
ROOT_TOKEN=$(jq -r '.root_token' "$INIT_OUTPUT_FILE")
export VAULT_TOKEN="$ROOT_TOKEN"

echo "Unsealing Vault..."
for i in {0..2}; do
    UNSEAL_KEY=$(jq -r ".unseal_keys_b64[$i]" "$INIT_OUTPUT_FILE")
    vault operator unseal "$UNSEAL_KEY" > /dev/null
done

echo "Vault unsealed successfully"
echo ""

# Enable audit logging
echo "Enabling audit logging..."
vault audit enable file file_path="$AUDIT_LOG_PATH"

echo ""
echo "=== Initial Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Securely store and distribute the unseal keys from $INIT_OUTPUT_FILE"
echo "2. Configure authentication methods (vault auth enable <method>)"
echo "3. Create policies (vault policy write <name> <file>)"
echo "4. Enable secret engines (vault secrets enable <type>)"
echo "5. Revoke the root token when initial setup is complete"
echo ""
echo "Root Token (current session): $ROOT_TOKEN"
echo "Use this token to complete initial setup, then revoke it"

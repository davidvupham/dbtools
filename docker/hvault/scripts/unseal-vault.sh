#!/usr/bin/env bash
# Unseal Vault using stored unseal keys
# This script should be run when Vault starts sealed

set -e

VAULT_ADDR="${VAULT_ADDR:-http://localhost:8200}"
KEYS_FILE="${KEYS_FILE:-/tmp/vault-init-keys.json}"

echo "=== Vault Unseal Script ==="
echo "Vault Address: $VAULT_ADDR"
echo ""

# Check if Vault is accessible
echo "Checking Vault status..."
if ! vault status > /dev/null 2>&1; then
    echo "Error: Cannot connect to Vault at $VAULT_ADDR"
    exit 1
fi

# Check if Vault is sealed
if vault status 2>&1 | grep -q "Sealed.*false"; then
    echo "Vault is already unsealed"
    exit 0
fi

# Check if keys file exists
if [ ! -f "$KEYS_FILE" ]; then
    echo "Error: Keys file not found at $KEYS_FILE"
    echo "Please provide unseal keys manually or specify KEYS_FILE environment variable"
    exit 1
fi

echo "Unsealing Vault..."
echo "Reading unseal keys from $KEYS_FILE"

# Get the threshold from vault status
THRESHOLD=$(vault status -format=json 2>/dev/null | jq -r '.t' || echo "3")

echo "Using $THRESHOLD unseal keys"

# Unseal using threshold number of keys
for i in $(seq 0 $((THRESHOLD - 1))); do
    UNSEAL_KEY=$(jq -r ".unseal_keys_b64[$i]" "$KEYS_FILE")
    if [ "$UNSEAL_KEY" = "null" ] || [ -z "$UNSEAL_KEY" ]; then
        echo "Error: Could not read unseal key $i from $KEYS_FILE"
        exit 1
    fi

    echo "Applying unseal key $((i + 1))/$THRESHOLD..."
    vault operator unseal "$UNSEAL_KEY" > /dev/null
done

echo ""
echo "Vault unsealed successfully"
vault status
